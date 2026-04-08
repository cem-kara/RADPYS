# -*- coding: utf-8 -*-
"""ui/components/cards.py - card ve istatistik bilesenleri."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.styles import T


class Card(QFrame):
    """Basit kart kapsayici."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(16, 14, 16, 14)
        self._lay.setSpacing(10)

    @property
    def layout_(self):
        return self._lay


class SectionCard(QFrame):
    """Baslik cizgisi olan bolum karti."""

    aksiyon_tikland = Signal()

    def __init__(self, baslik: str, ikon: str = "", aksiyon_etiket: str = "", aksiyon_ikon: str = "", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            f"SectionCard {{"
            f"  background:{T.bg2};"
            f"  border:1px solid {T.border};"
            f"  border-radius:{T.radius}px;"
            f"}}"
        )

        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        hdr = QWidget()
        hdr.setStyleSheet(
            f"background:{T.bg3};"
            f"border-top-left-radius:{T.radius}px;"
            f"border-top-right-radius:{T.radius}px;"
        )
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(16, 10, 12, 10)
        hdr_lay.setSpacing(8)

        if ikon:
            from ui.styles.icons import pixmap as ipx

            ikon_lbl = QLabel()
            ikon_lbl.setPixmap(ipx(ikon, size=T.icon_md, color=T.text2))
            ikon_lbl.setStyleSheet("background:transparent;")
            hdr_lay.addWidget(ikon_lbl)

        baslik_lbl = QLabel(baslik)
        baslik_lbl.setStyleSheet(
            f"color:{T.text}; font-size:12.5px; font-weight:600;"
            f"background:transparent;"
        )
        hdr_lay.addWidget(baslik_lbl)
        hdr_lay.addStretch()

        if aksiyon_etiket:
            from ui.components.buttons import PrimaryButton

            self._aksiyon_btn = PrimaryButton(aksiyon_etiket, ikon=aksiyon_ikon)
            self._aksiyon_btn.setFixedHeight(28)
            self._aksiyon_btn.clicked.connect(self.aksiyon_tikland)
            hdr_lay.addWidget(self._aksiyon_btn)

        main_lay.addWidget(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{T.border};")
        main_lay.addWidget(sep)

        self._icerik = QWidget()
        self._icerik.setStyleSheet("background:transparent;")
        self._lay = QVBoxLayout(self._icerik)
        self._lay.setContentsMargins(16, 14, 16, 16)
        self._lay.setSpacing(12)
        main_lay.addWidget(self._icerik)

    @property
    def layout_(self) -> QVBoxLayout:
        return self._lay


class InfoCard(QFrame):
    """Yatay etiket-deger satirlari icin bilgi karti."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(16, 12, 16, 12)
        self._lay.setSpacing(8)

    def ekle(self, etiket: str, deger: str = "-", ikon: str = "") -> QLabel:
        """Bir bilgi satiri ekler ve deger labelini dondurur."""
        satir = QWidget()
        satir.setStyleSheet("background:transparent;")
        slay = QHBoxLayout(satir)
        slay.setContentsMargins(0, 0, 0, 0)
        slay.setSpacing(10)

        if ikon:
            from ui.styles.icons import pixmap as ipx

            i_lbl = QLabel()
            i_lbl.setPixmap(ipx(ikon, size=T.icon_sm, color=T.text3))
            i_lbl.setStyleSheet("background:transparent;")
            i_lbl.setFixedSize(T.icon_sm, T.icon_sm)
            slay.addWidget(i_lbl)

        etiket_lbl = QLabel(etiket + ":")
        etiket_lbl.setFixedWidth(150)
        etiket_lbl.setStyleSheet(
            f"color:{T.text3}; font-size:11.5px; background:transparent;"
        )
        etiket_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        deger_lbl = QLabel(deger)
        deger_lbl.setStyleSheet(
            f"color:{T.text}; font-size:12.5px; background:transparent;"
        )
        deger_lbl.setWordWrap(True)

        slay.addWidget(etiket_lbl)
        slay.addWidget(deger_lbl, 1)
        self._lay.addWidget(satir)
        return deger_lbl


class StatCard(QFrame):
    """Metrik karti: baslik + buyuk deger + opsiyonel alt metin."""

    def __init__(self, baslik: str, ikon: str = "", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(4)

        ust = QHBoxLayout()
        ust.setSpacing(6)

        if ikon:
            from ui.styles.icons import pixmap as ipx

            i_lbl = QLabel()
            i_lbl.setPixmap(ipx(ikon, size=T.icon_sm, color=T.text3))
            i_lbl.setStyleSheet("background:transparent;")
            ust.addWidget(i_lbl)

        self._lbl_baslik = QLabel(baslik.upper())
        self._lbl_baslik.setStyleSheet(
            f"color:{T.text3}; font-size:10px; font-weight:600;"
            f"letter-spacing:0.5px; background:transparent;"
        )
        ust.addWidget(self._lbl_baslik)
        ust.addStretch()
        lay.addLayout(ust)

        self._lbl_deger = QLabel("-")
        font = QFont()
        font.setPointSize(22)
        font.setBold(True)
        self._lbl_deger.setFont(font)
        self._lbl_deger.setStyleSheet("background:transparent;")

        self._lbl_alt = QLabel("")
        self._lbl_alt.setStyleSheet(
            f"color:{T.text2}; font-size:11px; background:transparent;"
        )
        self._lbl_alt.setVisible(False)

        lay.addWidget(self._lbl_deger)
        lay.addWidget(self._lbl_alt)

    def set(self, deger: str, renk: str = "", alt: str = "") -> None:
        self._lbl_deger.setText(deger)
        self._lbl_deger.setStyleSheet(
            f"color:{renk if renk else T.text}; background:transparent;"
        )
        if alt:
            self._lbl_alt.setText(alt)
            self._lbl_alt.setVisible(True)
        else:
            self._lbl_alt.setVisible(False)
