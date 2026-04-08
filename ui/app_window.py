# -*- coding: utf-8 -*-
"""
ui/app_window.py — REPYS 2.0 Ana Pencere.
Tüm ikonlar ui/icons.py üzerinden qtawesome (mdi6) ile gelir.
"""
from __future__ import annotations
from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QFont
from ui.theme import T
from ui.icons import ic, Icon
import app.module_registry as reg
from app.db.database import Database


# ══════════════════════════════════════════════════════════════════
#  TOPBAR
# ══════════════════════════════════════════════════════════════════

class _Topbar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(T.topbar_h)
        self.setObjectName("Topbar")
        self.setStyleSheet(
            f"QFrame#Topbar{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {T.bg1},stop:1 {T.bg2});"
            f"border-bottom:1px solid {T.border};}}"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(12)

        # ── Logo bloğu ────────────────────────────────────────────
        logo_w = QWidget()
        logo_w.setFixedWidth(T.sidebar_w)
        logo_w.setStyleSheet("background:transparent;")
        ll = QHBoxLayout(logo_w)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(9)

        badge = QLabel("R")
        badge.setFixedSize(26, 26)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont(); f.setPointSize(10); f.setBold(True)
        badge.setFont(f)
        badge.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {T.accent},stop:1 {T.teal2});"
            f"border-radius:7px;color:white;"
        )
        ll.addWidget(badge)

        col = QVBoxLayout()
        col.setSpacing(0)
        col.setContentsMargins(0, 0, 0, 0)
        nm = QLabel("REPYS")
        nm.setStyleSheet(
            f"color:{T.text};font-size:13.5px;font-weight:700;"
            f"letter-spacing:0.04em;"
        )
        sub = QLabel("Radyoloji Yönetim Sistemi")
        sub.setStyleSheet(f"color:{T.text3};font-size:9px;")
        col.addWidget(nm)
        col.addWidget(sub)
        ll.addLayout(col)
        ll.addStretch()
        lay.addWidget(logo_w)

        lay.addWidget(self._vsep())
        lay.addStretch()

        # ── Saat ──────────────────────────────────────────────────
        self._clock = QLabel()
        self._clock.setStyleSheet(
            f"color:{T.text2};font-size:11.5px;"
            f"font-family:'IBM Plex Sans','Source Sans 3','Work Sans','Noto Sans',sans-serif;"
            f"letter-spacing:0.04em;"
        )
        lay.addWidget(self._clock)
        lay.addWidget(self._vsep())

        # ── Bildirim ikonu ────────────────────────────────────────
        nb = QPushButton()
        nb.setIcon(ic("bildirim", T.text2, 17))
        nb.setIconSize(QSize(17, 17))
        nb.setFixedSize(32, 32)
        nb.setCursor(Qt.CursorShape.PointingHandCursor)
        nb.setToolTip("Bildirimler")
        nb.setStyleSheet(
            f"QPushButton{{background:{T.bg2};"
            f"border:1px solid {T.border2};border-radius:8px;}}"
            f"QPushButton:hover{{background:{T.bg3};border-color:{T.accent2};}}"
        )
        lay.addWidget(nb)
        lay.addWidget(self._vsep())

        # ── Kullanıcı avatarı ─────────────────────────────────────
        av = QLabel("AB")
        av.setFixedSize(28, 28)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f2 = QFont(); f2.setPointSize(9); f2.setBold(True)
        av.setFont(f2)
        av.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {T.accent},stop:1 {T.teal2});"
            f"border-radius:14px;color:white;"
        )
        lay.addWidget(av)

        timer = QTimer(self)
        timer.timeout.connect(self._tick)
        timer.start(1000)
        self._tick()

    @staticmethod
    def _vsep() -> QFrame:
        s = QFrame()
        s.setFrameShape(QFrame.Shape.VLine)
        s.setFixedSize(1, 18)
        s.setStyleSheet(f"background:{T.border};")
        return s

    def _tick(self):
        n = datetime.now()
        self._clock.setText(
            n.strftime("%d.%m.%Y") + "   " + n.strftime("%H:%M:%S")
        )


# ══════════════════════════════════════════════════════════════════
#  SIDEBAR BUTONU
# ══════════════════════════════════════════════════════════════════

class _SbBtn(QFrame):
    """Tek sidebar navigasyon butonu — QIcon tabanlı."""

    clicked = Signal(str)

    def __init__(self, mod: reg.ModuleDef, parent=None):
        super().__init__(parent)
        self.mod_id = mod.id

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 8, 12, 8)
        lay.setSpacing(10)

        # İkon etiketi — QLabel ile pixmap
        self._ikon_lbl = QLabel()
        self._ikon_lbl.setFixedSize(18, 18)
        self._ikon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._ikon_lbl.setStyleSheet("background:transparent;")

        self._txt_lbl = QLabel(mod.label)
        self._txt_lbl.setStyleSheet(f"font-size:12px;background:transparent;")

        lay.addWidget(self._ikon_lbl)
        lay.addWidget(self._txt_lbl, 1)

        # Badge
        self._badge: QLabel | None = None
        if mod.badge_fn is not None:
            b = QLabel("")
            b.setAlignment(Qt.AlignmentFlag.AlignCenter)
            b.setContentsMargins(5, 0, 5, 0)
            b.setFixedHeight(17)
            b.setStyleSheet(
                f"background:{mod.badge_renk};color:white;"
                f"border-radius:4px;font-size:9px;font-weight:700;"
                f"font-family:'Consolas','Courier New',monospace;"
            )
            b.setVisible(False)
            lay.addWidget(b)
            self._badge = b

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._mod_icon = mod.icon
        self._uygula_stil(False)

    def _uygula_stil(self, aktif: bool):
        if aktif:
            self.setStyleSheet(
                f"QFrame{{background:rgba(35,197,184,0.12);"
                f"border-left:3px solid {T.accent};"
                f"border-radius:10px;margin:2px 10px 2px 8px;}}"
            )
            renk = T.accent2
        else:
            self.setStyleSheet(
                f"QFrame{{background:transparent;"
                f"border-left:3px solid transparent;"
                f"border-radius:10px;margin:2px 10px 2px 8px;}}"
                f"QFrame:hover{{background:{T.bg3};}}"
            )
            renk = T.text2

        # İkonu yeni renkle güncelle
        from ui.icons import pixmap as ipx
        self._ikon_lbl.setPixmap(ipx(self._mod_icon, renk, 16))
        self._txt_lbl.setStyleSheet(
            f"font-size:12px;color:{renk};background:transparent;"
        )

    def set_aktif(self, aktif: bool):
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
    """Registry-driven sidebar. Yeni modül için DOKUNMA."""

    navigasyon = Signal(str)

    def __init__(self, db: Database, oturum: dict | None = None, parent=None):
        super().__init__(parent)
        self._db = db
        self._oturum = oturum
        self._butonlar: dict[str, _SbBtn] = {}

        self.setFixedWidth(T.sidebar_w)
        self.setStyleSheet(
            f"QFrame{{background:{T.bg1};"
            f"border-right:1px solid {T.border};}}"
        )

        kok = QVBoxLayout(self)
        kok.setContentsMargins(0, 12, 0, 0)
        kok.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background:transparent;")

        ic_w = QWidget()
        ic_w.setStyleSheet("background:transparent;")
        ic_lay = QVBoxLayout(ic_w)
        ic_lay.setContentsMargins(0, 0, 0, 0)
        ic_lay.setSpacing(2)

        from app.rbac import modul_gorunur_mu
        for bolum, modlar in reg.get_bolumler():
            gorunen_modlar = [m for m in modlar if modul_gorunur_mu(oturum, m.id)]
            if not gorunen_modlar:
                continue
            # Bölüm başlığı
            blbl = QLabel(bolum.label.upper())
            blbl.setContentsMargins(16, 8, 0, 4)
            blbl.setStyleSheet(
                f"color:{T.text4};font-size:9px;font-weight:700;"
                f"letter-spacing:0.14em;"
                f"font-family:'IBM Plex Sans','Source Sans 3','Work Sans','Noto Sans',sans-serif;"
            )
            ic_lay.addWidget(blbl)

            for mod in gorunen_modlar:
                btn = _SbBtn(mod, ic_w)
                btn.clicked.connect(self._navigasyon)
                ic_lay.addWidget(btn)
                self._butonlar[mod.id] = btn

            ayr = QFrame()
            ayr.setFixedHeight(1)
            ayr.setStyleSheet(
                f"background:rgba(90,130,200,0.07);margin:6px 12px;"
            )
            ic_lay.addWidget(ayr)

        ic_lay.addStretch()
        scroll.setWidget(ic_w)
        kok.addWidget(scroll, 1)

        # Footer
        self._footer_olustur(kok)

        # Badge timer
        self._badge_timer = QTimer(self)
        self._badge_timer.timeout.connect(self._badge_guncelle)
        self._badge_timer.start(30_000)
        self._badge_guncelle()

        # Varsayılan sayfa
        v = reg.get_varsayilan_id()
        if v:
            self._navigasyon(v)

    def _footer_olustur(self, kok: QVBoxLayout):
        ft = QFrame()
        ft.setStyleSheet(
            f"QFrame{{border-top:1px solid {T.border};background:transparent;}}"
            f"QFrame:hover{{background:{T.bg3};}}"
        )
        ft.setCursor(Qt.CursorShape.PointingHandCursor)
        fl = QHBoxLayout(ft)
        fl.setContentsMargins(12, 10, 12, 10)
        fl.setSpacing(10)

        # Kullanıcı ikon etiketi
        ikon_lbl = QLabel()
        ikon_lbl.setFixedSize(30, 30)
        ikon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        from ui.icons import pixmap as ipx
        ikon_lbl.setPixmap(ipx("kullanici", T.accent2, 22))
        ikon_lbl.setStyleSheet(
            f"background:rgba(52,121,255,0.12);"
            f"border-radius:15px;"
        )
        fl.addWidget(ikon_lbl)

        uc = QVBoxLayout()
        uc.setSpacing(1)
        uc.setContentsMargins(0, 0, 0, 0)
        from app.rbac import kullanici_kisa_ad, rol as _rol
        _ad = kullanici_kisa_ad(self._oturum)
        _rol_str = _rol(self._oturum)
        _rol_etiket = {"admin": "Sistem Yöneticisi", "yonetici": "Yönetici", "kullanici": "Kullanıcı"}.get(_rol_str, _rol_str)
        nm = QLabel(_ad)
        nm.setStyleSheet(f"font-size:12px;font-weight:600;color:{T.text};")
        rl = QLabel(_rol_etiket)
        rl.setStyleSheet(f"font-size:9.5px;color:{T.text3};")
        uc.addWidget(nm)
        uc.addWidget(rl)
        fl.addLayout(uc, 1)

        more_lbl = Icon.label("ayarlar", T.text3, 14)
        fl.addWidget(more_lbl)

        kok.addWidget(ft)

    def _navigasyon(self, mod_id: str):
        for k, btn in self._butonlar.items():
            btn.set_aktif(k == mod_id)
        self.navigasyon.emit(mod_id)

    def git(self, mod_id: str):
        self._navigasyon(mod_id)

    def _badge_guncelle(self):
        if not self._db:
            return
        for mod in reg.get_all():
            if mod.badge_fn and mod.id in self._butonlar:
                try:
                    self._butonlar[mod.id].set_badge(
                        str(mod.badge_fn(self._db) or "")
                    )
                except Exception:
                    pass


# ══════════════════════════════════════════════════════════════════
#  ANA PENCERE
# ══════════════════════════════════════════════════════════════════

class AppWindow(QMainWindow):

    def __init__(self, db: Database, oturum: dict | None = None, parent=None):
        super().__init__(parent)
        self._db    = db
        self._oturum = oturum
        self._pages: dict[str, QWidget] = {}
        self.setWindowTitle("REPYS 2.0")
        self.resize(1440, 900)
        self.setMinimumSize(1024, 700)
        self._build()

    def _build(self):
        root = QWidget()
        root.setObjectName("AppRoot")
        root.setStyleSheet(f"background:{T.bg0};")
        self.setCentralWidget(root)

        kok = QVBoxLayout(root)
        kok.setContentsMargins(0, 0, 0, 0)
        kok.setSpacing(0)

        kok.addWidget(_Topbar(root))

        orta = QWidget()
        orta.setStyleSheet("background:transparent;")
        ol = QHBoxLayout(orta)
        ol.setContentsMargins(0, 0, 0, 0)
        ol.setSpacing(0)

        self._sidebar = Sidebar(self._db, oturum=self._oturum, parent=orta)
        self._sidebar.navigasyon.connect(self._goto)
        ol.addWidget(self._sidebar)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background:{T.bg0};")
        ol.addWidget(self._stack, 1)

        kok.addWidget(orta, 1)

    def _goto(self, mod_id: str):
        if mod_id not in self._pages:
            try:
                page = reg.sayfa_olustur(mod_id, self._db, oturum=self._oturum)
            except Exception:
                from ui.pages.placeholder import PlaceholderPage
                page = PlaceholderPage(self._db)
            self._pages[mod_id] = page
            self._stack.addWidget(page)
        self._stack.setCurrentWidget(self._pages[mod_id])
