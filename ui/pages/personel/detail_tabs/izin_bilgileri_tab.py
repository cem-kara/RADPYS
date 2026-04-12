# -*- coding: utf-8 -*-
"""Personel detay penceresi icin izin bilgileri sekmesi."""
from __future__ import annotations

from datetime import date

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.config import YILLIK_MAX_DEVIR
from app.services.izin_service import IzinService
from app.text_utils import turkish_lower
from app.validators import format_tarih
from ui.components import AsyncRunner, DataTable
from ui.styles import T


class PersonelIzinBilgileriTab(QWidget):
    """Personelin izin ozetini ve gecmis izin hareketlerini gosterir."""

    @staticmethod
    def _izin_turu_norm(tur: str) -> str:
        text = turkish_lower(str(tur or "")).strip()
        return (
            text.replace("ü", "u")
            .replace("ı", "i")
            .replace("ş", "s")
            .replace("ğ", "g")
            .replace("ö", "o")
            .replace("ç", "c")
        )

    def __init__(
        self,
        db,
        personel_id_getter,
        memuriyet_baslama_getter,
        alert_callback=None,
        parent=None,
    ):
        super().__init__(parent)
        self._svc = IzinService(db)
        self._personel_id_getter = personel_id_getter
        self._memuriyet_baslama_getter = memuriyet_baslama_getter
        self._alert_callback = alert_callback
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        self._card_yillik = self._make_card("Yillik Izin Durumu")
        self._card_sua = self._make_card("Sua ve Diger Izinler")
        top_row.addWidget(self._card_yillik, 1)
        top_row.addWidget(self._card_sua, 1)
        root.addLayout(top_row)

        self._lbl_devreden = self._add_stat(self._card_yillik, "Devir Eden Izin")
        self._lbl_hak = self._add_stat(self._card_yillik, "Bu Yil Hak Edilen")
        self._lbl_toplam = self._add_stat(self._card_yillik, "Toplam Izin Hakki")
        self._lbl_kull_yillik = self._add_stat(self._card_yillik, "Kullanilan Yillik Izin")
        self._lbl_kalan = self._add_stat(self._card_yillik, "Kalan Yillik Izin")
        self._lbl_kull_diger = self._add_stat(self._card_yillik, "Kullanilan Diger Izinler")
        self._lbl_iptal = self._add_stat(self._card_yillik, "Iptal Edilen Izinler")

        self._lbl_sua_hak = self._add_stat(self._card_sua, "Hak Edilen Sua Izin")
        self._lbl_sua_kull = self._add_stat(self._card_sua, "Kullanilan Sua Izinleri")
        self._lbl_sua_kalan = self._add_stat(self._card_sua, "Kalan Sua Izni")
        self._lbl_sua_cari = self._add_stat(self._card_sua, "Cari Yil Sua Kazanim")

        gecmis = QFrame(self)
        gecmis.setStyleSheet(
            f"QFrame{{background:{T.bg1};border:1px solid {T.border};border-radius:{T.radius}px;}}"
        )
        gecmis_lay = QVBoxLayout(gecmis)
        gecmis_lay.setContentsMargins(10, 10, 10, 10)
        gecmis_lay.setSpacing(6)

        title = QLabel("Gecmis Izin Hareketleri")
        title.setStyleSheet(f"color:{T.accent2};font-size:12px;font-weight:700;")
        gecmis_lay.addWidget(title)

        self._tablo = DataTable(gecmis)
        self._tablo.kur_kolonlar(
            [
                ("tur", "Izin Turu", 130),
                ("baslama_ui", "Baslangic", 100),
                ("bitis_ui", "Bitis", 100),
                ("gun", "Gun", 70),
                ("durum", "Durum", 80),
                ("aciklama", "Aciklama", 200),
            ],
            geren="aciklama",
        )
        gecmis_lay.addWidget(self._tablo, 1)
        root.addWidget(gecmis, 1)

    def _make_card(self, title: str) -> QFrame:
        card = QFrame(self)
        card.setStyleSheet(
            f"QFrame{{background:{T.bg1};border:1px solid {T.border};border-radius:{T.radius}px;}}"
        )
        lay = QVBoxLayout(card)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(4)

        lbl = QLabel(title)
        lbl.setStyleSheet(
            f"color:{T.accent2};font-size:12px;font-weight:700;"
            f"background:{T.overlay_low};padding:2px 8px;border-radius:8px;"
        )
        lay.addWidget(lbl)
        return card

    def _add_stat(self, card: QFrame, label: str) -> QLabel:
        lay = card.layout()
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        key = QLabel(label)
        key.setStyleSheet(f"color:{T.text3};font-size:11px;")
        val = QLabel("0.0")
        val.setStyleSheet(f"color:{T.text};font-size:11px;font-weight:600;")

        row.addWidget(key)
        row.addStretch()
        row.addWidget(val)
        lay.addLayout(row)

        sep = QFrame(card)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{T.border};")
        lay.addWidget(sep)
        return val

    def yenile(self) -> None:
        personel_id = str(self._personel_id_getter() or "").strip()
        if not personel_id:
            self._tablo.set_veri([])
            self._set_zero_values()
            return

        AsyncRunner(
            fn=lambda: self._svc.listele(personel_id=personel_id),
            on_done=self._load_done,
            on_error=self._load_error,
            parent=self,
        ).start()

    def _load_done(self, rows: list[dict]) -> None:
        yil = date.today().year
        aktif_rows = [r for r in rows if str(r.get("durum") or "") == "aktif"]
        iptal_rows = [r for r in rows if str(r.get("durum") or "") == "iptal"]

        bu_yil_hak = float(self._svc.yillik_hak_hesapla(self._memuriyet_baslama_getter()))
        onceki_hak = float(self._svc.yillik_hak_hesapla(self._memuriyet_baslama_getter(), date(yil - 1, 12, 31)))

        kull_onceki = sum(
            int(r.get("gun") or 0)
            for r in aktif_rows
            if self._izin_turu_norm(r.get("tur")) == "yillik izin"
            and str(r.get("baslama") or "").startswith(str(yil - 1))
        )
        kull_bu_yil = sum(
            int(r.get("gun") or 0)
            for r in aktif_rows
            if self._izin_turu_norm(r.get("tur")) == "yillik izin"
            and str(r.get("baslama") or "").startswith(str(yil))
        )
        kull_diger = sum(
            int(r.get("gun") or 0)
            for r in aktif_rows
            if self._izin_turu_norm(r.get("tur")) != "yillik izin"
        )
        iptal_toplam = sum(
            int(r.get("gun") or 0)
            for r in iptal_rows
            if str(r.get("baslama") or "").startswith(str(yil))
        )

        devreden_kaba = max(0.0, onceki_hak - float(kull_onceki))
        devreden_limit = bu_yil_hak * float(YILLIK_MAX_DEVIR)
        devreden = min(devreden_kaba, devreden_limit)

        toplam_hak = devreden + bu_yil_hak
        kalan = max(0.0, toplam_hak - float(kull_bu_yil))

        self._lbl_devreden.setText(f"{devreden:.1f}")
        self._lbl_hak.setText(f"{bu_yil_hak:.1f}")
        self._lbl_toplam.setText(f"{toplam_hak:.1f}")
        self._lbl_kull_yillik.setText(f"{float(kull_bu_yil):.1f}")
        self._lbl_kalan.setText(f"{kalan:.1f}")
        self._lbl_kull_diger.setText(f"{float(kull_diger):.1f}")
        self._lbl_iptal.setText(f"{float(iptal_toplam):.1f}")

        # Su an suaya dair kaynak alan yok; yer ayrik tutuldu.
        self._lbl_sua_hak.setText("0.0")
        self._lbl_sua_kull.setText("0.0")
        self._lbl_sua_kalan.setText("0.0")
        self._lbl_sua_cari.setText("0.0")

        tablo_rows = []
        for r in rows:
            tablo_rows.append(
                {
                    "tur": str(r.get("tur") or "").replace("_", " ").upper(),
                    "baslama_ui": format_tarih(r.get("baslama"), ui=True),
                    "bitis_ui": format_tarih(r.get("bitis"), ui=True),
                    "gun": int(r.get("gun") or 0),
                    "durum": "Iptal" if str(r.get("durum") or "") == "iptal" else "Aktif",
                    "aciklama": str(r.get("aciklama") or ""),
                }
            )
        self._tablo.set_veri(tablo_rows)

    def _load_error(self, mesaj: str) -> None:
        self._tablo.set_veri([])
        self._set_zero_values()
        if callable(self._alert_callback):
            self._alert_callback(mesaj)

    def _set_zero_values(self) -> None:
        for lbl in (
            self._lbl_devreden,
            self._lbl_hak,
            self._lbl_toplam,
            self._lbl_kull_yillik,
            self._lbl_kalan,
            self._lbl_kull_diger,
            self._lbl_iptal,
            self._lbl_sua_hak,
            self._lbl_sua_kull,
            self._lbl_sua_kalan,
            self._lbl_sua_cari,
        ):
            lbl.setText("0.0")
