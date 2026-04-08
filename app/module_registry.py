# -*- coding: utf-8 -*-
"""
app/module_registry.py
──────────────────────
Modül kayıt sistemi — menus.json'dan okur.

Yeni modül eklemek:
    1. menus.json'a yeni nesne ekle
    2. ui/pages/yeni_modul/ altına sayfa sınıfını yaz
    3. Badge gerekiyorsa app/badge_functions.py'e fonksiyon ekle
    ← Başka hiçbir dosyaya dokunmak gerekmez.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

_MENUS_JSON = Path(__file__).parent.parent / "menus.json"


@dataclass
class BolumDef:
    id:    str
    label: str
    sira:  int


@dataclass
class ModuleDef:
    id:         str
    label:      str
    icon:       str
    bolum:      str          # "ana_menu" | "cihaz" | "nobet" | "sistem"
    bolum_sira: int          # BolumDef.sira — sıralama için
    sira:       int
    page_cls:   str
    badge_fn:   Callable | None = field(default=None, repr=False)
    badge_renk: str             = "#3479ff"
    varsayilan: bool            = False


# ── Global depo ───────────────────────────────────────────────────

_moduller:   list[ModuleDef] = []
_bolumler:   dict[str, BolumDef] = {}
_yuklendi    = False
_PLACEHOLDER_PAGE = "ui.pages.placeholder.PlaceholderPage"


def _yukle() -> None:
    global _yuklendi
    if _yuklendi:
        return

    data = json.loads(_MENUS_JSON.read_text(encoding="utf-8"))
    _moduller.clear()
    _bolumler.clear()

    # Bölümleri yükle
    for bid, bveri in data["bolumler"].items():
        _bolumler[bid] = BolumDef(
            id    = bid,
            label = bveri["label"],
            sira  = bveri["sira"],
        )

    # Badge fonksiyonlarını yükle
    from app.badge_functions import BADGE_FN

    # Modülleri yükle
    for m in data["moduller"]:
        # Taslak moduller menude gosterilmez; temel iskelette sadece gercek
        # ekranlarin gorunur olmasi ileriki refactor maliyetini azaltir.
        if m.get("page_cls") == _PLACEHOLDER_PAGE:
            continue

        bolum_sira = _bolumler.get(m["bolum"], BolumDef("", "", 99)).sira
        badge_id   = m.get("badge_id")
        badge_fn   = BADGE_FN.get(badge_id) if badge_id else None

        _moduller.append(ModuleDef(
            id         = m["id"],
            label      = m["label"],
            icon       = m["icon"],
            bolum      = m["bolum"],
            bolum_sira = bolum_sira,
            sira       = m.get("sira", 99),
            page_cls   = m["page_cls"],
            badge_fn   = badge_fn,
            badge_renk = m.get("badge_renk", "#3479ff"),
            varsayilan = m.get("varsayilan", False),
        ))

    _yuklendi = True


# ── Public API ────────────────────────────────────────────────────

def get_all() -> list[ModuleDef]:
    _yukle()
    return sorted(_moduller, key=lambda m: (m.bolum_sira, m.sira))


def get_bolumler() -> list[tuple[BolumDef, list[ModuleDef]]]:
    """[(BolumDef, [ModuleDef, ...]), ...] — sidebar için."""
    _yukle()
    gruplar: dict[str, list[ModuleDef]] = {}
    for mod in get_all():
        gruplar.setdefault(mod.bolum, []).append(mod)

    return [
        (_bolumler[bid], modlar)
        for bid, modlar in sorted(
            gruplar.items(),
            key=lambda x: _bolumler.get(x[0], BolumDef("", "", 99)).sira
        )
    ]


def get_varsayilan_id() -> str:
    _yukle()
    for m in get_all():
        if m.varsayilan:
            return m.id
    lst = get_all()
    return lst[0].id if lst else ""


def sayfa_olustur(mod_id: str, db, oturum: dict | None = None) -> "QWidget":
    """Lazy import ile sayfa widget'ı oluşturur."""
    _yukle()
    mod = next((m for m in _moduller if m.id == mod_id), None)
    if mod is None:
        raise KeyError(f"Modül bulunamadı: '{mod_id}'")

    parcalar   = mod.page_cls.rsplit(".", 1)
    if len(parcalar) != 2:
        raise ValueError(f"Geçersiz page_cls tanımı: '{mod.page_cls}'")
    import importlib
    modul  = importlib.import_module(parcalar[0])
    sinif  = getattr(modul, parcalar[1])
    try:
        return sinif(db, oturum=oturum)
    except TypeError:
        return sinif(db)
