# -*- coding: utf-8 -*-
"""Kullanici ekleme is akisi."""
from __future__ import annotations

from app.exceptions import DogrulamaHatasi, KayitZatenVar
from app.validators import zorunlu


def execute(kullanici_repo, hash_fn, role_exists_fn, veri: dict) -> str:
    """Yeni kullanici olusturur ve ID dondurur."""
    ad = zorunlu(veri.get("ad"), "Kullanıcı adı")
    parola = zorunlu(veri.get("parola"), "Parola")
    rol = zorunlu(veri.get("rol"), "Rol")

    if not role_exists_fn(rol):
        raise DogrulamaHatasi(f"Geçersiz rol: {rol}")
    if len(parola) < 6:
        raise DogrulamaHatasi("Parola en az 6 karakter olmalıdır.")
    if kullanici_repo.ad_var_mi(ad):
        raise KayitZatenVar(f"Bu kullanıcı adı zaten kayıtlı: {ad}")

    return kullanici_repo.ekle(
        {
            "ad": ad,
            "sifre_hash": hash_fn(parola),
            "rol": rol,
            "aktif": bool(veri.get("aktif", True)),
            "sifre_degismeli": True,
            "personel_id": veri.get("personel_id"),
        }
    )
