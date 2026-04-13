# -*- coding: utf-8 -*-
"""app/hesaplamalar.py - Fiili hizmet ortak hesaplama fonksiyonlari."""
from __future__ import annotations

import math
from datetime import date

from app.validators import is_gunu_say


def turkce_normalize_lower(text: str) -> str:
    """Turkce karakterleri normalize ederek kucuk harfe cevirir."""
    src = str(text or "").strip().lower()
    rep = {
        "ş": "s",
        "ı": "i",
        "ğ": "g",
        "ü": "u",
        "ö": "o",
        "ç": "c",
        "İ": "i",
        "Ş": "s",
        "Ğ": "g",
        "Ü": "u",
        "Ö": "o",
        "Ç": "c",
    }
    for old, new in rep.items():
        src = src.replace(old, new)
    return src


def donem_tarih_araligi(yil: int, donem: int) -> tuple[date, date]:
    """Donemi ayin 15'i ile sonraki ayin 14'u arasi olarak doner."""
    yil_int = int(yil)
    donem_int = int(donem)
    if donem_int < 1 or donem_int > 12:
        raise ValueError("Donem 1-12 araliginda olmalidir.")

    bas = date(yil_int, donem_int, 15)
    if donem_int == 12:
        bit = date(yil_int + 1, 1, 14)
    else:
        bit = date(yil_int, donem_int + 1, 14)
    return bas, bit


def fiili_saat_hesapla(aylik_gun: float, izin_gun: float, kosul: str, saat_katsayi: float = 7.0) -> float:
    """Kosul A icin net gun * katsayi hesaplar, diger kosullarda 0 doner."""
    kos = str(kosul or "").strip().upper()
    if kos != "A":
        return 0.0
    net_gun = max(0.0, float(aylik_gun or 0.0) - float(izin_gun or 0.0))
    return float(net_gun) * float(saat_katsayi)


def sua_hak_edis_hesapla(toplam_saat: float) -> int:
    """Toplam fiili saate gore hak edilen sua gununu hesaplar."""
    try:
        saat = float(toplam_saat)
    except (TypeError, ValueError):
        return 0
    if saat <= 0:
        return 0
    return min(30, max(1, int(math.ceil(saat / 50.0))))


def is_gunu_hesapla(bas: date, bit: date, tatiller: set[str] | None = None) -> int:
    """Iki tarih arasindaki is gununu (dahil) hesaplar."""
    return is_gunu_say(
        bas.strftime("%Y-%m-%d"),
        bit.strftime("%Y-%m-%d"),
        tatiller=tatiller or set(),
    )
