# -*- coding: utf-8 -*-
"""Ortak Excel import iskeleti.

Bu modül ilk fazda sadece temel akışı sağlar:
- Excel okuma
- Kolon eşleme
- Satır önizleme/doğrulama
- Servis metoduna satır bazlı gönderim

Gelişmiş duplicate/transaction politikaları sonraki adımlarda eklenir.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


ValidatorFn = Callable[[Any], bool | tuple[bool, str]]


@dataclass(slots=True)
class AlanTanimi:
    ad: str
    etiket: str
    tip: str = "str"
    zorunlu: bool = False
    validator: ValidatorFn | None = None
    varsayilan: Any = None
    anahtar_kelimeler: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DuplicateKontrol:
    pk_alanlar: list[str] = field(default_factory=list)
    pk_cakisma: str = "raporla"
    yumusak_alanlar: list[str] = field(default_factory=list)
    yumusak_cakisma: str = "uyar"


@dataclass(slots=True)
class ImportKonfig:
    baslik: str
    servis_fabrika: Callable[[Any], Any]
    servis_metod: str
    tablo_adi: str
    alanlar: list[AlanTanimi]
    normalize_fn: Callable[[dict], dict] | None = None
    duplicate: DuplicateKontrol | None = None


@dataclass(slots=True)
class SatirSonucu:
    satir_no: int
    veri: dict
    basarili: bool
    hata_mesaji: str = ""
    duzeltilmis_veri: dict | None = None


@dataclass(slots=True)
class ImportSonucu:
    toplam: int
    basarili: int
    hatali: int
    satirlar: list[SatirSonucu]


def alanlar_tam_listesi(konfig: ImportKonfig) -> list[AlanTanimi]:
    """İlk fazda konfigde tanımlı alanlar döndürülür."""
    return list(konfig.alanlar)


class ExcelImportService:
    """Excel import işlemlerinin ortak çekirdeği."""

    _NORM_CHAR_MAP = str.maketrans({
        "ç": "c",
        "Ç": "c",
        "ğ": "g",
        "Ğ": "g",
        "ı": "i",
        "İ": "i",
        "ö": "o",
        "Ö": "o",
        "ş": "s",
        "Ş": "s",
        "ü": "u",
        "Ü": "u",
    })

    @staticmethod
    def _norm_key(text: str) -> str:
        normalized = str(text or "").translate(ExcelImportService._NORM_CHAR_MAP)
        return "".join(ch.lower() for ch in normalized if ch.isalnum())

    def excel_oku(self, dosya_yolu: str):
        try:
            import pandas as pd
        except Exception as exc:
            raise RuntimeError("Excel import için pandas kurulmalı.") from exc

        return pd.read_excel(dosya_yolu)

    def sutun_haritasi_olustur(self, df_kolonlari: list[str], konfig: ImportKonfig) -> dict[str, str]:
        kaynak_harita = {self._norm_key(col): str(col) for col in df_kolonlari}
        sonuc: dict[str, str] = {}

        for alan in alanlar_tam_listesi(konfig):
            adaylar = [alan.ad, alan.etiket, *alan.anahtar_kelimeler]
            for aday in adaylar:
                key = self._norm_key(aday)
                if key in kaynak_harita:
                    sonuc[alan.ad] = kaynak_harita[key]
                    break
        return sonuc

    @staticmethod
    def _validator_calistir(validator: ValidatorFn | None, value: Any) -> tuple[bool, str]:
        if validator is None:
            return True, ""
        sonuc = validator(value)
        if isinstance(sonuc, tuple):
            return bool(sonuc[0]), str(sonuc[1])
        return bool(sonuc), "Geçersiz alan"

    def satir_onizleme(self, df, harita: dict[str, str], konfig: ImportKonfig) -> list[SatirSonucu]:
        satirlar: list[SatirSonucu] = []
        alanlar = alanlar_tam_listesi(konfig)

        for index, row in df.iterrows():
            kayit: dict[str, Any] = {}
            hata = ""

            for alan in alanlar:
                kaynak_kolon = harita.get(alan.ad)
                raw = row.get(kaynak_kolon) if kaynak_kolon else None

                if raw is None or str(raw).strip().lower() == "nan":
                    value = alan.varsayilan
                else:
                    value = str(raw).strip()

                if alan.zorunlu and not str(value or "").strip():
                    hata = f"Zorunlu alan boş: {alan.etiket}"
                    break

                ok, mesaj = self._validator_calistir(alan.validator, value)
                if not ok and str(value or "").strip():
                    hata = mesaj or f"Doğrulama hatası: {alan.etiket}"
                    break

                kayit[alan.ad] = value

            if not hata and konfig.normalize_fn:
                kayit = konfig.normalize_fn(kayit)

            satirlar.append(
                SatirSonucu(
                    satir_no=int(index) + 2,
                    veri=kayit,
                    basarili=not bool(hata),
                    hata_mesaji=hata,
                )
            )

        return satirlar

    def import_et(self, df, harita: dict[str, str], konfig: ImportKonfig, db: Any) -> ImportSonucu:
        satirlar = self.satir_onizleme(df, harita, konfig)
        servis = konfig.servis_fabrika(db)
        metod = getattr(servis, konfig.servis_metod)

        basarili = 0
        for satir in satirlar:
            if not satir.basarili:
                continue
            try:
                sonuc = metod(satir.veri)
                if isinstance(sonuc, bool) and not sonuc:
                    satir.basarili = False
                    satir.hata_mesaji = "Servis kaydı kabul etmedi"
                    continue
                basarili += 1
            except Exception as exc:
                satir.basarili = False
                satir.hata_mesaji = str(exc)

        toplam = len(satirlar)
        return ImportSonucu(
            toplam=toplam,
            basarili=basarili,
            hatali=toplam - basarili,
            satirlar=satirlar,
        )
