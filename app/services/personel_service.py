# -*- coding: utf-8 -*-
"""
app/services/personel_service.py
─────────────────────────────────
Personel iş mantığı.

Kurallar:
  - TC doğrulama zorunlu
  - Aynı TC iki kez eklenemez
  - Personel ASLA silinmez → pasife_al() kullanılır
  - Bakiye (izin, şua) bu serviste değil IzinService'te hesaplanır
"""
from __future__ import annotations
from app.db.database import Database
from app.db.repos.personel_repo import PersonelRepo
from app.db.repos.lookup_repo import LookupRepo, GorevYeriRepo
from app.exceptions import (
    KayitBulunamadi, KayitZatenVar,
    DogrulamaHatasi, PasifPersonelHatasi,
)
from app.validators import (
    tc_dogrula_veya_hata, zorunlu,
    parse_tarih_veya_hata, format_tarih, bugun,
)
from app.config import LookupKategori


class PersonelService:
    """
    Personel tablosu iş mantığı.

    Kullanım:
        svc = PersonelService(db)
        liste = svc.listele()
        pid   = svc.ekle({"tc_kimlik": "...", "ad": "Ali", "soyad": "Kaya"})
    """

    def __init__(self, db: Database):
        self._repo    = PersonelRepo(db)
        self._lookup  = LookupRepo(db)
        self._gy_repo = GorevYeriRepo(db)

    # ── Sorgular ──────────────────────────────────────────────────

    def listele(self, aktif_only: bool = True) -> list[dict]:
        """Personel listesi — soyad/ad sırası."""
        return self._repo.listele(aktif_only=aktif_only)

    def getir(self, personel_id: str) -> dict:
        """
        Tek personel kaydı.
        Raises: KayitBulunamadi
        """
        p = self._repo.getir(personel_id)
        if not p:
            raise KayitBulunamadi(f"Personel bulunamadı: {personel_id}")
        return p

    def tc_ile_getir(self, tc: str) -> dict:
        """
        TC kimlik ile personel getir.
        Raises: KayitBulunamadi
        """
        p = self._repo.tc_ile_getir(tc.strip())
        if not p:
            raise KayitBulunamadi(f"TC bulunamadı: {tc}")
        return p

    def say(self, durum: str | None = None) -> int:
        """Toplam veya duruma göre personel sayısı."""
        return self._repo.say(durum)

    # ── Dropdown Verileri ──────────────────────────────────────────

    def hizmet_siniflari(self) -> list[str]:
        return self._lookup.kategori(LookupKategori.HIZMET_SINIFI)

    def kadro_unvanlari(self) -> list[str]:
        return self._lookup.kategori(LookupKategori.KADRO_UNVANI)

    def gorev_yerleri(self) -> list[dict]:
        """[{"id": ..., "ad": ..., "sua_hakki": ...}] listesi."""
        return self._gy_repo.listele()

    def gorev_yeri_adlari(self) -> list[str]:
        return self._gy_repo.ad_listesi()

    # ── Yazma ─────────────────────────────────────────────────────

    def ekle(self, veri: dict) -> str:
        """
        Yeni personel ekler.

        Zorunlu alanlar: tc_kimlik, ad, soyad
        Returns: Yeni personelin ID'si

        Raises:
            TCHatasi           — geçersiz TC
            DogrulamaHatasi    — zorunlu alan boş
            KayitZatenVar      — TC zaten kayıtlı
        """
        tc = tc_dogrula_veya_hata(veri.get("tc_kimlik", ""))
        zorunlu(veri.get("ad"), "Ad")
        zorunlu(veri.get("soyad"), "Soyad")

        if self._repo.tc_var_mi(tc):
            raise KayitZatenVar(f"Bu TC Kimlik No zaten kayıtlı: {tc}")

        # Görev yeri ID'sini çöz (ad geldiyse ID'ye çevir)
        veri = dict(veri)
        if "gorev_yeri_ad" in veri and "gorev_yeri_id" not in veri:
            veri["gorev_yeri_id"] = self._gy_id_bul(veri.pop("gorev_yeri_ad"))

        return self._repo.ekle(veri)

    def guncelle(self, personel_id: str, veri: dict) -> None:
        """
        Personel bilgilerini günceller.
        tc_kimlik değiştirilemez.

        Raises: KayitBulunamadi
        """
        self.getir(personel_id)   # Varlık kontrolü

        veri = dict(veri)
        if "gorev_yeri_ad" in veri and "gorev_yeri_id" not in veri:
            veri["gorev_yeri_id"] = self._gy_id_bul(veri.pop("gorev_yeri_ad"))

        # tc_kimlik güncellenmesini engelle
        veri.pop("tc_kimlik", None)
        veri.pop("id", None)

        self._repo.guncelle(personel_id, veri)

    def pasife_al(self, personel_id: str,
                  ayrilik_tarihi: str,
                  ayrilik_nedeni: str = "") -> None:
        """
        Personeli pasife alır — fiziksel silme yok.

        Raises: KayitBulunamadi
        """
        p = self.getir(personel_id)
        if p.get("durum") == "ayrildi":
            raise PasifPersonelHatasi("Bu personel zaten ayrılmış.")

        parse_tarih_veya_hata(ayrilik_tarihi, "Ayrılış tarihi")

        self._repo.guncelle(personel_id, {
            "durum":          "ayrildi",
            "ayrilik_tarihi": ayrilik_tarihi,
            "ayrilik_nedeni": ayrilik_nedeni or "",
        })

    # ── Özel ──────────────────────────────────────────────────────

    def _gy_id_bul(self, gorev_yeri_ad: str) -> str | None:
        """Görev yeri adından ID döner. Bulunamazsa None."""
        if not gorev_yeri_ad:
            return None
        yerler = self._gy_repo.listele()
        for gy in yerler:
            if gy["ad"].strip().lower() == gorev_yeri_ad.strip().lower():
                return gy["id"]
        return None
