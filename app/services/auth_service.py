# -*- coding: utf-8 -*-
"""app/services/auth_service.py — RBAC kullanici giris ve yetki servisi"""
from __future__ import annotations
from datetime import datetime
import bcrypt

from app.db.database import Database
from app.db.repos.kullanici_repo import KullaniciRepo
from app.exceptions import (
    DogrulamaHatasi,
    KayitBulunamadi,
)
from app.security.permissions import require_permission
from app.security.session import build_session
from app.usecases.auth import (
    kullanici_aktiflik_guncelle,
    kullanici_ekle,
    kullanici_rol_guncelle,
)
from app.validators import zorunlu


class AuthService:
    """Kullanici dogrulama ve rol tabanli yetki kontrolu."""

    def __init__(self, db: Database):
        self._repo = KullaniciRepo(db)

    # ── Login / Oturum ────────────────────────────────────────────

    def giris_yap(self, kullanici_adi: str, parola: str) -> dict:
        ad = zorunlu(kullanici_adi, "Kullanıcı adı")
        zorunlu(parola, "Parola")

        row = self._repo.ad_ile_getir(ad)
        if not row or not int(row.get("aktif", 0)):
            raise DogrulamaHatasi("Kullanıcı adı veya parola hatalı.")

        if not self._parola_dogrula(parola, row["sifre_hash"]):
            raise DogrulamaHatasi("Kullanıcı adı veya parola hatalı.")

        an = self._simdi()
        self._repo.son_giris_guncelle(row["id"], an)
        row["son_giris"] = an
        return self._oturum(row)

    def yetki_kontrol(self, oturum: dict, yetki: str) -> None:
        require_permission(oturum, yetki)

    # ── Kullanici Yonetimi ────────────────────────────────────────

    def kullanici_listele(self, oturum: dict) -> list[dict]:
        self.yetki_kontrol(oturum, "kullanici.goruntule")
        return self._repo.listele()

    def kullanici_ekle(self, oturum: dict, veri: dict) -> str:
        self.yetki_kontrol(oturum, "kullanici.olustur")
        return kullanici_ekle(self._repo, self._parola_hashle, veri)

    def kullanici_rol_guncelle(self, oturum: dict, kullanici_id: str, rol: str) -> None:
        self.yetki_kontrol(oturum, "kullanici.guncelle")
        self._kullanici_getir(kullanici_id)
        kullanici_rol_guncelle(self._repo, kullanici_id, rol)

    def kullanici_pasife_al(self, oturum: dict, kullanici_id: str) -> None:
        self.yetki_kontrol(oturum, "kullanici.pasife_al")
        self._kullanici_getir(kullanici_id)
        kullanici_aktiflik_guncelle(self._repo, kullanici_id, False)

    def kullanici_aktif_et(self, oturum: dict, kullanici_id: str) -> None:
        self.yetki_kontrol(oturum, "kullanici.pasife_al")
        self._kullanici_getir(kullanici_id)
        kullanici_aktiflik_guncelle(self._repo, kullanici_id, True)

    def kullanici_getir(self, oturum: dict, kullanici_id: str) -> dict:
        self.yetki_kontrol(oturum, "kullanici.goruntule")
        return self._kullanici_getir(kullanici_id)

    # ── Yardimci ──────────────────────────────────────────────────

    def _kullanici_getir(self, kullanici_id: str) -> dict:
        row = self._repo.id_ile_getir(kullanici_id)
        if not row:
            raise KayitBulunamadi(f"Kullanıcı bulunamadı: {kullanici_id}")
        return row

    def _oturum(self, row: dict) -> dict:
        return build_session(row)

    @staticmethod
    def _simdi() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _parola_hashle(parola: str) -> str:
        return bcrypt.hashpw(parola.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def _parola_dogrula(parola: str, sifre_hash: str) -> bool:
        try:
            return bcrypt.checkpw(
                parola.encode("utf-8"),
                sifre_hash.encode("utf-8"),
            )
        except Exception:
            return False
