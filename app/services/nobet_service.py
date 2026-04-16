# -*- coding: utf-8 -*-
"""app/services/nobet_service.py - Nöbet planı hazırlık servis katmanı."""
from __future__ import annotations

import sqlite3
from datetime import date

from app.db.database import Database
from app.db.repos.nobet_repo import NobetRepo
from app.exceptions import DogrulamaHatasi, KayitBulunamadi, KayitZatenVar


class NobetService:
    """Nobet birim ve plan tablolari icin temel is kurallari."""

    def __init__(self, db: Database):
        self._repo = NobetRepo(db)

    def birimler_listele(self, aktif_only: bool = True) -> list[dict]:
        return self._repo.birimler_listele(aktif_only=aktif_only)

    def birim_kural_getir(self, birim_id: str) -> dict:
        bid = str(birim_id or "").strip()
        if not bid:
            raise DogrulamaHatasi("Birim secimi zorunludur.")
        if self._repo.birim_getir(bid) is None:
            raise KayitBulunamadi("Birim bulunamadi.")
        kural = self._repo.birim_kural_getir(bid) or {}
        if not kural:
            return {
                "birim_id": bid,
                "min_dinlenme_saat": 12.0,
                "resmi_tatil_calisma": 1,
                "dini_tatil_calisma": 1,
                "arefe_baslangic_saat": "13:00",
                "max_fazla_mesai_saat": 0.0,
                "tolerans_saat": 7.0,
                "max_devreden_saat": 12.0,
                "manuel_limit_asimina_izin": 1,
            }
        return kural

    def birim_kural_kaydet(self, birim_id: str, veri: dict) -> None:
        bid = str(birim_id or "").strip()
        if not bid:
            raise DogrulamaHatasi("Birim secimi zorunludur.")
        if self._repo.birim_getir(bid) is None:
            raise KayitBulunamadi("Birim bulunamadi.")

        min_dinlenme = float(veri.get("min_dinlenme_saat") or 12)
        tolerans = float(veri.get("tolerans_saat") or 7)
        devreden = float(veri.get("max_devreden_saat") or 12)
        max_fazla = float(veri.get("max_fazla_mesai_saat") or 0)
        arefe = str(veri.get("arefe_baslangic_saat") or "13:00").strip()
        if min_dinlenme < 0:
            raise DogrulamaHatasi("Dinlenme suresi negatif olamaz.")
        if tolerans < 0:
            raise DogrulamaHatasi("Tolerans negatif olamaz.")
        if devreden < 0:
            raise DogrulamaHatasi("Devreden saat negatif olamaz.")
        if max_fazla < 0:
            raise DogrulamaHatasi("Fazla mesai limiti negatif olamaz.")
        if len(arefe) != 5 or arefe[2] != ":":
            raise DogrulamaHatasi("Arefe baslangic saati HH:MM formatinda olmalidir.")

        self._repo.birim_kural_upsert(
            bid,
            {
                "min_dinlenme_saat": min_dinlenme,
                "resmi_tatil_calisma": 1 if bool(veri.get("resmi_tatil_calisma")) else 0,
                "dini_tatil_calisma": 1 if bool(veri.get("dini_tatil_calisma")) else 0,
                "arefe_baslangic_saat": arefe,
                "max_fazla_mesai_saat": max_fazla,
                "tolerans_saat": tolerans,
                "max_devreden_saat": devreden,
                "manuel_limit_asimina_izin": 1 if bool(veri.get("manuel_limit_asimina_izin")) else 0,
            },
        )

    def vardiya_listele(self, birim_id: str, aktif_only: bool = True) -> list[dict]:
        bid = str(birim_id or "").strip()
        if not bid:
            return []
        return self._repo.vardiya_listele(bid, aktif_only=aktif_only)

    def sablon_listele(self, aktif_only: bool = True) -> list[dict]:
        return self._repo.sablon_listele(aktif_only=aktif_only)

    def sablon_ekle(
        self,
        ad: str,
        baslangic_saat: str,
        bitis_saat: str,
        saat_suresi: float,
        aciklama: str = "",
    ) -> str:
        txt_ad = str(ad or "").strip()
        if not txt_ad:
            raise DogrulamaHatasi("Sablon adi zorunludur.")
        sure = float(saat_suresi)
        if sure <= 0:
            raise DogrulamaHatasi("Vardiya suresi pozitif olmalidir.")
        bas = str(baslangic_saat or "").strip()
        bit = str(bitis_saat or "").strip()
        if len(bas) != 5 or len(bit) != 5 or bas[2] != ":" or bit[2] != ":":
            raise DogrulamaHatasi("Saat formati HH:MM olmalidir.")
        try:
            return self._repo.sablon_ekle(txt_ad, bas, bit, sure, aciklama)
        except Exception as exc:
            if "UNIQUE" in str(exc).upper():
                raise KayitZatenVar(f"'{txt_ad}' adinda sablon zaten mevcut.") from exc
            raise

    def sablon_pasife_al(self, sablon_id: str) -> None:
        sid = str(sablon_id or "").strip()
        if not sid:
            raise DogrulamaHatasi("Sablon secimi zorunludur.")
        if self._repo.sablon_getir(sid) is None:
            raise KayitBulunamadi("Sablon bulunamadi.")
        self._repo.sablon_pasife_al(sid)

    def sablon_birime_ata(self, birim_id: str, sablon_id: str, max_personel: int) -> str:
        bid = str(birim_id or "").strip()
        sid = str(sablon_id or "").strip()
        if not bid:
            raise DogrulamaHatasi("Birim secimi zorunludur.")
        if not sid:
            raise DogrulamaHatasi("Sablon secimi zorunludur.")
        if self._repo.birim_getir(bid) is None:
            raise KayitBulunamadi("Birim bulunamadi.")
        if self._repo.sablon_getir(sid) is None:
            raise KayitBulunamadi("Sablon bulunamadi.")
        mp = int(max_personel)
        if mp < 1:
            raise DogrulamaHatasi("Max personel en az 1 olmalidir.")
        return self._repo.sablon_birime_ata(bid, sid, mp)

    def vardiya_pasife_al(self, vardiya_id: str) -> None:
        vid = str(vardiya_id or "").strip()
        if not vid:
            raise DogrulamaHatasi("Vardiya secimi zorunludur.")
        self._repo.vardiya_pasife_al(vid)

    def vardiya_ekle(
        self,
        birim_id: str,
        ad: str,
        saat_suresi: float,
        baslangic_saat: str,
        bitis_saat: str,
        max_personel: int = 1,
    ) -> str:
        bid = str(birim_id or "").strip()
        txt_ad = str(ad or "").strip()
        if not bid:
            raise DogrulamaHatasi("Birim secimi zorunludur.")
        if not txt_ad:
            raise DogrulamaHatasi("Vardiya adi zorunludur.")
        sure = float(saat_suresi)
        if sure <= 0:
            raise DogrulamaHatasi("Vardiya suresi pozitif olmalidir.")
        bas = str(baslangic_saat or "").strip()
        bit = str(bitis_saat or "").strip()
        if len(bas) != 5 or len(bit) != 5 or bas[2] != ":" or bit[2] != ":":
            raise DogrulamaHatasi("Saat formati HH:MM olmalidir.")
        mp = int(max_personel)
        if mp < 1:
            raise DogrulamaHatasi("Max personel en az 1 olmalidir.")
        return self._repo.vardiya_ekle(bid, txt_ad, sure, bas, bit, max_personel=mp)

    def birim_personellerini_esitle(self, birim_id: str) -> int:
        bid = str(birim_id or "").strip()
        if not bid:
            raise DogrulamaHatasi("Birim secimi zorunludur.")
        if self._repo.birim_getir(bid) is None:
            raise KayitBulunamadi("Birim bulunamadi.")
        return self._repo.birim_personellerini_esitle(bid)

    def birim_personel_kosullari_listele(self, birim_id: str) -> list[dict]:
        bid = str(birim_id or "").strip()
        if not bid:
            return []
        return self._repo.birim_personel_listele(bid)

    def personel_kosul_kaydet(self, birim_id: str, personel_id: str, veri: dict) -> None:
        bid = str(birim_id or "").strip()
        pid = str(personel_id or "").strip()
        if not bid or not pid:
            raise DogrulamaHatasi("Birim ve personel secimi zorunludur.")
        if float(veri.get("max_fazla_mesai_saat") or 0) < 0:
            raise DogrulamaHatasi("Fazla mesai limiti negatif olamaz.")
        if float(veri.get("tolerans_saat") or 7) < 0:
            raise DogrulamaHatasi("Tolerans negatif olamaz.")
        if float(veri.get("max_devreden_saat") or 12) < 0:
            raise DogrulamaHatasi("Devreden saat negatif olamaz.")

        self._repo.personel_kural_upsert(
            bid,
            pid,
            {
                "ister_24_saat": 1 if bool(veri.get("ister_24_saat")) else 0,
                "mesai_istemiyor": 1 if bool(veri.get("mesai_istemiyor")) else 0,
                "max_fazla_mesai_saat": float(veri.get("max_fazla_mesai_saat") or 0),
                "tolerans_saat": float(veri.get("tolerans_saat") or 7),
                "max_devreden_saat": float(veri.get("max_devreden_saat") or 12),
            },
        )

    def birimleri_gorev_yerinden_esitle(self) -> int:
        return self._repo.birimleri_gorev_yerinden_esitle()

    def planlari_listele(self, yil: int | None = None, ay: int | None = None) -> list[dict]:
        return self._repo.plan_listele(yil=yil, ay=ay)

    def taslak_plan_olustur(
        self,
        birim_id: str,
        yil: int,
        ay: int,
        notlar: str = "",
    ) -> str:
        bid = str(birim_id or "").strip()
        if not bid:
            raise DogrulamaHatasi("Nobet birimi secimi zorunludur.")

        if self._repo.birim_getir(bid) is None:
            raise KayitBulunamadi("Secilen nobet birimi bulunamadi.")

        y = int(yil)
        m = int(ay)
        if y < 2000 or y > 2100:
            raise DogrulamaHatasi("Yil gecersiz.")
        if m < 1 or m > 12:
            raise DogrulamaHatasi("Ay 1-12 araliginda olmalidir.")

        if self._repo.plan_getir(bid, y, m):
            raise KayitZatenVar("Bu birim ve ay icin plan zaten mevcut.")

        try:
            return self._repo.plan_ekle(
                birim_id=bid,
                yil=y,
                ay=m,
                durum="taslak",
                notlar=notlar,
            )
        except sqlite3.IntegrityError as exc:
            if "UNIQUE" in str(exc).upper():
                raise KayitZatenVar("Bu birim ve ay icin plan zaten mevcut.") from exc
            raise

    @staticmethod
    def varsayilan_donem() -> tuple[int, int]:
        bugun = date.today()
        return bugun.year, bugun.month
