# -*- coding: utf-8 -*-
"""Yeni personel kaydi sonrasi otomasyonlar."""
from __future__ import annotations

from app.db.database import Database
from app.db.repos.auth_repository import AuthRepository
from app.exceptions import KayitZatenVar
from app.security.password_hasher import PasswordHasher
from app.services.izin_service import IzinService
from app.services.personel_service import PersonelService
from app.text_utils import normalize_whitespace, turkish_lower


class PersonelOnboardingService:
    """Personel kaydi + hesap olusturma + hak edis otomasyonu."""

    def __init__(self, db: Database, oturum: dict | None = None):
        self._db = db
        self._oturum = oturum
        self._personel = PersonelService(db, oturum=oturum)
        self._auth_repo = AuthRepository(db)
        self._izin = IzinService(db)

    def kaydet_ve_hazirla(self, veri: dict, oturum: dict | None = None) -> dict:
        aktif_oturum = oturum if oturum is not None else self._oturum
        with self._db.transaction():
            personel_id = self._personel.ekle(veri, oturum=aktif_oturum)
            personel = self._personel.getir(personel_id)

            auth_info = self._hesap_olustur(personel)
            izin_bilgi = self._izin.hak_edis_bilgisi(personel.get("memuriyet_baslama"))

            return {
                "personel_id": personel_id,
                "kullanici_adi": auth_info["kullanici_adi"],
                "gecici_parola": auth_info["gecici_parola"],
                "izin_hak": izin_bilgi["yillik_hak"],
                "hizmet_yili": izin_bilgi["hizmet_yili"],
            }

    def _hesap_olustur(self, personel: dict) -> dict:
        personel_id = str(personel.get("id") or "")
        mevcut = self._auth_repo.personel_user_getir(personel_id)
        if mevcut:
            return {
                "kullanici_adi": str(mevcut.get("ad") or ""),
                "gecici_parola": "(mevcut kullanici)",
            }

        username = self._username_uret(personel)
        if self._auth_repo.username_exists(username):
            raise KayitZatenVar(f"Kullanici adi zaten var: {username}")

        gecici_parola = self._gecici_parola_uret(str(personel.get("tc_kimlik") or ""))
        self._auth_repo.ensure_role_exists("operator", base_role="kullanici")
        self._auth_repo.create_user(
            username=username,
            password_hash=PasswordHasher.hash_password(gecici_parola),
            personel_id=personel_id,
            role="operator",
            force_password_change=True,
        )
        return {"kullanici_adi": username, "gecici_parola": gecici_parola}

    @staticmethod
    def _username_uret(personel: dict) -> str:
        ad = turkish_lower(normalize_whitespace(str(personel.get("ad") or ""))).replace(" ", "")
        soyad = turkish_lower(normalize_whitespace(str(personel.get("soyad") or ""))).replace(" ", "")
        tc = str(personel.get("tc_kimlik") or "")
        suffix = tc[-4:] if len(tc) >= 4 else "0000"
        base = f"{ad}.{soyad}".strip(".")
        return f"{base}{suffix}" if base else f"personel{suffix}"

    @staticmethod
    def _gecici_parola_uret(tc_kimlik: str) -> str:
        tail = tc_kimlik[-6:] if len(tc_kimlik) >= 6 else "000000"
        return f"Rad{tail}!"
