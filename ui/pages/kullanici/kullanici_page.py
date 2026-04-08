# -*- coding: utf-8 -*-
"""ui/pages/kullanici/kullanici_page.py �?" RBAC kullanici giris modulu"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
)

from app.db.database import Database
from app.exceptions import AppHatasi
from app.rbac import yetki_var_mi
from app.services.auth_service import AuthService
from ui.components import (
    AlertBar,
    AsyncRunner,
    Card,
    DataTable,
    GhostButton,
    PrimaryButton,
)
from ui.styles import T


class KullaniciPage(QWidget):
    """Kullanici girisi ve rol bazli kullanici yonetimi ekrani."""

    def __init__(self, db: Database, oturum: dict | None = None, parent=None):
        super().__init__(parent)
        self._svc = AuthService(db)
        self._oturum: dict | None = oturum
        self.setStyleSheet(f"background:{T.bg0};")
        self._build()
        if self._oturum:
            self._oturum_uygula()

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)

        self._alert = AlertBar(self)
        lay.addWidget(self._alert)

        self._build_giris_karti(lay)
        self._build_kullanici_karti(lay)
        lay.addStretch(1)

    def _build_giris_karti(self, parent_lay: QVBoxLayout) -> None:
        kart = Card(self)
        kl = kart.layout_

        baslik = QLabel("RBAC Kullanici Girisi")
        baslik.setStyleSheet(f"color:{T.text}; font-size:16px; font-weight:700;")
        kl.addWidget(baslik)

        satir = QHBoxLayout()
        satir.setSpacing(8)

        self._inp_ad = QLineEdit()
        self._inp_ad.setPlaceholderText("Kullanici adi")
        self._inp_ad.setMinimumWidth(180)

        self._inp_parola = QLineEdit()
        self._inp_parola.setPlaceholderText("Parola")
        self._inp_parola.setEchoMode(QLineEdit.EchoMode.Password)
        self._inp_parola.returnPressed.connect(self._giris)

        self._btn_giris = PrimaryButton("Giris Yap")
        self._btn_giris.clicked.connect(self._giris)

        self._btn_cikis = GhostButton("Cikis")
        self._btn_cikis.clicked.connect(self._cikis)
        self._btn_cikis.setVisible(False)

        satir.addWidget(self._inp_ad)
        satir.addWidget(self._inp_parola, 1)
        satir.addWidget(self._btn_giris)
        satir.addWidget(self._btn_cikis)
        kl.addLayout(satir)

        self._lbl_oturum = QLabel("Durum: Giris yapilmadi")
        self._lbl_oturum.setStyleSheet(f"color:{T.text2}; font-size:12px;")
        kl.addWidget(self._lbl_oturum)

        parent_lay.addWidget(kart)

    def _build_kullanici_karti(self, parent_lay: QVBoxLayout) -> None:
        kart = Card(self)
        kl = kart.layout_

        baslik = QLabel("Kullanicilar")
        baslik.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        kl.addWidget(baslik)

        form = QHBoxLayout()
        form.setSpacing(8)

        self._new_ad = QLineEdit()
        self._new_ad.setPlaceholderText("Yeni kullanici adi")

        self._new_parola = QLineEdit()
        self._new_parola.setPlaceholderText("Parola (en az 6 karakter)")
        self._new_parola.setEchoMode(QLineEdit.EchoMode.Password)

        self._new_rol = QComboBox()
        self._new_rol.addItem("admin", "admin")
        self._new_rol.addItem("yonetici", "yonetici")
        self._new_rol.addItem("kullanici", "kullanici")

        self._btn_ekle = PrimaryButton("Kullanici Ekle")
        self._btn_ekle.clicked.connect(self._kullanici_ekle)

        form.addWidget(self._new_ad)
        form.addWidget(self._new_parola)
        form.addWidget(self._new_rol)
        form.addWidget(self._btn_ekle)
        kl.addLayout(form)

        self._tablo = DataTable(self)
        self._tablo.kur_kolonlar([
            ("ad", "Kullanici", 180),
            ("rol", "Rol", 120),
            ("aktif_txt", "Durum", 100),
            ("son_giris", "Son Giris", 190),
        ], geren="son_giris")
        kl.addWidget(self._tablo, 1)

        parent_lay.addWidget(kart, 1)

    # �"?�"? Aksiyonlar �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?

    def _giris(self) -> None:
        self._alert.temizle()
        try:
            self._oturum = self._svc.giris_yap(
                self._inp_ad.text(),
                self._inp_parola.text(),
            )
        except AppHatasi as e:
            self._alert.goster(str(e), "warning")
            return
        except Exception as e:
            self._alert.goster(f"Beklenmeyen hata: {e}", "danger")
            return

        self._lbl_oturum.setText(
            f"Durum: Aktif oturum {self._oturum['ad']} ({self._oturum['rol']})"
        )
        self._btn_cikis.setVisible(True)
        self._inp_parola.clear()
        self._btn_ekle.setEnabled(yetki_var_mi(self._oturum, "kullanici.olustur"))
        self._kullanici_listesi_yukle()

    def _cikis(self) -> None:
        self._oturum = None
        self._btn_cikis.setVisible(False)
        self._lbl_oturum.setText("Durum: Giris yapilmadi")
        self._tablo.set_veri([])
        self._btn_ekle.setEnabled(False)

    def _kullanici_listesi_yukle(self) -> None:
        if not self._oturum:
            return
        AsyncRunner(
            fn=lambda: self._svc.kullanici_listele(self._oturum),
            on_done=self._kullanici_listesi_goster,
            on_error=lambda m: self._alert.goster(m, "info"),
            parent=self,
        ).start()

    def _kullanici_listesi_goster(self, rows: list[dict]) -> None:
        for r in rows:
            r["aktif_txt"] = "Aktif" if int(r.get("aktif", 0)) else "Pasif"
        self._tablo.set_veri(rows)

    def _kullanici_ekle(self) -> None:
        self._alert.temizle()
        if not self._oturum:
            self._alert.goster("Kullanici eklemek icin once giris yapin.", "warning")
            return

        try:
            self._svc.kullanici_ekle(self._oturum, {
                "ad": self._new_ad.text(),
                "parola": self._new_parola.text(),
                "rol": self._new_rol.currentData(),
            })
            self._new_ad.clear()
            self._new_parola.clear()
            self._kullanici_listesi_yukle()
            self._alert.goster("Kullanici eklendi.", "success")
        except AppHatasi as e:
            self._alert.goster(str(e), "warning")
        except Exception as e:
            self._alert.goster(f"Beklenmeyen hata: {e}", "danger")

    def _oturum_uygula(self) -> None:
        self._lbl_oturum.setText(
            f"Durum: Aktif oturum {self._oturum['ad']} ({self._oturum['rol']})"
        )
        self._btn_giris.setVisible(False)
        self._btn_cikis.setVisible(False)
        self._inp_ad.setReadOnly(True)
        self._inp_parola.setReadOnly(True)
        self._inp_ad.setText(self._oturum["ad"])
        self._btn_ekle.setEnabled(yetki_var_mi(self._oturum, "kullanici.olustur"))
        self._kullanici_listesi_yukle()


