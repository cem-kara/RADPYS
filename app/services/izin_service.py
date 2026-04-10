# -*- coding: utf-8 -*-
"""app/services/izin_service.py - izin hak edis hesaplari."""
from __future__ import annotations

from datetime import date

from app.config import YILLIK_HAK_1_10, YILLIK_HAK_10P
from app.date_utils import parse_date


class IzinService:
    """Izin hak edis bilgilerini hesaplar."""

    @staticmethod
    def yillik_hak_hesapla(memuriyet_baslama, today: date | None = None) -> float:
        start = parse_date(memuriyet_baslama)
        if not start:
            return YILLIK_HAK_1_10

        ref = today or date.today()
        hizmet_yili = max(0.0, (ref - start).days / 365.25)
        return YILLIK_HAK_10P if hizmet_yili >= 10 else YILLIK_HAK_1_10

    def hak_edis_bilgisi(self, memuriyet_baslama, today: date | None = None) -> dict:
        start = parse_date(memuriyet_baslama)
        ref = today or date.today()
        hizmet_yili = 0.0 if not start else max(0.0, (ref - start).days / 365.25)
        return {
            "hizmet_yili": round(hizmet_yili, 2),
            "yillik_hak": self.yillik_hak_hesapla(memuriyet_baslama, ref),
        }
