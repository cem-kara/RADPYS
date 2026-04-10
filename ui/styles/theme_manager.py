# -*- coding: utf-8 -*-
"""ui/styles/theme_manager.py - merkezi tema yonetimi."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

from ui.styles.colors import DARK, LIGHT
from ui.styles.icons import Icons


class ThemeManager(QObject):
    """Tema yoneticisi singleton sinifi."""

    theme_changed = Signal(str)  # "dark" | "light"

    _current: str = "dark"
    _instance: ThemeManager | None = None

    @classmethod
    def instance(cls) -> "ThemeManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def apply_dark(app: QApplication) -> None:
        ThemeManager._apply(app, DARK)
        ThemeManager._current = "dark"
        ThemeManager.instance().theme_changed.emit("dark")

    @staticmethod
    def apply_light(app: QApplication) -> None:
        ThemeManager._apply(app, LIGHT)
        ThemeManager._current = "light"
        ThemeManager.instance().theme_changed.emit("light")

    @staticmethod
    def switch_theme(app: QApplication, theme: str) -> None:
        if (theme or "").lower() == "light":
            ThemeManager.apply_light(app)
            return
        ThemeManager.apply_dark(app)

    @staticmethod
    def current_theme() -> str:
        return ThemeManager._current

    @staticmethod
    def _apply(app: QApplication, tokens: dict[str, str]) -> None:
        app.setStyle("Fusion")
        ThemeManager._apply_palette(app, tokens)
        app.setStyleSheet(ThemeManager._build_stylesheet(tokens))

    @staticmethod
    def _apply_palette(app: QApplication, tokens: dict[str, str]) -> None:
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
        p.setColor(QPalette.ColorRole.PlaceholderText, QColor(tokens.get("PLACEHOLDER", "#38526a")))
        p.setColor(QPalette.ColorRole.Mid, QColor(tokens.get("BORDER_PRIMARY", "#192a42")))
        p.setColor(QPalette.ColorRole.Dark, QColor(tokens.get("BG_DARK", "#060b14")))
        p.setColor(QPalette.ColorRole.Light, QColor(tokens.get("BG_TERTIARY", "#141e2b")))

        disabled = QColor(tokens.get("TEXT_DISABLED", "#1a2a3e"))
        p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled)
        p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled)
        p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled)

        app.setPalette(p)

    @staticmethod
    def _build_stylesheet(tokens: dict[str, str]) -> str:
        """Uygulama geneli kontrast ve spacing iyilestiren QSS."""
        arrow_color = tokens.get("TEXT_SECONDARY", "#6a8ca8")
        combo_down = Icons.qss_url("chevron_down", arrow_color, 12)
        calendar = Icons.qss_url("calendar", arrow_color, 14)
        spin_up = Icons.qss_url("chevron_up", arrow_color, 10)
        spin_down = Icons.qss_url("chevron_down", arrow_color, 10)
        check_icon = Icons.qss_url("check",         "#ffffff",   12)
        cal_prev   = Icons.qss_url("chevron_left",  arrow_color, 14)
        cal_next   = Icons.qss_url("chevron_right", arrow_color, 14)
        return f"""
QMainWindow, QDialog {{
    background: {tokens.get("BG_PRIMARY", "#0b0f14")};
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
}}

QWidget {{
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
    font-family: 'Segoe UI', 'Noto Sans', sans-serif;
    font-size: 12px;
}}

QLabel {{
    background: transparent;
}}

QToolTip {{
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
    background: {tokens.get("BG_ELEVATED", "#182436")};
    border: 1px solid {tokens.get("BORDER_SECONDARY", "#203352")};
    padding: 6px 8px;
}}

QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {{
    background: {tokens.get("INPUT_BG", "#0f1724")};
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
    border: 1px solid {tokens.get("INPUT_BORDER", "#192a42")};
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: {tokens.get("ACCENT", "#4080e0")};
    selection-color: #ffffff;
}}

QTextEdit, QPlainTextEdit {{
    padding: 8px 10px;
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {tokens.get("INPUT_BORDER_FOCUS", "#4080e0")};
}}

QLineEdit:disabled, QComboBox:disabled, QDateEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
    color: {tokens.get("TEXT_DISABLED", "#1a2a3e")};
    border-color: {tokens.get("BORDER_PRIMARY", "#192a42")};
}}

QComboBox::drop-down, QDateEdit::drop-down {{
    border: none;
    width: 22px;
    margin-right: 4px;
}}

QComboBox::down-arrow {{
    image: url("{combo_down}");
    width: 12px;
    height: 12px;
}}

QDateEdit::down-arrow {{
    image: url("{calendar}");
    width: 10px;
    height: 10px;
}}

QComboBox QAbstractItemView {{
    background: {tokens.get("BG_SECONDARY", "#101722")};
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
    border: 1px solid {tokens.get("BORDER_SECONDARY", "#203352")};
    border-radius: 6px;
    outline: none;
    padding: 4px;
    selection-background-color: {tokens.get("ACCENT_20", "rgba(64,128,224,0.20)")};
    selection-color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
}}

QComboBox QAbstractItemView::item {{
    min-height: 28px;
    padding: 4px 8px;
    border-radius: 4px;
}}

QComboBox QAbstractItemView::item:hover {{
    background: {tokens.get("ACCENT_10", "rgba(64,128,224,0.10)")};
}}

QCheckBox, QRadioButton {{
    color: {tokens.get("TEXT_SECONDARY", "#6a8ca8")};
    spacing: 8px;
    font-size: 12px;
    background: transparent;
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {tokens.get("TEXT_SECONDARY", "#6a8ca8")};
    border-radius: 4px;
    background-color: {tokens.get("INPUT_BG", "#0f1724")};
}}

QCheckBox::indicator:hover {{
    border-color: {tokens.get("ACCENT", "#4080e0")};
    background-color: {tokens.get("BG_TERTIARY", "#141e2b")};
}}

QCheckBox::indicator:checked {{
    background-color: {tokens.get("ACCENT", "#4080e0")};
    border-color: {tokens.get("ACCENT", "#4080e0")};
    image: url("{check_icon}");
}}

QCheckBox::indicator:disabled {{
    border-color: {tokens.get("TEXT_DISABLED", "#1a2a3e")};
    background-color: {tokens.get("BG_SECONDARY", "#101722")};
}}

QRadioButton::indicator {{
    border-radius: 8px;
}}

QRadioButton::indicator:checked {{
    border-color: {tokens.get("ACCENT", "#4080e0")};
    background-color: qradialgradient(
        cx: 0.5, cy: 0.5, radius: 0.48,
        fx: 0.5, fy: 0.5,
        stop: 0 #ffffff,
        stop: 0.34 #ffffff,
        stop: 0.35 {tokens.get("ACCENT", "#4080e0")},
        stop: 1 {tokens.get("ACCENT", "#4080e0")}
    );
}}

QCalendarWidget {{
    background-color: {tokens.get("BG_SECONDARY", "#101722")};
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
    border: 1px solid {tokens.get("ACCENT_20", "rgba(64,128,224,0.20)")};
    border-radius: 8px;
}}

QCalendarWidget #qt_calendar_navigationbar {{
    background-color: {tokens.get("BG_TERTIARY", "#141e2b")};
    border-bottom: 1px solid {tokens.get("ACCENT_20", "rgba(64,128,224,0.20)")};
    border-radius: 8px 8px 0 0;
    padding: 4px 8px;
    min-height: 32px;
}}

QCalendarWidget QToolButton {{
    background-color: transparent;
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
    border: none;
    border-radius: 5px;
    padding: 4px 8px;
    font-size: 13px;
    font-weight: 700;
    min-width: 20px;
}}

QCalendarWidget QToolButton:hover {{
    background-color: {tokens.get("ACCENT_10", "rgba(64,128,224,0.10)")};
    color: {tokens.get("ACCENT2", "#60a8f8")};
}}

QCalendarWidget QToolButton::menu-indicator {{
    image: none;
    width: 0;
}}

QCalendarWidget QToolButton#qt_calendar_prevmonth {{
    qproperty-icon: none;
    image: url("{cal_prev}");
    width: 24px;
    height: 24px;
    padding: 4px;
}}

QCalendarWidget QToolButton#qt_calendar_nextmonth {{
    qproperty-icon: none;
    image: url("{cal_next}");
    width: 24px;
    height: 24px;
    padding: 4px;
}}

QCalendarWidget QToolButton#qt_calendar_prevmonth:hover,
QCalendarWidget QToolButton#qt_calendar_nextmonth:hover {{
    background-color: {tokens.get("ACCENT_10", "rgba(64,128,224,0.10)")};
    border-radius: 5px;
}}

QCalendarWidget QSpinBox {{
    background-color: transparent;
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
    border: none;
    font-size: 13px;
    font-weight: 700;
    padding: 2px 4px;
    selection-background-color: {tokens.get("ACCENT_10", "rgba(64,128,224,0.10)")};
    selection-color: {tokens.get("ACCENT2", "#60a8f8")};
}}

QCalendarWidget QSpinBox::up-button,
QCalendarWidget QSpinBox::down-button {{
    width: 0;
    height: 0;
    border: none;
}}

QCalendarWidget QWidget {{
    background-color: {tokens.get("BG_SECONDARY", "#101722")};
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
    alternate-background-color: {tokens.get("BG_SECONDARY", "#101722")};
}}

QCalendarWidget QTableView {{
    background-color: {tokens.get("BG_SECONDARY", "#101722")};
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
    gridline-color: transparent;
    border: none;
    outline: none;
    alternate-background-color: {tokens.get("BG_SECONDARY", "#101722")};
    selection-background-color: {tokens.get("ACCENT_10", "rgba(64,128,224,0.10)")};
    selection-color: {tokens.get("ACCENT2", "#60a8f8")};
}}

QCalendarWidget QTableView::item {{
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
    background-color: transparent;
    padding: 2px;
    border-radius: 4px;
    border: none;
    min-width: 28px;
    min-height: 24px;
}}

QCalendarWidget QTableView::item:hover {{
    background-color: {tokens.get("ACCENT_10", "rgba(64,128,224,0.10)")};
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
}}

QCalendarWidget QTableView::item:selected {{
    background-color: {tokens.get("ACCENT_20", "rgba(64,128,224,0.20)")};
    color: {tokens.get("ACCENT2", "#60a8f8")};
    font-weight: 700;
}}

QCalendarWidget QAbstractItemView {{
    background-color: {tokens.get("BG_SECONDARY", "#101722")};
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
    selection-background-color: {tokens.get("ACCENT_20", "rgba(64,128,224,0.20)")};
    selection-color: {tokens.get("ACCENT2", "#60a8f8")};
    font-size: 13px;
    outline: none;
    alternate-background-color: {tokens.get("BG_SECONDARY", "#101722")};
}}

QCalendarWidget QAbstractItemView:enabled {{
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
}}

QCalendarWidget QAbstractItemView:disabled {{
    color: {tokens.get("TEXT_MUTED", "#38526a")};
}}

QCalendarWidget QHeaderView {{
    background-color: {tokens.get("BG_TERTIARY", "#141e2b")};
    color: {tokens.get("TEXT_SECONDARY", "#6a8ca8")};
    font-size: 11px;
    font-weight: 700;
}}

QCalendarWidget QHeaderView::section {{
    background-color: {tokens.get("BG_TERTIARY", "#141e2b")};
    color: {tokens.get("TEXT_SECONDARY", "#6a8ca8")};
    border: none;
    border-bottom: 1px solid {tokens.get("ACCENT_20", "rgba(64,128,224,0.20)")};
    padding: 5px 2px;
    font-size: 11px;
    font-weight: 700;
}}
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 18px;
    border: none;
    margin-top: 1px;
    margin-right: 2px;
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 18px;
    border: none;
    margin-bottom: 1px;
    margin-right: 2px;
}}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    image: url("{spin_up}");
    width: 8px;
    height: 8px;
}}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    image: url("{spin_down}");
    width: 8px;
    height: 8px;
}}

QTabWidget::pane {{
    border: 1px solid {tokens.get("BORDER_PRIMARY", "#192a42")};
    background: {tokens.get("BG_SECONDARY", "#101722")};
    border-radius: 8px;
    top: -1px;
}}

QTabBar::tab {{
    color: {tokens.get("TEXT_SECONDARY", "#6a8ca8")};
    background: {tokens.get("BG_TERTIARY", "#141e2b")};
    border: 1px solid {tokens.get("BORDER_PRIMARY", "#192a42")};
    padding: 7px 14px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}

QTabBar::tab:selected {{
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
    background: {tokens.get("BG_SECONDARY", "#101722")};
    border-color: {tokens.get("BORDER_SECONDARY", "#203352")};
}}

QTabBar::tab:hover:!selected {{
    background: {tokens.get("BG_HOVER", "rgba(64,128,224,0.08)")};
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
}}

QPushButton {{
    color: {tokens.get("BTN_SECONDARY_TEXT", "#6a8ca8")};
    background: {tokens.get("BTN_SECONDARY_BG", "transparent")};
    border: 1px solid {tokens.get("BTN_SECONDARY_BORDER", "#192a42")};
    border-radius: 6px;
    padding: 4px 8px;
    font-weight: 600;
}}

QPushButton:hover {{
    background: {tokens.get("BTN_SECONDARY_HOVER", "#182436")};
    border-color: {tokens.get("BORDER_STRONG", "#2a4068")};
}}

QPushButton:pressed {{
    padding-top: 5px;
}}

QPushButton[primary='true'] {{
    color: {tokens.get("BTN_PRIMARY_TEXT", "#ffffff")};
    background: {tokens.get("BTN_PRIMARY_BG", "#2b62c8")};
    border: 1px solid {tokens.get("BTN_PRIMARY_BORDER", "#2b62c8")};
}}

QPushButton[primary='true']:hover {{
    background: {tokens.get("BTN_PRIMARY_HOVER", "#4080e0")};
    border-color: {tokens.get("BTN_PRIMARY_HOVER", "#4080e0")};
}}

QPushButton[danger='true'] {{
    color: {tokens.get("BTN_DANGER_TEXT", "#e85555")};
    background: {tokens.get("BTN_DANGER_BG", "rgba(232,85,85,0.12)")};
    border: 1px solid {tokens.get("BTN_DANGER_BORDER", "rgba(232,85,85,0.28)")};
}}

QPushButton[danger='true']:hover {{
    background: {tokens.get("BTN_DANGER_HOVER", "rgba(232,85,85,0.22)")};
}}

QPushButton[success='true'] {{
    color: {tokens.get("BTN_SUCCESS_TEXT", "#2ec98e")};
    background: {tokens.get("BTN_SUCCESS_BG", "rgba(46,201,142,0.12)")};
    border: 1px solid {tokens.get("BTN_SUCCESS_BORDER", "rgba(46,201,142,0.28)")};
}}

QPushButton[success='true']:hover {{
    background: {tokens.get("BTN_SUCCESS_HOVER", "rgba(46,201,142,0.22)")};
}}

QPushButton[ghost='true'] {{
    background: transparent;
    color: {tokens.get("TEXT_SECONDARY", "#6a8ca8")};
    border: 1px solid {tokens.get("BORDER_PRIMARY", "#192a42")};
}}

QPushButton[ghost='true']:hover {{
    background: {tokens.get("BG_HOVER", "rgba(64,128,224,0.08)")};
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
    border-color: {tokens.get("BORDER_STRONG", "#2a4068")};
}}

QPushButton[iconOnly='true'] {{
    min-height: 20px;
    padding: 0px;
}}

QTableView {{
    background: {tokens.get("BG_SECONDARY", "#101722")};
    alternate-background-color: {tokens.get("BG_TERTIARY", "#141e2b")};
    border: 1px solid {tokens.get("BORDER_PRIMARY", "#192a42")};
    gridline-color: {tokens.get("BORDER_PRIMARY", "#192a42")};
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
    selection-background-color: {tokens.get("BG_SELECTED", "rgba(64,128,224,0.15)")};
    selection-color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
    border-radius: 8px;
}}

QGroupBox {{
    border: 1px solid {tokens.get("BORDER_PRIMARY", "#192a42")};
    border-radius: 6px;
    margin-top: 10px;
    padding: 10px 10px 8px 10px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    padding: 0 4px;
    color: {tokens.get("TEXT_SECONDARY", "#6a8ca8")};
}}

QMenu {{
    background: {tokens.get("BG_ELEVATED", "#182436")};
    color: {tokens.get("TEXT_PRIMARY", "#d6e4f0")};
    border: 1px solid {tokens.get("BORDER_SECONDARY", "#203352")};
    border-radius: 6px;
    padding: 6px;
}}

QMenu::item {{
    padding: 6px 10px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background: {tokens.get("ACCENT_10", "rgba(64,128,224,0.10)")};
}}

QHeaderView::section {{
    background: {tokens.get("BG_TERTIARY", "#141e2b")};
    color: {tokens.get("TEXT_TABLE_HEADER", "#9ab8d0")};
    border: none;
    border-bottom: 1px solid {tokens.get("BORDER_PRIMARY", "#192a42")};
    padding: 8px;
    font-weight: 600;
}}

QScrollBar:vertical {{
    background: {tokens.get("BG_SECONDARY", "#101722")};
    width: 12px;
    margin: 2px;
}}

QScrollBar:horizontal {{
    background: {tokens.get("BG_SECONDARY", "#101722")};
    height: 12px;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background: {tokens.get("BORDER_SECONDARY", "#203352")};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:horizontal {{
    background: {tokens.get("BORDER_SECONDARY", "#203352")};
    border-radius: 6px;
    min-width: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {tokens.get("BORDER_STRONG", "#2a4068")};
}}

QScrollBar::handle:horizontal:hover {{
    background: {tokens.get("BORDER_STRONG", "#2a4068")};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
"""
