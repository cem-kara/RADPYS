# -*- coding: utf-8 -*-
"""app/security/policy.py — rol tabanlı policy yardımcıları."""
from __future__ import annotations

from app.exceptions import YetkiHatasi


def is_admin_session(oturum: dict | None) -> bool:
    """Oturum admin rolüne aitse True döner."""
    return str((oturum or {}).get("rol") or "") == "admin"


def require_admin_session(oturum: dict | None, mesaj: str) -> None:
    """Admin değilse YetkiHatasi fırlatır."""
    if not is_admin_session(oturum):
        raise YetkiHatasi(mesaj)
