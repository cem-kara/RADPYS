# -*- coding: utf-8 -*-
"""app/services/policy_service.py — Modül izin yönetimi servisi"""
from __future__ import annotations
from app.db.database import Database
from app.db.repos.policy_repo import PolicyRepo
from app.security.permissions import require_permission
from app.security.policy import require_admin_session
from app.usecases.policy import rol_modullerini_kaydet, tum_rol_modulleri_getir


class PolicyService:
    """DB'e kaydedilmiş modül izinlerini yönetir."""

    def __init__(self, db: Database):
        self._repo = PolicyRepo(db)

    def modul_seti_getir(self, rol: str) -> set[str] | None:
        """
        Verilen rol için izinli modüller kümesini döner.
        DB'de kayıt yoksa None döner (hardcoded fallback kullanılır).
        Admin rolü için None döner (tüm modüller).
        """
        rows = self._repo.rol_izinleri(rol)
        if not rows:
            return None  # Henüz DB'de kayıt yok
        return {r["modul_id"] for r in rows if int(r.get("izinli", 0))}

    def tum_rol_modulleri(self) -> dict[str, set[str] | None]:
        """Tüm rollerin modül izin haritasını döner."""
        return tum_rol_modulleri_getir(self._repo.tum_izinler())

    def rol_modulleri_detay(self, rol: str) -> list[dict]:
        """Verilen rol için {modul_id, izinli} listesi döner."""
        return self._repo.rol_izinleri(rol)

    def rol_modullerini_kaydet(self, oturum: dict, rol: str, modul_seti: set[str]) -> None:
        """Bir rolün modül izinlerini DB'ye yazar (admin yetkisi gerekir)."""
        require_admin_session(oturum, "Modül izinlerini sadece admin değiştirebilir.")
        require_permission(oturum, "kullanici.guncelle")
        rol_modullerini_kaydet(self._repo, rol, modul_seti)
