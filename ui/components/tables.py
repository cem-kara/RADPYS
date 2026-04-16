# -*- coding: utf-8 -*-
"""ui/components/tables.py �?" Standart veri tablosu"""
from __future__ import annotations
from PySide6.QtWidgets import (
    QTableView, QAbstractItemView, QHeaderView,
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PySide6.QtGui import QColor
from ui.styles import T


class _TableModel(QAbstractTableModel):
    """
    list[dict] veriyi QTableView'a ba�Ylayan model.

    Kullanım:
        model = _TableModel(
            kolonlar=[("id", "ID", 60), ("ad", "Ad Soyad", 200)],
            veri=[{"id": "x1", "ad": "Ali Kaya"}],
        )
    """

    def __init__(self, kolonlar: list[tuple], parent=None):
        """
        kolonlar: [(key, baslik, genislik), ...]
        """
        super().__init__(parent)
        self._kolonlar = kolonlar
        self._veri: list[dict] = []

    def set_veri(self, veri: list[dict]) -> None:
        self.beginResetModel()
        self._veri = veri or []
        self.endResetModel()

    def get_satir(self, row: int) -> dict | None:
        if 0 <= row < len(self._veri):
            return self._veri[row]
        return None

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._veri)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self._kolonlar)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self._kolonlar[section][1]
        return str(section + 1)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row  = self._veri[index.row()]
        key  = self._kolonlar[index.column()][0]
        deger = row.get(key)

        if role == Qt.ItemDataRole.DisplayRole:
            return self._display(key, deger, row)

        if role == Qt.ItemDataRole.ForegroundRole:
            renk = self._foreground(key, deger, row)
            return QColor(renk) if renk else None

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return self._alignment(key)

        return None

    def _display(self, key: str, deger, row: dict) -> str:
        """Subclass'ta override edilebilir."""
        if deger is None:
            return ""
        return str(deger)

    def _foreground(self, key: str, deger, row: dict) -> str | None:
        """Subclass'ta override edilebilir �?" renk kodu veya None."""
        return None

    def _alignment(self, key: str) -> int:
        return int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)


class DataTable(QTableView):
    """
    Standart veri tablosu.

    Kullanım:
        tablo = DataTable()
        tablo.kur_kolonlar([("tc_kimlik","TC",120),("ad","Ad",200)])
        tablo.set_veri([{"tc_kimlik":"...","ad":"..."}])
        satir = tablo.secili_satir()
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model  = _TableModel([])
        self._proxy  = QSortFilterProxyModel(self)
        self._proxy.setSourceModel(self._model)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setFilterKeyColumn(-1)  # Tüm kolonlarda ara
        self.setModel(self._proxy)

        # Görünüm
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setHighlightSections(False)
        self.setSortingEnabled(True)
        self.setWordWrap(False)
        self.verticalHeader().setDefaultSectionSize(36)

    def kur_kolonlar(self, kolonlar: list[tuple],
                     geren: int | str = -1) -> None:
        """
        Kolonları ayarla ve geni�Ylikleri uygula.

        kolonlar: [(key, baslik, genislik), ...]
        geren: Bu indeksteki kolon kalan alanı doldurur (-1 = son kolon)
        """
        self._model = _TableModel(kolonlar)
        self._proxy.setSourceModel(self._model)
        hdr = self.horizontalHeader()

        for i, (_, _, genislik) in enumerate(kolonlar):
            if genislik > 0:
                self.setColumnWidth(i, genislik)
                hdr.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)

        idx = geren if isinstance(geren, int) else \
              next((i for i, (k,_,__) in enumerate(kolonlar)
                    if k == geren), len(kolonlar)-1)
        if 0 <= idx < len(kolonlar):
            hdr.setSectionResizeMode(idx, QHeaderView.ResizeMode.Stretch)

    def set_veri(self, veri: list[dict]) -> None:
        self._model.set_veri(veri)

    def ara(self, metin: str) -> None:
        self._proxy.setFilterFixedString(metin)

    def secili_satir(self) -> dict | None:
        idx = self.currentIndex()
        if not idx.isValid():
            return None
        kaynak = self._proxy.mapToSource(idx)
        return self._model.get_satir(kaynak.row())

    def secili_satir_index(self) -> int:
        idx = self.currentIndex()
        if not idx.isValid():
            return -1
        return self._proxy.mapToSource(idx).row()


