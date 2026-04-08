# -*- coding: utf-8 -*-
"""ui/components/forms.py - modern form alanlari ve yardimci widget'lar."""
from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QComboBox, QTextEdit, QCheckBox,
    QRadioButton, QButtonGroup, QSpinBox, QDoubleSpinBox,
    QDateEdit, QSizePolicy, QPushButton, QFrame, QCalendarWidget,
)
from PySide6.QtCore import Qt, QDate, QSize, Signal
from ui.styles import T
from ui.styles.icons import ic, pixmap


# ï¿½"?ï¿½"? Ortak sabitler ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?
_ETIKET_STIL   = f"color:{T.text2}; font-size:11.5px; font-weight:500; background:transparent;"
_ZORUNLU_STIL  = f"color:{T.red};   font-size:12px;   font-weight:700; background:transparent;"
_YARDIM_STIL   = f"color:{T.text3}; font-size:10.5px; background:transparent;"
_HATA_STIL     = f"color:{T.red};   font-size:10.5px; background:transparent;"
_INPUT_HATA    = f"border: 1px solid {T.red};"


# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½
# FieldBase ï¿½?" tÃ¼m form alanlarÄ±nÄ±n temel sÄ±nÄ±fÄ±
# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

class FieldBase(QWidget):
    """
    Dikey dizili: [Etiket] ï¿½?' [Giriï¿½Y Widget] ï¿½?' [Hata/YardÄ±m SatÄ±rÄ±]

    Her alt sÄ±nÄ±f `_bitir(input_widget)` Ã§aï¿½YÄ±rmalÄ±dÄ±r.
    """

    def __init__(self, etiket: str, zorunlu: bool = False,
                 yardim: str = "", parent=None):
        super().__init__(parent)
        self._zorunlu     = zorunlu
        self._yardim_metin = yardim
        self._kuruldu     = False

        self._kok_lay = QVBoxLayout(self)
        self._kok_lay.setContentsMargins(0, 0, 0, 0)
        self._kok_lay.setSpacing(4)

        # ï¿½"?ï¿½"? Etiket satÄ±rÄ± ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?
        lbl_satir = QHBoxLayout()
        lbl_satir.setContentsMargins(0, 0, 0, 2)
        lbl_satir.setSpacing(3)

        self._lbl = QLabel(etiket)
        self._lbl.setStyleSheet(_ETIKET_STIL)
        lbl_satir.addWidget(self._lbl)

        if zorunlu:
            zr = QLabel("*")
            zr.setStyleSheet(_ZORUNLU_STIL)
            lbl_satir.addWidget(zr)

        lbl_satir.addStretch()
        self._kok_lay.addLayout(lbl_satir)

        # ï¿½"?ï¿½"? Alt bilgi satÄ±rÄ± ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?
        self._alt_lbl = QLabel()
        self._alt_lbl.setWordWrap(True)
        self._alt_lbl.setStyleSheet(_YARDIM_STIL)
        self._alt_lbl.setVisible(bool(yardim))
        if yardim:
            self._alt_lbl.setText(yardim)

    def _bitir(self, input_widget: QWidget) -> None:
        """Alt sÄ±nÄ±f: giriï¿½Y widget'Ä± oluï¿½Yturduktan sonra Ã§aï¿½YÄ±rÄ±r."""
        self._kok_lay.addWidget(input_widget)
        self._kok_lay.addWidget(self._alt_lbl)
        self._kuruldu = True

    # ï¿½"?ï¿½"? Doï¿½Yrulama API ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?

    def hata_goster(self, mesaj: str) -> None:
        """KÄ±rmÄ±zÄ± hata metni gÃ¶ster, input kenarlÄ±ï¿½YÄ±nÄ± kÄ±rmÄ±zÄ± yap."""
        self._alt_lbl.setText(mesaj)
        self._alt_lbl.setStyleSheet(_HATA_STIL)
        self._alt_lbl.setVisible(True)
        self._hata_stil_uygula(True)

    def hata_temizle(self) -> None:
        """Hata gÃ¶rÃ¼nÃ¼mÃ¼nÃ¼ sÄ±fÄ±rla."""
        self._hata_stil_uygula(False)
        if self._yardim_metin:
            self._alt_lbl.setText(self._yardim_metin)
            self._alt_lbl.setStyleSheet(_YARDIM_STIL)
            self._alt_lbl.setVisible(True)
        else:
            self._alt_lbl.setVisible(False)

    def _hata_stil_uygula(self, hata: bool) -> None:
        """Alt sÄ±nÄ±f override eder ï¿½?" input kenarlÄ±ï¿½YÄ±nÄ± deï¿½Yiï¿½Ytirir."""

    # ï¿½"?ï¿½"? Veri API (alt sÄ±nÄ±f implement eder) ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?

    def deger(self):
        raise NotImplementedError

    def set_deger(self, v) -> None:
        raise NotImplementedError

    def zorunlu_mu(self) -> bool:
        return self._zorunlu


# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½
# TextField
# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

class TextField(FieldBase):
    """
    Tek satÄ±rlÄ± metin giriï¿½Yi.

    KullanÄ±m:
        alan = TextField("Ad Soyad", zorunlu=True, ikon="profil")
        alan = TextField("TC Kimlik No", max_uzunluk=11, ikon="tc")
        deger = alan.deger()         # str (trimmed)
        alan.set_deger("Ali Kaya")
        alan.hata_goster("Zorunlu alan")
    """

    deger_degisti = Signal(str)   # QLineEdit.textChanged karï¿½YÄ±lÄ±ï¿½YÄ±

    def __init__(self, etiket: str, zorunlu: bool = False,
                 placeholder: str = "", ikon: str = "",
                 max_uzunluk: int = 0, yardim: str = "",
                 parent=None):
        super().__init__(etiket, zorunlu, yardim, parent)

        self._line = QLineEdit()
        self._line.setMinimumHeight(T.input_h)
        if placeholder:
            self._line.setPlaceholderText(placeholder)
        if max_uzunluk:
            self._line.setMaxLength(max_uzunluk)
        if ikon:
            self._line.addAction(
                ic(ikon, size=T.icon_sm, color=T.text3),
                QLineEdit.ActionPosition.LeadingPosition,
            )
        self._line.setClearButtonEnabled(True)
        self._line.textChanged.connect(self.deger_degisti)

        self._bitir(self._line)

    def deger(self) -> str:
        return self._line.text().strip()

    def set_deger(self, v) -> None:
        self._line.setText(str(v) if v is not None else "")

    def _hata_stil_uygula(self, hata: bool) -> None:
        self._line.setStyleSheet(_INPUT_HATA if hata else "")

    # Ham widget eriï¿½Yimi (Ã¶zel durumlar iÃ§in)
    @property
    def line_edit(self) -> QLineEdit:
        return self._line


# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½
# PasswordField
# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

class PasswordField(FieldBase):
    """
    Åifre giriï¿½Yi ï¿½?" saï¿½Yda gÃ¶ster/gizle butonu.

    KullanÄ±m:
        alan = PasswordField("Åifre", zorunlu=True)
        sifre = alan.deger()
    """

    def __init__(self, etiket: str, zorunlu: bool = False,
                 yardim: str = "", parent=None):
        super().__init__(etiket, zorunlu, yardim, parent)

        kap = QWidget()
        kap_lay = QHBoxLayout(kap)
        kap_lay.setContentsMargins(0, 0, 0, 0)
        kap_lay.setSpacing(4)

        self._line = QLineEdit()
        self._line.setMinimumHeight(T.input_h)
        self._line.setEchoMode(QLineEdit.EchoMode.Password)
        self._line.addAction(
            ic("parola", size=T.icon_sm, color=T.text3),
            QLineEdit.ActionPosition.LeadingPosition,
        )

        self._btn_goz = QPushButton()
        self._btn_goz.setFixedSize(T.input_h, T.input_h)
        self._btn_goz.setProperty("ghost", "true")
        self._btn_goz.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_goz.setIcon(ic("goz_kapali", size=T.icon_sm, color=T.text3))
        self._btn_goz.setIconSize(QSize(T.icon_sm, T.icon_sm))
        self._btn_goz.setToolTip("Åifreyi gÃ¶ster")
        self._btn_goz.setCheckable(True)
        self._btn_goz.toggled.connect(self._toggle_gozuk)

        kap_lay.addWidget(self._line, 1)
        kap_lay.addWidget(self._btn_goz)

        self._bitir(kap)

    def _toggle_gozuk(self, goster: bool) -> None:
        if goster:
            self._line.setEchoMode(QLineEdit.EchoMode.Normal)
            self._btn_goz.setIcon(ic("goz", size=T.icon_sm, color=T.accent))
            self._btn_goz.setToolTip("Åifreyi gizle")
        else:
            self._line.setEchoMode(QLineEdit.EchoMode.Password)
            self._btn_goz.setIcon(ic("goz_kapali", size=T.icon_sm, color=T.text3))
            self._btn_goz.setToolTip("Åifreyi gÃ¶ster")

    def deger(self) -> str:
        return self._line.text()

    def set_deger(self, v) -> None:
        self._line.setText(str(v) if v is not None else "")

    def _hata_stil_uygula(self, hata: bool) -> None:
        self._line.setStyleSheet(_INPUT_HATA if hata else "")


# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½
# DateField
# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

class DateField(FieldBase):
    """
    Tarih seÃ§ici ï¿½?" QDateEdit, TÃ¼rk gÃ¶rÃ¼ntÃ¼ formatÄ±, ISO Ã§Ä±ktÄ±.

    KullanÄ±m:
        alan = DateField("Doï¿½Yum Tarihi", zorunlu=True)
        iso_str = alan.deger()           # "2000-04-08" | ""
        alan.set_deger("2000-04-08")     # veya QDate
    """

    def __init__(self, etiket: str, zorunlu: bool = False,
                 yardim: str = "", parent=None):
        super().__init__(etiket, zorunlu, yardim, parent)

        self._date_edit = QDateEdit()
        self._date_edit.setMinimumHeight(T.input_h)
        self._date_edit.setDisplayFormat("dd.MM.yyyy")
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setSpecialValueText(" ")          # boï¿½Y gÃ¶rÃ¼nÃ¼m
        self._date_edit.setDate(QDate())                  # geÃ§ersiz = boï¿½Y
        self._date_edit.setMinimumDate(QDate(1900, 1, 1))
        self._date_edit.setMaximumDate(QDate(2100, 12, 31))

        # Popup takvim boyutunu form iÃ§inde daha estetik bir Ã¶lÃ§Ã¼ye sabitle.
        cal = self._date_edit.calendarWidget()
        if cal is not None:
            cal.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
            cal.setGridVisible(False)
            cal.setFixedSize(292, 236)

        self._date_edit.setToolTip("Takvimden tarih sec")

        self._bitir(self._date_edit)

    def deger(self) -> str:
        """ISO-8601 string dÃ¶ner. Alan boï¿½Y ise '' dÃ¶ner."""
        d = self._date_edit.date()
        if not d.isValid() or d == QDate():
            return ""
        return d.toString("yyyy-MM-dd")

    def set_deger(self, v) -> None:
        if v is None or v == "":
            self._date_edit.setDate(QDate())
            return
        if isinstance(v, QDate):
            self._date_edit.setDate(v)
        else:
            d = QDate.fromString(str(v), "yyyy-MM-dd")
            self._date_edit.setDate(d if d.isValid() else QDate())

    def _hata_stil_uygula(self, hata: bool) -> None:
        self._date_edit.setStyleSheet(_INPUT_HATA if hata else "")


# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½
# ComboField
# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

class ComboField(FieldBase):
    """
    AÃ§Ä±lÄ±r liste seÃ§imi.

    KullanÄ±m:
        alan = ComboField("Hizmet SÄ±nÄ±fÄ±", zorunlu=True)
        alan.doldur(["SHS", "GHS", "THS"])
        alan.doldur([("SHS", "shs_kodu"), ("GHS", "ghs_kodu")])   # (etiket, data)
        secim = alan.deger()    # currentData (str)
        alan.set_deger("shs_kodu")
    """

    secim_degisti = Signal(str)   # currentData

    def __init__(self, etiket: str, zorunlu: bool = False,
                 bos_secim: bool = True, yardim: str = "",
                 parent=None):
        super().__init__(etiket, zorunlu, yardim, parent)
        self._bos_secim = bos_secim

        self._combo = QComboBox()
        self._combo.setMinimumHeight(T.input_h)
        self._combo.currentIndexChanged.connect(
            lambda _: self.secim_degisti.emit(self.deger())
        )

        self._bitir(self._combo)

    def doldur(self, degerler: list, bos_secim: bool | None = None) -> None:
        """
        degerler: list[str] veya list[tuple[str, str]] (etiket, data)
        """
        if bos_secim is None:
            bos_secim = self._bos_secim

        self._combo.clear()
        if bos_secim:
            self._combo.addItem("-- Seciniz --", "")
        for d in degerler:
            if isinstance(d, (list, tuple)) and len(d) == 2:
                self._combo.addItem(str(d[0]), str(d[1]))
            else:
                self._combo.addItem(str(d), str(d))

    def deger(self) -> str:
        return self._combo.currentData() or ""

    def set_deger(self, v) -> None:
        idx = self._combo.findData(str(v) if v is not None else "")
        if idx >= 0:
            self._combo.setCurrentIndex(idx)

    def _hata_stil_uygula(self, hata: bool) -> None:
        self._combo.setStyleSheet(_INPUT_HATA if hata else "")

    @property
    def combo(self) -> QComboBox:
        return self._combo


# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½
# TextAreaField
# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

class TextAreaField(FieldBase):
    """
    ï¿½?ok satÄ±rlÄ± metin alanÄ±.

    KullanÄ±m:
        alan = TextAreaField("Notlar", yukseklik=90)
        metin = alan.deger()   # str
    """

    def __init__(self, etiket: str, zorunlu: bool = False,
                 placeholder: str = "", yukseklik: int = 80,
                 yardim: str = "", parent=None):
        super().__init__(etiket, zorunlu, yardim, parent)

        self._edit = QTextEdit()
        self._edit.setFixedHeight(yukseklik)
        self._edit.setPlaceholderText(placeholder)
        self._edit.setAcceptRichText(False)

        self._bitir(self._edit)

    def deger(self) -> str:
        return self._edit.toPlainText().strip()

    def set_deger(self, v) -> None:
        self._edit.setPlainText(str(v) if v is not None else "")

    def _hata_stil_uygula(self, hata: bool) -> None:
        self._edit.setStyleSheet(_INPUT_HATA if hata else "")


# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½
# IntField / FloatField
# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

class IntField(FieldBase):
    """
    Tam sayÄ± giriï¿½Yi ï¿½?" QSpinBox.

    KullanÄ±m:
        alan = IntField("YÄ±llÄ±k Hakediï¿½Y", min_val=0, max_val=365)
        sayi = alan.deger()   # int
    """

    def __init__(self, etiket: str, zorunlu: bool = False,
                 min_val: int = 0, max_val: int = 9999,
                 adim: int = 1, birim: str = "",
                 yardim: str = "", parent=None):
        super().__init__(etiket, zorunlu, yardim, parent)

        self._spin = QSpinBox()
        self._spin.setMinimumHeight(T.input_h)
        self._spin.setRange(min_val, max_val)
        self._spin.setSingleStep(adim)
        if birim:
            self._spin.setSuffix(f" {birim}")

        self._bitir(self._spin)

    def deger(self) -> int:
        return self._spin.value()

    def set_deger(self, v) -> None:
        try:
            self._spin.setValue(int(v))
        except (TypeError, ValueError):
            self._spin.setValue(self._spin.minimum())

    def _hata_stil_uygula(self, hata: bool) -> None:
        self._spin.setStyleSheet(_INPUT_HATA if hata else "")


class FloatField(FieldBase):
    """
    OndalÄ±klÄ± sayÄ± giriï¿½Yi ï¿½?" QDoubleSpinBox.

    KullanÄ±m:
        alan = FloatField("Doz (mSv)", min_val=0.0, max_val=100.0, adim=0.01)
        doz  = alan.deger()   # float
    """

    def __init__(self, etiket: str, zorunlu: bool = False,
                 min_val: float = 0.0, max_val: float = 9999.0,
                 adim: float = 0.1, ondalik: int = 2,
                 birim: str = "", yardim: str = "",
                 parent=None):
        super().__init__(etiket, zorunlu, yardim, parent)

        self._spin = QDoubleSpinBox()
        self._spin.setMinimumHeight(T.input_h)
        self._spin.setRange(min_val, max_val)
        self._spin.setSingleStep(adim)
        self._spin.setDecimals(ondalik)
        if birim:
            self._spin.setSuffix(f" {birim}")

        self._bitir(self._spin)

    def deger(self) -> float:
        return self._spin.value()

    def set_deger(self, v) -> None:
        try:
            self._spin.setValue(float(v))
        except (TypeError, ValueError):
            self._spin.setValue(self._spin.minimum())

    def _hata_stil_uygula(self, hata: bool) -> None:
        self._spin.setStyleSheet(_INPUT_HATA if hata else "")


# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½
# ReadonlyField
# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

class ReadonlyField(FieldBase):
    """
    Salt-okunur gÃ¶sterim alanÄ± ï¿½?" veri mevcut ama deï¿½Yiï¿½Ytirilemez.

    KullanÄ±m:
        alan = ReadonlyField("TC Kimlik No")
        alan.set_deger("12345678901")
        metin = alan.deger()
    """

    def __init__(self, etiket: str, yardim: str = "", parent=None):
        super().__init__(etiket, False, yardim, parent)

        self._line = QLineEdit()
        self._line.setMinimumHeight(T.input_h)
        self._line.setReadOnly(True)
        self._line.setStyleSheet(
            f"background:{T.bg1}; color:{T.text2}; border:1px solid {T.border};"
        )

        self._bitir(self._line)

    def deger(self) -> str:
        return self._line.text()

    def set_deger(self, v) -> None:
        self._line.setText(str(v) if v is not None else "")

    def _hata_stil_uygula(self, hata: bool) -> None:
        pass  # Read-only alanlarda hata stili eklenmez


# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½
# CheckField
# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

class CheckField(FieldBase):
    """
    Onay kutusu.

    KullanÄ±m:
        alan = CheckField("Aktif mi?", varsayilan=True)
        secili = alan.deger()   # bool
    """

    toggled = Signal(bool)

    def __init__(self, etiket: str, zorunlu: bool = False,
                 varsayilan: bool = False,
                 yardim: str = "", parent=None):
        super().__init__(etiket, zorunlu, yardim, parent)

        self._chk = QCheckBox()
        self._chk.setChecked(varsayilan)
        self._chk.setMinimumHeight(T.input_h)
        self._chk.toggled.connect(self.toggled)

        self._bitir(self._chk)

    def deger(self) -> bool:
        return self._chk.isChecked()

    def set_deger(self, v) -> None:
        self._chk.setChecked(bool(v))

    def _hata_stil_uygula(self, hata: bool) -> None:
        pass


# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½
# RadioGroup
# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

class RadioGroup(FieldBase):
    """
    Tek seÃ§imli radyo dÃ¼ï¿½Yme grubu.

    KullanÄ±m:
        alan = RadioGroup("Cinsiyet", secenekler=["Erkek","KadÄ±n"])
        alan = RadioGroup("Durum", secenekler=[("Aktif","aktif"),("Pasif","pasif")])
        alan.set_deger("aktif")
        secion = alan.deger()   # str (data deï¿½Yeri)
    """

    secim_degisti = Signal(str)

    def __init__(self, etiket: str, secenekler: list,
                 zorunlu: bool = False,
                 yatay: bool = True, yardim: str = "",
                 parent=None):
        super().__init__(etiket, zorunlu, yardim, parent)

        self._grup  = QButtonGroup(self)
        self._datalar: list[str] = []

        kap = QWidget()
        kap_lay = (QHBoxLayout if yatay else QVBoxLayout)(kap)
        kap_lay.setContentsMargins(0, 2, 0, 2)
        kap_lay.setSpacing(16 if yatay else 6)

        for idx, s in enumerate(secenekler):
            if isinstance(s, (list, tuple)) and len(s) == 2:
                etiket_s, data = str(s[0]), str(s[1])
            else:
                etiket_s = data = str(s)
            self._datalar.append(data)

            rb = QRadioButton(etiket_s)
            self._grup.addButton(rb, idx)
            kap_lay.addWidget(rb)

        if yatay:
            kap_lay.addStretch()
        self._grup.idToggled.connect(self._on_toggle)

        self._bitir(kap)

    def _on_toggle(self, bid: int, checked: bool) -> None:
        if checked and 0 <= bid < len(self._datalar):
            self.secim_degisti.emit(self._datalar[bid])

    def deger(self) -> str:
        bid = self._grup.checkedId()
        if bid < 0 or bid >= len(self._datalar):
            return ""
        return self._datalar[bid]

    def set_deger(self, v) -> None:
        sv = str(v) if v is not None else ""
        for bid, data in enumerate(self._datalar):
            if data == sv:
                btn = self._grup.button(bid)
                if btn:
                    btn.setChecked(True)
                return

    def _hata_stil_uygula(self, hata: bool) -> None:
        pass


# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½
# FormGroup ï¿½?" Baï¿½YlÄ±klÄ± form bÃ¶lÃ¼mÃ¼ (QGroupBox yerine)
# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

class FormGroup(QFrame):
    """
    Form bÃ¶lÃ¼m container'Ä±. QGroupBox yerine kullanÄ±lÄ±r.

    KullanÄ±m:
        grp = FormGroup("Kimlik Bilgileri", ikon="kimlik")
        grp.ekle(ad_alani)
        grp.ekle(soyad_alani)
        grp.ekle_yatay(dogum_alani, cinsiyet_alani)
    """

    def __init__(self, baslik: str, ikon: str = "", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)

        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # ï¿½"?ï¿½"? Baï¿½YlÄ±k barÄ± ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?
        hdr = QWidget()
        hdr.setStyleSheet(
            f"background:{T.bg3};"
            f"border-top-left-radius:{T.radius}px;"
            f"border-top-right-radius:{T.radius}px;"
        )
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(14, 8, 14, 8)
        hdr_lay.setSpacing(8)

        if ikon:
            ikon_lbl = QLabel()
            ikon_lbl.setPixmap(ic(ikon, T.text3, T.icon_sm).pixmap(
                QSize(T.icon_sm, T.icon_sm)))
            ikon_lbl.setStyleSheet("background:transparent;")
            hdr_lay.addWidget(ikon_lbl)

        baslik_lbl = QLabel(baslik.upper())
        baslik_lbl.setStyleSheet(
            f"color:{T.text3}; font-size:9.5px; font-weight:700;"
            f"letter-spacing:0.6px; background:transparent;"
        )
        hdr_lay.addWidget(baslik_lbl)
        hdr_lay.addStretch()
        main_lay.addWidget(hdr)

        # ï¿½"?ï¿½"? Ä°Ã§erik alanÄ± ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?
        self._content = QWidget()
        self._content.setStyleSheet(
            f"background:{T.bg2};"
            f"border:1px solid {T.border};"
            f"border-top:none;"
            f"border-bottom-left-radius:{T.radius}px;"
            f"border-bottom-right-radius:{T.radius}px;"
        )
        self._clay = QVBoxLayout(self._content)
        self._clay.setContentsMargins(16, 12, 16, 16)
        self._clay.setSpacing(12)
        main_lay.addWidget(self._content)

    def ekle(self, widget: QWidget) -> None:
        """Tek alan dikey olarak ekle."""
        self._clay.addWidget(widget)

    def ekle_yatay(self, *widgets: QWidget) -> None:
        """Birden fazla alanÄ± yatay olarak yan yana ekle."""
        row = QWidget()
        row.setStyleSheet("background:transparent;")
        rlay = QHBoxLayout(row)
        rlay.setContentsMargins(0, 0, 0, 0)
        rlay.setSpacing(14)
        for w in widgets:
            rlay.addWidget(w, 1)
        self._clay.addWidget(row)

    def ayrac(self) -> None:
        """Ä°nce yatay ayÄ±rÄ±cÄ± Ã§izgi ekle."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color:{T.border};")
        self._clay.addWidget(line)

    @property
    def icerik_lay(self) -> QVBoxLayout:
        return self._clay


# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½
# SearchBar ï¿½?" Arama kutusu (geliï¿½Ytirilmiï¿½Y)
# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

class SearchBar(QLineEdit):
    """
    Sol ikon + temizle butonu olan arama kutusu.

    KullanÄ±m:
        bar = SearchBar("Personel araï¿½?ï¿½")
        bar.textChanged.connect(tablo.ara)
    """

    def __init__(self, placeholder: str = "Araï¿½?ï¿½", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setClearButtonEnabled(True)
        self.setMinimumWidth(220)
        self.setMinimumHeight(T.input_h)
        self.addAction(
            ic("ara", size=T.icon_sm, color=T.text3),
            QLineEdit.ActionPosition.LeadingPosition,
        )








