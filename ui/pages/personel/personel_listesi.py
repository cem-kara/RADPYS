# -*- coding: utf-8 -*-
"""ui/pages/personel/personel_listesi.py - Screenshot odakli personel listesi."""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.personel_service import PersonelService
from ui.components.alerts import AlertBar
from ui.components.async_runner import AsyncRunner
from ui.components.buttons import GhostButton, PrimaryButton
from ui.components.forms import SearchBar
from ui.styles import T
from ui.styles.icons import ic


class _FilterChip(QPushButton):
    """Ust satirdaki durum filtre chip'i."""

    def __init__(self, etiket: str, renk: str, parent=None):
        super().__init__(etiket, parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {T.text2};
                border: 1px solid {T.border2};
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                border-color: {renk};
                color: {T.text};
            }}
            QPushButton:checked {{
                background-color: {T.overlay_low};
                color: {renk};
                border: 1px solid {renk};
                font-weight: 700;
            }}
            """
        )


class _AvatarCell(QWidget):
    """Ad ve soyad bas harflerini daire rozet olarak gosteren hucre."""

    def __init__(self, ad: str, soyad: str, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ilk = (ad[:1] + soyad[:1]).upper() or "?"
        rozet = QLabel(ilk)
        rozet.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rozet.setFixedSize(28, 28)
        rozet.setStyleSheet(
            f"background:{T.overlay_mid}; color:{T.text}; border-radius:14px; "
            "font-size:12px; font-weight:700;"
        )
        lay.addWidget(rozet)


class _DualLineCell(QWidget):
    """Iki satirli metin hucre widget'i."""

    def __init__(self, ust: str, alt: str = "", parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(1)

        ust_lbl = QLabel(ust)
        ust_lbl.setStyleSheet(f"color:{T.text}; font-size:12px; font-weight:500;")
        lay.addWidget(ust_lbl)

        alt_lbl = QLabel(alt)
        alt_lbl.setStyleSheet(f"color:{T.text3}; font-size:11px;")
        alt_lbl.setVisible(bool(alt))
        lay.addWidget(alt_lbl)


class _IzinBakiyeCell(QWidget):
    """Izin bakiyesi metin + progress gorunumu."""

    def __init__(self, kullanilan: float, toplam: float, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(4)

        txt = QLabel(f"{kullanilan:.1f} / {toplam:.1f}")
        txt.setStyleSheet(f"color:{T.text3}; font-size:11px;")
        lay.addWidget(txt)

        bar = QProgressBar()
        bar.setTextVisible(False)
        bar.setFixedHeight(4)
        bar.setRange(0, 100)
        yuzde = 0 if toplam <= 0 else max(0, min(100, int((kullanilan / toplam) * 100)))
        bar.setValue(yuzde)
        bar.setStyleSheet(
            f"QProgressBar{{background:{T.overlay_low}; border:none; border-radius:2px;}}"
            f"QProgressBar::chunk{{background:{T.accent2}; border-radius:2px;}}"
        )
        lay.addWidget(bar)


class _DurumCell(QWidget):
    """Durum etiketi ve opsiyonel bilgi bandi."""

    def __init__(self, durum: str, ek_bilgi: str = "", parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        d = (durum or "").lower()
        if d == "aktif":
            renk = T.green2
        elif d == "pasif":
            renk = T.red
        elif d == "izinli":
            renk = T.amber
        else:
            renk = T.text2

        badge = QLabel((durum or "-").title())
        badge.setStyleSheet(
            f"background:{T.overlay_low}; color:{renk}; border:1px solid {renk}66; "
            "border-radius:6px; padding:2px 10px; font-size:11px; font-weight:600;"
        )
        lay.addWidget(badge)

        bilgi = QLabel(ek_bilgi)
        bilgi.setVisible(bool(ek_bilgi))
        bilgi.setStyleSheet(
            f"background:{T.overlay_low}; color:{T.green2}; border:1px solid {T.green2}66; "
            "border-radius:6px; padding:2px 10px; font-size:11px;"
        )
        lay.addWidget(bilgi)
        lay.addStretch()


class PersonelListesi(QWidget):
    """Personel menusu acildiginda gorunen ana liste ekrani."""

    secildi = Signal(str)
    yeni_istendi = Signal()

    _KOLON_BASLIK = ["", "Ad Soyad", "TC / Sicil", "Birim - Unvan", "Telefon", "Izin Bakiye", "Durum"]

    def __init__(self, db, oturum: dict | None = None, parent=None):
        super().__init__(parent)
        self._db = db
        self._oturum = oturum
        self._svc = PersonelService(db)
        self._tumveri: list[dict] = []
        self._gorunen: list[dict] = []
        self._aktif_durum = "tumu"
        self._chip_map: dict[str, _FilterChip] = {}

        self._build()
        self._yukle()

    def _build(self) -> None:
        kok = QVBoxLayout(self)
        kok.setContentsMargins(0, 0, 0, 0)
        kok.setSpacing(0)

        ust = QFrame()
        ust.setStyleSheet(f"background:{T.bg1}; border-bottom:1px solid {T.border};")
        ust_lay = QVBoxLayout(ust)
        ust_lay.setContentsMargins(14, 10, 14, 10)
        ust_lay.setSpacing(10)

        satir1 = QHBoxLayout()
        satir1.setSpacing(8)

        baslik = QLabel("Personel Listesi")
        baslik.setStyleSheet(f"color:{T.text}; font-size:18px; font-weight:700;")
        satir1.addWidget(baslik)

        self._chip_map["aktif"] = self._chip_olustur("Aktif", T.green2, lambda r: self._durum_hesapla(r) == "aktif")
        self._chip_map["pasif"] = self._chip_olustur("Pasif", T.red, lambda r: self._durum_hesapla(r) == "pasif")
        self._chip_map["izinli"] = self._chip_olustur("Izinli", T.amber, lambda r: self._durum_hesapla(r) == "izinli")
        self._chip_map["tumu"] = self._chip_olustur("Tumu", T.accent2, lambda _: True)

        for anahtar in ["aktif", "pasif", "izinli", "tumu"]:
            satir1.addWidget(self._chip_map[anahtar])

        satir1.addSpacing(8)
        self._arama = SearchBar("Ad, TC, birim ara...")
        self._arama.setMinimumWidth(230)
        self._arama.textChanged.connect(self._filtrele)
        satir1.addWidget(self._arama)

        satir1.addStretch()

        btn_yenile = GhostButton("", ikon="yenile")
        btn_yenile.setFixedSize(34, 30)
        btn_yenile.setToolTip("Yenile")
        btn_yenile.clicked.connect(self._yukle)
        satir1.addWidget(btn_yenile)

        btn_yeni = PrimaryButton("Yeni Personel", ikon="ekle")
        btn_yeni.setFixedHeight(30)
        btn_yeni.clicked.connect(self.yeni_istendi)
        satir1.addWidget(btn_yeni)

        ust_lay.addLayout(satir1)

        satir2 = QHBoxLayout()
        satir2.setSpacing(8)

        filtre_lbl = QLabel("FILTRE:")
        filtre_lbl.setStyleSheet(f"color:{T.text3}; font-size:12px;")
        satir2.addWidget(filtre_lbl)

        self._cb_birim = QComboBox()
        self._cb_birim.setFixedWidth(250)
        self._cb_birim.currentTextChanged.connect(self._filtrele)
        satir2.addWidget(self._cb_birim)

        self._cb_sinif = QComboBox()
        self._cb_sinif.setFixedWidth(300)
        self._cb_sinif.currentTextChanged.connect(self._filtrele)
        satir2.addWidget(self._cb_sinif)

        satir2.addStretch()

        btn_excel = GhostButton("Excel", ikon="download")
        btn_excel.setFixedHeight(30)
        btn_excel.clicked.connect(lambda: self._alert.goster("Excel aktarim sonraki adimda eklenecek."))
        satir2.addWidget(btn_excel)

        ust_lay.addLayout(satir2)
        kok.addWidget(ust)

        self._alert = AlertBar(self)
        kok.addWidget(self._alert)

        self._tablo = QTableWidget()
        self._tablo.setColumnCount(len(self._KOLON_BASLIK))
        self._tablo.setHorizontalHeaderLabels(self._KOLON_BASLIK)
        self._tablo.verticalHeader().setVisible(False)
        self._tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tablo.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._tablo.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tablo.setAlternatingRowColors(True)
        self._tablo.setShowGrid(False)
        self._tablo.cellClicked.connect(self._satir_secildi)

        hdr = self._tablo.horizontalHeader()
        hdr.setStretchLastSection(False)
        hdr.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._tablo.setColumnWidth(0, 42)
        self._tablo.setColumnWidth(1, 260)
        self._tablo.setColumnWidth(2, 170)
        self._tablo.setColumnWidth(3, 330)
        self._tablo.setColumnWidth(4, 120)
        self._tablo.setColumnWidth(5, 250)
        self._tablo.setColumnWidth(6, 320)

        self._tablo.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {T.bg0};
                color: {T.text};
                border: 0;
                gridline-color: transparent;
                selection-background-color: {T.overlay_low};
                selection-color: {T.text};
            }}
            QTableCornerButton::section {{
                background-color: {T.bg2};
                border: 0;
            }}
            QHeaderView::section {{
                background-color: {T.bg2};
                color: {T.text2};
                border: 0;
                padding: 8px;
                font-size: 12px;
            }}
            QTableWidget::item {{
                border: 0;
            }}
            """
        )
        kok.addWidget(self._tablo, 1)

        self._chip_sec("tumu")
        self._combo_baslat()

    def _chip_olustur(self, ad: str, renk: str, pred: Callable[[dict], bool]) -> _FilterChip:
        chip = _FilterChip(f"{ad} (0)", renk)
        chip.clicked.connect(lambda: self._chip_tiklandi(chip, ad.lower(), pred))
        chip._counter_predicate = pred
        chip._base_text = ad
        return chip

    def _chip_tiklandi(self, secilen: _FilterChip, durum_anahtar: str, _pred: Callable[[dict], bool]) -> None:
        for key, chip in self._chip_map.items():
            chip.setChecked(chip is secilen)
            if chip is secilen:
                self._aktif_durum = key
        self._filtrele()

    def _chip_sec(self, key: str) -> None:
        for k, chip in self._chip_map.items():
            chip.setChecked(k == key)
        self._aktif_durum = key

    def _combo_baslat(self) -> None:
        self._cb_birim.blockSignals(True)
        self._cb_sinif.blockSignals(True)
        self._cb_birim.clear()
        self._cb_sinif.clear()
        self._cb_birim.addItem("Tum Birimler")
        self._cb_sinif.addItem("Tum Siniflar")
        self._cb_birim.blockSignals(False)
        self._cb_sinif.blockSignals(False)

    def _yukle(self) -> None:
        def _cek():
            return self._svc.listele(aktif_only=False)

        def _tamam(veri: list[dict]):
            self._tumveri = veri or []
            self._combo_doldur()
            self._chip_sayac_guncelle()
            self._filtrele()
            self._alert.temizle()

        def _hata(msg: str):
            self._alert.goster(msg)

        AsyncRunner(fn=_cek, on_done=_tamam, on_error=_hata, parent=self).start()

    def _combo_doldur(self) -> None:
        birimler = sorted({str(r.get("gorev_yeri_ad") or "-").strip() for r in self._tumveri if str(r.get("gorev_yeri_ad") or "").strip()})
        siniflar = sorted({str(r.get("hizmet_sinifi") or "-").strip() for r in self._tumveri if str(r.get("hizmet_sinifi") or "").strip()})

        sec_birim = self._cb_birim.currentText()
        sec_sinif = self._cb_sinif.currentText()

        self._cb_birim.blockSignals(True)
        self._cb_sinif.blockSignals(True)

        self._cb_birim.clear()
        self._cb_birim.addItem("Tum Birimler")
        self._cb_birim.addItems(birimler)

        self._cb_sinif.clear()
        self._cb_sinif.addItem("Tum Siniflar")
        self._cb_sinif.addItems(siniflar)

        idx_birim = self._cb_birim.findText(sec_birim)
        idx_sinif = self._cb_sinif.findText(sec_sinif)
        self._cb_birim.setCurrentIndex(idx_birim if idx_birim >= 0 else 0)
        self._cb_sinif.setCurrentIndex(idx_sinif if idx_sinif >= 0 else 0)

        self._cb_birim.blockSignals(False)
        self._cb_sinif.blockSignals(False)

    def _chip_sayac_guncelle(self) -> None:
        for chip in self._chip_map.values():
            pred = getattr(chip, "_counter_predicate", lambda _: True)
            adet = sum(1 for r in self._tumveri if pred(r))
            base = getattr(chip, "_base_text", "")
            chip.setText(f"{base} ({adet})")

    def _durum_hesapla(self, satir: dict) -> str:
        durum = str(satir.get("durum") or "").lower().strip()
        if durum in {"aktif", "pasif", "izinli"}:
            return durum
        return "aktif" if durum == "" else durum

    def _durum_eslesiyor_mu(self, satir: dict) -> bool:
        if self._aktif_durum == "tumu":
            return True
        return self._durum_hesapla(satir) == self._aktif_durum

    def _filtrele(self) -> None:
        arama = self._arama.text().strip().lower()
        birim = self._cb_birim.currentText()
        sinif = self._cb_sinif.currentText()

        sonuc: list[dict] = []
        for row in self._tumveri:
            if not self._durum_eslesiyor_mu(row):
                continue

            if birim != "Tum Birimler" and str(row.get("gorev_yeri_ad") or "-") != birim:
                continue
            if sinif != "Tum Siniflar" and str(row.get("hizmet_sinifi") or "-") != sinif:
                continue

            if arama:
                havuz = " ".join(
                    [
                        str(row.get("ad") or ""),
                        str(row.get("soyad") or ""),
                        str(row.get("tc_kimlik") or ""),
                        str(row.get("sicil_no") or ""),
                        str(row.get("gorev_yeri_ad") or ""),
                        str(row.get("kadro_unvani") or ""),
                    ]
                ).lower()
                if arama not in havuz:
                    continue

            sonuc.append(row)

        self._gorunen = sonuc
        self._tablo_yukle()

    def _tablo_yukle(self) -> None:
        self._tablo.setRowCount(len(self._gorunen))

        for idx, row in enumerate(self._gorunen):
            ad = str(row.get("ad") or "")
            soyad = str(row.get("soyad") or "")
            tc = str(row.get("tc_kimlik") or "-")
            sicil = str(row.get("sicil_no") or "-")
            birim = str(row.get("gorev_yeri_ad") or "-")
            unvan = str(row.get("kadro_unvani") or "-")
            telefon = str(row.get("telefon") or "-")
            durum = self._durum_hesapla(row)

            self._tablo.setCellWidget(idx, 0, _AvatarCell(ad, soyad))
            self._tablo.setCellWidget(idx, 1, _DualLineCell(f"{ad} {soyad}".strip()))
            self._tablo.setCellWidget(idx, 2, _DualLineCell(tc, sicil))
            self._tablo.setCellWidget(idx, 3, _DualLineCell(birim, unvan))
            self._tablo.setCellWidget(idx, 4, _DualLineCell(telefon))

            kullanilan = float(row.get("izin_kullanilan") or 0.0)
            toplam = float(row.get("izin_toplam") or 0.0)
            self._tablo.setCellWidget(idx, 5, _IzinBakiyeCell(kullanilan, toplam))

            ek = ""
            if durum == "izinli":
                bitis = str(row.get("izin_bitis") or "-")
                ek = f"Personel bugun izinli, bitis: {bitis}"
            self._tablo.setCellWidget(idx, 6, _DurumCell(durum, ek))

            id_item = QTableWidgetItem(str(row.get("id") or ""))
            id_item.setData(Qt.ItemDataRole.UserRole, str(row.get("id") or ""))
            self._tablo.setItem(idx, 0, id_item)

        self._tablo.resizeRowsToContents()

    def _satir_secildi(self, row: int, _col: int) -> None:
        item = self._tablo.item(row, 0)
        if not item:
            return
        personel_id = item.data(Qt.ItemDataRole.UserRole)
        if personel_id:
            self.secildi.emit(str(personel_id))

    def yenile(self) -> None:
        self._yukle()

    def sec(self, personel_id: str) -> None:
        for row in range(self._tablo.rowCount()):
            item = self._tablo.item(row, 0)
            if not item:
                continue
            if str(item.data(Qt.ItemDataRole.UserRole)) == personel_id:
                self._tablo.selectRow(row)
                self._tablo.scrollToItem(item, QTableWidget.ScrollHint.PositionAtCenter)
                break
