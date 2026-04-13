# -*- coding: utf-8 -*-
"""Import sayfalari icin ortak iskelet UI."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.excel_import_service import ExcelImportService, ImportKonfig
from ui.components import AlertBar
from ui.styles import T


class BaseImportPage(QWidget):
    """Excel import akisinin temel 4 adimli iskeleti."""

    def __init__(self, db, kaydeden: str = "", parent=None):
        super().__init__(parent)
        self._db = db
        self._kaydeden = kaydeden
        self._svc = ExcelImportService()
        self._konfig_obj = self._konfig()

        self._df = None
        self._harita: dict[str, str] = {}
        self._dosya_yolu: Optional[str] = None
        self._onizleme_satirlari = []
        self._esleme_combo: dict[str, QComboBox] = {}

        self._kur_ui()

    def _konfig(self) -> ImportKonfig:
        raise NotImplementedError

    def _kur_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        lbl = QLabel(self._konfig_obj.baslik)
        lbl.setStyleSheet(f"color:{T.text}; font-size:16px; font-weight:700;")
        root.addWidget(lbl)

        adim = QFrame(self)
        adim_lay = QHBoxLayout(adim)
        adim_lay.setContentsMargins(10, 6, 10, 6)
        adim_lay.setSpacing(8)
        adim.setStyleSheet(
            f"QFrame{{background:{T.bg1}; border:1px solid {T.border}; border-radius:{T.radius}px;}}"
        )
        adim_lay.addWidget(QLabel("1) Dosya Sec"))
        adim_lay.addWidget(QLabel("-> 2) Eslestir"))
        adim_lay.addWidget(QLabel("-> 3) Onizle"))
        adim_lay.addWidget(QLabel("-> 4) Ice Aktar"))
        adim_lay.addStretch(1)
        root.addWidget(adim)

        self._alert = AlertBar(self)
        root.addWidget(self._alert)

        btn_lay = QHBoxLayout()
        self._lbl_dosya = QLabel("Dosya secilmedi")
        self._lbl_dosya.setStyleSheet(f"color:{T.text3};")

        self._btn_sec = QPushButton("Dosya Sec")
        self._btn_sec.clicked.connect(self._dosya_sec)

        self._btn_onizle = QPushButton("Onizle")
        self._btn_onizle.setEnabled(False)
        self._btn_onizle.clicked.connect(self._onizle)

        self._btn_aktar = QPushButton("Ice Aktar")
        self._btn_aktar.setEnabled(False)
        self._btn_aktar.clicked.connect(self._aktar)

        btn_lay.addWidget(self._lbl_dosya, 1)
        btn_lay.addWidget(self._btn_sec)
        btn_lay.addWidget(self._btn_onizle)
        btn_lay.addWidget(self._btn_aktar)
        root.addLayout(btn_lay)

        self._esleme_kart = QFrame(self)
        self._esleme_kart.setStyleSheet(
            f"QFrame{{background:{T.bg1}; border:1px solid {T.border}; border-radius:{T.radius}px;}}"
        )
        esleme_root = QVBoxLayout(self._esleme_kart)
        esleme_root.setContentsMargins(10, 10, 10, 10)
        esleme_root.setSpacing(8)
        esleme_root.addWidget(QLabel("Sutun Eslestirme"))

        self._esleme_scroll = QScrollArea(self._esleme_kart)
        self._esleme_scroll.setWidgetResizable(True)
        self._esleme_wrap = QWidget(self._esleme_scroll)
        self._esleme_grid = QGridLayout(self._esleme_wrap)
        self._esleme_grid.setContentsMargins(0, 0, 0, 0)
        self._esleme_grid.setHorizontalSpacing(10)
        self._esleme_grid.setVerticalSpacing(6)
        self._esleme_scroll.setWidget(self._esleme_wrap)
        esleme_root.addWidget(self._esleme_scroll)

        self._esleme_kart.hide()
        root.addWidget(self._esleme_kart)

        self._tablo = QTableWidget(self)
        self._tablo.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tablo.setAlternatingRowColors(True)
        self._tablo.verticalHeader().setVisible(False)
        self._tablo.setColumnCount(0)
        root.addWidget(self._tablo, 1)

        self._lbl_ozet = QLabel("")
        self._lbl_ozet.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._lbl_ozet.setStyleSheet(f"color:{T.text3};")
        root.addWidget(self._lbl_ozet)

    def _dosya_sec(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Excel Dosyasi Sec",
            "",
            "Excel Dosyalari (*.xlsx *.xls);;Tum Dosyalar (*)",
        )
        if not path:
            return

        self._alert.temizle()
        self._dosya_yolu = path
        self._lbl_dosya.setText(path)
        self._btn_aktar.setEnabled(False)
        self._dosya_hazirla()

    def _dosya_hazirla(self) -> None:
        if not self._dosya_yolu:
            return
        try:
            self._df = self._svc.excel_oku(self._dosya_yolu)
            self._esleme_kur(list(self._df.columns))
            self._btn_onizle.setEnabled(True)
            self._alert.goster("Dosya yuklendi. Eslestirmeyi kontrol edip Onizle'ye basin.", "info")
        except Exception as exc:
            self._btn_onizle.setEnabled(False)
            self._esleme_kart.hide()
            self._alert.goster(str(exc), "danger")

    def _esleme_kur(self, kolonlar: list[str]) -> None:
        while self._esleme_grid.count():
            item = self._esleme_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self._esleme_combo.clear()
        otomatik = self._svc.sutun_haritasi_olustur(kolonlar, self._konfig_obj)

        self._esleme_grid.addWidget(QLabel("Uygulama Alani"), 0, 0)
        self._esleme_grid.addWidget(QLabel("Excel Kolonu"), 0, 1)
        row_idx = 1

        for alan in self._konfig_obj.alanlar:
            ad_lbl = QLabel(f"{alan.etiket} ({alan.ad})")
            cmb = QComboBox(self)
            cmb.addItem("(Atla)", "")
            for col in kolonlar:
                cmb.addItem(str(col), str(col))

            secilen = otomatik.get(alan.ad, "")
            pos = cmb.findData(secilen)
            cmb.setCurrentIndex(pos if pos >= 0 else 0)

            self._esleme_grid.addWidget(ad_lbl, row_idx, 0)
            self._esleme_grid.addWidget(cmb, row_idx, 1)
            self._esleme_combo[alan.ad] = cmb
            row_idx += 1

        self._esleme_kart.show()

    def _secili_harita(self) -> dict[str, str]:
        harita: dict[str, str] = {}
        for alan in self._konfig_obj.alanlar:
            cmb = self._esleme_combo.get(alan.ad)
            if cmb is None:
                continue
            secilen = str(cmb.currentData() or "").strip()
            if secilen:
                harita[alan.ad] = secilen
        return harita

    def _zorunlu_harita_kontrol(self, harita: dict[str, str]) -> str:
        eksik: list[str] = []
        for alan in self._konfig_obj.alanlar:
            if not alan.zorunlu:
                continue
            if alan.varsayilan is not None:
                continue
            if alan.ad not in harita:
                eksik.append(alan.etiket)
        return ", ".join(eksik)

    def _onizle(self) -> None:
        if self._df is None:
            return

        try:
            self._harita = self._secili_harita()
            eksik = self._zorunlu_harita_kontrol(self._harita)
            if eksik:
                self._alert.goster(f"Zorunlu alan eslestirmesi eksik: {eksik}", "warning")
                return

            self._onizleme_satirlari = self._svc.satir_onizleme(self._df, self._harita, self._konfig_obj)
            self._tablo_doldur()
            self._btn_aktar.setEnabled(True)
            self._alert.goster("Onizleme hazirlandi.", "success")
        except Exception as exc:
            self._alert.goster(str(exc), "danger")

    def _tablo_doldur(self) -> None:
        alanlar = [a.ad for a in self._konfig_obj.alanlar]
        self._tablo.setColumnCount(len(alanlar) + 2)
        self._tablo.setHorizontalHeaderLabels(["Satir", *alanlar, "Durum"])

        satirlar = self._onizleme_satirlari[:200]
        self._tablo.setRowCount(len(satirlar))
        for r, satir in enumerate(satirlar):
            self._tablo.setItem(r, 0, QTableWidgetItem(str(satir.satir_no)))
            for c, alan in enumerate(alanlar, start=1):
                self._tablo.setItem(r, c, QTableWidgetItem(str(satir.veri.get(alan, ""))))
            durum = "OK" if satir.basarili else satir.hata_mesaji
            self._tablo.setItem(r, len(alanlar) + 1, QTableWidgetItem(durum))

        toplam = len(self._onizleme_satirlari)
        hatali = len([s for s in self._onizleme_satirlari if not s.basarili])
        self._lbl_ozet.setText(f"Onizleme: toplam={toplam} hatali={hatali}")

    def _aktar(self) -> None:
        if self._df is None:
            return
        try:
            sonuc = self._svc.import_et(self._df, self._harita, self._konfig_obj, self._db)
            tur = "success" if sonuc.hatali == 0 else "warning"
            self._alert.goster(
                f"Aktarim tamamlandi. Basarili={sonuc.basarili}, Hatali={sonuc.hatali}",
                tur,
            )
        except Exception as exc:
            self._alert.goster(str(exc), "danger")
