# -*- coding: utf-8 -*-
"""ui/pages/yonetim/ayarlar_page.py - Sistem ayarlari sayfasi.

Sabitler (lookup + gorev_yeri) ve Tatiller sekmelerini barindiran,
RBAC yonetiminden bagimsiz genel ayarlar ekrani.
"""
from __future__ import annotations

from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from app.db.database import Database
from ui.pages.yonetim.nobet_sablon_tab import NobetSablonTab
from ui.pages.yonetim.sabitler_tab import SabitlerTab
from ui.pages.yonetim.tatiller_tab import TatillerTab
from ui.styles import T


class AyarlarPage(QWidget):
    """Lookup/gorev_yeri sabitleri ve tatil takvimi icin ayarlar sayfasi."""

    def __init__(self, db: Database, oturum: dict | None = None, parent=None):
        super().__init__(parent)
        self._db = db
        self.setStyleSheet(f"background:{T.bg0};")
        self._build()

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self._tab_widget(), 1)

    def _tab_widget(self) -> QTabWidget:
        tabs = QTabWidget(self)
        tabs.setStyleSheet(
            f"""
            QTabWidget::pane {{
                border: 1px solid {T.border};
                background: {T.bg1};
                border-radius: 0 {T.radius}px {T.radius}px {T.radius}px;
            }}
            QTabBar::tab {{
                background: {T.bg0};
                color: {T.text2};
                border: 1px solid {T.border};
                border-bottom: none;
                padding: 8px 18px;
                border-radius: 8px 8px 0 0;
                margin-right: 3px;
                font-size: 12px;
            }}
            QTabBar::tab:selected {{
                background: {T.bg1};
                color: {T.text};
                border-bottom: 2px solid {T.accent};
                font-weight: 700;
            }}
            QTabBar::tab:hover:!selected {{
                background: {T.bg3};
                color: {T.text};
            }}
            """
        )
        tabs.addTab(self._sekme_sabitler(), "Sabitler")
        tabs.addTab(self._sekme_nobet_sablonlari(), "Nobet Sablonlari")
        tabs.addTab(self._sekme_tatiller(), "Tatiller")
        return tabs

    def _sekme_sabitler(self) -> QWidget:
        w = QWidget(self)
        w.setStyleSheet(f"background:{T.bg1};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(SabitlerTab(self._db, parent=w), 1)
        return w

    def _sekme_tatiller(self) -> QWidget:
        w = QWidget(self)
        w.setStyleSheet(f"background:{T.bg1};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(TatillerTab(self._db, parent=w), 1)
        return w

    def _sekme_nobet_sablonlari(self) -> QWidget:
        w = QWidget(self)
        w.setStyleSheet(f"background:{T.bg1};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(NobetSablonTab(self._db, parent=w), 1)
        return w
