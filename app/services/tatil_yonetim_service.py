# -*- coding: utf-8 -*-
"""app/services/tatil_yonetim_service.py - Tatil yonetim servisi."""
from __future__ import annotations

import re
import sqlite3

from app.db.database import Database
from app.db.repos.tatil_repo import TatilRepo
from app.exceptions import DogrulamaHatasi, KayitZatenVar, KayitBulunamadi

_TARIH_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class TatilYonetimService:
    """tatil tablosu icin is kurali ve dogrulama katmani."""

    def __init__(self, db: Database):
        self._repo = TatilRepo(db)

    # ── yardimcilar ─────────────────────────────────────────────────

    @staticmethod
    def _dogrula_tarih(tarih: str) -> str:
        t = str(tarih or "").strip()
        if not t:
            raise DogrulamaHatasi("Tarih zorunludur.")
        if not _TARIH_RE.match(t):
            raise DogrulamaHatasi("Tarih formati YYYY-AA-GG olmalidir.")
        return t

    @staticmethod
    def _dogrula_ad(ad: str) -> str:
        a = str(ad or "").strip()
        if not a:
            raise DogrulamaHatasi("Tatil adi zorunludur.")
        return a

    @staticmethod
    def _dogrula_tur(tur: str) -> str:
        t = str(tur or "").strip()
        if t not in ("resmi", "dini"):
            raise DogrulamaHatasi("Tur 'resmi' veya 'dini' olmalidir.")
        return t

    @staticmethod
    def _dogrula_yarim_gun(yarim_gun: bool | int) -> bool:
        return bool(int(yarim_gun))

    # ── sorgu ────────────────────────────────────────────────────────

    def listele(
        self,
        yil: int | None = None,
        tur: str | None = None,
    ) -> list[dict]:
        return self._repo.listele(yil=yil, tur=tur)

    def mevcut_yillar(self) -> list[int]:
        return self._repo.mevcut_yillar()

    # ── yazma ────────────────────────────────────────────────────────

    def ekle(self, tarih: str, ad: str, tur: str, yarim_gun: bool | int = False) -> None:
        tarih = self._dogrula_tarih(tarih)
        ad = self._dogrula_ad(ad)
        tur = self._dogrula_tur(tur)
        yarim = self._dogrula_yarim_gun(yarim_gun)
        if self._repo.tarih_var_mi(tarih):
            raise KayitZatenVar(f"{tarih} tarihli tatil zaten kayitli.")
        try:
            self._repo.ekle(tarih, ad, tur, 1 if yarim else 0)
        except sqlite3.IntegrityError as exc:
            raise KayitZatenVar("Bu tarih zaten kayitli.") from exc

    def guncelle(self, tarih: str, ad: str, tur: str, yarim_gun: bool | int = False) -> None:
        tarih = self._dogrula_tarih(tarih)
        ad = self._dogrula_ad(ad)
        tur = self._dogrula_tur(tur)
        yarim = self._dogrula_yarim_gun(yarim_gun)
        if not self._repo.tarih_var_mi(tarih):
            raise KayitBulunamadi(f"{tarih} tarihinde kayitli tatil bulunamadi.")
        self._repo.guncelle(tarih, ad, tur, 1 if yarim else 0)

    def sil(self, tarih: str) -> None:
        t = self._dogrula_tarih(tarih)
        if not self._repo.tarih_var_mi(t):
            raise KayitBulunamadi(f"{t} tarihinde kayitli tatil bulunamadi.")
        self._repo.sil(t)
