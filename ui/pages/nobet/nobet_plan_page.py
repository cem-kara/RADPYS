# -*- coding: utf-8 -*-
"""ui/pages/nobet/nobet_plan_page.py - Nöbet koşulları ve plan hazırlık ekranı."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.exceptions import AppHatasi
from app.logger import exc_logla
from app.services.nobet_service import NobetService
from ui.components import AlertBar, Card, DataTable, GhostButton, PrimaryButton
from ui.styles import T


class NobetPlanPage(QWidget):
    """Nobet planindan once birim ve personel kosullarinin tanimlandigi ekran."""

    def __init__(self, db=None, oturum: dict | None = None, parent=None):
        super().__init__(parent)
        self._db = db
        self._oturum = oturum
        self._svc = NobetService(db) if db is not None else None
        self._secili_plan_id: str | None = None

        self.setStyleSheet(f"background:{T.bg0};")
        self._build()
        self.load_data()

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 14, 20, 14)
        lay.setSpacing(12)

        self._alert = AlertBar(self)
        lay.addWidget(self._alert)

        header = QLabel("Nobet Kosullari ve Plan Hazirlik")
        header.setStyleSheet(f"color:{T.text}; font-size:18px; font-weight:700;")
        lay.addWidget(header)

        info = QLabel(
            "Plan olusturmadan once birim kurali, slot ve personel kosullari burada belirlenir. "
            "Slot sayisi her birim icin degisken olabilir."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            f"color:{T.text2}; font-size:11px; padding:8px 12px;"
            f"background:{T.bg4}; border-radius:{T.radius_sm}px;"
            f"border-left:3px solid {T.accent};"
        )
        lay.addWidget(info)

        tabs = QTabWidget(self)
        tabs.addTab(self._kosul_sekmesi(), "Kosullar")
        tabs.addTab(self._plan_sekmesi(), "Plan")
        lay.addWidget(tabs, 1)

    def _kosul_sekmesi(self) -> QWidget:
        w = QWidget(self)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)
        lay.addWidget(self._birim_kural_karti(), 1)
        lay.addWidget(self._sablon_yonetim_karti(), 1)
        lay.addWidget(self._personel_kural_karti(), 1)
        return w

    def _plan_sekmesi(self) -> QWidget:
        w = QWidget(self)
        body = QHBoxLayout(w)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(14)
        body.addWidget(self._form_karti(), 0)
        body.addWidget(self._liste_karti(), 1)
        return w

    def _birim_kural_karti(self) -> Card:
        kart = Card(self)
        kl = kart.layout_

        title = QLabel("Birim Kurali")
        title.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        kl.addWidget(title)

        frm = QGridLayout()
        frm.setHorizontalSpacing(8)
        frm.setVerticalSpacing(8)

        frm.addWidget(self._etiket("Birim"), 0, 0, 1, 2)
        self._cb_kural_birim = QComboBox(self)
        self._cb_kural_birim.setMinimumHeight(32)
        self._cb_kural_birim.currentIndexChanged.connect(self._kosul_birim_degisti)
        frm.addWidget(self._cb_kural_birim, 1, 0, 1, 2)

        frm.addWidget(self._etiket("Min Dinlenme (saat)"), 2, 0)
        self._inp_min_dinlenme = QLineEdit(self)
        self._inp_min_dinlenme.setMinimumHeight(32)
        self._inp_min_dinlenme.setText("12")
        frm.addWidget(self._inp_min_dinlenme, 3, 0)

        frm.addWidget(self._etiket("Arefe Baslangic"), 2, 1)
        self._inp_arefe = QLineEdit(self)
        self._inp_arefe.setMinimumHeight(32)
        self._inp_arefe.setText("13:00")
        frm.addWidget(self._inp_arefe, 3, 1)

        frm.addWidget(self._etiket("Tolerans Saat"), 4, 0)
        self._inp_tolerans = QLineEdit(self)
        self._inp_tolerans.setMinimumHeight(32)
        self._inp_tolerans.setText("7")
        frm.addWidget(self._inp_tolerans, 5, 0)

        frm.addWidget(self._etiket("Max Devreden Saat"), 4, 1)
        self._inp_devreden = QLineEdit(self)
        self._inp_devreden.setMinimumHeight(32)
        self._inp_devreden.setText("12")
        frm.addWidget(self._inp_devreden, 5, 1)

        frm.addWidget(self._etiket("Max Fazla Mesai"), 6, 0)
        self._inp_max_fazla = QLineEdit(self)
        self._inp_max_fazla.setMinimumHeight(32)
        self._inp_max_fazla.setText("0")
        self._inp_max_fazla.setToolTip("0 = birim limiti tanimsiz")
        frm.addWidget(self._inp_max_fazla, 7, 0)

        self._chk_resmi = QCheckBox("Resmi tatilde mesaiye dahil")
        self._chk_dini = QCheckBox("Dini tatilde mesaiye dahil")
        self._chk_limit_override = QCheckBox("Manuel limit asimi izinli")
        frm.addWidget(self._chk_resmi, 8, 0, 1, 2)
        frm.addWidget(self._chk_dini, 9, 0, 1, 2)
        frm.addWidget(self._chk_limit_override, 10, 0, 1, 2)

        kl.addLayout(frm)

        self._btn_kural_kaydet = PrimaryButton("Birim Kuralini Kaydet")
        self._btn_kural_kaydet.clicked.connect(self._birim_kural_kaydet)
        kl.addWidget(self._btn_kural_kaydet)
        kl.addStretch(1)
        return kart

    def _sablon_yonetim_karti(self) -> Card:
        """Global vardiya şablonları ve birime şablon atama."""
        kart = Card(self)
        kl = kart.layout_

        title = QLabel("Vardiya Sablonlari")
        title.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        kl.addWidget(title)

        # ── Global şablon listesi ──────────────────────────────────
        lbl_sablon = QLabel("Tum Sablon Listesi")
        lbl_sablon.setStyleSheet(f"color:{T.text2}; font-size:12px; font-weight:600;")
        kl.addWidget(lbl_sablon)

        self._tbl_sablon = DataTable(self)
        self._tbl_sablon.kur_kolonlar(
            [
                ("ad", "Sablon Adi", 190),
                ("baslangic_saat", "Baslangic", 75),
                ("bitis_saat", "Bitis", 75),
                ("saat_suresi", "Sure", 55),
            ],
            geren="ad",
        )
        kl.addWidget(self._tbl_sablon, 1)

        sf = QGridLayout()
        sf.setHorizontalSpacing(8)
        sf.setVerticalSpacing(6)
        sf.addWidget(self._etiket("Sablon Adi"), 0, 0, 1, 2)
        self._inp_sablon_ad = QLineEdit(self)
        self._inp_sablon_ad.setPlaceholderText("Orn: Gece (20:00-08:00)")
        self._inp_sablon_ad.setMinimumHeight(30)
        sf.addWidget(self._inp_sablon_ad, 1, 0, 1, 2)

        sf.addWidget(self._etiket("Baslangic"), 2, 0)
        self._inp_sablon_bas = QLineEdit(self)
        self._inp_sablon_bas.setText("08:00")
        self._inp_sablon_bas.setMinimumHeight(30)
        sf.addWidget(self._inp_sablon_bas, 3, 0)

        sf.addWidget(self._etiket("Bitis"), 2, 1)
        self._inp_sablon_bit = QLineEdit(self)
        self._inp_sablon_bit.setText("16:00")
        self._inp_sablon_bit.setMinimumHeight(30)
        sf.addWidget(self._inp_sablon_bit, 3, 1)

        sf.addWidget(self._etiket("Sure (saat)"), 4, 0)
        self._inp_sablon_sure = QLineEdit(self)
        self._inp_sablon_sure.setText("8")
        self._inp_sablon_sure.setMinimumHeight(30)
        sf.addWidget(self._inp_sablon_sure, 5, 0)
        kl.addLayout(sf)

        btn_sablon_ekle = GhostButton("Sablon Ekle")
        btn_sablon_ekle.clicked.connect(self._sablon_ekle)
        btn_sablon_pasif = GhostButton("Seciyi Pasife Al")
        btn_sablon_pasif.clicked.connect(self._sablon_pasife_al)
        sb = QHBoxLayout()
        sb.addWidget(btn_sablon_ekle, 1)
        sb.addWidget(btn_sablon_pasif, 1)
        kl.addLayout(sb)

        kl.addWidget(self._ayrac())

        # ── Birime şablon atama ───────────────────────────────────
        lbl_ata = QLabel("Birime Vardiya Ata")
        lbl_ata.setStyleSheet(f"color:{T.text2}; font-size:12px; font-weight:600;")
        kl.addWidget(lbl_ata)

        af = QGridLayout()
        af.setHorizontalSpacing(8)
        af.setVerticalSpacing(6)
        af.addWidget(self._etiket("Sablon Sec"), 0, 0, 1, 2)
        self._cb_ata_sablon = QComboBox(self)
        self._cb_ata_sablon.setMinimumHeight(30)
        af.addWidget(self._cb_ata_sablon, 1, 0, 1, 2)

        af.addWidget(self._etiket("Max Personel"), 2, 0)
        self._inp_ata_max = QLineEdit(self)
        self._inp_ata_max.setText("1")
        self._inp_ata_max.setMinimumHeight(30)
        af.addWidget(self._inp_ata_max, 3, 0)
        kl.addLayout(af)

        btn_ata = PrimaryButton("Birime Ata")
        btn_ata.clicked.connect(self._sablon_birime_ata)
        kl.addWidget(btn_ata)

        lbl_birim_vrd = QLabel("Birim Vardiyalari")
        lbl_birim_vrd.setStyleSheet(f"color:{T.text2}; font-size:12px; font-weight:600;")
        kl.addWidget(lbl_birim_vrd)

        self._tbl_slot = DataTable(self)
        self._tbl_slot.kur_kolonlar(
            [
                ("sablon_ad", "Sablon", 150),
                ("baslangic_saat", "Baslangic", 72),
                ("bitis_saat", "Bitis", 72),
                ("max_personel", "Max P.", 55),
            ],
            geren="sablon_ad",
        )
        kl.addWidget(self._tbl_slot, 1)

        btn_vrd_pasif = GhostButton("Secili Vardiyayi Kaldir")
        btn_vrd_pasif.clicked.connect(self._birim_vardiya_kaldir)
        kl.addWidget(btn_vrd_pasif)
        return kart

    def _personel_kural_karti(self) -> Card:
        kart = Card(self)
        kl = kart.layout_

        title = QLabel("Personel Nobet Kosullari")
        title.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        kl.addWidget(title)

        self._tbl_personel = DataTable(self)
        self._tbl_personel.kur_kolonlar(
            [
                ("ad_soyad", "Personel", 200),
                ("ister_24_txt", "24s", 50),
                ("mesai_txt", "Mesai", 60),
                ("max_fazla_mesai_saat", "Max FM", 70),
                ("tolerans_saat", "Tol", 50),
                ("max_devreden_saat", "Devir", 55),
            ],
            geren="ad_soyad",
        )
        self._tbl_personel.clicked.connect(self._personel_secildi)
        kl.addWidget(self._tbl_personel, 1)

        self._btn_personel_esitle = GhostButton("Birim Personelini Eslestir")
        self._btn_personel_esitle.clicked.connect(self._personeli_esitle)
        kl.addWidget(self._btn_personel_esitle)

        pf = QGridLayout()
        pf.setHorizontalSpacing(8)
        pf.setVerticalSpacing(8)
        self._chk_24 = QCheckBox("24 saat nobet ister")
        self._chk_mesai = QCheckBox("Mesai istemiyor")
        pf.addWidget(self._chk_24, 0, 0, 1, 2)
        pf.addWidget(self._chk_mesai, 1, 0, 1, 2)

        pf.addWidget(self._etiket("Max Fazla Mesai"), 2, 0)
        self._inp_p_max_fazla = QLineEdit(self)
        self._inp_p_max_fazla.setMinimumHeight(32)
        self._inp_p_max_fazla.setText("0")
        pf.addWidget(self._inp_p_max_fazla, 3, 0)

        pf.addWidget(self._etiket("Tolerans Saat"), 2, 1)
        self._inp_p_tolerans = QLineEdit(self)
        self._inp_p_tolerans.setMinimumHeight(32)
        self._inp_p_tolerans.setText("7")
        pf.addWidget(self._inp_p_tolerans, 3, 1)

        pf.addWidget(self._etiket("Max Devreden Saat"), 4, 0)
        self._inp_p_devreden = QLineEdit(self)
        self._inp_p_devreden.setMinimumHeight(32)
        self._inp_p_devreden.setText("12")
        pf.addWidget(self._inp_p_devreden, 5, 0)
        kl.addLayout(pf)

        self._btn_personel_kaydet = PrimaryButton("Secili Personel Kosulunu Kaydet")
        self._btn_personel_kaydet.clicked.connect(self._personel_kosul_kaydet)
        kl.addWidget(self._btn_personel_kaydet)

        self._lbl_personel = QLabel("Personel seciniz")
        self._lbl_personel.setStyleSheet(f"color:{T.text3}; font-size:11px;")
        kl.addWidget(self._lbl_personel)
        return kart

    def _form_karti(self) -> Card:
        kart = Card(self)
        kart.setFixedWidth(320)
        kl = kart.layout_

        title = QLabel("Taslak Plan Olustur")
        title.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        kl.addWidget(title)

        frm = QGridLayout()
        frm.setHorizontalSpacing(8)
        frm.setVerticalSpacing(8)

        frm.addWidget(self._etiket("Nobet Birimi"), 0, 0, 1, 2)
        self._cb_birim = QComboBox(self)
        self._cb_birim.setMinimumHeight(32)
        frm.addWidget(self._cb_birim, 1, 0, 1, 2)

        frm.addWidget(self._etiket("Yil"), 2, 0)
        self._cb_yil = QComboBox(self)
        self._cb_yil.setMinimumHeight(32)
        for y in range(2025, 2036):
            self._cb_yil.addItem(str(y), y)
        frm.addWidget(self._cb_yil, 3, 0)

        frm.addWidget(self._etiket("Ay"), 2, 1)
        self._cb_ay = QComboBox(self)
        self._cb_ay.setMinimumHeight(32)
        for m in range(1, 13):
            self._cb_ay.addItem(f"{m:02d}", m)
        frm.addWidget(self._cb_ay, 3, 1)

        frm.addWidget(self._etiket("Notlar"), 4, 0, 1, 2)
        self._inp_not = QLineEdit(self)
        self._inp_not.setPlaceholderText("Istege bagli not")
        self._inp_not.setMinimumHeight(32)
        frm.addWidget(self._inp_not, 5, 0, 1, 2)

        kl.addLayout(frm)
        kl.addWidget(self._ayrac())

        self._btn_esitle = GhostButton("Birimleri Eslestir")
        self._btn_esitle.clicked.connect(self._birimleri_esitle)
        kl.addWidget(self._btn_esitle)

        self._btn_olustur = PrimaryButton("Taslak Plan Olustur")
        self._btn_olustur.clicked.connect(self._plan_olustur)
        kl.addWidget(self._btn_olustur)

        self._btn_yenile = GhostButton("Yenile")
        self._btn_yenile.clicked.connect(self.load_data)
        kl.addWidget(self._btn_yenile)

        kl.addStretch(1)
        return kart

    def _liste_karti(self) -> Card:
        kart = Card(self)
        kl = kart.layout_

        title = QLabel("Kayitli Nobet Planlari")
        title.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        kl.addWidget(title)

        self._tbl = DataTable(self)
        self._tbl.kur_kolonlar(
            [
                ("birim_ad", "Birim", 220),
                ("donem", "Donem", 100),
                ("durum_txt", "Durum", 90),
                ("satir_sayisi", "Satir", 70),
                ("olusturuldu", "Olusturuldu", 110),
            ],
            geren="birim_ad",
        )
        self._tbl.clicked.connect(self._satir_secildi)
        kl.addWidget(self._tbl, 1)

        self._lbl_ozet = QLabel("")
        self._lbl_ozet.setStyleSheet(f"color:{T.text3}; font-size:11px;")
        kl.addWidget(self._lbl_ozet)

        return kart

    @staticmethod
    def _etiket(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{T.text2}; font-size:11px; font-weight:600;")
        return lbl

    @staticmethod
    def _ayrac() -> QWidget:
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background:{T.border};")
        return line

    def _set_varsayilan_donem(self) -> None:
        if self._svc is None:
            return
        yil, ay = self._svc.varsayilan_donem()
        idx_y = self._cb_yil.findData(yil)
        if idx_y >= 0:
            self._cb_yil.setCurrentIndex(idx_y)
        idx_m = self._cb_ay.findData(ay)
        if idx_m >= 0:
            self._cb_ay.setCurrentIndex(idx_m)

    def load_data(self) -> None:
        self._alert.temizle()
        if self._svc is None:
            self._tbl.set_veri([])
            self._lbl_ozet.setText("Veritabani baglantisi bulunamadi.")
            return

        try:
            birimler = self._svc.birimler_listele(aktif_only=True)
            self._cb_birim.blockSignals(True)
            self._cb_kural_birim.blockSignals(True)
            self._cb_birim.clear()
            self._cb_kural_birim.clear()
            self._cb_birim.addItem("Birim secin", "")
            self._cb_kural_birim.addItem("Birim secin", "")
            for b in birimler:
                self._cb_birim.addItem(str(b.get("ad") or ""), str(b.get("id") or ""))
                self._cb_kural_birim.addItem(str(b.get("ad") or ""), str(b.get("id") or ""))
            self._cb_birim.blockSignals(False)
            self._cb_kural_birim.blockSignals(False)

            # Sablon listesini yenile
            self._sablon_listesini_yukle()

            plans = self._svc.planlari_listele()
            for p in plans:
                p["donem"] = f"{int(p.get('yil') or 0)}-{int(p.get('ay') or 0):02d}"
                p["durum_txt"] = str(p.get("durum") or "").title()
            self._tbl.set_veri(plans)
            self._lbl_ozet.setText(
                f"Aktif birim: {len(birimler)} | Plan sayisi: {len(plans)}"
            )
            self._set_varsayilan_donem()
            self._kosul_birim_degisti()
        except Exception as exc:
            exc_logla("NobetPlanPage.load_data", exc)
            self._tbl.set_veri([])
            self._lbl_ozet.setText("Nobet verileri yuklenemedi.")
            self._alert.goster(str(exc), "danger")

    def _satir_secildi(self, _index) -> None:
        row = self._tbl.secili_satir()
        self._secili_plan_id = str((row or {}).get("id") or "") or None

    def _birimleri_esitle(self) -> None:
        self._alert.temizle()
        if self._svc is None:
            return
        try:
            adet = self._svc.birimleri_gorev_yerinden_esitle()
            self.load_data()
            if adet > 0:
                self._alert.goster(f"{adet} yeni nobet birimi eklendi.", "success")
            else:
                self._alert.goster("Nobet birimleri zaten guncel.", "info")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetPlanPage._birimleri_esitle", exc)
            self._alert.goster("Birim esitleme sirasinda hata olustu.", "danger")

    def _kosul_birim_degisti(self) -> None:
        if self._svc is None:
            return
        birim_id = str(self._cb_kural_birim.currentData() or "").strip()
        if not birim_id:
            self._tbl_slot.set_veri([])
            self._tbl_personel.set_veri([])
            return
        try:
            kural = self._svc.birim_kural_getir(birim_id)
            self._inp_min_dinlenme.setText(str(kural.get("min_dinlenme_saat") or 12))
            self._inp_arefe.setText(str(kural.get("arefe_baslangic_saat") or "13:00"))
            self._inp_tolerans.setText(str(kural.get("tolerans_saat") or 7))
            self._inp_devreden.setText(str(kural.get("max_devreden_saat") or 12))
            self._inp_max_fazla.setText(str(kural.get("max_fazla_mesai_saat") or 0))
            self._chk_resmi.setChecked(bool(kural.get("resmi_tatil_calisma")))
            self._chk_dini.setChecked(bool(kural.get("dini_tatil_calisma")))
            self._chk_limit_override.setChecked(bool(kural.get("manuel_limit_asimina_izin")))

            self._birim_vardiya_listesini_yukle(birim_id)
            self._personel_liste_yenile()
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetPlanPage._kosul_birim_degisti", exc)
            self._alert.goster("Kosul verileri yuklenemedi.", "danger")

    def _sablon_listesini_yukle(self) -> None:
        if self._svc is None:
            return
        sablonlar = self._svc.sablon_listele()
        self._tbl_sablon.set_veri(sablonlar)
        self._cb_ata_sablon.blockSignals(True)
        self._cb_ata_sablon.clear()
        self._cb_ata_sablon.addItem("Sablon secin", "")
        for s in sablonlar:
            etiket = f"{str(s.get('ad') or '')} ({str(s.get('baslangic_saat') or '')}-{str(s.get('bitis_saat') or '')})"
            self._cb_ata_sablon.addItem(etiket, str(s.get("id") or ""))
        self._cb_ata_sablon.blockSignals(False)

    def _birim_vardiya_listesini_yukle(self, birim_id: str) -> None:
        if self._svc is None or not birim_id:
            self._tbl_slot.set_veri([])
            return
        rows = self._svc.vardiya_listele(birim_id)
        for r in rows:
            if not str(r.get("sablon_ad") or "").strip():
                r["sablon_ad"] = str(r.get("ad") or "")
        self._tbl_slot.set_veri(rows)

    def _sablon_ekle(self) -> None:
        self._alert.temizle()
        if self._svc is None:
            return
        try:
            self._svc.sablon_ekle(
                ad=self._inp_sablon_ad.text(),
                baslangic_saat=self._inp_sablon_bas.text(),
                bitis_saat=self._inp_sablon_bit.text(),
                saat_suresi=float(self._inp_sablon_sure.text() or 0),
            )
            self._inp_sablon_ad.clear()
            self._sablon_listesini_yukle()
            self._alert.goster("Sablon eklendi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetPlanPage._sablon_ekle", exc)
            self._alert.goster("Sablon eklenemedi.", "danger")

    def _sablon_pasife_al(self) -> None:
        self._alert.temizle()
        if self._svc is None:
            return
        row = self._tbl_sablon.secili_satir() or {}
        sid = str(row.get("id") or "").strip()
        if not sid:
            self._alert.goster("Pasife almak icin sablon seciniz.", "warning")
            return
        try:
            self._svc.sablon_pasife_al(sid)
            self._sablon_listesini_yukle()
            self._alert.goster("Sablon pasife alindi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetPlanPage._sablon_pasife_al", exc)
            self._alert.goster("Sablon pasife alinamadi.", "danger")

    def _sablon_birime_ata(self) -> None:
        self._alert.temizle()
        if self._svc is None:
            return
        birim_id = str(self._cb_kural_birim.currentData() or "").strip()
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
            exc_logla("NobetPlanPage._sablon_birime_ata", exc)
            self._alert.goster("Vardiya atanamadi.", "danger")

    def _birim_vardiya_kaldir(self) -> None:
        self._alert.temizle()
        if self._svc is None:
            return
        row = self._tbl_slot.secili_satir() or {}
        vid = str(row.get("id") or "").strip()
        if not vid:
            self._alert.goster("Kaldirmak icin birim vardiyasi seciniz.", "warning")
            return
        birim_id = str(self._cb_kural_birim.currentData() or "").strip()
        try:
            self._svc.vardiya_pasife_al(vid)
            self._birim_vardiya_listesini_yukle(birim_id)
            self._alert.goster("Birim vardiyasi kaldirildi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetPlanPage._birim_vardiya_kaldir", exc)
            self._alert.goster("Kaldirilirken hata olustu.", "danger")

    def _birim_kural_kaydet(self) -> None:
        self._alert.temizle()
        if self._svc is None:
            return
        birim_id = str(self._cb_kural_birim.currentData() or "").strip()
        try:
            self._svc.birim_kural_kaydet(
                birim_id,
                {
                    "min_dinlenme_saat": float(self._inp_min_dinlenme.text() or 12),
                    "resmi_tatil_calisma": self._chk_resmi.isChecked(),
                    "dini_tatil_calisma": self._chk_dini.isChecked(),
                    "arefe_baslangic_saat": self._inp_arefe.text(),
                    "max_fazla_mesai_saat": float(self._inp_max_fazla.text() or 0),
                    "tolerans_saat": float(self._inp_tolerans.text() or 7),
                    "max_devreden_saat": float(self._inp_devreden.text() or 12),
                    "manuel_limit_asimina_izin": self._chk_limit_override.isChecked(),
                },
            )
            self._alert.goster("Birim kurali kaydedildi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetPlanPage._birim_kural_kaydet", exc)
            self._alert.goster("Birim kurali kaydedilemedi.", "danger")

    def _personeli_esitle(self) -> None:
        self._alert.temizle()
        if self._svc is None:
            return
        birim_id = str(self._cb_kural_birim.currentData() or "").strip()
        try:
            adet = self._svc.birim_personellerini_esitle(birim_id)
            self._personel_liste_yenile()
            self._alert.goster(f"{adet} personel nobet listesine eklendi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetPlanPage._personeli_esitle", exc)
            self._alert.goster("Personel esitleme basarisiz.", "danger")

    def _personel_liste_yenile(self) -> None:
        birim_id = str(self._cb_kural_birim.currentData() or "").strip()
        rows = self._svc.birim_personel_kosullari_listele(birim_id)
        for r in rows:
            r["ad_soyad"] = f"{str(r.get('ad') or '').strip()} {str(r.get('soyad') or '').strip()}".strip()
            r["ister_24_txt"] = "E" if int(r.get("ister_24_saat") or 0) else "H"
            r["mesai_txt"] = "H" if int(r.get("mesai_istemiyor") or 0) else "E"
        self._tbl_personel.set_veri(rows)

    def _personel_secildi(self, _index) -> None:
        row = self._tbl_personel.secili_satir() or {}
        self._lbl_personel.setText(
            f"Secili: {str(row.get('ad') or '').strip()} {str(row.get('soyad') or '').strip()}"
        )
        self._chk_24.setChecked(bool(row.get("ister_24_saat")))
        self._chk_mesai.setChecked(bool(row.get("mesai_istemiyor")))
        self._inp_p_max_fazla.setText(str(row.get("max_fazla_mesai_saat") or 0))
        self._inp_p_tolerans.setText(str(row.get("tolerans_saat") or 7))
        self._inp_p_devreden.setText(str(row.get("max_devreden_saat") or 12))

    def _personel_kosul_kaydet(self) -> None:
        self._alert.temizle()
        if self._svc is None:
            return
        row = self._tbl_personel.secili_satir() or {}
        personel_id = str(row.get("personel_id") or "").strip()
        birim_id = str(self._cb_kural_birim.currentData() or "").strip()
        try:
            self._svc.personel_kosul_kaydet(
                birim_id,
                personel_id,
                {
                    "ister_24_saat": self._chk_24.isChecked(),
                    "mesai_istemiyor": self._chk_mesai.isChecked(),
                    "max_fazla_mesai_saat": float(self._inp_p_max_fazla.text() or 0),
                    "tolerans_saat": float(self._inp_p_tolerans.text() or 7),
                    "max_devreden_saat": float(self._inp_p_devreden.text() or 12),
                },
            )
            self._personel_liste_yenile()
            self._alert.goster("Personel kosulu kaydedildi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetPlanPage._personel_kosul_kaydet", exc)
            self._alert.goster("Personel kosulu kaydedilemedi.", "danger")

    def _plan_olustur(self) -> None:
        self._alert.temizle()
        if self._svc is None:
            return
        try:
            plan_id = self._svc.taslak_plan_olustur(
                birim_id=str(self._cb_birim.currentData() or "").strip(),
                yil=int(self._cb_yil.currentData() or 0),
                ay=int(self._cb_ay.currentData() or 0),
                notlar=self._inp_not.text(),
            )
            self.load_data()
            self._inp_not.clear()
            self._alert.goster(f"Taslak plan olusturuldu: {plan_id[:8]}", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetPlanPage._plan_olustur", exc)
            self._alert.goster("Plan olusturulurken beklenmeyen hata olustu.", "danger")
