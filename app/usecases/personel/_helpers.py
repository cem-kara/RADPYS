# -*- coding: utf-8 -*-
"""Personel use-case ortak yardimcilari."""
from __future__ import annotations


def gorev_yeri_id_bul(gorev_yeri_repo, gorev_yeri_ad: str) -> str | None:
    """Gorev yeri adindan ID dondurur. Bulunamazsa None."""
    if not gorev_yeri_ad:
        return None
    yerler = gorev_yeri_repo.listele()
    aranan = gorev_yeri_ad.strip().lower()
    for gy in yerler:
        if gy["ad"].strip().lower() == aranan:
            return gy["id"]
    return None
