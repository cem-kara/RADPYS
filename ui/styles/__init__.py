# -*- coding: utf-8 -*-

"""
ui/styles/__init__.py - Tema Sistemi
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Merkezi tema API. Renk token'ları ve tema yöneticisi.
Kullanım:
    from ui.styles import DARK, LIGHT, ThemeManager, Icons
    ThemeManager.apply_dark(app)
    ThemeManager.apply_light(app)
"""
from __future__ import annotations

# Renk Token'ları
from ui.styles.colors import DARK, LIGHT

# Tema Lookup
from ui.styles.themes import get_tokens, is_dark_theme, is_light_theme

# Tema Yönetimi
from ui.styles.theme_manager import ThemeManager

# Calisan tema degerleri
from ui.styles.runtime import T

# Icon'lar
try:
    from ui.styles.icons import Icons, ic, resolve_icon_color
except ImportError:
    Icons = None
    ic = None
    resolve_icon_color = None

__all__ = [

    "DARK",
    "LIGHT",
    "get_tokens",
    "is_dark_theme",
    "is_light_theme",
    "ThemeManager",
    "T",
    "Icons",
    "ic",
    "resolve_icon_color",

]



