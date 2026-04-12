# -*- coding: utf-8 -*-
"""tests/test_izin_service.py"""
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import Database
from app.db.migrations import run as migrate
from app.exceptions import LimitHatasi
from app.services.izin_service import IzinService
from app.services.personel_service import PersonelService


@pytest.fixture
def db(tmp_path):
    d = Database(tmp_path / "test.db")
    migrate(d)
    yield d
    d.close()


@pytest.fixture
def izin_svc(db):
    return IzinService(db)


@pytest.fixture
def personel_svc(db):
    return PersonelService(db)


def _gorev_yeri_id(db: Database, sua_hakki: int) -> str:
    gid = db.fetchval(
        "SELECT id FROM gorev_yeri WHERE sua_hakki = ? ORDER BY ad LIMIT 1",
        (sua_hakki,),
    )
    assert gid
    return str(gid)


def test_yillik_hak_hesapla_kademe(izin_svc):
    assert izin_svc.yillik_hak_hesapla("2026-01-02", today=date(2026, 12, 31)) == 0.0
    assert izin_svc.yillik_hak_hesapla("2020-01-01", today=date(2026, 12, 31)) == 20.0
    assert izin_svc.yillik_hak_hesapla("2010-01-01", today=date(2026, 12, 31)) == 30.0


def test_yillik_limit_asiminda_hata(izin_svc, personel_svc):
    personel_id = personel_svc.ekle(
        {
            "tc_kimlik": "10000000146",
            "ad": "Ali",
            "soyad": "Kaya",
            "memuriyet_baslama": "2020-01-01",
        }
    )
    yil = date.today().year
    izin_svc.ekle(
        {
            "personel_id": personel_id,
            "tur": "Yıllık İzin",
            "baslama": f"{yil}-01-10",
            "gun": 18,
        }
    )

    with pytest.raises(LimitHatasi):
        izin_svc.validate_izin_sure_limit(
            personel_id,
            "Yıllık İzin",
            3,
            f"{yil}-03-01",
        )


def test_ucretsiz_izin_personeli_pasif_yapar(izin_svc, personel_svc, db):
    personel_id = personel_svc.ekle(
        {
            "tc_kimlik": "14522068356",
            "ad": "Veli",
            "soyad": "Ak",
            "gorev_yeri_id": _gorev_yeri_id(db, 0),
            "memuriyet_baslama": "2018-01-01",
        }
    )

    izin_svc.ekle(
        {
            "personel_id": personel_id,
            "tur": "Ücretsiz İzin",
            "baslama": f"{date.today().year}-04-01",
            "gun": 5,
        }
    )

    guncel = personel_svc.getir(personel_id)
    assert guncel["durum"] == "pasif"


def test_sua_izni_hakki_olmayan_personelde_hata(izin_svc, personel_svc, db):
    personel_id = personel_svc.ekle(
        {
            "tc_kimlik": "10000000146",
            "ad": "Ayse",
            "soyad": "Demir",
            "gorev_yeri_id": _gorev_yeri_id(db, 0),
            "memuriyet_baslama": "2016-01-01",
        }
    )

    with pytest.raises(LimitHatasi):
        izin_svc.validate_izin_sure_limit(
            personel_id,
            "Şua İzni",
            1,
            f"{date.today().year}-05-01",
        )
