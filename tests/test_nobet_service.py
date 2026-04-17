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
            "max_ardisik_nobet": 2,
            "manuel_limit_asimina_izin": False,
        },
    )

    kural = svc.birim_kural_getir(birim_id)
    assert float(kural.get("max_devreden_saat") or 0) == 12
    assert str(kural.get("arefe_baslangic_saat") or "") == "13:00"
    assert int(kural.get("max_ardisik_nobet") or 0) == 2
    assert int(kural.get("manuel_limit_asimina_izin", 1)) == 0


def test_birim_kural_kaydet_max_ardisik_1den_kucuk_olamaz(db):
    svc = NobetService(db)
    svc.birimleri_gorev_yerinden_esitle()
    birim_id = str(svc.birimler_listele()[0].get("id") or "")

    with pytest.raises(DogrulamaHatasi):
        svc.birim_kural_kaydet(
            birim_id,
            {
                "min_dinlenme_saat": 12,
                "resmi_tatil_calisma": True,
                "dini_tatil_calisma": True,
                "arefe_baslangic_saat": "13:00",
                "max_fazla_mesai_saat": 0,
                "tolerans_saat": 7,
                "max_devreden_saat": 12,
                "max_ardisik_nobet": 0,
                "manuel_limit_asimina_izin": False,
            },
        )


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


def _test_birim_ve_personel_hazirla(db):
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
        ("p-hedef-1", "99999999992", "Hedef", "Personel", str(gorev_yeri.get("id") or ""), "aktif"),
    )
    svc.birim_personellerini_esitle(birim_id)
    return svc, birim_id, "p-hedef-1"


def test_aylik_calisma_gunu_ve_standart_hedef(db):
    svc, birim_id, pid = _test_birim_ve_personel_hazirla(db)

    # 2026-01: hafta ici 22 gun, 1 Ocak resmi tatil -> 21 gun
    hesap = svc.personel_aylik_hedef_ve_devir_hesapla(birim_id, pid, 2026, 1, gerceklesen_saat=0)
    assert float(hesap.get("calisma_gunu") or 0) == 21.0
    assert float(hesap.get("standart_hedef_saat") or 0) == 147.0
    assert float(hesap.get("kanuni_hedef_saat") or 0) == 147.0


def test_kanuni_mesai_duzenleme_hedef_hesabi(db):
    svc, birim_id, pid = _test_birim_ve_personel_hazirla(db)

    svc.personel_kanuni_mesai_ekle(
        birim_id=birim_id,
        personel_id=pid,
        baslangic_tarih="2026-01-01",
        bitis_tarih="2026-01-31",
        duzenleme_tipi="oran",
        deger=10,
        aciklama="sendika",
    )
    svc.personel_kanuni_mesai_ekle(
        birim_id=birim_id,
        personel_id=pid,
        baslangic_tarih="2026-01-01",
        bitis_tarih="2026-01-31",
        duzenleme_tipi="saat_dusum",
        deger=8,
        aciklama="emzirme",
    )

    hesap = svc.personel_aylik_hedef_ve_devir_hesapla(birim_id, pid, 2026, 1, gerceklesen_saat=0)
    # 147 * 0.9 - 8 = 124.3
    assert float(hesap.get("kanuni_hedef_saat") or 0) == 124.3


def test_kanuni_mesai_sut_0_6_gunluk_dusum_hesabi(db):
    svc, birim_id, pid = _test_birim_ve_personel_hazirla(db)

    svc.personel_kanuni_mesai_ekle(
        birim_id=birim_id,
        personel_id=pid,
        baslangic_tarih="2026-01-01",
        bitis_tarih="2026-01-31",
        duzenleme_tipi="sut_0_6",
        deger=0,
        aciklama="sut izni 0-6 ay",
    )

    hesap = svc.personel_aylik_hedef_ve_devir_hesapla(birim_id, pid, 2026, 1, gerceklesen_saat=0)
    # 2026-01 calisma gunu 21 -> 147 - (21 * 3) = 84
    assert float(hesap.get("kanuni_hedef_saat") or 0) == 84.0


def test_kanuni_mesai_yarim_zamanli_gunluk_dusum_hesabi(db):
    svc, birim_id, pid = _test_birim_ve_personel_hazirla(db)

    svc.personel_kanuni_mesai_ekle(
        birim_id=birim_id,
        personel_id=pid,
        baslangic_tarih="2026-01-01",
        bitis_tarih="2026-01-31",
        duzenleme_tipi="yarim_zamanli",
        deger=0,
        aciklama="yarim zamanli calisma",
    )

    hesap = svc.personel_aylik_hedef_ve_devir_hesapla(birim_id, pid, 2026, 1, gerceklesen_saat=0)
    # 147 - (21 * 3.5) = 73.5
    assert float(hesap.get("kanuni_hedef_saat") or 0) == 73.5


def test_devir_hesabi_ve_clip_12(db):
    svc, birim_id, pid = _test_birim_ve_personel_hazirla(db)

    svc.personel_aylik_devir_kaydet(birim_id, pid, 2025, 12, 10)
    hesap = svc.personel_aylik_hedef_ve_devir_hesapla(birim_id, pid, 2026, 1, gerceklesen_saat=200)

    assert float(hesap.get("onceki_devir_saat") or 0) == 10.0
    # devirli hedef 157, gerceklesen 200 => -43, clip -> -12
    assert float(hesap.get("yeni_devir_saat") or 0) == -12.0


def test_taslak_plan_olustur_ve_doldur_satir_uretir(db):
    svc = NobetService(db)
    svc.birimleri_gorev_yerinden_esitle()
    birim = svc.birimler_listele()[0]
    birim_id = str(birim.get("id") or "")

    gorev_yeri = db.fetchone(
        "SELECT id FROM gorev_yeri WHERE ad = ? LIMIT 1",
        (str(birim.get("ad") or ""),),
    )
    assert gorev_yeri is not None

    # Iki aktif personel ekle
    db.execute(
        "INSERT INTO personel (id, tc_kimlik, ad, soyad, gorev_yeri_id, durum) VALUES (?,?,?,?,?,?)",
        ("p-plan-1", "99999999993", "Plan", "Bir", str(gorev_yeri.get("id") or ""), "aktif"),
    )
    db.execute(
        "INSERT INTO personel (id, tc_kimlik, ad, soyad, gorev_yeri_id, durum) VALUES (?,?,?,?,?,?)",
        ("p-plan-2", "99999999994", "Plan", "Iki", str(gorev_yeri.get("id") or ""), "aktif"),
    )
    svc.birim_personellerini_esitle(birim_id)

    # Birime tek vardiya ata (max_personel=1)
    sablon = svc.sablon_listele()[0]
    svc.sablon_birime_ata(birim_id, str(sablon.get("id") or ""), max_personel=1)

    sonuc = svc.taslak_plan_olustur_ve_doldur(birim_id, 2026, 2, "otomatik")
    assert str(sonuc.get("plan_id") or "")
    assert int(sonuc.get("satir_sayisi") or 0) > 0

    plan_id = str(sonuc.get("plan_id") or "")
    satir_say = int(db.fetchval("SELECT COUNT(*) FROM nb_satir WHERE plan_id = ?", (plan_id,)) or 0)
    assert satir_say == int(sonuc.get("satir_sayisi") or 0)

    # Devir kayitlari yazilmis olmali
    devir_say = int(
        db.fetchval(
            "SELECT COUNT(*) FROM nb_personel_devir WHERE birim_id = ? AND yil = ? AND ay = ?",
            (birim_id, 2026, 2),
        )
        or 0
    )
    assert devir_say >= 2


def test_taslak_plan_arefe_gununde_sureyi_13ten_baslatir(db):
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
        ("p-arefe-1", "99999999995", "Arefe", "Personel", str(gorev_yeri.get("id") or ""), "aktif"),
    )
    svc.birim_personellerini_esitle(birim_id)

    db.execute(
        "INSERT OR REPLACE INTO tatil (tarih, ad, tur, yarim_gun) VALUES (?,?,?,?)",
        ("2026-02-16", "Arefe", "dini", 1),
    )
    svc.vardiya_ekle(birim_id, "Arefe Gunduz", 8.0, "08:00", "16:00", max_personel=1)

    sonuc = svc.taslak_plan_olustur_ve_doldur(birim_id, 2026, 2, "arefe")
    plan_id = str(sonuc.get("plan_id") or "")
    satir = db.fetchone(
        "SELECT saat_suresi FROM nb_satir WHERE plan_id = ? AND tarih = ? LIMIT 1",
        (plan_id, "2026-02-16"),
    )
    assert satir is not None
    assert float(satir.get("saat_suresi") or 0) == 3.0


def test_taslak_plan_min_dinlenme_kuralinda_ertesi_gun_bosluk_birakir(db):
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
        ("p-rest-1", "99999999996", "Dinlenme", "Personel", str(gorev_yeri.get("id") or ""), "aktif"),
    )
    svc.birim_personellerini_esitle(birim_id)
    svc.birim_kural_kaydet(
        birim_id,
        {
            "min_dinlenme_saat": 12,
            "resmi_tatil_calisma": True,
            "dini_tatil_calisma": True,
            "arefe_baslangic_saat": "13:00",
            "max_fazla_mesai_saat": 0,
            "tolerans_saat": 7,
            "max_devreden_saat": 12,
            "manuel_limit_asimina_izin": False,
        },
    )
    svc.vardiya_ekle(birim_id, "Uzun Gece", 16.0, "20:00", "12:00", max_personel=1)

    sonuc = svc.taslak_plan_olustur_ve_doldur(birim_id, 2026, 2, "dinlenme")
    assert int(sonuc.get("satir_sayisi") or 0) == 14
    assert any(str(x.get("neden") or "") == "min_dinlenme" for x in (sonuc.get("eksik_atama") or []))


def test_taslak_plan_max_ardisik_limitinde_gun_asiri_yazar(db):
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
        ("p-ardisik-1", "99999999997", "Ardisik", "Personel", str(gorev_yeri.get("id") or ""), "aktif"),
    )
    svc.birim_personellerini_esitle(birim_id)
    svc.birim_kural_kaydet(
        birim_id,
        {
            "min_dinlenme_saat": 0,
            "resmi_tatil_calisma": True,
            "dini_tatil_calisma": True,
            "arefe_baslangic_saat": "13:00",
            "max_fazla_mesai_saat": 0,
            "tolerans_saat": 7,
            "max_devreden_saat": 12,
            "max_ardisik_nobet": 1,
            "manuel_limit_asimina_izin": False,
        },
    )
    svc.vardiya_ekle(birim_id, "Gunduz", 8.0, "08:00", "16:00", max_personel=1)

    sonuc = svc.taslak_plan_olustur_ve_doldur(birim_id, 2026, 2, "ardisik")
    assert int(sonuc.get("satir_sayisi") or 0) == 14
    assert any(str(x.get("neden") or "") == "ardisik_limit" for x in (sonuc.get("eksik_atama") or []))


def test_plan_personel_aylik_nobet_ozeti_dolu_doner(db):
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
        ("p-ozet-1", "99999999998", "Ozet", "Bir", str(gorev_yeri.get("id") or ""), "aktif"),
    )
    db.execute(
        "INSERT INTO personel (id, tc_kimlik, ad, soyad, gorev_yeri_id, durum) VALUES (?,?,?,?,?,?)",
        ("p-ozet-2", "99999999989", "Ozet", "Iki", str(gorev_yeri.get("id") or ""), "aktif"),
    )
    svc.birim_personellerini_esitle(birim_id)

    sablon = svc.sablon_listele()[0]
    svc.sablon_birime_ata(birim_id, str(sablon.get("id") or ""), max_personel=1)

    sonuc = svc.taslak_plan_olustur_ve_doldur(birim_id, 2026, 3, "ozet")
    plan_id = str(sonuc.get("plan_id") or "")

    ozet = svc.plan_personel_aylik_nobet_ozeti(plan_id)
    assert ozet
    assert any(str(r.get("ad_soyad") or "").startswith("Ozet") for r in ozet)
    assert all(str(r.get("nobet_tarihleri") or "") for r in ozet)


def test_plan_gunluk_vardiya_durumu_bos_ve_dolu_slotlari_doner(db):
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
        ("p-detay-1", "99999999988", "Detay", "Bir", str(gorev_yeri.get("id") or ""), "aktif"),
    )
    svc.birim_personellerini_esitle(birim_id)

    sablon = svc.sablon_listele()[0]
    svc.sablon_birime_ata(birim_id, str(sablon.get("id") or ""), max_personel=2)

    sonuc = svc.taslak_plan_olustur_ve_doldur(birim_id, 2026, 4, "detay")
    plan_id = str(sonuc.get("plan_id") or "")

    detay = svc.plan_gunluk_vardiya_durumu(plan_id, birim_id, 2026, 4)
    assert detay
    assert any(str(r.get("durum") or "") == "Dolu" for r in detay)
    assert any(str(r.get("durum") or "") == "Bos" for r in detay)
