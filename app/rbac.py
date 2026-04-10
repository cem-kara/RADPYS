# -*- coding: utf-8 -*-
"""app/rbac.py — UI ve moduller icin rol tabanli yetki yardimcilari.

Başlangıçta hardcoded policy kullanılır.
`init_dari_db(db)` çağrıldıktan sonra DB'deki izinler aktif olur.
"""
from __future__ import annotations
from app.config import RBAC_ROL_YETKILERI
from app.security.permissions import has_permission, require_permission
from app.text_utils import turkish_upper

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
    "operator": {
        "dashboard",
        "personel",
        "dokumanlar",
    },
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
    return has_permission(oturum, eylem)


def yetki_gerektir(oturum: dict | None, eylem: str) -> None:
    require_permission(oturum, eylem)


def kullanici_kisa_ad(oturum: dict | None) -> str:
    o = oturum or {}
    ad = str(
        o.get("ad")
        or o.get("kullanici_ad")
        or o.get("kullanici_adi")
        or o.get("username")
        or "Kullanici"
    )
    return ad


def kullanici_avatar(oturum: dict | None) -> str:
    ad = kullanici_kisa_ad(oturum).strip()
    if not ad:
        return "KU"
    parcalar = [p for p in ad.replace("_", " ").split() if p]
    if len(parcalar) >= 2:
        return turkish_upper(parcalar[0][0] + parcalar[1][0])
    return turkish_upper(ad[:2])


def rol_modul_haritasi() -> dict[str, set[str] | None]:
    """Mevcut (DB veya hardcoded) modul izin haritasını döner."""
    if _db_moduller is not None:
        sonuc: dict[str, set[str] | None] = {}
        for r, moduller in _db_moduller.items():
            sonuc[r] = None if moduller is None else set(moduller)
        return sonuc
    sonuc: dict[str, set[str] | None] = {}
    for r, moduller in _ROLE_MODULES.items():
        sonuc[r] = None if moduller is None else set(moduller)
    return sonuc


def rol_eylem_haritasi() -> dict[str, set[str]]:
    """Config tabanlı eylem izin haritasını döner."""
    return {r: set(e) for r, e in RBAC_ROL_YETKILERI.items()}
