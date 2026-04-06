# -*- coding: utf-8 -*-
"""ui/components/cards.py — Kart ve istatistik widget'ları"""
from __future__ import annotations
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.theme import T


class Card(QFrame):
    """
    Kenarlıklı, arka planlı kart container.
    GroupBox yerine kullanılır — başlık opsiyonel.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(16, 14, 16, 14)
        self._lay.setSpacing(10)

    @property
    def layout_(self):
        return self._lay


class StatCard(QFrame):
    """
    Metrik kartı: başlık + büyük sayı + opsiyonel alt metin.

    Kullanım:
        card = StatCard("Toplam Personel")
        card.set("42")
        card.set("5", renk=T.warning, alt="Bu ay izinli")
    """

    def __init__(self, baslik: str, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(2)

        self._lbl_baslik = QLabel(baslik.upper())
        self._lbl_baslik.setStyleSheet(
            f"color:{T.text_muted}; font-size:10px; font-weight:600;"
            f"letter-spacing:0.5px;"
        )

        self._lbl_deger = QLabel("—")
        font = QFont()
        font.setPointSize(22)
        font.setBold(True)
        self._lbl_deger.setFont(font)

        self._lbl_alt = QLabel("")
        self._lbl_alt.setStyleSheet(f"color:{T.text_secondary}; font-size:11px;")
        self._lbl_alt.setVisible(False)

        lay.addWidget(self._lbl_baslik)
        lay.addWidget(self._lbl_deger)
        lay.addWidget(self._lbl_alt)

    def set(self, deger: str, renk: str = "", alt: str = "") -> None:
        self._lbl_deger.setText(deger)
        self._lbl_deger.setStyleSheet(
            f"color:{renk if renk else T.text_primary};"
        )
        if alt:
            self._lbl_alt.setText(alt)
            self._lbl_alt.setVisible(True)
        else:
            self._lbl_alt.setVisible(False)
