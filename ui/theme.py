# -*- coding: utf-8 -*-
"""ui/theme.py — HTML referansından alınan renk paleti ve stylesheet"""
from __future__ import annotations
from dataclasses import dataclass
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QPalette, QColor


@dataclass(frozen=True)
class _Palette:
    # ── Arka planlar (HTML: --bg0 → --bg4) ──────────────────────
    bg0: str = "#0b0f14"   # En derin — uygulama zemini
    bg1: str = "#101722"   # Topbar, sidebar
    bg2: str = "#141e2b"   # Kart, panel
    bg3: str = "#1a2636"   # Hover, seçili
    bg4: str = "#223247"   # Input, progress track

    # ── Kenarlıklar ───────────────────────────────────────────────
    border:  str = "rgba(255,255,255,0.06)"
    border2: str = "rgba(255,255,255,0.12)"

    # ── Metin ─────────────────────────────────────────────────────
    text:  str = "#e6edf6"    # Birincil
    text2: str = "#b6c2d2"    # İkincil
    text3: str = "#7e8ca3"    # Soluk
    text4: str = "#4a5b73"    # En soluk

    # ── Anlam renkleri ────────────────────────────────────────────
    accent:  str = "#23c5b8"
    accent2: str = "#45d7cd"
    accent3: str = "#7ae4dd"

    green:   str = "#1fbf76"
    green2:  str = "#34e58b"
    red:     str = "#e24d5f"
    red2:    str = "#ff6f84"
    amber:   str = "#e0a73a"
    amber2:  str = "#f6c356"
    purple:  str = "#2f7dd1"
    purple2: str = "#5aa1e6"
    teal:    str = "#0f8f8a"
    teal2:   str = "#2cc8bf"

    # ── Layout ────────────────────────────────────────────────────
    sidebar_w: int = 240
    topbar_h:  int = 52
    radius:    int = 12
    radius_sm: int = 9


T = _Palette()


def _qss(p: _Palette = T) -> str:
    return f"""
/* ── Global ─────────────────────────────────────── */
* {{ outline: 0; }}
QWidget {{
    background-color: {p.bg0};
    color: {p.text};
    font-family: "IBM Plex Sans","Source Sans 3","Work Sans","Noto Sans","Segoe UI",sans-serif;
    font-size: 12.5px;
    selection-background-color: {p.accent};
    selection-color: white;
}}
QWidget#AppRoot {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 {p.bg0}, stop:1 {p.bg2});
}}
QMainWindow, QDialog {{
    background-color: {p.bg0};
}}

/* ── Inputs ──────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {p.bg2};
    border: 1px solid {p.border2};
    border-radius: {p.radius_sm}px;
    padding: 7px 12px;
    color: {p.text};
}}
QLineEdit:focus, QTextEdit:focus {{
    border-color: {p.accent};
}}
QLineEdit:disabled {{ color: {p.text3}; background: {p.bg1}; }}

/* ── ComboBox ────────────────────────────────────── */
QComboBox {{
    background-color: {p.bg2};
    border: 1px solid {p.border2};
    border-radius: {p.radius_sm}px;
    padding: 7px 12px;
    color: {p.text};
    min-width: 80px;
}}
QComboBox:focus {{ border-color: {p.accent}; }}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox::down-arrow {{
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {p.text2};
    width: 0; height: 0; margin-right: 6px;
}}
QComboBox QAbstractItemView {{
    background-color: {p.bg2};
    border: 1px solid {p.border2};
    border-radius: {p.radius_sm}px;
    color: {p.text};
    selection-background-color: {p.bg3};
    outline: 0;
    padding: 4px;
}}
QComboBox QAbstractItemView::item {{
    padding: 6px 10px;
    border-radius: 5px;
    min-height: 26px;
}}

/* ── Butonlar ────────────────────────────────────── */
QPushButton {{
    background-color: {p.bg2};
    border: 1px solid {p.border2};
    border-radius: {p.radius_sm}px;
    padding: 7px 14px;
    color: {p.text2};
    font-size: 11.5px;
    min-height: 28px;
}}
QPushButton:hover {{
    background-color: {p.bg3};
    color: {p.text};
    border-color: {p.accent2};
}}
QPushButton:pressed {{ background-color: {p.bg4}; }}
QPushButton:disabled {{ color: {p.text3}; }}

QPushButton[primary="true"] {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 {p.accent}, stop:1 {p.accent2});
    border: none;
    color: white;
    font-weight: 600;
}}
QPushButton[primary="true"]:hover {{ background-color: {p.accent2}; }}

QPushButton[danger="true"] {{
    background-color: rgba(226,77,95,0.16);
    border: 1px solid rgba(226,77,95,0.35);
    color: {p.red2};
}}
QPushButton[danger="true"]:hover {{
    background-color: rgba(232,58,90,0.25);
}}

QPushButton[ghost="true"] {{
    background-color: transparent;
    border-color: transparent;
    color: {p.text3};
}}
QPushButton[ghost="true"]:hover {{
    background-color: {p.bg3};
    color: {p.text};
}}

/* ── GroupBox ────────────────────────────────────── */
QGroupBox {{
    background-color: {p.bg1};
    border: 1px solid {p.border};
    border-radius: {p.radius}px;
    margin-top: 10px;
    padding: 14px 10px 10px 10px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: {p.text3};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px; top: -6px;
    background-color: {p.bg1};
    padding: 0 4px;
}}

/* ── Tablo ───────────────────────────────────────── */
QTableView {{
    background-color: {p.bg1};
    border: 1px solid {p.border};
    border-radius: {p.radius}px;
    gridline-color: rgba(255,255,255,0.04);
    alternate-background-color: {p.bg2};
    show-decoration-selected: 1;
}}
QTableView::item {{
    padding: 6px 10px;
    border: none;
    color: {p.text2};
}}
QTableView::item:selected {{
    background-color: rgba(52,121,255,0.12);
    color: {p.text};
}}
QTableView::item:hover:!selected {{
    background-color: rgba(90,130,200,0.05);
}}
QHeaderView::section {{
    background-color: {p.bg1};
    color: {p.text3};
    border: none;
    border-bottom: 1px solid {p.border};
    border-right: 1px solid {p.border};
    padding: 7px 10px;
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}}
QHeaderView::section:last {{ border-right: none; }}

/* ── TabWidget ───────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {p.border};
    border-radius: {p.radius}px;
    background-color: {p.bg1};
    top: -1px;
}}
QTabBar {{
    background: transparent;
}}
QTabBar::tab {{
    background-color: {p.bg2};
    border: none;
    border-radius: 5px;
    padding: 5px 14px;
    color: {p.text3};
    font-size: 10.5px;
    margin-right: 2px;
    font-family: "IBM Plex Sans","Source Sans 3","Work Sans","Noto Sans",sans-serif;
}}
QTabBar::tab:selected {{
    background-color: {p.bg3};
    color: {p.text};
}}
QTabBar::tab:hover:!selected {{
    color: {p.text2};
    background-color: {p.bg3};
}}

/* ── ScrollBar ───────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 6px; margin: 2px;
}}
QScrollBar::handle:vertical {{
    background-color: {p.bg4};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background-color: {p.text3}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0; background: none;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 6px; margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background-color: {p.bg4};
    border-radius: 3px;
    min-width: 30px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0; background: none;
}}

/* ── Splitter ────────────────────────────────────── */
QSplitter::handle {{
    background-color: {p.border};
}}

/* ── ToolTip ─────────────────────────────────────── */
QToolTip {{
    background-color: {p.bg3};
    color: {p.text};
    border: 1px solid {p.border2};
    border-radius: 5px;
    padding: 4px 8px;
    font-size: 11px;
}}

/* ── Menu ────────────────────────────────────────── */
QMenu {{
    background-color: {p.bg2};
    border: 1px solid {p.border2};
    border-radius: {p.radius_sm}px;
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 20px;
    border-radius: 4px;
    color: {p.text2};
    font-size: 11.5px;
}}
QMenu::item:selected {{ background-color: {p.bg3}; color: {p.text}; }}
QMenu::separator {{
    height: 1px;
    background-color: {p.border};
    margin: 4px 8px;
}}

/* ── Dialog ──────────────────────────────────────── */
QDialog {{
    background-color: {p.bg1};
    border: 1px solid {p.border2};
    border-radius: {p.radius}px;
}}

/* ── Frame ───────────────────────────────────────── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {p.border};
}}

/* ── Checkbox ────────────────────────────────────── */
QCheckBox {{ color: {p.text}; spacing: 8px; }}
QCheckBox::indicator {{
    width: 15px; height: 15px;
    border: 1px solid {p.border2};
    border-radius: 4px;
    background-color: {p.bg2};
}}
QCheckBox::indicator:checked {{
    background-color: {p.accent};
    border-color: {p.accent};
}}

/* ── SpinBox ─────────────────────────────────────── */
QSpinBox, QDoubleSpinBox {{
    background-color: {p.bg2};
    border: 1px solid {p.border2};
    border-radius: {p.radius_sm}px;
    padding: 7px 12px;
    color: {p.text};
}}
QSpinBox:focus, QDoubleSpinBox:focus {{ border-color: {p.accent}; }}
QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    border: none; background: transparent; width: 16px;
}}
"""


def apply(app: QApplication) -> None:
    app.setStyle("Fusion")
    font = QFont()
    for aday in ("IBM Plex Sans", "Source Sans 3", "Work Sans", "Noto Sans", "Segoe UI"):
        f = QFont(aday)
        if f.exactMatch():
            font = f
            break
    font.setPointSize(10)
    app.setFont(font)
    app.setStyleSheet(_qss())

    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window,        QColor(T.bg0))
    pal.setColor(QPalette.ColorRole.WindowText,    QColor(T.text))
    pal.setColor(QPalette.ColorRole.Base,          QColor(T.bg2))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(T.bg1))
    pal.setColor(QPalette.ColorRole.Text,          QColor(T.text))
    pal.setColor(QPalette.ColorRole.Button,        QColor(T.bg2))
    pal.setColor(QPalette.ColorRole.ButtonText,    QColor(T.text))
    pal.setColor(QPalette.ColorRole.Highlight,     QColor(T.accent))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    pal.setColor(QPalette.ColorRole.ToolTipBase,   QColor(T.bg3))
    pal.setColor(QPalette.ColorRole.ToolTipText,   QColor(T.text))
    app.setPalette(pal)
