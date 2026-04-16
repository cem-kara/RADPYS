# -*- coding: utf-8 -*-
"""Personel guncelleme is akisi."""
from __future__ import annotations

from app.usecases.personel._helpers import gorev_yeri_id_bul
from app.validators import bugun


def execute(personel_repo, gorev_yeri_repo, personel_id: str, veri: dict) -> None:
    """Personel alanlarini gunceller; tc_kimlik ve id korunur."""
    mevcut = personel_repo.getir(personel_id) or {}
    onceki_gorev_yeri_id = str(mevcut.get("gorev_yeri_id") or "").strip() or None

    payload = dict(veri)
    if "gorev_yeri_ad" in payload and "gorev_yeri_id" not in payload:
        payload["gorev_yeri_id"] = gorev_yeri_id_bul(
            gorev_yeri_repo,
            payload.pop("gorev_yeri_ad"),
        )

    gorev_yeri_baslama = str(
        payload.pop("gorev_yeri_baslama", "")
        or payload.get("memuriyet_baslama")
        or bugun()
    )

    payload.pop("tc_kimlik", None)
    payload.pop("id", None)

    yeni_gorev_yeri_id = (
        str(payload.get("gorev_yeri_id") or "").strip() or None
        if "gorev_yeri_id" in payload
        else onceki_gorev_yeri_id
    )

    personel_repo.guncelle(personel_id, payload)

    if "gorev_yeri_id" not in payload:
        return

    if yeni_gorev_yeri_id == onceki_gorev_yeri_id:
        return

    if onceki_gorev_yeri_id:
        personel_repo.aktif_gorev_gecmisini_kapat(personel_id, bugun())

    if yeni_gorev_yeri_id:
        personel_repo.gorev_gecmisi_ekle(
            personel_id,
            yeni_gorev_yeri_id,
            gorev_yeri_baslama,
            aciklama="Gorev yeri degisikligi",
        )
