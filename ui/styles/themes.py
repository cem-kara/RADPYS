# -*- coding: utf-8 -*-
"""
ui/styles/themes.py ï¿½?" Tema Lookup API
ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

colors.py'daki DARK/LIGHT sÃ¶zlÃ¼klerine kolay eriï¿½Yim.

KullanÄ±m:
    from ui.styles.themes import get_tokens
    tokens = get_tokens("dark")
    print(tokens["TEXT_PRIMARY"])
"""

from __future__ import annotations
from ui.styles.colors import DARK, LIGHT


def get_tokens(theme_name: str) -> dict[str, str]:
    """
    Tema token'larÄ±nÄ± al.
    
    Args:
        theme_name: "dark" veya "light"
    
    Returns:
        Renk token sÃ¶zlÃ¼ï¿½YÃ¼
    """
    name = str(theme_name).lower() if theme_name else "dark"
    return LIGHT if name == "light" else DARK


def is_dark_theme(theme_name: str) -> bool:
    """Koyu tema mi kontrol et."""
    return str(theme_name).lower() != "light"


def is_light_theme(theme_name: str) -> bool:
    """AÃ§Ä±k tema mi kontrol et."""
    return str(theme_name).lower() == "light"

