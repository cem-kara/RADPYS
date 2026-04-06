# -*- coding: utf-8 -*-
"""
ui/pages/personel/personel_form.py
────────────────────────────────────
Yeni personel ekleme formu (QDialog).
"""
from __future__ import annotations
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QGroupBox,
    QScrollArea, QFrame, QWidget,
)
from PySide6.QtCore import Qt, Signal
from ui.theme import T
from ui.components.buttons import PrimaryButton, GhostButton
from ui.components.alerts import AlertBar


class PersonelForm(QDialog):
    """
    Yeni personel ekleme dialog'u.

    Sinyal:
        kaydedildi(personel_id) — başarılı ekleme sonrası

    Kullanım:
        dlg = PersonelForm(svc, parent=self)
        if dlg.exec():
            pid = dlg.yeni_id
    """

    kaydedildi = Signal(str)

    def __init__(self, svc, parent=None):
        super().__init__(parent)
        self._svc    = svc
        self.yeni_id: str | None = None
        self.setWindowTitle("Yeni Personel Ekle")
        self.setMinimumWidth(580)
        self.setModal(True)
        self._build()
        self._dropdown_doldur()

    # ── UI ────────────────────────────────────────────────────────

    def _build(self):
        kok = QVBoxLayout(self)
        kok.setContentsMargins(0, 0, 0, 0)
        kok.setSpacing(0)

        # Başlık
        hdr = QFrame()
        hdr.setStyleSheet(f"background:{T.bg_panel}; border-bottom:1px solid {T.border};")
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(20, 14, 20, 14)
        lbl = QLabel("Yeni Personel Ekle")
        lbl.setStyleSheet(f"color:{T.text_primary}; font-size:16px; font-weight:600;")
        hdr_lay.addWidget(lbl)
        hdr_lay.addStretch()
        kok.addWidget(hdr)

        # Uyarı
        self._alert = AlertBar(self)
        kok.addWidget(self._alert)

        # Form içeriği
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(20, 16, 20, 16)
        inner_lay.setSpacing(14)

        self._alanlar: dict[str, QLineEdit | QComboBox] = {}

        # Zorunlu
        gb1 = self._grup("Kimlik Bilgileri *", [
            ("tc_kimlik",  "TC Kimlik No *",    True,  "11 haneli TC"),
            ("ad",         "Ad *",              True,  ""),
            ("soyad",      "Soyad *",           True,  ""),
            ("dogum_tarihi","Doğum Tarihi",     True,  "YYYY-MM-DD"),
            ("dogum_yeri", "Doğum Yeri",        True,  ""),
        ])
        inner_lay.addWidget(gb1)

        # Görev
        gb2 = self._grup_combo("Görev Bilgileri", [
            ("hizmet_sinifi",     "Hizmet Sınıfı"),
            ("kadro_unvani",      "Kadro Unvanı"),
            ("gorev_yeri_ad",     "Görev Yeri"),
        ], text_ek=[
            ("sicil_no",          "Sicil No",         True, ""),
            ("memuriyet_baslama", "Mem. Başlama",     True, "YYYY-MM-DD"),
        ])
        inner_lay.addWidget(gb2)

        # İletişim
        gb3 = self._grup("İletişim", [
            ("telefon", "Telefon", True, "05XX XXX XX XX"),
            ("e_posta", "E-posta", True, ""),
        ])
        inner_lay.addWidget(gb3)

        # Eğitim
        gb4 = self._grup("1. Eğitim", [
            ("okul_1",       "Okul",       True, ""),
            ("fakulte_1",    "Fakülte",    True, ""),
            ("mezuniyet_1",  "Mezuniyet",  True, "YYYY-MM-DD"),
            ("diploma_no_1", "Diploma No", True, ""),
        ])
        inner_lay.addWidget(gb4)

        scroll.setWidget(inner)
        kok.addWidget(scroll, 1)

        # Alt butonlar
        alt = QFrame()
        alt.setStyleSheet(f"background:{T.bg_panel}; border-top:1px solid {T.border};")
        alt_lay = QHBoxLayout(alt)
        alt_lay.setContentsMargins(20, 12, 20, 12)
        alt_lay.addStretch()
        btn_iptal = GhostButton("İptal")
        btn_iptal.clicked.connect(self.reject)
        self._btn_kaydet = PrimaryButton("Personel Ekle")
        self._btn_kaydet.clicked.connect(self._kaydet)
        alt_lay.addWidget(btn_iptal)
        alt_lay.addWidget(self._btn_kaydet)
        kok.addWidget(alt)

    def _grup(self, baslik: str, alanlar: list) -> QGroupBox:
        gb   = QGroupBox(baslik)
        grid = QGridLayout(gb)
        grid.setContentsMargins(12, 8, 12, 8)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)
        for i, (key, etiket, _, placeholder) in enumerate(alanlar):
            lbl = QLabel(etiket)
            lbl.setStyleSheet(f"color:{T.text_secondary}; font-size:12px;")
            lbl.setFixedWidth(140)
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            edit = QLineEdit()
            if placeholder:
                edit.setPlaceholderText(placeholder)
            grid.addWidget(lbl, i, 0)
            grid.addWidget(edit, i, 1)
            self._alanlar[key] = edit
        grid.setColumnStretch(1, 1)
        return gb

    def _grup_combo(self, baslik: str, combo_alan: list,
                    text_ek: list | None = None) -> QGroupBox:
        gb   = QGroupBox(baslik)
        grid = QGridLayout(gb)
        grid.setContentsMargins(12, 8, 12, 8)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)
        satir = 0
        for key, etiket in combo_alan:
            lbl = QLabel(etiket)
            lbl.setStyleSheet(f"color:{T.text_secondary}; font-size:12px;")
            lbl.setFixedWidth(140)
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            cb = QComboBox()
            grid.addWidget(lbl, satir, 0)
            grid.addWidget(cb, satir, 1)
            self._alanlar[key] = cb
            satir += 1
        for key, etiket, _, ph in (text_ek or []):
            lbl = QLabel(etiket)
            lbl.setStyleSheet(f"color:{T.text_secondary}; font-size:12px;")
            lbl.setFixedWidth(140)
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            edit = QLineEdit()
            edit.setPlaceholderText(ph)
            grid.addWidget(lbl, satir, 0)
            grid.addWidget(edit, satir, 1)
            self._alanlar[key] = edit
            satir += 1
        grid.setColumnStretch(1, 1)
        return gb

    # ── Dropdown ──────────────────────────────────────────────────

    def _dropdown_doldur(self):
        def _cb(key: str, liste: list[str]):
            cb = self._alanlar.get(key)
            if not isinstance(cb, QComboBox):
                return
            cb.addItem("— Seçiniz —", "")
            for d in liste:
                cb.addItem(d, d)

        _cb("hizmet_sinifi", self._svc.hizmet_siniflari())
        _cb("kadro_unvani",  self._svc.kadro_unvanlari())
        _cb("gorev_yeri_ad", self._svc.gorev_yeri_adlari())

    # ── Kaydet ────────────────────────────────────────────────────

    def _kaydet(self):
        self._alert.temizle()
        veri: dict[str, str] = {}
        for key, widget in self._alanlar.items():
            if isinstance(widget, QLineEdit):
                veri[key] = widget.text().strip()
            elif isinstance(widget, QComboBox):
                veri[key] = widget.currentData() or ""

        self._btn_kaydet.setEnabled(False)
        self._btn_kaydet.setText("Kaydediliyor…")
        try:
            self.yeni_id = self._svc.ekle(veri)
            self.kaydedildi.emit(self.yeni_id)
            self.accept()
        except Exception as e:
            self._alert.goster(str(e))
            self._btn_kaydet.setEnabled(True)
            self._btn_kaydet.setText("Personel Ekle")
