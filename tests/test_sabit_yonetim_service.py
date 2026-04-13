# -*- coding: utf-8 -*-
"""tests/test_sabit_yonetim_service.py"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import Database
from app.db.migrations import run as migrate
from app.db.seed import seed_all
from app.services.sabit_yonetim_service import SabitYonetimService


@pytest.fixture
def db(tmp_path):
    d = Database(tmp_path / "test.db")
    migrate(d)
    seed_all(d)
    yield d
    d.close()


def test_lookup_ekle_guncelle_aktiflik(db):
    svc = SabitYonetimService(db)

    kid = svc.lookup_ekle("izin_tur", "Test Izin Turu", siralama=999, aktif=True)
    rows = svc.lookup_listele("izin_tur", include_pasif=True)
    hedef = next(r for r in rows if r["id"] == kid)
    assert hedef["deger"] == "Test Izin Turu"
    assert int(hedef["aktif"]) == 1

    svc.lookup_guncelle(kid, "Test Izin Turu Guncel", siralama=1000, aktif=False)
    rows = svc.lookup_listele("izin_tur", include_pasif=True)
    hedef = next(r for r in rows if r["id"] == kid)
    assert hedef["deger"] == "Test Izin Turu Guncel"
    assert int(hedef["siralama"]) == 1000
    assert int(hedef["aktif"]) == 0

    svc.lookup_aktiflik_degistir(kid, True)
    rows = svc.lookup_listele("izin_tur", include_pasif=True)
    hedef = next(r for r in rows if r["id"] == kid)
    assert int(hedef["aktif"]) == 1


def test_gorev_yeri_ekle_guncelle_aktiflik(db):
    svc = SabitYonetimService(db)

    gid = svc.gorev_yeri_ekle("Test Birim", "TB", sua_hakki=False, aktif=True)
    rows = svc.gorev_yeri_listele(include_pasif=True)
    hedef = next(r for r in rows if r["id"] == gid)
    assert hedef["ad"] == "Test Birim"
    assert int(hedef["aktif"]) == 1

    svc.gorev_yeri_guncelle(gid, "Test Birim Guncel", "TBG", sua_hakki=True, aktif=False)
    rows = svc.gorev_yeri_listele(include_pasif=True)
    hedef = next(r for r in rows if r["id"] == gid)
    assert hedef["ad"] == "Test Birim Guncel"
    assert hedef["kisaltma"] == "TBG"
    assert int(hedef["sua_hakki"]) == 1
    assert int(hedef["aktif"]) == 0

    svc.gorev_yeri_aktiflik_degistir(gid, True)
    rows = svc.gorev_yeri_listele(include_pasif=True)
    hedef = next(r for r in rows if r["id"] == gid)
    assert int(hedef["aktif"]) == 1
