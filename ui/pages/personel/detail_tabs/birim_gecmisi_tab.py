# -*- coding: utf-8 -*-
"""Personel detay penceresi icin birim gecmisi sekmesi."""
from __future__ import annotations

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.security.permission_messages import admin_required_message
from app.services.personel_service import PersonelService
from app.validators import format_tarih
from ui.components import AsyncRunner
from ui.styles import T


class PersonelBirimGecmisiTab(QWidget):
    """Personelin gorev yeri gecmisini salt-okunur tablo olarak gosterir."""

    def __init__(self, db=None, personel_id_getter=None, oturum_getter=None, parent=None):
        super().__init__(parent)
        self._svc = PersonelService(db) if db is not None else None
        self._personel_id_getter = personel_id_getter or (lambda: "")
        self._oturum_getter = oturum_getter or (lambda: None)
        self._rows: list[dict] = []
        self._selected_id: str = ""
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        self._uyari = QLabel("")
        self._uyari.setStyleSheet(f"color:{T.text3};font-size:11px;")
        root.addWidget(self._uyari)

        self._tablo = QTableWidget(self)
        self._tablo.setColumnCount(5)
        self._tablo.setHorizontalHeaderLabels(
            ["Birim", "Baslama", "Bitis", "Aciklama", "Kayit Tarihi"]
        )
        self._tablo.verticalHeader().setVisible(False)
        self._tablo.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tablo.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._tablo.setAlternatingRowColors(True)
        self._tablo.horizontalHeader().setStretchLastSection(True)
        self._tablo.itemSelectionChanged.connect(self._on_row_selected)

        root.addWidget(self._tablo, 1)

        self._admin_box = QWidget(self)
        self._admin_panel = QVBoxLayout(self._admin_box)
        self._admin_panel.setContentsMargins(0, 0, 0, 0)
        self._admin_panel.setSpacing(6)

        form_row = QHBoxLayout()
        form_row.setSpacing(6)

        self._cmb_birim = QComboBox(self)
        self._cmb_birim.setMinimumWidth(220)

        self._dt_baslama = QDateEdit(self)
        self._dt_baslama.setCalendarPopup(True)
        self._dt_baslama.setDisplayFormat("dd.MM.yyyy")

        self._dt_bitis = QDateEdit(self)
        self._dt_bitis.setCalendarPopup(True)
        self._dt_bitis.setDisplayFormat("dd.MM.yyyy")
        self._dt_bitis.setSpecialValueText("-")
        self._dt_bitis.setDate(self._dt_bitis.minimumDate())

        self._txt_aciklama = QLineEdit(self)
        self._txt_aciklama.setPlaceholderText("Aciklama")

        form_row.addWidget(QLabel("Birim"))
        form_row.addWidget(self._cmb_birim)
        form_row.addWidget(QLabel("Baslama"))
        form_row.addWidget(self._dt_baslama)
        form_row.addWidget(QLabel("Bitis"))
        form_row.addWidget(self._dt_bitis)
        form_row.addWidget(self._txt_aciklama, 1)
        self._admin_panel.addLayout(form_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        btn_row.addStretch(1)

        self._btn_yeni = QPushButton("Yeni Kayit Ekle", self)
        self._btn_yeni.clicked.connect(self._add_record)

        self._btn_guncelle = QPushButton("Secili Kaydi Guncelle", self)
        self._btn_guncelle.clicked.connect(self._update_record)
        self._btn_guncelle.setEnabled(False)

        btn_row.addWidget(self._btn_yeni)
        btn_row.addWidget(self._btn_guncelle)
        self._admin_panel.addLayout(btn_row)

        root.addWidget(self._admin_box)

        self._apply_admin_visibility()

    def yenile(self) -> None:
        personel_id = str(self._personel_id_getter() or "").strip()
        if not personel_id or self._svc is None:
            self._rows = []
            self._selected_id = ""
            self._tablo.setRowCount(0)
            self._uyari.setText("Birim gecmisi bulunamadi.")
            return

        self._load_birimler()

        AsyncRunner(
            fn=lambda: self._svc.gorev_gecmisi(personel_id),
            on_done=self._load_done,
            on_error=self._load_error,
            parent=self,
        ).start()

    def _load_birimler(self) -> None:
        if self._svc is None:
            return
        mevcut = self._cmb_birim.currentData()
        self._cmb_birim.clear()
        self._cmb_birim.addItem("Seciniz", "")
        for gy in self._svc.gorev_yerleri():
            self._cmb_birim.addItem(str(gy.get("ad") or ""), str(gy.get("id") or ""))
        if mevcut:
            idx = self._cmb_birim.findData(mevcut)
            if idx >= 0:
                self._cmb_birim.setCurrentIndex(idx)

    def _load_done(self, rows: list[dict]) -> None:
        self._rows = rows or []
        self._selected_id = ""
        self._btn_guncelle.setEnabled(False)
        self._tablo.setRowCount(len(rows))
        for i, row in enumerate(rows):
            bitis = format_tarih(row.get("bitis_tarihi"), ui=True) if row.get("bitis_tarihi") else "Aktif"
            vals = [
                str(row.get("gorev_yeri_ad") or "-"),
                format_tarih(row.get("baslama_tarihi"), ui=True),
                bitis,
                str(row.get("aciklama") or ""),
                format_tarih(row.get("olusturuldu"), ui=True),
            ]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                if c in (1, 2, 4):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._tablo.setItem(i, c, item)

        if rows:
            self._uyari.setText(f"Toplam {len(rows)} birim kaydi bulundu.")
        else:
            self._uyari.setText("Birim gecmisi bulunamadi.")

    def _load_error(self, message: str) -> None:
        self._rows = []
        self._selected_id = ""
        self._btn_guncelle.setEnabled(False)
        self._tablo.setRowCount(0)
        self._uyari.setText(message or "Birim gecmisi yuklenemedi.")

    def _is_admin(self) -> bool:
        oturum = self._oturum_getter() or {}
        return str(oturum.get("rol") or "").strip().lower() == "admin"

    def _apply_admin_visibility(self) -> None:
        is_admin = self._is_admin()
        self._admin_box.setVisible(is_admin)
        if not is_admin:
            self._uyari.setText("Bu sekmede duzenleme islemleri yalnizca admin icin aciktir.")

    def _on_row_selected(self) -> None:
        if not self._is_admin():
            return
        idx = self._tablo.currentRow()
        if idx < 0 or idx >= len(self._rows):
            self._selected_id = ""
            self._btn_guncelle.setEnabled(False)
            return

        row = self._rows[idx]
        self._selected_id = str(row.get("id") or "")
        birim_id = str(row.get("gorev_yeri_id") or "")
        birim_idx = self._cmb_birim.findData(birim_id)
        self._cmb_birim.setCurrentIndex(birim_idx if birim_idx >= 0 else 0)

        bas = row.get("baslama_tarihi")
        bit = row.get("bitis_tarihi")
        if bas:
            bas_qt = QDate.fromString(format_tarih(bas, ui=True), "dd.MM.yyyy")
            if bas_qt.isValid():
                self._dt_baslama.setDate(bas_qt)
        if bit:
            bit_qt = QDate.fromString(format_tarih(bit, ui=True), "dd.MM.yyyy")
            if bit_qt.isValid():
                self._dt_bitis.setDate(bit_qt)
        else:
            self._dt_bitis.setDate(self._dt_bitis.minimumDate())
        self._txt_aciklama.setText(str(row.get("aciklama") or ""))
        self._btn_guncelle.setEnabled(bool(self._selected_id))

    def _form_payload(self) -> dict:
        bitis_tarih = format_tarih(self._dt_bitis.date().toPython(), ui=False)
        if self._dt_bitis.date() == self._dt_bitis.minimumDate():
            bitis_tarih = ""
        return {
            "gorev_yeri_id": str(self._cmb_birim.currentData() or "").strip(),
            "baslama_tarihi": format_tarih(self._dt_baslama.date().toPython(), ui=False),
            "bitis_tarihi": bitis_tarih,
            "aciklama": str(self._txt_aciklama.text() or "").strip(),
        }

    def _add_record(self) -> None:
        if not self._is_admin():
            self._uyari.setText(admin_required_message())
            return
        personel_id = str(self._personel_id_getter() or "").strip()
        payload = self._form_payload()
        if not personel_id or not payload.get("gorev_yeri_id"):
            self._uyari.setText("Birim secimi zorunludur.")
            return

        AsyncRunner(
            fn=lambda: self._svc.gorev_gecmisi_ekle(
                personel_id,
                payload["gorev_yeri_id"],
                payload["baslama_tarihi"],
                payload["bitis_tarihi"] or None,
                payload["aciklama"],
                oturum=self._oturum_getter(),
            ),
            on_done=lambda _id: self._after_write("Kayit eklendi."),
            on_error=self._load_error,
            parent=self,
        ).start()

    def _update_record(self) -> None:
        if not self._is_admin():
            self._uyari.setText(admin_required_message())
            return
        personel_id = str(self._personel_id_getter() or "").strip()
        if not personel_id or not self._selected_id:
            self._uyari.setText("Guncellemek icin bir kayit secin.")
            return
        payload = self._form_payload()
        if not payload.get("gorev_yeri_id"):
            self._uyari.setText("Birim secimi zorunludur.")
            return

        AsyncRunner(
            fn=lambda: self._svc.gorev_gecmisi_guncelle(
                personel_id,
                self._selected_id,
                payload,
                oturum=self._oturum_getter(),
            ),
            on_done=lambda _: self._after_write("Kayit guncellendi."),
            on_error=self._load_error,
            parent=self,
        ).start()

    def _after_write(self, message: str) -> None:
        self._uyari.setText(message)
        self.yenile()
