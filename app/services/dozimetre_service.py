# -*- coding: utf-8 -*-
"""app/services/dozimetre_service.py - Dozimetre takip is mantigi."""
from __future__ import annotations

import sqlite3

from app.config import HP10_TEHLIKE, HP10_UYARI
from app.db.database import Database
from app.db.repos.dozimetre_repo import DozimetreRepo
from app.db.repos.personel_repo import PersonelRepo


class DozimetreService:
    """Dozimetre olcum verilerini UI dostu sekilde sunar."""

    def __init__(self, db: Database):
        self._db = db
        self._repo = DozimetreRepo(db)
        self._personel_repo = PersonelRepo(db)

    @staticmethod
    def _to_float(value) -> float | None:
        if value is None:
            return None
        text = str(value).strip().replace(",", ".")
        if not text:
            return None
        try:
            return float(text)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _durum_hesapla(hp10: float | None, raw_durum: str | None) -> str:
        if hp10 is not None:
            if hp10 >= HP10_TEHLIKE:
                return "Tehlike"
            if hp10 >= HP10_UYARI:
                return "Uyari"
            return "Normal"
        return str(raw_durum or "").strip() or "Belirsiz"

    def tum_olcumler(
        self,
        yil: int | None = None,
        periyot: int | None = None,
        birim: str | None = None,
    ) -> list[dict]:
        rows = self._repo.listele(yil=yil, periyot=periyot, birim=birim)
        out: list[dict] = []

        for r in rows:
            hp10 = self._to_float(r.get("hp10"))
            hp007 = self._to_float(r.get("hp007"))
            out.append(
                {
                    "id": str(r.get("id") or ""),
                    "personel_id": str(r.get("personel_id") or ""),
                    "ad_soyad": f"{r.get('ad') or ''} {r.get('soyad') or ''}".strip(),
                    "tc_kimlik": str(r.get("tc_kimlik") or ""),
                    "birim": str(r.get("birim") or ""),
                    "yil": int(r.get("yil") or 0),
                    "periyot": int(r.get("periyot") or 0),
                    "periyot_adi": str(r.get("periyot_adi") or ""),
                    "dozimetre_no": str(r.get("dozimetre_no") or ""),
                    "tur": str(r.get("tur") or ""),
                    "bolge": str(r.get("bolge") or ""),
                    "hp10": hp10,
                    "hp007": hp007,
                    "durum": self._durum_hesapla(hp10, r.get("durum")),
                    "rapor_no": str(r.get("rapor_no") or ""),
                }
            )
        return out

    def istatistikler(self, rows: list[dict]) -> dict:
        if not rows:
            return {
                "toplam": 0,
                "personel": 0,
                "rapor": 0,
                "max_hp10": None,
                "uyari": 0,
                "tehlike": 0,
            }

        hp10_vals = [r.get("hp10") for r in rows if r.get("hp10") is not None]
        return {
            "toplam": len(rows),
            "personel": len({str(r.get("personel_id") or "") for r in rows if r.get("personel_id")}),
            "rapor": len({str(r.get("rapor_no") or "") for r in rows if str(r.get("rapor_no") or "").strip()}),
            "max_hp10": max(hp10_vals) if hp10_vals else None,
            "uyari": sum(1 for r in rows if str(r.get("durum") or "") == "Uyari"),
            "tehlike": sum(1 for r in rows if str(r.get("durum") or "") == "Tehlike"),
        }

    def personel_listesi(self) -> list[dict]:
        rows = self._personel_repo.listele(aktif_only=False)
        out: list[dict] = []
        for r in rows:
            pid = str(r.get("id") or "").strip()
            tc = str(r.get("tc_kimlik") or "").strip()
            if not pid or not tc:
                continue
            out.append(
                {
                    "id": pid,
                    "KimlikNo": tc,
                    "AdSoyad": f"{r.get('ad') or ''} {r.get('soyad') or ''}".strip(),
                }
            )
        return out

    def rapor_olcumleri(self, rapor_no: str) -> list[dict]:
        no = str(rapor_no or "").strip()
        if not no:
            return []
        return self._repo.rapor_listele(no)

    def personel_olcumleri(
        self,
        personel_id: str,
        yil: int | None = None,
    ) -> list[dict]:
        """Belirli bir personele ait tum olcumleri dondurur."""
        pid = str(personel_id or "").strip()
        if not pid:
            return []
        rows = self._repo.listele(personel_id=pid, yil=yil)
        out: list[dict] = []
        for r in rows:
            hp10 = self._to_float(r.get("hp10"))
            hp007 = self._to_float(r.get("hp007"))
            out.append(
                {
                    "id": str(r.get("id") or ""),
                    "yil": int(r.get("yil") or 0),
                    "periyot": int(r.get("periyot") or 0),
                    "periyot_adi": str(r.get("periyot_adi") or ""),
                    "dozimetre_no": str(r.get("dozimetre_no") or ""),
                    "tur": str(r.get("tur") or ""),
                    "bolge": str(r.get("bolge") or ""),
                    "hp10": hp10,
                    "hp007": hp007,
                    "durum": self._durum_hesapla(hp10, r.get("durum")),
                    "rapor_no": str(r.get("rapor_no") or ""),
                }
            )
        return out

    def olcum_ekle(self, kayit: dict) -> bool:
        pid = str(kayit.get("personel_id") or "").strip()
        if not pid:
            raise ValueError("personel_id zorunludur")

        payload = {
            "personel_id": pid,
            "rapor_no": str(kayit.get("rapor_no") or "").strip() or None,
            "yil": int(kayit.get("yil") or 0),
            "periyot": int(kayit.get("periyot") or 0),
            "periyot_adi": str(kayit.get("periyot_adi") or "").strip() or None,
            "dozimetre_no": str(kayit.get("dozimetre_no") or "").strip() or None,
            "tur": str(kayit.get("tur") or "").strip() or None,
            "bolge": str(kayit.get("bolge") or "").strip() or None,
            "hp10": self._to_float(kayit.get("hp10")),
            "hp007": self._to_float(kayit.get("hp007")),
            "durum": str(kayit.get("durum") or "").strip() or None,
        }

        if payload["yil"] <= 0 or payload["periyot"] <= 0:
            raise ValueError("yil ve periyot zorunludur")

        try:
            self._repo.ekle(payload)
            return True
        except sqlite3.IntegrityError as exc:
            if "UNIQUE" in str(exc).upper():
                return False
            raise
