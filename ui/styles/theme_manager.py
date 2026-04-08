# -*- coding: utf-8 -*-
"""
ui/styles/theme_manager.py ï¿½?" Tema YÃ¶netim Sistemi
ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

Merkezi tema kontrol. QApplication'a QSS uygulama, tema
deï¿½Yiï¿½Yiklik sinyali.

KullanÄ±m:
    from ui.styles import ThemeManager
    
    ThemeManager.apply_dark(app)   # Koyu tema
    ThemeManager.apply_light(app)  # AÃ§Ä±k tema
    
    # Ä°syayÄ±nda deï¿½Yiï¿½Yiklik
    ThemeManager.switch_theme(app, "light")
"""

from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication

from ui.styles.colors import DARK, LIGHT


class ThemeManager(QObject):
    """Tema yÃ¶neticisi singleton."""

    theme_changed = Signal(str)  # "dark" | "light"
    
    _current: str = "dark"
    _instance: ThemeManager | None = None

    @classmethod
    def instance(cls) -> ThemeManager:
        """Singleton Ã¶rneï¿½Yi al."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()

    # ï¿½"?ï¿½"? Public API ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?

    @staticmethod
    def apply_dark(app: QApplication) -> None:
        """Koyu temayÄ± uygula."""
        ThemeManager._apply(app, DARK)
        ThemeManager._current = "dark"
        ThemeManager.instance().theme_changed.emit("dark")

    @staticmethod
    def apply_light(app: QApplication) -> None:
        """AÃ§Ä±k temayÄ± uygula."""
        ThemeManager._apply(app, LIGHT)
        ThemeManager._current = "light"
        ThemeManager.instance().theme_changed.emit("light")

    @staticmethod
    def switch_theme(app: QApplication, theme: str) -> None:
        """TemayÄ± deï¿½Yiï¿½Ytir."""
        if theme.lower() == "light":
            ThemeManager.apply_light(app)
        else:
            ThemeManager.apply_dark(app)

    @staticmethod
    def current_theme() -> str:
        """Aktif tema adÄ±nÄ± dÃ¶ner."""
        return ThemeManager._current

    # ï¿½"?ï¿½"? Ä°Ã§ API ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?

    @staticmethod
    def _apply(app: QApplication, tokens: dict[str, str]) -> None:
        """Token'larÄ± QApplication'a uygula."""
        app.setStyle("Fusion")
        ThemeManager._apply_palette(app, tokens)

    @staticmethod
    def _apply_palette(app: QApplication, tokens: dict[str, str]) -> None:
        """Qt QPalette ayarla."""
        p = QPalette()

        p.setColor(QPalette.ColorRole.Window, QColor(tokens.get("BG_PRIMARY", "#0b0f14")))
        p.setColor(QPalette.ColorRole.WindowText, QColor(tokens.get("TEXT_PRIMARY", "#d6e4f0")))
        p.setColor(QPalette.ColorRole.Base, QColor(tokens.get("BG_SECONDARY", "#101722")))
        p.setColor(QPalette.ColorRole.AlternateBase, QColor(tokens.get("BG_TERTIARY", "#141e2b")))
        p.setColor(QPalette.ColorRole.Text, QColor(tokens.get("TEXT_PRIMARY", "#d6e4f0")))
        p.setColor(QPalette.ColorRole.Button, QColor(tokens.get("BG_SECONDARY", "#101722")))
        p.setColor(QPalette.ColorRole.ButtonText, QColor(tokens.get("TEXT_PRIMARY", "#d6e4f0")))
        p.setColor(QPalette.ColorRole.ToolTipBase, QColor(tokens.get("BG_ELEVATED", "#182436")))
        p.setColor(QPalette.ColorRole.ToolTipText, QColor(tokens.get("TEXT_PRIMARY", "#d6e4f0")))
        p.setColor(QPalette.ColorRole.Highlight, QColor(tokens.get("ACCENT", "#4080e0")))
        p.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        p.setColor(QPalette.ColorRole.Link, QColor(tokens.get("ACCENT", "#4080e0")))
        p.setColor(QPalette.ColorRole.PlaceholderText, QColor(tokens.get("TEXT_MUTED", "#38526a")))
        p.setColor(QPalette.ColorRole.Mid, QColor(tokens.get("BORDER_PRIMARY", "#192a42")))
        p.setColor(QPalette.ColorRole.Dark, QColor(tokens.get("BG_DARK", "#060b14")))
        p.setColor(QPalette.ColorRole.Light, QColor(tokens.get("BG_TERTIARY", "#141e2b")))

        app.setPalette(p)

