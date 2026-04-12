# -*- coding: utf-8 -*-
"""tests/test_fhsz_service.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import Database
from app.db.migrations import run as migrate
from app.services.fhsz_service import FhszService
from app.services.personel_service import PersonelService


def test_puantaj_rapor_kumulatif_hesap(tmp_path):
    db = Database(tmp_path / "test.db")
    migrate(db)
    try:
        psvc = PersonelService(db)
        fsvc = FhszService(db)

        pid = psvc.ekle(
            {
                "tc_kimlik": "10000000146",
                "ad": "Ali",
                "soyad": "Kaya",
                "memuriyet_baslama": "2018-01-01",
            }
        )

        fsvc.donem_kaydet(
            yil=2026,
            donem=1,
            satirlar=[
                {
                    "personel_id": pid,
                    "calisma_kosulu": "A",
                    "aylik_gun": 20,
                    "izin_gun": 2,
                }
            ],
        )
        fsvc.donem_kaydet(
            yil=2026,
            donem=2,
            satirlar=[
                {
                    "personel_id": pid,
                    "calisma_kosulu": "A",
                    "aylik_gun": 18,
                    "izin_gun": 0,
                }
            ],
        )

        rapor = fsvc.puantaj_rapor_uret(yil=2026)
        assert len(rapor) == 3

        d1 = next(r for r in rapor if r["donem"] == 1)
        d2 = next(r for r in rapor if r["donem"] == 2)
        toplam = next(r for r in rapor if r["donem"] == "Toplam")

        assert d1["fiili_saat"] == 126.0
        assert d1["kumulatif_saat"] == 126.0
        assert d2["fiili_saat"] == 126.0
        assert d2["kumulatif_saat"] == 252.0
        assert toplam["kumulatif_saat"] == 252.0
        assert toplam["sua_hak_edis"] == 6

        tek = fsvc.puantaj_rapor_uret(yil=2026, donem=2)
        assert len(tek) == 1
        assert tek[0]["donem"] == 2
        assert tek[0]["kumulatif_saat"] == 252.0
    finally:
        db.close()
