# -*- coding: utf-8 -*-
"""Personel use-case fonksiyonlari."""

from app.usecases.personel.personel_ekle import execute as personel_ekle
from app.usecases.personel.personel_guncelle import execute as personel_guncelle
from app.usecases.personel.personel_pasife_al import execute as personel_pasife_al

__all__ = ["personel_ekle", "personel_guncelle", "personel_pasife_al"]
