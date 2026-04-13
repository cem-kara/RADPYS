# -*- coding: utf-8 -*-
"""ui/pages/personel/fiili_hizmet_merkez_page.py - Fiili hizmet merkezi."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.logger import exc_logla
from ui.pages.placeholder import PlaceholderPage
from ui.styles import T


_TABS: tuple[tuple[str, str], ...] = (
    ("IZIN", "Izin Takip"),
    ("FHSZ", "FHSZ Yonetim"),
    ("PUANTAJ", "Puantaj Rapor"),
)


class FiiliHizmetMerkezPage(QWidget):
    """Izin, FHSZ ve puantaj ekranlarini tek merkezde yonetir."""

    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self._db = db
        self._modules: dict[str, QWidget] = {}
        self._tab_buttons: dict[str, QPushButton] = {}
        self._active_code = "IZIN"

        self.setStyleSheet(f"background:{T.bg0};")
        self._build()
        self._switch_tab(self._active_code)

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 14)
        root.setSpacing(12)

        root.addWidget(self._build_header())

        self._stack = QStackedWidget(self)
        root.addWidget(self._stack, 1)

    def _build_header(self) -> QWidget:
        host = QFrame(self)
        host.setStyleSheet(
            f"QFrame{{background:{T.bg1}; border:1px solid {T.border}; border-radius:{T.radius}px;}}"
        )
        lay = QVBoxLayout(host)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(8)

        top = QHBoxLayout()
        top.setSpacing(10)

        title = QLabel("Fiili Hizmet Merkezi")
        title.setStyleSheet(f"color:{T.text}; font-size:16px; font-weight:700;")
        subtitle = QLabel("Izin takip, FHSZ yonetim ve puantaj rapor islemleri")
        subtitle.setStyleSheet(f"color:{T.text2}; font-size:11px;")

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        top.addLayout(title_col)
        top.addStretch(1)
        lay.addLayout(top)

        nav = QHBoxLayout()
        nav.setSpacing(6)
        for code, label in _TABS:
            btn = QPushButton(label, self)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _=False, c=code: self._switch_tab(c))
            self._tab_buttons[code] = btn
            nav.addWidget(btn)
        nav.addStretch(1)

        lay.addLayout(nav)
        self._refresh_tab_button_styles()
        return host

    def _refresh_tab_button_styles(self) -> None:
        for code, btn in self._tab_buttons.items():
            active = code == self._active_code
            if active:
                btn.setStyleSheet(
                    f"QPushButton{{"
                    f"background:{T.bg3};"
                    f"color:{T.text};"
                    f"border:1px solid {T.accent};"
                    f"border-radius:7px;"
                    f"padding:6px 12px;"
                    f"font-size:11px;"
                    f"font-weight:700;"
                    f"}}"
                )
            else:
                btn.setStyleSheet(
                    f"QPushButton{{"
                    f"background:{T.bg2};"
                    f"color:{T.text2};"
                    f"border:1px solid {T.border};"
                    f"border-radius:7px;"
                    f"padding:6px 12px;"
                    f"font-size:11px;"
                    f"font-weight:600;"
                    f"}}"
                    f"QPushButton:hover{{"
                    f"color:{T.text};"
                    f"border-color:{T.border2};"
                    f"}}"
                )

    def _module_factory(self, code: str) -> Callable[[], QWidget]:
        if code == "IZIN":
            return lambda: self._safe_create("ui.pages.izin.izin_listesi", "IzinListesiPage")
        if code == "FHSZ":
            return lambda: self._safe_create("ui.pages.personel.fhsz_yonetim_page", "FhszYonetimPage")
        if code == "PUANTAJ":
            return lambda: self._safe_create("ui.pages.personel.puantaj_rapor_page", "PuantajRaporPage")
        return lambda: PlaceholderPage(self._db, self)

    def _safe_create(self, module_name: str, class_name: str) -> QWidget:
        try:
            mod = __import__(module_name, fromlist=[class_name])
            cls = getattr(mod, class_name)
            return cls(self._db, self)
        except Exception as exc:
            exc_logla("FiiliHizmetMerkezPage._safe_create", exc)
            return PlaceholderPage(self._db, self)

    def _switch_tab(self, code: str) -> None:
        if code not in dict(_TABS):
            return

        self._active_code = code
        self._refresh_tab_button_styles()

        if code not in self._modules:
            widget = self._module_factory(code)()
            self._modules[code] = widget
            self._stack.addWidget(widget)

        current = self._modules[code]
        self._stack.setCurrentWidget(current)

        load_data = getattr(current, "load_data", None)
        if callable(load_data):
            try:
                load_data()
            except Exception:
                pass
