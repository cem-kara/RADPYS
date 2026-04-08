# -*- coding: utf-8 -*-
"""app/services/auth_service.py — RBAC kullanici giris ve yetki servisi"""
from __future__ import annotations
from datetime import datetime
import bcrypt

from app.config import RBAC_ROL_YETKILERI, RBAC_ROLLER
from app.db.database import Database
from app.db.repos.kullanici_repo import KullaniciRepo
from app.exceptions import (
    DogrulamaHatasi,
    KayitBulunamadi,
    KayitZatenVar,
    YetkiHatasi,
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
        if yetki not in set(oturum.get("yetkiler", [])):
            raise YetkiHatasi(f"Bu işlem için yetkiniz yok: {yetki}")

    # ── Kullanici Yonetimi ────────────────────────────────────────

    def kullanici_listele(self, oturum: dict) -> list[dict]:
        self.yetki_kontrol(oturum, "kullanici.goruntule")
        return self._repo.listele()

    def kullanici_ekle(self, oturum: dict, veri: dict) -> str:
        self.yetki_kontrol(oturum, "kullanici.olustur")

        ad = zorunlu(veri.get("ad"), "Kullanıcı adı")
        parola = zorunlu(veri.get("parola"), "Parola")
        rol = zorunlu(veri.get("rol"), "Rol")

        if rol not in RBAC_ROLLER:
            raise DogrulamaHatasi(f"Geçersiz rol: {rol}")

        if len(parola) < 6:
            raise DogrulamaHatasi("Parola en az 6 karakter olmalıdır.")

        if self._repo.ad_var_mi(ad):
            raise KayitZatenVar(f"Bu kullanıcı adı zaten kayıtlı: {ad}")

        return self._repo.ekle({
            "ad": ad,
            "sifre_hash": self._parola_hashle(parola),
            "rol": rol,
            "aktif": bool(veri.get("aktif", True)),
            "personel_id": veri.get("personel_id"),
        })

    def kullanici_rol_guncelle(self, oturum: dict, kullanici_id: str, rol: str) -> None:
        self.yetki_kontrol(oturum, "kullanici.guncelle")

        if rol not in RBAC_ROLLER:
            raise DogrulamaHatasi(f"Geçersiz rol: {rol}")

        self._kullanici_getir(kullanici_id)
        self._repo.guncelle(kullanici_id, {"rol": rol})

    def kullanici_pasife_al(self, oturum: dict, kullanici_id: str) -> None:
        self.yetki_kontrol(oturum, "kullanici.pasife_al")
        self._kullanici_getir(kullanici_id)
        self._repo.guncelle(kullanici_id, {"aktif": 0})

    def kullanici_aktif_et(self, oturum: dict, kullanici_id: str) -> None:
        self.yetki_kontrol(oturum, "kullanici.pasife_al")
        self._kullanici_getir(kullanici_id)
        self._repo.guncelle(kullanici_id, {"aktif": 1})

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
        rol = row["rol"]
        return {
            "id": row["id"],
            "ad": row["ad"],
            "rol": rol,
            "yetkiler": sorted(RBAC_ROL_YETKILERI.get(rol, set())),
            "son_giris": row.get("son_giris"),
        }

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
