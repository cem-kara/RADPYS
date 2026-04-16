# -*- coding: utf-8 -*-
"""Personel import iskeleti."""
from __future__ import annotations

from app.services.excel_import_service import AlanTanimi, ImportKonfig
from app.services.personel_service import PersonelService
from app.text_utils import turkish_title_case
from app.validators import validate_email, validate_phone_number, validate_tc_kimlik_no
from ui.pages.imports.components.base_import_page import BaseImportPage


def _tc_v(v):
    text = _tc_norm(v)
    if not text:
        return False, "TC Kimlik No zorunlu"
    return validate_tc_kimlik_no(text), "Gecersiz TC Kimlik No"


def _tc_norm(v) -> str:
    raw = str(v or "").strip()
    if raw.endswith(".0"):
        raw = raw[:-2]
    return "".join(ch for ch in raw if ch.isdigit())


def _mail_v(v):
    if not str(v or "").strip():
        return True, ""
    return validate_email(v), "Gecersiz e-posta"


def _tel_v(v):
    if not str(v or "").strip():
        return True, ""
    return validate_phone_number(v), "Gecersiz telefon"


def _normalize(kayit: dict) -> dict:
    kayit["tc_kimlik"] = _tc_norm(kayit.get("tc_kimlik"))

    ad_soyad = str(kayit.get("ad_soyad") or "").strip()
    if ad_soyad and (not str(kayit.get("ad") or "").strip() or not str(kayit.get("soyad") or "").strip()):
        parcalar = [p for p in ad_soyad.split() if p]
        if parcalar:
            kayit["ad"] = " ".join(parcalar[:-1]) if len(parcalar) > 1 else parcalar[0]
            kayit["soyad"] = parcalar[-1] if len(parcalar) > 1 else ""

    ad = str(kayit.get("ad") or "").strip()
    soyad = str(kayit.get("soyad") or "").strip()
    if ad:
        kayit["ad"] = turkish_title_case(ad)
    if soyad:
        kayit["soyad"] = turkish_title_case(soyad)

    for key in ("dogum_yeri", "hizmet_sinifi", "kadro_unvani", "gorev_yeri_ad"):
        text = str(kayit.get(key) or "").strip()
        if text:
            kayit[key] = turkish_title_case(text)

    return kayit


class _PersonelImportAdapter:
    def __init__(self, db):
        self._svc = PersonelService(db)

    def ekle(self, kayit: dict) -> str:
        return self._svc.ekle(kayit)

    def guncelle_veya_ekle_import(self, kayit: dict) -> str:
        return self._svc.guncelle_veya_ekle_import(kayit)


def _personel_servis(db):
    return _PersonelImportAdapter(db)


KONFIG = ImportKonfig(
    baslik="Toplu Personel Ice Aktarma",
    servis_fabrika=_personel_servis,
    servis_metod="ekle",
    servis_metod_upsert="guncelle_veya_ekle_import",
    tablo_adi="personel",
    normalize_fn=_normalize,
    alanlar=[
        AlanTanimi(
            "tc_kimlik",
            "TC Kimlik No",
            "tc",
            zorunlu=True,
            validator=_tc_v,
            anahtar_kelimeler=["tc", "kimlik", "tckimlik", "kimlikno", "kimlikno"],
        ),
        AlanTanimi("ad", "Ad", "str", anahtar_kelimeler=["ad", "isim", "name"]),
        AlanTanimi("soyad", "Soyad", "str", anahtar_kelimeler=["soyad", "surname"]),
        AlanTanimi("ad_soyad", "Ad Soyad", "str", anahtar_kelimeler=["adsoyad", "adisoyadi", "namesurname"]),
        AlanTanimi("dogum_tarihi", "Dogum Tarihi", "date", anahtar_kelimeler=["dogumtarihi", "dogum", "birthdate"]),
        AlanTanimi("dogum_yeri", "Dogum Yeri", "str", anahtar_kelimeler=["dogumyeri", "birthplace"]),
        AlanTanimi("hizmet_sinifi", "Hizmet Sinifi", "str", anahtar_kelimeler=["hizmetsinifi", "sinif", "hizmet"]),
        AlanTanimi("kadro_unvani", "Kadro Unvani", "str", anahtar_kelimeler=["kadrounvani", "unvan", "title"]),
        AlanTanimi("gorev_yeri_ad", "Gorev Yeri", "str", anahtar_kelimeler=["gorevyeri", "birim", "bolum", "department"]),
        AlanTanimi("sicil_no", "Sicil No", "str", anahtar_kelimeler=["sicil", "sicilno", "kurumsicilno"]),
        AlanTanimi("memuriyet_baslama", "Memuriyet Baslama", "date", anahtar_kelimeler=["memuriyetbaslama", "memuriyetebaslamatarihi", "isebas"]),
        AlanTanimi("telefon", "Telefon", "str", validator=_tel_v, anahtar_kelimeler=["telefon", "tel", "gsm", "ceptelefonu"]),
        AlanTanimi("e_posta", "E-Posta", "str", validator=_mail_v, anahtar_kelimeler=["eposta", "email", "mail"]),
        AlanTanimi("okul_1", "Mezun Okul (1)", "str", anahtar_kelimeler=["okul1", "mezunolunanokul", "mezunokul", "school"]),
        AlanTanimi("fakulte_1", "Mezun Fakultesi (1)", "str", anahtar_kelimeler=["fakulte1", "mezunolunanfakulte", "mezunfakulte", "faculty"]),
        AlanTanimi("mezuniyet_1", "Mezuniyet Tarihi (1)", "date", anahtar_kelimeler=["mezuniyet1", "mezuniyettarihi", "graduationdate"]),
        AlanTanimi("diploma_no_1", "Diploma No (1)", "str", anahtar_kelimeler=["diplomano", "diploma", "diploma1"]),
        AlanTanimi("okul_2", "Mezun Okul (2)", "str", anahtar_kelimeler=["okul2", "mezunolunanokul2", "mezunokul2", "school2"]),
        AlanTanimi("fakulte_2", "Mezun Fakultesi (2)", "str", anahtar_kelimeler=["fakulte2", "mezunolunanfakulte2", "mezunfakulte2", "faculty2"]),
        AlanTanimi("mezuniyet_2", "Mezuniyet Tarihi (2)", "date", anahtar_kelimeler=["mezuniyet2", "mezuniyettarihi2", "graduationdate2"]),
        AlanTanimi("diploma_no_2", "Diploma No (2)", "str", anahtar_kelimeler=["diplomano2", "diploma2"]),
    ],
)


class PersonelImportPage(BaseImportPage):
    def _konfig(self) -> ImportKonfig:
        return KONFIG
