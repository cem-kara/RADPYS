# -*- coding: utf-8 -*-
"""Sifre hashleme ve dogrulama yardimcilari."""
from __future__ import annotations

import bcrypt


class PasswordHasher:
    """bcrypt tabanli sifre hashleyici."""

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
        except Exception:
            return False
