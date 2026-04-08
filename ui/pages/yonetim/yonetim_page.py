# -*- coding: utf-8 -*-
"""ui/pages/yonetim/yonetim_page.py - RBAC merkezi yonetim sayfasi."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

import app.rbac as rbac
from app.db.database import Database
from app.exceptions import AppHatasi
from app.logger import exc_logla
from app.services.auth_service import AuthService
from app.services.policy_service import PolicyService
from ui.components import AlertBar, Card, DataTable, GhostButton, PrimaryButton, StatCard
from ui.styles import T


_MODUL_ETIKET = {
    "dashboard": "Dashboard",
    "personel": "Personel",
    "izin": "Izin Takip",
    "saglik": "Saglik",
    "dozimetre": "Dozimetre",
    "cihaz": "Cihaz",
    "ariza": "Ariza",
    "bakim": "Bakim",
    "rke": "RKE",
    "nobet": "Nobet",
    "mesai": "Mesai",
    "dokumanlar": "Dokumanlar",
    "kullanici_giris": "Kullanici Yonetimi",
    "rapor": "Raporlar",
    "ayarlar": "Yonetim",
}

_ROL_ETIKET = {
    "admin": "Admin",
    "yonetici": "Yonetici",
    "kullanici": "Kullanici",
}

_EYLEM_ETIKET = {
    "personel.ekle": "Personel ekleme",
    "personel.guncelle": "Personel guncelleme",
    "personel.pasife_al": "Personel pasife alma",
    "kullanici.goruntule": "Kullanici listeleme",
    "kullanici.olustur": "Kullanici olusturma",
    "kullanici.guncelle": "Kullanici guncelleme",
    "kullanici.pasife_al": "Kullanici aktif/pasif",
}

_TUM_MODULLER = list(_MODUL_ETIKET.keys())
_TUM_EYLEMLER = sorted(_EYLEM_ETIKET.keys())


class YonetimPage(QWidget):
    """Kullanicilar ve rol tabanli erisim izinleri icin merkezi sayfa."""

    def __init__(self, db: Database, oturum: dict | None = None, parent=None):
        super().__init__(parent)
        self._db = db
        self._oturum = oturum
        self._svc = AuthService(db)
        self._policy_svc = PolicyService(db)
        self._secili_id: str | None = None
        self._cb_moduller: dict[str, QCheckBox] = {}
        self._cb_eylemler: dict[str, QCheckBox] = {}
        self._roller: list[str] = self._rolleri_yukle()

        self.setStyleSheet(f"background:{T.bg0};")
        self._build()
        self._rol_formlarini_yenile()
        self._liste_yukle()
        self._ozet_yukle()
        self._izin_yukle(self._cb_izin_rol.currentData() or "kullanici")
        self._eylem_formunu_yukle(self._cb_eylem_rol.currentData() or "admin")

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 16, 24, 16)
        lay.setSpacing(14)

        self._alert = AlertBar(self)
        lay.addWidget(self._alert)
        lay.addWidget(self._baslik_satiri())
        lay.addWidget(self._istatistik_satiri())
        lay.addWidget(self._tab_widget(), 1)

    def _baslik_satiri(self) -> QWidget:
        w = QWidget(self)
        w.setStyleSheet("background:transparent;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        col = QVBoxLayout()
        col.setSpacing(2)

        baslik = QLabel("Yonetim Merkezi")
        baslik.setStyleSheet(f"color:{T.text}; font-size:20px; font-weight:700;")
        alt = QLabel("Kullanici hesaplari ve RBAC ayarlari bu ekrandan yonetilir.")
        alt.setStyleSheet(f"color:{T.text2}; font-size:12px;")

        col.addWidget(baslik)
        col.addWidget(alt)
        lay.addLayout(col)
        lay.addStretch(1)
        return w

    def _istatistik_satiri(self) -> QWidget:
        w = QWidget(self)
        w.setStyleSheet("background:transparent;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        self._stat_toplam = StatCard("Toplam Kullanici")
        self._stat_aktif = StatCard("Aktif")
        self._stat_pasif = StatCard("Pasif")
        self._stat_oturum = StatCard("Oturum Rolu")
        self._stat_oturum.set(_ROL_ETIKET.get((self._oturum or {}).get("rol", ""), "-"), T.purple)

        lay.addWidget(self._stat_toplam, 1)
        lay.addWidget(self._stat_aktif, 1)
        lay.addWidget(self._stat_pasif, 1)
        lay.addWidget(self._stat_oturum, 1)
        return w

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
        tabs.addTab(self._sekme_kullanicilar(), "Kullanicilar")
        tabs.addTab(self._sekme_modul_izinleri(), "Modul Izinleri")
        tabs.addTab(self._sekme_eylem_yetkileri(), "Eylem Yetkileri")
        tabs.addTab(self._sekme_yetki_ozeti(), "Yetki Ozeti")
        return tabs

    def _sekme_kullanicilar(self) -> QWidget:
        w = QWidget(self)
        w.setStyleSheet(f"background:{T.bg1};")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(16)
        lay.addWidget(self._yeni_kullanici_formu(), 0)
        lay.addWidget(self._kullanici_listesi(), 1)
        return w

    def _yeni_kullanici_formu(self) -> Card:
        kart = Card(self)
        kart.setFixedWidth(300)
        kl = kart.layout_

        baslik = QLabel("Yeni Kullanici")
        baslik.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        aciklama = QLabel(
            "Olusturulan kullanici ilk giriste sifresini degistirmek zorundadir."
        )
        aciklama.setWordWrap(True)
        aciklama.setStyleSheet(f"color:{T.text2}; font-size:11px;")
        kl.addWidget(baslik)
        kl.addWidget(aciklama)
        kl.addWidget(self._ayrac())

        kl.addWidget(self._alan_etiketi("Kullanici Adi"))
        self._inp_ad = QLineEdit(self)
        self._inp_ad.setPlaceholderText("kullanici.adi")
        self._inp_ad.setMinimumHeight(34)
        kl.addWidget(self._inp_ad)

        kl.addWidget(self._alan_etiketi("Gecici Parola"))
        self._inp_parola = QLineEdit(self)
        self._inp_parola.setPlaceholderText("En az 6 karakter")
        self._inp_parola.setEchoMode(QLineEdit.EchoMode.Password)
        self._inp_parola.setMinimumHeight(34)
        kl.addWidget(self._inp_parola)

        kl.addWidget(self._alan_etiketi("Rol"))
        self._cb_yeni_rol = QComboBox(self)
        self._cb_yeni_rol.setMinimumHeight(34)
        kl.addWidget(self._cb_yeni_rol)

        kl.addWidget(self._ayrac())
        self._btn_ekle = PrimaryButton("Kullanici Ekle")
        self._btn_ekle.clicked.connect(self._kullanici_ekle)
        kl.addWidget(self._btn_ekle)
        kl.addStretch(1)
        return kart

    def _kullanici_listesi(self) -> Card:
        kart = Card(self)
        kl = kart.layout_

        baslik = QLabel("Mevcut Kullanici Listesi")
        baslik.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        aciklama = QLabel(
            "Satir secip rol guncelleyebilir, kullaniciyi aktif veya pasif yapabilirsiniz."
        )
        aciklama.setWordWrap(True)
        aciklama.setStyleSheet(f"color:{T.text2}; font-size:11px;")
        kl.addWidget(baslik)
        kl.addWidget(aciklama)
        kl.addWidget(self._ayrac())

        self._tablo = DataTable(self)
        self._tablo.kur_kolonlar(
            [
                ("ad", "Kullanici", 180),
                ("rol_txt", "Rol", 110),
                ("aktif_txt", "Durum", 80),
                ("sifre_txt", "Ilk Giris", 90),
                ("son_giris", "Son Giris", 170),
                ("id", "ID", 0),
            ],
            geren="id",
        )
        self._tablo.clicked.connect(self._satir_secildi)
        kl.addWidget(self._tablo, 1)

        kl.addWidget(self._ayrac())
        alt = QHBoxLayout()
        alt.setSpacing(8)

        rol_lbl = QLabel("Yeni Rol:")
        rol_lbl.setStyleSheet(f"color:{T.text2}; font-size:11px;")
        alt.addWidget(rol_lbl)

        self._cb_secili_rol = QComboBox(self)
        self._cb_secili_rol.setMinimumHeight(32)
        self._cb_secili_rol.setFixedWidth(140)
        alt.addWidget(self._cb_secili_rol)

        self._btn_rol_guncelle = PrimaryButton("Rolu Guncelle")
        self._btn_rol_guncelle.clicked.connect(self._secili_rol_guncelle)
        alt.addWidget(self._btn_rol_guncelle)

        self._btn_aktif_pasif = GhostButton("Aktif / Pasif")
        self._btn_aktif_pasif.clicked.connect(self._aktif_pasif_degistir)
        alt.addWidget(self._btn_aktif_pasif)

        alt.addStretch(1)
        kl.addLayout(alt)
        return kart

    def _sekme_modul_izinleri(self) -> QWidget:
        w = QWidget(self)
        w.setStyleSheet(f"background:{T.bg1};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        lay.addWidget(self._bilgi_bandi(
            "Her rol icin menude gorunecek modulleri buradan yonetebilirsiniz. "
            "Admin rolu her zaman tum modullere sahiptir."
        ))

        kart = Card(self)
        kl = kart.layout_

        ust = QHBoxLayout()
        ust.setSpacing(8)

        lbl_rol = QLabel("Duzenlenecek Rol:")
        lbl_rol.setStyleSheet(f"color:{T.text}; font-size:13px; font-weight:700;")
        ust.addWidget(lbl_rol)

        self._cb_izin_rol = QComboBox(self)
        self._cb_izin_rol.setMinimumHeight(34)
        self._cb_izin_rol.setFixedWidth(160)
        self._cb_izin_rol.currentIndexChanged.connect(self._izin_rol_degisti)
        ust.addWidget(self._cb_izin_rol)

        self._inp_rol_adi = QLineEdit(self)
        self._inp_rol_adi.setPlaceholderText("Yeni rol adi")
        self._inp_rol_adi.setMinimumHeight(34)
        self._inp_rol_adi.setFixedWidth(170)
        ust.addWidget(self._inp_rol_adi)

        self._cb_rol_kopya = QComboBox(self)
        self._cb_rol_kopya.setMinimumHeight(34)
        self._cb_rol_kopya.setFixedWidth(160)
        ust.addWidget(self._cb_rol_kopya)

        self._btn_rol_ekle = PrimaryButton("Rol Ekle")
        self._btn_rol_ekle.clicked.connect(self._rol_ekle)
        ust.addWidget(self._btn_rol_ekle)

        self._btn_modul_tumu = GhostButton("Tumunu Sec")
        self._btn_modul_tumu.clicked.connect(self._tum_modulleri_sec)
        ust.addWidget(self._btn_modul_tumu)

        self._btn_modul_temizle = GhostButton("Temizle")
        self._btn_modul_temizle.clicked.connect(self._tum_modulleri_temizle)
        ust.addWidget(self._btn_modul_temizle)

        ust.addStretch(1)

        self._btn_izin_kaydet = PrimaryButton("Degisiklikleri Kaydet")
        self._btn_izin_kaydet.clicked.connect(self._modul_izinleri_kaydet)
        ust.addWidget(self._btn_izin_kaydet)

        kl.addLayout(ust)
        kl.addWidget(self._ayrac())
        kl.addWidget(self._modul_checkbox_grid())
        lay.addWidget(kart, 1)
        return w

    def _sekme_eylem_yetkileri(self) -> QWidget:
        w = QWidget(self)
        w.setStyleSheet(f"background:{T.bg1};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        lay.addWidget(self._bilgi_bandi(
            "Bu form eylem yetkileri icin hazirlandi. Mevcut yapida eylem izinleri "
            "config tabanlidir; bu ekran su an salt okunur bir planlama formu olarak calisir."
        ))

        kart = Card(self)
        kl = kart.layout_

        ust = QHBoxLayout()
        ust.setSpacing(8)
        lbl_rol = QLabel("Rol:")
        lbl_rol.setStyleSheet(f"color:{T.text}; font-size:13px; font-weight:700;")
        ust.addWidget(lbl_rol)

        self._cb_eylem_rol = QComboBox(self)
        self._cb_eylem_rol.setMinimumHeight(34)
        self._cb_eylem_rol.setFixedWidth(160)
        self._cb_eylem_rol.currentIndexChanged.connect(self._eylem_rol_degisti)
        ust.addWidget(self._cb_eylem_rol)
        ust.addStretch(1)
        kl.addLayout(ust)

        kl.addWidget(self._ayrac())
        kl.addWidget(self._eylem_checkbox_grid())
        lay.addWidget(kart, 1)
        return w

    def _sekme_yetki_ozeti(self) -> QWidget:
        w = QWidget(self)
        w.setStyleSheet(f"background:{T.bg1};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        baslik = QLabel("Rol ve Yetki Matrisi")
        baslik.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        lay.addWidget(baslik)

        mod_lbl = QLabel("Modul Gorunurlugu")
        mod_lbl.setStyleSheet(f"color:{T.text2}; font-size:11.5px; font-weight:600;")
        lay.addWidget(mod_lbl)

        self._tbl_moduller = DataTable(self)
        self._tbl_moduller.kur_kolonlar(
            [("rol", "Rol", 100), ("moduller", "Gorebilecegi Moduller", 0)],
            geren="moduller",
        )
        lay.addWidget(self._tbl_moduller, 2)

        eylem_lbl = QLabel("Eylem Yetkileri")
        eylem_lbl.setStyleSheet(f"color:{T.text2}; font-size:11.5px; font-weight:600;")
        lay.addWidget(eylem_lbl)

        self._tbl_eylemler = DataTable(self)
        self._tbl_eylemler.kur_kolonlar(
            [("rol", "Rol", 100), ("eylemler", "Yetkiler", 0)],
            geren="eylemler",
        )
        lay.addWidget(self._tbl_eylemler, 1)
        return w

    def _modul_checkbox_grid(self) -> QWidget:
        w = QWidget(self)
        w.setStyleSheet("background:transparent;")
        grid = QGridLayout(w)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(8)

        for idx, modul_id in enumerate(_TUM_MODULLER):
            satir, sutun = divmod(idx, 4)
            grid.addWidget(self._checkbox_karti(modul_id, _MODUL_ETIKET[modul_id], self._cb_moduller), satir, sutun)
        return w

    def _eylem_checkbox_grid(self) -> QWidget:
        w = QWidget(self)
        w.setStyleSheet("background:transparent;")
        grid = QGridLayout(w)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(8)

        for idx, eylem in enumerate(_TUM_EYLEMLER):
            satir, sutun = divmod(idx, 2)
            kart = self._checkbox_karti(eylem, _EYLEM_ETIKET[eylem], self._cb_eylemler)
            self._cb_eylemler[eylem].setEnabled(False)
            grid.addWidget(kart, satir, sutun)
        return w

    def _checkbox_karti(self, anahtar: str, etiket: str, hedef: dict[str, QCheckBox]) -> QWidget:
        kap = QWidget(self)
        kap.setStyleSheet(f"background:{T.bg4}; border-radius:{T.radius_sm}px;")
        lay = QHBoxLayout(kap)
        lay.setContentsMargins(10, 8, 10, 8)

        cb = QCheckBox(etiket, kap)
        cb.setStyleSheet(
            f"QCheckBox {{ color:{T.text}; font-size:11.5px; spacing:6px; background:transparent; }}"
            f"QCheckBox::indicator {{ width:16px; height:16px; border:2px solid {T.border2}; "
            f"border-radius:3px; background:{T.bg3}; }}"
            f"QCheckBox::indicator:checked {{ background:{T.accent}; border-color:{T.accent}; }}"
        )
        hedef[anahtar] = cb
        lay.addWidget(cb)
        return kap

    def _alan_etiketi(self, metin: str) -> QLabel:
        lbl = QLabel(metin, self)
        lbl.setStyleSheet(f"color:{T.text2}; font-size:11px; font-weight:600;")
        return lbl

    def _bilgi_bandi(self, mesaj: str) -> QLabel:
        lbl = QLabel(mesaj, self)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(
            f"color:{T.text2}; font-size:11px; padding:8px 12px;"
            f"background:{T.bg4}; border-radius:{T.radius_sm}px;"
            f"border-left:3px solid {T.accent};"
        )
        return lbl

    @staticmethod
    def _ayrac() -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setFixedHeight(1)
        f.setStyleSheet(f"background:{T.border}; margin:4px 0;")
        return f

    def _yetki_uygula(self) -> None:
        olustur = rbac.yetki_var_mi(self._oturum, "kullanici.olustur")
        guncelle = rbac.yetki_var_mi(self._oturum, "kullanici.guncelle")
        pasife = rbac.yetki_var_mi(self._oturum, "kullanici.pasife_al")

        self._btn_ekle.setEnabled(olustur)
        self._btn_rol_guncelle.setEnabled(guncelle)
        self._btn_aktif_pasif.setEnabled(pasife)
        self._btn_izin_kaydet.setEnabled(guncelle)
        self._btn_modul_tumu.setEnabled(guncelle)
        self._btn_modul_temizle.setEnabled(guncelle)
        self._btn_rol_ekle.setEnabled(guncelle)

    def _rolleri_yukle(self) -> list[str]:
        try:
            roller = self._policy_svc.tum_roller()
        except Exception:
            roller = []
        if not roller:
            roller = ["admin", "yonetici", "kullanici"]
        return sorted(set(str(r) for r in roller))

    def _rol_combo_doldur(self, combo: QComboBox, *, include_admin: bool = True, secili: str | None = None) -> None:
        onceki = secili or combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        for rol_adi in self._roller:
            if not include_admin and rol_adi == "admin":
                continue
            combo.addItem(_ROL_ETIKET.get(rol_adi, rol_adi), rol_adi)
        if onceki is not None:
            idx = combo.findData(onceki)
            if idx >= 0:
                combo.setCurrentIndex(idx)
        combo.blockSignals(False)

    def _rol_formlarini_yenile(self, secili_rol: str | None = None) -> None:
        self._rol_combo_doldur(self._cb_yeni_rol, include_admin=True, secili=secili_rol)
        self._rol_combo_doldur(self._cb_secili_rol, include_admin=True, secili=secili_rol)
        self._rol_combo_doldur(self._cb_izin_rol, include_admin=False, secili=secili_rol)
        self._rol_combo_doldur(self._cb_eylem_rol, include_admin=True, secili=secili_rol)

        self._cb_rol_kopya.blockSignals(True)
        onceki = self._cb_rol_kopya.currentData()
        self._cb_rol_kopya.clear()
        self._cb_rol_kopya.addItem("Bos rol", "")
        for rol_adi in self._roller:
            self._cb_rol_kopya.addItem(_ROL_ETIKET.get(rol_adi, rol_adi), rol_adi)
        idx = self._cb_rol_kopya.findData(onceki)
        if idx >= 0:
            self._cb_rol_kopya.setCurrentIndex(idx)
        self._cb_rol_kopya.blockSignals(False)

    def _ozet_yukle(self) -> None:
        mod_rows = []
        for rol_adi, moduller in rbac.rol_modul_haritasi().items():
            if moduller is None:
                mod_txt = "Tum moduller"
            else:
                mod_txt = " | ".join(_MODUL_ETIKET.get(mod, mod) for mod in sorted(moduller)) or "-"
            mod_rows.append({"rol": _ROL_ETIKET.get(rol_adi, rol_adi), "moduller": mod_txt})
        self._tbl_moduller.set_veri(mod_rows)

        eylem_rows = []
        for rol_adi, eylemler in rbac.rol_eylem_haritasi().items():
            eylem_txt = " | ".join(_EYLEM_ETIKET.get(eylem, eylem) for eylem in sorted(eylemler)) or "-"
            eylem_rows.append({"rol": _ROL_ETIKET.get(rol_adi, rol_adi), "eylemler": eylem_txt})
        self._tbl_eylemler.set_veri(eylem_rows)

    def _izin_yukle(self, rol_adi: str) -> None:
        try:
            izinler = self._policy_svc.modul_seti_getir(rol_adi)
        except Exception as exc:
            exc_logla("YonetimPage._izin_yukle", exc)
            izinler = None

        if izinler is None:
            hardcoded = rbac.rol_modul_haritasi().get(rol_adi)
            izinler = set(_TUM_MODULLER) if hardcoded is None else set(hardcoded or set())

        for modul_id, cb in self._cb_moduller.items():
            cb.setChecked(modul_id in izinler)

    def _eylem_formunu_yukle(self, rol_adi: str) -> None:
        eylemler = rbac.rol_eylem_haritasi().get(rol_adi, set())
        for eylem, cb in self._cb_eylemler.items():
            cb.setChecked(eylem in eylemler)

    def _liste_yukle(self) -> None:
        self._alert.temizle()
        try:
            rows = self._svc.kullanici_listele(self._oturum)
        except AppHatasi as exc:
            self._tablo.set_veri([])
            self._alert.goster(str(exc), "warning")
            self._yetki_uygula()
            return
        except Exception as exc:
            self._tablo.set_veri([])
            exc_logla("YonetimPage._liste_yukle", exc)
            self._alert.goster(str(exc), "danger")
            self._yetki_uygula()
            return

        for row in rows:
            row["aktif_txt"] = "Aktif" if int(row.get("aktif", 0)) else "Pasif"
            row["rol_txt"] = _ROL_ETIKET.get(str(row.get("rol") or ""), str(row.get("rol") or "-"))
            row["sifre_txt"] = "Bekliyor" if int(row.get("sifre_degismeli", 0)) else "Tamam"
            row["son_giris"] = row.get("son_giris") or "-"

        self._tablo.set_veri(rows)

        toplam = len(rows)
        aktif = sum(1 for row in rows if int(row.get("aktif", 0)))
        pasif = toplam - aktif
        self._stat_toplam.set(str(toplam), T.accent)
        self._stat_aktif.set(str(aktif), T.green2)
        self._stat_pasif.set(str(pasif), T.red if pasif else T.text2)
        self._yetki_uygula()

    def _izin_rol_degisti(self, _idx: int) -> None:
        self._izin_yukle(self._cb_izin_rol.currentData() or "yonetici")

    def _eylem_rol_degisti(self, _idx: int) -> None:
        self._eylem_formunu_yukle(self._cb_eylem_rol.currentData() or "admin")

    def _tum_modulleri_sec(self) -> None:
        for cb in self._cb_moduller.values():
            cb.setChecked(True)

    def _tum_modulleri_temizle(self) -> None:
        for cb in self._cb_moduller.values():
            cb.setChecked(False)

    def _modul_izinleri_kaydet(self) -> None:
        self._alert.temizle()
        rol_adi = self._cb_izin_rol.currentData() or "yonetici"
        aktif_moduller = {modul_id for modul_id, cb in self._cb_moduller.items() if cb.isChecked()}

        try:
            self._policy_svc.rol_modullerini_kaydet(self._oturum, rol_adi, aktif_moduller)
            rbac.init_dari_db(self._db)
            self._ozet_yukle()
            self._alert.goster(f"{_ROL_ETIKET.get(rol_adi, rol_adi)} rolu modul izinleri kaydedildi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("YonetimPage._modul_izinleri_kaydet", exc)
            self._alert.goster(str(exc), "danger")

    def _rol_ekle(self) -> None:
        self._alert.temizle()
        yeni_rol = self._inp_rol_adi.text().strip()
        kopya_rol = str(self._cb_rol_kopya.currentData() or "").strip() or None
        try:
            rol_adi = self._policy_svc.rol_ekle(self._oturum, yeni_rol, kopya_rol)
            self._inp_rol_adi.clear()
            self._roller = self._rolleri_yukle()
            self._rol_formlarini_yenile(secili_rol=rol_adi)
            self._izin_yukle(rol_adi)
            self._ozet_yukle()
            self._alert.goster(f"Yeni rol eklendi: {rol_adi}", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("YonetimPage._rol_ekle", exc)
            self._alert.goster(str(exc), "danger")

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
            self._svc.kullanici_ekle(
                self._oturum,
                {
                    "ad": self._inp_ad.text(),
                    "parola": self._inp_parola.text(),
                    "rol": self._cb_yeni_rol.currentData(),
                },
            )
            self._inp_ad.clear()
            self._inp_parola.clear()
            self._liste_yukle()
            self._alert.goster("Kullanici basariyla eklendi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("YonetimPage._kullanici_ekle", exc)
            self._alert.goster(str(exc), "danger")

    def _secili_rol_guncelle(self) -> None:
        self._alert.temizle()
        if not self._secili_id:
            self._alert.goster("Lutfen listeden bir kullanici secin.", "warning")
            return
        try:
            self._svc.kullanici_rol_guncelle(self._oturum, self._secili_id, self._cb_secili_rol.currentData())
            self._liste_yukle()
            self._alert.goster("Kullanici rolu guncellendi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("YonetimPage._secili_rol_guncelle", exc)
            self._alert.goster(str(exc), "danger")

    def _aktif_pasif_degistir(self) -> None:
        self._alert.temizle()
        satir = self._tablo.secili_satir()
        if not satir or not self._secili_id:
            self._alert.goster("Lutfen listeden bir kullanici secin.", "warning")
            return

        try:
            if int(satir.get("aktif", 0)):
                self._svc.kullanici_pasife_al(self._oturum, self._secili_id)
                self._alert.goster("Kullanici pasife alindi.", "warning")
            else:
                self._svc.kullanici_aktif_et(self._oturum, self._secili_id)
                self._alert.goster("Kullanici aktif edildi.", "success")
            self._liste_yukle()
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("YonetimPage._aktif_pasif_degistir", exc)
            self._alert.goster(str(exc), "danger")
