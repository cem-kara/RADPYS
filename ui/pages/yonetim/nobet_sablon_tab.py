# -*- coding: utf-8 -*-
"""ui/pages/yonetim/nobet_sablon_tab.py - Nobet vardiya sablon yonetim sekmesi."""
from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from app.exceptions import AppHatasi
from app.logger import exc_logla
from app.services.nobet_service import NobetService
from ui.components import AlertBar, Card, DataTable, GhostButton, PrimaryButton
from ui.styles import T


class NobetSablonTab(QWidget):
    """Global vardiya sablonlari ve birime atama islemleri."""

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self._svc = NobetService(db)
        self._build()
        self.yenile()

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        self._alert = AlertBar(self)
        lay.addWidget(self._alert)

        info = QLabel(
            "Bu sekmede global vardiya sablonlari yonetilir ve secili nobet birimine atanir. "
            "Sure alani girilmez; baslangic ve bitis saatinden otomatik hesaplanir."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            f"color:{T.text2}; font-size:11px; padding:8px 12px;"
            f"background:{T.bg4}; border-radius:{T.radius_sm}px;"
            f"border-left:3px solid {T.accent};"
        )
        lay.addWidget(info)

        body = QHBoxLayout()
        body.setSpacing(14)
        body.addWidget(self._sablon_karti(), 1)
        body.addWidget(self._atama_karti(), 1)
        lay.addLayout(body, 1)

    def _sablon_karti(self) -> Card:
        kart = Card(self)
        kl = kart.layout_

        baslik = QLabel("Global Vardiya Sablonlari")
        baslik.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        kl.addWidget(baslik)

        self._tbl_sablon = DataTable(self)
        self._tbl_sablon.kur_kolonlar(
            [
                ("ad", "Sablon Adi", 180),
                ("baslangic_saat", "Baslangic", 75),
                ("bitis_saat", "Bitis", 75),
                ("saat_suresi", "Sure", 55),
            ],
            geren="ad",
        )
        kl.addWidget(self._tbl_sablon, 1)

        frm = QGridLayout()
        frm.setHorizontalSpacing(8)
        frm.setVerticalSpacing(6)

        frm.addWidget(self._etiket("Sablon Adi"), 0, 0, 1, 2)
        self._inp_sablon_ad = QLineEdit(self)
        self._inp_sablon_ad.setMinimumHeight(30)
        self._inp_sablon_ad.setPlaceholderText("Orn: Gece (20:00-08:00)")
        frm.addWidget(self._inp_sablon_ad, 1, 0, 1, 2)

        frm.addWidget(self._etiket("Baslangic"), 2, 0)
        self._inp_sablon_bas = QLineEdit(self)
        self._inp_sablon_bas.setMinimumHeight(30)
        self._inp_sablon_bas.setText("08:00")
        frm.addWidget(self._inp_sablon_bas, 3, 0)

        frm.addWidget(self._etiket("Bitis"), 2, 1)
        self._inp_sablon_bit = QLineEdit(self)
        self._inp_sablon_bit.setMinimumHeight(30)
        self._inp_sablon_bit.setText("16:00")
        frm.addWidget(self._inp_sablon_bit, 3, 1)

        kl.addLayout(frm)

        btns = QHBoxLayout()
        self._btn_sablon_ekle = PrimaryButton("Sablon Ekle")
        self._btn_sablon_ekle.clicked.connect(self._sablon_ekle)
        self._btn_sablon_pasif = GhostButton("Seciliyi Pasife Al")
        self._btn_sablon_pasif.clicked.connect(self._sablon_pasife_al)
        btns.addWidget(self._btn_sablon_ekle)
        btns.addWidget(self._btn_sablon_pasif)
        kl.addLayout(btns)

        return kart

    def _atama_karti(self) -> Card:
        kart = Card(self)
        kl = kart.layout_

        baslik = QLabel("Birime Sablon Ata")
        baslik.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        kl.addWidget(baslik)

        frm = QGridLayout()
        frm.setHorizontalSpacing(8)
        frm.setVerticalSpacing(6)

        frm.addWidget(self._etiket("Nobet Birimi"), 0, 0, 1, 2)
        self._cb_birim = QComboBox(self)
        self._cb_birim.setMinimumHeight(30)
        self._cb_birim.currentIndexChanged.connect(self._birim_degisti)
        frm.addWidget(self._cb_birim, 1, 0, 1, 2)

        frm.addWidget(self._etiket("Sablon Sec"), 2, 0, 1, 2)
        self._cb_ata_sablon = QComboBox(self)
        self._cb_ata_sablon.setMinimumHeight(30)
        frm.addWidget(self._cb_ata_sablon, 3, 0, 1, 2)

        frm.addWidget(self._etiket("Max Personel"), 4, 0)
        self._inp_ata_max = QLineEdit(self)
        self._inp_ata_max.setMinimumHeight(30)
        self._inp_ata_max.setText("1")
        frm.addWidget(self._inp_ata_max, 5, 0)

        kl.addLayout(frm)

        btns = QHBoxLayout()
        self._btn_ata = PrimaryButton("Birime Ata")
        self._btn_ata.clicked.connect(self._sablon_birime_ata)
        self._btn_esitle = GhostButton("Birimleri Eslestir")
        self._btn_esitle.clicked.connect(self._birimleri_esitle)
        btns.addWidget(self._btn_ata)
        btns.addWidget(self._btn_esitle)
        kl.addLayout(btns)

        alt = QLabel("Birim Vardiyalari")
        alt.setStyleSheet(f"color:{T.text2}; font-size:12px; font-weight:600;")
        kl.addWidget(alt)

        self._tbl_vardiya = DataTable(self)
        self._tbl_vardiya.kur_kolonlar(
            [
                ("sablon_ad", "Sablon", 150),
                ("baslangic_saat", "Baslangic", 72),
                ("bitis_saat", "Bitis", 72),
                ("max_personel", "Max P.", 55),
            ],
            geren="sablon_ad",
        )
        kl.addWidget(self._tbl_vardiya, 1)

        self._btn_vardiya_kaldir = GhostButton("Secili Vardiyayi Kaldir")
        self._btn_vardiya_kaldir.clicked.connect(self._birim_vardiya_kaldir)
        kl.addWidget(self._btn_vardiya_kaldir)

        return kart

    @staticmethod
    def _etiket(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{T.text2}; font-size:11px; font-weight:600;")
        return lbl

    @staticmethod
    def _saat_suresi_hesapla(baslangic: str, bitis: str) -> float:
        fmt = "%H:%M"
        bas = datetime.strptime(str(baslangic or "").strip(), fmt)
        bit = datetime.strptime(str(bitis or "").strip(), fmt)
        dakika = int((bit - bas).total_seconds() // 60)
        if dakika <= 0:
            dakika += 24 * 60
        return round(dakika / 60.0, 2)

    def yenile(self) -> None:
        self._alert.temizle()
        try:
            self._sablon_listesini_yukle()
            self._birim_listesini_yukle()
            self._birim_vardiya_listesini_yukle(str(self._cb_birim.currentData() or "").strip())
        except Exception as exc:
            exc_logla("NobetSablonTab.yenile", exc)
            self._alert.goster("Nobet sablon verileri yuklenemedi.", "danger")

    def _sablon_listesini_yukle(self) -> None:
        sablonlar = self._svc.sablon_listele()
        self._tbl_sablon.set_veri(sablonlar)

        self._cb_ata_sablon.blockSignals(True)
        self._cb_ata_sablon.clear()
        self._cb_ata_sablon.addItem("Sablon secin", "")
        for s in sablonlar:
            etiket = f"{str(s.get('ad') or '')} ({str(s.get('baslangic_saat') or '')}-{str(s.get('bitis_saat') or '')})"
            self._cb_ata_sablon.addItem(etiket, str(s.get("id") or ""))
        self._cb_ata_sablon.blockSignals(False)

    def _birim_listesini_yukle(self) -> None:
        secili = str(self._cb_birim.currentData() or "").strip() if self._cb_birim.count() > 0 else ""
        birimler = self._svc.birimler_listele(aktif_only=True)
        self._cb_birim.blockSignals(True)
        self._cb_birim.clear()
        self._cb_birim.addItem("Birim secin", "")
        for b in birimler:
            self._cb_birim.addItem(str(b.get("ad") or ""), str(b.get("id") or ""))
        idx = self._cb_birim.findData(secili)
        self._cb_birim.setCurrentIndex(idx if idx >= 0 else 0)
        self._cb_birim.blockSignals(False)

    def _birim_degisti(self) -> None:
        birim_id = str(self._cb_birim.currentData() or "").strip()
        self._birim_vardiya_listesini_yukle(birim_id)

    def _birim_vardiya_listesini_yukle(self, birim_id: str) -> None:
        if not birim_id:
            self._tbl_vardiya.set_veri([])
            return
        rows = self._svc.vardiya_listele(birim_id)
        for r in rows:
            if not str(r.get("sablon_ad") or "").strip():
                r["sablon_ad"] = str(r.get("ad") or "")
        self._tbl_vardiya.set_veri(rows)

    def _sablon_ekle(self) -> None:
        self._alert.temizle()
        try:
            sure = self._saat_suresi_hesapla(self._inp_sablon_bas.text(), self._inp_sablon_bit.text())
            self._svc.sablon_ekle(
                ad=self._inp_sablon_ad.text(),
                baslangic_saat=self._inp_sablon_bas.text(),
                bitis_saat=self._inp_sablon_bit.text(),
                saat_suresi=sure,
            )
            self._inp_sablon_ad.clear()
            self._sablon_listesini_yukle()
            self._alert.goster("Sablon eklendi.", "success")
        except ValueError:
            self._alert.goster("Saat formati HH:MM olmalidir.", "warning")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetSablonTab._sablon_ekle", exc)
            self._alert.goster("Sablon eklenemedi.", "danger")

    def _sablon_pasife_al(self) -> None:
        self._alert.temizle()
        row = self._tbl_sablon.secili_satir() or {}
        sid = str(row.get("id") or "").strip()
        if not sid:
            self._alert.goster("Pasife almak icin sablon seciniz.", "warning")
            return
        try:
            self._svc.sablon_pasife_al(sid)
            self._sablon_listesini_yukle()
            self._birim_vardiya_listesini_yukle(str(self._cb_birim.currentData() or "").strip())
            self._alert.goster("Sablon pasife alindi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetSablonTab._sablon_pasife_al", exc)
            self._alert.goster("Sablon pasife alinamadi.", "danger")

    def _sablon_birime_ata(self) -> None:
        self._alert.temizle()
        birim_id = str(self._cb_birim.currentData() or "").strip()
        sablon_id = str(self._cb_ata_sablon.currentData() or "").strip()
        try:
            max_p = int(self._inp_ata_max.text() or 1)
        except ValueError:
            self._alert.goster("Max personel gecerli bir sayi olmalidir.", "warning")
            return
        try:
            self._svc.sablon_birime_ata(birim_id, sablon_id, max_p)
            self._birim_vardiya_listesini_yukle(birim_id)
            self._alert.goster("Vardiya birime atandi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetSablonTab._sablon_birime_ata", exc)
            self._alert.goster("Vardiya atanamadi.", "danger")

    def _birim_vardiya_kaldir(self) -> None:
        self._alert.temizle()
        row = self._tbl_vardiya.secili_satir() or {}
        vid = str(row.get("id") or "").strip()
        if not vid:
            self._alert.goster("Kaldirmak icin birim vardiyasi seciniz.", "warning")
            return
        birim_id = str(self._cb_birim.currentData() or "").strip()
        try:
            self._svc.vardiya_pasife_al(vid)
            self._birim_vardiya_listesini_yukle(birim_id)
            self._alert.goster("Birim vardiyasi kaldirildi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetSablonTab._birim_vardiya_kaldir", exc)
            self._alert.goster("Kaldirilirken hata olustu.", "danger")

    def _birimleri_esitle(self) -> None:
        self._alert.temizle()
        try:
            adet = self._svc.birimleri_gorev_yerinden_esitle()
            self._birim_listesini_yukle()
            if adet > 0:
                self._alert.goster(f"{adet} yeni nobet birimi eklendi.", "success")
            else:
                self._alert.goster("Nobet birimleri zaten guncel.", "info")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetSablonTab._birimleri_esitle", exc)
            self._alert.goster("Birim esitleme sirasinda hata olustu.", "danger")
