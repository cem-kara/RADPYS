# -*- coding: utf-8 -*-
"""tests/test_tatil_yonetim_service.py"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import Database
from app.db.migrations import run as migrate
from app.db.seed import seed_all
from app.exceptions import DogrulamaHatasi, KayitBulunamadi, KayitZatenVar
from app.services.tatil_yonetim_service import TatilYonetimService


@pytest.fixture
def db(tmp_path):
    d = Database(tmp_path / "test.db")
    migrate(d)
    seed_all(d)
    yield d
    d.close()


def test_tatil_ekle_ve_listele(db):
    svc = TatilYonetimService(db)
    svc.ekle("2030-01-01", "Yilbasi 2030", "resmi", yarim_gun=False)
    rows = svc.listele(yil=2030)
    assert any(
        r["tarih"] == "2030-01-01"
        and r["ad"] == "Yilbasi 2030"
        and int(r.get("yarim_gun") or 0) == 0
        for r in rows
    )


def test_tatil_tur_filtresi(db):
    svc = TatilYonetimService(db)
    svc.ekle("2030-04-23", "Ulusal Egemenlik 2030", "resmi")
    svc.ekle("2030-03-30", "Ramazan Bayrami 2030", "dini")

    resmi = svc.listele(tur="resmi")
    dini = svc.listele(tur="dini")

    assert any(r["tarih"] == "2030-04-23" for r in resmi)
    assert not any(r["tarih"] == "2030-03-30" for r in resmi)
    assert any(r["tarih"] == "2030-03-30" for r in dini)


def test_tatil_guncelle(db):
    svc = TatilYonetimService(db)
    svc.ekle("2030-05-01", "Emek 2030", "resmi")
    svc.guncelle("2030-05-01", "Emek ve Dayanisma Gunu", "resmi", yarim_gun=True)
    rows = svc.listele(yil=2030)
    hedef = next(r for r in rows if r["tarih"] == "2030-05-01")
    assert hedef["ad"] == "Emek ve Dayanisma Gunu"
    assert int(hedef.get("yarim_gun") or 0) == 1


def test_tatil_yarim_gun_kaydi(db):
    svc = TatilYonetimService(db)
    svc.ekle("2030-12-31", "Yilbasi Arefesi", "resmi", yarim_gun=True)
    rows = svc.listele(yil=2030)
    hedef = next(r for r in rows if r["tarih"] == "2030-12-31")
    assert int(hedef.get("yarim_gun") or 0) == 1


def test_tatil_sil(db):
    svc = TatilYonetimService(db)
    svc.ekle("2030-08-30", "Zafer Bayrami 2030", "resmi")
    svc.sil("2030-08-30")
    rows = svc.listele(yil=2030)
    assert not any(r["tarih"] == "2030-08-30" for r in rows)


def test_ayni_tarih_iki_kez_eklenemez(db):
    svc = TatilYonetimService(db)
    svc.ekle("2030-10-29", "Cumhuriyet Bayrami 2030", "resmi")
    with pytest.raises(KayitZatenVar):
        svc.ekle("2030-10-29", "Baska Ad", "dini")


def test_gecersiz_tarih_formati_reddedilir(db):
    svc = TatilYonetimService(db)
    with pytest.raises(DogrulamaHatasi):
        svc.ekle("29-10-2025", "Yanlis Format", "resmi")


def test_gecersiz_tur_reddedilir(db):
    svc = TatilYonetimService(db)
    with pytest.raises(DogrulamaHatasi):
        svc.ekle("2025-11-10", "Ataturk", "ulusal")


def test_olmayan_kayit_guncellenemez(db):
    svc = TatilYonetimService(db)
    with pytest.raises(KayitBulunamadi):
        svc.guncelle("2099-01-01", "Hayali Tatil", "resmi")


def test_mevcut_yillar(db):
    svc = TatilYonetimService(db)
    svc.ekle("2030-01-01", "Yilbasi 2030", "resmi")
    svc.ekle("2031-01-01", "Yilbasi 2031", "resmi")
    yillar = svc.mevcut_yillar()
    assert 2030 in yillar
    assert 2031 in yillar
    assert yillar == sorted(yillar, reverse=True)
