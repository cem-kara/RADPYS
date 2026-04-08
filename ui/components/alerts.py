# -*- coding: utf-8 -*-
"""ui/components/alerts.py �?" Uyarı bandı bile�Yeni"""
from __future__ import annotations
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from ui.styles import T


class AlertBar(QFrame):
    """
    Satır içi uyarı/bilgi/hata bandı.
    Exception mesajlarını göstermek için kullanılır �?" dialog açmaz.

    Kullanım:
        self._alert = AlertBar(self)
        layout.addWidget(self._alert)
        self._alert.goster("İzin limiti a�Yıldı.", "warning")
        self._alert.temizle()

    Türler: "danger" | "warning" | "success" | "info"
    """

    # ikon_adi: ui/icons.py'deki IKONLAR anahtarı
    _STILLER = {
        "danger":  (T.red,    "rgba(232,58,90,0.10)",   "alert_hata"),
        "warning": (T.amber,  "rgba(232,160,32,0.10)",  "alert_uyari"),
        "success": (T.green2, "rgba(29,184,106,0.10)",  "alert_basari"),
        "info":    (T.accent2,"rgba(52,121,255,0.12)",  "alert_bilgi"),
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

        self._kapat = QPushButton()
        self._kapat.setFixedSize(20, 20)
        self._kapat.setFlat(True)
        self._kapat.setCursor(Qt.CursorShape.PointingHandCursor)
        self._kapat.clicked.connect(self.temizle)
        from ui.styles.icons import ic as _ic
        from PySide6.QtCore import QSize
        self._kapat.setIcon(_ic('kapat', size=12, color=T.text3))
        self._kapat.setIconSize(QSize(12, 12))

        lay.addWidget(self._ikon)
        lay.addWidget(self._mesaj, 1)
        lay.addWidget(self._kapat)

    def goster(self, mesaj: str, tur: str = "danger") -> None:
        """Uyarı bandını gösterir."""
        from ui.styles.icons import pixmap as ipx
        renk, arka, ikon_adi = self._STILLER.get(tur, self._STILLER["danger"])
        self._ikon.setPixmap(ipx(ikon_adi, size=16, color=renk))
        self._ikon.setFixedSize(16, 16)
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
        Try/except kısayolu �?" exception'ı alert'e yazar.

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


