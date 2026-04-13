# -*- coding: utf-8 -*-
"""ui/pages/personel/dozimetre_takip_page.py - Dozimetre olcum takip ekrani."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.logger import exc_logla
from app.services.dozimetre_service import DozimetreService
from ui.pages.personel.dozimetre_import_page import DozimetreImportPage
from ui.components import AlertBar, PrimaryButton
from ui.styles import T


class _StatKart(QFrame):
    def __init__(self, baslik: str, renk: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"QFrame{{background:{T.bg1}; border:1px solid {T.border}; border-radius:{T.radius}px;}}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(2)
        lbl = QLabel(baslik.upper())
        lbl.setStyleSheet(f"color:{T.text3}; font-size:10px; font-weight:700;")
        self._deger = QLabel("-")
        self._deger.setStyleSheet(f"color:{renk}; font-size:24px; font-weight:800;")
        lay.addWidget(lbl)
        lay.addWidget(self._deger)

    def set(self, value: str) -> None:
        self._deger.setText(str(value))


class DozimetreTakipPage(QWidget):
    """Dozimetre olcumlerinin merkezi izleme sayfasi."""

    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self._db = db
        self._svc = DozimetreService(db) if db is not None else None
        self._tum: list[dict] = []
        self.setStyleSheet(f"background:{T.bg0};")
        self._build()
        self.load_data()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 14)
        root.setSpacing(10)

        top = QHBoxLayout()
        lbl = QLabel("Dozimetre Takip")
        lbl.setStyleSheet(f"color:{T.text}; font-size:18px; font-weight:700;")
        top.addWidget(lbl)
        top.addStretch(1)
        self._btn_import = QPushButton("Yeni Donem Raporu")
        self._btn_import.clicked.connect(self._open_import)
        top.addWidget(self._btn_import)
        self._btn_yenile = PrimaryButton("Yenile")
        self._btn_yenile.clicked.connect(self.load_data)
        top.addWidget(self._btn_yenile)
        root.addLayout(top)

        self._alert = AlertBar(self)
        root.addWidget(self._alert)

        self._stats = self._build_stats()
        root.addWidget(self._stats)

        self._filters = self._build_filters()
        root.addWidget(self._filters)

        self._table = QTableWidget(self)
        self._table.setColumnCount(10)
        self._table.setHorizontalHeaderLabels(
            [
                "Ad Soyad",
                "TC",
                "Birim",
                "Yil",
                "Periyot",
                "Dozimetre No",
                "Hp10",
                "Hp007",
                "Durum",
                "Rapor No",
            ]
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self._table, 1)

        self._lbl_ozet = QLabel("")
        self._lbl_ozet.setStyleSheet(f"color:{T.text3}; font-size:11px;")
        root.addWidget(self._lbl_ozet)

    def _build_stats(self) -> QFrame:
        frm = QFrame(self)
        frm.setStyleSheet("background:transparent;")
        lay = QHBoxLayout(frm)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        self._k_toplam = _StatKart("Toplam Olcum", T.accent2)
        self._k_personel = _StatKart("Personel", T.teal2)
        self._k_rapor = _StatKart("Rapor", T.amber)
        self._k_max = _StatKart("Maks Hp10", T.text)
        self._k_uyari = _StatKart("Uyari", T.warning if hasattr(T, "warning") else "#e8a020")
        self._k_tehlike = _StatKart("Tehlike", T.red2)

        for k in (
            self._k_toplam,
            self._k_personel,
            self._k_rapor,
            self._k_max,
            self._k_uyari,
            self._k_tehlike,
        ):
            lay.addWidget(k)
        return frm

    def _build_filters(self) -> QFrame:
        frm = QFrame(self)
        frm.setStyleSheet(
            f"QFrame{{background:{T.bg1}; border:1px solid {T.border}; border-radius:{T.radius}px;}}"
        )
        lay = QGridLayout(frm)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setHorizontalSpacing(8)
        lay.setVerticalSpacing(6)

        self._yil = QComboBox(self)
        self._yil.addItem("Tum Yillar", None)
        self._yil.currentIndexChanged.connect(self._filtrele)

        self._periyot = QComboBox(self)
        self._periyot.addItem("Tum Periyotlar", None)
        self._periyot.currentIndexChanged.connect(self._filtrele)

        self._birim = QComboBox(self)
        self._birim.addItem("Tum Birimler", None)
        self._birim.currentIndexChanged.connect(self._filtrele)

        self._durum = QComboBox(self)
        self._durum.addItem("Tum Durumlar", None)
        self._durum.addItems(["Normal", "Uyari", "Tehlike"])
        self._durum.currentIndexChanged.connect(self._filtrele)

        self._ara = QLineEdit(self)
        self._ara.setPlaceholderText("Ad soyad, TC veya rapor no ara...")
        self._ara.textChanged.connect(self._filtrele)

        lay.addWidget(QLabel("Yil"), 0, 0)
        lay.addWidget(self._yil, 0, 1)
        lay.addWidget(QLabel("Periyot"), 0, 2)
        lay.addWidget(self._periyot, 0, 3)
        lay.addWidget(QLabel("Birim"), 0, 4)
        lay.addWidget(self._birim, 0, 5)
        lay.addWidget(QLabel("Durum"), 1, 0)
        lay.addWidget(self._durum, 1, 1)
        lay.addWidget(self._ara, 1, 2, 1, 4)
        return frm

    @staticmethod
    def _fmt_dose(value: float | None) -> str:
        return "" if value is None else f"{value:.3f}"

    def load_data(self) -> None:
        if self._svc is None:
            return
        try:
            self._tum = self._svc.tum_olcumler()
            self._doldur_filterler()
            self._filtrele()
        except Exception as exc:
            exc_logla("DozimetreTakipPage.load_data", exc)
            self._alert.goster(str(exc), "danger")

    def _doldur_filterler(self) -> None:
        yillar = sorted({int(r.get("yil") or 0) for r in self._tum if int(r.get("yil") or 0) > 0}, reverse=True)
        periyotlar = sorted({int(r.get("periyot") or 0) for r in self._tum if int(r.get("periyot") or 0) > 0})
        birimler = sorted({str(r.get("birim") or "") for r in self._tum if str(r.get("birim") or "").strip()})

        self._yil.blockSignals(True)
        self._yil.clear()
        self._yil.addItem("Tum Yillar", None)
        for y in yillar:
            self._yil.addItem(str(y), y)
        self._yil.blockSignals(False)

        self._periyot.blockSignals(True)
        self._periyot.clear()
        self._periyot.addItem("Tum Periyotlar", None)
        for p in periyotlar:
            self._periyot.addItem(str(p), p)
        self._periyot.blockSignals(False)

        self._birim.blockSignals(True)
        self._birim.clear()
        self._birim.addItem("Tum Birimler", None)
        for b in birimler:
            self._birim.addItem(b, b)
        self._birim.blockSignals(False)

    def _filtrele(self) -> None:
        yil = self._yil.currentData()
        periyot = self._periyot.currentData()
        birim = self._birim.currentData()
        durum = self._durum.currentText().strip()
        ara = self._ara.text().strip().lower()

        rows: list[dict] = []
        for r in self._tum:
            if yil is not None and int(r.get("yil") or 0) != int(yil):
                continue
            if periyot is not None and int(r.get("periyot") or 0) != int(periyot):
                continue
            if birim and str(r.get("birim") or "") != str(birim):
                continue
            if durum != "Tum Durumlar" and str(r.get("durum") or "") != durum:
                continue
            if ara:
                haystack = " ".join(
                    [
                        str(r.get("ad_soyad") or "").lower(),
                        str(r.get("tc_kimlik") or "").lower(),
                        str(r.get("rapor_no") or "").lower(),
                    ]
                )
                if ara not in haystack:
                    continue
            rows.append(r)

        stats = self._svc.istatistikler(rows) if self._svc else {}
        self._k_toplam.set(str(stats.get("toplam", 0)))
        self._k_personel.set(str(stats.get("personel", 0)))
        self._k_rapor.set(str(stats.get("rapor", 0)))
        max_hp10 = stats.get("max_hp10")
        self._k_max.set(self._fmt_dose(max_hp10) if max_hp10 is not None else "-")
        self._k_uyari.set(str(stats.get("uyari", 0)))
        self._k_tehlike.set(str(stats.get("tehlike", 0)))

        self._table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            vals = [
                r.get("ad_soyad", ""),
                r.get("tc_kimlik", ""),
                r.get("birim", ""),
                r.get("yil", ""),
                r.get("periyot", ""),
                r.get("dozimetre_no", ""),
                self._fmt_dose(r.get("hp10")),
                self._fmt_dose(r.get("hp007")),
                r.get("durum", ""),
                r.get("rapor_no", ""),
            ]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(str(v))
                it.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                if c >= 3:
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if c in {6, 7}:
                    hp_val = r.get("hp10") if c == 6 else r.get("hp007")
                    if hp_val is not None:
                        if float(hp_val) >= 5.0:
                            it.setForeground(QColor(T.red2))
                        elif float(hp_val) >= 2.0:
                            it.setForeground(QColor(T.warning if hasattr(T, "warning") else "#e8a020"))
                        else:
                            it.setForeground(QColor(T.teal2))

                if c == 8:
                    d = str(r.get("durum") or "")
                    if d == "Tehlike":
                        it.setForeground(QColor(T.red2))
                    elif d == "Uyari":
                        it.setForeground(QColor(T.warning if hasattr(T, "warning") else "#e8a020"))
                    elif d == "Normal":
                        it.setForeground(QColor(T.teal2))

                self._table.setItem(i, c, it)

        self._lbl_ozet.setText(f"Toplam {len(rows)} kayit")

    def _open_import(self) -> None:
        dlg = QDialog(self)
        dlg.setWindowTitle("Dozimetre Raporu Ice Aktar")
        dlg.resize(1100, 700)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(DozimetreImportPage(db=self._db, parent=dlg))
        dlg.finished.connect(self.load_data)
        dlg.exec()
