# -*- coding: utf-8 -*-
"""Personel pasife alma is akisi."""
from __future__ import annotations

from app.exceptions import PasifPersonelHatasi
from app.validators import parse_tarih_veya_hata


def execute(
    personel_repo,
    mevcut_personel: dict,
    personel_id: str,
    ayrilik_tarihi: str,
    ayrilik_nedeni: str = "",
) -> None:
    """Personeli ayrildi durumuna getirir."""
    if mevcut_personel.get("durum") == "ayrildi":
        raise PasifPersonelHatasi("Bu personel zaten ayrılmış.")

    parse_tarih_veya_hata(ayrilik_tarihi, "Ayrılış tarihi")
    personel_repo.guncelle(
        personel_id,
        {
            "durum": "ayrildi",
            "ayrilik_tarihi": ayrilik_tarihi,
            "ayrilik_nedeni": ayrilik_nedeni or "",
        },
    )
