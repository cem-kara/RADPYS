# -*- coding: utf-8 -*-
"""Ortak belge sekmesi widget'i."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
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
from app.services.dokuman_service import DokumanService
from ui.components.alerts import AlertBar
from ui.styles import T


class BelgeSekmesi(QWidget):
    """Belge yukleme/listeleme/silme akisinin ortak UI parcasi."""

    def __init__(self, db, entity_turu: str, entity_id: str = "", klasor_adi: str = "", parent=None):
        super().__init__(parent)
        self._svc = DokumanService(db)
        self._entity_turu = entity_turu
        self._entity_id = entity_id
        self._klasor_adi = klasor_adi
        self._dosya_yolu = ""
        self._build()
        self._load_turler()
        self.yenile()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        self._alert = AlertBar(self)
        root.addWidget(self._alert)

        card = QFrame(self)
        card.setStyleSheet(
            f"QFrame{{background:{T.bg1};border:1px solid {T.border};border-radius:{T.radius}px;}}"
        )
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        top = QHBoxLayout()
        top.setSpacing(6)

        self._tur = QLineEdit()
        self._tur.setPlaceholderText("Belge Turu")
        top.addWidget(QLabel("Tur:"))
        top.addWidget(self._tur, 2)

        self._aciklama = QLineEdit()
        self._aciklama.setPlaceholderText("Aciklama")
        top.addWidget(QLabel("Aciklama:"))
        top.addWidget(self._aciklama, 3)

        self._btn_sec = QPushButton("Dosya Sec")
        self._btn_sec.clicked.connect(self._dosya_sec)
        top.addWidget(self._btn_sec)

        self._btn_yukle = QPushButton("Yukle")
        self._btn_yukle.clicked.connect(self._yukle)
        top.addWidget(self._btn_yukle)

        lay.addLayout(top)

        self._lbl_dosya = QLabel("Dosya secilmedi")
        self._lbl_dosya.setStyleSheet(f"color:{T.text3};")
        lay.addWidget(self._lbl_dosya)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["ID", "Tur", "Dosya", "Yuklendi"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setColumnHidden(0, True)
        lay.addWidget(self._table)

        foot = QHBoxLayout()
        foot.addStretch()
        self._btn_sil = QPushButton("Secili Belgeyi Sil")
        self._btn_sil.clicked.connect(self._sil)
        foot.addWidget(self._btn_sil)
        lay.addLayout(foot)

        root.addWidget(card)
        self._set_entity_ready(bool(self._entity_id))

    def _load_turler(self) -> None:
        try:
            turler = self._svc.belge_turleri()
            if turler and not self._tur.text().strip():
                self._tur.setText(turler[0])
        except Exception as exc:
            exc_logla("BelgeSekmesi._load_turler", exc)

    def set_entity(self, entity_turu: str, entity_id: str, klasor_adi: str = "") -> None:
        self._entity_turu = entity_turu
        self._entity_id = entity_id
        self._klasor_adi = klasor_adi
        self._set_entity_ready(bool(entity_id))
        self.yenile()

    def _set_entity_ready(self, ready: bool) -> None:
        self._btn_sec.setEnabled(ready)
        self._btn_yukle.setEnabled(ready)
        self._btn_sil.setEnabled(ready)
        if not ready:
            self._alert.goster("Belgeler icin once kayit olusturun.", "info")
        else:
            self._alert.temizle()

    def _dosya_sec(self) -> None:
        fp, _ = QFileDialog.getOpenFileName(self, "Belge Sec", "", "Tum Dosyalar (*.*)")
        if not fp:
            return
        self._dosya_yolu = fp
        self._lbl_dosya.setText(fp)

    def _yukle(self) -> None:
        if not self._entity_id:
            self._alert.goster("Once kaydi tamamlayin.", "warning")
            return
        tur = self._tur.text().strip()
        if not tur:
            self._alert.goster("Belge turu zorunlu.", "warning")
            return
        if not self._dosya_yolu:
            self._alert.goster("Yuklenecek dosyayi secin.", "warning")
            return

        try:
            self._svc.yukle(
                file_path=self._dosya_yolu,
                entity_turu=self._entity_turu,
                entity_id=self._entity_id,
                tur=tur,
                aciklama=self._aciklama.text().strip(),
                klasor_adi=self._klasor_adi,
            )
            self._dosya_yolu = ""
            self._lbl_dosya.setText("Dosya secilmedi")
            self._aciklama.clear()
            self.yenile()
            self._alert.goster("Belge yuklendi.", "success")
        except Exception as exc:
            exc_logla("BelgeSekmesi._yukle", exc)
            self._alert.goster(str(exc), "danger")

    def _sil(self) -> None:
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            self._alert.goster("Silmek icin bir kayit secin.", "warning")
            return
        belge_id = self._table.item(rows[0].row(), 0).text()
        try:
            self._svc.sil(belge_id)
            self.yenile()
            self._alert.goster("Belge silindi.", "success")
        except Exception as exc:
            exc_logla("BelgeSekmesi._sil", exc)
            self._alert.goster(str(exc), "danger")

    def yenile(self) -> None:
        self._table.setRowCount(0)
        if not self._entity_id:
            return

        try:
            rows = self._svc.listele(self._entity_turu, self._entity_id)
        except Exception as exc:
            exc_logla("BelgeSekmesi.yenile", exc)
            self._alert.goster(str(exc), "danger")
            return

        for r in rows:
            row_no = self._table.rowCount()
            self._table.insertRow(row_no)
            self._table.setItem(row_no, 0, QTableWidgetItem(str(r.get("id") or "")))
            self._table.setItem(row_no, 1, QTableWidgetItem(str(r.get("tur") or "")))
            self._table.setItem(row_no, 2, QTableWidgetItem(str(r.get("dosya_adi") or "")))
            self._table.setItem(row_no, 3, QTableWidgetItem(str(r.get("yuklendi") or "")))

        self._table.resizeColumnsToContents()
        self._table.horizontalHeader().setStretchLastSection(True)
