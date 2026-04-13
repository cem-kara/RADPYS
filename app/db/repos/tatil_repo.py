# -*- coding: utf-8 -*-
"""app/db/repos/tatil_repo.py - tatil tablosu icin SQL katmani."""
from __future__ import annotations

from app.db.repos.base import BaseRepo


class TatilRepo(BaseRepo):
    """Resmi ve dini tatil kayitlari icin repo."""

    def listele(
        self,
        yil: int | None = None,
        tur: str | None = None,
    ) -> list[dict]:
        sql = "SELECT tarih, ad, tur, yarim_gun FROM tatil WHERE 1=1"
        params: list = []
        if yil is not None:
            sql += " AND strftime('%Y', tarih) = ?"
            params.append(str(yil))
        if tur:
            sql += " AND tur = ?"
            params.append(str(tur))
        sql += " ORDER BY tarih"
        return self._db.fetchall(sql, tuple(params))

    def mevcut_yillar(self) -> list[int]:
        rows = self._db.fetchall(
            "SELECT DISTINCT CAST(strftime('%Y', tarih) AS INTEGER) AS yil "
            "FROM tatil ORDER BY yil DESC"
        )
        return [int(r["yil"]) for r in rows if r.get("yil")]

    def ekle(self, tarih: str, ad: str, tur: str, yarim_gun: int = 0) -> None:
        self._db.execute(
            "INSERT INTO tatil (tarih, ad, tur, yarim_gun) VALUES (?,?,?,?)",
            (tarih, ad, tur, int(yarim_gun)),
        )

    def guncelle(self, tarih: str, ad: str, tur: str, yarim_gun: int = 0) -> None:
        self._db.execute(
            "UPDATE tatil SET ad=?, tur=?, yarim_gun=? WHERE tarih=?",
            (ad, tur, int(yarim_gun), tarih),
        )

    def sil(self, tarih: str) -> None:
        self._db.execute("DELETE FROM tatil WHERE tarih=?", (tarih,))

    def tarih_var_mi(self, tarih: str) -> bool:
        return bool(
            self._db.fetchval("SELECT 1 FROM tatil WHERE tarih=?", (tarih,))
        )
