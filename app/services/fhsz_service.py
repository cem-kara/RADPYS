# -*- coding: utf-8 -*-
"""app/services/fhsz_service.py - FHSZ yonetim is mantigi."""
from __future__ import annotations

import math
from datetime import datetime, timedelta

from app.db.database import Database
from app.db.repos.fhsz_repo import FhszRepo
from app.db.repos.personel_repo import PersonelRepo
from app.validators import pozitif_sayi


class FhszService:
    """FHSZ donem kayitlarini hesaplama ve kaydetme servisi."""

    SAAT_KATSAYI = 7.0

    @staticmethod
    def sua_hak_edis_hesapla(toplam_saat: float) -> int:
        """Toplam fiili saate gore hak edilen sua gununu hesaplar."""
        try:
            saat = float(toplam_saat)
        except (TypeError, ValueError):
            return 0
        if saat <= 0:
            return 0
        return min(30, max(1, int(math.ceil(saat / 50.0))))

    def __init__(self, db: Database):
        self._db = db
        self._repo = FhszRepo(db)
        self._p_repo = PersonelRepo(db)

    @staticmethod
    def fiili_saat_hesapla(aylik_gun: int, izin_gun: int, kosul: str) -> float:
        """Kosul A icin fiili saat hesaplar; kosul B icin 0 doner."""
        kos = str(kosul or "").strip().upper()
        if kos != "A":
            return 0.0
        net_gun = max(0, int(aylik_gun or 0) - int(izin_gun or 0))
        return float(net_gun) * FhszService.SAAT_KATSAYI

    def donem_listele(self, yil: int, donem: int) -> list[dict]:
        """Kayitli donem satirlarini personel detaylariyla getirir."""
        return self._repo.listele(yil=int(yil), donem=int(donem))

    def donem_varsayilan_grid(self) -> list[dict]:
        """Kayit yoksa aktif personel icin varsayilan satirlar olusturur."""
        rows = []
        personeller = self._p_repo.listele(aktif_only=True)
        for p in personeller:
            if str(p.get("durum") or "") == "ayrildi":
                continue
            kosul = "A" if int(p.get("sua_hakki") or 0) == 1 else "B"
            rows.append(
                {
                    "personel_id": str(p.get("id") or ""),
                    "tc_kimlik": str(p.get("tc_kimlik") or ""),
                    "ad_soyad": f"{p.get('ad') or ''} {p.get('soyad') or ''}".strip(),
                    "gorev_yeri": str(p.get("gorev_yeri_ad") or ""),
                    "calisma_kosulu": kosul,
                    "aylik_gun": 0,
                    "izin_gun": 0,
                    "fiili_saat": 0.0,
                    "notlar": "",
                }
            )
        return rows

    def donem_getir_veya_olustur(self, yil: int, donem: int) -> list[dict]:
        mevcut = self.donem_listele(yil, donem)
        if mevcut:
            return [
                {
                    "personel_id": str(r.get("personel_id") or ""),
                    "tc_kimlik": str(r.get("tc_kimlik") or ""),
                    "ad_soyad": f"{r.get('ad') or ''} {r.get('soyad') or ''}".strip(),
                    "gorev_yeri": str(r.get("gorev_yeri_ad") or ""),
                    "calisma_kosulu": str(r.get("calisma_kosulu") or "B"),
                    "aylik_gun": int(r.get("aylik_gun") or 0),
                    "izin_gun": int(r.get("izin_gun") or 0),
                    "fiili_saat": float(r.get("fiili_saat") or 0.0),
                    "notlar": str(r.get("notlar") or ""),
                }
                for r in mevcut
            ]
        return self.donem_varsayilan_grid()

    def donem_kaydet(self, yil: int, donem: int, satirlar: list[dict]) -> int:
        """Donem satirlarini eskiyi silip yeniden yazar."""
        yil_int = pozitif_sayi(yil, "Yil")
        donem_int = pozitif_sayi(donem, "Donem")
        if donem_int < 1 or donem_int > 12:
            raise ValueError("Donem 1-12 araliginda olmalidir.")

        temiz: list[dict] = []
        for s in satirlar or []:
            pid = str(s.get("personel_id") or "").strip()
            if not pid:
                continue
            aylik_gun = max(0, int(s.get("aylik_gun") or 0))
            izin_gun = max(0, int(s.get("izin_gun") or 0))
            kosul = str(s.get("calisma_kosulu") or "B").strip().upper()
            if kosul not in {"A", "B"}:
                kosul = "B"
            fiili = self.fiili_saat_hesapla(aylik_gun, izin_gun, kosul)
            temiz.append(
                {
                    "personel_id": pid,
                    "yil": yil_int,
                    "donem": donem_int,
                    "aylik_gun": aylik_gun,
                    "izin_gun": izin_gun,
                    "fiili_saat": fiili,
                    "calisma_kosulu": kosul,
                    "notlar": str(s.get("notlar") or "").strip() or None,
                }
            )

        with self._db.transaction():
            self._repo.donem_sil(yil_int, donem_int)
            for kayit in temiz:
                self._repo.ekle(kayit)

        return len(temiz)

    def puantaj_rapor_uret(self, yil: int, donem: int | None = None) -> list[dict]:
        """Yil ve istege bagli donem filtresiyle puantaj rapor satirlarini uretir."""
        yil_int = int(yil)
        if donem is not None:
            donem = int(donem)

        tum = self._repo.listele(yil=yil_int)
        if not tum:
            return []

        personel_map: dict[str, list[dict]] = {}
        for r in tum:
            pid = str(r.get("personel_id") or "").strip()
            if not pid:
                continue
            personel_map.setdefault(pid, []).append(r)

        sonuc: list[dict] = []
        for _, kayitlar in sorted(
            personel_map.items(),
            key=lambda x: f"{str(x[1][0].get('soyad') or '')} {str(x[1][0].get('ad') or '')}".lower(),
        ):
            kayitlar.sort(key=lambda k: int(k.get("donem") or 0))

            kumulatif_saat = 0.0
            toplam_gun = 0
            toplam_izin = 0
            toplam_saat = 0.0
            ad_soyad = f"{kayitlar[0].get('ad') or ''} {kayitlar[0].get('soyad') or ''}".strip()
            tc = str(kayitlar[0].get("tc_kimlik") or "")

            for r in kayitlar:
                d = int(r.get("donem") or 0)
                aylik_gun = int(r.get("aylik_gun") or 0)
                izin_gun = int(r.get("izin_gun") or 0)
                fiili_saat = float(r.get("fiili_saat") or 0.0)

                kumulatif_saat += fiili_saat
                toplam_gun += aylik_gun
                toplam_izin += izin_gun
                toplam_saat += fiili_saat

                if donem is not None and d != donem:
                    continue

                sonuc.append(
                    {
                        "tc_kimlik": tc,
                        "ad_soyad": ad_soyad,
                        "yil": yil_int,
                        "donem": d,
                        "aylik_gun": aylik_gun,
                        "izin_gun": izin_gun,
                        "fiili_saat": fiili_saat,
                        "kumulatif_saat": kumulatif_saat,
                        "sua_hak_edis": self.sua_hak_edis_hesapla(kumulatif_saat),
                    }
                )

            if donem is None:
                sonuc.append(
                    {
                        "tc_kimlik": tc,
                        "ad_soyad": ad_soyad,
                        "yil": yil_int,
                        "donem": "Toplam",
                        "aylik_gun": toplam_gun,
                        "izin_gun": toplam_izin,
                        "fiili_saat": toplam_saat,
                        "kumulatif_saat": toplam_saat,
                        "sua_hak_edis": self.sua_hak_edis_hesapla(toplam_saat),
                    }
                )

        return sonuc

    def izin_kesisim_gun_hesapla(
        self,
        personel_id: str,
        donem_bas: datetime,
        donem_bit: datetime,
    ) -> int:
        """Donem aralığında personelin kaç gün izni var hesaplar."""
        try:
            cursor = self._db.conn.execute(
                """
                SELECT COUNT(*) as gun_sayisi
                FROM izin
                WHERE personel_id = ?
                  AND baslama_tarihi <= ?
                  AND bitis_tarihi >= ?
                  AND durum != 'iptal'
                """,
                (personel_id, donem_bit.strftime("%Y-%m-%d"), donem_bas.strftime("%Y-%m-%d")),
            )
            row = cursor.fetchone()
            if row:
                return int(row[0]) or 0
        except Exception:
            pass
        return 0
