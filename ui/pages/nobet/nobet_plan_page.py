# -*- coding: utf-8 -*-
"""ui/pages/nobet/nobet_plan_page.py - Nöbet koşulları ve plan hazırlık ekranı."""
from __future__ import annotations

from calendar import Calendar
from collections import defaultdict
from datetime import date
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.exceptions import AppHatasi
from app.logger import exc_logla
from app.services.nobet_service import NobetService
from ui.components import AlertBar, Card, DataTable, GhostButton, PrimaryButton
from ui.styles import T

_GUN = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]

# ── Hücre Renkleri ────────────────────────────────────────────────────────────
_BG_NORMAL   = ""  # T.bg1  — çalışma zamanında doldurulur
_BG_HAFTA    = ""  # T.bg2
_BG_TATIL    = "#2a1010"
_BOR_SECILI  = ""  # T.accent
_BOR_EKSIK   = "#e67e22"
_BOR_TATIL   = "#c0392b"
_BOR_NORMAL  = ""  # T.border


# ══════════════════════════════════════════════════════════════════════════════
#  Takvim hücresi — her gün için özel QFrame widget
# ══════════════════════════════════════════════════════════════════════════════

class _GunHucresi(QFrame):
    """Aylık takvim ızgarasındaki tek gün hücresi."""

    tiklandi = Signal(object)  # date gönderir

    def __init__(self, gun: date, parent=None):
        super().__init__(parent)
        self.gun = gun
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(2)

        # Başlık: gün numarası + adı
        ust = QFrame()
        ust_l = QHBoxLayout(ust)
        ust_l.setContentsMargins(0, 0, 0, 0)
        ust_l.setSpacing(4)
        self._lbl_gun = QLabel()
        self._lbl_gun.setStyleSheet("font-size:11px; font-weight:700;")
        self._badge_eksik = QLabel("!")
        self._badge_eksik.setVisible(False)
        self._badge_eksik.setStyleSheet(
            "font-size:9px; font-weight:700; color:white;"
            f"background:{_BOR_EKSIK}; padding:1px 4px; border-radius:6px;"
        )
        ust_l.addWidget(self._lbl_gun, 1)
        ust_l.addWidget(self._badge_eksik, 0, Qt.AlignmentFlag.AlignRight)
        lay.addWidget(ust)

        # Atama listesi
        self._icerik_w = QWidget()
        self._icerik_l = QVBoxLayout(self._icerik_w)
        self._icerik_l.setContentsMargins(0, 0, 0, 0)
        self._icerik_l.setSpacing(1)
        lay.addWidget(self._icerik_w, 1)

        self._guncelle_bos()

    # ------------------------------------------------------------------
    def guncelle(
        self,
        rows: list[dict],
        tatil: bool = False,
        haftasonu: bool = False,
        secili: bool = False,
        eksik: bool = False,
    ) -> None:
        """Hücreyi render eder. rows: plan_gunluk_vardiya_durumu çıktısı."""
        # Arka plan + kenarlık
        if secili:
            bg     = T.bg3
            border = f"2px solid {T.accent}"
        elif tatil:
            bg     = _BG_TATIL
            border = f"2px solid {_BOR_TATIL}"
        elif haftasonu:
            bg     = T.bg2
            border = f"1px solid {T.border}"
        else:
            bg     = T.bg1
            border = f"1px solid {T.border}"

        if eksik and not secili:
            border = f"2px solid {_BOR_EKSIK}"

        self._badge_eksik.setVisible(eksik)
        self.setStyleSheet(
            f"_GunHucresi {{ background:{bg}; border:{border}; border-radius:4px; }}"
        )

        # Başlık rengi
        gun_no = self.gun.day
        gun_ad = _GUN[self.gun.weekday()]
        if tatil:
            renk = _BOR_TATIL
        elif haftasonu:
            renk = T.accent
        else:
            renk = T.text2
        self._lbl_gun.setText(f"<span style='color:{renk}'>{gun_no} {gun_ad}</span>")

        # İçerik temizle
        while self._icerik_l.count():
            item = self._icerik_l.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Vardiya grupla → personel + boş slot
        vmap: dict[str, dict] = {}
        for r in rows:
            v = str(r.get("vardiya") or "-")
            if v not in vmap:
                vmap[v] = {"dolu": [], "bos": 0}
            if str(r.get("durum") or "") == "Dolu":
                p = str(r.get("personel") or "").strip()
                if p and p != "-":
                    vmap[v]["dolu"].append(p)
            else:
                vmap[v]["bos"] += 1

        shown = 0
        for vardiya, veri in vmap.items():
            if shown >= 6:
                lbl = QLabel("…")
                lbl.setStyleSheet(f"color:{T.text3}; font-size:9px;")
                self._icerik_l.addWidget(lbl)
                break
            for p in veri["dolu"]:
                lbl = QLabel(p)
                lbl.setStyleSheet(f"color:{T.text}; font-size:10px;")
                lbl.setWordWrap(True)
                self._icerik_l.addWidget(lbl)
                shown += 1
            if veri["bos"] > 0:
                lbl = QLabel(f"{vardiya}: BOS x{veri['bos']}")
                lbl.setStyleSheet(f"color:{_BOR_EKSIK}; font-size:9px; font-style:italic;")
                self._icerik_l.addWidget(lbl)
        self._icerik_l.addStretch()

    # ------------------------------------------------------------------
    def _guncelle_bos(self) -> None:
        self.setStyleSheet(
            f"_GunHucresi {{ background:{T.bg1}; border:1px solid {T.border}; border-radius:4px; }}"
        )
        gun_no = self.gun.day
        gun_ad = _GUN[self.gun.weekday()]
        self._lbl_gun.setText(f"<span style='color:{T.text3}'>{gun_no} {gun_ad}</span>")

    def mousePressEvent(self, e):
        self.tiklandi.emit(self.gun)
        super().mousePressEvent(e)


class _BosHucre(QFrame):
    """Ayın başı/sonu için şeffaf dolgu hücresi."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet("_BosHucre { background: transparent; border: none; }")



# ══════════════════════════════════════════════════════════════════════════════
#  Ana Sayfa
# ══════════════════════════════════════════════════════════════════════════════

class NobetPlanPage(QWidget):
    """Nöbet planı: koşul yönetimi + takvim görünümü + manuel atama."""

    def __init__(self, db=None, oturum: dict | None = None, parent=None):
        super().__init__(parent)
        self._db  = db
        self._oturum = oturum
        self._svc = NobetService(db) if db is not None else None
        self._secili_plan_id:   str | None  = None
        self._secili_plan_meta: dict | None = None
        self._secili_gun:       Optional[date] = None
        self._hucreler:   dict[str, _GunHucresi] = {}
        self._gunluk_map: dict[str, list[dict]]   = {}
        self._tatil_set:  set[str]                = set()

        self.setStyleSheet(f"background:{T.bg0};")
        self._build()
        self.load_data()

    # ── Genel yapı ────────────────────────────────────────────────────────────

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(10)

        self._alert = AlertBar(self)
        lay.addWidget(self._alert)

        hdr = QHBoxLayout()
        header = QLabel("Nöbet Koşulları ve Plan Hazırlık")
        header.setStyleSheet(f"color:{T.text}; font-size:17px; font-weight:700;")
        hdr.addWidget(header, 1)
        lay.addLayout(hdr)

        tabs = QTabWidget(self)
        tabs.addTab(self._kosul_sekmesi(), "Koşullar")
        tabs.addTab(self._plan_sekmesi(), "Plan")
        lay.addWidget(tabs, 1)

    # ── Koşullar sekmesi ──────────────────────────────────────────────────────

    def _kosul_sekmesi(self) -> QWidget:
        w = QWidget(self)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)
        lay.addWidget(self._personel_kural_karti(), 1)
        return w

    # ── Plan sekmesi — 3 panelli layout ───────────────────────────────────────

    def _plan_sekmesi(self) -> QWidget:
        w = QWidget(self)
        root = QVBoxLayout(w)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        # Üst toolbar: birim/yıl/ay + oluşturma butonları
        root.addWidget(self._plan_toolbar())

        # Plan listesi (kompakt)
        self._tbl = DataTable(self)
        self._tbl.kur_kolonlar(
            [
                ("birim_ad", "Birim", 220),
                ("donem", "Dönem", 90),
                ("durum_txt", "Durum", 80),
                ("satir_sayisi", "Satır", 60),
                ("olusturuldu", "Oluşturuldu", 110),
            ],
            geren="birim_ad",
        )
        self._tbl.setMaximumHeight(150)
        self._tbl.clicked.connect(self._satir_secildi)
        root.addWidget(self._tbl)

        self._lbl_ozet = QLabel("")
        self._lbl_ozet.setStyleSheet(f"color:{T.text3}; font-size:11px;")
        root.addWidget(self._lbl_ozet)

        # Eksik atama (başlangıçta gizli)
        self._tbl_eksik = DataTable(self)
        self._tbl_eksik.kur_kolonlar(
            [
                ("tarih", "Tarih", 100),
                ("vardiya", "Vardiya", 130),
                ("neden_txt", "Neden", 160),
            ],
            geren="neden_txt",
        )
        self._tbl_eksik.setMaximumHeight(0)
        root.addWidget(self._tbl_eksik)

        # Alt alan: sol panel | takvim ızgara | sağ panel
        alt = QHBoxLayout()
        alt.setContentsMargins(0, 0, 0, 0)
        alt.setSpacing(0)
        alt.addWidget(self._sol_panel_olustur(), 0)
        alt.addWidget(self._takvim_alani_olustur(), 1)
        self._sag_panel_w = self._sag_panel_olustur()
        self._sag_panel_w.setVisible(False)
        alt.addWidget(self._sag_panel_w, 0)
        root.addLayout(alt, 1)

        return w

    # ── Plan toolbar ──────────────────────────────────────────────────────────

    def _plan_toolbar(self) -> QFrame:
        bar = QFrame(self)
        bar.setProperty("bg-role", "panel")
        bar.setStyleSheet(
            f"background:{T.bg2}; border-radius:{T.radius_sm}px;"
            f"border:1px solid {T.border};"
        )
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 8, 12, 8)
        lay.setSpacing(8)

        lay.addWidget(self._etiket("Birim"))
        self._cb_birim = QComboBox(self)
        self._cb_birim.setMinimumHeight(30)
        self._cb_birim.setMinimumWidth(180)
        lay.addWidget(self._cb_birim)

        lay.addWidget(self._etiket("Yıl"))
        self._cb_yil = QComboBox(self)
        self._cb_yil.setMinimumHeight(30)
        for y in range(2025, 2036):
            self._cb_yil.addItem(str(y), y)
        lay.addWidget(self._cb_yil)

        lay.addWidget(self._etiket("Ay"))
        self._cb_ay = QComboBox(self)
        self._cb_ay.setMinimumHeight(30)
        for m in range(1, 13):
            self._cb_ay.addItem(f"{m:02d}", m)
        lay.addWidget(self._cb_ay)

        self._inp_not = QLineEdit(self)
        self._inp_not.setPlaceholderText("Not (isteğe bağlı)")
        self._inp_not.setMinimumHeight(30)
        lay.addWidget(self._inp_not, 1)

        lay.addStretch()

        self._btn_esitle = GhostButton("Birimleri Eşleştir")
        self._btn_esitle.clicked.connect(self._birimleri_esitle)
        lay.addWidget(self._btn_esitle)

        self._btn_olustur = GhostButton("Sadece Taslak Oluştur")
        self._btn_olustur.clicked.connect(self._plan_olustur)
        lay.addWidget(self._btn_olustur)

        self._btn_otomatik = PrimaryButton("Otomatik Plan Oluştur")
        self._btn_otomatik.clicked.connect(self._plan_olustur_ve_doldur)
        lay.addWidget(self._btn_otomatik)

        self._btn_yenile = GhostButton("Yenile")
        self._btn_yenile.clicked.connect(self.load_data)
        lay.addWidget(self._btn_yenile)

        return bar

    # ── Sol panel: personel dağılımı ──────────────────────────────────────────

    def _sol_panel_olustur(self) -> QFrame:
        p = QFrame(self)
        p.setFixedWidth(210)
        p.setStyleSheet(
            f"background:{T.bg1}; border-right:1px solid {T.border};"
        )
        lay = QVBoxLayout(p)
        lay.setContentsMargins(12, 14, 12, 14)
        lay.setSpacing(8)

        lbl = QLabel("Personel Dağılımı")
        lbl.setStyleSheet(f"color:{T.text}; font-size:12px; font-weight:700;")
        lay.addWidget(lbl)

        self._lbl_sol_ozet = QLabel("Plan seçilmedi")
        self._lbl_sol_ozet.setStyleSheet(f"color:{T.text3}; font-size:10px;")
        self._lbl_sol_ozet.setWordWrap(True)
        lay.addWidget(self._lbl_sol_ozet)

        sep = QWidget(); sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{T.border};")
        lay.addWidget(sep)

        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setFrameShape(QFrame.Shape.NoFrame)
        self._sol_w = QWidget()
        self._sol_l = QVBoxLayout(self._sol_w)
        self._sol_l.setContentsMargins(0, 0, 0, 0)
        self._sol_l.setSpacing(4)
        sc.setWidget(self._sol_w)
        lay.addWidget(sc, 1)
        return p

    # ── Takvim alanı: başlık + ızgara ─────────────────────────────────────────

    def _takvim_alani_olustur(self) -> QWidget:
        w = QWidget(self)
        wl = QVBoxLayout(w)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(0)

        # Gün başlıkları
        hdr = QFrame()
        hdr.setFixedHeight(30)
        hdr.setStyleSheet(
            f"background:{T.bg3}; border-bottom:1px solid {T.border};"
        )
        hl = QGridLayout(hdr)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(0)
        for i, g in enumerate(_GUN):
            lbl = QLabel(g)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            renk = T.accent if i >= 5 else T.text2
            lbl.setStyleSheet(f"color:{renk}; font-size:11px; font-weight:700;")
            hl.addWidget(lbl, 0, i)
            hl.setColumnStretch(i, 1)
        wl.addWidget(hdr)

        # Kaydırılabilir takvim ızgarası
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setFrameShape(QFrame.Shape.NoFrame)
        self._tw = QWidget()
        self._tl = QGridLayout(self._tw)
        self._tl.setContentsMargins(0, 0, 0, 0)
        self._tl.setSpacing(1)
        for c in range(7):
            self._tl.setColumnStretch(c, 1)
        sc.setWidget(self._tw)
        wl.addWidget(sc, 1)
        return w

    # ── Sağ panel: manuel atama (slide-in) ────────────────────────────────────

    def _sag_panel_olustur(self) -> QFrame:
        p = QFrame(self)
        p.setFixedWidth(280)
        p.setStyleSheet(
            f"background:{T.bg1}; border-left:1px solid {T.border};"
        )
        lay = QVBoxLayout(p)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        # Başlık + kapat
        hdr = QHBoxLayout()
        lbl_hdr = QLabel("Manuel Atama")
        lbl_hdr.setStyleSheet(f"color:{T.text}; font-size:13px; font-weight:700;")
        hdr.addWidget(lbl_hdr, 1)
        btn_kapat = GhostButton("✕")
        btn_kapat.setFixedSize(26, 26)
        btn_kapat.clicked.connect(lambda: self._sag_panel_w.setVisible(False))
        hdr.addWidget(btn_kapat)
        lay.addLayout(hdr)

        self._lbl_secili_gun = QLabel("Gün seçiniz")
        self._lbl_secili_gun.setStyleSheet(f"color:{T.text2}; font-size:11px;")
        lay.addWidget(self._lbl_secili_gun)

        sep = QWidget(); sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{T.border};")
        lay.addWidget(sep)

        lay.addWidget(self._etiket("Personel"))
        self._cb_manuel_personel = QComboBox(self)
        self._cb_manuel_personel.setMinimumHeight(32)
        lay.addWidget(self._cb_manuel_personel)

        lay.addWidget(self._etiket("Vardiya"))
        self._cb_manuel_vardiya = QComboBox(self)
        self._cb_manuel_vardiya.setMinimumHeight(32)
        lay.addWidget(self._cb_manuel_vardiya)

        lay.addWidget(self._etiket("Tarih (YYYY-AA-GG)"))
        self._inp_manuel_tarih = QLineEdit(self)
        self._inp_manuel_tarih.setPlaceholderText("2026-05-01")
        self._inp_manuel_tarih.setMinimumHeight(32)
        lay.addWidget(self._inp_manuel_tarih)

        self._btn_manuel_ekle = PrimaryButton("Atama Kaydet")
        self._btn_manuel_ekle.clicked.connect(self._manuel_atama_kaydet)
        lay.addWidget(self._btn_manuel_ekle)

        lay.addStretch(1)
        return p

    # ── Koşullar kart ─────────────────────────────────────────────────────────

    def _personel_kural_karti(self) -> Card:
        kart = Card(self)
        kl = kart.layout_

        title = QLabel("Personel Nobet Kosullari")
        title.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        kl.addWidget(title)

        frm = QGridLayout()
        frm.setHorizontalSpacing(8)
        frm.setVerticalSpacing(8)
        frm.addWidget(self._etiket("Birim"), 0, 0)
        self._cb_kural_birim = QComboBox(self)
        self._cb_kural_birim.setMinimumHeight(32)
        self._cb_kural_birim.currentIndexChanged.connect(self._kosul_birim_degisti)
        frm.addWidget(self._cb_kural_birim, 1, 0)
        kl.addLayout(frm)

        self._tbl_personel = DataTable(self)
        self._tbl_personel.kur_kolonlar(
            [
                ("ad_soyad", "Personel", 200),
                ("ister_24_txt", "24s", 50),
                ("mesai_txt", "Mesai", 60),
                ("max_fazla_mesai_saat", "Max FM", 70),
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

        pf.addWidget(self._etiket("Max Devreden Saat"), 2, 1)
        self._inp_p_devreden = QLineEdit(self)
        self._inp_p_devreden.setMinimumHeight(32)
        self._inp_p_devreden.setText("12")
        pf.addWidget(self._inp_p_devreden, 3, 1)
        kl.addLayout(pf)

        self._btn_personel_kaydet = PrimaryButton("Secili Personel Kosulunu Kaydet")
        self._btn_personel_kaydet.clicked.connect(self._personel_kosul_kaydet)
        kl.addWidget(self._btn_personel_kaydet)

        self._lbl_personel = QLabel("Personel seciniz")
        self._lbl_personel.setStyleSheet(f"color:{T.text3}; font-size:11px;")
        kl.addWidget(self._lbl_personel)
        return kart

    # ── Yardımcı widget üreticiler ────────────────────────────────────────────
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
            self._lbl_ozet.setText("Veritabanı bağlantısı bulunamadı.")
            return

        try:
            birimler = self._svc.birimler_listele(aktif_only=True)
            self._cb_birim.blockSignals(True)
            self._cb_kural_birim.blockSignals(True)
            self._cb_birim.clear()
            self._cb_kural_birim.clear()
            self._cb_birim.addItem("Birim seçin", "")
            self._cb_kural_birim.addItem("Birim seçin", "")
            for b in birimler:
                self._cb_birim.addItem(str(b.get("ad") or ""), str(b.get("id") or ""))
                self._cb_kural_birim.addItem(str(b.get("ad") or ""), str(b.get("id") or ""))
            self._cb_birim.blockSignals(False)
            self._cb_kural_birim.blockSignals(False)

            plans = self._svc.planlari_listele()
            for p in plans:
                p["donem"] = f"{int(p.get('yil') or 0)}-{int(p.get('ay') or 0):02d}"
                p["durum_txt"] = str(p.get("durum") or "").title()
            self._tbl.set_veri(plans)
            self._tbl_eksik.setMaximumHeight(0)
            self._lbl_ozet.setText(
                f"Aktif birim: {len(birimler)}  |  Plan sayısı: {len(plans)}"
            )
            self._set_varsayilan_donem()
            self._kosul_birim_degisti()
        except Exception as exc:
            exc_logla("NobetPlanPage.load_data", exc)
            self._tbl.set_veri([])
            self._lbl_ozet.setText("Nöbet verileri yüklenemedi.")
            self._alert.goster(str(exc), "danger")

    # ── Takvim çizimi ─────────────────────────────────────────────────────────

    def _takvim_ciz(self, plan: dict | None = None) -> None:
        """Seçili plana göre aylık takvim ızgarasını çizer."""
        secili    = plan or self._secili_plan_meta or {}
        birim_id  = str(secili.get("birim_id") or "").strip()
        yil       = int(secili.get("yil") or 0)
        ay        = int(secili.get("ay") or 0)

        # Izgarayı temizle
        while self._tl.count():
            item = self._tl.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._hucreler.clear()

        if not birim_id or yil < 2000 or ay < 1 or ay > 12:
            self._sol_panel_guncelle()
            return

        # Günlük veri haritası
        plan_id = str(secili.get("id") or self._secili_plan_id or "").strip()
        self._gunluk_map = {}
        if plan_id and self._svc:
            try:
                rows = self._svc.plan_gunluk_vardiya_durumu(plan_id, birim_id, yil, ay)
                for r in rows:
                    t = str(r.get("tarih") or "")
                    self._gunluk_map.setdefault(t, []).append(r)
            except Exception as exc:
                exc_logla("NobetPlanPage._takvim_ciz veri", exc)

        # Tatil seti
        self._tatil_set = set()
        if self._svc:
            try:
                from calendar import monthrange as _mr
                gun_sayisi = _mr(yil, ay)[1]
                tatil_rows = self._svc.tatil_aralik_listele(
                    date(yil, ay, 1).isoformat(),
                    date(yil, ay, gun_sayisi).isoformat(),
                )
                for t in tatil_rows:
                    turu = str(t.get("tur") or "").strip()
                    if turu in ("resmi", "dini"):
                        self._tatil_set.add(str(t.get("tarih") or ""))
            except Exception:
                pass

        # Hücreleri yerleştir
        cal     = Calendar(firstweekday=0)
        haftalar = cal.monthdayscalendar(yil, ay)
        for satir_no, hafta in enumerate(haftalar):
            for sutun_no, gun_no in enumerate(hafta):
                if gun_no == 0:
                    w = _BosHucre(self._tw)
                else:
                    try:
                        gun_obj = date(yil, ay, gun_no)
                    except ValueError:
                        w = _BosHucre(self._tw)
                        self._tl.addWidget(w, satir_no, sutun_no)
                        continue
                    tarih_str = gun_obj.isoformat()
                    hucre = _GunHucresi(gun_obj, self._tw)
                    hucre.tiklandi.connect(self._gun_tiklandi)
                    gun_rows  = self._gunluk_map.get(tarih_str, [])
                    tatil     = tarih_str in self._tatil_set
                    haftasonu = sutun_no >= 5
                    eksik     = any(str(r.get("durum") or "") == "Bos" for r in gun_rows)
                    hucre.guncelle(gun_rows, tatil=tatil, haftasonu=haftasonu, eksik=eksik)
                    self._hucreler[tarih_str] = hucre
                    w = hucre
                self._tl.addWidget(w, satir_no, sutun_no)

        self._sol_panel_guncelle()

    # ── Sol panel güncelleme ──────────────────────────────────────────────────

    def _sol_panel_guncelle(self) -> None:
        while self._sol_l.count():
            item = self._sol_l.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._gunluk_map:
            self._lbl_sol_ozet.setText("Plan seçilmedi")
            return

        sayac: dict[str, int] = defaultdict(int)
        for rows in self._gunluk_map.values():
            for r in rows:
                if str(r.get("durum") or "") == "Dolu":
                    p = str(r.get("personel") or "").strip()
                    if p and p != "-":
                        sayac[p] += 1

        toplam = sum(sayac.values())
        self._lbl_sol_ozet.setText(
            f"{toplam} atama  |  {len(sayac)} personel"
        )

        for ad_soyad, sayi in sorted(sayac.items()):
            satir = QFrame()
            satir.setStyleSheet(
                f"background:{T.bg2}; border-radius:4px; border:1px solid {T.border};"
            )
            sl = QHBoxLayout(satir)
            sl.setContentsMargins(6, 4, 6, 4)
            lbl_ad = QLabel(ad_soyad)
            lbl_ad.setStyleSheet(f"color:{T.text}; font-size:11px;")
            lbl_ad.setWordWrap(True)
            lbl_sayi = QLabel(f"{sayi} gün")
            lbl_sayi.setStyleSheet(
                f"color:{T.accent}; font-size:11px; font-weight:700;"
            )
            lbl_sayi.setFixedWidth(46)
            sl.addWidget(lbl_ad, 1)
            sl.addWidget(lbl_sayi)
            self._sol_l.addWidget(satir)
        self._sol_l.addStretch()

    # ── Gün tıklama ───────────────────────────────────────────────────────────

    def _gun_tiklandi(self, gun: date) -> None:
        self._secili_gun = gun
        tarih_str = gun.isoformat()

        # Tüm hücreleri yeniden render et (seçili/değil)
        for t, h in self._hucreler.items():
            gun_rows  = self._gunluk_map.get(t, [])
            tatil     = t in self._tatil_set
            haftasonu = h.gun.weekday() >= 5
            eksik     = any(str(r.get("durum") or "") == "Bos" for r in gun_rows)
            h.guncelle(
                gun_rows,
                tatil=tatil,
                haftasonu=haftasonu,
                secili=(t == tarih_str),
                eksik=eksik,
            )

        # Sağ paneli aç
        self._lbl_secili_gun.setText(f"Seçili gün: {tarih_str}")
        self._inp_manuel_tarih.setText(tarih_str)
        self._sag_panel_w.setVisible(True)

    # ── Plan seçimi ───────────────────────────────────────────────────────────

    def _satir_secildi(self, _index) -> None:
        row = self._tbl.secili_satir()
        self._secili_plan_id   = str((row or {}).get("id") or "") or None
        self._secili_plan_meta = row or None
        self._takvim_ciz()
        self._manuel_form_doldur()

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
            self._tbl_personel.set_veri([])
            return
        try:
            self._personel_liste_yenile()
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetPlanPage._kosul_birim_degisti", exc)
            self._alert.goster("Kosul verileri yuklenemedi.", "danger")

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
            self._secili_plan_id = plan_id
            self._secili_plan_meta = {
                "id": plan_id,
                "birim_id": str(self._cb_birim.currentData() or "").strip(),
                "yil": int(self._cb_yil.currentData() or 0),
                "ay": int(self._cb_ay.currentData() or 0),
            }
            self._takvim_ciz(self._secili_plan_meta)
            self._manuel_form_doldur()
            self._inp_not.clear()
            self._alert.goster(f"Taslak plan olusturuldu: {plan_id[:8]}", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetPlanPage._plan_olustur", exc)
            self._alert.goster("Plan olusturulurken beklenmeyen hata olustu.", "danger")

    @staticmethod
    def _eksik_neden_text(neden: str) -> str:
        harita = {
            "uygun_aday_yok": "Uygun aday yok",
            "min_dinlenme": "Min dinlenme",
            "ardisik_limit": "Ardisik limit",
            "vardiya_suresi_sifir": "Vardiya suresi 0",
        }
        anahtar = str(neden or "").strip()
        return harita.get(anahtar, anahtar or "-")

    def _plan_olustur_ve_doldur(self) -> None:
        self._alert.temizle()
        if self._svc is None:
            return
        birim_id = str(self._cb_birim.currentData() or "").strip()
        yil = int(self._cb_yil.currentData() or 0)
        ay = int(self._cb_ay.currentData() or 0)
        try:
            sonuc = self._svc.taslak_plan_olustur_ve_doldur(
                birim_id=birim_id,
                yil=yil,
                ay=ay,
                notlar=self._inp_not.text(),
            )
            eksikler = list(sonuc.get("eksik_atama") or [])
            vardiya_map = {
                str(v.get("id") or "").strip(): str(v.get("ad") or "").strip()
                for v in self._svc.vardiya_listele(birim_id, aktif_only=True)
            }
            for e in eksikler:
                vid = str(e.get("vardiya_id") or "").strip()
                e["vardiya"] = vardiya_map.get(vid, vid)
                e["neden_txt"] = self._eksik_neden_text(str(e.get("neden") or ""))

            if eksikler:
                self._tbl_eksik.set_veri(eksikler)
                self._tbl_eksik.setMaximumHeight(200)
            else:
                self._tbl_eksik.set_veri([])
                self._tbl_eksik.setMaximumHeight(0)

            self.load_data()
            self._secili_plan_id = str(sonuc.get("plan_id") or "")
            self._secili_plan_meta = {
                "id": self._secili_plan_id,
                "birim_id": birim_id,
                "yil": yil,
                "ay": ay,
            }
            self._takvim_ciz(self._secili_plan_meta)
            self._manuel_form_doldur()
            self._inp_not.clear()
            self._alert.goster(
                f"Plan dolduruldu. Satir: {int(sonuc.get('satir_sayisi') or 0)} | Eksik: {len(eksikler)}",
                "success",
            )
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetPlanPage._plan_olustur_ve_doldur", exc)
            self._alert.goster("Otomatik plan doldurma sirasinda hata olustu.", "danger")

    def _manuel_form_doldur(self) -> None:
        secili = self._secili_plan_meta or {}
        birim_id = str(secili.get("birim_id") or "").strip()
        self._cb_manuel_personel.clear()
        self._cb_manuel_vardiya.clear()
        if not birim_id or self._svc is None:
            return
        for p in self._svc.birim_personel_kosullari_listele(birim_id):
            ad = str(p.get("ad") or "").strip()
            soyad = str(p.get("soyad") or "").strip()
            self._cb_manuel_personel.addItem(f"{ad} {soyad}".strip(), str(p.get("personel_id") or ""))
        for v in self._svc.vardiya_listele(birim_id, aktif_only=True):
            self._cb_manuel_vardiya.addItem(str(v.get("ad") or ""), str(v.get("id") or ""))

    def _manuel_atama_kaydet(self) -> None:
        self._alert.temizle()
        if self._svc is None or not self._secili_plan_id:
            self._alert.goster("Once bir plan secin.", "warning")
            return
        personel_id = str(self._cb_manuel_personel.currentData() or "").strip()
        vardiya_id = str(self._cb_manuel_vardiya.currentData() or "").strip()
        tarih = self._inp_manuel_tarih.text().strip()
        try:
            self._svc.plan_satir_manuel_ekle(self._secili_plan_id, personel_id, vardiya_id, tarih)
            self._takvim_ciz()
            self._alert.goster("Atama kaydedildi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("NobetPlanPage._manuel_atama_kaydet", exc)
            self._alert.goster("Atama kaydedilemedi.", "danger")
