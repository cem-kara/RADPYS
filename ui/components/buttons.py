# -*- coding: utf-8 -*-
"""ui/components/buttons.py — Buton bileşenleri"""
from __future__ import annotations
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt


class PrimaryButton(QPushButton):
    """Mavi aksiyon butonu (primary=true)."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setProperty("primary", "true")
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class DangerButton(QPushButton):
    """Kırmızı silme/iptal butonu (danger=true)."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setProperty("danger", "true")
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class GhostButton(QPushButton):
    """Şeffaf arka plan butonu (ghost=true)."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setProperty("ghost", "true")
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class IconButton(QPushButton):
    """İkon butonu — metin yok, kare boyut."""
    def __init__(self, tooltip: str = "", size: int = 32, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setProperty("ghost", "true")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if tooltip:
            self.setToolTip(tooltip)
