# -*- coding: utf-8 -*-
"""
ui/pages/personel/panels/kimlik_panel.py
�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?
Personel kimlik bilgilerini gösteren ve düzenleyen panel.

Görünüm/Düzenleme ayrımı:
  - Varsayılan: salt okunur
  - "Düzenle" butonuna basınca alanlar aktif olur
  - "Kaydet" �?' servis �?' ba�Yarılıysa tekrar salt okunur
  - "İptal" �?' de�Yi�Yiklikler geri alınır
"""
from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QGroupBox,
    QScrollArea, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ui.styles import T
from ui.components.buttons import PrimaryButton, GhostButton, DangerButton
from ui.components.alerts import AlertBar
from ui.components.badges import Badge


class KimlikPanel(QWidget):
    """
    Personel kimlik bilgileri paneli.

    Sinyaller:
        kaydedildi(personel_id) �?" ba�Yarılı kayıt sonrası
        pasife_alindi(personel_id) �?" pasife alma sonrası

    Kullanım:
        panel = KimlikPanel(svc)
        panel.yukle(personel_id)
    """

    kaydedildi    = Signal(str)
    pasife_alindi = Signal(str)

    def __init__(self, svc, parent=None):
        super().__init__(parent)
        self._svc        = svc
        self._personel   = None   # Mevcut kayıt dict
        self._duzenleme  = False
        self._alanlar: dict[str, QLineEdit | QComboBox] = {}
        self._build()

    # �"?�"? UI �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?

    def _build(self):
        kok = QVBoxLayout(self)
        kok.setContentsMargins(0, 0, 0, 0)
        kok.setSpacing(12)

        # Uyarı bandı
        self._alert = AlertBar(self)
        kok.addWidget(self._alert)

        # Scroll alanı
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        icerik = QWidget()
        icerik_lay = QVBoxLayout(icerik)
        icerik_lay.setContentsMargins(20, 16, 20, 16)
        icerik_lay.setSpacing(16)

        # �"?�"? Ba�Ylık satırı �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?
        baslik_lay = QHBoxLayout()
        self._lbl_baslik = QLabel("�?"")
        f = QFont()
        f.setPointSize(16)
        f.setBold(True)
        self._lbl_baslik.setFont(f)
        self._lbl_durum = Badge("aktif")
        baslik_lay.addWidget(self._lbl_baslik)
        baslik_lay.addWidget(self._lbl_durum)
        baslik_lay.addStretch()

        from ui.styles.icons import ic as _ic
        from PySide6.QtCore import QSize as _QS
        self._btn_duzenle = GhostButton("  Düzenle")
        self._btn_duzenle.setIcon(_ic("duzenle", size=14, color=T.text2))
        self._btn_duzenle.setIconSize(_QS(14, 14))
        self._btn_duzenle.clicked.connect(self._duzenleme_baslat)
        self._btn_kaydet  = PrimaryButton("  Kaydet")
        self._btn_kaydet.setIcon(_ic("kaydet", size=14, color="white"))
        self._btn_kaydet.setIconSize(_QS(14, 14))
        self._btn_kaydet.clicked.connect(self._kaydet)
        self._btn_kaydet.setVisible(False)
        self._btn_iptal   = GhostButton("İptal")
        self._btn_iptal.clicked.connect(self._duzenleme_iptal)
        self._btn_iptal.setVisible(False)
        baslik_lay.addWidget(self._btn_iptal)
        baslik_lay.addWidget(self._btn_kaydet)
        baslik_lay.addWidget(self._btn_duzenle)
        icerik_lay.addLayout(baslik_lay)

        # �"?�"? Ki�Yisel Bilgiler �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?
        icerik_lay.addWidget(self._grup_olustur("Ki�Yisel Bilgiler", [
            ("tc_kimlik",         "TC Kimlik No",        False),  # hiç düzenlenemez
            ("ad",                "Ad",                  True),
            ("soyad",             "Soyad",               True),
            ("dogum_tarihi",      "Do�Yum Tarihi",        True),
            ("dogum_yeri",        "Do�Yum Yeri",          True),
        ]))

        # �"?�"? Görev Bilgileri �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?
        icerik_lay.addWidget(self._grup_olustur_combo("Görev Bilgileri", [
            ("hizmet_sinifi",    "Hizmet Sınıfı"),
            ("kadro_unvani",     "Kadro Unvanı"),
        ], text_alanlar=[
            ("gorev_yeri_ad",   "Görev Yeri"),
            ("sicil_no",        "Sicil No"),
            ("memuriyet_baslama", "Memuriyet Ba�Ylama"),
        ]))

        # �"?�"? İleti�Yim �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?
        icerik_lay.addWidget(self._grup_olustur("İleti�Yim", [
            ("telefon", "Telefon", True),
            ("e_posta", "E-posta", True),
        ]))

        # �"?�"? E�Yitim 1 �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?
        icerik_lay.addWidget(self._grup_olustur("1. E�Yitim", [
            ("okul_1",       "Okul",           True),
            ("fakulte_1",    "Fakülte",        True),
            ("mezuniyet_1",  "Mezuniyet",      True),
            ("diploma_no_1", "Diploma No",     True),
        ]))

        # �"?�"? E�Yitim 2 �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?
        icerik_lay.addWidget(self._grup_olustur("2. E�Yitim (varsa)", [
            ("okul_2",       "Okul",           True),
            ("fakulte_2",    "Fakülte",        True),
            ("mezuniyet_2",  "Mezuniyet",      True),
            ("diploma_no_2", "Diploma No",     True),
        ]))

        # �"?�"? Ayrılı�Y (pasifse) �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?
        self._ayrilik_grup = self._grup_olustur("Ayrılı�Y Bilgileri", [
            ("ayrilik_tarihi", "Ayrılı�Y Tarihi", False),
            ("ayrilik_nedeni", "Ayrılma Nedeni", False),
        ])
        self._ayrilik_grup.setVisible(False)
        icerik_lay.addWidget(self._ayrilik_grup)

        icerik_lay.addStretch()
        scroll.setWidget(icerik)
        kok.addWidget(scroll, 1)

        # �"?�"? Alt butonlar (tehlikeli i�Ylemler) �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?
        alt_lay = QHBoxLayout()
        alt_lay.setContentsMargins(20, 0, 20, 16)
        alt_lay.addStretch()
        self._btn_pasif = DangerButton("Personeli Pasife Al")
        self._btn_pasif.clicked.connect(self._pasife_al)
        self._btn_pasif.setVisible(False)
        alt_lay.addWidget(self._btn_pasif)
        kok.addLayout(alt_lay)

    def _grup_olustur(self, baslik: str,
                      alanlar: list[tuple]) -> QGroupBox:
        """(db_key, etiket, duzenlenebilir) listesinden GroupBox olu�Yturur."""
        gb  = QGroupBox(baslik)
        grid = QGridLayout(gb)
        grid.setContentsMargins(12, 10, 12, 10)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(8)

        for i, (key, etiket, duzenlenebilir) in enumerate(alanlar):
            lbl = QLabel(etiket + ":")
            lbl.setStyleSheet(f"color:{T.text2}; font-size:12px;")
            lbl.setFixedWidth(150)
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            edit = QLineEdit()
            edit.setReadOnly(True)
            edit.setProperty("_duzenlenebilir", duzenlenebilir)
            edit.setStyleSheet(
                f"background:{T.bg1}; border:1px solid {T.border};"
                f"border-radius:6px; padding:6px 10px; color:{T.text};"
            )
            grid.addWidget(lbl, i, 0)
            grid.addWidget(edit, i, 1)
            self._alanlar[key] = edit

        grid.setColumnStretch(1, 1)
        return gb

    def _grup_olustur_combo(self, baslik: str,
                             combo_alanlar: list[tuple],
                             text_alanlar: list[tuple] | None = None) -> QGroupBox:
        """Karı�Yık combo + text input'lu grup."""
        gb   = QGroupBox(baslik)
        grid = QGridLayout(gb)
        grid.setContentsMargins(12, 10, 12, 10)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(8)
        satir = 0

        for key, etiket in combo_alanlar:
            lbl = QLabel(etiket + ":")
            lbl.setStyleSheet(f"color:{T.text2}; font-size:12px;")
            lbl.setFixedWidth(150)
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            combo = QComboBox()
            combo.setEnabled(False)
            grid.addWidget(lbl, satir, 0)
            grid.addWidget(combo, satir, 1)
            self._alanlar[key] = combo
            satir += 1

        for key, etiket in (text_alanlar or []):
            lbl = QLabel(etiket + ":")
            lbl.setStyleSheet(f"color:{T.text2}; font-size:12px;")
            lbl.setFixedWidth(150)
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            edit = QLineEdit()
            edit.setReadOnly(True)
            edit.setProperty("_duzenlenebilir", True)
            edit.setStyleSheet(
                f"background:{T.bg1}; border:1px solid {T.border};"
                f"border-radius:6px; padding:6px 10px; color:{T.text};"
            )
            grid.addWidget(lbl, satir, 0)
            grid.addWidget(edit, satir, 1)
            self._alanlar[key] = edit
            satir += 1

        grid.setColumnStretch(1, 1)
        return gb

    # �"?�"? Veri Yükleme �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?

    def yukle(self, personel_id: str) -> None:
        """Personeli yükler ve alanları doldurur."""
        from ui.components.async_runner import AsyncRunner

        def _cek():
            return self._svc.getir(personel_id)

        def _goster(p: dict):
            self._personel = p
            self._doldur(p)
            self._alert.temizle()

        def _hata(msg: str):
            self._alert.goster(msg)

        AsyncRunner(fn=_cek, on_done=_goster, on_error=_hata, parent=self).start()

    def _doldur(self, p: dict) -> None:
        """Dict verisiyle alanları doldurur."""
        ad_soyad = f"{p.get('ad', '')} {p.get('soyad', '')}".strip()
        self._lbl_baslik.setText(ad_soyad or "�?"")
        self._lbl_durum.set(p.get("durum", "aktif"))

        # Görev yeri adını da al (JOIN ile gelmi�Y olabilir)
        if "gorev_yeri_ad" in self._alanlar:
            gy_ad = p.get("gorev_yeri_ad") or ""
            alan = self._alanlar["gorev_yeri_ad"]
            if isinstance(alan, QLineEdit):
                alan.setText(gy_ad)

        for key, widget in self._alanlar.items():
            if key == "gorev_yeri_ad":
                continue   # Yukarıda hallettik
            val = p.get(key) or ""
            if isinstance(widget, QLineEdit):
                widget.setText(str(val))
            elif isinstance(widget, QComboBox):
                # Combo'ya veriyi doldur
                self._combo_doldur_ve_sec(widget, key, str(val))

        # Ayrılı�Y grubu görünürlü�Yü
        self._ayrilik_grup.setVisible(p.get("durum") == "ayrildi")
        self._btn_pasif.setVisible(p.get("durum") == "aktif")

    def _combo_doldur_ve_sec(self, combo: QComboBox,
                              key: str, secili: str) -> None:
        """Combo'yu servis verisiyle doldurur ve mevcut de�Yeri seçer."""
        combo.clear()
        combo.addItem("�?" Seçiniz �?"", "")

        liste = []
        if key == "hizmet_sinifi":
            liste = self._svc.hizmet_siniflari()
        elif key == "kadro_unvani":
            liste = self._svc.kadro_unvanlari()

        for d in liste:
            combo.addItem(d, d)

        idx = combo.findData(secili)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    # �"?�"? Düzenleme Modu �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?

    def _duzenleme_baslat(self) -> None:
        self._duzenleme = True
        self._btn_duzenle.setVisible(False)
        self._btn_kaydet.setVisible(True)
        self._btn_iptal.setVisible(True)
        self._btn_pasif.setVisible(False)

        for key, widget in self._alanlar.items():
            if key == "tc_kimlik":
                continue   # TC hiç de�Yi�Ytirilemez
            if isinstance(widget, QLineEdit):
                if widget.property("_duzenlenebilir"):
                    widget.setReadOnly(False)
                    widget.setStyleSheet(
                        f"background:{T.bg4}; border:1px solid {T.accent};"
                        f"border-radius:6px; padding:6px 10px; color:{T.text};"
                    )
            elif isinstance(widget, QComboBox):
                widget.setEnabled(True)

    def _duzenleme_iptal(self) -> None:
        self._duzenleme = False
        self._btn_duzenle.setVisible(True)
        self._btn_kaydet.setVisible(False)
        self._btn_iptal.setVisible(False)
        if self._personel:
            self._doldur(self._personel)
        self._salt_okunur_yap()
        self._alert.temizle()

    def _salt_okunur_yap(self) -> None:
        for widget in self._alanlar.values():
            if isinstance(widget, QLineEdit):
                widget.setReadOnly(True)
                widget.setStyleSheet(
                    f"background:{T.bg1}; border:1px solid {T.border};"
                    f"border-radius:6px; padding:6px 10px; color:{T.text};"
                )
            elif isinstance(widget, QComboBox):
                widget.setEnabled(False)

    # �"?�"? Kaydet �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?

    def _kaydet(self) -> None:
        if not self._personel:
            return

        veri = {}
        for key, widget in self._alanlar.items():
            if key == "tc_kimlik":
                continue
            if isinstance(widget, QLineEdit):
                veri[key] = widget.text().strip()
            elif isinstance(widget, QComboBox):
                veri[key] = widget.currentData() or ""

        pid = self._personel["id"]

        try:
            self._svc.guncelle(pid, veri)
            # Güncel veriyi yeniden yükle
            self._personel = self._svc.getir(pid)
            self._doldur(self._personel)
            self._duzenleme = False
            self._btn_duzenle.setVisible(True)
            self._btn_kaydet.setVisible(False)
            self._btn_iptal.setVisible(False)
            self._salt_okunur_yap()
            self._alert.goster("Bilgiler kaydedildi.", "success")
            self.kaydedildi.emit(pid)
        except Exception as e:
            self._alert.goster(str(e))

    # �"?�"? Pasife Al �"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?�"?

    def _pasife_al(self) -> None:
        if not self._personel:
            return
        from PySide6.QtWidgets import QInputDialog, QDialog
        tarih, ok = QInputDialog.getText(
            self, "Pasife Al",
            "Ayrılı�Y tarihi (YYYY-MM-DD):",
        )
        if not ok or not tarih.strip():
            return
        try:
            self._svc.pasife_al(self._personel["id"], tarih.strip())
            self._personel = self._svc.getir(self._personel["id"])
            self._doldur(self._personel)
            self._alert.goster("Personel pasife alındı.", "warning")
            self.pasife_alindi.emit(self._personel["id"])
        except Exception as e:
            self._alert.goster(str(e))


