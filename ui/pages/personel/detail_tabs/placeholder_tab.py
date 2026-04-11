# -*- coding: utf-8 -*-
"""Personel detay sekmeleri icin ortak placeholder tab."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.styles import T
from ui.styles.icons import Icons


class PersonelDetailPlaceholderTab(QWidget):
    """Henuz gelistirilmemis personel detay sekmeleri icin ortak iskelet."""

    def __init__(self, title: str, subtitle: str = "Bu sekme yakinda eklenecek.", parent=None):
        super().__init__(parent)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(10)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = Icons.label("bakim", T.text3, 44)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(icon)

        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet(
            f"color:{T.text2}; font-size:16px; font-weight:700;"
            f"background:transparent;"
        )
        lay.addWidget(lbl_title)

        lbl_sub = QLabel(subtitle)
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setStyleSheet(
            f"color:{T.text4}; font-size:12px; background:transparent;"
        )
        lay.addWidget(lbl_sub)

    def yenile(self) -> None:
        """Detay host tarafinda tek tip cagri icin no-op."""
        return
