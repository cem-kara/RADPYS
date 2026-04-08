# -*- coding: utf-8 -*-
"""app/db/repos/policy_repo.py — rbac_modul_izin tablosu SQL katmanı"""
from __future__ import annotations
from uuid import uuid4

from app.db.repos.base import BaseRepo


class PolicyRepo(BaseRepo):
    """rbac_modul_izin tablosu CRUD. Sadece SQL — iş mantığı yok."""

    def tum_izinler(self) -> list[dict]:
        return self._db.fetchall(
            "SELECT * FROM rbac_modul_izin ORDER BY rol, modul_id"
        )

    def tum_roller(self) -> list[str]:
        rows = self._db.fetchall(
            "SELECT DISTINCT rol FROM rbac_modul_izin ORDER BY rol"
        )
        return [str(r.get("rol")) for r in rows if r.get("rol")]

    def tum_moduller(self) -> list[str]:
        rows = self._db.fetchall(
            "SELECT DISTINCT modul_id FROM rbac_modul_izin ORDER BY modul_id"
        )
        return [str(r.get("modul_id")) for r in rows if r.get("modul_id")]

    def rol_var_mi(self, rol: str) -> bool:
        return bool(self._db.fetchval(
            "SELECT 1 FROM rbac_modul_izin WHERE rol = ? LIMIT 1",
            (rol,),
        ))

    def rol_ekle(self, rol: str, aktif_modul_seti: set[str] | None = None) -> None:
        tum_moduller = self.tum_moduller()
        aktif = set(aktif_modul_seti or set())
        for modul_id in tum_moduller:
            self._db.execute(
                "INSERT OR IGNORE INTO rbac_modul_izin (id, rol, modul_id, izinli) "
                "VALUES (?,?,?,?)",
                (uuid4().hex, rol, modul_id, 1 if modul_id in aktif else 0),
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
