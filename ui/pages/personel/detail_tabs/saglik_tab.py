# -*- coding: utf-8 -*-
"""Personel detayinda Saglik/Muayene bilgi + kayit giris sekmesi."""
from __future__ import annotations

import os
from collections import Counter
from datetime import date

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.logger import exc_logla
from app.services.dokuman_service import DokumanService
from app.services.saglik_service import SaglikService
from ui.components import AlertBar, DangerButton, GhostButton, PrimaryButton
from ui.styles import T


class PersonelSaglikTab(QWidget):
    """Personelin saglik sekmesi: ozet/liste (bilgi) + muayene giris/duzenle formu."""

    def __init__(self, db=None, personel_id_getter=None, parent=None):
        super().__init__(parent)
        self._db = db
        self._svc = SaglikService(db) if db is not None else None
        self._dokuman_svc = DokumanService(db) if db is not None else None
        self._personel_id_getter = personel_id_getter or (lambda: "")
        self._rows: list[dict] = []
        self._secili_yil_tercihi: int | None = None
        self._editing_id: str | None = None
        self._rapor_dosya_yolu = ""
        self._rapor_belge_id: str | None = None
        self._build()

    # ─────────────────────────── UI inşa ────────────────────────────

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)

        # Başlık + Yeni Muayene butonu
        self._alert = AlertBar(self)
        root.addWidget(self._alert)

        # İnline giriş formu (gizli başlar)
        self._form_frame = self._build_form()
        self._form_frame.setVisible(False)
        root.addWidget(self._form_frame)

        # Akış durum etiketi
        self._akis_lbl = QLabel("")
        self._akis_lbl.setStyleSheet(f"color:{T.text2};font-size:11px;")
        root.addWidget(self._akis_lbl)

        # Filtre + eylem satırı
        filtre_row = QHBoxLayout()
        filtre_row.setSpacing(8)

        lbl_yil = QLabel("Yil:")
        lbl_yil.setStyleSheet(f"color:{T.text2};font-size:11px;")
        self._cmb_yil = QComboBox(self)
        self._cmb_yil.currentIndexChanged.connect(self._on_yil_filtre)
        filtre_row.addWidget(lbl_yil)
        filtre_row.addWidget(self._cmb_yil)
        filtre_row.addStretch(1)

        self._btn_yeni = PrimaryButton("Yeni Muayene")
        self._btn_yeni.clicked.connect(self._ac_form_yeni)
        filtre_row.addWidget(self._btn_yeni)
        root.addLayout(filtre_row)

        # Özet kartlar
        ust = QHBoxLayout()
        ust.setSpacing(10)
        ust.addWidget(self._build_ozet_kart())
        ust.addWidget(self._build_durum_kart())
        ust.addStretch(1)
        root.addLayout(ust)

        # Kayıtlar tablosu
        self._table = QTableWidget(self)
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            ["Uzmanlik", "Muayene", "Sonraki", "Sonuc", "Durum", "Rapor"]
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.doubleClicked.connect(self._on_tablo_cift_tik)
        self._table.cellClicked.connect(self._hucre_tikla)
        root.addWidget(self._table, 1)

    def _build_form(self) -> QFrame:
        frm = QFrame(self)
        frm.setStyleSheet(
            f"QFrame{{background:{T.bg1};border:1px solid {T.accent};"
            f"border-radius:{T.radius}px;}}"
        )
        lay = QVBoxLayout(frm)
        lay.setContentsMargins(14, 10, 14, 12)
        lay.setSpacing(8)

        # Başlık satırı
        baslik_row = QHBoxLayout()
        self._frm_baslik = QLabel("Yeni Muayene")
        self._frm_baslik.setStyleSheet(
            f"color:{T.text};font-size:13px;font-weight:700;"
        )
        baslik_row.addWidget(self._frm_baslik)
        baslik_row.addStretch(1)
        btn_kapat = GhostButton("Kapat")
        btn_kapat.clicked.connect(self._kapat_form)
        baslik_row.addWidget(btn_kapat)
        lay.addLayout(baslik_row)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{T.border};")
        lay.addWidget(sep)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)

        def lbl(t: str) -> QLabel:
            w = QLabel(t)
            w.setStyleSheet(f"color:{T.text2};font-size:11px;font-weight:600;")
            return w

        # Uzmanlik
        self._u = QComboBox(self)
        grid.addWidget(lbl("Uzmanlik *"), 0, 0)
        grid.addWidget(self._u, 0, 1)

        # Muayene tarihi
        self._t = QDateEdit(self)
        self._t.setCalendarPopup(True)
        self._t.setDate(QDate.currentDate())
        self._t.dateChanged.connect(self._tarih_degisti)
        grid.addWidget(lbl("Muayene Tarihi *"), 0, 2)
        grid.addWidget(self._t, 0, 3)

        # Sonraki (readonly, otomatik)
        self._s = QDateEdit(self)
        self._s.setCalendarPopup(False)
        self._s.setEnabled(False)
        self._s.setDate(QDate.currentDate().addYears(1))
        grid.addWidget(lbl("Sonraki Kontrol"), 1, 0)
        grid.addWidget(self._s, 1, 1)

        # Sonuç
        self._sonuc = QComboBox(self)
        self._sonuc.addItem("", None)
        self._sonuc.addItems(["Uygun", "Takip", "Uygun Degil"])
        grid.addWidget(lbl("Sonuc"), 1, 2)
        grid.addWidget(self._sonuc, 1, 3)

        # Not
        self._not = QLineEdit(self)
        self._not.setPlaceholderText("Notlar...")
        grid.addWidget(lbl("Not"), 2, 0)
        self._not_label_col = 0
        grid.addWidget(self._not, 2, 1, 1, 3)

        lay.addLayout(grid)

        # Rapor satırı
        rapor_row = QHBoxLayout()
        rapor_row.setSpacing(8)
        self._rapor_lbl = QLabel("Rapor: Yuklenmedi")
        self._rapor_lbl.setStyleSheet(f"color:{T.text2};font-size:11px;")
        rapor_row.addWidget(self._rapor_lbl, 1)
        self._btn_rapor_sec = GhostButton("Rapor Formu Sec")
        self._btn_rapor_sec.clicked.connect(self._rapor_sec)
        rapor_row.addWidget(self._btn_rapor_sec)
        lay.addLayout(rapor_row)

        # Butonlar
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self._btn_sil = DangerButton("Kaydi Sil")
        self._btn_sil.clicked.connect(self._sil)
        self._btn_sil.setVisible(False)
        self._btn_kaydet = PrimaryButton("Kaydet")
        self._btn_kaydet.clicked.connect(self._kaydet)
        self._btn_iptal = DangerButton("Vazgec")
        self._btn_iptal.clicked.connect(self._kapat_form)
        btn_row.addWidget(self._btn_sil)
        btn_row.addWidget(self._btn_iptal)
        btn_row.addWidget(self._btn_kaydet)
        lay.addLayout(btn_row)

        return frm

    def _build_ozet_kart(self) -> QGroupBox:
        grp = QGroupBox("Muayene Ozeti", self)
        grp.setStyleSheet(
            f"QGroupBox{{border:1px solid {T.border};"
            f"border-radius:{T.radius}px;padding-top:12px;}}"
        )
        gl = QGridLayout(grp)
        gl.setContentsMargins(12, 10, 12, 10)
        gl.setHorizontalSpacing(10)
        gl.setVerticalSpacing(6)

        self._lbl_toplam = self._stat_satiri(gl, 0, "Toplam Kayit")
        self._lbl_yil = self._stat_satiri(gl, 1, "Secili Yil")
        self._lbl_son_muayene = self._stat_satiri(gl, 2, "Son Muayene")
        self._lbl_rapor = self._stat_satiri(gl, 3, "Raporlu")
        return grp

    def _build_durum_kart(self) -> QGroupBox:
        grp = QGroupBox("Durum Gosterge", self)
        grp.setStyleSheet(
            f"QGroupBox{{border:1px solid {T.border};"
            f"border-radius:{T.radius}px;padding-top:12px;}}"
        )
        gl = QGridLayout(grp)
        gl.setContentsMargins(12, 10, 12, 10)
        gl.setHorizontalSpacing(10)
        gl.setVerticalSpacing(6)

        self._lbl_gecerli = self._stat_satiri(gl, 0, "Gecerli")
        self._lbl_riskli = self._stat_satiri(gl, 1, "Riskli")
        self._lbl_gecikmis = self._stat_satiri(gl, 2, "Gecikmis")
        self._lbl_planli = self._stat_satiri(gl, 3, "Planlandi")
        return grp

    def _stat_satiri(self, grid: QGridLayout, row: int, etiket: str) -> QLabel:
        k = QLabel(etiket)
        k.setStyleSheet(f"color:{T.text2};font-size:11px;")
        v = QLabel("-")
        v.setStyleSheet(f"color:{T.text};font-size:12px;font-weight:700;")
        v.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(k, row, 0)
        grid.addWidget(v, row, 1)
        return v

    # ─────────────────────────── Form yardımcıları ──────────────────

    def _secili_yil_form(self) -> int:
        return int(self._t.date().year())

    def _tarih_degisti(self) -> None:
        self._s.setDate(self._t.date().addYears(1))
        self._guncelle_akis_ve_uzmanlik()

    def _guncelle_akis_ve_uzmanlik(self) -> None:
        if self._svc is None:
            return
        pid = str(self._personel_id_getter() or "").strip()
        if not pid:
            return

        yil = self._secili_yil_form()
        durum = self._svc.personel_yil_uzmanlik_durumu(pid, yil)
        eksik = list(durum.get("eksik") or [])
        tamam = list(durum.get("tamamlanan") or [])

        self._akis_lbl.setText(
            f"{yil}: Tamamlanan {len(tamam)}/3"
            f" ({', '.join(tamam) if tamam else '-'})  |  "
            f"Eksik: {', '.join(eksik) if eksik else 'Yok'}"
        )

        rapor = self._svc.personel_yil_tek_rapor(pid, yil)
        self._rapor_belge_id = str(rapor.get("belge_id") or "").strip() if rapor else None
        if rapor:
            self._rapor_lbl.setText(f"Rapor: {str(rapor.get('dosya_adi') or '-')}")
            self._btn_rapor_sec.setText("Raporu Degistir")
        else:
            self._rapor_lbl.setText("Rapor: Yuklenmedi")
            self._btn_rapor_sec.setText("Rapor Formu Sec")

        if self._editing_id:
            return

        # Düzenleme dışında sadece eksik uzmanlıkları göster
        self._u.blockSignals(True)
        self._u.clear()
        secenekler = eksik or list(durum.get("zorunlu") or [])
        for uz in secenekler:
            self._u.addItem(str(uz))
        self._u.blockSignals(False)
        self._u.setEnabled(bool(secenekler))
        self._btn_kaydet.setEnabled(bool(secenekler))

        if not secenekler and not eksik:
            self._alert.goster(
                f"{yil} yili icin bu personelin 3 zorunlu muayenesi tamamlanmis.", "info"
            )

    def _rapor_sec(self) -> None:
        fp, _ = QFileDialog.getOpenFileName(self, "Rapor Formu Sec", "", "Tum Dosyalar (*.*)")
        if not fp:
            return
        self._rapor_dosya_yolu = fp
        self._rapor_lbl.setText(f"Secilen: {fp}")

    def _ac_form_yeni(self) -> None:
        self._editing_id = None
        self._rapor_dosya_yolu = ""
        self._frm_baslik.setText("Yeni Muayene Girisi")
        self._btn_sil.setVisible(False)
        self._t.setDate(QDate.currentDate())
        self._s.setDate(QDate.currentDate().addYears(1))
        self._sonuc.setCurrentIndex(0)
        self._not.clear()
        self._guncelle_akis_ve_uzmanlik()
        self._form_frame.setVisible(True)

    def _kapat_form(self) -> None:
        self._editing_id = None
        self._rapor_dosya_yolu = ""
        self._form_frame.setVisible(False)

    def _on_tablo_cift_tik(self) -> None:
        row = self._table.currentRow()
        if row < 0:
            return
        r = self._table.item(row, 0)
        if r is None:
            return
        row_obj = r.data(Qt.ItemDataRole.UserRole)
        if not row_obj:
            return

        self._editing_id = str(row_obj.get("id") or "")
        self._frm_baslik.setText("Muayene Duzenle")
        self._btn_sil.setVisible(True)

        # Uzmanlık combosunu güncelleyerek mevcut değeri seç
        self._u.blockSignals(True)
        self._u.clear()
        if self._svc:
            for uz in self._svc.uzmanlik_secenekleri():
                self._u.addItem(uz)
        self._u.blockSignals(False)
        self._u.setEnabled(True)
        uidx = self._u.findText(str(row_obj.get("uzmanlik") or ""))
        if uidx >= 0:
            self._u.setCurrentIndex(uidx)

        tarih_db = str(row_obj.get("muayene_tarihi_db") or "")
        t_qd = QDate.fromString(tarih_db, "yyyy-MM-dd")
        if t_qd.isValid():
            self._t.blockSignals(True)
            self._t.setDate(t_qd)
            self._s.setDate(t_qd.addYears(1))
            self._t.blockSignals(False)

        sidx = self._sonuc.findText(str(row_obj.get("sonuc") or ""))
        self._sonuc.setCurrentIndex(sidx if sidx >= 0 else 0)
        self._not.setText(str(row_obj.get("notlar") or ""))
        self._btn_kaydet.setEnabled(True)

        # Rapor durumunu güncelle
        pid = str(self._personel_id_getter() or "").strip()
        if pid and self._svc:
            yil = int(t_qd.year()) if t_qd.isValid() else date.today().year
            rapor = self._svc.personel_yil_tek_rapor(pid, yil)
            self._rapor_belge_id = str(rapor.get("belge_id") or "").strip() if rapor else None
            if rapor:
                self._rapor_lbl.setText(f"Rapor: {str(rapor.get('dosya_adi') or '-')}")
                self._btn_rapor_sec.setText("Raporu Degistir")
            else:
                self._rapor_lbl.setText("Rapor: Yuklenmedi")
                self._btn_rapor_sec.setText("Rapor Formu Sec")

        self._rapor_dosya_yolu = ""
        self._form_frame.setVisible(True)

    def _kaydet(self) -> None:
        if self._svc is None:
            return
        pid = str(self._personel_id_getter() or "").strip()
        if not pid:
            self._alert.goster("Personel bilgisi alinamadi.", "warning")
            return

        belge_id = self._rapor_belge_id
        if self._rapor_dosya_yolu and self._dokuman_svc:
            try:
                yil = self._secili_yil_form()
                belge_id = self._dokuman_svc.yukle(
                    file_path=self._rapor_dosya_yolu,
                    entity_turu="muayene_formu",
                    entity_id=f"{pid}:{yil}",
                    tur="Periyodik Muayene Raporu",
                    aciklama="3 uzmanlik tek rapor formu",
                    klasor_adi=f"muayene_{pid}_{yil}",
                )
            except Exception as exc:
                exc_logla("PersonelSaglikTab._kaydet.rapor", exc)
                self._alert.goster(f"Rapor yuklenemedi: {exc}", "danger")
                return

        try:
            payload = {
                "personel_id": pid,
                "uzmanlik": self._u.currentText().strip(),
                "tarih": self._t.date().toString("yyyy-MM-dd"),
                "sonuc": self._sonuc.currentText().strip(),
                "notlar": self._not.text().strip(),
                "belge_id": belge_id,
            }
            self._svc.muayene_kaydet(payload, muayene_id=self._editing_id)
            self._alert.goster("Muayene kaydi kaydedildi.", "success")
            self._kapat_form()
            self.yenile()
        except Exception as exc:
            exc_logla("PersonelSaglikTab._kaydet", exc)
            self._alert.goster(str(exc), "danger")

    # ─────────────────────────── Filtre / Liste ──────────────────────

    def _on_yil_filtre(self) -> None:
        self._secili_yil_tercihi = self._cmb_yil.currentData()
        self._apply_filters()

    def _populate_yil_filtre(self) -> None:
        yillar = sorted(
            {int(r.get("yil") or 0) for r in self._rows if int(r.get("yil") or 0) > 0},
            reverse=True,
        )
        self._cmb_yil.blockSignals(True)
        self._cmb_yil.clear()
        self._cmb_yil.addItem("Tum Yillar", None)
        for y in yillar:
            self._cmb_yil.addItem(str(y), y)
        if self._secili_yil_tercihi is not None:
            idx = self._cmb_yil.findData(self._secili_yil_tercihi)
            if idx >= 0:
                self._cmb_yil.setCurrentIndex(idx)
        self._cmb_yil.blockSignals(False)

    def _apply_filters(self) -> None:
        yil = self._cmb_yil.currentData()

        rows = list(self._rows)
        if yil is not None:
            rows = [r for r in rows if int(r.get("yil") or 0) == int(yil)]

        # Özet kartlar
        self._lbl_toplam.setText(str(len(rows)))
        self._lbl_yil.setText(str(yil) if yil is not None else "Tum")
        self._lbl_son_muayene.setText(
            str(rows[0].get("muayene_tarihi") or "-") if rows else "-"
        )
        self._lbl_rapor.setText(str(sum(1 for r in rows if r.get("rapor_var"))))

        d_say = Counter(str(r.get("durum") or "") for r in rows)
        self._lbl_gecerli.setText(str(d_say.get("Gecerli", 0)))
        self._lbl_riskli.setText(str(d_say.get("Riskli", 0)))
        self._lbl_gecikmis.setText(str(d_say.get("Gecikmis", 0)))
        self._lbl_planli.setText(str(d_say.get("Planlandi", 0)))

        # Tablo
        durum_renk = {
            "Gecerli": T.green2,
            "Riskli": T.warning if hasattr(T, "warning") else "#e8a020",
            "Gecikmis": T.red,
            "Planlandi": T.text3,
        }
        self._table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            vals = [
                str(row.get("uzmanlik") or ""),
                str(row.get("muayene_tarihi") or ""),
                str(row.get("sonraki_kontrol") or ""),
                str(row.get("sonuc") or ""),
                str(row.get("durum") or ""),
                "Var" if row.get("rapor_var") else "Yok",
            ]
            for c, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                if c != 0:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # Durum kolonuna renk
                if c == 4:
                    from PySide6.QtGui import QColor
                    renk = durum_renk.get(v)
                    if renk:
                        item.setForeground(QColor(renk))
                self._table.setItem(i, c, item)
            # Satıra ham dict'i UserRole ile göm (düzenleme için)
            self._table.item(i, 0).setData(Qt.ItemDataRole.UserRole, row)

        if not self._rows:
            self._alert.goster(
                "Bu personel icin saglik muayene kaydi bulunamadi.", "info"
            )
        elif not rows:
            self._alert.goster("Secili yila ait kayit yok.", "info")
        else:
            self._alert.temizle()

    # ─────────────────────────── Genel yenile ────────────────────────

    def _clear_ozet(self) -> None:
        for lbl in (
            self._lbl_toplam, self._lbl_yil, self._lbl_son_muayene, self._lbl_rapor,
            self._lbl_gecerli, self._lbl_riskli, self._lbl_gecikmis, self._lbl_planli,
        ):
            lbl.setText("-")
        self._table.setRowCount(0)

    def yenile(self) -> None:
        pid = str(self._personel_id_getter() or "").strip()
        if not pid or self._svc is None:
            self._alert.goster("Personel secimi alinamadi.", "warning")
            self._rows = []
            self._clear_ozet()
            return

        try:
            self._rows = self._svc.personel_muayene_kayitlari(pid)
        except Exception as exc:
            exc_logla("PersonelSaglikTab.yenile", exc)
            self._alert.goster(str(exc), "danger")
            return

        self._populate_yil_filtre()
        self._apply_filters()

    def _hucre_tikla(self, row: int, col: int) -> None:
        """Rapor kolonu (5) tiklandığında dosyayı aç."""
        if col != 5:
            return
        item = self._table.item(row, 0)
        if item is None:
            return
        r = item.data(Qt.ItemDataRole.UserRole)
        if not r:
            return
        lokal_yol = str(r.get("lokal_yol") or "").strip()
        if not lokal_yol:
            self._alert.goster("Bu kayda ait rapor dosyasi bulunamadi.", "warning")
            return
        try:
            os.startfile(lokal_yol)
        except Exception as exc:
            self._alert.goster(f"Dosya acilamadi: {exc}", "danger")

    def _sil(self) -> None:
        if not self._editing_id or self._svc is None:
            return
        cevap = QMessageBox.question(
            self,
            "Kaydi Sil",
            "Bu muayene kaydini silmek istediginizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if cevap != QMessageBox.StandardButton.Yes:
            return
        try:
            self._svc.muayene_sil(self._editing_id)
            self._alert.goster("Muayene kaydi silindi.", "success")
            self._kapat_form()
            self.yenile()
        except Exception as exc:
            exc_logla("PersonelSaglikTab._sil", exc)
            self._alert.goster(str(exc), "danger")
