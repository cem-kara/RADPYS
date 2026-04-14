# -*- coding: utf-8 -*-
"""Toplu import merkezi iskeleti."""
from __future__ import annotations

from PySide6.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget

from ui.pages.imports.devir_import_page import DevirImportPage
from ui.pages.imports.izin_import_page import IzinImportPage
from ui.pages.imports.personel_import_page import PersonelImportPage


class ImportCenterPage(QWidget):
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self._db = db
        self._kur_ui()

    def _kur_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget(self)
        tabs.addTab(PersonelImportPage(db=self._db), "Personel")
        tabs.addTab(IzinImportPage(db=self._db), "Izin")
        tabs.addTab(DevirImportPage(db=self._db), "Izin Devir / Bakiye")

        placeholder = QWidget(self)
        p_lay = QVBoxLayout(placeholder)
        p_lay.addWidget(QLabel("Diger import sekmeleri ikinci adimda eklenecek."))
        tabs.addTab(placeholder, "Yakinda")

        root.addWidget(tabs)
