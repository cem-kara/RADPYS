# -*- coding: utf-8 -*-
"""ui/pages/personel/saglik_takip_page.py - Tum personel saglik takip formu."""
from __future__ import annotations

import os
from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.logger import exc_logla
from app.services.dokuman_service import DokumanService
from app.services.saglik_service import SaglikService
from ui.components import AlertBar, DangerButton, GhostButton, PrimaryButton
from ui.styles import T


class SaglikTakipPage(QWidget):
    """Tum personel icin saglik muayene listeleme ve kayit formu."""

    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self._svc = SaglikService(db) if db is not None else None
        self._dokuman_svc = DokumanService(db) if db is not None else None
        self._tum: list[dict] = []
        self._editing_id: str | None = None
        self._force_uzmanlik: str | None = None
        self._rapor_dosya_yolu = ""
        self._rapor_belge_id: str | None = None

        self.setStyleSheet(f"background:{T.bg0};")
        self._build()
        self._yukle()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 14)
        root.setSpacing(10)

        top = QHBoxLayout()
        lbl = QLabel("Saglik Takip")
        lbl.setStyleSheet(f"color:{T.text}; font-size:18px; font-weight:700;")
        top.addWidget(lbl)
        top.addStretch(1)
        self._btn_yeni = PrimaryButton("Yeni Muayene")
        self._btn_yeni.clicked.connect(self._ac_form)
        top.addWidget(self._btn_yeni)
        root.addLayout(top)

        self._alert = AlertBar(self)
        root.addWidget(self._alert)

        self._form = self._build_form()
        self._form.setVisible(False)
        root.addWidget(self._form)

        self._akıs_lbl = QLabel("")
        self._akıs_lbl.setStyleSheet(f"color:{T.text2}; font-size:11px;")
        root.addWidget(self._akıs_lbl)

        root.addWidget(self._build_filter())

        self._table = QTableWidget(self)
        self._table.setColumnCount(9)
        self._table.setHorizontalHeaderLabels(
            ["Ad Soyad", "Birim", "Uzmanlik", "Muayene", "Sonraki", "Sonuc", "Durum", "Ilerleme", "Rapor"]
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.doubleClicked.connect(self._duzenle_secili)
        self._table.cellClicked.connect(self._hucre_tikla)
        root.addWidget(self._table, 1)

        self._lbl_ozet = QLabel("")
        self._lbl_ozet.setStyleSheet(f"color:{T.text3}; font-size:11px;")
        root.addWidget(self._lbl_ozet)

    def _build_filter(self) -> QFrame:
        frame = QFrame(self)
        frame.setStyleSheet(
            f"QFrame{{background:{T.bg1}; border:1px solid {T.border}; border-radius:{T.radius}px;}}"
        )
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(8)

        self._yil = QComboBox(self)
        self._yil.addItem("Tum Yillar", None)
        this_year = date.today().year
        for y in range(this_year + 1, this_year - 4, -1):
            self._yil.addItem(str(y), y)
        self._yil.setCurrentIndex(2)
        self._yil.currentIndexChanged.connect(self._yukle)
        lay.addWidget(self._yil)

        self._durum = QComboBox(self)
        self._durum.addItem("Tum Durumlar", None)
        for d in ("Gecerli", "Riskli", "Gecikmis", "Planlandi"):
            self._durum.addItem(d, d)
        self._durum.currentIndexChanged.connect(self._filtrele)
        lay.addWidget(self._durum)

        self._ara = QLineEdit(self)
        self._ara.setPlaceholderText("Ad soyad veya birim ara...")
        self._ara.textChanged.connect(self._filtrele)
        lay.addWidget(self._ara, 1)

        return frame

    def _build_form(self) -> QFrame:
        frm = QFrame(self)
        frm.setStyleSheet(
            f"QFrame{{background:{T.bg1}; border:1px solid {T.border}; border-radius:{T.radius}px;}}"
        )
        lay = QVBoxLayout(frm)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(8)

        row = QHBoxLayout()
        self._frm_baslik = QLabel("Yeni Muayene")
        self._frm_baslik.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        row.addWidget(self._frm_baslik)
        row.addStretch(1)
        self._btn_kapat = GhostButton("Kapat")
        self._btn_kapat.clicked.connect(self._kapat_form)
        row.addWidget(self._btn_kapat)
        lay.addLayout(row)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        self._p = QComboBox(self)
        self._p.currentIndexChanged.connect(self._yenile_akıs_ve_uzmanlik)
        self._u = QComboBox(self)
        self._t = QDateEdit(self)
        self._t.setCalendarPopup(True)
        self._t.setDate(date.today())
        self._t.dateChanged.connect(self._yenile_akıs_ve_uzmanlik)
        self._t.dateChanged.connect(self._tarih_degisti)
        self._s = QDateEdit(self)
        self._s.setCalendarPopup(True)
        self._s.setDate(date.today())
        self._s.setEnabled(False)
        self._sonuc = QComboBox(self)
        self._sonuc.addItem("", None)
        self._sonuc.addItems(["Uygun", "Takip", "Uygun Degil"])
        self._not = QLineEdit(self)
        self._not.setPlaceholderText("Not...")
        self._rapor_lbl = QLabel("Rapor: Yuklenmedi")
        self._rapor_lbl.setStyleSheet(f"color:{T.text2};")
        self._btn_rapor_sec = GhostButton("Rapor Formu Sec")
        self._btn_rapor_sec.clicked.connect(self._rapor_sec)

        grid.addWidget(QLabel("Personel"), 0, 0)
        grid.addWidget(self._p, 0, 1)
        grid.addWidget(QLabel("Uzmanlik"), 0, 2)
        grid.addWidget(self._u, 0, 3)

        grid.addWidget(QLabel("Muayene Tarihi"), 1, 0)
        grid.addWidget(self._t, 1, 1)
        grid.addWidget(QLabel("Sonraki Kontrol"), 1, 2)
        grid.addWidget(self._s, 1, 3)

        grid.addWidget(QLabel("Sonuc"), 2, 0)
        grid.addWidget(self._sonuc, 2, 1)
        grid.addWidget(QLabel("Not"), 2, 2)
        grid.addWidget(self._not, 2, 3)

        rapor_row = QHBoxLayout()
        rapor_row.addWidget(self._rapor_lbl, 1)
        rapor_row.addWidget(self._btn_rapor_sec)
        lay.addLayout(rapor_row)

        lay.addLayout(grid)

        aks = QHBoxLayout()
        aks.addStretch(1)
        self._btn_sil = DangerButton("Kaydi Sil")
        self._btn_sil.clicked.connect(self._sil)
        self._btn_sil.setVisible(False)
        self._btn_kaydet = PrimaryButton("Kaydet")
        self._btn_kaydet.clicked.connect(self._kaydet)
        self._btn_iptal = DangerButton("Iptal")
        self._btn_iptal.clicked.connect(self._kapat_form)
        aks.addWidget(self._btn_sil)
        aks.addWidget(self._btn_kaydet)
        aks.addWidget(self._btn_iptal)
        lay.addLayout(aks)

        return frm

    def load_data(self):
        self._yukle()

    def _yukle(self) -> None:
        if self._svc is None:
            return
        try:
            yil = self._yil.currentData()
            self._tum = self._svc.tum_muayene_kayitlari(yil=yil)
            self._fill_form_sources()
            self._filtrele()
            self._yenile_akıs_ve_uzmanlik()
        except Exception as exc:
            exc_logla("SaglikTakipPage._yukle", exc)
            self._alert.goster(str(exc), "danger")

    def _fill_form_sources(self) -> None:
        if self._svc is None:
            return

        self._u.blockSignals(True)
        self._u.clear()
        for u in self._svc.uzmanlik_secenekleri():
            self._u.addItem(u)
        self._u.blockSignals(False)

        current_pid = self._p.currentData()
        self._p.blockSignals(True)
        self._p.clear()
        for p in self._svc.personel_secenekleri():
            self._p.addItem(f"{p['ad_soyad']} ({p['birim']})", p["id"])
        if current_pid:
            idx = self._p.findData(current_pid)
            if idx >= 0:
                self._p.setCurrentIndex(idx)
        self._p.blockSignals(False)
        self._yenile_akıs_ve_uzmanlik()

    def _secili_yil(self) -> int:
        return int(self._t.date().year())

    def _tarih_degisti(self) -> None:
        self._s.setDate(self._t.date().addYears(1))

    def _yenile_akıs_ve_uzmanlik(self) -> None:
        if self._svc is None:
            return

        pid = str(self._p.currentData() or "").strip()
        if not pid:
            self._akıs_lbl.setText("Personel secildiginde 3 ana uzmanlik akisi aktif olur.")
            return

        yil = self._secili_yil()
        durum = self._svc.personel_yil_uzmanlik_durumu(pid, yil)
        eksik = list(durum.get("eksik") or [])
        tamam = list(durum.get("tamamlanan") or [])
        rapor = self._svc.personel_yil_tek_rapor(pid, yil)
        self._rapor_belge_id = str(rapor.get("belge_id") or "").strip() if rapor else None

        if rapor:
            self._rapor_lbl.setText(f"Rapor: {str(rapor.get('dosya_adi') or '-')}")
            self._btn_rapor_sec.setText("Raporu Degistir")
        else:
            self._rapor_lbl.setText("Rapor: Yuklenmedi")
            self._btn_rapor_sec.setText("Rapor Formu Sec")

        self._akıs_lbl.setText(
            f"{yil} akisi: Tamamlanan {len(tamam)}/3 ({', '.join(tamam) if tamam else '-'}) | "
            f"Eksik: {', '.join(eksik) if eksik else '-'}"
        )

        if self._editing_id:
            return

        self._u.blockSignals(True)
        self._u.clear()
        secenekler = eksik or list(durum.get("zorunlu") or [])
        for uz in secenekler:
            self._u.addItem(str(uz))
        self._u.blockSignals(False)

        if not secenekler:
            self._u.addItem("-")
            self._u.setEnabled(False)
            self._btn_kaydet.setEnabled(False)
            self._alert.goster("Bu personelin secili yilda 3 ana muayenesi tamam.", "info")
            return

        self._u.setEnabled(True)
        self._btn_kaydet.setEnabled(True)

    def _filtrele(self) -> None:
        q = self._ara.text().strip().lower()
        durum = self._durum.currentData()

        # personel+yil bazinda tamamlanan uzmanlik sayisi
        ilerleme: dict[tuple, int] = {}
        for r in self._tum:
            key = (str(r.get("personel_id") or ""), int(r.get("yil") or 0))
            ilerleme[key] = ilerleme.get(key, 0) + 1

        rows = []
        for r in self._tum:
            if durum and str(r.get("durum") or "") != str(durum):
                continue
            ad = str(r.get("ad_soyad") or "").lower()
            birim = str(r.get("birim") or "").lower()
            if q and q not in ad and q not in birim:
                continue
            rows.append(r)

        self._table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            key = (str(r.get("personel_id") or ""), int(r.get("yil") or 0))
            imza_n = ilerleme.get(key, 1)
            imza_txt = f"{imza_n}/3"
            vals = [
                r.get("ad_soyad", ""),
                r.get("birim", ""),
                r.get("uzmanlik", ""),
                r.get("muayene_tarihi", ""),
                r.get("sonraki_kontrol", ""),
                r.get("sonuc", ""),
                r.get("durum", ""),
                imza_txt,
                r.get("rapor", "-"),
            ]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(str(v))
                it.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                if c >= 3:
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._table.setItem(i, c, it)
            self._table.item(i, 0).setData(Qt.ItemDataRole.UserRole, r)

        self._lbl_ozet.setText(f"Toplam {len(rows)} kayit")

    def _ac_form(self) -> None:
        self._editing_id = None
        self._force_uzmanlik = None
        self._rapor_dosya_yolu = ""
        self._frm_baslik.setText("Yeni Muayene")
        self._btn_sil.setVisible(False)
        self._temizle_form()
        self._yenile_akıs_ve_uzmanlik()
        self._form.setVisible(True)

    def _kapat_form(self) -> None:
        self._editing_id = None
        self._force_uzmanlik = None
        self._rapor_dosya_yolu = ""
        self._form.setVisible(False)

    def _rapor_entity(self) -> tuple[str, str, str] | None:
        pid = str(self._p.currentData() or "").strip()
        if not pid:
            return None
        yil = self._secili_yil()
        entity_turu = "muayene_formu"
        entity_id = f"{pid}:{yil}"
        klasor_adi = f"muayene_{pid}_{yil}"
        return entity_turu, entity_id, klasor_adi

    def _rapor_sec(self) -> None:
        entity = self._rapor_entity()
        if entity is None:
            self._alert.goster("Once personel seciniz.", "warning")
            return

        fp, _ = QFileDialog.getOpenFileName(self, "Rapor Formu Sec", "", "Tum Dosyalar (*.*)")
        if not fp:
            return
        self._rapor_dosya_yolu = fp
        self._rapor_lbl.setText(f"Rapor (secilen): {fp}")

    def _duzenle_secili(self) -> None:
        row = self._table.currentRow()
        if row < 0:
            return
        row_obj = self._table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        if not row_obj:
            return

        self._editing_id = str(row_obj.get("id") or "")
        self._force_uzmanlik = str(row_obj.get("uzmanlik") or "").strip()
        self._frm_baslik.setText("Muayene Duzenle")
        self._btn_sil.setVisible(True)

        pidx = self._p.findData(str(row_obj.get("personel_id") or ""))
        if pidx >= 0:
            self._p.setCurrentIndex(pidx)

        self._u.blockSignals(True)
        self._u.clear()
        for uz in self._svc.uzmanlik_secenekleri() if self._svc else []:
            self._u.addItem(uz)
        self._u.blockSignals(False)

        uidx = self._u.findText(self._force_uzmanlik)
        if uidx >= 0:
            self._u.setCurrentIndex(uidx)

        self._set_date(self._t, str(row_obj.get("muayene_tarihi_db") or ""))
        self._set_date(self._s, str(row_obj.get("sonraki_kontrol_db") or ""))

        sidx = self._sonuc.findText(str(row_obj.get("sonuc") or ""))
        if sidx >= 0:
            self._sonuc.setCurrentIndex(sidx)
        self._not.setText(str(row_obj.get("notlar") or ""))
        self._form.setVisible(True)

    def _set_date(self, widget: QDateEdit, raw: str) -> None:
        dt = QDate.fromString(str(raw or ""), "yyyy-MM-dd")
        if dt.isValid():
            widget.setDate(dt)

    def _temizle_form(self) -> None:
        if self._p.count() > 0:
            self._p.setCurrentIndex(0)
        self._t.setDate(QDate.currentDate())
        self._s.setDate(QDate.currentDate().addYears(1))
        self._sonuc.setCurrentIndex(0)
        self._not.clear()

    def _kaydet(self) -> None:
        if self._svc is None:
            return
        try:
            pid = self._p.currentData()
            if not pid:
                self._alert.goster("Personel seciniz.", "warning")
                return

            belge_id = self._rapor_belge_id
            if self._rapor_dosya_yolu:
                entity = self._rapor_entity()
                if entity is None or self._dokuman_svc is None:
                    self._alert.goster("Rapor baglantisi olusturulamadi.", "danger")
                    return
                entity_turu, entity_id, klasor_adi = entity
                belge_id = self._dokuman_svc.yukle(
                    file_path=self._rapor_dosya_yolu,
                    entity_turu=entity_turu,
                    entity_id=entity_id,
                    tur="Periyodik Muayene Raporu",
                    aciklama="3 uzmanlik tek rapor formu",
                    klasor_adi=klasor_adi,
                )

            payload = {
                "personel_id": str(pid),
                "uzmanlik": self._u.currentText().strip(),
                "tarih": self._t.date().toString("yyyy-MM-dd"),
                "sonuc": self._sonuc.currentText().strip(),
                "notlar": self._not.text().strip(),
                "belge_id": belge_id,
            }
            self._svc.muayene_kaydet(payload, muayene_id=self._editing_id)
            self._alert.goster("Saglik kaydi kaydedildi.", "success")
            self._kapat_form()
            self._yukle()
        except Exception as exc:
            exc_logla("SaglikTakipPage._kaydet", exc)
            self._alert.goster(str(exc), "danger")

    def _hucre_tikla(self, row: int, col: int) -> None:
        """Rapor kolonu (8) tiklandığında dosyayı aç."""
        if col != 8:
            return
        item = self._table.item(row, 0)
        if item is None:
            return
        r = item.data(Qt.ItemDataRole.UserRole)
        if not r:
            return
        lokal_yol = str(r.get("lokal_yol") or "").strip()
        if not lokal_yol:
            self._alert.goster("Bu kayda ait rapor dosyasi bulunamadi.", "warning")
            return
        try:
            os.startfile(lokal_yol)
        except Exception as exc:
            self._alert.goster(f"Dosya acilamadi: {exc}", "danger")

    def _sil(self) -> None:
        if not self._editing_id or self._svc is None:
            return
        cevap = QMessageBox.question(
            self,
            "Kaydi Sil",
            "Bu muayene kaydini silmek istediginizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if cevap != QMessageBox.StandardButton.Yes:
            return
        try:
            self._svc.muayene_sil(self._editing_id)
            self._alert.goster("Muayene kaydi silindi.", "success")
            self._kapat_form()
            self._yukle()
        except Exception as exc:
            exc_logla("SaglikTakipPage._sil", exc)
            self._alert.goster(str(exc), "danger")
