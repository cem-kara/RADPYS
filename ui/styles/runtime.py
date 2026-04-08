# -*- coding: utf-8 -*-
"""ui/styles/runtime.py — calisan tema degerleri icin ortak API."""
from __future__ import annotations

from ui.styles.colors import DARK, LIGHT
from ui.styles.theme_manager import ThemeManager


class ThemeValues:
    """Aktif tema tokenlarini alan bazli sunar."""

    # Layout sabitleri
    sidebar_w = 240
    topbar_h = 52
    radius = 12
    radius_sm = 9
    input_h = 34
    icon_sm = 14
    icon_md = 16
    icon_lg = 20

    @staticmethod
    def _tokens() -> dict[str, str]:
        return LIGHT if ThemeManager.current_theme() == "light" else DARK

    @property
    def bg0(self) -> str:
        return self._tokens()["BG_PRIMARY"]

    @property
    def bg1(self) -> str:
        return self._tokens()["BG_SECONDARY"]

    @property
    def bg2(self) -> str:
        return self._tokens()["BG_TERTIARY"]

    @property
    def bg3(self) -> str:
        return self._tokens()["BG_ELEVATED"]

    @property
    def bg4(self) -> str:
        return self._tokens()["INPUT_BG"]

    @property
    def border(self) -> str:
        return self._tokens()["BORDER_PRIMARY"]

    @property
    def border2(self) -> str:
        return self._tokens()["BORDER_SECONDARY"]

    @property
    def text(self) -> str:
        return self._tokens()["TEXT_PRIMARY"]

    @property
    def text2(self) -> str:
        return self._tokens()["TEXT_SECONDARY"]

    @property
    def text3(self) -> str:
        return self._tokens()["TEXT_MUTED"]

    @property
    def text4(self) -> str:
        return self._tokens()["TEXT_DISABLED"]

    @property
    def accent(self) -> str:
        return self._tokens()["ACCENT"]

    @property
    def accent2(self) -> str:
        return self._tokens()["ACCENT2"]

    @property
    def accent_bg(self) -> str:
        return self._tokens()["ACCENT_BG"]

    @property
    def green2(self) -> str:
        return self._tokens()["STATUS_SUCCESS"]

    @property
    def red(self) -> str:
        return self._tokens()["STATUS_ERROR"]

    @property
    def red2(self) -> str:
        return self._tokens()["STATUS_ERROR"]

    @property
    def amber(self) -> str:
        return self._tokens()["STATUS_WARNING"]

    @property
    def purple(self) -> str:
        return self._tokens()["STATUS_INFO"]

    @property
    def teal2(self) -> str:
        return self._tokens()["ACCENT2"]

    @property
    def overlay_low(self) -> str:
        return self._tokens()["OVERLAY_LOW"]

    @property
    def overlay_mid(self) -> str:
        return self._tokens()["OVERLAY_MID"]


T = ThemeValues()
