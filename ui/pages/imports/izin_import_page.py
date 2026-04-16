# -*- coding: utf-8 -*-
"""Izin import sayfasi."""
from __future__ import annotations

from app.date_utils import parse_date
from app.exceptions import DogrulamaHatasi
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QWidget

from app.config import LookupKategori, LookupPolitika
from app.services.excel_import_service import AlanTanimi, ImportKonfig
from app.services.izin_service import IzinService
from app.services.personel_service import PersonelService
from app.services.reference_validation_service import ReferenceValidationService
from app.text_utils import turkish_title_case
from app.validators import validate_tc_kimlik_no
from ui.pages.imports.components.base_import_page import BaseImportPage
from ui.styles import T


def _tc_v(v):
    text = _tc_norm(v)
    if not text:
        return True, ""
    return validate_tc_kimlik_no(text), "Gecersiz TC Kimlik No"


def _tc_norm(v) -> str:
    raw = str(v or "").strip()
    if not raw:
        return ""

    if raw.endswith(".0"):
        raw = raw[:-2]

    digits = "".join(ch for ch in raw if ch.isdigit())
    return digits


def _tarih_v(v):
    text = str(v or "").strip()
    if not text:
        return False, "Tarih zorunlu"
    return parse_date(text) is not None, "Gecersiz tarih"


def _gun_v(v):
    text = str(v or "").strip()
    if not text:
        return True, ""
    try:
        return int(float(text)) > 0, "Gun pozitif tam sayi olmalidir"
    except (TypeError, ValueError):
        return False, "Gun pozitif tam sayi olmalidir"


def _normalize(kayit: dict) -> dict:
    for key in ("tur", "aciklama"):
        kayit[key] = str(kayit.get(key) or "").strip()

    kayit["tc_kimlik"] = _tc_norm(kayit.get("tc_kimlik"))

    for key in ("baslama", "bitis"):
        dt = parse_date(kayit.get(key))
        kayit[key] = str(dt) if dt else ""

    gun_text = str(kayit.get("gun") or "").strip()
    if gun_text:
        try:
            kayit["gun"] = int(float(gun_text))
        except (TypeError, ValueError):
            kayit["gun"] = ""
    else:
        kayit["gun"] = ""

    if kayit.get("tur"):
        kayit["tur"] = turkish_title_case(kayit["tur"])

    return kayit


class _IzinImportAdapter:
    """Import satirini IzinService.ekle formatina cevirir."""

    def __init__(self, db, otomatik_ekle: bool = False):
        self._izin = IzinService(db)
        self._personel = PersonelService(db)
        self._ref = ReferenceValidationService(db)
        self._otomatik_ekle = otomatik_ekle

    def _izin_tur_norm(self, tur_raw: str) -> str:
        text = str(tur_raw or "").strip()
        if not text:
            raise DogrulamaHatasi("Izin turu zorunludur.")

        politika = LookupPolitika.PERMISSIVE if self._otomatik_ekle else None
        adaylar = [text]
        if " - " in text:
            adaylar.insert(0, text.split(" - ", 1)[0].strip())

        son_hata = ""
        for aday in adaylar:
            sonuc = self._ref.dogrula_lookup_deger(
                LookupKategori.IZIN_TUR,
                aday,
                politika=politika,
            )
            if sonuc.basarili:
                return sonuc.kanonik_deger
            son_hata = sonuc.mesaj

        raise DogrulamaHatasi(son_hata or f"Izin turu lookup listesinde yok: {tur_raw}")

    @staticmethod
    def _gun_hesapla(kayit: dict) -> int:
        gun = kayit.get("gun")
        if str(gun or "").strip():
            try:
                value = int(gun)
                if value <= 0:
                    raise ValueError
                return value
            except (TypeError, ValueError) as exc:
                raise DogrulamaHatasi("Gun pozitif bir tam sayi olmalidir.") from exc

        baslama = parse_date(kayit.get("baslama"))
        bitis = parse_date(kayit.get("bitis"))
        if baslama and bitis and bitis >= baslama:
            return (bitis - baslama).days + 1

        raise DogrulamaHatasi("Gun bos ise baslama ve bitis tarihleri gecerli olmali.")

    def _personel_id_bul(self, kayit: dict) -> str:
        tc = str(kayit.get("tc_kimlik") or "").strip()
        if not tc:
            raise DogrulamaHatasi("TC Kimlik No zorunludur.")
        if not validate_tc_kimlik_no(tc):
            raise DogrulamaHatasi(f"Gecersiz TC Kimlik No: {tc}")

        personel = self._personel.tc_ile_getir(tc)
        pid = str(personel.get("id") or "").strip()
        if not pid:
            raise DogrulamaHatasi(f"TC ile personel bulundu ama ID bos: {tc}")
        return pid

    def ekle(self, kayit: dict) -> str:
        personel_id = self._personel_id_bul(kayit)
        tur = str(kayit.get("tur") or "").strip()
        baslama = str(kayit.get("baslama") or "").strip()
        if not baslama:
            raise DogrulamaHatasi("Baslama tarihi zorunludur.")

        payload = {
            "personel_id": personel_id,
            "tur": self._izin_tur_norm(tur),
            "baslama": baslama,
            "gun": self._gun_hesapla(kayit),
            "aciklama": str(kayit.get("aciklama") or "").strip() or None,
        }
        return self._izin.ekle_arsiv(payload)

    def guncelle_veya_ekle_arsiv(self, kayit: dict) -> str:
        personel_id = self._personel_id_bul(kayit)
        tur = str(kayit.get("tur") or "").strip()
        baslama = str(kayit.get("baslama") or "").strip()
        if not baslama:
            raise DogrulamaHatasi("Baslama tarihi zorunludur.")

        payload = {
            "personel_id": personel_id,
            "tur": self._izin_tur_norm(tur),
            "baslama": baslama,
            "gun": self._gun_hesapla(kayit),
            "aciklama": str(kayit.get("aciklama") or "").strip() or None,
        }
        return self._izin.guncelle_veya_ekle_arsiv(payload)


def _izin_servis_fabrikasi(otomatik_ekle: bool):
    def _fabrika(db):
        return _IzinImportAdapter(db, otomatik_ekle=otomatik_ekle)
    return _fabrika


def _konfig_olustur(otomatik_ekle: bool) -> ImportKonfig:
    return ImportKonfig(
        baslik="Toplu Izin Ice Aktarma",
        servis_fabrika=_izin_servis_fabrikasi(otomatik_ekle),
        servis_metod="ekle",
        servis_metod_upsert="guncelle_veya_ekle_arsiv",
        tablo_adi="izin",
        normalize_fn=_normalize,
        alanlar=[
            AlanTanimi("tc_kimlik", "TC Kimlik No", "tc", zorunlu=True, validator=_tc_v, anahtar_kelimeler=["tc", "tckimlik", "kimlikno", "kimlik", "tckn"]),
            AlanTanimi("tur", "Izin Turu", "str", zorunlu=True, anahtar_kelimeler=["izinturu", "izin", "tur", "type"]),
            AlanTanimi("baslama", "Baslama Tarihi", "date", zorunlu=True, validator=_tarih_v, anahtar_kelimeler=["baslama", "baslamatarihi", "baslangictarihi", "startdate", "baslangic"]),
            AlanTanimi("bitis", "Bitis Tarihi", "date", anahtar_kelimeler=["bitis", "bitistarihi", "enddate", "bitisdate"]),
            AlanTanimi("gun", "Gun", "int", validator=_gun_v, anahtar_kelimeler=["gun", "gunsayisi", "sure", "suregun"]),
            AlanTanimi("aciklama", "Aciklama", "str", anahtar_kelimeler=["aciklama", "not", "reason"]),
        ],
    )


class IzinImportPage(BaseImportPage):
    def __init__(self, db=None, parent=None):
        self._cb_otomatik = QCheckBox("Bilinmeyen izin turlerini otomatik kaydet")
        self._cb_otomatik.setChecked(False)
        super().__init__(db=db, parent=parent)

    def _konfig(self) -> ImportKonfig:
        return _konfig_olustur(self._cb_otomatik.isChecked())

    def _kur_ui(self) -> None:
        super()._kur_ui()
        # Checkbox'i alert bar'in hemen ustune ekle
        layout = self.layout()
        bilgi = QWidget(self)
        bilgi_lay = QHBoxLayout(bilgi)
        bilgi_lay.setContentsMargins(0, 0, 0, 0)
        self._cb_otomatik.setStyleSheet(
            f"color:{T.text2}; font-size:12px;"
        )
        bilgi_lay.addWidget(self._cb_otomatik)
        bilgi_lay.addStretch(1)
        bilgi_lay.addWidget(
            _bilgi_etiketi(
                "Aktif: Yeni tur lookup listesine eklenir. "
                "Pasif: Listede olmayan tur hataya dusar."
            )
        )
        layout.insertWidget(2, bilgi)  # adim bari ve alert arasina

    def _aktar(self) -> None:
        # Aktarim aninda guncel checkbox durumuna gore konfig yenilenir.
        self._konfig_obj = _konfig_olustur(self._cb_otomatik.isChecked())
        super()._aktar()


def _bilgi_etiketi(metin: str) -> QLabel:
    lbl = QLabel(metin)
    lbl.setStyleSheet("color: #8a8fa8; font-size: 11px;")
    lbl.setWordWrap(True)
    return lbl
