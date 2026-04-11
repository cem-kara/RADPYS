# -*- coding: utf-8 -*-
"""Personel ekleme / duzenleme formu."""
from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.config import BELGE_DIR
from app.exceptions import KayitBulunamadi
from app.logger import exc_logla
from app.services.personel_onboarding_service import PersonelOnboardingService
from app.services.personel_service import PersonelService
from app.text_utils import (
    capitalize_first_letter,
    format_phone_number,
    normalize_whitespace,
    turkish_lower,
    turkish_title_case,
)
from app.validators import (
    bugun,
    format_tarih,
    parse_tarih,
    validate_email,
    validate_phone_number,
    validate_tc_kimlik_no,
)
from ui.components import AlertBar, AsyncRunner, BelgeSekmesi, GhostButton, PrimaryButton
from ui.styles import T


class PersonelEklePage(QWidget):
    """Personel ekle / guncelle sayfasi."""

    form_closed = Signal()

    def __init__(self, db, edit_data: dict | None = None, on_saved=None, parent=None):
        super().__init__(parent)
        self._db = db
        self._svc = PersonelService(db)
        self._onboarding = PersonelOnboardingService(db)
        self._edit_data = edit_data
        self._on_saved = on_saved
        self._is_edit = bool(edit_data)
        self._personel_id = str((edit_data or {}).get("id") or "")
        self._foto_yolu: str = ""
        self._foto_degisti: bool = False

        self._build()
        self._load_lookups()
        if self._is_edit:
            self._fill_form(edit_data or {})
            self._docs_tab.set_entity("personel", self._personel_id, self.tc.text().strip())

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(10)

        self._alert = AlertBar(self)
        root.addWidget(self._alert)

        title = QLabel("Personel Duzenle" if self._is_edit else "Personel Ekle")
        title.setStyleSheet(f"color:{T.text};font-size:16px;font-weight:700;")
        root.addWidget(title)

        self._tabs = QTabWidget(self)
        self._tabs.setStyleSheet(
            f"QTabWidget::pane{{border:1px solid {T.border};background:{T.bg1};border-radius:{T.radius}px;}}"
            f"QTabBar::tab{{background:{T.bg2};color:{T.text2};padding:6px 12px;margin-right:4px;border:1px solid {T.border};border-bottom:none;border-top-left-radius:6px;border-top-right-radius:6px;}}"
            f"QTabBar::tab:selected{{background:{T.bg1};color:{T.text};}}"
        )

        self._tab_kimlik = QWidget(self)
        self._tab_belgeler = QWidget(self)
        self._tabs.addTab(self._tab_kimlik, "Kimlik")
        self._tabs.addTab(self._tab_belgeler, "Belgeler")

        self._build_kimlik_tab(self._tab_kimlik)
        self._build_belgeler_tab(self._tab_belgeler)

        if not self._is_edit:
            self._tabs.setTabEnabled(1, False)

        root.addWidget(self._tabs, 1)

    def _build_kimlik_tab(self, tab: QWidget) -> None:
        root = QHBoxLayout(tab)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(12)

        left = QFrame()
        left.setFixedWidth(260)
        left.setStyleSheet(
            f"QFrame{{background:{T.bg1};border:1px solid {T.border};border-radius:{T.radius}px;}}"
        )
        self._kimlik_frame = left
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(12, 12, 12, 12)
        left_lay.setSpacing(8)

        left_title = QLabel("Fotograf ve Kimlik Bilgileri")
        left_title.setStyleSheet(
            f"color:{T.accent2};font-size:12px;font-weight:700;"
            f"background:{T.overlay_low};padding:2px 8px;border-radius:8px;"
        )
        left_lay.addWidget(left_title)

        foto_box = QFrame()
        foto_box.setMinimumHeight(170)
        foto_box.setStyleSheet(
            f"QFrame{{background:{T.bg0};border:1px dashed {T.border2};border-radius:{T.radius_sm}px;}}"
        )
        foto_lay = QVBoxLayout(foto_box)
        foto_lay.setContentsMargins(8, 8, 8, 8)
        foto_lay.addStretch()
        self._foto_lbl = QLabel("Fotograf")
        self._foto_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._foto_lbl.setMinimumHeight(140)
        self._foto_lbl.setStyleSheet(f"color:{T.text3};font-size:12px;")
        foto_lay.addWidget(self._foto_lbl)
        foto_lay.addStretch()
        self.btn_fotograf = GhostButton("Fotograf Sec", ikon="upload")
        self.btn_fotograf.clicked.connect(self._on_fotograf_sec)
        foto_lay.addWidget(self.btn_fotograf)
        left_lay.addWidget(foto_box)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{T.border};")
        left_lay.addWidget(sep)

        self.tc = QLineEdit()
        self.tc.setMaxLength(11)
        self.tc.setPlaceholderText("11 haneli TC")
        self.ad = QLineEdit()
        self.ad.setPlaceholderText("Ad")
        self.soyad = QLineEdit()
        self.soyad.setPlaceholderText("Soyad")
        self.dogum_yeri = QComboBox()
        self.dogum_yeri.setEditable(True)
        self.dogum_tarihi = QDateEdit()
        self.dogum_tarihi.setCalendarPopup(True)
        self.dogum_tarihi.setDate(QDate.currentDate().addYears(-30))
        self.hizmet_sinifi = QComboBox()
        self.kadro_unvani = QComboBox()
        self.gorev_yeri = QComboBox()
        self.sicil_no = QLineEdit()
        self.memuriyet_baslama = QDateEdit()
        self.memuriyet_baslama.setCalendarPopup(True)
        self.memuriyet_baslama.setDate(QDate.currentDate())
        self.telefon = QLineEdit()
        self.telefon.setPlaceholderText("05XX XXX XX XX")
        self.e_posta = QLineEdit()
        self.e_posta.setPlaceholderText("ornek@mail.com")

        self.okul_1 = QComboBox()
        self.okul_1.setEditable(True)
        self.fakulte_1 = QComboBox()
        self.fakulte_1.setEditable(True)
        self.mezuniyet_1 = QDateEdit()
        self.mezuniyet_1.setCalendarPopup(True)
        self.mezuniyet_1.setDate(QDate.currentDate())
        self.diploma_no_1 = QLineEdit()

        self.okul_2 = QComboBox()
        self.okul_2.setEditable(True)
        self.fakulte_2 = QComboBox()
        self.fakulte_2.setEditable(True)
        self.mezuniyet_2 = QDateEdit()
        self.mezuniyet_2.setCalendarPopup(True)
        self.mezuniyet_2.setDate(QDate.currentDate())
        self.diploma_no_2 = QLineEdit()

        self._install_text_utils_bindings()

        # Sol kimlik formu
        kimlik_lbl = QLabel("TC Kimlik No *")
        kimlik_lbl.setStyleSheet(f"color:{T.text2};font-weight:600;")
        left_lay.addWidget(kimlik_lbl)
        left_lay.addWidget(self.tc)

        adsoyad_lbl = QLabel("Ad Soyad *")
        adsoyad_lbl.setStyleSheet(f"color:{T.text2};font-weight:600;")
        left_lay.addWidget(adsoyad_lbl)
        ad_row = QHBoxLayout()
        ad_row.setSpacing(6)
        self.ad.setPlaceholderText("Ad")
        self.soyad.setPlaceholderText("Soyad")
        ad_row.addWidget(self.ad)
        ad_row.addWidget(self.soyad)
        left_lay.addLayout(ad_row)

        dy_lbl = QLabel("Dogum Yeri")
        dy_lbl.setStyleSheet(f"color:{T.text2};font-weight:600;")
        left_lay.addWidget(dy_lbl)
        left_lay.addWidget(self.dogum_yeri)

        dt_lbl = QLabel("Dogum Tarihi")
        dt_lbl.setStyleSheet(f"color:{T.text2};font-weight:600;")
        left_lay.addWidget(dt_lbl)
        left_lay.addWidget(self.dogum_tarihi)
        left_lay.addStretch()

        # Sag panel (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        right_host = QWidget()
        right = QVBoxLayout(right_host)
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(10)

        # Iletisim bilgileri
        iletisim = QFrame()
        iletisim.setStyleSheet(
            f"QFrame{{background:{T.bg1};border:1px solid {T.border};border-radius:{T.radius}px;}}"
        )
        self._frame_iletisim = iletisim
        iletisim_lay = QGridLayout(iletisim)
        self._lay_iletisim = iletisim_lay
        iletisim_lay.setContentsMargins(12, 10, 12, 12)
        iletisim_lay.setHorizontalSpacing(10)
        iletisim_lay.setVerticalSpacing(6)
        iletisim_lay.addWidget(self._section_title("Iletisim Bilgileri"), 0, 0, 1, 2)
        iletisim_lay.addWidget(self._field_label("Cep Telefonu"), 1, 0)
        iletisim_lay.addWidget(self._field_label("E-posta"), 1, 1)
        iletisim_lay.addWidget(self.telefon, 2, 0)
        iletisim_lay.addWidget(self.e_posta, 2, 1)
        iletisim_lay.setColumnStretch(0, 1)
        iletisim_lay.setColumnStretch(1, 1)
        right.addWidget(iletisim)

        # Kurumsal bilgiler
        kurumsal = QFrame()
        kurumsal.setStyleSheet(
            f"QFrame{{background:{T.bg1};border:1px solid {T.border};border-radius:{T.radius}px;}}"
        )
        self._frame_kurumsal = kurumsal
        kurumsal_lay = QGridLayout(kurumsal)
        self._lay_kurumsal = kurumsal_lay
        kurumsal_lay.setContentsMargins(12, 10, 12, 12)
        kurumsal_lay.setHorizontalSpacing(10)
        kurumsal_lay.setVerticalSpacing(6)
        kurumsal_lay.addWidget(self._section_title("Kurumsal Bilgiler"), 0, 0, 1, 3)
        kurumsal_lay.addWidget(self._field_label("Hizmet Sinifi *"), 1, 0)
        kurumsal_lay.addWidget(self._field_label("Kadro Unvani *"), 1, 1)
        kurumsal_lay.addWidget(self._field_label("Gorev Yeri"), 1, 2)
        kurumsal_lay.addWidget(self.hizmet_sinifi, 2, 0)
        kurumsal_lay.addWidget(self.kadro_unvani, 2, 1)
        kurumsal_lay.addWidget(self.gorev_yeri, 2, 2)
        kurumsal_lay.addWidget(self._field_label("Baslama Tarihi"), 3, 0)
        kurumsal_lay.addWidget(self._field_label("Kurum Sicil No"), 3, 1)
        kurumsal_lay.addWidget(self.memuriyet_baslama, 4, 0)
        kurumsal_lay.addWidget(self.sicil_no, 4, 1)
        kurumsal_lay.setColumnStretch(0, 1)
        kurumsal_lay.setColumnStretch(1, 1)
        kurumsal_lay.setColumnStretch(2, 1)
        right.addWidget(kurumsal)

        # Egitim bilgileri
        egitim = QFrame()
        egitim.setStyleSheet(
            f"QFrame{{background:{T.bg1};border:1px solid {T.border};border-radius:{T.radius}px;}}"
        )
        self._frame_egitim = egitim
        egitim_lay = QGridLayout(egitim)
        self._lay_egitim = egitim_lay
        egitim_lay.setContentsMargins(12, 10, 12, 12)
        egitim_lay.setHorizontalSpacing(8)
        egitim_lay.setVerticalSpacing(8)

        egitim_lay.addWidget(self._section_title("Egitim Bilgileri"), 0, 0, 1, 4)
        alt1 = QLabel("Lise / Onlisans / Lisans")
        alt1.setStyleSheet(f"color:{T.accent2};font-size:11px;")
        egitim_lay.addWidget(alt1, 1, 0, 1, 4)
        egitim_lay.addWidget(self._field_label("Okul Adi"), 2, 0)
        egitim_lay.addWidget(self._field_label("Bolum / Fakulte"), 2, 1)
        egitim_lay.addWidget(self._field_label("Mezuniyet Tarihi"), 2, 2)
        egitim_lay.addWidget(self._field_label("Diploma No"), 2, 3)
        egitim_lay.addWidget(self.okul_1, 3, 0)
        egitim_lay.addWidget(self.fakulte_1, 3, 1)
        egitim_lay.addWidget(self.mezuniyet_1, 3, 2)
        egitim_lay.addWidget(self.diploma_no_1, 3, 3)

        alt2 = QLabel("Onlisans / Lisans / Yuksek Lisans / Doktora")
        alt2.setStyleSheet(f"color:{T.accent2};font-size:11px;")
        egitim_lay.addWidget(alt2, 4, 0, 1, 4)
        egitim_lay.addWidget(self._field_label("Okul Adi"), 5, 0)
        egitim_lay.addWidget(self._field_label("Bolum / Fakulte"), 5, 1)
        egitim_lay.addWidget(self._field_label("Mezuniyet Tarihi"), 5, 2)
        egitim_lay.addWidget(self._field_label("Diploma No"), 5, 3)
        egitim_lay.addWidget(self.okul_2, 6, 0)
        egitim_lay.addWidget(self.fakulte_2, 6, 1)
        egitim_lay.addWidget(self.mezuniyet_2, 6, 2)
        egitim_lay.addWidget(self.diploma_no_2, 6, 3)
        egitim_lay.setColumnStretch(0, 1)
        egitim_lay.setColumnStretch(1, 1)
        egitim_lay.setColumnStretch(2, 1)
        egitim_lay.setColumnStretch(3, 1)

        right.addWidget(egitim)

        footer = QHBoxLayout()
        footer.addStretch()
        btn_cancel = GhostButton("Kapat")
        btn_cancel.clicked.connect(self.form_closed.emit)
        footer.addWidget(btn_cancel)
        self.btn_save = PrimaryButton("Guncelle" if self._is_edit else "Kaydet")
        self.btn_save.clicked.connect(self._on_save)
        footer.addWidget(self.btn_save)
        right.addLayout(footer)
        right.addStretch()

        scroll.setWidget(right_host)

        root.addWidget(left)
        root.addWidget(scroll, 1)

    def _build_belgeler_tab(self, tab: QWidget) -> None:
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(8)

        self._docs_tab = BelgeSekmesi(
            db=self._db,
            entity_turu="personel",
            entity_id=self._personel_id,
            klasor_adi=self.tc.text().strip() if self._is_edit else "",
            parent=tab,
        )
        lay.addWidget(self._docs_tab)

    @staticmethod
    def _row(layout: QGridLayout, row: int, l1: str, w1, l2: str, w2) -> None:
        left_lbl = QLabel(l1)
        left_lbl.setStyleSheet(f"color:{T.text2};")
        right_lbl = QLabel(l2)
        right_lbl.setStyleSheet(f"color:{T.text2};")
        layout.addWidget(left_lbl, row, 0)
        layout.addWidget(w1, row, 1)
        layout.addWidget(right_lbl, row, 2)
        layout.addWidget(w2, row, 3)

    @staticmethod
    def _section_title(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color:{T.accent2};font-size:12px;font-weight:700;"
            f"background:{T.overlay_low};padding:2px 8px;border-radius:8px;"
        )
        return lbl

    @staticmethod
    def _field_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{T.text2};font-size:11px;font-weight:600;")
        return lbl

    def _load_lookups(self) -> None:
        try:
            self.hizmet_sinifi.clear()
            self.hizmet_sinifi.addItem("")
            self.hizmet_sinifi.addItems(self._svc.hizmet_siniflari())

            self.kadro_unvani.clear()
            self.kadro_unvani.addItem("")
            self.kadro_unvani.addItems(self._svc.kadro_unvanlari())

            self.gorev_yeri.clear()
            self.gorev_yeri.addItem("")
            self.gorev_yeri.addItems(self._svc.gorev_yeri_adlari())

            rows = self._svc.listele(aktif_only=False)
            dogum_yerleri = sorted(
                {str(r.get("dogum_yeri") or "").strip() for r in rows if str(r.get("dogum_yeri") or "").strip()}
            )
            self.dogum_yeri.clear()
            self.dogum_yeri.addItem("")
            self.dogum_yeri.addItems(dogum_yerleri)

            okullar = sorted({
                v for r in rows
                for v in (str(r.get("okul_1") or "").strip(), str(r.get("okul_2") or "").strip())
                if v
            })
            for combo in (self.okul_1, self.okul_2):
                combo.clear()
                combo.addItem("")
                combo.addItems(okullar)

            fakulteler = sorted({
                v for r in rows
                for v in (str(r.get("fakulte_1") or "").strip(), str(r.get("fakulte_2") or "").strip())
                if v
            })
            for combo in (self.fakulte_1, self.fakulte_2):
                combo.clear()
                combo.addItem("")
                combo.addItems(fakulteler)
        except Exception as exc:
            exc_logla("PersonelEklePage._load_lookups", exc)
            self._alert.goster("Lookup verileri yuklenemedi.", "warning")

    def _install_text_utils_bindings(self) -> None:
        self._bind_line_edit(self.ad, mode="title")
        self._bind_line_edit(self.soyad, mode="title")
        self._bind_line_edit(self.sicil_no, mode="first_upper")
        self._bind_line_edit(self.telefon, mode="phone")
        self._bind_line_edit(self.e_posta, mode="email")
        self._bind_line_edit(self.diploma_no_1, mode="first_upper")
        self._bind_line_edit(self.diploma_no_2, mode="first_upper")

        # Editable combo line edit'lerini de text_utils ile normalize et.
        for _combo, _mode in (
            (self.dogum_yeri, "title"),
            (self.okul_1, "title"),
            (self.okul_2, "title"),
            (self.fakulte_1, "title"),
            (self.fakulte_2, "title"),
        ):
            le = _combo.lineEdit()
            if le is not None:
                self._bind_line_edit(le, mode=_mode)

    @staticmethod
    def _bind_line_edit(widget: QLineEdit, mode: str) -> None:
        if widget is None:
            return
        widget.editingFinished.connect(lambda w=widget, m=mode: PersonelEklePage._normalize_line_edit(w, m))

    @staticmethod
    def _normalize_line_edit(widget: QLineEdit, mode: str) -> None:
        raw = widget.text()
        normalized = normalize_whitespace(raw)

        if mode == "title":
            normalized = turkish_title_case(normalized)
        elif mode == "first_upper":
            normalized = capitalize_first_letter(normalized)
        elif mode == "email":
            normalized = turkish_lower(normalized)
        elif mode == "phone":
            normalized = format_phone_number(normalized)

        if normalized != raw:
            widget.setText(normalized)

    def _fill_form(self, row: dict) -> None:
        self._personel_id = str(row.get("id") or "").strip()
        self.tc.setText(str(row.get("tc_kimlik") or ""))
        self.tc.setEnabled(False)

        self.ad.setText(str(row.get("ad") or ""))
        self.soyad.setText(str(row.get("soyad") or ""))
        self.dogum_yeri.setCurrentText(str(row.get("dogum_yeri") or ""))

        self._set_date(self.dogum_tarihi, row.get("dogum_tarihi"))
        self.hizmet_sinifi.setCurrentText(str(row.get("hizmet_sinifi") or ""))
        self.kadro_unvani.setCurrentText(str(row.get("kadro_unvani") or ""))
        self.gorev_yeri.setCurrentText(str(row.get("gorev_yeri_ad") or ""))

        self.sicil_no.setText(str(row.get("sicil_no") or ""))
        self._set_date(self.memuriyet_baslama, row.get("memuriyet_baslama"))
        self.telefon.setText(str(row.get("telefon") or ""))
        self.e_posta.setText(str(row.get("e_posta") or ""))

        self.okul_1.setCurrentText(str(row.get("okul_1") or ""))
        self.fakulte_1.setCurrentText(str(row.get("fakulte_1") or ""))
        self._set_date(self.mezuniyet_1, row.get("mezuniyet_1"))
        self.diploma_no_1.setText(str(row.get("diploma_no_1") or ""))

        self.okul_2.setCurrentText(str(row.get("okul_2") or ""))
        self.fakulte_2.setCurrentText(str(row.get("fakulte_2") or ""))
        self._set_date(self.mezuniyet_2, row.get("mezuniyet_2"))
        self.diploma_no_2.setText(str(row.get("diploma_no_2") or ""))

        foto_yolu = str(row.get("fotograf") or "").strip()
        if foto_yolu:
            self._foto_yolu = foto_yolu
            self._foto_goster(foto_yolu)

    def _on_fotograf_sec(self) -> None:
        """Dosya diyalogu acar, secilen resmi onizleme olarak gosterir."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Fotograf Sec",
            "",
            "Resim Dosyalari (*.jpg *.jpeg *.png *.bmp);;Tum Dosyalar (*)",
        )
        if not path:
            return
        self._foto_yolu = path
        self._foto_degisti = True
        self._foto_goster(path)

    def _foto_goster(self, yol: str) -> None:
        """Verilen dosya yolundaki resmi foto kutusuna yukler."""
        if not yol or not Path(yol).is_file():
            return
        pix = QPixmap(yol)
        if pix.isNull():
            self._alert.goster("Resim okunamadi.", "warning")
            return
        w = self._foto_lbl.width() or 220
        h = self._foto_lbl.minimumHeight() or 140
        scaled = pix.scaled(
            w, h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._foto_lbl.setPixmap(scaled)
        self._foto_lbl.setText("")

    @staticmethod
    def _set_date(widget: QDateEdit, value) -> None:
        parsed = parse_tarih(value)
        if not parsed:
            return
        qd = QDate(parsed.year, parsed.month, parsed.day)
        if qd.isValid():
            widget.setDate(qd)

    def _validate(self) -> list[str]:
        errors: list[str] = []

        tc = self.tc.text().strip()
        if not tc:
            errors.append("TC Kimlik No zorunlu.")
        elif not validate_tc_kimlik_no(tc):
            errors.append("Gecersiz TC Kimlik No.")

        if not normalize_whitespace(self.ad.text()):
            errors.append("Ad zorunlu.")
        if not normalize_whitespace(self.soyad.text()):
            errors.append("Soyad zorunlu.")

        email = self.e_posta.text().strip()
        if email and not validate_email(email):
            errors.append("E-posta formati gecersiz.")

        phone = self.telefon.text().strip()
        if phone and not validate_phone_number(phone):
            errors.append("Telefon formati gecersiz.")

        return errors

    def _payload(self) -> dict:
        return {
            "tc_kimlik": self.tc.text().strip(),
            "ad": turkish_title_case(normalize_whitespace(self.ad.text())),
            "soyad": turkish_title_case(normalize_whitespace(self.soyad.text())),
            "dogum_yeri": turkish_title_case(normalize_whitespace(self.dogum_yeri.currentText())),
            "dogum_tarihi": format_tarih(self.dogum_tarihi.date().toPython(), ui=False),
            "hizmet_sinifi": self.hizmet_sinifi.currentText().strip(),
            "kadro_unvani": self.kadro_unvani.currentText().strip(),
            "gorev_yeri_ad": self.gorev_yeri.currentText().strip(),
            "sicil_no": capitalize_first_letter(normalize_whitespace(self.sicil_no.text())),
            "memuriyet_baslama": format_tarih(self.memuriyet_baslama.date().toPython(), ui=False) or bugun(),
            "telefon": format_phone_number(normalize_whitespace(self.telefon.text())),
            "e_posta": turkish_lower(normalize_whitespace(self.e_posta.text())),
            "okul_1": turkish_title_case(normalize_whitespace(self.okul_1.currentText())),
            "fakulte_1": turkish_title_case(normalize_whitespace(self.fakulte_1.currentText())),
            "mezuniyet_1": format_tarih(self.mezuniyet_1.date().toPython(), ui=False),
            "diploma_no_1": capitalize_first_letter(normalize_whitespace(self.diploma_no_1.text())),
            "okul_2": turkish_title_case(normalize_whitespace(self.okul_2.currentText())),
            "fakulte_2": turkish_title_case(normalize_whitespace(self.fakulte_2.currentText())),
            "mezuniyet_2": format_tarih(self.mezuniyet_2.date().toPython(), ui=False),
            "diploma_no_2": capitalize_first_letter(normalize_whitespace(self.diploma_no_2.text())),
        }

    def _on_save(self) -> None:
        errors = self._validate()
        if errors:
            self._alert.goster("\n".join(errors), "warning")
            return

        payload = self._payload()
        self.btn_save.setEnabled(False)

        def _run() -> dict:
            if self._is_edit:
                pid = self._personel_id
                if not pid:
                    current = self._svc.tc_ile_getir(payload["tc_kimlik"])
                    pid = str(current.get("id") or "").strip()
                    if not pid:
                        raise KayitBulunamadi("Guncellenecek personel bulunamadi.")
                self._svc.guncelle(pid, payload)
                return {
                    "personel_id": pid,
                    "kullanici_adi": "-",
                    "gecici_parola": "-",
                    "izin_hak": 0,
                    "hizmet_yili": 0,
                    "is_edit": True,
                }
            data = self._onboarding.kaydet_ve_hazirla(payload)
            data["is_edit"] = False
            return data

        def _done(result: dict) -> None:
            self.btn_save.setEnabled(True)
            self._personel_id = str(result.get("personel_id") or "")

            # ── Fotograf kopyalama ────────────────────────────────
            if self._foto_degisti and self._foto_yolu and self._personel_id:
                try:
                    src = Path(self._foto_yolu)
                    if src.is_file():
                        tc = self.tc.text().strip()
                        klasor = BELGE_DIR / "personel" / (tc or self._personel_id)
                        klasor.mkdir(parents=True, exist_ok=True)
                        tarih = bugun()
                        dosya_kimlik = tc or self._personel_id
                        dest = klasor / f"{dosya_kimlik}_fotograf_{tarih}{src.suffix.lower()}"
                        i = 1
                        while dest.exists():
                            dest = klasor / f"{dosya_kimlik}_fotograf_{tarih}_{i}{src.suffix.lower()}"
                            i += 1
                        shutil.copy2(src, dest)
                        self._svc.guncelle(self._personel_id, {"fotograf": str(dest)})
                        self._foto_yolu = str(dest)
                        self._foto_degisti = False
                except Exception as exc:
                    exc_logla("PersonelEklePage._done.foto", exc)
                    self._alert.goster("Fotograf kaydedilemedi.", "warning")
            # ─────────────────────────────────────────────────────

            if self._on_saved:
                self._on_saved()

            if bool(result.get("is_edit")):
                self._alert.goster("Kayit guncellendi.", "success")
                self.form_closed.emit()
                return

            self._docs_tab.set_entity("personel", self._personel_id, self.tc.text().strip())
            self._tabs.setTabEnabled(1, True)
            self._tabs.setCurrentIndex(1)
            self.tc.setEnabled(False)

            self._alert.goster(
                "Kayit tamamlandi. Kullanici: "
                f"{result.get('kullanici_adi')} | Gecici parola: {result.get('gecici_parola')} | "
                f"Yillik hak: {result.get('izin_hak')} gun",
                "success",
            )

        def _err(msg: str) -> None:
            self.btn_save.setEnabled(True)
            self._alert.goster(msg, "danger")

        AsyncRunner(fn=_run, on_done=_done, on_error=_err, parent=self).start()
