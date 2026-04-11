# -*- coding: utf-8 -*-
"""
app/services/izin_service.py
──────────────────────────────
İzin iş mantığı.

Kurallar:
  - Çakışan tarihlere izin eklenemez
  - Sadece aktif izinler iptal edilebilir
  - Bakiye hesabı DB'ye yazılmaz, çalışma anında hesaplanır
  - Memuriyet başlama tarihine göre yıllık hak belirlenir (657 SK md.102)
"""
from __future__ import annotations

from datetime import date

from app.config import (
    LookupKategori,
    YILLIK_HAK_1_10,
    YILLIK_HAK_10P,
)
from app.date_utils import parse_date
from app.db.database import Database
from app.db.repos.izin_repo import IzinRepo
from app.db.repos.lookup_repo import LookupRepo
from app.db.repos.personel_repo import PersonelRepo
from app.exceptions import KayitBulunamadi
from app.usecases.izin import izin_ekle, izin_iptal


class IzinService:
    """
    İzin tablosu iş mantığı.

    Kullanım:
        svc = IzinService(db)
        pk  = svc.ekle({"personel_id": "...", "tur": "yillik", ...})
    """

    def __init__(self, db: Database):
        self._repo   = IzinRepo(db)
        self._p_repo = PersonelRepo(db)
        self._lookup = LookupRepo(db)

    # ── Sorgular ──────────────────────────────────────────────────

    def listele(
        self,
        personel_id: str | None = None,
        yil: int | None = None,
        durum: str | None = None,
    ) -> list[dict]:
        """İzin listesi — başlama tarihine göre azalan sıra."""
        return self._repo.listele(
            personel_id=personel_id, yil=yil, durum=durum
        )

    def getir(self, pk: str) -> dict:
        """
        Tek izin kaydı.
        Raises: KayitBulunamadi
        """
        row = self._repo.getir(pk)
        if not row:
            raise KayitBulunamadi(f"İzin kaydı bulunamadı: {pk}")
        return row

    def izin_turleri(self) -> list[str]:
        """Lookup'tan izin türü listesi."""
        return self._lookup.kategori(LookupKategori.IZIN_TUR)

    def personel_listesi(self) -> list[dict]:
        """Aktif personel listesi (id, ad, soyad, kadro_unvani)."""
        return self._p_repo.listele(aktif_only=True)

    def bakiye_hesapla(self, personel_id: str, yil: int) -> dict:
        """
        Yıllık izin bakiyesini hesaplar.

        Returns:
            {
                "hak":        int  — yıllık hak (gün)
                "kullanilan": int  — o yıl kullanılan (aktif kayıtlar)
                "kalan":      int  — kalan = hak - kullanılan
            }
        """
        p = self._p_repo.getir(personel_id)
        if not p:
            raise KayitBulunamadi(f"Personel bulunamadı: {personel_id}")
        hak = int(self.yillik_hak_hesapla(p.get("memuriyet_baslama")))
        kullanilan = self._repo.yillik_kullanim(personel_id, yil, tur="yillik")
        return {
            "hak": hak,
            "kullanilan": kullanilan,
            "kalan": max(0, hak - kullanilan),
        }

    # ── Yazma ──────────────────────────────────────────────────────

    def ekle(self, veri: dict) -> str:
        """
        Yeni izin kaydı ekler.
        Raises: DogrulamaHatasi, CakismaHatasi
        """
        return izin_ekle.execute(self._repo, veri)

    def iptal(self, pk: str) -> None:
        """
        İzni iptal eder.
        Raises: KayitBulunamadi, IsKuraliHatasi
        """
        izin_iptal.execute(self._repo, pk)

    # ── Statik yardımcılar ─────────────────────────────────────────

    @staticmethod
    def yillik_hak_hesapla(memuriyet_baslama, today: date | None = None) -> float:
        """657 SK md.102: memuriyet süresine göre yıllık hak."""
        start = parse_date(memuriyet_baslama)
        if not start:
            return YILLIK_HAK_1_10
        ref = today or date.today()
        hizmet_yili = max(0.0, (ref - start).days / 365.25)
        return YILLIK_HAK_10P if hizmet_yili >= 10 else YILLIK_HAK_1_10

    def hak_edis_bilgisi(self, memuriyet_baslama, today: date | None = None) -> dict:
        """Geriye dönük uyumluluk için korundu."""
        start = parse_date(memuriyet_baslama)
        ref = today or date.today()
        hizmet_yili = 0.0 if not start else max(0.0, (ref - start).days / 365.25)
        return {
            "hizmet_yili": round(hizmet_yili, 2),
            "yillik_hak": self.yillik_hak_hesapla(memuriyet_baslama, ref),
        }
