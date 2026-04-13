# -*- coding: utf-8 -*-
"""tests/test_dozimetre_service.py"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import Database
from app.db.migrations import run as migrate
from app.db.seed import seed_all
from app.services.personel_service import PersonelService
from app.services.dozimetre_service import DozimetreService


@pytest.fixture
def db(tmp_path):
    d = Database(tmp_path / "test.db")
    migrate(d)
    seed_all(d)
    yield d
    d.close()


@pytest.fixture
def personel_id(db):
    psvc = PersonelService(db)
    return psvc.ekle(
        {
            "tc_kimlik": "10000000146",
            "ad": "Doz",
            "soyad": "Test",
            "memuriyet_baslama": "2021-01-01",
        }
    )


def _ekle(db, pid, hp10, hp007, periyot=1, rapor_no="R-2026-01"):
    db.execute(
        "INSERT INTO dozimetre ("
        "id, personel_id, rapor_no, yil, periyot, periyot_adi, dozimetre_no, tur, bolge, hp10, hp007, durum"
        ") VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            f"id{periyot}{int(hp10 * 1000)}",
            pid,
            rapor_no,
            2026,
            periyot,
            f"{periyot}. Periyot",
            f"DZM-{periyot}",
            "TLD",
            "Govde",
            hp10,
            hp007,
            "",
        ),
    )


def test_tum_olcumler_durum_hesaplar(db, personel_id):
    _ekle(db, personel_id, hp10=1.2, hp007=0.8, periyot=1)
    _ekle(db, personel_id, hp10=2.5, hp007=1.1, periyot=2)
    _ekle(db, personel_id, hp10=5.1, hp007=2.0, periyot=3)

    svc = DozimetreService(db)
    rows = svc.tum_olcumler(yil=2026)
    durumlar = {r["periyot"]: r["durum"] for r in rows}

    assert durumlar[1] == "Normal"
    assert durumlar[2] == "Uyari"
    assert durumlar[3] == "Tehlike"


def test_istatistikler_hesaplar(db, personel_id):
    _ekle(db, personel_id, hp10=1.2, hp007=0.8, periyot=1, rapor_no="R-1")
    _ekle(db, personel_id, hp10=2.5, hp007=1.0, periyot=2, rapor_no="R-1")
    _ekle(db, personel_id, hp10=5.0, hp007=1.5, periyot=3, rapor_no="R-2")

    svc = DozimetreService(db)
    stats = svc.istatistikler(svc.tum_olcumler(yil=2026))

    assert stats["toplam"] == 3
    assert stats["personel"] == 1
    assert stats["rapor"] == 2
    assert stats["uyari"] == 1
    assert stats["tehlike"] == 1
    assert float(stats["max_hp10"]) == 5.0


def test_olcum_ekle_ve_mukerrer_atla(db, personel_id):
    svc = DozimetreService(db)

    ok1 = svc.olcum_ekle(
        {
            "personel_id": personel_id,
            "rapor_no": "R-IMP-1",
            "yil": 2026,
            "periyot": 1,
            "periyot_adi": "1. Periyot",
            "dozimetre_no": "DZM-100",
            "tur": "RADAT",
            "bolge": "Govde",
            "hp10": 1.1,
            "hp007": 0.8,
            "durum": "Sinirin Altinda",
        }
    )
    ok2 = svc.olcum_ekle(
        {
            "personel_id": personel_id,
            "rapor_no": "R-IMP-1",
            "yil": 2026,
            "periyot": 1,
            "periyot_adi": "1. Periyot",
            "dozimetre_no": "DZM-100",
            "tur": "RADAT",
            "bolge": "Govde",
            "hp10": 1.1,
            "hp007": 0.8,
            "durum": "Sinirin Altinda",
        }
    )

    assert ok1 is True
    assert ok2 is False
    assert len(svc.rapor_olcumleri("R-IMP-1")) == 1
