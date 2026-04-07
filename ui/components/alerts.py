# -*- coding: utf-8 -*-
"""ui/components/alerts.py — Uyarı bandı bileşeni"""
from __future__ import annotations
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from ui.theme import T


class AlertBar(QFrame):
    """
    Satır içi uyarı/bilgi/hata bandı.
    Exception mesajlarını göstermek için kullanılır — dialog açmaz.

    Kullanım:
        self._alert = AlertBar(self)
        layout.addWidget(self._alert)
        self._alert.goster("İzin limiti aşıldı.", "warning")
        self._alert.temizle()

    Türler: "danger" | "warning" | "success" | "info"
    """

    _STILLER = {
        "danger":  (T.red,  "rgba(232,58,90,0.10)",  "⛔"),
        "warning": (T.amber, "rgba(232,160,32,0.10)", "⚠"),
        "success": (T.green2, "rgba(29,184,106,0.10)", "✓"),
        "info":    (T.accent2,    "rgba(52,121,255,0.12)",  "ℹ"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 8, 8, 8)
        lay.setSpacing(8)

        self._ikon  = QLabel()
        self._mesaj = QLabel()
        self._mesaj.setWordWrap(True)
        self._mesaj.setSizePolicy(
            self._mesaj.sizePolicy().horizontalPolicy(),
            self._mesaj.sizePolicy().verticalPolicy(),
        )

        self._kapat = QPushButton("✕")
        self._kapat.setFixedSize(20, 20)
        self._kapat.setFlat(True)
        self._kapat.setCursor(Qt.CursorShape.PointingHandCursor)
        self._kapat.clicked.connect(self.temizle)

        lay.addWidget(self._ikon)
        lay.addWidget(self._mesaj, 1)
        lay.addWidget(self._kapat)

    def goster(self, mesaj: str, tur: str = "danger") -> None:
        """Uyarı bandını gösterir."""
        renk, arka, ikon = self._STILLER.get(tur, self._STILLER["danger"])
        self._ikon.setText(ikon)
        self._mesaj.setText(mesaj)
        self.setStyleSheet(
            f"background-color:{arka};"
            f"border:1px solid {renk}60;"
            f"border-radius:6px;"
        )
        self._ikon.setStyleSheet(f"color:{renk}; font-size:14px;")
        self._mesaj.setStyleSheet(f"color:{renk}; background:transparent;")
        self._kapat.setStyleSheet(
            f"color:{renk}; background:transparent; border:none;"
        )
        self.setVisible(True)

    def temizle(self) -> None:
        """Uyarı bandını gizler."""
        self._mesaj.setText("")
        self.setVisible(False)

    @classmethod
    def hata_yakala(cls, parent, fn, alert_widget: "AlertBar"):
        """
        Try/except kısayolu — exception'ı alert'e yazar.

        Kullanım:
            AlertBar.hata_yakala(self, lambda: svc.kaydet(veri), self._alert)
        """
        from app.exceptions import AppHatasi
        alert_widget.temizle()
        try:
            fn()
        except AppHatasi as e:
            alert_widget.goster(str(e), "warning")
        except Exception as e:
            alert_widget.goster(f"Beklenmeyen hata: {e}", "danger")
