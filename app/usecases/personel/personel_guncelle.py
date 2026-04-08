# -*- coding: utf-8 -*-
"""Personel guncelleme is akisi."""
from __future__ import annotations

from app.usecases.personel._helpers import gorev_yeri_id_bul


def execute(personel_repo, gorev_yeri_repo, personel_id: str, veri: dict) -> None:
    """Personel alanlarini gunceller; tc_kimlik ve id korunur."""
    payload = dict(veri)
    if "gorev_yeri_ad" in payload and "gorev_yeri_id" not in payload:
        payload["gorev_yeri_id"] = gorev_yeri_id_bul(
            gorev_yeri_repo,
            payload.pop("gorev_yeri_ad"),
        )

    payload.pop("tc_kimlik", None)
    payload.pop("id", None)
    personel_repo.guncelle(personel_id, payload)
