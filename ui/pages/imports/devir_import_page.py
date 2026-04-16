# -*- coding: utf-8 -*-
"""Personel izin devir/bakiye referans verisini Excel'den DB'ye aktarır."""
from __future__ import annotations

import datetime

from app.date_utils import parse_date
from app.db.repos.izin_devir_repo import IzinDevirRepo
from app.exceptions import DogrulamaHatasi
from app.services.excel_import_service import AlanTanimi, ImportKonfig
from app.services.personel_service import PersonelService
from app.validators import validate_tc_kimlik_no
from ui.pages.imports.components.base_import_page import BaseImportPage


def _tc_v(v):
    text = _tc_norm(v)
    if not text:
        return True, ""
    return validate_tc_kimlik_no(text), "Gecersiz TC Kimlik No"


def _tc_norm(v) -> str:
    raw = str(v or "").strip()
    if raw.endswith(".0"):
        raw = raw[:-2]
    return "".join(ch for ch in raw if ch.isdigit())


def _gun_v(v):
    text = str(v or "").strip()
    if not text:
        return True, ""
    try:
        return int(float(text)) >= 0, "Gun 0 veya pozitif olmalidir"
    except (TypeError, ValueError):
        return False, "Gecersiz sayi"


def _normalize(kayit: dict) -> dict:
    kayit["tc_kimlik"] = _tc_norm(kayit.get("tc_kimlik"))

    for key in ("hak_gun", "devir_gun"):
        raw = str(kayit.get(key) or "").strip()
        try:
            kayit[key] = max(0, int(float(raw))) if raw else 0
        except (TypeError, ValueError):
            kayit[key] = 0

    yil_raw = str(kayit.get("yil") or "").strip()
    if yil_raw:
        try:
            kayit["yil"] = int(float(yil_raw))
        except (TypeError, ValueError):
            kayit["yil"] = datetime.date.today().year
    else:
        kayit["yil"] = datetime.date.today().year

    return kayit


class _DevirImportAdapter:
    """Import satirini izin_devir tablosuna upsert yapar."""

    def __init__(self, db):
        self._personel = PersonelService(db)
        self._devir_repo = IzinDevirRepo(db)

    def ekle(self, kayit: dict) -> str:
        tc = _tc_norm(kayit.get("tc_kimlik"))
        if not tc:
            raise DogrulamaHatasi("TC Kimlik No zorunludur.")
        if not validate_tc_kimlik_no(tc):
            raise DogrulamaHatasi(f"Gecersiz TC Kimlik No: {tc}")

        personel = self._personel.tc_ile_getir(tc)
        personel_id = str(personel.get("id") or "").strip()
        if not personel_id:
            raise DogrulamaHatasi(f"TC ile personel bulundu ama ID bos: {tc}")

        yil = int(kayit.get("yil") or datetime.date.today().year)
        hak_gun = int(kayit.get("hak_gun") or 0)
        devir_gun = int(kayit.get("devir_gun") or 0)

        return self._devir_repo.kaydet(personel_id, yil, hak_gun, devir_gun)

    def guncelle_veya_ekle(self, kayit: dict) -> str:
        return self.ekle(kayit)


def _devir_servis(db):
    return _DevirImportAdapter(db)


KONFIG = ImportKonfig(
    baslik="Izin Devir / Bakiye Referans Aktarma",
    servis_fabrika=_devir_servis,
    servis_metod="ekle",
    servis_metod_upsert="guncelle_veya_ekle",
    tablo_adi="izin_devir",
    normalize_fn=_normalize,
    alanlar=[
        AlanTanimi(
            "tc_kimlik", "TC Kimlik No", "tc",
            zorunlu=True, validator=_tc_v,
            anahtar_kelimeler=["tc", "tckimlik", "kimlikno", "kimlik", "tckn"],
        ),
        AlanTanimi(
            "yil", "Yil", "int",
            anahtar_kelimeler=["yil", "year"],
        ),
        AlanTanimi(
            "hak_gun", "Hak Edilen (Gun)", "int",
            validator=_gun_v,
            anahtar_kelimeler=["hakedilen", "hak", "hakedis", "yaklasikhak"],
        ),
        AlanTanimi(
            "devir_gun", "Devir (Gun)", "int",
            validator=_gun_v,
            anahtar_kelimeler=["devir", "devrizin", "devirgun", "carryover"],
        ),
    ],
)


class DevirImportPage(BaseImportPage):
    def _konfig(self) -> ImportKonfig:
        return KONFIG
