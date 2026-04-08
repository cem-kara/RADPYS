# -*- coding: utf-8 -*-
"""Kullanici rol guncelleme is akisi."""
from __future__ import annotations

from app.config import RBAC_ROLLER
from app.exceptions import DogrulamaHatasi


def execute(kullanici_repo, kullanici_id: str, rol: str) -> None:
    """Kullanicinin rolunu gunceller."""
    if rol not in RBAC_ROLLER:
        raise DogrulamaHatasi(f"Geçersiz rol: {rol}")
    kullanici_repo.guncelle(kullanici_id, {"rol": rol})
