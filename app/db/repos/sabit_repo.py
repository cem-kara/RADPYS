# -*- coding: utf-8 -*-
"""app/db/repos/sabit_repo.py - lookup ve gorev_yeri sabitleri icin SQL katmani."""
from __future__ import annotations

from app.db.repos.base import BaseRepo


class SabitRepo(BaseRepo):
    """Yonetim ekraninda duzenlenecek sabit tablolarin repo katmani."""

    # ── lookup ──────────────────────────────────────────────────────

    def lookup_kategoriler(self) -> list[str]:
        rows = self._db.fetchall(
            "SELECT DISTINCT kategori FROM lookup ORDER BY kategori"
        )
        return [str(r.get("kategori") or "") for r in rows if str(r.get("kategori") or "").strip()]

    def lookup_listele(self, kategori: str | None = None, include_pasif: bool = True) -> list[dict]:
        sql = "SELECT id, kategori, deger, siralama, aktif FROM lookup WHERE 1=1"
        params: list = []
        if kategori:
            sql += " AND kategori = ?"
            params.append(str(kategori))
        if not include_pasif:
            sql += " AND aktif = 1"
        sql += " ORDER BY kategori, siralama, deger"
        return self._db.fetchall(sql, tuple(params))

    def lookup_ekle(self, kategori: str, deger: str, siralama: int = 0, aktif: int = 1) -> str:
        sid = self._new_id()
        self._db.execute(
            "INSERT INTO lookup (id, kategori, deger, siralama, aktif) VALUES (?,?,?,?,?)",
            (sid, kategori, deger, int(siralama), int(aktif)),
        )
        return sid

    def lookup_guncelle(self, kayit_id: str, deger: str, siralama: int, aktif: int) -> None:
        self._db.execute(
            "UPDATE lookup SET deger=?, siralama=?, aktif=? WHERE id=?",
            (deger, int(siralama), int(aktif), kayit_id),
        )

    def lookup_aktiflik_guncelle(self, kayit_id: str, aktif: int) -> None:
        self._db.execute("UPDATE lookup SET aktif=? WHERE id=?", (int(aktif), kayit_id))

    # ── gorev_yeri ──────────────────────────────────────────────────

    def gorev_yeri_listele(self, include_pasif: bool = True) -> list[dict]:
        sql = "SELECT id, ad, kisaltma, sua_hakki, aktif FROM gorev_yeri"
        if not include_pasif:
            sql += " WHERE aktif = 1"
        sql += " ORDER BY ad"
        return self._db.fetchall(sql)

    def gorev_yeri_ekle(self, ad: str, kisaltma: str | None, sua_hakki: int = 0, aktif: int = 1) -> str:
        sid = self._new_id()
        self._db.execute(
            "INSERT INTO gorev_yeri (id, ad, kisaltma, sua_hakki, aktif) VALUES (?,?,?,?,?)",
            (sid, ad, kisaltma, int(sua_hakki), int(aktif)),
        )
        return sid

    def gorev_yeri_guncelle(
        self,
        kayit_id: str,
        ad: str,
        kisaltma: str | None,
        sua_hakki: int,
        aktif: int,
    ) -> None:
        self._db.execute(
            "UPDATE gorev_yeri SET ad=?, kisaltma=?, sua_hakki=?, aktif=? WHERE id=?",
            (ad, kisaltma, int(sua_hakki), int(aktif), kayit_id),
        )

    def gorev_yeri_aktiflik_guncelle(self, kayit_id: str, aktif: int) -> None:
        self._db.execute("UPDATE gorev_yeri SET aktif=? WHERE id=?", (int(aktif), kayit_id))
