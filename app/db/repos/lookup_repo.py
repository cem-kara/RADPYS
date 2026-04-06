# -*- coding: utf-8 -*-
"""app/db/repos/lookup_repo.py — Lookup + GorevYeri repo'ları"""
from __future__ import annotations
from app.db.repos.base import BaseRepo


class LookupRepo(BaseRepo):
    """
    lookup tablosu — dropdown listelerini sağlar.
    """

    def kategori(self, kategori: str) -> list[str]:
        """Kategoriye ait aktif değerleri sıralı döner."""
        rows = self._db.fetchall(
            "SELECT deger FROM lookup "
            "WHERE kategori = ? AND aktif = 1 "
            "ORDER BY siralama, deger",
            (kategori,),
        )
        return [r["deger"] for r in rows]

    def tum_kategoriler(self) -> dict[str, list[str]]:
        """Tüm kategorileri {kategori: [deger, ...]} dict'i olarak döner."""
        rows = self._db.fetchall(
            "SELECT kategori, deger FROM lookup "
            "WHERE aktif = 1 ORDER BY kategori, siralama, deger"
        )
        sonuc: dict[str, list[str]] = {}
        for r in rows:
            sonuc.setdefault(r["kategori"], []).append(r["deger"])
        return sonuc


class GorevYeriRepo(BaseRepo):
    """gorev_yeri tablosu."""

    def listele(self, aktif_only: bool = True) -> list[dict]:
        sql = "SELECT * FROM gorev_yeri"
        if aktif_only:
            sql += " WHERE aktif = 1"
        sql += " ORDER BY ad"
        return self._db.fetchall(sql)

    def getir(self, gorev_yeri_id: str) -> dict | None:
        return self._db.fetchone(
            "SELECT * FROM gorev_yeri WHERE id = ?",
            (gorev_yeri_id,),
        )

    def ad_listesi(self, aktif_only: bool = True) -> list[str]:
        rows = self.listele(aktif_only)
        return [r["ad"] for r in rows]
