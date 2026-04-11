# -*- coding: utf-8 -*-
"""ui/pages/izin/izin_listesi.py — İzin takip ana sayfası."""
from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate, QModelIndex, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.logger import exc_logla
from app.services.izin_service import IzinService
from app.validators import format_tarih
from ui.components import (
    AlertBar,
    AsyncRunner,
    DataTable,
    DangerButton,
    GhostButton,
    PrimaryButton,
)
from ui.components.tables import _TableModel
from ui.styles import T


# ─────────────────────────────────────────────────────────────────
#  Özelleştirilmiş tablo modeli
# ─────────────────────────────────────────────────────────────────

_KOLONLAR = [
    ("ad_soyad",    "Personel",       220),
    ("kadro_unvani","Unvan",          150),
    ("tur",         "İzin Türü",      140),
    ("baslama_ui",  "Başlama",         95),
    ("bitis_ui",    "Bitiş",           95),
    ("gun",         "Gün",             55),
    ("durum",       "Durum",           80),
    ("aciklama",    "Açıklama",       160),
]


class _IzinModel(_TableModel):
    """İzin tablosu modeli — renk ve format override'larıyla."""

    def _display(self, key: str, deger, row: dict) -> str:
        if deger is None or str(deger).strip() == "":
            return ""
        if key == "gun":
            return f"{deger} gün"
        if key == "durum":
            return {"aktif": "Aktif", "iptal": "İptal"}.get(str(deger), str(deger))
        return str(deger)

    def _foreground(self, key: str, deger, row: dict) -> str | None:
        if key == "gun":
            return T.accent
        if key == "durum":
            return T.green2 if str(deger) == "aktif" else T.red
        if key == "ad_soyad":
            return T.text
        return T.text2

    def _alignment(self, key: str) -> int:
        center = int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        left   = int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        return center if key in ("gun", "durum", "baslama_ui", "bitis_ui") else left


class _IzinTablosu(DataTable):
    """DataTable'ı izin kolonlarıyla hazır kurar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = _IzinModel(_KOLONLAR)
        self._proxy.setSourceModel(self._model)

        hdr = self.horizontalHeader()
        from PySide6.QtWidgets import QHeaderView
        for i, (_, _, w) in enumerate(_KOLONLAR):
            if w > 0:
                self.setColumnWidth(i, w)
                hdr.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
        # Unvan kolonunu gerer
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)


# ─────────────────────────────────────────────────────────────────
#  İzin ekleme formu
# ─────────────────────────────────────────────────────────────────

class _IzinFormPaneli(QFrame):
    """Yeni izin ekleme formu — liste sayfasına gömülü."""

    from PySide6.QtCore import Signal
    kaydedildi = Signal()
    kapatildi  = Signal()

    def __init__(self, svc: IzinService, parent=None):
        super().__init__(parent)
        self._svc = svc
        self._personel: list[dict] = []
        self.setStyleSheet(
            f"QFrame{{background:{T.bg1};"
            f"border:1px solid {T.border};"
            f"border-radius:{T.radius}px;}}"
        )
        self._build()
        self._yukle_lookups()

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 14)
        lay.setSpacing(10)

        # Başlık
        baslik_row = QHBoxLayout()
        baslik_lbl = QLabel("Yeni İzin Kaydı")
        baslik_lbl.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        baslik_row.addWidget(baslik_lbl)
        baslik_row.addStretch()
        btn_kapat = GhostButton("", ikon="x")
        btn_kapat.setFixedSize(28, 28)
        btn_kapat.clicked.connect(self.kapatildi.emit)
        baslik_row.addWidget(btn_kapat)
        lay.addLayout(baslik_row)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{T.border};")
        lay.addWidget(sep)

        self._alert = AlertBar(self)
        lay.addWidget(self._alert)

        def _lbl(text: str) -> QLabel:
            w = QLabel(text)
            w.setStyleSheet(f"color:{T.text2}; font-size:11px; font-weight:600;")
            return w

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 2)

        self._personel_cb = QComboBox()
        self._personel_cb.setEditable(True)
        self._personel_cb.lineEdit().setPlaceholderText("Personel ara…")
        self._personel_cb.setMinimumHeight(T.input_h)
        self._personel_cb.currentIndexChanged.connect(self._on_personel_degisti)
        grid.addWidget(_lbl("Personel *"), 0, 0)
        grid.addWidget(self._personel_cb, 1, 0)

        self._tur_cb = QComboBox()
        self._tur_cb.setMinimumHeight(T.input_h)
        self._tur_cb.currentTextChanged.connect(self._on_tur_degisti)
        grid.addWidget(_lbl("İzin Türü *"), 0, 1)
        grid.addWidget(self._tur_cb, 1, 1)

        self._gun_sb = QSpinBox()
        self._gun_sb.setMinimum(1)
        self._gun_sb.setMaximum(365)
        self._gun_sb.setValue(1)
        self._gun_sb.setMinimumHeight(T.input_h)
        self._gun_sb.valueChanged.connect(self._guncelle_bitis)
        grid.addWidget(_lbl("Gün *"), 0, 2)
        grid.addWidget(self._gun_sb, 1, 2)

        self._baslama = QDateEdit()
        self._baslama.setCalendarPopup(True)
        self._baslama.setDate(QDate.currentDate())
        self._baslama.setMinimumHeight(T.input_h)
        self._baslama.dateChanged.connect(self._guncelle_bitis)
        grid.addWidget(_lbl("Başlama Tarihi *"), 0, 3)
        grid.addWidget(self._baslama, 1, 3)
        lay.addLayout(grid)

        # Bitiş + bakiye satırı
        alt_row = QHBoxLayout()
        alt_row.addWidget(QLabel("Bitiş:"))
        self._lbl_bitis = QLabel("—")
        self._lbl_bitis.setStyleSheet(f"color:{T.accent}; font-weight:600;")
        alt_row.addWidget(self._lbl_bitis)
        alt_row.addSpacing(20)
        self._lbl_bakiye = QLabel()
        self._lbl_bakiye.setStyleSheet(f"color:{T.text3}; font-size:11px;")
        alt_row.addWidget(self._lbl_bakiye)
        alt_row.addStretch()
        lay.addLayout(alt_row)

        # Açıklama
        lay.addWidget(_lbl("Açıklama"))
        self._aciklama = QTextEdit()
        self._aciklama.setFixedHeight(52)
        self._aciklama.setPlaceholderText("İsteğe bağlı…")
        lay.addWidget(self._aciklama)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_vazgec = GhostButton("Vazgeç")
        btn_vazgec.clicked.connect(self.kapatildi.emit)
        btn_row.addWidget(btn_vazgec)
        self._btn_kaydet = PrimaryButton("Kaydet", ikon="check")
        self._btn_kaydet.clicked.connect(self._on_kaydet)
        btn_row.addWidget(self._btn_kaydet)
        lay.addLayout(btn_row)

        self._guncelle_bitis()

    def _yukle_lookups(self) -> None:
        try:
            self._personel = self._svc.personel_listesi()
            self._personel_cb.clear()
            self._personel_cb.addItem("", userData="")
            for p in self._personel:
                self._personel_cb.addItem(
                    f"{p['ad']} {p['soyad']} — {p.get('kadro_unvani') or ''}",
                    userData=p["id"],
                )
            self._tur_cb.clear()
            self._tur_cb.addItem("")
            self._tur_cb.addItems(self._svc.izin_turleri())
        except Exception as exc:
            exc_logla("IzinFormPaneli._yukle_lookups", exc)

    def _guncelle_bitis(self) -> None:
        from app.validators import bitis_hesapla
        try:
            bitis_str = bitis_hesapla(str(self._baslama.date().toPython()), self._gun_sb.value())
            self._lbl_bitis.setText(format_tarih(bitis_str, ui=True))
        except Exception:
            self._lbl_bitis.setText("—")

    def _on_personel_degisti(self, _) -> None:
        self._on_tur_degisti(self._tur_cb.currentText())

    def _on_tur_degisti(self, tur: str) -> None:
        if tur.lower() != "yillik":
            self._lbl_bakiye.setText("")
            return
        pid = self._personel_cb.currentData()
        if not pid:
            return
        try:
            b = self._svc.bakiye_hesapla(pid, date.today().year)
            self._lbl_bakiye.setText(
                f"Yıllık hak: {b['hak']} gün  |  "
                f"Kullanılan: {b['kullanilan']} gün  |  "
                f"Kalan: {b['kalan']} gün"
            )
        except Exception:
            self._lbl_bakiye.setText("")

    def _on_kaydet(self) -> None:
        self._alert.temizle()
        pid = self._personel_cb.currentData()
        if not pid:
            self._alert.goster("Personel seçiniz.", "warning")
            return
        self._btn_kaydet.setEnabled(False)
        veri = {
            "personel_id": pid,
            "tur": self._tur_cb.currentText().strip(),
            "baslama": str(self._baslama.date().toPython()),
            "gun": self._gun_sb.value(),
            "aciklama": self._aciklama.toPlainText().strip() or None,
        }
        AsyncRunner(
            fn=lambda: self._svc.ekle(veri),
            on_done=self._on_kayit_ok,
            on_error=self._on_kayit_hata,
            parent=self,
        ).start()

    def _on_kayit_ok(self, _) -> None:
        self._btn_kaydet.setEnabled(True)
        self.kaydedildi.emit()

    def _on_kayit_hata(self, mesaj: str) -> None:
        self._btn_kaydet.setEnabled(True)
        self._alert.goster(mesaj, "warning")


# ─────────────────────────────────────────────────────────────────
#  Ana sayfa
# ─────────────────────────────────────────────────────────────────

class IzinListesiPage(QWidget):
    """İzin takip ana sayfası."""

    def __init__(self, db, oturum=None, parent=None):
        super().__init__(parent)
        self._svc = IzinService(db)
        self._tum_kayitlar: list[dict] = []
        self._form_acik = False
        self.setStyleSheet(f"background:{T.bg0};")
        self._build()
        self._yukle()

    # ── Yapı ──────────────────────────────────────────────────────

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        # Başlık
        baslik_row = QHBoxLayout()
        baslik_lbl = QLabel("İzin Takip")
        baslik_lbl.setStyleSheet(f"color:{T.text}; font-size:18px; font-weight:700;")
        baslik_row.addWidget(baslik_lbl)
        baslik_row.addStretch()
        self._btn_yeni = PrimaryButton("Yeni İzin", ikon="plus")
        self._btn_yeni.clicked.connect(self._toggle_form)
        baslik_row.addWidget(self._btn_yeni)
        root.addLayout(baslik_row)

        self._alert = AlertBar(self)
        root.addWidget(self._alert)

        # Form paneli
        self._form = _IzinFormPaneli(self._svc, self)
        self._form.kaydedildi.connect(self._on_form_kaydedildi)
        self._form.kapatildi.connect(self._kapat_form)
        self._form.setVisible(False)
        root.addWidget(self._form)

        # Filtre çubuğu
        filtre_frame = QFrame()
        filtre_frame.setStyleSheet(
            f"QFrame{{background:{T.bg1};"
            f"border:1px solid {T.border};"
            f"border-radius:{T.radius}px;}}"
        )
        fl = QHBoxLayout(filtre_frame)
        fl.setContentsMargins(12, 8, 12, 8)
        fl.setSpacing(10)

        self._ara = QLineEdit()
        self._ara.setPlaceholderText("Personel ara…")
        self._ara.setFixedHeight(T.input_h)
        self._ara.textChanged.connect(self._filtrele)
        fl.addWidget(self._ara, 3)

        self._yil_cb = QComboBox()
        self._yil_cb.setFixedHeight(T.input_h)
        self._yil_cb.addItem("Tümü", userData=None)
        bugun_yil = date.today().year
        for y in range(bugun_yil, bugun_yil - 5, -1):
            self._yil_cb.addItem(str(y), userData=y)
        self._yil_cb.setCurrentIndex(1)
        self._yil_cb.currentIndexChanged.connect(self._yukle)
        fl.addWidget(self._yil_cb, 1)

        self._tur_cb = QComboBox()
        self._tur_cb.setFixedHeight(T.input_h)
        self._tur_cb.addItem("Tüm Türler", userData="")
        self._tur_cb.currentIndexChanged.connect(self._filtrele)
        fl.addWidget(self._tur_cb, 1)

        self._durum_cb = QComboBox()
        self._durum_cb.setFixedHeight(T.input_h)
        self._durum_cb.addItems(["Tüm Durumlar", "Aktif", "İptal"])
        self._durum_cb.currentIndexChanged.connect(self._filtrele)
        fl.addWidget(self._durum_cb, 1)

        root.addWidget(filtre_frame)

        # Tablo
        self._tablo = _IzinTablosu(self)
        self._tablo.doubleClicked.connect(self._on_satir_cift_tiklandi)
        root.addWidget(self._tablo, 1)

        # Özet
        self._lbl_ozet = QLabel()
        self._lbl_ozet.setStyleSheet(f"color:{T.text3}; font-size:11px;")
        root.addWidget(self._lbl_ozet)

        # İptal butonu (seçili satır)
        eylem_row = QHBoxLayout()
        eylem_row.addStretch()
        self._btn_iptal = DangerButton("Seçili İzni İptal Et", ikon="x")
        self._btn_iptal.clicked.connect(self._on_iptal_tiklandi)
        eylem_row.addWidget(self._btn_iptal)
        root.addLayout(eylem_row)

        # Tür combo'sunu doldur
        try:
            for tur in self._svc.izin_turleri():
                self._tur_cb.addItem(tur, userData=tur)
        except Exception:
            pass

    # ── Veri yükleme ──────────────────────────────────────────────

    def _yukle(self) -> None:
        self._alert.temizle()
        yil = self._yil_cb.currentData()
        AsyncRunner(
            fn=lambda: self._svc.listele(yil=yil),
            on_done=self._goster,
            on_error=lambda m: self._alert.goster(m, "danger"),
            parent=self,
        ).start()

    def _goster(self, kayitlar: list[dict]) -> None:
        # Tabloya uygun alanları ekle
        for r in kayitlar:
            r["ad_soyad"] = f"{r.get('ad') or ''} {r.get('soyad') or ''}".strip()
            r["baslama_ui"] = format_tarih(r.get("baslama"), ui=True)
            r["bitis_ui"]   = format_tarih(r.get("bitis"),   ui=True)
        self._tum_kayitlar = kayitlar
        self._filtrele()

    def _filtrele(self) -> None:
        ara          = self._ara.text().strip().lower()
        tur_filtre   = self._tur_cb.currentData() or ""
        durum_filtre = {0: "", 1: "aktif", 2: "iptal"}.get(self._durum_cb.currentIndex(), "")

        sonuc = [
            r for r in self._tum_kayitlar
            if (not ara          or ara in r.get("ad_soyad", "").lower())
            and (not tur_filtre  or r.get("tur")   == tur_filtre)
            and (not durum_filtre or r.get("durum") == durum_filtre)
        ]
        self._tablo.set_veri(sonuc)
        toplam = len(self._tum_kayitlar)
        aktif  = sum(1 for r in self._tum_kayitlar if r.get("durum") == "aktif")
        self._lbl_ozet.setText(f"Toplam {toplam} kayıt  |  {aktif} aktif")

    # ── Form yönetimi ─────────────────────────────────────────────

    def _toggle_form(self) -> None:
        if self._form_acik:
            self._kapat_form()
        else:
            self._ac_form()

    def _ac_form(self) -> None:
        self._form_acik = True
        self._form.setVisible(True)
        self._btn_yeni.setText("Kapat")

    def _kapat_form(self) -> None:
        self._form_acik = False
        self._form.setVisible(False)
        self._btn_yeni.setText("Yeni İzin")

    def _on_form_kaydedildi(self) -> None:
        self._kapat_form()
        self._alert.goster("İzin kaydı eklendi.", "success")
        self._yukle()

    # ── İptal işlemi ──────────────────────────────────────────────

    def _on_satir_cift_tiklandi(self, _: QModelIndex) -> None:
        row = self._tablo.secili_satir()
        if row and row.get("durum") == "aktif":
            self._iptal_et(str(row["id"]))

    def _on_iptal_tiklandi(self) -> None:
        row = self._tablo.secili_satir()
        if not row:
            self._alert.goster("Lütfen iptal edilecek kaydı seçiniz.", "warning")
            return
        if row.get("durum") != "aktif":
            self._alert.goster("Seçili izin zaten iptal edilmiş.", "warning")
            return
        self._iptal_et(str(row["id"]))

    def _iptal_et(self, izin_id: str) -> None:
        self._alert.temizle()
        AsyncRunner(
            fn=lambda: self._svc.iptal(izin_id),
            on_done=lambda _: self._on_iptal_ok(),
            on_error=lambda m: self._alert.goster(m, "warning"),
            parent=self,
        ).start()

    def _on_iptal_ok(self) -> None:
        self._alert.goster("İzin iptal edildi.", "success")
        self._yukle()
