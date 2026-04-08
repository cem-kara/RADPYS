# -*- coding: utf-8 -*-
"""Tum rollerin modul izin haritasi is akisi."""
from __future__ import annotations


def execute(rows: list[dict]) -> dict[str, set[str] | None]:
    """Policy satirlarindan rol-modul haritasi uretir."""
    rol_map: dict[str, list[dict]] = {}
    for row in rows:
        rol_map.setdefault(row["rol"], []).append(row)

    sonuc: dict[str, set[str] | None] = {}
    for rol_adi, kayitlar in rol_map.items():
        hepsi_izinli = all(int(k.get("izinli", 0)) for k in kayitlar)
        if hepsi_izinli and rol_adi == "admin":
            sonuc[rol_adi] = None
        else:
            sonuc[rol_adi] = {
                k["modul_id"] for k in kayitlar if int(k.get("izinli", 0))
            }
    return sonuc
