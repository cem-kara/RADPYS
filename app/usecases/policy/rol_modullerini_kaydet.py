# -*- coding: utf-8 -*-
"""Rol modullerini kaydetme is akisi."""
from __future__ import annotations

from app.exceptions import YetkiHatasi


def execute(policy_repo, rol: str, modul_seti: set[str]) -> None:
    """Verilen rol icin modul izinlerini kaydeder."""
    if rol == "admin":
        raise YetkiHatasi("Admin rolünün modül izinleri değiştirilemez.")
    policy_repo.rol_modullerini_kaydet(rol, modul_seti)
