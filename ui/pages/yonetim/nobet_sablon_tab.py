# -*- coding: utf-8 -*-
"""ui/pages/yonetim/nobet_sablon_tab.py - Nobet vardiya sablon yonetim sekmesi."""
from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import (
    QCheckBox,
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
        body.addWidget(self._birim_kural_karti(), 1)
        body.addWidget(self._sablon_karti(), 1)
        body.addWidget(self._atama_karti(), 1)
        lay.addLayout(body, 1)

    def _birim_kural_karti(self) -> Card:
        kart = Card(self)
        kl = kart.layout_

        baslik = QLabel("Birim Kurallari")
        baslik.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        kl.addWidget(baslik)

        frm = QGridLayout()
        frm.setHorizontalSpacing(8)
        frm.setVerticalSpacing(6)

        frm.addWidget(self._etiket("Nobet Birimi"), 0, 0, 1, 2)
        self._cb_kural_birim = QComboBox(self)
        self._cb_kural_birim.setMinimumHeight(30)
        self._cb_kural_birim.currentIndexChanged.connect(self._kural_birim_degisti)
        frm.addWidget(self._cb_kural_birim, 1, 0, 1, 2)

        frm.addWidget(self._etiket("Min Dinlenme (saat)"), 2, 0)
        self._inp_kural_min_dinlenme = QLineEdit(self)
        self._inp_kural_min_dinlenme.setMinimumHeight(30)
        self._inp_kural_min_dinlenme.setText("12")
        frm.addWidget(self._inp_kural_min_dinlenme, 3, 0)

        frm.addWidget(self._etiket("Tolerans (saat)"), 2, 1)
        self._inp_kural_tolerans = QLineEdit(self)
        self._inp_kural_tolerans.setMinimumHeight(30)
        self._inp_kural_tolerans.setText("7")
        frm.addWidget(self._inp_kural_tolerans, 3, 1)

        frm.addWidget(self._etiket("Max Fazla Mesai"), 4, 0)
        self._inp_kural_max_fazla = QLineEdit(self)
        self._inp_kural_max_fazla.setMinimumHeight(30)
        self._inp_kural_max_fazla.setText("0")
        frm.addWidget(self._inp_kural_max_fazla, 5, 0)

        frm.addWidget(self._etiket("Max Devreden Saat"), 4, 1)
        self._inp_kural_max_devreden = QLineEdit(self)
        self._inp_kural_max_devreden.setMinimumHeight(30)
        self._inp_kural_max_devreden.setText("12")
        frm.addWidget(self._inp_kural_max_devreden, 5, 1)

        frm.addWidget(self._etiket("Max Ardisik Nobet"), 6, 0)
        self._inp_kural_max_ardisik = QLineEdit(self)
        self._inp_kural_max_ardisik.setMinimumHeight(30)
        self._inp_kural_max_ardisik.setText("2")
        frm.addWidget(self._inp_kural_max_ardisik, 7, 0)

        self._chk_kural_resmi = QCheckBox("Resmi tatilde mesaiye dahil")
        self._chk_kural_dini = QCheckBox("Dini tatilde mesaiye dahil")
        self._chk_kural_manual = QCheckBox("Manuel limit asimina izinli")
        frm.addWidget(self._chk_kural_resmi, 8, 0, 1, 2)
        frm.addWidget(self._chk_kural_dini, 9, 0, 1, 2)
        frm.addWidget(self._chk_kural_manual, 10, 0, 1, 2)

        kl.addLayout(frm)

        self._btn_kural_kaydet = PrimaryButton("Birim Kuralini Kaydet")
        self._btn_kural_kaydet.clicked.connect(self._birim_kural_kaydet)
        kl.addWidget(self._btn_kural_kaydet)

        alt = QLabel("Personel Kanuni Mesai Duzenlemesi")
        alt.setStyleSheet(f"color:{T.text2}; font-size:12px; font-weight:600;")
        kl.addWidget(alt)

        kfrm = QGridLayout()
        kfrm.setHorizontalSpacing(8)
        kfrm.setVerticalSpacing(6)

        kfrm.addWidget(self._etiket("Personel"), 0, 0, 1, 2)
        self._cb_kanuni_personel = QComboBox(self)
        self._cb_kanuni_personel.setMinimumHeight(30)
        kfrm.addWidget(self._cb_kanuni_personel, 1, 0, 1, 2)

        kfrm.addWidget(self._etiket("Tip"), 2, 0)
        self._cb_kanuni_tip = QComboBox(self)
        self._cb_kanuni_tip.setMinimumHeight(30)
        self._cb_kanuni_tip.addItem("Saat Dusum", "saat_dusum")
        self._cb_kanuni_tip.addItem("Oran (%)", "oran")
        self._cb_kanuni_tip.addItem("Manuel Hedef Saat", "manuel_hedef")
        self._cb_kanuni_tip.addItem("Sut Izni (0-6 Ay)", "sut_0_6")
        self._cb_kanuni_tip.addItem("Sut Izni (6-12 Ay)", "sut_6_12")
        self._cb_kanuni_tip.addItem("Yarim Zamanli", "yarim_zamanli")
        kfrm.addWidget(self._cb_kanuni_tip, 3, 0)

        kfrm.addWidget(self._etiket("Deger"), 2, 1)
        self._inp_kanuni_deger = QLineEdit(self)
        self._inp_kanuni_deger.setMinimumHeight(30)
        self._inp_kanuni_deger.setText("0")
        kfrm.addWidget(self._inp_kanuni_deger, 3, 1)

        kfrm.addWidget(self._etiket("Baslangic (YYYY-AA-GG)"), 4, 0)
        self._inp_kanuni_bas = QLineEdit(self)
        self._inp_kanuni_bas.setMinimumHeight(30)
        self._inp_kanuni_bas.setPlaceholderText("2026-01-01")
        kfrm.addWidget(self._inp_kanuni_bas, 5, 0)

        kfrm.addWidget(self._etiket("Bitis (opsiyonel)"), 4, 1)
        self._inp_kanuni_bit = QLineEdit(self)
        self._inp_kanuni_bit.setMinimumHeight(30)
        self._inp_kanuni_bit.setPlaceholderText("2026-06-30")
        kfrm.addWidget(self._inp_kanuni_bit, 5, 1)

        kfrm.addWidget(self._etiket("Aciklama"), 6, 0, 1, 2)
        self._inp_kanuni_aciklama = QLineEdit(self)
        self._inp_kanuni_aciklama.setMinimumHeight(30)
        kfrm.addWidget(self._inp_kanuni_aciklama, 7, 0, 1, 2)
        kl.addLayout(kfrm)

        kbtn = QHBoxLayout()
        self._btn_kanuni_ekle = PrimaryButton("Kanuni Duzenleme Ekle")
        self._btn_kanuni_ekle.clicked.connect(self._kanuni_duzenleme_ekle)
        self._btn_kanuni_pasif = GhostButton("Secili Duzenlemeyi Pasife Al")
        self._btn_kanuni_pasif.clicked.connect(self._kanuni_duzenleme_pasife_al)
        kbtn.addWidget(self._btn_kanuni_ekle)
        kbtn.addWidget(self._btn_kanuni_pasif)
        kl.addLayout(kbtn)

        self._tbl_kanuni = DataTable(self)
        self._tbl_kanuni.kur_kolonlar(
            [
                ("ad_soyad", "Personel", 140),
                ("duzenleme_tipi", "Tip", 85),
                ("deger", "Deger", 55),
                ("baslangic_tarih", "Bas", 75),
                ("bitis_tarih", "Bit", 75),
            ],
            geren="ad_soyad",
        )
        kl.addWidget(self._tbl_kanuni, 1)

        return kart

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
            self._kural_birim_degisti()
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
        secili_kural = str(self._cb_kural_birim.currentData() or "").strip() if self._cb_kural_birim.count() > 0 else ""
        birimler = self._svc.birimler_listele(aktif_only=True)

        self._cb_birim.blockSignals(True)
        self._cb_birim.clear()
        self._cb_birim.addItem("Birim secin", "")

        self._cb_kural_birim.blockSignals(True)
        self._cb_kural_birim.clear()
        self._cb_kural_birim.addItem("Birim secin", "")

        for b in birimler:
            etiket = str(b.get("ad") or "")
            deger = str(b.get("id") or "")
            self._cb_birim.addItem(etiket, deger)
            self._cb_kural_birim.addItem(etiket, deger)

        idx = self._cb_birim.findData(secili)
        self._cb_birim.setCurrentIndex(idx if idx >= 0 else 0)
        self._cb_birim.blockSignals(False)

        idx_kural = self._cb_kural_birim.findData(secili_kural)
        self._cb_kural_birim.setCurrentIndex(idx_kural if idx_kural >= 0 else 0)
        self._cb_kural_birim.blockSignals(False)

    def _kural_birim_degisti(self) -> None:
        birim_id = str(self._cb_kural_birim.currentData() or "").strip()
        if not birim_id:
            self._inp_kural_min_dinlenme.setText("12")
            self._inp_kural_tolerans.setText("7")
            self._inp_kural_max_fazla.setText("0")
            self._inp_kural_max_devreden.setText("12")
            self._inp_kural_max_ardisik.setText("2")
            self._chk_kural_resmi.setChecked(False)
            self._chk_kural_dini.setChecked(False)
            self._chk_kural_manual.setChecked(False)
            self._cb_kanuni_personel.clear()
            self._cb_kanuni_personel.addItem("Personel secin", "")
            self._tbl_kanuni.set_veri([])
            return
        try:
            kural = self._svc.birim_kural_getir(birim_id)
            self._inp_kural_min_dinlenme.setText(str(kural.get("min_dinlenme_saat") or 12))
            self._inp_kural_tolerans.setText(str(kural.get("tolerans_saat") or 7))
            self._inp_kural_max_fazla.setText(str(kural.get("max_fazla_mesai_saat") or 0))
            self._inp_kural_max_devreden.setText(str(kural.get("max_devreden_saat") or 12))
            self._inp_kural_max_ardisik.setText(str(kural.get("max_ardisik_nobet") or 2))
            self._chk_kural_resmi.setChecked(bool(kural.get("resmi_tatil_calisma")))
            self._chk_kural_dini.setChecked(bool(kural.get("dini_tatil_calisma")))
            self._chk_kural_manual.setChecked(bool(kural.get("manuel_limit_asimina_izin")))
            self._kanuni_personel_listesini_yukle(birim_id)
            self._kanuni_liste_yukle(birim_id)
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetSablonTab._kural_birim_degisti", exc)
            self._alert.goster("Birim kurali yuklenemedi.", "danger")

    def _kanuni_personel_listesini_yukle(self, birim_id: str) -> None:
        rows = self._svc.birim_personel_kosullari_listele(birim_id)
        self._cb_kanuni_personel.blockSignals(True)
        self._cb_kanuni_personel.clear()
        self._cb_kanuni_personel.addItem("Personel secin", "")
        for r in rows:
            ad = str(r.get("ad") or "").strip()
            soyad = str(r.get("soyad") or "").strip()
            pid = str(r.get("personel_id") or "").strip()
            self._cb_kanuni_personel.addItem(f"{ad} {soyad}".strip(), pid)
        self._cb_kanuni_personel.blockSignals(False)

    def _kanuni_liste_yukle(self, birim_id: str) -> None:
        rows = self._svc.personel_kanuni_mesai_listele(birim_id)
        for r in rows:
            ad = str(r.get("ad") or "").strip()
            soyad = str(r.get("soyad") or "").strip()
            r["ad_soyad"] = f"{ad} {soyad}".strip()
        self._tbl_kanuni.set_veri(rows)

    def _kanuni_duzenleme_ekle(self) -> None:
        self._alert.temizle()
        birim_id = str(self._cb_kural_birim.currentData() or "").strip()
        personel_id = str(self._cb_kanuni_personel.currentData() or "").strip()
        tip = str(self._cb_kanuni_tip.currentData() or "").strip()
        try:
            deger = float(self._inp_kanuni_deger.text() or 0)
        except ValueError:
            self._alert.goster("Deger alani sayisal olmalidir.", "warning")
            return
        try:
            self._svc.personel_kanuni_mesai_ekle(
                birim_id=birim_id,
                personel_id=personel_id,
                baslangic_tarih=self._inp_kanuni_bas.text(),
                bitis_tarih=self._inp_kanuni_bit.text(),
                duzenleme_tipi=tip,
                deger=deger,
                aciklama=self._inp_kanuni_aciklama.text(),
            )
            self._kanuni_liste_yukle(birim_id)
            self._alert.goster("Kanuni duzenleme eklendi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetSablonTab._kanuni_duzenleme_ekle", exc)
            self._alert.goster("Kanuni duzenleme eklenemedi.", "danger")

    def _kanuni_duzenleme_pasife_al(self) -> None:
        self._alert.temizle()
        row = self._tbl_kanuni.secili_satir() or {}
        kid = str(row.get("id") or "").strip()
        if not kid:
            self._alert.goster("Pasife almak icin bir kayit seciniz.", "warning")
            return
        birim_id = str(self._cb_kural_birim.currentData() or "").strip()
        try:
            self._svc.personel_kanuni_mesai_pasife_al(kid)
            self._kanuni_liste_yukle(birim_id)
            self._alert.goster("Kanuni duzenleme pasife alindi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetSablonTab._kanuni_duzenleme_pasife_al", exc)
            self._alert.goster("Kayit pasife alinamadi.", "danger")

    def _birim_kural_kaydet(self) -> None:
        self._alert.temizle()
        birim_id = str(self._cb_kural_birim.currentData() or "").strip()
        try:
            self._svc.birim_kural_kaydet(
                birim_id,
                {
                    "min_dinlenme_saat": float(self._inp_kural_min_dinlenme.text() or 12),
                    "resmi_tatil_calisma": self._chk_kural_resmi.isChecked(),
                    "dini_tatil_calisma": self._chk_kural_dini.isChecked(),
                    "arefe_baslangic_saat": "13:00",
                    "max_fazla_mesai_saat": float(self._inp_kural_max_fazla.text() or 0),
                    "tolerans_saat": float(self._inp_kural_tolerans.text() or 7),
                    "max_devreden_saat": float(self._inp_kural_max_devreden.text() or 12),
                    "max_ardisik_nobet": int(self._inp_kural_max_ardisik.text() or 2),
                    "manuel_limit_asimina_izin": self._chk_kural_manual.isChecked(),
                },
            )
            self._alert.goster("Birim kurali kaydedildi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except ValueError:
            self._alert.goster("Sayisal alanlarda gecerli deger giriniz.", "warning")
        except Exception as exc:
            exc_logla("NobetSablonTab._birim_kural_kaydet", exc)
            self._alert.goster("Birim kurali kaydedilemedi.", "danger")

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
