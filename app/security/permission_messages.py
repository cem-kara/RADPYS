# -*- coding: utf-8 -*-
"""Merkezi yetki hata/uyari mesaji yardimcilari."""
from __future__ import annotations

_PERMISSION_MESSAGES: dict[str, str] = {
    "personel.ekle": "Bu islem icin personel ekleme yetkiniz yok.",
    "personel.guncelle": "Bu islem icin personel guncelleme yetkiniz yok.",
    "personel.pasife_al": "Bu islem icin personel pasife alma yetkiniz yok.",
    "kullanici.goruntule": "Bu islem icin kullanici goruntuleme yetkiniz yok.",
    "kullanici.olustur": "Bu islem icin kullanici olusturma yetkiniz yok.",
    "kullanici.guncelle": "Bu islem icin kullanici guncelleme yetkiniz yok.",
    "kullanici.pasife_al": "Bu islem icin kullanici pasife alma yetkiniz yok.",
}


def permission_denied_message(permission: str) -> str:
    key = str(permission or "").strip()
    if key in _PERMISSION_MESSAGES:
        return _PERMISSION_MESSAGES[key]
    return f"Bu islem icin yetkiniz yok: {key}" if key else "Bu islem icin yetkiniz yok."


def admin_required_message() -> str:
    return "Bu islem yalnizca admin yetkisi ile yapilabilir."
