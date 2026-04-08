# -*- coding: utf-8 -*-
"""Personel ekleme is akisi."""
from __future__ import annotations

from app.exceptions import KayitZatenVar
from app.usecases.personel._helpers import gorev_yeri_id_bul
from app.validators import tc_dogrula_veya_hata, zorunlu


def execute(personel_repo, gorev_yeri_repo, veri: dict) -> str:
    """Yeni personel ekler ve olusan ID'yi dondurur."""
    tc = tc_dogrula_veya_hata(veri.get("tc_kimlik", ""))
    zorunlu(veri.get("ad"), "Ad")
    zorunlu(veri.get("soyad"), "Soyad")

    if personel_repo.tc_var_mi(tc):
        raise KayitZatenVar(f"Bu TC Kimlik No zaten kayıtlı: {tc}")

    payload = dict(veri)
    if "gorev_yeri_ad" in payload and "gorev_yeri_id" not in payload:
        payload["gorev_yeri_id"] = gorev_yeri_id_bul(
            gorev_yeri_repo,
            payload.pop("gorev_yeri_ad"),
        )

    return personel_repo.ekle(payload)
