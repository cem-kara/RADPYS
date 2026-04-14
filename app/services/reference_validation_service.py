# -*- coding: utf-8 -*-
"""Merkezi lookup/reference dogrulama servisi."""
from __future__ import annotations

from dataclasses import dataclass

from app.config import LOOKUP_DOGRULAMA_POLITIKALARI, LookupPolitika
from app.db.repos.lookup_repo import LookupRepo
from app.text_utils import turkish_lower, turkish_title_case


@dataclass(slots=True)
class ReferenceValidationResult:
    basarili: bool
    kanonik_deger: str = ""
    aksiyon: str = "none"  # none | review | added
    mesaj: str = ""


class ReferenceValidationService:
    """Lookup degerlerini normalize/kanonik hale getirir."""

    def __init__(self, db):
        self._lookup = LookupRepo(db)

    @staticmethod
    def _norm(text: str) -> str:
        tip = turkish_lower(str(text or "")).strip()
        return " ".join(
            tip.replace("ü", "u")
            .replace("ı", "i")
            .replace("ş", "s")
            .replace("ğ", "g")
            .replace("ö", "o")
            .replace("ç", "c")
            .replace("_", " ")
            .replace("-", " ")
            .split()
        )

    def _kanonik_harita(self, kategori: str) -> dict[str, str]:
        harita: dict[str, str] = {}
        for deger in self._lookup.kategori(kategori):
            anahtar = self._norm(deger)
            if anahtar and anahtar not in harita:
                harita[anahtar] = deger
        return harita

    def dogrula_lookup_deger(
        self,
        kategori: str,
        ham_deger: str,
        politika: str | None = None,
    ) -> ReferenceValidationResult:
        metin = str(ham_deger or "").strip()
        if not metin:
            return ReferenceValidationResult(False, mesaj="Deger bos olamaz")

        aktif_politika = politika or LOOKUP_DOGRULAMA_POLITIKALARI.get(kategori, LookupPolitika.STRICT)
        kanonik_harita = self._kanonik_harita(kategori)
        anahtar = self._norm(metin)

        if anahtar in kanonik_harita:
            return ReferenceValidationResult(True, kanonik_deger=kanonik_harita[anahtar])

        alias_eslesme = self._lookup.alias_ile_getir(kategori, metin)
        if alias_eslesme:
            return ReferenceValidationResult(True, kanonik_deger=alias_eslesme)

        if aktif_politika == LookupPolitika.PERMISSIVE:
            yeni = turkish_title_case(metin)
            self._lookup.deger_ekle(kategori, yeni)
            self._lookup.alias_ekle(kategori, metin, yeni, kaynak="otomatik")
            return ReferenceValidationResult(True, kanonik_deger=yeni, aksiyon="added")

        if aktif_politika == LookupPolitika.REVIEW:
            return ReferenceValidationResult(
                False,
                aksiyon="review",
                mesaj=f"Deger onay bekliyor: {metin}",
            )

        return ReferenceValidationResult(
            False,
            mesaj=f"Lookup listesinde bulunamadi: {metin}",
        )
