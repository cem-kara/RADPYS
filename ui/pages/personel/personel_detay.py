# -*- coding: utf-8 -*-
"""Personel detay/duzenleme formu.

Tasarim ve davranis olarak PersonelEklePage ile ayni kalir,
ancak bu form yalnizca duzenleme akisi icin kullanilir.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QDateEdit, QHBoxLayout, QLabel, QLineEdit, QWidget

from app.text_utils import (
    capitalize_first_letter,
    format_phone_number,
    normalize_whitespace,
    turkish_lower,
    turkish_title_case,
)
from app.validators import format_tarih, validate_email, validate_phone_number
from ui.components import IconButton
from ui.pages.personel.detail_tabs import build_detail_tab_registrations
from ui.pages.personel.personel_ekle import PersonelEklePage
from ui.styles import T
from ui.styles.icons import ic


class PersonelDetayPage(PersonelEklePage):
    """Personel duzenleme icin ayrilmis form."""

    def __init__(self, db, edit_data: dict, on_saved=None, parent=None):
        super().__init__(db=db, edit_data=edit_data or {}, on_saved=on_saved, parent=parent)
        self._detail_tabs: dict[str, dict] = {}
        self._section_states: dict[str, bool] = {
            "iletisim": False,
            "kurumsal": False,
            "egitim": False,
        }
        self._section_snapshots: dict[str, dict] = {
            "iletisim": {},
            "kurumsal": {},
            "egitim": {},
        }
        self._install_detail_tabs(db)
        self._install_section_actions()
        self._apply_readonly_mode()

    def _current_memuriyet_baslama_iso(self) -> str:
        return format_tarih(self.memuriyet_baslama.date().toPython(), ui=False)

    def _install_detail_tabs(self, db) -> None:
        for reg in build_detail_tab_registrations():
            widget = reg.factory(self, db)
            self._tabs.addTab(widget, reg.label)
            self._detail_tabs[reg.tab_id] = {
                "widget": widget,
                "refresh_on_sections": set(reg.refresh_on_sections),
            }
            if hasattr(widget, "yenile"):
                widget.yenile()

    def _refresh_detail_tabs(self, section_name: str | None = None) -> None:
        for meta in self._detail_tabs.values():
            refresh_on = meta.get("refresh_on_sections", set())
            if section_name and refresh_on and section_name not in refresh_on:
                continue
            widget = meta.get("widget")
            if hasattr(widget, "yenile"):
                widget.yenile()

    def _install_section_actions(self) -> None:
        self._lbl_iletisim = QLabel()
        self._btn_iletisim = IconButton(size=26, compact=True)
        self._btn_iletisim.clicked.connect(lambda: self._save_or_edit_section("iletisim"))
        self._btn_iletisim_cancel = IconButton(size=26, compact=True)
        self._btn_iletisim_cancel.clicked.connect(lambda: self._cancel_section("iletisim"))
        self._lay_iletisim.addWidget(
            self._action_bar(self._lbl_iletisim, self._btn_iletisim, self._btn_iletisim_cancel),
            0,
            1,
            1,
            1,
            Qt.AlignmentFlag.AlignRight,
        )

        self._lbl_kurumsal = QLabel()
        self._btn_kurumsal = IconButton(size=26, compact=True)
        self._btn_kurumsal.clicked.connect(lambda: self._save_or_edit_section("kurumsal"))
        self._btn_kurumsal_cancel = IconButton(size=26, compact=True)
        self._btn_kurumsal_cancel.clicked.connect(lambda: self._cancel_section("kurumsal"))
        self._lay_kurumsal.addWidget(
            self._action_bar(self._lbl_kurumsal, self._btn_kurumsal, self._btn_kurumsal_cancel),
            0,
            2,
            1,
            1,
            Qt.AlignmentFlag.AlignRight,
        )

        self._lbl_egitim = QLabel()
        self._btn_egitim = IconButton(size=26, compact=True)
        self._btn_egitim.clicked.connect(lambda: self._save_or_edit_section("egitim"))
        self._btn_egitim_cancel = IconButton(size=26, compact=True)
        self._btn_egitim_cancel.clicked.connect(lambda: self._cancel_section("egitim"))
        self._lay_egitim.addWidget(
            self._action_bar(self._lbl_egitim, self._btn_egitim, self._btn_egitim_cancel),
            0,
            3,
            1,
            1,
            Qt.AlignmentFlag.AlignRight,
        )

    def _action_bar(self, status_lbl: QLabel, button: IconButton, cancel_button: IconButton) -> QWidget:
        host = QWidget(self)
        lay = QHBoxLayout(host)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        status_lbl.setStyleSheet(
            f"color:{T.text3};font-size:10px;padding:2px 8px;"
            f"background:{T.overlay_low};border:1px solid {T.border};border-radius:9px;"
        )
        lay.addWidget(status_lbl)
        lay.addWidget(button)
        lay.addWidget(cancel_button)
        return host

    def _apply_readonly_mode(self) -> None:
        self.btn_save.setVisible(False)
        self.btn_fotograf.setEnabled(False)

        for widget in [self.tc, self.ad, self.soyad, self.dogum_yeri, self.dogum_tarihi]:
            self._set_widget_enabled(widget, False)

        for name in ("iletisim", "kurumsal", "egitim"):
            self._set_section_enabled(name, False)
            self._refresh_section_ui(name)

    def _section_widgets(self, name: str) -> list:
        if name == "iletisim":
            return [self.telefon, self.e_posta]
        if name == "kurumsal":
            return [self.hizmet_sinifi, self.kadro_unvani, self.gorev_yeri, self.memuriyet_baslama, self.sicil_no]
        if name == "egitim":
            return [
                self.okul_1,
                self.fakulte_1,
                self.mezuniyet_1,
                self.diploma_no_1,
                self.okul_2,
                self.fakulte_2,
                self.mezuniyet_2,
                self.diploma_no_2,
            ]
        return []

    def _set_widget_enabled(self, widget, enabled: bool) -> None:
        if isinstance(widget, QLineEdit):
            widget.setReadOnly(not enabled)
            return
        if isinstance(widget, QComboBox):
            widget.setEnabled(enabled)
            if widget.isEditable():
                le = widget.lineEdit()
                if le is not None:
                    le.setReadOnly(not enabled)
            return
        if isinstance(widget, QDateEdit):
            widget.setEnabled(enabled)
            return
        widget.setEnabled(enabled)

    def _set_section_enabled(self, name: str, enabled: bool) -> None:
        for w in self._section_widgets(name):
            self._set_widget_enabled(w, enabled)

    def _section_payload(self, name: str) -> dict:
        if name == "iletisim":
            return {
                "telefon": format_phone_number(normalize_whitespace(self.telefon.text())),
                "e_posta": turkish_lower(normalize_whitespace(self.e_posta.text())),
            }
        if name == "kurumsal":
            return {
                "hizmet_sinifi": self.hizmet_sinifi.currentText().strip(),
                "kadro_unvani": self.kadro_unvani.currentText().strip(),
                "gorev_yeri_ad": self.gorev_yeri.currentText().strip(),
                "sicil_no": capitalize_first_letter(normalize_whitespace(self.sicil_no.text())),
                "memuriyet_baslama": format_tarih(self.memuriyet_baslama.date().toPython(), ui=False),
            }
        if name == "egitim":
            return {
                "okul_1": turkish_title_case(normalize_whitespace(self.okul_1.currentText())),
                "fakulte_1": turkish_title_case(normalize_whitespace(self.fakulte_1.currentText())),
                "mezuniyet_1": format_tarih(self.mezuniyet_1.date().toPython(), ui=False),
                "diploma_no_1": capitalize_first_letter(normalize_whitespace(self.diploma_no_1.text())),
                "okul_2": turkish_title_case(normalize_whitespace(self.okul_2.currentText())),
                "fakulte_2": turkish_title_case(normalize_whitespace(self.fakulte_2.currentText())),
                "mezuniyet_2": format_tarih(self.mezuniyet_2.date().toPython(), ui=False),
                "diploma_no_2": capitalize_first_letter(normalize_whitespace(self.diploma_no_2.text())),
            }
        return {}

    def _validate_section(self, name: str) -> str:
        if name != "iletisim":
            return ""

        email = self.e_posta.text().strip()
        if email and not validate_email(email):
            return "E-posta formati gecersiz."
        phone = self.telefon.text().strip()
        if phone and not validate_phone_number(phone):
            return "Telefon formati gecersiz."
        return ""

    def _section_button(self, name: str):
        if name == "iletisim":
            return self._btn_iletisim
        if name == "kurumsal":
            return self._btn_kurumsal
        return self._btn_egitim

    def _section_cancel_button(self, name: str):
        if name == "iletisim":
            return self._btn_iletisim_cancel
        if name == "kurumsal":
            return self._btn_kurumsal_cancel
        return self._btn_egitim_cancel

    def _section_status_label(self, name: str) -> QLabel:
        if name == "iletisim":
            return self._lbl_iletisim
        if name == "kurumsal":
            return self._lbl_kurumsal
        return self._lbl_egitim

    def _section_frame(self, name: str):
        if name == "iletisim":
            return self._frame_iletisim
        if name == "kurumsal":
            return self._frame_kurumsal
        return self._frame_egitim

    def _refresh_section_ui(self, name: str) -> None:
        is_editing = self._section_states.get(name, False)
        btn = self._section_button(name)
        cancel_btn = self._section_cancel_button(name)
        lbl = self._section_status_label(name)
        frame = self._section_frame(name)

        if is_editing:
            btn.setToolTip("Kaydet")
            btn.setIcon(ic("check", size=16, color=T.green2))
            btn.setStyleSheet(
                f"QPushButton{{background:{T.accent2};border:1px solid {T.accent2};border-radius:{T.radius_sm}px;}}"
            )
            cancel_btn.setToolTip("Iptal")
            cancel_btn.setIcon(ic("x", size=16, color=T.text2))
            cancel_btn.setVisible(True)
            lbl.setText("Duzenleniyor")
            lbl.setStyleSheet(
                f"color:{T.green2};font-size:10px;padding:2px 8px;"
                f"background:{T.overlay_low};border:1px solid {T.green2};border-radius:9px;"
            )
            frame.setStyleSheet(
                f"QFrame{{background:{T.bg1};border:1px solid {T.accent2};border-radius:{T.radius}px;}}"
            )
            return

        btn.setToolTip("Duzenle")
        btn.setIcon(ic("edit", size=16, color=T.text2))
        btn.setStyleSheet("")
        cancel_btn.setVisible(False)
        lbl.setText("Salt-okunur")
        lbl.setStyleSheet(
            f"color:{T.text3};font-size:10px;padding:2px 8px;"
            f"background:{T.overlay_low};border:1px solid {T.border};border-radius:9px;"
        )
        frame.setStyleSheet(
            f"QFrame{{background:{T.bg1};border:1px solid {T.border};border-radius:{T.radius}px;}}"
        )

    def _capture_section_snapshot(self, name: str) -> dict:
        if name == "iletisim":
            return {"telefon": self.telefon.text(), "e_posta": self.e_posta.text()}
        if name == "kurumsal":
            return {
                "hizmet_sinifi": self.hizmet_sinifi.currentText(),
                "kadro_unvani": self.kadro_unvani.currentText(),
                "gorev_yeri": self.gorev_yeri.currentText(),
                "sicil_no": self.sicil_no.text(),
                "memuriyet_baslama": self.memuriyet_baslama.date(),
            }
        if name == "egitim":
            return {
                "okul_1": self.okul_1.currentText(),
                "fakulte_1": self.fakulte_1.currentText(),
                "mezuniyet_1": self.mezuniyet_1.date(),
                "diploma_no_1": self.diploma_no_1.text(),
                "okul_2": self.okul_2.currentText(),
                "fakulte_2": self.fakulte_2.currentText(),
                "mezuniyet_2": self.mezuniyet_2.date(),
                "diploma_no_2": self.diploma_no_2.text(),
            }
        return {}

    def _restore_section_snapshot(self, name: str) -> None:
        snap = self._section_snapshots.get(name) or {}
        if not snap:
            return

        if name == "iletisim":
            self.telefon.setText(str(snap.get("telefon") or ""))
            self.e_posta.setText(str(snap.get("e_posta") or ""))
            return
        if name == "kurumsal":
            self.hizmet_sinifi.setCurrentText(str(snap.get("hizmet_sinifi") or ""))
            self.kadro_unvani.setCurrentText(str(snap.get("kadro_unvani") or ""))
            self.gorev_yeri.setCurrentText(str(snap.get("gorev_yeri") or ""))
            self.sicil_no.setText(str(snap.get("sicil_no") or ""))
            d = snap.get("memuriyet_baslama")
            if d is not None:
                self.memuriyet_baslama.setDate(d)
            return

        self.okul_1.setCurrentText(str(snap.get("okul_1") or ""))
        self.fakulte_1.setCurrentText(str(snap.get("fakulte_1") or ""))
        d1 = snap.get("mezuniyet_1")
        if d1 is not None:
            self.mezuniyet_1.setDate(d1)
        self.diploma_no_1.setText(str(snap.get("diploma_no_1") or ""))
        self.okul_2.setCurrentText(str(snap.get("okul_2") or ""))
        self.fakulte_2.setCurrentText(str(snap.get("fakulte_2") or ""))
        d2 = snap.get("mezuniyet_2")
        if d2 is not None:
            self.mezuniyet_2.setDate(d2)
        self.diploma_no_2.setText(str(snap.get("diploma_no_2") or ""))

    def _save_or_edit_section(self, name: str) -> None:
        is_editing = self._section_states.get(name, False)

        if not is_editing:
            self._section_snapshots[name] = self._capture_section_snapshot(name)
            self._set_section_enabled(name, True)
            self._section_states[name] = True
            self._refresh_section_ui(name)
            return

        err = self._validate_section(name)
        if err:
            self._alert.goster(err, "warning")
            return

        try:
            self._svc.guncelle(self._personel_id, self._section_payload(name))
        except Exception as exc:
            self._alert.goster(str(exc), "danger")
            return

        self._set_section_enabled(name, False)
        self._section_states[name] = False
        self._refresh_section_ui(name)
        self._alert.goster("Alan grubu guncellendi.", "success")
        self._refresh_detail_tabs(section_name=name)

        if self._on_saved:
            self._on_saved()

    def _cancel_section(self, name: str) -> None:
        if not self._section_states.get(name, False):
            return

        self._restore_section_snapshot(name)
        self._set_section_enabled(name, False)
        self._section_states[name] = False
        self._refresh_section_ui(name)
