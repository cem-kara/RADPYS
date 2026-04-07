# -*- coding: utf-8 -*-
"""
ui/app_window.py
────────────────
REPYS 2.0 Ana Pencere.

Tasarım kararları:
  - Sidebar tamamen module_registry'den otomatik inşa edilir.
  - Yeni modül eklemek için bu dosyaya DOKUNULMAZ.
  - Topbar: logo, saat, bildirim, kullanıcı.
  - Sidebar: 220px, bölümlü, badge destekli.
  - Sayfalar: lazy yükleme (ilk tıklamada oluşturulur).

Layout:
  ┌─── Topbar 46px ─────────────────────────────────────────────┐
  ├─ Sidebar 220px ─┬─────── İçerik (QStackedWidget) ───────────┤
  │  [Bölüm başlığı]│                                            │
  │  ○ Dashboard    │                                            │
  │  ○ Personel  47 │                                            │
  │  ○ İzin Takip 6 │                                            │
  │  ─────────────  │                                            │
  │  [Cihaz]        │                                            │
  │  ...            │                                            │
  │  ─────────────  │                                            │
  │  [Kullanıcı]    │                                            │
  └─────────────────┴────────────────────────────────────────────┘
"""
from __future__ import annotations
from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal, QTimer
from ui.theme import T
from app.db.database import Database
import app.module_registry as reg


# ══════════════════════════════════════════════════════════════════
#  TOPBAR
# ══════════════════════════════════════════════════════════════════

class _Topbar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(46)
        self.setStyleSheet(
            f"QFrame{{background:{T.bg1};"
            f"border-bottom:1px solid rgba(90,130,200,0.12);}}"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(12)

        # Logo
        logo = QWidget()
        logo.setFixedWidth(220)
        logo.setStyleSheet("background:transparent;")
        ll = QHBoxLayout(logo)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(8)

        badge = QLabel("R")
        badge.setFixedSize(24, 24)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {T.accent},stop:1 {T.purple});"
            f"border-radius:6px;color:white;font-size:12px;"
            f"font-weight:800;letter-spacing:-0.5px;"
        )
        ll.addWidget(badge)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        title_col.setContentsMargins(0, 0, 0, 0)
        nm = QLabel("REPYS")
        nm.setStyleSheet(
            f"color:{T.text};font-size:13px;font-weight:700;"
            f"letter-spacing:0.05em;"
        )
        vr = QLabel("Radyoloji Yönetim Sistemi")
        vr.setStyleSheet(
            f"color:{T.text3};font-size:8.5px;letter-spacing:0.03em;"
        )
        title_col.addWidget(nm)
        title_col.addWidget(vr)
        ll.addLayout(title_col)
        ll.addStretch()

        lay.addWidget(logo)

        # Dikey ayraç
        sep = self._vsep()
        lay.addWidget(sep)
        lay.addStretch()

        # Saat + tarih
        self._saat = QLabel()
        self._saat.setStyleSheet(
            f"color:{T.text2};font-size:11.5px;"
            f"font-family:'Consolas','Courier New',monospace;letter-spacing:0.04em;"
        )
        lay.addWidget(self._saat)

        lay.addWidget(self._vsep())

        # Bildirim
        nb = QPushButton("🔔")
        nb.setFixedSize(30, 30)
        nb.setCursor(Qt.CursorShape.PointingHandCursor)
        nb.setStyleSheet(
            f"QPushButton{{background:{T.bg2};"
            f"border:1px solid rgba(90,130,200,0.12);border-radius:8px;"
            f"font-size:13px;color:{T.text2};}}"
            f"QPushButton:hover{{background:{T.bg3};color:{T.text};}}"
        )
        lay.addWidget(nb)

        lay.addWidget(self._vsep())

        # Avatar
        av = QLabel("AB")
        av.setFixedSize(28, 28)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {T.accent},stop:1 {T.purple2});"
            f"border-radius:14px;color:white;font-size:10px;font-weight:700;"
        )
        lay.addWidget(av)

        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(1000)
        self._tick()

    @staticmethod
    def _vsep() -> QFrame:
        s = QFrame()
        s.setFrameShape(QFrame.Shape.VLine)
        s.setFixedSize(1, 18)
        s.setStyleSheet("background:rgba(90,130,200,0.15);")
        return s

    def _tick(self):
        n = datetime.now()
        self._saat.setText(
            n.strftime("%d.%m.%Y") + "  " + n.strftime("%H:%M:%S")
        )


# ══════════════════════════════════════════════════════════════════
#  SIDEBAR BUTON
# ══════════════════════════════════════════════════════════════════

class _SbBtn(QFrame):
    """Tek sidebar navigasyon butonu."""

    clicked = Signal(str)

    def __init__(self, mod: reg.ModuleDef, parent=None):
        super().__init__(parent)
        self.mod_id = mod.id
        self._aktif = False

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 7, 10, 7)
        lay.setSpacing(9)

        self._ikon = QLabel(mod.icon)
        self._ikon.setFixedWidth(18)
        self._ikon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._ikon.setStyleSheet("font-size:14px;background:transparent;")

        self._lbl = QLabel(mod.label)
        self._lbl.setStyleSheet(f"font-size:12px;background:transparent;")

        lay.addWidget(self._ikon)
        lay.addWidget(self._lbl, 1)

        self._badge: QLabel | None = None
        if mod.badge_fn is not None:
            b = QLabel("")
            b.setAlignment(Qt.AlignmentFlag.AlignCenter)
            b.setFixedHeight(17)
            b.setContentsMargins(6, 0, 6, 0)
            b.setStyleSheet(
                f"background:{mod.badge_renk};color:white;"
                f"border-radius:4px;font-size:9px;font-weight:700;"
                f"font-family:'Consolas','Courier New',monospace;"
            )
            b.setVisible(False)
            lay.addWidget(b)
            self._badge = b

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._uygula_stil(False)

    def _uygula_stil(self, aktif: bool):
        if aktif:
            self.setStyleSheet(
                f"QFrame{{background:rgba(52,121,255,0.10);"
                f"border-left:2px solid {T.accent};"
                f"border-radius:0 8px 8px 0;margin:0 8px 0 0;}}"
            )
            c = T.accent2
        else:
            self.setStyleSheet(
                f"QFrame{{background:transparent;"
                f"border-left:2px solid transparent;"
                f"border-radius:0 8px 8px 0;margin:0 8px 0 0;}}"
                f"QFrame:hover{{background:{T.bg3};}}"
            )
            c = T.text2
        self._ikon.setStyleSheet(f"font-size:14px;color:{c};background:transparent;")
        self._lbl.setStyleSheet(f"font-size:12px;color:{c};background:transparent;")

    def set_aktif(self, aktif: bool):
        self._aktif = aktif
        self._uygula_stil(aktif)

    def set_badge(self, txt: str):
        if self._badge:
            self._badge.setText(txt)
            self._badge.setVisible(bool(txt))

    def mousePressEvent(self, _):
        self.clicked.emit(self.mod_id)


# ══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════

class Sidebar(QFrame):
    """
    Modül registry'den otomatik inşa edilen sidebar.
    Yeni modül eklenince bu sınıfa DOKUNULMAZ.
    """

    navigasyon = Signal(str)   # sayfa id'si emit edilir

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self._db      = db
        self._butonlar: dict[str, _SbBtn] = {}

        self.setFixedWidth(220)
        self.setStyleSheet(
            f"QFrame{{background:{T.bg1};"
            f"border-right:1px solid rgba(90,130,200,0.10);}}"
        )

        kok = QVBoxLayout(self)
        kok.setContentsMargins(0, 12, 0, 0)
        kok.setSpacing(0)

        # Scroll içerik
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background:transparent;")

        ic = QWidget()
        ic.setStyleSheet("background:transparent;")
        ic_lay = QVBoxLayout(ic)
        ic_lay.setContentsMargins(0, 0, 0, 0)
        ic_lay.setSpacing(2)

        # ── Registry'den bölümleri ve modülleri oku ───────────────
        for bolum, modlar in reg.get_bolumler():
            # Bölüm başlığı
            b_lbl = QLabel(bolum.label.upper())
            b_lbl.setContentsMargins(16, 8, 0, 4)
            b_lbl.setStyleSheet(
                f"color:{T.text4};font-size:9px;font-weight:700;"
                f"letter-spacing:0.14em;"
                f"font-family:'Consolas','Courier New',monospace;"
            )
            ic_lay.addWidget(b_lbl)

            # Modül butonları
            for mod in modlar:
                btn = _SbBtn(mod, ic)
                btn.clicked.connect(self._navigasyon)
                ic_lay.addWidget(btn)
                self._butonlar[mod.id] = btn

            # Bölüm ayracı
            ayr = QFrame()
            ayr.setFixedHeight(1)
            ayr.setStyleSheet(
                "background:rgba(90,130,200,0.07);margin:6px 12px;"
            )
            ic_lay.addWidget(ayr)

        ic_lay.addStretch()
        scroll.setWidget(ic)
        kok.addWidget(scroll, 1)

        # ── Kullanıcı footer ──────────────────────────────────────
        self._footer_olustur(kok)

        # Badge güncelleme timer'ı (30 sn'de bir)
        self._badge_timer = QTimer(self)
        self._badge_timer.timeout.connect(self._badge_guncelle)
        self._badge_timer.start(30_000)
        self._badge_guncelle()

        # Varsayılan seçim
        varsayilan = reg.get_varsayilan_id()
        if varsayilan:
            self._navigasyon(varsayilan)

    def _footer_olustur(self, kok: QVBoxLayout):
        ft = QFrame()
        ft.setStyleSheet(
            f"QFrame{{border-top:1px solid rgba(90,130,200,0.10);"
            f"background:transparent;}}"
            f"QFrame:hover{{background:{T.bg3};}}"
        )
        ft.setCursor(Qt.CursorShape.PointingHandCursor)
        fl = QHBoxLayout(ft)
        fl.setContentsMargins(12, 10, 12, 10)
        fl.setSpacing(10)

        av = QLabel("AB")
        av.setFixedSize(30, 30)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {T.accent},stop:1 {T.purple2});"
            f"border-radius:15px;color:white;font-size:11px;font-weight:700;"
        )
        fl.addWidget(av)

        uc = QVBoxLayout()
        uc.setSpacing(1)
        uc.setContentsMargins(0, 0, 0, 0)
        nm = QLabel("Admin")
        nm.setStyleSheet(
            f"font-size:12px;font-weight:600;color:{T.text};"
        )
        rl = QLabel("Sistem Yöneticisi")
        rl.setStyleSheet(f"font-size:9.5px;color:{T.text3};")
        uc.addWidget(nm)
        uc.addWidget(rl)
        fl.addLayout(uc, 1)

        more = QLabel("···")
        more.setStyleSheet(f"color:{T.text3};font-size:14px;")
        fl.addWidget(more)

        kok.addWidget(ft)

    def _navigasyon(self, mod_id: str):
        for k, btn in self._butonlar.items():
            btn.set_aktif(k == mod_id)
        self.navigasyon.emit(mod_id)

    def git(self, mod_id: str):
        self._navigasyon(mod_id)

    def _badge_guncelle(self):
        """Badge'leri registry'deki badge_fn ile günceller."""
        if not self._db:
            return
        for mod in reg.get_all():
            if mod.badge_fn and mod.id in self._butonlar:
                try:
                    deger = mod.badge_fn(self._db) or ""
                    self._butonlar[mod.id].set_badge(str(deger))
                except Exception:
                    pass


# ══════════════════════════════════════════════════════════════════
#  ANA PENCERE
# ══════════════════════════════════════════════════════════════════

class AppWindow(QMainWindow):
    """
    Ana uygulama penceresi.
    Sayfa listesi, sidebar menüsü — tamamen module_registry'den gelir.
    Yeni modül eklemek için bu dosyaya DOKUNULMAZ.
    """

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self._db    = db
        self._pages: dict[str, QWidget] = {}   # lazy cache
        self.setWindowTitle("REPYS 2.0")
        self.resize(1440, 900)
        self.setMinimumSize(1024, 700)
        self._build()

    def _build(self):
        root = QWidget()
        root.setStyleSheet(f"background:{T.bg0};")
        self.setCentralWidget(root)

        kok = QVBoxLayout(root)
        kok.setContentsMargins(0, 0, 0, 0)
        kok.setSpacing(0)

        # Topbar
        kok.addWidget(_Topbar(root))

        # Orta: sidebar + içerik
        orta = QWidget()
        orta.setStyleSheet("background:transparent;")
        ol = QHBoxLayout(orta)
        ol.setContentsMargins(0, 0, 0, 0)
        ol.setSpacing(0)

        self._sidebar = Sidebar(self._db, orta)
        self._sidebar.navigasyon.connect(self._goto)
        ol.addWidget(self._sidebar)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background:{T.bg0};")
        ol.addWidget(self._stack, 1)

        kok.addWidget(orta, 1)

    def _goto(self, mod_id: str):
        """Sayfayı göster. İlk ziyarette lazy olarak oluşturur."""
        if mod_id not in self._pages:
            try:
                page = reg.sayfa_olustur(mod_id, self._db)
            except Exception as e:
                from ui.pages.placeholder import PlaceholderPage
                page = PlaceholderPage(self._db)
            self._pages[mod_id] = page
            self._stack.addWidget(page)

        self._stack.setCurrentWidget(self._pages[mod_id])
