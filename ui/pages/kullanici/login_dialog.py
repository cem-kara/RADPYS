# -*- coding: utf-8 -*-
"""ui/pages/kullanici/login_dialog.py — Uygulama acilis giris diyalogu"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout

from app.db.database import Database
from app.exceptions import AppHatasi
from app.services.auth_service import AuthService
from ui.components import AlertBar, GhostButton, PrimaryButton
from ui.theme import T


class LoginDialog(QDialog):
    """Uygulamaya giris icin zorunlu kullanici adi/parola diyaloğu."""

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self._svc = AuthService(db)
        self.oturum: dict | None = None

        self.setModal(True)
        self.setWindowTitle("REPYS Giris")
        self.setMinimumWidth(420)
        self.setStyleSheet(f"background:{T.bg1};")

        self._build()

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(10)

        baslik = QLabel("Kullanici Girisi")
        baslik.setAlignment(Qt.AlignmentFlag.AlignLeft)
        baslik.setStyleSheet(f"color:{T.text}; font-size:16px; font-weight:700;")

        alt = QLabel("Devam etmek icin kullanici adiniz ve parolaniz ile giris yapin.")
        alt.setWordWrap(True)
        alt.setStyleSheet(f"color:{T.text2}; font-size:12px;")

        self._alert = AlertBar(self)

        self._inp_ad = QLineEdit(self)
        self._inp_ad.setPlaceholderText("Kullanici adi")
        self._inp_ad.setMinimumHeight(34)

        self._inp_parola = QLineEdit(self)
        self._inp_parola.setPlaceholderText("Parola")
        self._inp_parola.setEchoMode(QLineEdit.EchoMode.Password)
        self._inp_parola.setMinimumHeight(34)
        self._inp_parola.returnPressed.connect(self._giris)

        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(8)

        self._btn_cikis = GhostButton("Iptal")
        self._btn_cikis.clicked.connect(self.reject)

        self._btn_giris = PrimaryButton("Giris Yap")
        self._btn_giris.clicked.connect(self._giris)

        btn_lay.addStretch(1)
        btn_lay.addWidget(self._btn_cikis)
        btn_lay.addWidget(self._btn_giris)

        lay.addWidget(baslik)
        lay.addWidget(alt)
        lay.addWidget(self._alert)
        lay.addWidget(self._inp_ad)
        lay.addWidget(self._inp_parola)
        lay.addLayout(btn_lay)

        self._inp_ad.setFocus()

    def _giris(self) -> None:
        self._alert.temizle()
        try:
            self.oturum = self._svc.giris_yap(self._inp_ad.text(), self._inp_parola.text())
        except AppHatasi as e:
            self._alert.goster(str(e), "warning")
            self._inp_parola.selectAll()
            self._inp_parola.setFocus()
            return
        except Exception as e:
            self._alert.goster(f"Beklenmeyen hata: {e}", "danger")
            return

        self.accept()
