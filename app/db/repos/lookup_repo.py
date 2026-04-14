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

    def deger_var_mi(self, kategori: str, deger: str) -> bool:
        return bool(self._db.fetchval(
            "SELECT 1 FROM lookup WHERE kategori=? AND deger=?",
            (kategori, deger),
        ))

    def deger_ekle(self, kategori: str, deger: str) -> None:
        """Kategoriye yeni bir değer ekler. Zaten varsa sessizce atlar."""
        if self.deger_var_mi(kategori, deger):
            return
        maks = self._db.fetchval(
            "SELECT COALESCE(MAX(siralama), -1) FROM lookup WHERE kategori=?",
            (kategori,),
        ) or 0
        self._db.execute(
            "INSERT OR IGNORE INTO lookup (id, kategori, deger, siralama, aktif) "
            "VALUES (?,?,?,?,1)",
            (self._new_id(), kategori, deger, int(maks) + 1),
        )

    @staticmethod
    def _norm_text(text: str) -> str:
        map_ = str.maketrans({
            "c": "c", "C": "c",
            "g": "g", "G": "g",
            "i": "i", "I": "i",
            "o": "o", "O": "o",
            "s": "s", "S": "s",
            "u": "u", "U": "u",
            "ç": "c", "Ç": "c",
            "ğ": "g", "Ğ": "g",
            "ı": "i", "İ": "i",
            "ö": "o", "Ö": "o",
            "ş": "s", "Ş": "s",
            "ü": "u", "Ü": "u",
        })
        normalized = str(text or "").translate(map_).lower()
        return " ".join(normalized.replace("_", " ").replace("-", " ").split())

    def alias_ekle(self, kategori: str, alias: str, lookup_deger: str, kaynak: str = "manuel") -> None:
        alias_norm = self._norm_text(alias)
        if not alias_norm:
            return
        self._db.execute(
            "INSERT OR REPLACE INTO lookup_alias "
            "(id, kategori, alias, alias_norm, lookup_deger, aktif, kaynak) "
            "VALUES (?, ?, ?, ?, ?, 1, ?)",
            (self._new_id(), kategori, alias, alias_norm, lookup_deger, kaynak),
        )

    def alias_ile_getir(self, kategori: str, deger: str) -> str | None:
        alias_norm = self._norm_text(deger)
        if not alias_norm:
            return None
        row = self._db.fetchone(
            "SELECT lookup_deger FROM lookup_alias "
            "WHERE kategori=? AND alias_norm=? AND aktif=1",
            (kategori, alias_norm),
        )
        return str(row.get("lookup_deger") or "") if row else None


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
