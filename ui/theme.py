# -*- coding: utf-8 -*-
"""ui/theme.py — HTML referansından alınan renk paleti ve stylesheet"""
from __future__ import annotations
from dataclasses import dataclass
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QPalette, QColor


@dataclass(frozen=True)
class _Palette:
    # ── Arka planlar (HTML: --bg0 → --bg4) ──────────────────────
    bg0: str = "#070b11"   # En derin — uygulama zemini
    bg1: str = "#0c1320"   # Topbar, sidebar
    bg2: str = "#101828"   # Kart, panel
    bg3: str = "#162036"   # Hover, seçili
    bg4: str = "#1c2a44"   # Input, progress track

    # ── Kenarlıklar ───────────────────────────────────────────────
    border:  str = "rgba(90,130,200,0.10)"
    border2: str = "rgba(90,130,200,0.22)"

    # ── Metin ─────────────────────────────────────────────────────
    text:  str = "#cdd8f0"    # Birincil
    text2: str = "#6e88b0"    # İkincil
    text3: str = "#3a506e"    # Soluk
    text4: str = "#1e3050"    # En soluk

    # ── Anlam renkleri ────────────────────────────────────────────
    accent:  str = "#3479ff"
    accent2: str = "#5b9bff"
    accent3: str = "#8cbfff"

    green:   str = "#1db86a"
    green2:  str = "#24e07f"
    red:     str = "#e83a5a"
    red2:    str = "#ff6080"
    amber:   str = "#e8a020"
    amber2:  str = "#ffbb40"
    purple:  str = "#8b5cf6"
    purple2: str = "#a78bfa"
    teal:    str = "#0d9488"
    teal2:   str = "#2dd4bf"

    # ── Layout ────────────────────────────────────────────────────
    sidebar_w: int = 200
    topbar_h:  int = 44
    radius:    int = 10
    radius_sm: int = 7


T = _Palette()


def _qss(p: _Palette = T) -> str:
    return f"""
/* ── Global ─────────────────────────────────────── */
* {{ outline: 0; }}
QWidget {{
    background-color: {p.bg0};
    color: {p.text};
    font-family: "Segoe UI", "SF Pro Text", system-ui, sans-serif;
    font-size: 12px;
    selection-background-color: {p.accent};
    selection-color: white;
}}
QMainWindow, QDialog {{
    background-color: {p.bg0};
}}

/* ── Inputs ──────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {p.bg2};
    border: 1px solid rgba(90,130,200,0.15);
    border-radius: {p.radius_sm}px;
    padding: 6px 10px;
    color: {p.text};
}}
QLineEdit:focus, QTextEdit:focus {{
    border-color: {p.accent};
}}
QLineEdit:disabled {{ color: {p.text3}; background: {p.bg1}; }}

/* ── ComboBox ────────────────────────────────────── */
QComboBox {{
    background-color: {p.bg2};
    border: 1px solid rgba(90,130,200,0.15);
    border-radius: {p.radius_sm}px;
    padding: 6px 10px;
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
    border: 1px solid rgba(90,130,200,0.22);
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
    border: 1px solid rgba(90,130,200,0.18);
    border-radius: {p.radius_sm}px;
    padding: 6px 14px;
    color: {p.text2};
    font-size: 11px;
    min-height: 28px;
}}
QPushButton:hover {{
    background-color: {p.bg3};
    color: {p.text};
    border-color: rgba(90,130,200,0.30);
}}
QPushButton:pressed {{ background-color: {p.bg4}; }}
QPushButton:disabled {{ color: {p.text3}; }}

QPushButton[primary="true"] {{
    background-color: {p.accent};
    border: none;
    color: white;
    font-weight: 600;
}}
QPushButton[primary="true"]:hover {{ background-color: {p.accent2}; }}

QPushButton[danger="true"] {{
    background-color: rgba(232,58,90,0.15);
    border: 1px solid rgba(232,58,90,0.3);
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
    border: 1px solid rgba(90,130,200,0.10);
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
    border: 1px solid rgba(90,130,200,0.10);
    border-radius: {p.radius}px;
    gridline-color: rgba(90,130,200,0.05);
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
    border-bottom: 1px solid rgba(90,130,200,0.10);
    border-right: 1px solid rgba(90,130,200,0.05);
    padding: 7px 10px;
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}}
QHeaderView::section:last {{ border-right: none; }}

/* ── TabWidget ───────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid rgba(90,130,200,0.10);
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
    font-family: "Consolas","Courier New",monospace;
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
    width: 3px; margin: 2px;
}}
QScrollBar::handle:vertical {{
    background-color: {p.bg4};
    border-radius: 2px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background-color: {p.text3}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0; background: none;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 3px; margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background-color: {p.bg4};
    border-radius: 2px;
    min-width: 30px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0; background: none;
}}

/* ── Splitter ────────────────────────────────────── */
QSplitter::handle {{
    background-color: rgba(90,130,200,0.10);
}}

/* ── ToolTip ─────────────────────────────────────── */
QToolTip {{
    background-color: {p.bg3};
    color: {p.text};
    border: 1px solid rgba(90,130,200,0.22);
    border-radius: 5px;
    padding: 4px 8px;
    font-size: 11px;
}}

/* ── Menu ────────────────────────────────────────── */
QMenu {{
    background-color: {p.bg2};
    border: 1px solid rgba(90,130,200,0.22);
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
    background-color: rgba(90,130,200,0.10);
    margin: 4px 8px;
}}

/* ── Dialog ──────────────────────────────────────── */
QDialog {{
    background-color: {p.bg1};
    border: 1px solid rgba(90,130,200,0.22);
    border-radius: {p.radius}px;
}}

/* ── Frame ───────────────────────────────────────── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: rgba(90,130,200,0.15);
}}

/* ── Checkbox ────────────────────────────────────── */
QCheckBox {{ color: {p.text}; spacing: 8px; }}
QCheckBox::indicator {{
    width: 15px; height: 15px;
    border: 1px solid rgba(90,130,200,0.25);
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
    border: 1px solid rgba(90,130,200,0.15);
    border-radius: {p.radius_sm}px;
    padding: 6px 10px;
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
    for aday in ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Arial"):
        f = QFont(aday)
        if f.exactMatch():
            font = f
            break
    font.setPointSize(9)
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
