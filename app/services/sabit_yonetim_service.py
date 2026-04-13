# -*- coding: utf-8 -*-
"""app/services/sabit_yonetim_service.py - DB sabitleri yonetim servisi."""
from __future__ import annotations

import sqlite3

from app.db.database import Database
from app.db.repos.sabit_repo import SabitRepo
from app.exceptions import DogrulamaHatasi, KayitZatenVar


class SabitYonetimService:
    """Lookup ve gorev_yeri sabitleri icin is kurali katmani."""

    def __init__(self, db: Database):
        self._repo = SabitRepo(db)

    # ── lookup ──────────────────────────────────────────────────────

    def lookup_kategoriler(self) -> list[str]:
        return self._repo.lookup_kategoriler()

    def lookup_listele(self, kategori: str | None = None, include_pasif: bool = True) -> list[dict]:
        return self._repo.lookup_listele(kategori=kategori, include_pasif=include_pasif)

    def lookup_ekle(self, kategori: str, deger: str, siralama: int = 0, aktif: bool = True) -> str:
        kat = str(kategori or "").strip()
        val = str(deger or "").strip()
        if not kat:
            raise DogrulamaHatasi("Kategori zorunludur.")
        if not val:
            raise DogrulamaHatasi("Deger zorunludur.")
        try:
            return self._repo.lookup_ekle(kat, val, int(siralama), 1 if aktif else 0)
        except sqlite3.IntegrityError as exc:
            if "UNIQUE" in str(exc).upper():
                raise KayitZatenVar("Bu kategori icin ayni deger zaten var.") from exc
            raise

    def lookup_guncelle(self, kayit_id: str, deger: str, siralama: int, aktif: bool) -> None:
        kid = str(kayit_id or "").strip()
        val = str(deger or "").strip()
        if not kid:
            raise DogrulamaHatasi("Guncellenecek lookup kaydi secilmedi.")
        if not val:
            raise DogrulamaHatasi("Deger zorunludur.")
        try:
            self._repo.lookup_guncelle(kid, val, int(siralama), 1 if aktif else 0)
        except sqlite3.IntegrityError as exc:
            if "UNIQUE" in str(exc).upper():
                raise KayitZatenVar("Bu kategori icin ayni deger zaten var.") from exc
            raise

    def lookup_aktiflik_degistir(self, kayit_id: str, aktif: bool) -> None:
        kid = str(kayit_id or "").strip()
        if not kid:
            raise DogrulamaHatasi("Aktif/pasif degistirmek icin kayit secin.")
        self._repo.lookup_aktiflik_guncelle(kid, 1 if aktif else 0)

    # ── gorev_yeri ──────────────────────────────────────────────────

    def gorev_yeri_listele(self, include_pasif: bool = True) -> list[dict]:
        return self._repo.gorev_yeri_listele(include_pasif=include_pasif)

    def gorev_yeri_ekle(
        self,
        ad: str,
        kisaltma: str | None = None,
        sua_hakki: bool = False,
        aktif: bool = True,
    ) -> str:
        name = str(ad or "").strip()
        kis = str(kisaltma or "").strip() or None
        if not name:
            raise DogrulamaHatasi("Gorev yeri adi zorunludur.")
        try:
            return self._repo.gorev_yeri_ekle(name, kis, 1 if sua_hakki else 0, 1 if aktif else 0)
        except sqlite3.IntegrityError as exc:
            if "UNIQUE" in str(exc).upper():
                raise KayitZatenVar("Bu gorev yeri adi zaten var.") from exc
            raise

    def gorev_yeri_guncelle(
        self,
        kayit_id: str,
        ad: str,
        kisaltma: str | None,
        sua_hakki: bool,
        aktif: bool,
    ) -> None:
        kid = str(kayit_id or "").strip()
        name = str(ad or "").strip()
        kis = str(kisaltma or "").strip() or None
        if not kid:
            raise DogrulamaHatasi("Guncellenecek gorev yeri secilmedi.")
        if not name:
            raise DogrulamaHatasi("Gorev yeri adi zorunludur.")
        try:
            self._repo.gorev_yeri_guncelle(kid, name, kis, 1 if sua_hakki else 0, 1 if aktif else 0)
        except sqlite3.IntegrityError as exc:
            if "UNIQUE" in str(exc).upper():
                raise KayitZatenVar("Bu gorev yeri adi zaten var.") from exc
            raise

    def gorev_yeri_aktiflik_degistir(self, kayit_id: str, aktif: bool) -> None:
        kid = str(kayit_id or "").strip()
        if not kid:
            raise DogrulamaHatasi("Aktif/pasif degistirmek icin kayit secin.")
        self._repo.gorev_yeri_aktiflik_guncelle(kid, 1 if aktif else 0)
