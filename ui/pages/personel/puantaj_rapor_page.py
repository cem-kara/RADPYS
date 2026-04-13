# -*- coding: utf-8 -*-
"""ui/pages/personel/puantaj_rapor_page.py - Puantaj rapor sayfasi."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QCursor
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.logger import exc_logla
from app.services.fhsz_service import FhszService
from ui.components import AlertBar, DangerButton, PrimaryButton, SuccessButton
from ui.styles import T


_COLS = [
    "Kimlik No",
    "Adi Soyadi",
    "Yil",
    "Donem",
    "Top. Gun",
    "Top. Izin",
    "Fiili Saat",
    "Kumulatif Saat",
    "Hak Edilen Sua",
]

_AY_ISIMLERI = [
    "Ocak",
    "Subat",
    "Mart",
    "Nisan",
    "Mayis",
    "Haziran",
    "Temmuz",
    "Agustos",
    "Eylul",
    "Ekim",
    "Kasim",
    "Aralik",
]


class PuantajRaporPage(QWidget):
    """FHSZ tablosundan yil/donem bazli puantaj rapor uretir."""

    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self._svc = FhszService(db)
        self._rapor_data: list[dict] = []
        self.setStyleSheet(f"background:{T.bg0};")
        self._build()

    def _build(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 12, 20, 12)
        main.setSpacing(10)

        self._alert = AlertBar(self)
        main.addWidget(self._alert)

        bar = QFrame(self)
        bar.setStyleSheet(
            f"QFrame{{background:{T.bg1}; border:1px solid {T.border}; border-radius:{T.radius}px;}}"
        )
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(12, 8, 12, 8)
        bl.setSpacing(8)

        bl.addWidget(self._mk_label("Rapor Yili:"))
        self._yil = QComboBox(self)
        by = datetime.now().year
        for y in range(by - 5, by + 5):
            self._yil.addItem(str(y), y)
        self._yil.setCurrentText(str(by))
        bl.addWidget(self._yil)

        bl.addWidget(self._mk_label("Donem:"))
        self._donem = QComboBox(self)
        self._donem.addItem("Tumu", None)
        for d, ay_adi in enumerate(_AY_ISIMLERI, 1):
            self._donem.addItem(ay_adi, d)
        bl.addWidget(self._donem)

        bl.addStretch(1)
        self._btn_getir = PrimaryButton("Raporu Olustur")
        self._btn_getir.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._btn_getir.clicked.connect(self._rapor_olustur)
        bl.addWidget(self._btn_getir)

        main.addWidget(bar)

        self._lbl_bilgi = QLabel("Veri bekleniyor...")
        self._lbl_bilgi.setStyleSheet(f"color:{T.text3}; font-size:11px;")
        self._lbl_bilgi.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        main.addWidget(self._lbl_bilgi)

        self._tablo = QTableWidget(self)
        self._tablo.setColumnCount(len(_COLS))
        self._tablo.setHorizontalHeaderLabels(_COLS)
        self._tablo.verticalHeader().setVisible(False)
        self._tablo.setAlternatingRowColors(True)
        self._tablo.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tablo.horizontalHeader().setStretchLastSection(True)
        main.addWidget(self._tablo, 1)

        bot = QFrame(self)
        bot.setStyleSheet(
            f"QFrame{{background:{T.bg1}; border:1px solid {T.border}; border-radius:{T.radius}px;}}"
        )
        bo = QHBoxLayout(bot)
        bo.setContentsMargins(12, 8, 12, 8)
        bo.setSpacing(12)

        self._lbl_durum = QLabel("Hazir")
        self._lbl_durum.setStyleSheet(f"color:{T.text3}; font-size:11px;")
        bo.addWidget(self._lbl_durum)
        bo.addStretch(1)

        self._progress = QProgressBar(self)
        self._progress.setRange(0, 0)
        self._progress.setVisible(False)
        self._progress.setFixedWidth(150)
        bo.addWidget(self._progress)

        self._btn_excel = SuccessButton("Excel Indir")
        self._btn_excel.setEnabled(False)
        self._btn_excel.clicked.connect(self._excel_indir)
        bo.addWidget(self._btn_excel)

        self._btn_pdf = DangerButton("PDF Indir")
        self._btn_pdf.setEnabled(False)
        self._btn_pdf.clicked.connect(self._pdf_indir)
        bo.addWidget(self._btn_pdf)

        main.addWidget(bot)

    def _mk_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{T.text2}; font-size:11px;")
        return lbl

    def load_data(self):
        self._rapor_olustur()

    def _rapor_olustur(self) -> None:
        self._alert.temizle()
        self._tablo.setRowCount(0)
        self._rapor_data = []

        yil = int(self._yil.currentData())
        donem = self._donem.currentData()

        self._btn_getir.setEnabled(False)
        self._progress.setVisible(True)
        self._lbl_durum.setText("Rapor hazirlaniyor...")

        try:
            rows = self._svc.puantaj_rapor_uret(yil=yil, donem=donem)
            self._rapor_data = rows
            self._tablo.setRowCount(len(rows))

            for i, r in enumerate(rows):
                vals = [
                    r.get("tc_kimlik", ""),
                    r.get("ad_soyad", ""),
                    r.get("yil", ""),
                    self._donem_metni(r.get("donem", "")),
                    int(r.get("aylik_gun", 0)),
                    int(r.get("izin_gun", 0)),
                    f"{float(r.get('fiili_saat', 0)):.0f}",
                    f"{float(r.get('kumulatif_saat', 0)):.0f}",
                    int(r.get("sua_hak_edis", 0)),
                ]
                for c, v in enumerate(vals):
                    item = QTableWidgetItem(str(v))
                    item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                    if c >= 2:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if str(r.get("donem", "")) == "Toplam":
                        item.setBackground(QColor(T.bg3))
                    self._tablo.setItem(i, c, item)

            donem_txt = self._donem.currentText()
            self._lbl_bilgi.setText(f"{len(rows)} kayit  •  {donem_txt}  •  {yil}")
            self._lbl_durum.setText(f"Rapor hazir - {len(rows)} satir")
            self._btn_excel.setEnabled(len(rows) > 0)
            self._btn_pdf.setEnabled(len(rows) > 0)
        except Exception as exc:
            exc_logla("PuantajRaporPage._rapor_olustur", exc)
            self._alert.goster(str(exc), "danger")
            self._lbl_bilgi.setText("Hata olustu.")
            self._lbl_durum.setText("Hazir")
            self._btn_excel.setEnabled(False)
            self._btn_pdf.setEnabled(False)
        finally:
            self._btn_getir.setEnabled(True)
            self._progress.setVisible(False)

    def _excel_indir(self) -> None:
        if not self._rapor_data:
            return

        yil = self._yil.currentText()
        donem = self._donem.currentText().replace(" ", "_")
        default_name = f"FHSZ_Puantaj_Rapor_{yil}_{donem}.xlsx"
        path, _ = QFileDialog.getSaveFileName(self, "Excel Kaydet", default_name, "Excel Dosyasi (*.xlsx)")
        if not path:
            return

        try:
            import openpyxl
            from openpyxl.styles import Alignment, Font

            wb = openpyxl.Workbook()
            ws = wb.active
            if ws is None:
                raise RuntimeError("Excel sayfasi olusturulamadi")
            ws.title = "Puantaj Rapor"
            ws.append(_COLS)

            for r in self._rapor_data:
                ws.append(
                    [
                        r.get("tc_kimlik", ""),
                        r.get("ad_soyad", ""),
                        r.get("yil", ""),
                        r.get("donem", ""),
                        int(r.get("aylik_gun", 0)),
                        int(r.get("izin_gun", 0)),
                        int(float(r.get("fiili_saat", 0))),
                        int(float(r.get("kumulatif_saat", 0))),
                        int(r.get("sua_hak_edis", 0)),
                    ]
                )

            for cell in ws[1]:
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal="center")

            wb.save(path)
            self._lbl_durum.setText(f"Excel kaydedildi: {Path(path).name}")
            self._alert.goster("Excel dosyasi kaydedildi.", "success")
        except ImportError:
            self._alert.goster("openpyxl modulu yuklu degil.", "warning")
        except Exception as exc:
            exc_logla("PuantajRaporPage._excel_indir", exc)
            self._alert.goster(str(exc), "danger")

    def _pdf_indir(self) -> None:
        if not self._rapor_data:
            return

        yil = self._yil.currentText()
        donem = self._donem.currentText().replace(" ", "_")
        default_name = f"FHSZ_Puantaj_Rapor_{yil}_{donem}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", default_name, "PDF Dosyasi (*.pdf)")
        if not path:
            return

        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

            data = [_COLS]
            for r in self._rapor_data:
                data.append(
                    [
                        str(r.get("tc_kimlik", "")),
                        str(r.get("ad_soyad", "")),
                        str(r.get("yil", "")),
                        str(r.get("donem", "")),
                        str(int(r.get("aylik_gun", 0))),
                        str(int(r.get("izin_gun", 0))),
                        str(int(float(r.get("fiili_saat", 0)))),
                        str(int(float(r.get("kumulatif_saat", 0)))),
                        str(int(r.get("sua_hak_edis", 0))),
                    ]
                )

            doc = SimpleDocTemplate(path, pagesize=landscape(A4))
            tbl = Table(data, repeatRows=1)
            tbl.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D75FE")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ]
                )
            )
            doc.build([tbl])
            self._lbl_durum.setText(f"PDF kaydedildi: {Path(path).name}")
            self._alert.goster("PDF dosyasi kaydedildi.", "success")
        except ImportError:
            self._alert.goster("reportlab modulu yuklu degil.", "warning")
        except Exception as exc:
            exc_logla("PuantajRaporPage._pdf_indir", exc)
            self._alert.goster(str(exc), "danger")

    @staticmethod
    def _donem_metni(donem) -> str:
        if isinstance(donem, int) and 1 <= donem <= 12:
            return _AY_ISIMLERI[donem - 1]
        return str(donem)
