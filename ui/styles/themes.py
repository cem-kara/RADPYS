# -*- coding: utf-8 -*-

"""
ui/styles/themes.py - Tema Lookup API
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
colors.py'daki DARK/LIGHT sözlüklerine kolay erişim.
Kullanım:
    from ui.styles.themes import get_tokens
    tokens = get_tokens("dark")
    print(tokens["TEXT_PRIMARY"])
"""

from __future__ import annotations
from ui.styles.colors import DARK, LIGHT

def get_tokens(theme_name: str) -> dict[str, str]:
    """
    Tema token'larını al.
    Args:
        theme_name: "dark" veya "light"
    Returns:
        Renk token sözlüğü
    """
    name = str(theme_name).lower() if theme_name else "dark"
    return LIGHT if name == "light" else DARK

def is_dark_theme(theme_name: str) -> bool:
    """Koyu tema mı kontrol et."""
    return str(theme_name).lower() != "light"

def is_light_theme(theme_name: str) -> bool:
    """Açık tema mı kontrol et."""
    return str(theme_name).lower() == "light"



