# -*- coding: utf-8 -*-

"""ö

ui/styles/theme_manager.py -?" Tema Yönetim Sistemi

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



Merkezi tema kontrol. QApplication'a QSS uygulama, tema

deşişiklik sinyali.



Kullanım:

    from ui.styles import ThemeManager

    

    ThemeManager.apply_dark(app)   # Koyu tema

    ThemeManager.apply_light(app)  # Açık tema

    

    # İsyayÄöda deşişiklik

    ThemeManager.switch_theme(app, "light")

"""



from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication
from ui.styles.colors import DARK, LIGHT



class ThemeManager(QObject):

    """Tema yöneticisi singleton."""



    theme_changed = Signal(str)  # "dark" | "light"

    

    _current: str = "dark"

    _instance: ThemeManager | None = None



    @classmethod

    def instance(cls) -> ThemeManager:

        """Singleton örneşi al."""

        if cls._instance is None:

            cls._instance = cls()

        return cls._instance



    def __init__(self):

        super().__init__()



    # ---- Public API --------------------------------------------------------------------------------------



    @staticmethod

    def apply_dark(app: QApplication) -> None:

        """Koyu temayı uygula."""

        ThemeManager._apply(app, DARK)

        ThemeManager._current = "dark"

        ThemeManager.instance().theme_changed.emit("dark")



    @staticmethod

    def apply_light(app: QApplication) -> None:

        """Açık temayı uygula."""

        ThemeManager._apply(app, LIGHT)

        ThemeManager._current = "light"

        ThemeManager.instance().theme_changed.emit("light")



    @staticmethod

    def switch_theme(app: QApplication, theme: str) -> None:

        """Temayı deşiştir."""

        if theme.lower() == "light":

            ThemeManager.apply_light(app)

        else:

            ThemeManager.apply_dark(app)



    @staticmethod

    def current_theme() -> str:

        """Aktif tema adını döner."""

        return ThemeManager._current



    # ---- İç API ------------------------------------------------------------------------------------------------



    @staticmethod

    def _apply(app: QApplication, tokens: dict[str, str]) -> None:

        """Token'ları QApplication'a uygula."""

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



