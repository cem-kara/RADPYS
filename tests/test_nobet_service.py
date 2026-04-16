# -*- coding: utf-8 -*-
"""tests/test_nobet_service.py"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import Database
from app.db.migrations import run as migrate
from app.db.seed import seed_all
from app.exceptions import DogrulamaHatasi, KayitZatenVar
from app.services.nobet_service import NobetService


@pytest.fixture
def db(tmp_path):
    d = Database(tmp_path / "test.db")
    migrate(d)
    seed_all(d)
    yield d
    d.close()


def test_birimleri_gorev_yerinden_esitle_idempotent(db):
    svc = NobetService(db)

    ilk = svc.birimleri_gorev_yerinden_esitle()
    assert ilk > 0

    ikinci = svc.birimleri_gorev_yerinden_esitle()
    assert ikinci == 0

    birimler = svc.birimler_listele()
    gorev_yeri_say = db.fetchval("SELECT COUNT(*) FROM gorev_yeri WHERE COALESCE(aktif, 1) = 1") or 0
    assert len(birimler) == int(gorev_yeri_say)


def test_taslak_plan_olustur_ve_listele(db):
    svc = NobetService(db)
    svc.birimleri_gorev_yerinden_esitle()
    birim = svc.birimler_listele()[0]

    pid = svc.taslak_plan_olustur(str(birim.get("id") or ""), 2026, 5, "Ilk taslak")
    assert pid

    plans = svc.planlari_listele(yil=2026, ay=5)
    assert len(plans) == 1
    assert str(plans[0].get("birim_id") or "") == str(birim.get("id") or "")
    assert str(plans[0].get("durum") or "") == "taslak"


def test_taslak_plan_olustur_mukerrer_hata(db):
    svc = NobetService(db)
    svc.birimleri_gorev_yerinden_esitle()
    birim = svc.birimler_listele()[0]

    svc.taslak_plan_olustur(str(birim.get("id") or ""), 2026, 6)
    with pytest.raises(KayitZatenVar):
        svc.taslak_plan_olustur(str(birim.get("id") or ""), 2026, 6)


def test_taslak_plan_olustur_gecersiz_ay_hata(db):
    svc = NobetService(db)
    svc.birimleri_gorev_yerinden_esitle()
    birim = svc.birimler_listele()[0]

    with pytest.raises(DogrulamaHatasi):
        svc.taslak_plan_olustur(str(birim.get("id") or ""), 2026, 13)


def test_birim_kural_kaydet_ve_getir(db):
    svc = NobetService(db)
    svc.birimleri_gorev_yerinden_esitle()
    birim_id = str(svc.birimler_listele()[0].get("id") or "")

    svc.birim_kural_kaydet(
        birim_id,
        {
            "min_dinlenme_saat": 12,
            "resmi_tatil_calisma": True,
            "dini_tatil_calisma": True,
            "arefe_baslangic_saat": "13:00",
            "max_fazla_mesai_saat": 16,
            "tolerans_saat": 7,
            "max_devreden_saat": 12,
            "manuel_limit_asimina_izin": False,
        },
    )

    kural = svc.birim_kural_getir(birim_id)
    assert float(kural.get("max_devreden_saat") or 0) == 12
    assert str(kural.get("arefe_baslangic_saat") or "") == "13:00"
    assert int(kural.get("manuel_limit_asimina_izin", 1)) == 0


def test_personel_kosul_kaydet_ve_listele(db):
    svc = NobetService(db)
    svc.birimleri_gorev_yerinden_esitle()
    birim = svc.birimler_listele()[0]
    birim_id = str(birim.get("id") or "")

    gorev_yeri = db.fetchone(
        "SELECT id FROM gorev_yeri WHERE ad = ? LIMIT 1",
        (str(birim.get("ad") or ""),),
    )
    assert gorev_yeri is not None

    db.execute(
        "INSERT INTO personel (id, tc_kimlik, ad, soyad, gorev_yeri_id, durum) VALUES (?,?,?,?,?,?)",
        ("p-test-nobet-1", "99999999991", "Test", "Personel", str(gorev_yeri.get("id") or ""), "aktif"),
    )

    _ = svc.birim_personellerini_esitle(birim_id)
    rows = svc.birim_personel_kosullari_listele(birim_id)
    assert rows

    pid = str(rows[0].get("personel_id") or "")
    svc.personel_kosul_kaydet(
        birim_id,
        pid,
        {
            "ister_24_saat": True,
            "mesai_istemiyor": True,
            "max_fazla_mesai_saat": 0,
            "tolerans_saat": 7,
            "max_devreden_saat": 12,
        },
    )

    guncel = svc.birim_personel_kosullari_listele(birim_id)
    secili = next((r for r in guncel if str(r.get("personel_id") or "") == pid), None)
    assert secili is not None
    assert int(secili.get("ister_24_saat") or 0) == 1
    assert int(secili.get("mesai_istemiyor") or 0) == 1


def test_sablon_ekle_ve_listele(db):
    svc = NobetService(db)
    # Seed sablonlari zaten migration'dan geliyor
    mevcut = svc.sablon_listele()
    assert mevcut  # en az 5 seed sablon mevcut

    sid = svc.sablon_ekle("Test Gunduz", "07:00", "15:00", 8.0)
    assert sid

    guncel = svc.sablon_listele()
    assert any(str(s.get("ad") or "") == "Test Gunduz" for s in guncel)


def test_sablon_pasife_al(db):
    svc = NobetService(db)
    sid = svc.sablon_ekle("Pasif Test", "09:00", "17:00", 8.0)
    svc.sablon_pasife_al(sid)
    aktifler = svc.sablon_listele(aktif_only=True)
    assert not any(str(s.get("id") or "") == sid for s in aktifler)


def test_sablon_birime_ata(db):
    svc = NobetService(db)
    svc.birimleri_gorev_yerinden_esitle()
    birim_id = str(svc.birimler_listele()[0].get("id") or "")
    sablon = svc.sablon_listele()[0]
    sablon_id = str(sablon.get("id") or "")

    vid = svc.sablon_birime_ata(birim_id, sablon_id, max_personel=3)
    assert vid

    vardiyalar = svc.vardiya_listele(birim_id)
    atanan = next((v for v in vardiyalar if str(v.get("sablon_id") or "") == sablon_id), None)
    assert atanan is not None
    assert int(atanan.get("max_personel") or 0) == 3


def test_sablon_birime_ata_idempotent_max_gunceller(db):
    svc = NobetService(db)
    svc.birimleri_gorev_yerinden_esitle()
    birim_id = str(svc.birimler_listele()[0].get("id") or "")
    sablon_id = str(svc.sablon_listele()[0].get("id") or "")

    svc.sablon_birime_ata(birim_id, sablon_id, max_personel=2)
    svc.sablon_birime_ata(birim_id, sablon_id, max_personel=5)

    vardiyalar = svc.vardiya_listele(birim_id)
    atanan = next((v for v in vardiyalar if str(v.get("sablon_id") or "") == sablon_id), None)
    assert atanan is not None
    assert int(atanan.get("max_personel") or 0) == 5
