# -*- coding: utf-8 -*-
"""ui/pages/kullanici/login_dialog.py — Uygulama acilis giris diyalogu."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)

from app.db.database import Database
from app.exceptions import AppHatasi
from app.services.auth_service import AuthService
from ui.styles import DARK, LIGHT, ThemeManager


def _tokens() -> dict[str, str]:
    return LIGHT if ThemeManager.current_theme() == "light" else DARK


class LoginDialog(QDialog):
    """Uygulamaya giris icin zorunlu kullanici adi/parola diyalogu."""

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self._svc = AuthService(db)
        self.oturum: dict | None = None
        self._bekleyen_kullanici_id: str | None = None

        self.setModal(True)
        self.setWindowTitle("RADPYS Giris")
        self.setMinimumWidth(420)

        self._build()
        self._apply_theme_styles()

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(10)

        baslik = QLabel("Kullanici Girisi")
        baslik.setAlignment(Qt.AlignmentFlag.AlignLeft)
        baslik.setObjectName("LoginTitle")

        alt = QLabel("Devam etmek icin kullanici adiniz ve parolaniz ile giris yapin.")
        alt.setWordWrap(True)
        alt.setObjectName("LoginSubtitle")

        self._alert = QLabel("")
        self._alert.setObjectName("LoginAlert")
        self._alert.setVisible(False)
        self._alert.setWordWrap(True)

        self._inp_ad = QLineEdit(self)
        self._inp_ad.setPlaceholderText("Kullanici adi")
        self._inp_ad.setMinimumHeight(34)

        self._inp_parola = QLineEdit(self)
        self._inp_parola.setPlaceholderText("Parola")
        self._inp_parola.setEchoMode(QLineEdit.EchoMode.Password)
        self._inp_parola.setMinimumHeight(34)
        self._inp_parola.returnPressed.connect(self._giris)

        self._inp_yeni_parola = QLineEdit(self)
        self._inp_yeni_parola.setPlaceholderText("Yeni parola")
        self._inp_yeni_parola.setEchoMode(QLineEdit.EchoMode.Password)
        self._inp_yeni_parola.setMinimumHeight(34)
        self._inp_yeni_parola.setVisible(False)
        self._inp_yeni_parola.returnPressed.connect(self._giris)

        self._inp_yeni_parola_tekrar = QLineEdit(self)
        self._inp_yeni_parola_tekrar.setPlaceholderText("Yeni parola (tekrar)")
        self._inp_yeni_parola_tekrar.setEchoMode(QLineEdit.EchoMode.Password)
        self._inp_yeni_parola_tekrar.setMinimumHeight(34)
        self._inp_yeni_parola_tekrar.setVisible(False)
        self._inp_yeni_parola_tekrar.returnPressed.connect(self._giris)

        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(8)

        self._btn_cikis = QPushButton("Iptal")
        self._btn_cikis.setObjectName("LoginCancelButton")
        self._btn_cikis.clicked.connect(self.reject)

        self._btn_giris = QPushButton("Giris Yap")
        self._btn_giris.setObjectName("LoginPrimaryButton")
        self._btn_giris.clicked.connect(self._giris)

        btn_lay.addStretch(1)
        btn_lay.addWidget(self._btn_cikis)
        btn_lay.addWidget(self._btn_giris)

        lay.addWidget(baslik)
        lay.addWidget(alt)
        lay.addWidget(self._alert)
        lay.addWidget(self._inp_ad)
        lay.addWidget(self._inp_parola)
        lay.addWidget(self._inp_yeni_parola)
        lay.addWidget(self._inp_yeni_parola_tekrar)
        lay.addLayout(btn_lay)

        self._inp_ad.setFocus()

    def _apply_theme_styles(self) -> None:
        t = _tokens()
        self.setStyleSheet(
            f"""
            QDialog {{
                background: {t['BG_SECONDARY']};
                color: {t['TEXT_PRIMARY']};
            }}
            QLabel#LoginTitle {{
                color: {t['TEXT_PRIMARY']};
                font-size: 16px;
                font-weight: 700;
            }}
            QLabel#LoginSubtitle {{
                color: {t['TEXT_SECONDARY']};
                font-size: 12px;
            }}
            QLabel#LoginAlert {{
                border: 1px solid {t['STATUS_WARNING_BORDER']};
                background: {t['STATUS_WARNING_BG']};
                color: {t['STATUS_WARNING']};
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 11px;
            }}
            QLineEdit {{
                background: {t['INPUT_BG']};
                border: 1px solid {t['INPUT_BORDER']};
                border-radius: 8px;
                padding: 6px 10px;
                color: {t['TEXT_PRIMARY']};
            }}
            QLineEdit:focus {{
                border-color: {t['INPUT_BORDER_FOCUS']};
            }}
            QPushButton#LoginCancelButton {{
                background: {t['BTN_SECONDARY_BG']};
                color: {t['BTN_SECONDARY_TEXT']};
                border: 1px solid {t['BTN_SECONDARY_BORDER']};
                border-radius: 8px;
                padding: 7px 12px;
            }}
            QPushButton#LoginCancelButton:hover {{
                background: {t['BTN_SECONDARY_HOVER']};
            }}
            QPushButton#LoginPrimaryButton {{
                background: {t['BTN_PRIMARY_BG']};
                color: {t['BTN_PRIMARY_TEXT']};
                border: 1px solid {t['BTN_PRIMARY_BORDER']};
                border-radius: 8px;
                padding: 7px 12px;
                font-weight: 600;
            }}
            QPushButton#LoginPrimaryButton:hover {{
                background: {t['BTN_PRIMARY_HOVER']};
            }}
            """
        )

    def _show_alert(self, mesaj: str, tur: str = "warning") -> None:
        t = _tokens()
        stiller = {
            "warning": (t["STATUS_WARNING"], t["STATUS_WARNING_BG"], t["STATUS_WARNING_BORDER"]),
            "danger": (t["STATUS_ERROR"], t["STATUS_ERROR_BG"], t["STATUS_ERROR_BORDER"]),
            "success": (t["STATUS_SUCCESS"], t["STATUS_SUCCESS_BG"], t["STATUS_SUCCESS_BORDER"]),
            "info": (t["STATUS_INFO"], t["ACCENT_BG"], t["ACCENT_35"]),
        }
        renk, arkaplan, kenar = stiller.get(tur, stiller["warning"])
        self._alert.setStyleSheet(
            f"border:1px solid {kenar}; background:{arkaplan}; color:{renk}; border-radius:8px; padding:8px 10px;"
        )
        self._alert.setText(mesaj)
        self._alert.setVisible(True)

    def _giris(self) -> None:
        self._alert.clear()
        self._alert.setVisible(False)

        if self._bekleyen_kullanici_id:
            self._ilk_sifre_degistir()
            return

        try:
            self.oturum = self._svc.giris_yap(self._inp_ad.text(), self._inp_parola.text())
        except AppHatasi as e:
            self._show_alert(str(e), "warning")
            self._inp_parola.selectAll()
            self._inp_parola.setFocus()
            return
        except Exception as e:
            self._show_alert(f"Beklenmeyen hata: {e}", "danger")
            return

        if self.oturum and self.oturum.get("sifre_degismeli"):
            self._bekleyen_kullanici_id = str(self.oturum["id"])
            self._btn_giris.setText("Sifreyi Degistir")
            self._inp_yeni_parola.setVisible(True)
            self._inp_yeni_parola_tekrar.setVisible(True)
            self._show_alert(
                "Ilk giriste sifre degistirmeniz zorunludur.",
                "info",
            )
            self._inp_yeni_parola.setFocus()
            return

        self.accept()

    def _ilk_sifre_degistir(self) -> None:
        if not self._bekleyen_kullanici_id:
            return

        yeni = self._inp_yeni_parola.text()
        tekrar = self._inp_yeni_parola_tekrar.text()
        if not yeni or not tekrar:
            self._show_alert("Yeni parola alanlari zorunludur.", "warning")
            return
        if yeni != tekrar:
            self._show_alert("Yeni parola alanlari uyusmuyor.", "warning")
            self._inp_yeni_parola_tekrar.selectAll()
            self._inp_yeni_parola_tekrar.setFocus()
            return
        if yeni == self._inp_parola.text():
            self._show_alert("Yeni parola mevcut parola ile ayni olamaz.", "warning")
            self._inp_yeni_parola.selectAll()
            self._inp_yeni_parola.setFocus()
            return

        try:
            self._svc.ilk_giris_parola_degistir(self._bekleyen_kullanici_id, yeni)
        except AppHatasi as e:
            self._show_alert(str(e), "warning")
            return
        except Exception as e:
            self._show_alert(f"Beklenmeyen hata: {e}", "danger")
            return

        if self.oturum is not None:
            self.oturum["sifre_degismeli"] = False
        self.accept()
