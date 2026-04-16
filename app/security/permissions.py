# -*- coding: utf-8 -*-
"""app/security/permissions.py — merkezi eylem/yetki kontrolleri."""
from __future__ import annotations

from app.config import RBAC_ROL_YETKILERI
from app.exceptions import YetkiHatasi
from app.security.permission_messages import permission_denied_message


def _oturum_yetkileri(oturum: dict | None) -> set[str]:
    """Oturumdaki yetkileri döner; yoksa role göre fallback üretir."""
    o = oturum or {}
    if "yetkiler" in o and o.get("yetkiler") is not None:
        return set(o.get("yetkiler", []))
    rol = str(o.get("rol") or "kullanici")
    return set(RBAC_ROL_YETKILERI.get(rol, set()))


def has_permission(oturum: dict | None, yetki: str) -> bool:
    """Oturumun istenen eylem yetkisine sahip olup olmadığını döner."""
    return yetki in _oturum_yetkileri(oturum)


def require_permission(oturum: dict | None, yetki: str) -> None:
    """Yetki yoksa YetkiHatasi firlatir."""
    if not has_permission(oturum, yetki):
        raise YetkiHatasi(permission_denied_message(yetki))
