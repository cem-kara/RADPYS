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

        self.accept()
