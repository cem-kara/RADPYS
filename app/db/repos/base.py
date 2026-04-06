# -*- coding: utf-8 -*-
"""
app/db/repos/base.py
────────────────────
Repository taban sınıfı.
SQL string'leri subclass'ta yazılır — bu sınıfta iş mantığı yok.
"""
from __future__ import annotations
from uuid import uuid4
from app.db.database import Database


class BaseRepo:
    """
    Minimal taban — sadece DB erişimi ve ID üretimi.
    Her subclass kendi SQL'ini açıkça yazar.
    """

    def __init__(self, db: Database):
        self._db = db

    def _new_id(self) -> str:
        """Yeni UUID üretir (32 hex karakter)."""
        return uuid4().hex
