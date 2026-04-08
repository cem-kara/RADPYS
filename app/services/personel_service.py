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
from app.exceptions import KayitBulunamadi
from app.usecases.personel import personel_ekle, personel_guncelle, personel_pasife_al
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
        return personel_ekle(self._repo, self._gy_repo, veri)

    def guncelle(self, personel_id: str, veri: dict) -> None:
        """
        Personel bilgilerini günceller.
        tc_kimlik değiştirilemez.

        Raises: KayitBulunamadi
        """
        self.getir(personel_id)   # Varlık kontrolü
        personel_guncelle(self._repo, self._gy_repo, personel_id, veri)

    def pasife_al(self, personel_id: str,
                  ayrilik_tarihi: str,
                  ayrilik_nedeni: str = "") -> None:
        """
        Personeli pasife alır — fiziksel silme yok.

        Raises: KayitBulunamadi
        """
        p = self.getir(personel_id)
        personel_pasife_al(
            self._repo,
            p,
            personel_id,
            ayrilik_tarihi,
            ayrilik_nedeni,
        )
