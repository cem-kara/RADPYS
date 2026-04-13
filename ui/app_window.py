# -*- coding: utf-8 -*-
"""
ui/app_window.py -?" RADPYS 2.0 Ana Pencere.
Tüm ikonlar ui/icons.py üzerinden qtawesome (mdi6) ile gelir.
"""
from __future__ import annotations
from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame,
    QScrollArea,
    QStackedWidget,
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QFont
from ui.styles import DARK, LIGHT, ThemeManager
from ui.styles.icons import Icons, ic, pixmap as ipx
import app.module_registry as reg
from app.db.database import Database


def _tokens() -> dict[str, str]:
    return LIGHT if ThemeManager.current_theme() == "light" else DARK


class _ThemeProxy:
    sidebar_w = 256
    topbar_h = 52

    @property
    def bg0(self) -> str:
        return _tokens()["BG_PRIMARY"]

    @property
    def bg1(self) -> str:
        return _tokens()["BG_SECONDARY"]

    @property
    def bg2(self) -> str:
        return _tokens()["BG_TERTIARY"]

    @property
    def bg3(self) -> str:
        return _tokens()["BG_ELEVATED"]

    @property
    def border(self) -> str:
        return _tokens()["BORDER_PRIMARY"]

    @property
    def border2(self) -> str:
        return _tokens()["BORDER_SECONDARY"]

    @property
    def text(self) -> str:
        return _tokens()["TEXT_PRIMARY"]

    @property
    def text2(self) -> str:
        return _tokens()["TEXT_SECONDARY"]

    @property
    def text3(self) -> str:
        return _tokens()["TEXT_MUTED"]

    @property
    def text4(self) -> str:
        return _tokens()["TEXT_DISABLED"]

    @property
    def accent(self) -> str:
        return _tokens()["ACCENT"]

    @property
    def accent2(self) -> str:
        return _tokens()["ACCENT2"]

    @property
    def teal2(self) -> str:
        return _tokens()["ACCENT2"]

    @property
    def accent_bg(self) -> str:
        return _tokens()["ACCENT_BG"]

    @property
    def overlay_low(self) -> str:
        return _tokens()["OVERLAY_LOW"]

    @property
    def overlay_mid(self) -> str:
        return _tokens()["OVERLAY_MID"]


T = _ThemeProxy()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#  TOPBAR
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class _Topbar(QFrame):
    def __init__(self, oturum: dict | None = None, parent=None):
        super().__init__(parent)
        self._oturum = oturum
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

        # ---- Logo bloşu ----------------------------------------------------------------------------------------
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
        nm = QLabel("RADPYS")
        nm.setStyleSheet(
            f"color:{T.text};font-size:13.5px;font-weight:700;"
            f"letter-spacing:0.04em;"
        )
        sub = QLabel("Radyoloji Personel ve Cihaz Yönetim Sistemi")
        sub.setStyleSheet(f"color:{T.text3};font-size:9px;")
        col.addWidget(nm)
        col.addWidget(sub)
        ll.addLayout(col)
        ll.addStretch()
        lay.addWidget(logo_w)

        lay.addWidget(self._vsep())
        lay.addStretch()

        # ---- Saat ----------------------------------------------------------------------------------------------------
        self._clock = QLabel()
        self._clock.setStyleSheet(
            f"color:{T.text2};font-size:11.5px;"
            f"font-family:'IBM Plex Sans','Source Sans 3','Work Sans','Noto Sans',sans-serif;"
            f"letter-spacing:0.04em;"
        )
        lay.addWidget(self._clock)
        lay.addWidget(self._vsep())

        # ---- Bildirim ikonu --------------------------------------------------------------------------------
        nb = QPushButton()
        nb.setIcon(ic("bildirim", size=20, color=T.text2))
        nb.setIconSize(QSize(20, 20))
        nb.setFixedSize(32, 32)
        nb.setCursor(Qt.CursorShape.PointingHandCursor)
        nb.setToolTip("Bildirimler")
        nb.setStyleSheet(
            f"background:{T.bg2};"
            f"border:1px solid {T.border2};"
            "border-radius:8px;"
        )
        lay.addWidget(nb)
        lay.addWidget(self._vsep())

        # ---- Kullanıcı avatarı --------------------------------------------------------------------------
        from app.rbac import kullanici_avatar
        av = QLabel(kullanici_avatar(self._oturum))
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


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#  SIDEBAR BUTONU
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class _SbBtn(QFrame):
    """Tek sidebar navigasyon butonu -?" QIcon tabanlı."""

    clicked = Signal(str)

    def __init__(self, mod: reg.ModuleDef, parent=None):
        super().__init__(parent)
        self.mod_id = mod.id
        self.setMinimumHeight(42)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 7, 10, 7)
        lay.setSpacing(10)

        # İkon butonu -?" QPushButton ile HiDPI-aware icon
        self._ikon_btn = QPushButton()
        self._ikon_btn.setFixedSize(30, 30)
        self._ikon_btn.setIconSize(QSize(22, 22))
        self._ikon_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._ikon_btn.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._ikon_btn.setStyleSheet(
            f"background:{T.overlay_low};"
            "border:none;"
            "border-radius:10px;"
            "padding:0px;"
        )

        self._txt_lbl = QLabel(mod.label)
        self._txt_lbl.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._txt_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._txt_lbl.setStyleSheet(
            "font-size:12.5px;"
            "background:transparent;"
            "border:none;"
            "outline:none;"
        )

        lay.addWidget(self._ikon_btn)
        lay.addWidget(self._txt_lbl, 1)

        # Badge
        self._badge: QLabel | None = None
        if mod.badge_fn is not None:
            b = QLabel("")
            b.setAlignment(Qt.AlignmentFlag.AlignCenter)
            b.setContentsMargins(6, 0, 6, 0)
            b.setFixedHeight(18)
            b.setStyleSheet(
                f"background:{mod.badge_renk};color:white;"
                f"border-radius:9px;font-size:9px;font-weight:700;"
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
                f"QFrame{{background:{T.accent_bg};"
                f"border:1px solid {T.accent};"
                f"border-radius:12px;margin:3px 6px;}}"
            )
            ikon_bg = T.overlay_mid
            renk = T.text
        else:
            self.setStyleSheet(
                f"QFrame{{background:transparent;"
                f"border:1px solid transparent;"
                f"border-radius:12px;margin:3px 6px;}}"
                f"QFrame:hover{{background:{T.overlay_low};border-color:{T.border};}}"
            )
            ikon_bg = "transparent"
            renk = T.text2

        # İkonu yeni renkle güncelle
        self._ikon_btn.setIcon(ic(self._mod_icon, size=22, color=renk))
        self._ikon_btn.setStyleSheet(
            f"background:{ikon_bg};"
            "border:none;"
            "border-radius:10px;"
            "padding:0px;"
        )
        self._txt_lbl.setStyleSheet(
            f"font-size:12.5px;"
            f"font-weight:600;"
            f"color:{renk};"
            "background:transparent;"
            "border:none;"
            "outline:none;"
        )

    def set_aktif(self, aktif: bool):
        self._uygula_stil(aktif)

    def set_badge(self, txt: str):
        if self._badge:
            self._badge.setText(txt)
            self._badge.setVisible(bool(txt))

    def mousePressEvent(self, _):
        self.clicked.emit(self.mod_id)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#  SIDEBAR
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
            f"QFrame{{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            f"stop:0 {T.bg1},stop:1 {T.bg2});"
            f"border-right:1px solid {T.border};}}"
        )

        kok = QVBoxLayout(self)
        kok.setContentsMargins(8, 10, 8, 10)
        kok.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea{background:transparent;border:none;}"
            "QScrollBar:vertical{background:transparent;width:6px;margin:2px 0 2px 0;}"
            f"QScrollBar::handle:vertical{{background:{T.border2};border-radius:3px;min-height:28px;}}"
            "QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0px;}"
        )

        ic_w = QWidget()
        ic_w.setStyleSheet("background:transparent;")
        ic_lay = QVBoxLayout(ic_w)
        ic_lay.setContentsMargins(2, 2, 2, 2)
        ic_lay.setSpacing(4)

        from app.rbac import modul_gorunur_mu
        for bolum, modlar in reg.get_bolumler():
            gorunen_modlar = [m for m in modlar if modul_gorunur_mu(oturum, m.id)]
            if not gorunen_modlar:
                continue
            # Bölüm başlışı
            blbl = QLabel(bolum.label.upper())
            blbl.setContentsMargins(14, 12, 0, 4)
            blbl.setStyleSheet(
                f"color:{T.text3};font-size:9.5px;font-weight:700;"
                f"letter-spacing:0.16em;"
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
                f"background:{T.overlay_low};margin:6px 12px;"
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
            f"QFrame{{border:1px solid {T.border};"
            f"background:{T.overlay_low};border-radius:12px;}}"
            f"QFrame:hover{{background:{T.overlay_mid};border-color:{T.border2};}}"
        )
        ft.setCursor(Qt.CursorShape.PointingHandCursor)
        fl = QHBoxLayout(ft)
        fl.setContentsMargins(10, 9, 10, 9)
        fl.setSpacing(9)

        # Kullanıcı ikon etiketi
        ikon_lbl = QLabel()
        ikon_lbl.setFixedSize(30, 30)
        ikon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ikon_lbl.setPixmap(ipx("kullanici", size=22, color=T.accent2))
        ikon_lbl.setStyleSheet(
            f"background:{T.accent_bg};"
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

        more_lbl = QLabel()
        more_lbl.setFixedSize(16, 16)
        more_lbl.setPixmap(ipx("ayarlar", size=16, color=T.text3))
        more_lbl.setStyleSheet("background:transparent;")
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


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#  ANA PENCERE
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class AppWindow(QMainWindow):

    def __init__(self, db: Database, oturum: dict | None = None, parent=None):
        super().__init__(parent)
        self._db    = db
        self._oturum = oturum
        self._pages: dict[str, QWidget] = {}
        self._active_mod_id: str = ""
        self.setWindowTitle("RADPYS 2.0")
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

        kok.addWidget(_Topbar(oturum=self._oturum, parent=root))

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
        self._active_mod_id = mod_id
        if mod_id not in self._pages:
            try:
                page = reg.sayfa_olustur(mod_id, self._db, oturum=self._oturum)
            except Exception:
                from ui.pages.placeholder import PlaceholderPage
                page = PlaceholderPage(self._db)
            self._pages[mod_id] = page
            self._stack.addWidget(page)
        self._stack.setCurrentWidget(self._pages[mod_id])

    def open_mdi_child(self, key: str, widget: QWidget, title: str):
        eski = self._pages.get(key)
        if eski is not None and eski is not widget:
            self._stack.removeWidget(eski)
            eski.deleteLater()

        self._pages[key] = widget
        if self._stack.indexOf(widget) < 0:
            self._stack.addWidget(widget)
        self._stack.setCurrentWidget(widget)
        self.setWindowTitle(f"RADPYS 2.0 - {title}")
        return widget

    def close_mdi_child(self, key: str) -> None:
        sayfa = self._pages.pop(key, None)
        if sayfa is None:
            return

        self._stack.removeWidget(sayfa)
        sayfa.deleteLater()

        if self._active_mod_id and self._active_mod_id in self._pages:
            self._stack.setCurrentWidget(self._pages[self._active_mod_id])
            return

        if self._pages:
            self._stack.setCurrentWidget(next(iter(self._pages.values())))


