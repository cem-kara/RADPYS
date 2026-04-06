# -*- coding: utf-8 -*-
"""
ui/app_window.py
────────────────
Ana uygulama penceresi.

Yapı:
  ┌────────┬────────────────────────────────────┐
  │Sidebar │         İçerik Alanı               │
  │ 72px   │         (QStackedWidget)           │
  └────────┴────────────────────────────────────┘
"""
from __future__ import annotations
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont
from ui.theme import T
from app.db.database import Database


# ══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════

class _SidebarBtn(QPushButton):
    """İkon + etiket — sidebar navigasyon butonu."""

    def __init__(self, ikon: str, etiket: str, sayfa: str, parent=None):
        super().__init__(parent)
        self.sayfa   = sayfa
        self._ikon   = ikon
        self._etiket = etiket
        self._aktif  = False

        self.setFixedWidth(T.sidebar_width)
        self.setFixedHeight(64)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(True)

        # Layout bir kez kurulur; stil güncellemelerinde tekrar oluşturulmaz.
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._ikon_lbl = QLabel(self._ikon)
        self._ikon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._ikon_lbl.setStyleSheet("font-size:18px; background:transparent;")
        self._ikon_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self._txt_lbl = QLabel(self._etiket)
        self._txt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._txt_lbl.setStyleSheet("font-size:9px; background:transparent;")
        self._txt_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        lay.addWidget(self._ikon_lbl)
        lay.addWidget(self._txt_lbl)

        self._uygula_stil()

    def set_aktif(self, aktif: bool) -> None:
        self._aktif = aktif
        self.setChecked(aktif)
        self._uygula_stil()

    def _uygula_stil(self):
        renk      = T.accent if self._aktif else T.text_muted
        bg        = T.accent_dim if self._aktif else "transparent"
        border    = f"border-left: 2px solid {T.accent};" if self._aktif else \
                    "border-left: 2px solid transparent;"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                {border}
                border-top: none;
                border-right: none;
                border-bottom: none;
                border-radius: 0;
                padding: 0;
                color: {renk};
                font-size: 20px;
            }}
            QPushButton:hover {{
                background-color: {T.bg_hover};
                color: {T.text_primary};
            }}
        """)

        self._ikon_lbl.setStyleSheet(
            f"color:{renk}; font-size:18px; background:transparent;"
        )
        self._txt_lbl.setStyleSheet(
            f"color:{renk}; font-size:9px; background:transparent;"
        )


class Sidebar(QFrame):
    """Sol navigasyon çubuğu."""

    sayfa_degisti = Signal(str)

    MENU = [
        ("⊞",  "Panel",    "dashboard"),
        ("👥", "Personel", "personel"),
        ("📅", "Nöbet",    "nobet"),
        ("🔧", "Cihaz",    "cihaz"),
        ("📊", "Rapor",    "rapor"),
        ("⚙",  "Ayarlar",  "ayarlar"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(T.sidebar_width)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {T.bg_panel};
                border-right: 1px solid {T.border};
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Logo alanı
        logo = QLabel("R")
        logo.setFixedHeight(56)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont()
        f.setPointSize(20)
        f.setBold(True)
        logo.setFont(f)
        logo.setStyleSheet(f"color:{T.accent}; background:transparent;")
        lay.addWidget(logo)

        # Ayraç
        ayr = QFrame()
        ayr.setFrameShape(QFrame.Shape.HLine)
        ayr.setStyleSheet(f"background:{T.border}; max-height:1px;")
        lay.addWidget(ayr)

        # Menü butonları
        self._butonlar: dict[str, _SidebarBtn] = {}
        for ikon, etiket, sayfa in self.MENU:
            btn = _SidebarBtn(ikon, etiket, sayfa, self)
            btn.clicked.connect(lambda _, s=sayfa: self._secildi(s))
            lay.addWidget(btn)
            self._butonlar[sayfa] = btn

        lay.addStretch()

        # İlk sayfa aktif
        self._secildi("dashboard")

    def _secildi(self, sayfa: str) -> None:
        for k, btn in self._butonlar.items():
            btn.set_aktif(k == sayfa)
        self.sayfa_degisti.emit(sayfa)


# ══════════════════════════════════════════════════════════════════
#  PLACEHOLDER SAYFALAR (Sprint 2-6'da doldurulacak)
# ══════════════════════════════════════════════════════════════════

def _placeholder(baslik: str) -> QWidget:
    w   = QWidget()
    lay = QVBoxLayout(w)
    lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl = QLabel(baslik)
    lbl.setStyleSheet(
        f"color:{T.text_muted}; font-size:24px; font-weight:600;"
    )
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lay.addWidget(lbl)
    alt = QLabel("Bu sayfa henüz hazırlanıyor.")
    alt.setAlignment(Qt.AlignmentFlag.AlignCenter)
    alt.setStyleSheet(f"color:{T.text_muted}; font-size:13px;")
    lay.addWidget(alt)
    return w


# ══════════════════════════════════════════════════════════════════
#  ANA PENCERE
# ══════════════════════════════════════════════════════════════════

class AppWindow(QMainWindow):
    """
    Ana uygulama penceresi.

    Sidebar + QStackedWidget yapısı.
    Sayfalar lazy olarak oluşturulur — Sprint 2-6'da doldurulacak.
    """

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self._db = db
        self.setWindowTitle("REPYS 2.0")
        self.resize(1440, 900)
        self.setMinimumSize(1024, 700)
        self._build()

    def _build(self):
        merkez = QWidget()
        self.setCentralWidget(merkez)

        root = QHBoxLayout(merkez)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self._sidebar = Sidebar(self)
        self._sidebar.sayfa_degisti.connect(self._goto)
        root.addWidget(self._sidebar)

        # İçerik alanı
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(
            f"background-color:{T.bg_app};"
        )
        root.addWidget(self._stack, 1)

        # Sayfalar — placeholder, Sprint 2'den itibaren gerçek sayfalar
        self._sayfalar: dict[str, QWidget] = {}
        for sayfa in ("dashboard", "personel", "nobet",
                      "cihaz", "rapor", "ayarlar"):
            w = self._sayfa_olustur(sayfa)
            self._sayfalar[sayfa] = w
            self._stack.addWidget(w)

        # Başlangıç sayfası
        self._goto("dashboard")

    def _sayfa_olustur(self, sayfa: str) -> QWidget:
        """Gerçek sayfa sınıfları — henüz yazılmayanlar placeholder."""
        if sayfa == "personel":
            from ui.pages.personel.personel_page import PersonelPage
            return PersonelPage(self._db)
        basliklar = {
            "dashboard": "📊 Dashboard",
            "nobet":     "📅 Nöbet Planlama",
            "cihaz":     "🔧 Cihaz Yönetimi",
            "rapor":     "📊 Raporlar",
            "ayarlar":   "⚙ Ayarlar",
        }
        return _placeholder(basliklar.get(sayfa, sayfa))

    def _goto(self, sayfa: str) -> None:
        w = self._sayfalar.get(sayfa)
        if w:
            self._stack.setCurrentWidget(w)
