# -*- coding: utf-8 -*-
"""
ui/pages/placeholder.py
────────────────────────
Henüz yazılmamış modüller için geçici sayfa.
PlaceholderPage(db) imzasına uyar — modül kayıt sistemiyle uyumlu.
"""
from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from ui.theme import T


class PlaceholderPage(QWidget):
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{T.bg0};")
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(14)

        ikon = QLabel("🚧")
        ikon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ikon.setStyleSheet("font-size:44px; background:transparent;")

        tit = QLabel("Bu modül geliştiriliyor")
        tit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tit.setStyleSheet(
            f"color:{T.text3}; font-size:18px; font-weight:700;"
            f" background:transparent;"
        )

        alt = QLabel("İlerleyen sprintlerde buraya taşınacak.")
        alt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        alt.setStyleSheet(
            f"color:{T.text4}; font-size:12px; background:transparent;"
        )

        lay.addWidget(ikon)
        lay.addWidget(tit)
        lay.addWidget(alt)
