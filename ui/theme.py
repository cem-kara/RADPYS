# -*- coding: utf-8 -*-
"""
ui/theme.py
───────────
Tema sistemi — saf Python, QSS template yok.

Kullanım:
    from ui.theme import apply, T
    apply(app)           # Ana pencere açılmadan önce
    T.ACCENT             # "#4f8ef7" — renk sabitine erişim
"""
from __future__ import annotations
from dataclasses import dataclass
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QPalette, QColor


# ══════════════════════════════════════════════════════════════════
#  RENK PALETİ
# ══════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class _Palette:

    # ── Arka planlar ─────────────────────────────────────────────
    bg_app:       str = "#0d1117"   # En koyu — uygulama zemini
    bg_panel:     str = "#161b22"   # Panel, sidebar
    bg_card:      str = "#1c2128"   # Kart, groupbox
    bg_input:     str = "#21262d"   # Input, combobox
    bg_hover:     str = "#2d333b"   # Hover
    bg_selected:  str = "#1f3252"   # Seçili satır

    # ── Kenarlıklar ───────────────────────────────────────────────
    border:       str = "#30363d"
    border_focus: str = "#4f8ef7"

    # ── Anlam renkleri ────────────────────────────────────────────
    accent:       str = "#4f8ef7"   # Mavi — primary action
    accent_hover: str = "#6ea8ff"
    accent_dim:   str = "#1f3252"   # Accent'ın koyu arka planı

    success:      str = "#3fb950"   # Yeşil
    success_dim:  str = "#0f2d1a"

    warning:      str = "#d29922"   # Sarı
    warning_dim:  str = "#2d1f00"

    danger:       str = "#f85149"   # Kırmızı
    danger_dim:   str = "#2d0f0f"

    info:         str = "#58a6ff"   # Açık mavi (link/bilgi)

    # ── Metin ─────────────────────────────────────────────────────
    text_primary:   str = "#e6edf3"
    text_secondary: str = "#8b949e"
    text_muted:     str = "#484f58"
    text_disabled:  str = "#484f58"
    text_link:      str = "#58a6ff"

    # ── Layout ────────────────────────────────────────────────────
    sidebar_width:  int = 72
    border_radius:  int = 8
    border_radius_sm: int = 6


# Tek global tema örneği
T = _Palette()


# ══════════════════════════════════════════════════════════════════
#  STYLESHEET
# ══════════════════════════════════════════════════════════════════

def _stylesheet(p: _Palette = T) -> str:
    return f"""
/* ── Global ─────────────────────────────────────────────────── */
* {{
    outline: 0;
}}
QWidget {{
    background-color: {p.bg_app};
    color: {p.text_primary};
    font-family: "Segoe UI", "SF Pro Text", "Helvetica Neue",
                 system-ui, -apple-system, sans-serif;
    font-size: 13px;
    selection-background-color: {p.accent};
    selection-color: white;
}}
QMainWindow, QDialog {{
    background-color: {p.bg_app};
}}

/* ── GroupBox / Kart ─────────────────────────────────────────── */
QGroupBox {{
    background-color: {p.bg_card};
    border: 1px solid {p.border};
    border-radius: {p.border_radius}px;
    margin-top: 10px;
    padding: 14px 10px 10px 10px;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: {p.text_secondary};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: -6px;
    background-color: {p.bg_card};
    padding: 0 4px;
}}

/* ── Frame ───────────────────────────────────────────────────── */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {{
    color: {p.border};
}}

/* ── Inputs ──────────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {p.bg_input};
    border: 1px solid {p.border};
    border-radius: {p.border_radius_sm}px;
    padding: 7px 10px;
    color: {p.text_primary};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {p.border_focus};
    background-color: {p.bg_card};
}}
QLineEdit:disabled, QTextEdit:disabled {{
    color: {p.text_disabled};
    background-color: {p.bg_panel};
}}
QLineEdit[readOnly=true] {{
    color: {p.text_secondary};
    background-color: {p.bg_panel};
}}

/* ── ComboBox ────────────────────────────────────────────────── */
QComboBox {{
    background-color: {p.bg_input};
    border: 1px solid {p.border};
    border-radius: {p.border_radius_sm}px;
    padding: 7px 10px;
    color: {p.text_primary};
    min-width: 80px;
}}
QComboBox:focus {{
    border-color: {p.border_focus};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {p.text_secondary};
    width: 0;
    height: 0;
    margin-right: 6px;
}}
QComboBox QAbstractItemView {{
    background-color: {p.bg_card};
    border: 1px solid {p.border};
    border-radius: {p.border_radius_sm}px;
    color: {p.text_primary};
    selection-background-color: {p.accent_dim};
    padding: 4px;
    outline: 0;
}}
QComboBox QAbstractItemView::item {{
    padding: 6px 10px;
    border-radius: 4px;
    min-height: 28px;
}}
QComboBox QAbstractItemView::item:hover {{
    background-color: {p.bg_hover};
}}

/* ── SpinBox ─────────────────────────────────────────────────── */
QSpinBox, QDoubleSpinBox {{
    background-color: {p.bg_input};
    border: 1px solid {p.border};
    border-radius: {p.border_radius_sm}px;
    padding: 7px 10px;
    color: {p.text_primary};
}}
QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {p.border_focus};
}}
QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    border: none;
    background: transparent;
    width: 16px;
}}

/* ── DateEdit ────────────────────────────────────────────────── */
QDateEdit {{
    background-color: {p.bg_input};
    border: 1px solid {p.border};
    border-radius: {p.border_radius_sm}px;
    padding: 7px 10px;
    color: {p.text_primary};
}}
QDateEdit:focus {{ border-color: {p.border_focus}; }}

/* ── Butonlar ────────────────────────────────────────────────── */
QPushButton {{
    background-color: {p.bg_input};
    border: 1px solid {p.border};
    border-radius: {p.border_radius_sm}px;
    padding: 8px 18px;
    color: {p.text_primary};
    font-weight: 500;
    min-height: 32px;
}}
QPushButton:hover {{
    background-color: {p.bg_hover};
    border-color: {p.text_muted};
}}
QPushButton:pressed {{
    background-color: {p.bg_panel};
}}
QPushButton:disabled {{
    color: {p.text_disabled};
    border-color: {p.border};
    background-color: {p.bg_panel};
}}

/* Primary (mavi) */
QPushButton[primary="true"] {{
    background-color: {p.accent};
    border-color: {p.accent};
    color: white;
    font-weight: 600;
}}
QPushButton[primary="true"]:hover {{
    background-color: {p.accent_hover};
    border-color: {p.accent_hover};
}}
QPushButton[primary="true"]:pressed {{
    background-color: {p.accent};
}}
QPushButton[primary="true"]:disabled {{
    background-color: {p.accent_dim};
    border-color: {p.accent_dim};
    color: {p.text_muted};
}}

/* Danger (kırmızı) */
QPushButton[danger="true"] {{
    background-color: {p.danger};
    border-color: {p.danger};
    color: white;
    font-weight: 600;
}}
QPushButton[danger="true"]:hover {{
    background-color: #ff6b63;
    border-color: #ff6b63;
}}

/* Ghost (çerçevesiz) */
QPushButton[ghost="true"] {{
    background-color: transparent;
    border-color: transparent;
    color: {p.text_secondary};
}}
QPushButton[ghost="true"]:hover {{
    background-color: {p.bg_hover};
    color: {p.text_primary};
}}

/* ── Checkbox / Radio ────────────────────────────────────────── */
QCheckBox, QRadioButton {{
    color: {p.text_primary};
    spacing: 8px;
}}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {p.border};
    border-radius: 3px;
    background-color: {p.bg_input};
}}
QRadioButton::indicator {{
    border-radius: 8px;
}}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background-color: {p.accent};
    border-color: {p.accent};
}}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
    border-color: {p.border_focus};
}}

/* ── Tablo ───────────────────────────────────────────────────── */
QTableView {{
    background-color: {p.bg_card};
    border: 1px solid {p.border};
    border-radius: {p.border_radius}px;
    gridline-color: {p.border};
    alternate-background-color: {p.bg_input};
    show-decoration-selected: 1;
}}
QTableView::item {{
    padding: 6px 12px;
    border: none;
}}
QTableView::item:selected {{
    background-color: {p.bg_selected};
    color: {p.text_primary};
}}
QTableView::item:hover:!selected {{
    background-color: {p.bg_hover};
}}
QHeaderView::section {{
    background-color: {p.bg_panel};
    color: {p.text_secondary};
    border: none;
    border-bottom: 1px solid {p.border};
    border-right: 1px solid {p.border};
    padding: 8px 12px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}}
QHeaderView::section:last {{
    border-right: none;
}}

/* ── TabWidget ───────────────────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {p.border};
    border-radius: {p.border_radius}px;
    background-color: {p.bg_card};
    top: -1px;
}}
QTabBar::tab {{
    background-color: {p.bg_panel};
    border: 1px solid {p.border};
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    padding: 8px 20px;
    color: {p.text_secondary};
    font-weight: 500;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background-color: {p.bg_card};
    color: {p.text_primary};
    border-bottom: 2px solid {p.accent};
}}
QTabBar::tab:hover:!selected {{
    color: {p.text_primary};
    background-color: {p.bg_hover};
}}

/* ── ScrollBar ───────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background-color: {p.border};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {p.text_muted};
}}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
    background: none;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background-color: {p.border};
    border-radius: 4px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{
    background-color: {p.text_muted};
}}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0;
    background: none;
}}

/* ── Splitter ────────────────────────────────────────────────── */
QSplitter::handle {{
    background-color: {p.border};
}}

/* ── ToolTip ─────────────────────────────────────────────────── */
QToolTip {{
    background-color: {p.bg_card};
    color: {p.text_primary};
    border: 1px solid {p.border};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}}

/* ── Menu ────────────────────────────────────────────────────── */
QMenu {{
    background-color: {p.bg_card};
    border: 1px solid {p.border};
    border-radius: {p.border_radius_sm}px;
    padding: 4px;
}}
QMenu::item {{
    padding: 7px 20px;
    border-radius: 4px;
    color: {p.text_primary};
}}
QMenu::item:selected {{
    background-color: {p.bg_hover};
}}
QMenu::separator {{
    height: 1px;
    background-color: {p.border};
    margin: 4px 8px;
}}

/* ── StatusBar ───────────────────────────────────────────────── */
QStatusBar {{
    background-color: {p.bg_panel};
    color: {p.text_secondary};
    border-top: 1px solid {p.border};
    font-size: 12px;
}}

/* ── MessageBox ──────────────────────────────────────────────── */
QMessageBox {{
    background-color: {p.bg_card};
    border: 1px solid {p.border};
    border-radius: {p.border_radius}px;
}}
QMessageBox QLabel {{
    color: {p.text_primary};
    background: transparent;
}}

/* ── Dialog ──────────────────────────────────────────────────── */
QDialog {{
    background-color: {p.bg_card};
    border: 1px solid {p.border};
    border-radius: {p.border_radius}px;
}}
"""


# ══════════════════════════════════════════════════════════════════
#  FONT
# ══════════════════════════════════════════════════════════════════

def _uygulama_fontu() -> QFont:
    font = QFont()
    # Platform'a göre en iyi sistemi seç
    for aday in ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Arial"):
        f = QFont(aday)
        if f.exactMatch():
            font = f
            break
    font.setPointSize(10)
    return font


# ══════════════════════════════════════════════════════════════════
#  PUBLIC API
# ══════════════════════════════════════════════════════════════════

def apply(app: QApplication) -> None:
    """
    Temayı uygulamaya uygular.
    main.py'de QApplication oluşturulduktan hemen sonra çağırılır.

    Kullanım:
        app = QApplication(sys.argv)
        from ui.theme import apply
        apply(app)
    """
    app.setStyle("Fusion")
    app.setFont(_uygulama_fontu())
    app.setStyleSheet(_stylesheet())

    # Qt palette — sistem dialog'ları için de koyu tema
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor(T.bg_app))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor(T.text_primary))
    palette.setColor(QPalette.ColorRole.Base,            QColor(T.bg_input))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(T.bg_card))
    palette.setColor(QPalette.ColorRole.Text,            QColor(T.text_primary))
    palette.setColor(QPalette.ColorRole.Button,          QColor(T.bg_input))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor(T.text_primary))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor(T.accent))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Link,            QColor(T.text_link))
    palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor(T.bg_card))
    palette.setColor(QPalette.ColorRole.ToolTipText,     QColor(T.text_primary))
    app.setPalette(palette)
