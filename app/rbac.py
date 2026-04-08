# -*- coding: utf-8 -*-
"""app/rbac.py — UI ve moduller icin rol tabanli yetki yardimcilari.

Başlangıçta hardcoded policy kullanılır.
`init_dari_db(db)` çağrıldıktan sonra DB'deki izinler aktif olur.
"""
from __future__ import annotations

# ── DB'den yüklenen dinamik policy (başlangıçta None) ─────────────
_db_moduller: dict[str, set[str] | None] | None = None


def init_dari_db(db) -> None:
    """
    DB'den modül izinlerini yükler.
    main.py startup'ında migrations'dan sonra çağrılır.
    """
    global _db_moduller
    try:
        from app.services.policy_service import PolicyService
        svc = PolicyService(db)
        _db_moduller = svc.tum_rol_modulleri()
    except Exception:
        _db_moduller = None



_ROLE_MODULES = {
    "admin": None,  # None = tum moduller
    "yonetici": {
        "dashboard",
        "personel",
        "izin",
        "saglik",
        "dozimetre",
        "cihaz",
        "ariza",
        "bakim",
        "rke",
        "nobet",
        "mesai",
        "dokumanlar",
        "rapor",
        "kullanici_giris",
    },
    "kullanici": {
        "dashboard",
        "personel",
        "dokumanlar",
    },
}

_ROLE_ACTIONS = {
    "admin": {
        "personel.ekle",
        "personel.guncelle",
        "personel.pasife_al",
        "kullanici.goruntule",
        "kullanici.olustur",
        "kullanici.guncelle",
        "kullanici.pasife_al",
    },
    "yonetici": {
        "personel.ekle",
        "personel.guncelle",
        "kullanici.goruntule",
        "kullanici.guncelle",
    },
    "kullanici": set(),
}


def rol(oturum: dict | None) -> str:
    return str((oturum or {}).get("rol") or "kullanici")


def modul_gorunur_mu(oturum: dict | None, modul_id: str) -> bool:
    r = rol(oturum)
    # DB'den yüklenmiş policy varsa ona bak
    if _db_moduller is not None and r in _db_moduller:
        izinler = _db_moduller.get(r)
        if izinler is None:
            return True  # admin — tüm modüller
        return modul_id in izinler
    # Hardcoded fallback
    izinli = _ROLE_MODULES.get(r, set())
    if izinli is None:
        return True
    return modul_id in izinli


def yetki_var_mi(oturum: dict | None, eylem: str) -> bool:
    izinler = _ROLE_ACTIONS.get(rol(oturum), set())
    return eylem in izinler


def kullanici_kisa_ad(oturum: dict | None) -> str:
    ad = str((oturum or {}).get("ad") or "Kullanici")
    return ad


def kullanici_avatar(oturum: dict | None) -> str:
    ad = kullanici_kisa_ad(oturum).strip()
    if not ad:
        return "KU"
    parcalar = [p for p in ad.replace("_", " ").split() if p]
    if len(parcalar) >= 2:
        return (parcalar[0][0] + parcalar[1][0]).upper()
    return ad[:2].upper()


def rol_modul_haritasi() -> dict[str, set[str] | None]:
    """Mevcut (DB veya hardcoded) modul izin haritasını döner."""
    if _db_moduller is not None:
        return dict(_db_moduller)
    return dict(_ROLE_MODULES)


def rol_eylem_haritasi() -> dict[str, set[str]]:
    """Hardcoded eylem izin haritasını döner."""
    return {r: set(e) for r, e in _ROLE_ACTIONS.items()}


def rol_modul_haritasi() -> dict[str, set[str] | None]:
    """Rollere gore gorunur modul haritasi (salt-okunur kopya)."""
    sonuc: dict[str, set[str] | None] = {}
    for r, moduller in _ROLE_MODULES.items():
        sonuc[r] = None if moduller is None else set(moduller)
    return sonuc


def rol_eylem_haritasi() -> dict[str, set[str]]:
    """Rollere gore eylem/yetki haritasi (salt-okunur kopya)."""
    return {r: set(eylemler) for r, eylemler in _ROLE_ACTIONS.items()}
