# -*- coding: utf-8 -*-
"""Import sayfalari icin ortak iskelet UI."""
from __future__ import annotations

from collections import Counter
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.excel_import_service import ExcelImportService, ImportKonfig
from ui.components import AlertBar
from ui.pages.imports.components.hata_duzeltme_dialog import HataDuzeltmeDialog
from ui.styles import T

# Durum renkleri
_RENK_BASARILI = QColor(T.green2)
_RENK_HATA     = QColor(T.red)


class BaseImportPage(QWidget):
    """
    3 adımlı import iskeleti:
      1) Dosya Seç + Sütun Eşleştir
      2) İçe Aktar  →  tablo sadece HATALI satırları gösterir
      3) Hataları Düzelt (dosya veya program içi)
    """

    def __init__(self, db, kaydeden: str = "", parent=None):
        super().__init__(parent)
        self._db = db
        self._kaydeden = kaydeden
        self._svc = ExcelImportService()
        self._konfig_obj = self._konfig()

        self._df = None
        self._harita: dict[str, str] = {}
        self._dosya_yolu: Optional[str] = None
        self._esleme_combo: dict[str, QComboBox] = {}
        self._son_import_sonucu = None
        self._upsert_modu: bool = False

        self._kur_ui()

    def _konfig(self) -> ImportKonfig:
        raise NotImplementedError

    # -------------------------------------------------------------
    # UI kurulumu
    # -------------------------------------------------------------

    def _kur_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        # Başlık
        lbl = QLabel(self._konfig_obj.baslik)
        lbl.setStyleSheet(f"color:{T.text}; font-size:16px; font-weight:700;")
        root.addWidget(lbl)

        # Adım göstergesi (3 adım)
        adim = QFrame(self)
        adim_lay = QHBoxLayout(adim)
        adim_lay.setContentsMargins(10, 6, 10, 6)
        adim_lay.setSpacing(8)
        adim.setStyleSheet(
            f"QFrame{{background:{T.bg1}; border:1px solid {T.border}; border-radius:{T.radius}px;}}"
        )
        adim_lay.addWidget(QLabel("1) Dosya Seç + Sütun Eşleştir"))
        adim_lay.addWidget(QLabel("→ 2) İçe Aktar"))
        adim_lay.addWidget(QLabel("→ 3) Hataları Düzelt"))
        adim_lay.addStretch(1)
        root.addWidget(adim)

        # Uyarı bandı
        self._alert = AlertBar(self)
        root.addWidget(self._alert)

        # -- Buton satırı --------------------------------------
        btn_lay = QHBoxLayout()

        self._lbl_dosya = QLabel("Dosya seçilmedi")
        self._lbl_dosya.setStyleSheet(f"color:{T.text3};")

        self._lbl_upsert = QLabel("")
        self._lbl_upsert.setStyleSheet(f"color:{T.accent}; font-size:11px; font-weight:600;")
        self._lbl_upsert.hide()

        self._btn_sec = QPushButton("📂  Dosya Seç")
        self._btn_sec.clicked.connect(self._dosya_sec)

        self._btn_aktar = QPushButton("⬆  İçe Aktar")
        self._btn_aktar.setEnabled(False)
        self._btn_aktar.clicked.connect(self._aktar)
        self._btn_aktar.setStyleSheet(
            f"background:{T.accent}; color:#fff;"
            f"border-radius:{T.radius_sm}px; padding:5px 14px; font-weight:600;"
        )

        self._btn_hata_raporu = QPushButton("💾  Hata Dosyası İndir")
        self._btn_hata_raporu.setEnabled(False)
        self._btn_hata_raporu.clicked.connect(self._hata_raporu_kaydet)

        self._btn_duzenle = QPushButton("✏  Hataları Düzenle")
        self._btn_duzenle.setEnabled(False)
        self._btn_duzenle.setStyleSheet(
            f"background:{T.amber}; color:#fff;"
            f"border-radius:{T.radius_sm}px; padding:5px 14px; font-weight:600;"
        )
        self._btn_duzenle.clicked.connect(self._hatali_duzenle)

        btn_lay.addWidget(self._lbl_dosya, 1)
        btn_lay.addWidget(self._lbl_upsert)
        btn_lay.addWidget(self._btn_sec)
        btn_lay.addWidget(self._btn_aktar)
        btn_lay.addWidget(self._btn_hata_raporu)
        btn_lay.addWidget(self._btn_duzenle)
        root.addLayout(btn_lay)

        # -- Sütun eşleştirme kartı -----------------------------
        self._esleme_kart = QFrame(self)
        self._esleme_kart.setStyleSheet(
            f"QFrame{{background:{T.bg1}; border:1px solid {T.border}; border-radius:{T.radius}px;}}"
        )
        esleme_root = QVBoxLayout(self._esleme_kart)
        esleme_root.setContentsMargins(10, 10, 10, 10)
        esleme_root.setSpacing(8)

        esleme_baslik_lay = QHBoxLayout()
        esleme_baslik_lay.addWidget(
            QLabel("Sütun Eşleştirme — Excel sütunlarını uygulama alanlarıyla eşleştirin")
        )
        esleme_baslik_lay.addStretch(1)
        esleme_root.addLayout(esleme_baslik_lay)

        self._esleme_scroll = QScrollArea(self._esleme_kart)
        self._esleme_scroll.setWidgetResizable(True)
        self._esleme_scroll.setMaximumHeight(200)
        self._esleme_wrap = QWidget(self._esleme_scroll)
        self._esleme_grid = QGridLayout(self._esleme_wrap)
        self._esleme_grid.setContentsMargins(0, 0, 0, 0)
        self._esleme_grid.setHorizontalSpacing(10)
        self._esleme_grid.setVerticalSpacing(5)
        self._esleme_scroll.setWidget(self._esleme_wrap)
        esleme_root.addWidget(self._esleme_scroll)
        self._esleme_kart.hide()
        root.addWidget(self._esleme_kart)

        # -- Sonuç tablosu --------------------------------------
        # Başlangıçta boş "sonuç bekliyor" etiketi
        self._lbl_tablo_aciklama = QLabel(
            "İçe aktarım yapıldıktan sonra burada yalnızca hatalı satırlar gösterilir."
        )
        self._lbl_tablo_aciklama.setStyleSheet(f"color:{T.text3}; font-size:12px;")
        root.addWidget(self._lbl_tablo_aciklama)

        self._tablo = QTableWidget(self)
        self._tablo.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tablo.setAlternatingRowColors(False)
        self._tablo.verticalHeader().setVisible(False)
        self._tablo.setColumnCount(0)
        root.addWidget(self._tablo, 1)

        self._lbl_ozet = QLabel("")
        self._lbl_ozet.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._lbl_ozet.setStyleSheet(f"color:{T.text3}; font-size:12px;")
        root.addWidget(self._lbl_ozet)

    # -------------------------------------------------------------
    # Adım 1: Dosya seç + eşleştir
    # -------------------------------------------------------------

    def _dosya_sec(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Dosya Seç", "",
            "Excel / CSV Dosyaları (*.xlsx *.xls *.csv);;Tüm Dosyalar (*)",
        )
        if not path:
            return

        self._alert.temizle()
        self._dosya_yolu = path
        self._lbl_dosya.setText(path.split("\\")[-1])
        self._upsert_modu = False
        self._lbl_upsert.hide()
        self._btn_aktar.setEnabled(False)
        self._btn_hata_raporu.setEnabled(False)
        self._btn_duzenle.setEnabled(False)
        self._son_import_sonucu = None
        self._tablo.clearContents()
        self._tablo.setColumnCount(0)
        self._tablo.setRowCount(0)
        self._lbl_ozet.setText("")
        self._lbl_tablo_aciklama.show()
        self._dosya_hazirla()

    def _dosya_hazirla(self) -> None:
        if not self._dosya_yolu:
            return
        try:
            self._df = self._svc.excel_oku(self._dosya_yolu)
            kolonlar = list(self._df.columns)

            self._upsert_modu = HataDuzeltmeDialog.HATA_KOLON_SONU in kolonlar
            if self._upsert_modu:
                self._lbl_upsert.setText("[ DÜZELTME DOSYASI — güncelle / ekle modu ]")
                self._lbl_upsert.show()
                kolonlar = [c for c in kolonlar if c != HataDuzeltmeDialog.HATA_KOLON_SONU]
            else:
                self._lbl_upsert.hide()

            self._esleme_kur(kolonlar)
            self._btn_aktar.setEnabled(True)

            satirsay = len(self._df)
            mesaj = (
                f"Dosya yüklendi — {satirsay} satır. "
                "Sütun eşleştirmeyi kontrol edip 'İçe Aktar'a basın."
            )
            if self._upsert_modu:
                mesaj = f"Düzeltme dosyası — {satirsay} satır. Güncelle/ekle modu aktif."
            self._alert.goster(mesaj, "info")
        except Exception as exc:
            self._btn_aktar.setEnabled(False)
            self._esleme_kart.hide()
            self._alert.goster(str(exc), "danger")

    def _esleme_kur(self, kolonlar: list[str]) -> None:
        while self._esleme_grid.count():
            item = self._esleme_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._esleme_combo.clear()
        otomatik = self._svc.sutun_haritasi_olustur(kolonlar, self._konfig_obj)

        baslik_stil = f"color:{T.text2}; font-size:11px; font-weight:600;"
        lbl_us = QLabel("Uygulama Alanı")
        lbl_us.setStyleSheet(baslik_stil)
        lbl_ex = QLabel("Excel Sütunu")
        lbl_ex.setStyleSheet(baslik_stil)
        self._esleme_grid.addWidget(lbl_us, 0, 0)
        self._esleme_grid.addWidget(lbl_ex, 0, 1)

        for row_idx, alan in enumerate(self._konfig_obj.alanlar, start=1):
            zorunlu_isaret = " *" if alan.zorunlu else ""
            ad_lbl = QLabel(f"{alan.etiket}{zorunlu_isaret}")
            ad_lbl.setStyleSheet(
                f"color:{T.text};" if alan.zorunlu else f"color:{T.text2};"
            )

            cmb = QComboBox(self)
            cmb.addItem("(Atla)", "")
            for col in kolonlar:
                cmb.addItem(str(col), str(col))

            secilen = otomatik.get(alan.ad, "")
            pos = cmb.findData(secilen)
            cmb.setCurrentIndex(pos if pos >= 0 else 0)

            self._esleme_grid.addWidget(ad_lbl, row_idx, 0)
            self._esleme_grid.addWidget(cmb, row_idx, 1)
            self._esleme_combo[alan.ad] = cmb

        self._esleme_kart.show()

    def _secili_harita(self) -> dict[str, str]:
        harita: dict[str, str] = {}
        for alan in self._konfig_obj.alanlar:
            cmb = self._esleme_combo.get(alan.ad)
            if cmb is None:
                continue
            secilen = str(cmb.currentData() or "").strip()
            if secilen:
                harita[alan.ad] = secilen
        return harita

    def _zorunlu_harita_kontrol(self, harita: dict[str, str]) -> str:
        eksik: list[str] = []
        for alan in self._konfig_obj.alanlar:
            if not alan.zorunlu:
                continue
            if alan.varsayilan is not None:
                continue
            if alan.ad not in harita:
                eksik.append(alan.etiket)
        return ", ".join(eksik)

    # -------------------------------------------------------------
    # Adım 2: İçe aktar
    # -------------------------------------------------------------

    def _aktar(self) -> None:
        if self._df is None:
            return

        self._harita = self._secili_harita()
        eksik = self._zorunlu_harita_kontrol(self._harita)
        if eksik:
            self._alert.goster(f"Zorunlu alan eşleştirmesi eksik: {eksik}", "warning")
            return

        try:
            sonuc = self._svc.import_et(
                self._df, self._harita, self._konfig_obj, self._db,
                upsert=self._upsert_modu,
            )
            self._son_import_sonucu = sonuc
            self._hata_tablosu_doldur(sonuc)

            hatali_var = sonuc.hatali > 0
            self._btn_hata_raporu.setEnabled(hatali_var)
            self._btn_duzenle.setEnabled(
                hatali_var and bool(self._konfig_obj.servis_metod_upsert)
            )
            self._btn_aktar.setEnabled(False)   # tekrar import'u engelle

            if sonuc.hatali == 0:
                self._alert.goster(
                    f"✓ Tüm {sonuc.basarili} kayıt başarıyla aktarıldı.", "success"
                )
            else:
                ozet = self._hata_ozeti(sonuc)
                self._alert.goster(
                    f"{sonuc.basarili} kayıt aktarıldı — "
                    f"{sonuc.hatali} satırda sorun var. "
                    f"En sık: {ozet}",
                    "warning",
                )
        except Exception as exc:
            self._alert.goster(str(exc), "danger")

    # -------------------------------------------------------------
    # Sonuç tablosu — sadece HATALI satırlar
    # -------------------------------------------------------------

    def _hata_tablosu_doldur(self, sonuc) -> None:
        """Import sonrası tabloyu SADECE hatalı satırlarla doldurur.

        Sütun düzeni:
          Satır No | <alan etiketleri...> | Sorun (hata mesajı) | Sorunlu Alan
        """
        hatali = [s for s in sonuc.satirlar if not s.basarili]

        self._lbl_tablo_aciklama.hide()

        if not hatali:
            self._tablo.setColumnCount(1)
            self._tablo.setHorizontalHeaderLabels(["Durum"])
            self._tablo.setRowCount(1)
            item = QTableWidgetItem(f"✓ Tüm {sonuc.basarili} satır başarıyla aktarıldı.")
            item.setForeground(QBrush(_RENK_BASARILI))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._tablo.setItem(0, 0, item)
            self._lbl_ozet.setText(f"Toplam {sonuc.toplam} satır — hata yok.")
            return

        # Alan listesi (etiket başlıklarıyla)
        alanlar = self._konfig_obj.alanlar
        alan_adlari = [a.ad for a in alanlar]
        alan_etiketleri = [a.etiket for a in alanlar]

        sutun_sayisi = len(alanlar) + 3   # Satır No + alanlar + Sorun + Sorunlu Alan
        self._tablo.setColumnCount(sutun_sayisi)
        self._tablo.setHorizontalHeaderLabels(
            ["Satır", *alan_etiketleri, "⚠ Sorun (Ne Yapılmalı)", "Sorunlu Alan"]
        )
        self._tablo.horizontalHeader().setStretchLastSection(False)
        self._tablo.setRowCount(len(hatali))

        fiyatli_brush = QBrush(QColor(T.bg3))      # satır arkaplanı
        hata_brush = QBrush(_RENK_HATA)

        for r, satir in enumerate(hatali):
            # Satır No
            item_no = QTableWidgetItem(str(satir.satir_no))
            item_no.setFlags(item_no.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_no.setBackground(fiyatli_brush)
            self._tablo.setItem(r, 0, item_no)

            # Alan değerleri
            for c, (ad, etiket) in enumerate(zip(alan_adlari, alan_etiketleri), start=1):
                val = str(satir.veri.get(ad) or "")
                item_val = QTableWidgetItem(val)
                item_val.setFlags(item_val.flags() & ~Qt.ItemFlag.ItemIsEditable)
                # Sorunlu alan varsa vurgula
                if satir.hata_alani and satir.hata_alani == etiket:
                    item_val.setForeground(hata_brush)
                    item_val.setToolTip(f"Bu alan sorunlu: {satir.hata_mesaji}")
                self._tablo.setItem(r, c, item_val)

            # Sorun mesajı
            sorun_item = QTableWidgetItem(str(satir.hata_mesaji or ""))
            sorun_item.setFlags(sorun_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            sorun_item.setForeground(hata_brush)
            self._tablo.setItem(r, len(alanlar) + 1, sorun_item)

            # Sorunlu alan adı
            alan_item = QTableWidgetItem(str(satir.hata_alani or ""))
            alan_item.setFlags(alan_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            alan_item.setForeground(hata_brush)
            self._tablo.setItem(r, len(alanlar) + 2, alan_item)

        self._tablo.resizeColumnsToContents()
        self._lbl_ozet.setText(
            f"{sonuc.basarili}/{sonuc.toplam} satir aktarildi -- "
            f"{sonuc.hatali} duzeltilmesi gereken kayit asagida"
        )

    def _hata_raporu_kaydet(self) -> None:
        sonuc = self._son_import_sonucu
        if not sonuc or int(getattr(sonuc, "hatali", 0)) == 0:
            self._alert.goster("Kaydedilecek hata bulunmuyor.", "info")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Hata Dosyasini Kaydet", "import_hata_duzeltme.csv",
            "CSV Dosyasi (*.csv)",
        )
        if not path:
            return
        try:
            HataDuzeltmeDialog.hata_dosyasi_yaz(path, self._konfig_obj, sonuc)
            self._alert.goster(
                f"Hata dosyasi kaydedildi: {path.split(chr(92))[-1]}\n"
                "Dosyayi acin, Sorun sutununa bakin, ilgili alanlari duzeltip "
                "tekrar yukleyin -- sistem otomatik guncelleme moduna gecer.",
                "success",
            )
        except Exception as exc:
            self._alert.goster(f"Hata dosyasi kaydedilemedi: {exc}", "danger")

    def _hatali_duzenle(self) -> None:
        sonuc = self._son_import_sonucu
        if not sonuc or int(getattr(sonuc, "hatali", 0)) == 0:
            self._alert.goster("Duzenlenecek hata bulunmuyor.", "info")
            return
        dlg = HataDuzeltmeDialog(
            self._konfig_obj, sonuc, self._svc, self._db, self._kaydeden, self
        )
        dlg.exec()
        if dlg.yeniden_sonuc:
            self._son_import_sonucu = dlg.yeniden_sonuc
            self._hata_tablosu_doldur(dlg.yeniden_sonuc)
            hala_hatali = dlg.yeniden_sonuc.hatali > 0
            self._btn_duzenle.setEnabled(hala_hatali)
            self._btn_hata_raporu.setEnabled(hala_hatali)
            tur = "success" if not hala_hatali else "warning"
            self._alert.goster(
                f"Yeniden aktarim tamamlandi -- "
                f"Basarili: {dlg.yeniden_sonuc.basarili}, Hatali: {dlg.yeniden_sonuc.hatali}",
                tur,
            )

    @staticmethod
    def _hata_ozeti(sonuc) -> str:
        if not sonuc or int(getattr(sonuc, "hatali", 0)) <= 0:
            return ""
        sayac = Counter(
            str(s.hata_mesaji or "Bilinmeyen hata")
            for s in sonuc.satirlar
            if not s.basarili
        )
        parcalar = [f'"{mesaj}" ({adet}x)' for mesaj, adet in sayac.most_common(3)]
        return " | ".join(parcalar)
