# -*- coding: utf-8 -*-
"""ui/components/forms.py — Form alanı bileşenleri"""
from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QComboBox, QTextEdit,
)
from PySide6.QtCore import Qt
from ui.theme import T


class FormRow(QWidget):
    """
    Etiket + input çifti. Standart form satırı.

    Kullanım:
        row = FormRow("Ad Soyad", QLineEdit())
        row = FormRow("Durum", QComboBox(), zorunlu=True)
    """

    def __init__(self, etiket: str, widget: QWidget,
                 zorunlu: bool = False, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        lbl = QLabel(etiket + (" *" if zorunlu else ""))
        lbl.setFixedWidth(160)
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lbl.setStyleSheet(
            f"color:{'#e6edf3' if zorunlu else T.text_secondary};"
            f"font-size:12px;"
        )

        lay.addWidget(lbl)
        lay.addWidget(widget, 1)
        self.input = widget


class SearchBar(QLineEdit):
    """Arama kutusu — büyüteç ikonu, temizle butonu."""

    def __init__(self, placeholder: str = "Ara…", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setClearButtonEnabled(True)
        self.setMinimumWidth(220)


class LookupCombo(QComboBox):
    """
    Lookup tablosundan değer listeleyen combobox.
    Sprint 2'de servis entegrasyonu eklenecek.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(False)

    def doldur(self, degerler: list[str], bos_secim: bool = True) -> None:
        self.clear()
        if bos_secim:
            self.addItem("— Seçiniz —", "")
        for d in degerler:
            self.addItem(d, d)

    def secili_deger(self) -> str:
        return self.currentData() or ""
