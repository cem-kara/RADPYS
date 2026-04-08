# -*- coding: utf-8 -*-
"""Kullanici aktiflik degistirme is akisi."""
from __future__ import annotations


def execute(kullanici_repo, kullanici_id: str, aktif: bool) -> None:
    """Kullaniciyi aktif/pasif duruma getirir."""
    kullanici_repo.guncelle(kullanici_id, {"aktif": 1 if aktif else 0})
