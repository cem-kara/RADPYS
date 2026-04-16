# -*- coding: utf-8 -*-
"""
ui/pages/imports/components/hata_duzeltme_dialog.py

Import sonrası hatalı satırların program içinde düzenlenmesi
ve tekrar aktarılması için dialog.
"""
from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.excel_import_service import (
    ImportKonfig,
    ImportSonucu,
    SatirSonucu,
)
from ui.components import AlertBar
from ui.styles import T


class HataDuzeltmeDialog(QDialog):
    """
    Import sonrası hatalı satırları düzenleyip tekrar aktarmak için dialog.

    Kullanım:
        dlg = HataDuzeltmeDialog(konfig, son_sonuc, svc, db, kaydeden, parent)
        dlg.exec()
        # Kullanıcı yeniden aktarım yaptıysa dlg.yeniden_sonuc dolu olur
    """

    HATA_KOLON_SONU = "__hata__"

    def __init__(
        self,
        konfig: ImportKonfig,
        son_sonuc: ImportSonucu,
        svc,                      # ExcelImportService örneği
        db: Any,
        kaydeden: str = "",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._konfig = konfig
        self._svc = svc
        self._db = db
        self._kaydeden = kaydeden
        self.yeniden_sonuc: ImportSonucu | None = None

        # Sadece hatalı satırları al
        self._hatali: list[SatirSonucu] = [
            s for s in son_sonuc.satirlar if not s.basarili
        ]

        self.setWindowTitle("Hatalı Kayıtları Düzenle")
        self.setMinimumSize(900, 520)
        self._kur_ui()

    # ────────────────────────────────────────────────────────────────
    # UI
    # ────────────────────────────────────────────────────────────────

    def _kur_ui(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(10)

        baslik = QLabel(
            f"Hatalı Satırlar ({len(self._hatali)} kayıt) — "
            "Düzenleme yaptıktan sonra 'Yeniden Aktar' butonuna basın."
        )
        baslik.setStyleSheet(f"color:{T.text}; font-weight:700; font-size:13px;")
        baslik.setWordWrap(True)
        lay.addWidget(baslik)

        self._alert = AlertBar(self)
        lay.addWidget(self._alert)

        self._tablo = QTableWidget()
        self._tablo.setAlternatingRowColors(True)
        self._tablo.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._tablo.verticalHeader().setVisible(False)
        lay.addWidget(self._tablo, 1)

        # Butonlar
        btn_lay = QHBoxLayout()
        btn_lay.addStretch(1)

        self._btn_aktar = QPushButton("Yeniden Aktar (güncelle / ekle)")
        self._btn_aktar.setStyleSheet(
            f"background:{T.accent}; color:#fff; "
            f"border-radius:{T.radius}px; padding:6px 16px;"
        )
        self._btn_aktar.clicked.connect(self._yeniden_aktar)

        btn_iptal = QPushButton("Kapat")
        btn_iptal.clicked.connect(self.reject)

        btn_lay.addWidget(btn_iptal)
        btn_lay.addWidget(self._btn_aktar)
        lay.addLayout(btn_lay)

        self._doldur()

    def _alanlar(self) -> list[str]:
        return [a.ad for a in self._konfig.alanlar]

    def _doldur(self) -> None:
        alanlar = self._alanlar()
        self._tablo.setColumnCount(len(alanlar) + 2)
        basliklar = ["Satır", *alanlar, "Hata"]
        self._tablo.setHorizontalHeaderLabels(basliklar)
        self._tablo.horizontalHeader().setStretchLastSection(True)

        self._tablo.setRowCount(len(self._hatali))
        for r, satir in enumerate(self._hatali):
            # Satır numarası — düzenlenemez
            satir_item = QTableWidgetItem(str(satir.satir_no))
            satir_item.setFlags(satir_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            satir_item.setForeground(
                self._tablo.palette().color(self._tablo.foregroundRole())
            )
            self._tablo.setItem(r, 0, satir_item)

            # Düzenlenebilir alan hücreleri
            for c, alan in enumerate(alanlar, start=1):
                item = QTableWidgetItem(str(satir.veri.get(alan) or ""))
                self._tablo.setItem(r, c, item)

            # Hata metni — düzenlenemez, renkli
            hata_item = QTableWidgetItem(str(satir.hata_mesaji or ""))
            hata_item.setFlags(hata_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            hata_item.setForeground(
                self._tablo.palette().color(self._tablo.foregroundRole())
            )
            self._tablo.setItem(r, len(alanlar) + 1, hata_item)

        self._tablo.resizeColumnsToContents()

    # ────────────────────────────────────────────────────────────────
    # Yeniden aktarım
    # ────────────────────────────────────────────────────────────────

    def _oku_duzeltilmis(self) -> list[dict]:
        """Tablo hücrelerinden düzeltilmiş veri diktlerini toplar."""
        alanlar = self._alanlar()
        kayitlar: list[dict] = []
        for r in range(self._tablo.rowCount()):
            kayit: dict = {}
            for c, alan in enumerate(alanlar, start=1):
                item = self._tablo.item(r, c)
                kayit[alan] = (item.text() if item else "").strip()
            kayitlar.append(kayit)
        return kayitlar

    def _yeniden_aktar(self) -> None:
        if not self._konfig.servis_metod_upsert:
            QMessageBox.warning(
                self,
                "Desteklenmiyor",
                "Bu import türü için güncelleme modu tanımlanmamış.",
            )
            return

        kayitlar = self._oku_duzeltilmis()

        try:
            import pandas as pd  # type: ignore[import-untyped]
        except ImportError:
            self._alert.goster("pandas yüklü değil, aktarım yapılamıyor.", "danger")
            return

        if self._konfig.normalize_fn:
            kayitlar = [self._konfig.normalize_fn(dict(k)) for k in kayitlar]

        df = pd.DataFrame(kayitlar)
        alanlar = self._alanlar()
        # Tüm alanları string harita ile direkt eşle
        harita = {a: a for a in alanlar if a in df.columns}
        for a in alanlar:
            if a not in df.columns:
                df[a] = ""

        try:
            sonuc = self._svc.import_et(
                df, harita, self._konfig, self._db, upsert=True
            )
        except Exception as exc:
            self._alert.goster(f"Aktarım hatası: {exc}", "danger")
            return

        self.yeniden_sonuc = sonuc

        tur = "success" if sonuc.hatali == 0 else "warning"
        self._alert.goster(
            f"Yeniden aktarım: Başarılı={sonuc.basarili}, Hatalı={sonuc.hatali}",
            tur,
        )

        # Hâlâ hatalı olanları tabloda göster
        self._hatali = [s for s in sonuc.satirlar if not s.basarili]
        self._doldur()

        if sonuc.hatali == 0:
            self._btn_aktar.setEnabled(False)
            self._btn_aktar.setText("Tüm kayıtlar aktarıldı")

    # ────────────────────────────────────────────────────────────────
    # Statik: CSV hata dosyasına marker yaz
    # ────────────────────────────────────────────────────────────────

    @staticmethod
    def hata_dosyasi_yaz(path: str, konfig: ImportKonfig, sonuc: ImportSonucu) -> None:
        """Hatalı satırları, re-import için işaretli CSV olarak kaydeder.

        Sutun duzeni:
          <alan etiketleri...> | Sorun (hata mesaji) | Sorunlu Alan | __hata__
        """
        alan_adlari  = [a.ad     for a in konfig.alanlar]
        alan_etiketi = [a.etiket for a in konfig.alanlar]
        marker = HataDuzeltmeDialog.HATA_KOLON_SONU

        def _temiz(val: str) -> str:
            return str(val or "").replace(";", ",").replace("\n", " ")

        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            basliklar = [*alan_etiketi, "Sorun (Hata Mesaji)", "Sorunlu Alan", marker]
            f.write(";".join(basliklar) + "\n")

            for satir in sonuc.satirlar:
                if satir.basarili:
                    continue
                values = [_temiz(satir.veri.get(ad, "")) for ad in alan_adlari]
                values.append(_temiz(satir.hata_mesaji))
                values.append(_temiz(getattr(satir, "hata_alani", "")))
                values.append("")   # __hata__ marker -- bos birakilir
                f.write(";".join(values) + "\n")
