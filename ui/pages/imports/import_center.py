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

        rehber = QWidget(self)
        r_lay = QVBoxLayout(rehber)
        bilgi = QLabel(
            "Standart Import Akisi:\n"
            "1) Excel/CSV dosyasini sec\n"
            "2) Sutun eslestirmeyi kontrol et\n"
            "3) Onizle ve aktar\n"
            "4) Hata varsa: Hata Dosyasi Kaydet veya Hatali Kayitlari Duzenle\n"
            "5) Duzeltme dosyasi tekrar yuklendiginda sistem guncelle/ekle moduna gecer"
        )
        bilgi.setWordWrap(True)
        r_lay.addWidget(bilgi)
        r_lay.addStretch(1)
        tabs.addTab(rehber, "Import Rehberi")

        root.addWidget(tabs)
