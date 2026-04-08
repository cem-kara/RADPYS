# -*- coding: utf-8 -*-
"""app/security/session.py — oturum sözleşmesi yardımcıları."""
from __future__ import annotations

from app.config import RBAC_ROL_YETKILERI


def build_session(row: dict) -> dict:
    """Kullanici kaydindan standart oturum dict'i üretir."""
    rol = str(row.get("rol") or "kullanici")
    return {
        "id": row["id"],
        "ad": row["ad"],
        "rol": rol,
        "yetkiler": sorted(RBAC_ROL_YETKILERI.get(rol, set())),
        "sifre_degismeli": bool(int(row.get("sifre_degismeli", 0))),
        "son_giris": row.get("son_giris"),
    }
