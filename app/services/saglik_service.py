# -*- coding: utf-8 -*-
"""app/services/saglik_service.py - Personel saglik/muayene bilgi servisi."""
from __future__ import annotations

from datetime import date, timedelta

from app.date_utils import parse_date, to_db_date, to_ui_date
from app.db.database import Database
from app.db.repos.lookup_repo import LookupRepo
from app.db.repos.muayene_repo import MuayeneRepo
from app.db.repos.personel_repo import PersonelRepo
from app.validators import bugun


class SaglikService:
    """Personel muayene kayitlarini salt-okunur panel icin hazirlar."""

    RISKLI_GUN = 60
    ZORUNLU_ANA_UZMANLIKLAR = ("Dermatoloji", "Dahiliye", "Goz")

    def __init__(self, db: Database):
        self._db = db
        self._repo = MuayeneRepo(db)
        self._personel_repo = PersonelRepo(db)
        self._lookup_repo = LookupRepo(db)

    def _durum_hesapla(self, sonraki_tarih: str | None) -> str:
        sonraki = parse_date(sonraki_tarih)
        if not sonraki:
            return "Planlandi"

        bugun = date.today()
        if sonraki < bugun:
            return "Gecikmis"
        if sonraki <= bugun + timedelta(days=self.RISKLI_GUN):
            return "Riskli"
        return "Gecerli"

    @staticmethod
    def _sonuc_etiketi(raw: str | None) -> str:
        val = str(raw or "").strip().lower()
        if val == "uygun":
            return "Uygun"
        if val == "uygun_degil":
            return "Uygun Degil"
        if val == "takip":
            return "Takip"
        return ""

    @staticmethod
    def _sonuc_db(raw: str | None) -> str | None:
        val = str(raw or "").strip().lower()
        if val in {"uygun", "uygun"}:
            return "uygun"
        if val in {"uygun degil", "uygun değil", "uygun_degil"}:
            return "uygun_degil"
        if val in {"takip"}:
            return "takip"
        return None

    @staticmethod
    def _norm_uzmanlik(raw: str | None) -> str:
        return str(raw or "").strip().lower().replace("ö", "o").replace("ü", "u").replace("ı", "i")

    def _zorunlu_harita(self) -> dict[str, str]:
        return {self._norm_uzmanlik(v): v for v in self.ZORUNLU_ANA_UZMANLIKLAR}

    def _personel_yil_kayitlari(self, personel_id: str, yil: int) -> list[dict]:
        kayitlar = self._repo.listele(yil=yil, personel_id=personel_id)
        return kayitlar or []

    @staticmethod
    def _bir_yil_sonra(tarih: date) -> date:
        try:
            return tarih.replace(year=tarih.year + 1)
        except ValueError:
            # 29 Subat gibi durumlarda bir sonraki yilin son gecerli gunu kullanilir.
            return tarih.replace(year=tarih.year + 1, day=28)

    def uzmanlik_secenekleri(self) -> list[str]:
        rows = self._lookup_repo.kategori("uzmanlik")
        tercih = list(self.ZORUNLU_ANA_UZMANLIKLAR)
        if not rows:
            return tercih

        mevcut = {self._norm_uzmanlik(v): str(v) for v in rows}
        secili = [mevcut.get(self._norm_uzmanlik(z), z) for z in tercih]
        return secili

    def personel_yil_uzmanlik_durumu(self, personel_id: str, yil: int) -> dict:
        zorunlu = self.uzmanlik_secenekleri()
        zorunlu_norm = {self._norm_uzmanlik(v): v for v in zorunlu}
        tamamlanan_norm: set[str] = set()
        for r in self._personel_yil_kayitlari(personel_id, yil):
            key = self._norm_uzmanlik(r.get("uzmanlik"))
            if key in zorunlu_norm:
                tamamlanan_norm.add(key)

        tamamlanan = [zorunlu_norm[k] for k in zorunlu_norm if k in tamamlanan_norm]
        eksik = [zorunlu_norm[k] for k in zorunlu_norm if k not in tamamlanan_norm]
        return {
            "yil": int(yil),
            "zorunlu": zorunlu,
            "tamamlanan": tamamlanan,
            "eksik": eksik,
            "tamamlandi": len(eksik) == 0,
        }

    def personel_yil_tek_rapor(self, personel_id: str, yil: int) -> dict | None:
        for r in self._personel_yil_kayitlari(personel_id, yil):
            belge_id = str(r.get("belge_id") or "").strip()
            if belge_id:
                return {
                    "belge_id": belge_id,
                    "dosya_adi": str(r.get("dosya_adi") or ""),
                }
        return None

    def personel_secenekleri(self) -> list[dict]:
        rows = self._personel_repo.listele(aktif_only=True)
        out: list[dict] = []
        for r in rows:
            pid = str(r.get("id") or "").strip()
            if not pid:
                continue
            out.append(
                {
                    "id": pid,
                    "ad_soyad": f"{r.get('ad') or ''} {r.get('soyad') or ''}".strip(),
                    "birim": str(r.get("gorev_yeri_ad") or ""),
                    "tc_kimlik": str(r.get("tc_kimlik") or ""),
                }
            )
        return out

    def tum_muayene_kayitlari(self, yil: int | None = None) -> list[dict]:
        rows = self._repo.listele(yil=yil)
        out: list[dict] = []
        for r in rows:
            tarih_raw = str(r.get("tarih") or "")
            tarih = parse_date(tarih_raw)
            sonraki_raw = str(r.get("sonraki") or "")
            out.append(
                {
                    "id": str(r.get("id") or ""),
                    "personel_id": str(r.get("personel_id") or ""),
                    "ad_soyad": f"{r.get('ad') or ''} {r.get('soyad') or ''}".strip(),
                    "birim": str(r.get("birim") or ""),
                    "uzmanlik": str(r.get("uzmanlik") or ""),
                    "muayene_tarihi": to_ui_date(tarih_raw),
                    "sonraki_kontrol": to_ui_date(sonraki_raw),
                    "muayene_tarihi_db": tarih_raw,
                    "sonraki_kontrol_db": sonraki_raw,
                    "sonuc": self._sonuc_etiketi(r.get("sonuc")),
                    "durum": self._durum_hesapla(sonraki_raw),
                    "yil": int(tarih.year) if tarih else 0,
                    "rapor": str(r.get("dosya_adi") or "") if r.get("belge_id") else "-",
                    "lokal_yol": str(r.get("lokal_yol") or ""),
                    "notlar": str(r.get("notlar") or ""),
                }
            )
        return out

    def muayene_kaydet(self, veri: dict, muayene_id: str | None = None) -> str:
        pid = str(veri.get("personel_id") or "").strip()
        uzmanlik = str(veri.get("uzmanlik") or "").strip()
        tarih = to_db_date(veri.get("tarih"))
        if not pid or not uzmanlik or not parse_date(tarih):
            raise ValueError("Personel, uzmanlik ve muayene tarihi zorunludur.")

        yil = parse_date(tarih).year
        uzmanlik_map = {self._norm_uzmanlik(v): v for v in self.uzmanlik_secenekleri()}
        uzmanlik_key = self._norm_uzmanlik(uzmanlik)
        if uzmanlik_key not in uzmanlik_map:
            raise ValueError("Bu akista sadece 3 ana uzmanlik icin kayit acilabilir.")
        uzmanlik = uzmanlik_map[uzmanlik_key]

        ayni_yil_kayitlari = self._personel_yil_kayitlari(pid, yil)
        mid = str(muayene_id or "").strip()

        for kayit in ayni_yil_kayitlari:
            if str(kayit.get("id") or "") == mid:
                continue
            if self._norm_uzmanlik(kayit.get("uzmanlik")) == uzmanlik_key:
                raise ValueError("Ayni personel icin ayni yil/uzmanlik kaydi zaten var.")

        rapor_ids = {str(k.get("belge_id") or "").strip() for k in ayni_yil_kayitlari if str(k.get("belge_id") or "").strip()}
        giren_belge = str(veri.get("belge_id") or "").strip()
        if rapor_ids and giren_belge and giren_belge not in rapor_ids:
            raise ValueError("Ayni personelin ayni yil muayeneleri tek rapor evragi ile eslesmelidir.")
        belge_id = giren_belge or (next(iter(rapor_ids)) if rapor_ids else None)

        sonraki_tarih = self._bir_yil_sonra(parse_date(tarih)).strftime("%Y-%m-%d")

        payload = {
            "personel_id": pid,
            "uzmanlik": uzmanlik,
            "tarih": tarih,
            "sonraki": sonraki_tarih,
            "sonuc": self._sonuc_db(veri.get("sonuc")),
            "notlar": str(veri.get("notlar") or "").strip() or None,
            "belge_id": belge_id,
            "olusturuldu": bugun(),
        }

        if mid:
            self._repo.guncelle(mid, payload)
            return mid
        return self._repo.ekle(payload)

    def personel_muayene_kayitlari(self, personel_id: str) -> list[dict]:
        pid = str(personel_id or "").strip()
        if not pid:
            return []

        rows = self._repo.personel_listele(pid)
        out: list[dict] = []
        for r in rows:
            tarih_raw = str(r.get("tarih") or "")
            tarih = parse_date(tarih_raw)
            sonraki_raw = str(r.get("sonraki") or "")

            out.append(
                {
                    "id": str(r.get("id") or ""),
                    "uzmanlik": str(r.get("uzmanlik") or ""),
                    "muayene_tarihi": to_ui_date(tarih_raw),
                    "sonraki_kontrol": to_ui_date(sonraki_raw),
                    "muayene_tarihi_db": tarih_raw,
                    "sonraki_kontrol_db": sonraki_raw,
                    "sonuc": self._sonuc_etiketi(r.get("sonuc")),
                    "durum": self._durum_hesapla(sonraki_raw),
                    "yil": int(tarih.year) if tarih else 0,
                    "rapor_var": bool(r.get("belge_id")),
                    "rapor_adi": str(r.get("dosya_adi") or ""),
                    "lokal_yol": str(r.get("lokal_yol") or ""),
                    "notlar": str(r.get("notlar") or ""),
                }
            )
        return out

    def muayene_sil(self, muayene_id: str) -> None:
        mid = str(muayene_id or "").strip()
        if not mid:
            raise ValueError("Muayene ID zorunludur.")
        self._repo.sil(mid)
