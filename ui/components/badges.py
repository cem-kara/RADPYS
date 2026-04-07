# -*- coding: utf-8 -*-
"""ui/components/badges.py — Durum rozetleri"""
from __future__ import annotations
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from ui.theme import T


class Badge(QLabel):
    """
    Renkli durum rozeti.

    Kullanım:
        badge = Badge("aktif")
        badge = Badge("asim", tur="danger")
    """

    _DURUM_MAP = {
        "aktif":         (T.green2, T.bg0),
        "pasif":         (T.text3, T.bg4),
        "ayrildi":       (T.red, T.bg0),
        "taslak":        (T.amber, T.bg0),
        "onaylandi":     (T.green2, T.bg0),
        "iptal":         (T.text3, T.bg4),
        "uygun":         (T.green2, T.bg0),
        "uygun_degil":   (T.red, T.bg0),
        "takip":         (T.amber, T.bg0),
        "asim":          (T.red, "rgba(232,58,90,0.10)"),
        "normal":        (T.green2, T.bg0),
        "uyari":         (T.amber, "rgba(232,160,32,0.10)"),
        "tehlike":       (T.red, "rgba(232,58,90,0.10)"),
    }

    _TUR_MAP = {
        "success": (T.green2, "rgba(29,184,106,0.10)"),
        "warning": (T.amber, "rgba(232,160,32,0.10)"),
        "danger":  (T.red,  "rgba(232,58,90,0.10)"),
        "info":    (T.accent2,    "rgba(52,121,255,0.12)"),
        "muted":   (T.text3, T.bg4),
    }

    def __init__(self, etiket: str, tur: str = "", parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set(etiket, tur)

    def set(self, etiket: str, tur: str = "") -> None:
        self.setText(etiket.replace("_", " ").title())
        anahtar = etiket.lower().replace(" ", "_")

        if tur and tur in self._TUR_MAP:
            renk, arka = self._TUR_MAP[tur]
        elif anahtar in self._DURUM_MAP:
            renk, arka = self._DURUM_MAP[anahtar]
        else:
            renk, arka = T.text2, T.bg4

        self.setStyleSheet(
            f"background-color:{arka};"
            f"color:{renk};"
            f"border: 1px solid {renk}40;"
            f"border-radius:10px;"
            f"padding:2px 10px;"
            f"font-size:11px;"
            f"font-weight:600;"
        )
