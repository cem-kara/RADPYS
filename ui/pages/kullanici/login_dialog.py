# -*- coding: utf-8 -*-
"""ui/pages/kullanici/login_dialog.py — Uygulama acilis giris diyalogu."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
)

from app.db.database import Database
from app.exceptions import AppHatasi
from app.services.auth_service import AuthService
from ui.components import AlertBar, GhostButton, PrimaryButton
from ui.styles import DARK, LIGHT, ThemeManager
from ui.styles.icons import pixmap as icon_pixmap


def _tokens() -> dict[str, str]:
    return LIGHT if ThemeManager.current_theme() == "light" else DARK


class LoginDialog(QDialog):
    """Uygulamaya giris icin zorunlu kullanici adı/parola diyalogu."""

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self._svc = AuthService(db)
        self.oturum: dict | None = None
        self._bekleyen_kullanici_id: str | None = None

        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setWindowTitle("RADPYS Giriş")
        self.setFixedSize(460, 500)

        self._build()
        self._apply_theme_styles()

    def _build(self) -> None:
        root_lay = QVBoxLayout(self)
        root_lay.setContentsMargins(18, 18, 18, 18)
        root_lay.setSpacing(0)

        self._card = QFrame(self)
        self._card.setObjectName("LoginCard")

        lay = QVBoxLayout(self._card)
        lay.setContentsMargins(34, 34, 34, 30)
        lay.setSpacing(12)

        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        title_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo = QLabel()
        logo.setPixmap(icon_pixmap("lock", size=22, color="accent"))
        logo.setFixedSize(24, 24)

        baslik = QLabel("RADPYS GIRIS")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setObjectName("LoginTitle")

        title_row.addWidget(logo)
        title_row.addWidget(baslik)

        alt = QLabel("Devam etmek için kullanıcı adı ve parola girin.")
        alt.setWordWrap(True)
        alt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        alt.setObjectName("LoginSubtitle")

        self._alert = AlertBar(self._card)

        self._inp_ad = QLineEdit(self._card)
        self._inp_ad.setPlaceholderText("Kullanıcı adı")
        self._inp_ad.setMinimumHeight(40)

        self._inp_parola = QLineEdit(self._card)
        self._inp_parola.setPlaceholderText("Parola")
        self._inp_parola.setEchoMode(QLineEdit.EchoMode.Password)
        self._inp_parola.setMinimumHeight(40)
        self._inp_parola.returnPressed.connect(self._giris)

        self._inp_yeni_parola = QLineEdit(self._card)
        self._inp_yeni_parola.setPlaceholderText("Yeni parola")
        self._inp_yeni_parola.setEchoMode(QLineEdit.EchoMode.Password)
        self._inp_yeni_parola.setMinimumHeight(40)
        self._inp_yeni_parola.setVisible(False)
        self._inp_yeni_parola.returnPressed.connect(self._giris)

        self._inp_yeni_parola_tekrar = QLineEdit(self._card)
        self._inp_yeni_parola_tekrar.setPlaceholderText("Yeni parola (tekrar)")
        self._inp_yeni_parola_tekrar.setEchoMode(QLineEdit.EchoMode.Password)
        self._inp_yeni_parola_tekrar.setMinimumHeight(40)
        self._inp_yeni_parola_tekrar.setVisible(False)
        self._inp_yeni_parola_tekrar.returnPressed.connect(self._giris)

        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(8)

        self._btn_cikis = GhostButton("Iptal")
        self._btn_cikis.setMinimumHeight(38)
        self._btn_cikis.clicked.connect(self.reject)

        self._btn_giris = PrimaryButton("Giris Yap")
        self._btn_giris.setMinimumHeight(38)
        self._btn_giris.clicked.connect(self._giris)

        btn_lay.addStretch(1)
        btn_lay.addWidget(self._btn_cikis)
        btn_lay.addWidget(self._btn_giris)

        lay.addLayout(title_row)
        lay.addWidget(alt)
        lay.addWidget(self._alert)
        lay.addWidget(self._inp_ad)
        lay.addWidget(self._inp_parola)
        lay.addWidget(self._inp_yeni_parola)
        lay.addWidget(self._inp_yeni_parola_tekrar)
        lay.addLayout(btn_lay)

        root_lay.addWidget(self._card)

        self._inp_ad.setFocus()

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._giris()
            return
        if key == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)

    def _apply_theme_styles(self) -> None:
        t = _tokens()
        self.setStyleSheet(
            f"""
            QDialog {{
                background: transparent;
                color: {t['TEXT_PRIMARY']};
            }}
            QFrame#LoginCard {{
                background: {t['BG_SECONDARY']};
                border: 1px solid {t['BORDER_PRIMARY']};
                border-radius: 14px;
            }}
            QLabel#LoginTitle {{
                color: {t['TEXT_PRIMARY']};
                font-size: 20px;
                font-weight: 700;
            }}
            QLabel#LoginSubtitle {{
                color: {t['TEXT_SECONDARY']};
                font-size: 12px;
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
            """
        )

    def _show_alert(self, mesaj: str, tur: str = "warning") -> None:
        self._alert.goster(mesaj, tur)

    def _giris(self) -> None:
        self._alert.temizle()

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
