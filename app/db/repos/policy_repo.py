# -*- coding: utf-8 -*-
"""app/db/repos/policy_repo.py — rbac_modul_izin tablosu SQL katmanı"""
from __future__ import annotations
from app.db.repos.base import BaseRepo


class PolicyRepo(BaseRepo):
    """rbac_modul_izin tablosu CRUD. Sadece SQL — iş mantığı yok."""

    def tum_izinler(self) -> list[dict]:
        return self._db.fetchall(
            "SELECT * FROM rbac_modul_izin ORDER BY rol, modul_id"
        )

    def rol_izinleri(self, rol: str) -> list[dict]:
        return self._db.fetchall(
            "SELECT modul_id, izinli FROM rbac_modul_izin WHERE rol=?",
            (rol,),
        )

    def izin_guncelle(self, rol: str, modul_id: str, izinli: bool) -> None:
        self._db.execute(
            "UPDATE rbac_modul_izin SET izinli=? WHERE rol=? AND modul_id=?",
            (1 if izinli else 0, rol, modul_id),
        )

    def rol_modullerini_kaydet(self, rol: str, aktif_modul_seti: set[str]) -> None:
        """Verilen rolün tüm modül izinlerini toplu günceller."""
        rows = self._db.fetchall(
            "SELECT modul_id FROM rbac_modul_izin WHERE rol=?", (rol,)
        )
        for row in rows:
            mid = row["modul_id"]
            izinli = 1 if mid in aktif_modul_seti else 0
            self._db.execute(
                "UPDATE rbac_modul_izin SET izinli=? WHERE rol=? AND modul_id=?",
                (izinli, rol, mid),
            )
