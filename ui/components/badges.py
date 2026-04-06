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
        "aktif":         (T.success, T.bg_app),
        "pasif":         (T.text_muted, T.bg_input),
        "ayrildi":       (T.danger, T.bg_app),
        "taslak":        (T.warning, T.bg_app),
        "onaylandi":     (T.success, T.bg_app),
        "iptal":         (T.text_muted, T.bg_input),
        "uygun":         (T.success, T.bg_app),
        "uygun_degil":   (T.danger, T.bg_app),
        "takip":         (T.warning, T.bg_app),
        "asim":          (T.danger, T.danger_dim),
        "normal":        (T.success, T.bg_app),
        "uyari":         (T.warning, T.warning_dim),
        "tehlike":       (T.danger, T.danger_dim),
    }

    _TUR_MAP = {
        "success": (T.success, T.success_dim),
        "warning": (T.warning, T.warning_dim),
        "danger":  (T.danger,  T.danger_dim),
        "info":    (T.info,    T.accent_dim),
        "muted":   (T.text_muted, T.bg_input),
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
            renk, arka = T.text_secondary, T.bg_input

        self.setStyleSheet(
            f"background-color:{arka};"
            f"color:{renk};"
            f"border: 1px solid {renk}40;"
            f"border-radius:10px;"
            f"padding:2px 10px;"
            f"font-size:11px;"
            f"font-weight:600;"
        )
