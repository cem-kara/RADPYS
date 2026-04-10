# -*- coding: utf-8 -*-
"""app/db/repos/auth_repository.py - personel onboarding auth islemleri."""
from __future__ import annotations

from app.db.repos.base import BaseRepo
from app.db.repos.kullanici_repo import KullaniciRepo
from app.db.repos.policy_repo import PolicyRepo


class AuthRepository(BaseRepo):
    """Kullanici ve rol atama icin birlesik repository yardimcisi."""

    def __init__(self, db):
        super().__init__(db)
        self._kullanici = KullaniciRepo(db)
        self._policy = PolicyRepo(db)

    def username_exists(self, username: str) -> bool:
        return self._kullanici.ad_var_mi(username)

    def personel_user_getir(self, personel_id: str) -> dict | None:
        return self._db.fetchone(
            "SELECT * FROM kullanici WHERE personel_id=? LIMIT 1",
            (personel_id,),
        )

    def ensure_role_exists(self, role: str, base_role: str = "kullanici") -> None:
        if self._policy.rol_var_mi(role):
            return

        base_rows = self._policy.rol_izinleri(base_role)
        aktif_moduller = {
            str(r.get("modul_id"))
            for r in base_rows
            if int(r.get("izinli") or 0)
        }
        self._policy.rol_ekle(role, aktif_moduller)

    def create_user(
        self,
        username: str,
        password_hash: str,
        personel_id: str,
        role: str = "operator",
        force_password_change: bool = True,
    ) -> str:
        return self._kullanici.ekle(
            {
                "ad": username,
                "sifre_hash": password_hash,
                "personel_id": personel_id,
                "rol": role,
                "aktif": True,
                "sifre_degismeli": force_password_change,
            }
        )

    def assign_role(self, user_id: str, role: str) -> None:
        self._kullanici.guncelle(user_id, {"rol": role})
