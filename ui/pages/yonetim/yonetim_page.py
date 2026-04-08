# -*- coding: utf-8 -*-
"""ui/pages/yonetim/yonetim_page.py ï¿½?" RBAC merkezi yÃ¶netim sayfasÄ±"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox,
    QTabWidget, QFrame, QGridLayout, QCheckBox,
)

from app.db.database import Database
from app.exceptions import AppHatasi
import app.rbac as rbac
from app.services.auth_service import AuthService
from app.services.policy_service import PolicyService
from ui.components import (
    AlertBar, Card, DataTable,
    GhostButton, PrimaryButton, StatCard,
)
from ui.styles import T


# ï¿½"?ï¿½"? ModÃ¼l etiketleri ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?
_MODUL_ETIKET: dict[str, str] = {
    "dashboard":       "Dashboard",
    "personel":        "Personel",
    "izin":            "Ä°zin Takip",
    "saglik":          "Saï¿½YlÄ±k",
    "dozimetre":       "Dozimetre",
    "cihaz":           "Cihaz",
    "ariza":           "ArÄ±za",
    "bakim":           "BakÄ±m",
    "rke":             "RKE",
    "nobet":           "NÃ¶bet",
    "mesai":           "Mesai",
    "dokumanlar":      "DÃ¶kÃ¼manlar",
    "kullanici_giris": "KullanÄ±cÄ± YÃ¶netimi",
    "rapor":           "Raporlar",
    "ayarlar":         "YÃ¶netim",
}
_TUM_MODULLER = list(_MODUL_ETIKET.keys())


class YonetimPage(QWidget):
    """KullanÄ±cÄ± ve rol tabanlÄ± eriï¿½Yim yÃ¶netimi iÃ§in merkezi sayfa."""

    def __init__(self, db: Database, oturum: dict | None = None, parent=None):
        super().__init__(parent)
        self._svc        = AuthService(db)
        self._policy_svc = PolicyService(db)
        self._db         = db
        self._oturum     = oturum
        self._secili_id: str | None = None
        self._cb_moduller: dict[str, QCheckBox] = {}

        self.setStyleSheet(f"background:{T.bg0};")
        self._build()
        self._liste_yukle()

    # ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½
    #  Ä°SKELET
    # ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 16, 24, 16)
        lay.setSpacing(14)

        self._alert = AlertBar(self)
        lay.addWidget(self._alert)
        lay.addWidget(self._baslik_satiri())
        lay.addWidget(self._stat_satiri())
        lay.addWidget(self._tab_widget(), 1)

    # ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?
    #  BAÅLIK & Ä°STATÄ°STÄ°K
    # ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?

    def _baslik_satiri(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)

        baslik = QLabel("YÃ¶netim Merkezi")
        baslik.setStyleSheet(
            f"color:{T.text}; font-size:20px; font-weight:700;"
        )
        alt = QLabel("KullanÄ±cÄ±lar ve rol tabanlÄ± eriï¿½Yim izinlerini yÃ¶netin")
        alt.setStyleSheet(f"color:{T.text2}; font-size:12px;")

        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(baslik)
        col.addWidget(alt)
        lay.addLayout(col)
        lay.addStretch(1)
        return w

    def _stat_satiri(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        self._stat_toplam     = StatCard("Toplam KullanÄ±cÄ±")
        self._stat_aktif      = StatCard("Aktif")
        self._stat_pasif      = StatCard("Pasif")
        self._stat_oturum_rol = StatCard("Oturum RolÃ¼")
        self._stat_oturum_rol.set(
            (self._oturum or {}).get("rol", "ï¿½?""), T.purple
        )

        lay.addWidget(self._stat_toplam, 1)
        lay.addWidget(self._stat_aktif, 1)
        lay.addWidget(self._stat_pasif, 1)
        lay.addWidget(self._stat_oturum_rol, 1)
        return w

    # ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?
    #  SEKME WIDGET
    # ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?

    def _tab_widget(self) -> QTabWidget:
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
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
                padding: 8px 22px;
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
        """)
        tabs.addTab(self._sekme_kullanicilar(),   "KullanÄ±cÄ±lar")
        tabs.addTab(self._sekme_modul_izinleri(), "ModÃ¼l Ä°zinleri")
        tabs.addTab(self._sekme_yetki_ozeti(),    "Yetki ï¿½-zeti")
        return tabs

    # ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?
    #  SEKME 1 ï¿½?" KULLANICILAR
    # ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?

    def _sekme_kullanicilar(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{T.bg1};")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(16)
        lay.addWidget(self._yeni_kullanici_formu(), 0)
        lay.addWidget(self._kullanici_listesi(), 1)
        return w

    def _yeni_kullanici_formu(self) -> Card:
        kart = Card(self)
        kart.setFixedWidth(280)
        kl = kart.layout_

        baslik = QLabel("Yeni KullanÄ±cÄ±")
        baslik.setStyleSheet(
            f"color:{T.text}; font-size:14px; font-weight:700;"
        )
        aciklama = QLabel("Sisteme yeni bir kullanÄ±cÄ± hesabÄ± ekleyin.")
        aciklama.setWordWrap(True)
        aciklama.setStyleSheet(f"color:{T.text2}; font-size:11px;")
        kl.addWidget(baslik)
        kl.addWidget(aciklama)
        kl.addWidget(self._ayrac())

        lbl_ad = QLabel("KullanÄ±cÄ± AdÄ±")
        lbl_ad.setStyleSheet(
            f"color:{T.text2}; font-size:11px; font-weight:600;"
        )
        self._inp_ad = QLineEdit()
        self._inp_ad.setPlaceholderText("KullanÄ±cÄ± adÄ± girinï¿½?ï¿½")
        self._inp_ad.setMinimumHeight(34)
        kl.addWidget(lbl_ad)
        kl.addWidget(self._inp_ad)

        lbl_par = QLabel("Parola")
        lbl_par.setStyleSheet(
            f"color:{T.text2}; font-size:11px; font-weight:600;"
        )
        self._inp_parola = QLineEdit()
        self._inp_parola.setPlaceholderText("En az 6 karakterï¿½?ï¿½")
        self._inp_parola.setEchoMode(QLineEdit.EchoMode.Password)
        self._inp_parola.setMinimumHeight(34)
        kl.addWidget(lbl_par)
        kl.addWidget(self._inp_parola)

        lbl_rol = QLabel("Rol")
        lbl_rol.setStyleSheet(
            f"color:{T.text2}; font-size:11px; font-weight:600;"
        )
        self._cb_yeni_rol = QComboBox()
        self._cb_yeni_rol.addItem("KullanÄ±cÄ±", "kullanici")
        self._cb_yeni_rol.addItem("YÃ¶netici",  "yonetici")
        self._cb_yeni_rol.addItem("Admin",     "admin")
        self._cb_yeni_rol.setMinimumHeight(34)
        kl.addWidget(lbl_rol)
        kl.addWidget(self._cb_yeni_rol)

        kl.addWidget(self._ayrac())
        self._btn_ekle = PrimaryButton("KullanÄ±cÄ± Ekle")
        self._btn_ekle.clicked.connect(self._kullanici_ekle)
        kl.addWidget(self._btn_ekle)
        kl.addStretch(1)
        return kart

    def _kullanici_listesi(self) -> Card:
        kart = Card(self)
        kl = kart.layout_

        baslik = QLabel("Mevcut KullanÄ±cÄ±lar")
        baslik.setStyleSheet(
            f"color:{T.text}; font-size:14px; font-weight:700;"
        )
        aciklama = QLabel(
            "Bir kullanÄ±cÄ±ya tÄ±klayarak seÃ§in, ardÄ±ndan aï¿½Yaï¿½YÄ±daki iï¿½Ylemleri kullanÄ±n."
        )
        aciklama.setWordWrap(True)
        aciklama.setStyleSheet(f"color:{T.text2}; font-size:11px;")
        kl.addWidget(baslik)
        kl.addWidget(aciklama)
        kl.addWidget(self._ayrac())

        self._tablo = DataTable(self)
        self._tablo.kur_kolonlar([
            ("ad",        "KullanÄ±cÄ± AdÄ±", 180),
            ("rol",       "Rol",           110),
            ("aktif_txt", "Durum",          80),
            ("son_giris", "Son Giriï¿½Y",     170),
            ("id",        "ID",              0),
        ], geren="id")
        self._tablo.clicked.connect(self._satir_secildi)
        kl.addWidget(self._tablo, 1)

        kl.addWidget(self._ayrac())
        aksiyon_lbl = QLabel("SeÃ§ili KullanÄ±cÄ± Ä°ï¿½Ylemleri")
        aksiyon_lbl.setStyleSheet(
            f"color:{T.text2}; font-size:11px; font-weight:600;"
        )
        kl.addWidget(aksiyon_lbl)

        alt = QHBoxLayout()
        alt.setSpacing(8)

        rol_lbl = QLabel("Yeni Rol:")
        rol_lbl.setStyleSheet(f"color:{T.text2}; font-size:11px;")

        self._cb_secili_rol = QComboBox()
        self._cb_secili_rol.addItem("KullanÄ±cÄ±", "kullanici")
        self._cb_secili_rol.addItem("YÃ¶netici",  "yonetici")
        self._cb_secili_rol.addItem("Admin",     "admin")
        self._cb_secili_rol.setMinimumHeight(32)
        self._cb_secili_rol.setFixedWidth(130)

        self._btn_rol_guncelle = PrimaryButton("RolÃ¼ GÃ¼ncelle")
        self._btn_rol_guncelle.clicked.connect(self._secili_rol_guncelle)

        self._btn_aktif_pasif = GhostButton("Aktif / Pasif Deï¿½Yiï¿½Ytir")
        self._btn_aktif_pasif.clicked.connect(self._aktif_pasif_degistir)

        alt.addWidget(rol_lbl)
        alt.addWidget(self._cb_secili_rol)
        alt.addWidget(self._btn_rol_guncelle)
        alt.addWidget(self._btn_aktif_pasif)
        alt.addStretch(1)
        kl.addLayout(alt)
        return kart

    # ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?
    #  SEKME 2 ï¿½?" MODï¿½oL Ä°ZÄ°NLERÄ°
    # ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?

    def _sekme_modul_izinleri(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{T.bg1};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        bilgi = QLabel(
            "Her rol iÃ§in hangi modÃ¼llerin gÃ¶rÃ¼neceï¿½Yini buradan belirleyin. "
            "Admin rolÃ¼nÃ¼n izinleri deï¿½Yiï¿½Ytirilemez ï¿½?" her zaman tÃ¼m modÃ¼llere eriï¿½Yir. "
            "Kaydedilen deï¿½Yiï¿½Yiklikler hemen belleï¿½Ye alÄ±nÄ±r."
        )
        bilgi.setWordWrap(True)
        bilgi.setStyleSheet(
            f"color:{T.text2}; font-size:11px; padding:8px 12px;"
            f"background:{T.bg4}; border-radius:{T.radius_sm}px;"
            f"border-left:3px solid {T.accent};"
        )
        lay.addWidget(bilgi)

        kart = Card(self)
        kl = kart.layout_

        ust = QHBoxLayout()
        lbl_rol = QLabel("DÃ¼zenlenecek Rol:")
        lbl_rol.setStyleSheet(
            f"color:{T.text}; font-size:13px; font-weight:700;"
        )
        self._cb_izin_rol = QComboBox()
        self._cb_izin_rol.addItem("YÃ¶netici",  "yonetici")
        self._cb_izin_rol.addItem("KullanÄ±cÄ±", "kullanici")
        self._cb_izin_rol.setMinimumHeight(34)
        self._cb_izin_rol.setFixedWidth(160)
        self._cb_izin_rol.currentIndexChanged.connect(self._izin_rol_degisti)

        self._btn_izin_kaydet = PrimaryButton("Deï¿½Yiï¿½Yiklikleri Kaydet")
        self._btn_izin_kaydet.clicked.connect(self._modul_izinleri_kaydet)

        ust.addWidget(lbl_rol)
        ust.addWidget(self._cb_izin_rol)
        ust.addStretch(1)
        ust.addWidget(self._btn_izin_kaydet)
        kl.addLayout(ust)
        kl.addWidget(self._ayrac())

        # Checkbox Ä±zgarasÄ± ï¿½?" 5 sÃ¼tun
        grid_w = QWidget()
        grid_w.setStyleSheet("background:transparent;")
        grid = QGridLayout(grid_w)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(8)

        SUTUN = 5
        for idx, modul_id in enumerate(_TUM_MODULLER):
            satir, sutun = divmod(idx, SUTUN)
            etiket = _MODUL_ETIKET.get(modul_id, modul_id)

            cb_kap = QWidget()
            cb_kap.setStyleSheet(
                f"background:{T.bg4}; border-radius:{T.radius_sm}px;"
            )
            cb_kap_lay = QHBoxLayout(cb_kap)
            cb_kap_lay.setContentsMargins(10, 8, 10, 8)

            cb = QCheckBox(etiket)
            cb.setStyleSheet(
                f"QCheckBox {{ color:{T.text}; font-size:11.5px; "
                f"spacing:6px; background:transparent; }}"
                f"QCheckBox::indicator {{ width:16px; height:16px; "
                f"border:2px solid {T.border2}; border-radius:3px; "
                f"background:{T.bg3}; }}"
                f"QCheckBox::indicator:checked {{ "
                f"background:{T.accent}; border-color:{T.accent}; }}"
                f"QCheckBox::indicator:hover {{ border-color:{T.accent2}; }}"
            )
            cb_kap_lay.addWidget(cb)
            self._cb_moduller[modul_id] = cb
            grid.addWidget(cb_kap, satir, sutun)

        kl.addWidget(grid_w)
        lay.addWidget(kart, 1)

        self._izin_yukle(self._cb_izin_rol.currentData() or "yonetici")
        return w

    # ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?
    #  SEKME 3 ï¿½?" YETKÄ° ï¿½-ZETÄ°
    # ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?

    def _sekme_yetki_ozeti(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"background:{T.bg1};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        baslik = QLabel("Rol & Yetki Matrisi  (Salt Okunur)")
        baslik.setStyleSheet(
            f"color:{T.text}; font-size:14px; font-weight:700;"
        )
        lay.addWidget(baslik)

        mod_lbl = QLabel("ModÃ¼l Eriï¿½Yim Ä°zinleri")
        mod_lbl.setStyleSheet(
            f"color:{T.text2}; font-size:11.5px; font-weight:600; margin-top:4px;"
        )
        lay.addWidget(mod_lbl)

        self._tbl_moduller = DataTable(self)
        self._tbl_moduller.kur_kolonlar([
            ("rol",      "Rol",                  100),
            ("moduller", "GÃ¶rebileceï¿½Yi ModÃ¼ller",   0),
        ], geren="moduller")
        lay.addWidget(self._tbl_moduller, 2)

        ey_lbl = QLabel("Form / Eylem Yetkileri")
        ey_lbl.setStyleSheet(
            f"color:{T.text2}; font-size:11.5px; font-weight:600; margin-top:8px;"
        )
        lay.addWidget(ey_lbl)

        self._tbl_eylemler = DataTable(self)
        self._tbl_eylemler.kur_kolonlar([
            ("rol",      "Rol",       100),
            ("eylemler", "Yetkiler",    0),
        ], geren="eylemler")
        lay.addWidget(self._tbl_eylemler, 1)

        self._ozet_yukle()
        return w

    # ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?
    #  YARDIMCI
    # ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?

    @staticmethod
    def _ayrac() -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setFixedHeight(1)
        f.setStyleSheet(f"background:{T.border}; margin:4px 0;")
        return f

    def _yetki_uygula(self) -> None:
        olustur  = rbac.yetki_var_mi(self._oturum, "kullanici.olustur")
        guncelle = rbac.yetki_var_mi(self._oturum, "kullanici.guncelle")
        pasife   = rbac.yetki_var_mi(self._oturum, "kullanici.pasife_al")

        self._btn_ekle.setEnabled(olustur)
        self._btn_rol_guncelle.setEnabled(guncelle)
        self._btn_aktif_pasif.setEnabled(pasife)
        self._btn_izin_kaydet.setEnabled(guncelle)

    def _ozet_yukle(self) -> None:
        mod_rows = []
        for r, moduller in rbac.rol_modul_haritasi().items():
            if moduller is None:
                txt = "TÃ¼m modÃ¼ller"
            else:
                txt = " Â· ".join(
                    _MODUL_ETIKET.get(m, m) for m in sorted(moduller)
                )
            mod_rows.append({"rol": r, "moduller": txt})
        self._tbl_moduller.set_veri(mod_rows)

        eylem_rows = []
        for r, eylemler in rbac.rol_eylem_haritasi().items():
            txt = " Â· ".join(sorted(eylemler)) if eylemler else "ï¿½?""
            eylem_rows.append({"rol": r, "eylemler": txt})
        self._tbl_eylemler.set_veri(eylem_rows)

    def _izin_yukle(self, rol_adi: str) -> None:
        try:
            izinler = self._policy_svc.modul_seti_getir(rol_adi)
        except Exception:
            izinler = None
        if izinler is None:
            hardcoded = rbac.rol_modul_haritasi().get(rol_adi)
            izinler = (
                set(_TUM_MODULLER) if hardcoded is None
                else (hardcoded or set())
            )
        for modul_id, cb in self._cb_moduller.items():
            cb.setChecked(modul_id in izinler)

    def _liste_yukle(self) -> None:
        self._alert.temizle()
        try:
            rows = self._svc.kullanici_listele(self._oturum)
        except AppHatasi as e:
            self._tablo.set_veri([])
            self._alert.goster(str(e), "warning")
            self._yetki_uygula()
            return

        for r in rows:
            r["aktif_txt"] = "Aktif" if int(r.get("aktif", 0)) else "Pasif"
        self._tablo.set_veri(rows)

        toplam = len(rows)
        aktif  = sum(1 for r in rows if int(r.get("aktif", 0)))
        pasif  = toplam - aktif
        self._stat_toplam.set(str(toplam), T.accent)
        self._stat_aktif.set(str(aktif),   T.green2)
        self._stat_pasif.set(str(pasif),   T.red if pasif else T.text2)
        self._yetki_uygula()

    # ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?
    #  Ä°ÅLEMLER
    # ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?

    def _izin_rol_degisti(self, _idx: int) -> None:
        self._izin_yukle(self._cb_izin_rol.currentData() or "yonetici")

    def _modul_izinleri_kaydet(self) -> None:
        self._alert.temizle()
        rol_adi = self._cb_izin_rol.currentData() or "yonetici"
        aktif_moduller = {
            mid for mid, cb in self._cb_moduller.items() if cb.isChecked()
        }
        try:
            self._policy_svc.rol_modullerini_kaydet(
                self._oturum, rol_adi, aktif_moduller
            )
            rbac.init_dari_db(self._db)  # Bellek iÃ§i policy yenile
            self._ozet_yukle()
            self._alert.goster(
                f"'{rol_adi}' rolÃ¼nÃ¼n modÃ¼l izinleri kaydedildi. "
                "MenÃ¼ filtrelemesi gÃ¼ncellendi.",
                "success",
            )
        except AppHatasi as e:
            self._alert.goster(str(e), "warning")

    def _satir_secildi(self, _index) -> None:
        satir = self._tablo.secili_satir()
        if not satir:
            self._secili_id = None
            return
        self._secili_id = satir.get("id")
        idx = self._cb_secili_rol.findData(satir.get("rol"))
        if idx >= 0:
            self._cb_secili_rol.setCurrentIndex(idx)

    def _kullanici_ekle(self) -> None:
        self._alert.temizle()
        try:
            self._svc.kullanici_ekle(self._oturum, {
                "ad":     self._inp_ad.text(),
                "parola": self._inp_parola.text(),
                "rol":    self._cb_yeni_rol.currentData(),
            })
            self._inp_ad.clear()
            self._inp_parola.clear()
            self._liste_yukle()
            self._alert.goster("KullanÄ±cÄ± baï¿½YarÄ±yla eklendi.", "success")
        except AppHatasi as e:
            self._alert.goster(str(e), "warning")

    def _secili_rol_guncelle(self) -> None:
        self._alert.temizle()
        if not self._secili_id:
            self._alert.goster("LÃ¼tfen tablodan bir kullanÄ±cÄ± seÃ§in.", "warning")
            return
        try:
            self._svc.kullanici_rol_guncelle(
                self._oturum,
                self._secili_id,
                self._cb_secili_rol.currentData(),
            )
            self._liste_yukle()
            self._alert.goster("KullanÄ±cÄ± rolÃ¼ gÃ¼ncellendi.", "success")
        except AppHatasi as e:
            self._alert.goster(str(e), "warning")

    def _aktif_pasif_degistir(self) -> None:
        self._alert.temizle()
        satir = self._tablo.secili_satir()
        if not satir or not self._secili_id:
            self._alert.goster("LÃ¼tfen tablodan bir kullanÄ±cÄ± seÃ§in.", "warning")
            return
        try:
            if int(satir.get("aktif", 0)):
                self._svc.kullanici_pasife_al(self._oturum, self._secili_id)
                self._alert.goster("KullanÄ±cÄ± pasife alÄ±ndÄ±.", "warning")
            else:
                self._svc.kullanici_aktif_et(self._oturum, self._secili_id)
                self._alert.goster("KullanÄ±cÄ± aktif edildi.", "success")
            self._liste_yukle()
        except AppHatasi as e:
            self._alert.goster(str(e), "warning")


