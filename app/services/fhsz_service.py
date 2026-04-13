# -*- coding: utf-8 -*-
"""app/services/fhsz_service.py - FHSZ yonetim is mantigi."""
from __future__ import annotations

from datetime import date, datetime

from app.db.database import Database
from app.db.repos.fhsz_repo import FhszRepo
from app.db.repos.personel_repo import PersonelRepo
from app.hesaplamalar import (
    donem_tarih_araligi as hesap_donem_tarih_araligi,
    fiili_saat_hesapla as hesap_fiili_saat,
    is_gunu_hesapla,
    sua_hak_edis_hesapla as hesap_sua_hak_edis,
    turkce_normalize_lower,
)
from app.validators import parse_tarih, pozitif_sayi


class FhszService:
    """FHSZ donem kayitlarini hesaplama ve kaydetme servisi."""

    SAAT_KATSAYI = 7.0
    FHSZ_ESIK = date(2022, 4, 26)
    IZIN_VERILEN_SINIFLAR = {
        "akademik personel",
        "asistan doktor",
        "radyasyon gorevlisi",
        "hemsire",
    }

    @staticmethod
    def sua_hak_edis_hesapla(toplam_saat: float) -> int:
        """Toplam fiili saate gore hak edilen sua gununu hesaplar."""
        return hesap_sua_hak_edis(toplam_saat)

    def __init__(self, db: Database):
        self._db = db
        self._repo = FhszRepo(db)
        self._p_repo = PersonelRepo(db)

    @staticmethod
    def donem_tarih_araligi(yil: int, donem: int) -> tuple[date, date]:
        """Donem tarihini 15 -> sonraki ay 14 olarak hesaplar."""
        return hesap_donem_tarih_araligi(yil, donem)

    def _tatil_setleri(self, bas: date, bit: date) -> tuple[set[str], set[str]]:
        rows = self._db.fetchall(
            "SELECT tarih, yarim_gun FROM tatil WHERE tarih BETWEEN ? AND ?",
            (bas.strftime("%Y-%m-%d"), bit.strftime("%Y-%m-%d")),
        )
        tam_tatil = set()
        yarim_tatil = set()
        for r in rows:
            tarih = str(r.get("tarih") or "").strip()
            if not tarih:
                continue
            if int(r.get("yarim_gun") or 0) == 1:
                yarim_tatil.add(tarih)
            else:
                tam_tatil.add(tarih)
        return tam_tatil, yarim_tatil

    @staticmethod
    def _yarim_tatil_sayisi(bas: date, bit: date, yarim_tatiller: set[str]) -> int:
        adet = 0
        for tarih_str in yarim_tatiller:
            dt = parse_tarih(tarih_str)
            if not dt:
                continue
            if dt < bas or dt > bit:
                continue
            if dt.weekday() >= 5:
                continue
            adet += 1
        return adet

    @staticmethod
    def _normalize_sinif(text: str) -> str:
        return turkce_normalize_lower(text)

    def _personel_uygun_mu(self, personel: dict) -> bool:
        sinif = self._normalize_sinif(personel.get("hizmet_sinifi") or "")
        if not sinif:
            return True
        return sinif in self.IZIN_VERILEN_SINIFLAR

    def _personel_donem_is_gunu(
        self,
        personel: dict,
        bas: date,
        bit: date,
        tatiller: set[str],
        yarim_tatiller: set[str],
    ) -> float:
        durum = str(personel.get("durum") or "").strip().lower()
        ayrilis = parse_tarih(personel.get("ayrilik_tarihi"))

        kisi_bit = bit
        if durum in {"pasif", "ayrildi"} and ayrilis:
            if ayrilis < bas:
                return 0
            if ayrilis < bit:
                kisi_bit = ayrilis

        tam_is_gunu = float(is_gunu_hesapla(bas, kisi_bit, tatiller=tatiller))
        yarim_adet = self._yarim_tatil_sayisi(bas, kisi_bit, yarim_tatiller)
        return max(0.0, tam_is_gunu - (0.5 * float(yarim_adet)))

    def _izin_kesisim_gun_hesapla(self, personel_id: str, bas: date, bit: date, tatiller: set[str]) -> float:
        izinler = self._db.fetchall(
            "SELECT baslama, bitis, durum FROM izin "
            "WHERE personel_id = ? "
            "AND baslama <= ? "
            "AND bitis >= ?",
            (personel_id, bit.strftime("%Y-%m-%d"), bas.strftime("%Y-%m-%d")),
        )

        toplam = 0.0
        for row in izinler:
            if str(row.get("durum") or "").strip().lower() == "iptal":
                continue
            izin_bas = parse_tarih(row.get("baslama"))
            izin_bit = parse_tarih(row.get("bitis"))
            if not izin_bas or not izin_bit:
                continue
            kesisim_bas = max(bas, izin_bas)
            kesisim_bit = min(bit, izin_bit)
            if kesisim_bas > kesisim_bit:
                continue
            toplam += is_gunu_hesapla(kesisim_bas, kesisim_bit, tatiller=tatiller)
        return toplam

    def donem_hesapla(self, yil: int, donem: int) -> list[dict]:
        """Donem kaydini is kuralina gore hesaplar veya kayitli satirlari gunceller."""
        yil_int = int(yil)
        donem_int = int(donem)
        donem_bas, donem_bit = self.donem_tarih_araligi(yil_int, donem_int)

        if donem_bit < self.FHSZ_ESIK:
            raise ValueError("26.04.2022 oncesi donemler icin FHSZ hesaplanamaz.")

        hesap_bas = max(donem_bas, self.FHSZ_ESIK)
        tam_tatiller, yarim_tatiller = self._tatil_setleri(hesap_bas, donem_bit)

        kayitli = self.donem_listele(yil_int, donem_int)
        kayit_map: dict[str, dict] = {
            str(r.get("personel_id") or ""): r for r in kayitli if r.get("personel_id")
        }

        rows: list[dict] = []
        personeller = self._p_repo.listele(aktif_only=False)
        for p in personeller:
            pid = str(p.get("id") or "").strip()
            if not pid:
                continue
            if not self._personel_uygun_mu(p):
                continue

            aylik_gun = self._personel_donem_is_gunu(
                p,
                hesap_bas,
                donem_bit,
                tam_tatiller,
                yarim_tatiller,
            )
            if aylik_gun <= 0:
                continue

            mevcut = kayit_map.get(pid, {})
            kosul = str(mevcut.get("calisma_kosulu") or "").strip().upper()
            if kosul not in {"A", "B"}:
                kosul = "A" if int(p.get("sua_hakki") or 0) == 1 else "B"

            izin_gun = float(mevcut.get("izin_gun") or 0.0)
            if izin_gun <= 0:
                izin_gun = self._izin_kesisim_gun_hesapla(pid, hesap_bas, donem_bit, tam_tatiller)

            fiili_saat = self.fiili_saat_hesapla(aylik_gun, izin_gun, kosul)
            rows.append(
                {
                    "personel_id": pid,
                    "tc_kimlik": str(p.get("tc_kimlik") or ""),
                    "ad_soyad": f"{p.get('ad') or ''} {p.get('soyad') or ''}".strip(),
                    "gorev_yeri": str(p.get("gorev_yeri_ad") or ""),
                    "calisma_kosulu": kosul,
                    "aylik_gun": aylik_gun,
                    "izin_gun": izin_gun,
                    "fiili_saat": fiili_saat,
                    "notlar": str(mevcut.get("notlar") or ""),
                }
            )

        rows.sort(key=lambda r: str(r.get("ad_soyad") or "").lower())
        return rows

    @staticmethod
    def fiili_saat_hesapla(aylik_gun: float, izin_gun: float, kosul: str) -> float:
        """Kosul A icin fiili saat hesaplar; kosul B icin 0 doner."""
        return hesap_fiili_saat(aylik_gun, izin_gun, kosul, saat_katsayi=FhszService.SAAT_KATSAYI)

    def donem_listele(self, yil: int, donem: int) -> list[dict]:
        """Kayitli donem satirlarini personel detaylariyla getirir."""
        return self._repo.listele(yil=int(yil), donem=int(donem))

    def personel_kayitlari_listele(self, personel_id: str) -> list[dict]:
        """Personelin kayitli FHSZ satirlarini salt-okunur liste olarak getirir."""
        pid = str(personel_id or "").strip()
        if not pid:
            return []

        rows = self._repo.listele(personel_id=pid)
        rows.sort(key=lambda r: (int(r.get("yil") or 0), int(r.get("donem") or 0)), reverse=True)
        return rows

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
        # Geriye donuk uyumluluk: eski arayuzlar bu metodu kullaniyor.
        return self.donem_hesapla(yil, donem)

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
            aylik_gun = max(0.0, float(s.get("aylik_gun") or 0.0))
            izin_gun = max(0.0, float(s.get("izin_gun") or 0.0))
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
        """Donem araliginda izin kayitlarinin is gunu kesisimini hesaplar."""
        bas = donem_bas.date() if isinstance(donem_bas, datetime) else donem_bas
        bit = donem_bit.date() if isinstance(donem_bit, datetime) else donem_bit
        tatiller = self._tatil_seti(bas, bit)
        return self._izin_kesisim_gun_hesapla(personel_id, bas, bit, tatiller)
