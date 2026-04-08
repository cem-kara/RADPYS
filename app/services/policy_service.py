# -*- coding: utf-8 -*-
"""app/services/policy_service.py — Modül izin yönetimi servisi"""
from __future__ import annotations
from app.db.database import Database
from app.db.repos.policy_repo import PolicyRepo
from app.exceptions import YetkiHatasi


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
        rows = self._repo.tum_izinler()
        rol_map: dict[str, list[dict]] = {}
        for r in rows:
            rol_map.setdefault(r["rol"], []).append(r)

        sonuc: dict[str, set[str] | None] = {}
        for rol_adi, kayitlar in rol_map.items():
            # Tüm modüller izinliyse None (admin benzeri davranış)
            hepsi_izinli = all(int(k.get("izinli", 0)) for k in kayitlar)
            if hepsi_izinli and rol_adi == "admin":
                sonuc[rol_adi] = None
            else:
                sonuc[rol_adi] = {k["modul_id"] for k in kayitlar if int(k.get("izinli", 0))}
        return sonuc

    def rol_modulleri_detay(self, rol: str) -> list[dict]:
        """Verilen rol için {modul_id, izinli} listesi döner."""
        return self._repo.rol_izinleri(rol)

    def rol_modullerini_kaydet(self, oturum: dict, rol: str, modul_seti: set[str]) -> None:
        """Bir rolün modül izinlerini DB'ye yazar (admin yetkisi gerekir)."""
        from app.rbac import yetki_var_mi
        if oturum.get("rol") != "admin":
            raise YetkiHatasi("Modül izinlerini sadece admin değiştirebilir.")
        if not yetki_var_mi(oturum, "kullanici.guncelle"):
            raise YetkiHatasi("Modül izinlerini değiştirme yetkiniz yok.")
        if rol == "admin":
            raise YetkiHatasi("Admin rolünün modül izinleri değiştirilemez.")
        self._repo.rol_modullerini_kaydet(rol, modul_seti)
