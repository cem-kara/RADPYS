# -*- coding: utf-8 -*-
"""tests/test_personel_service.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.db.database import Database
from app.db.migrations import run as migrate
from app.services.personel_service import PersonelService
from app.exceptions import (
    CakismaHatasi,
    KayitBulunamadi, KayitZatenVar,
    PasifPersonelHatasi,
    YetkiHatasi,
)
from app.exceptions import TCHatasi


# ── Fixture ───────────────────────────────────────────────────────

@pytest.fixture
def db(tmp_path):
    d = Database(tmp_path / "test.db")
    migrate(d)
    yield d
    d.close()

@pytest.fixture
def svc(db):
    return PersonelService(db)

@pytest.fixture
def ali_id(svc):
    """Temel bir personel kaydı döner."""
    return svc.ekle({
        "tc_kimlik": "10000000146",
        "ad":        "Ali",
        "soyad":     "Kaya",
    })


# ── Ekle ─────────────────────────────────────────────────────────

class TestEkle:

    def test_basarili(self, svc):
        pid = svc.ekle({
            "tc_kimlik": "10000000146",
            "ad": "Ali", "soyad": "Kaya",
        })
        assert pid and len(pid) == 32   # UUID hex

    def test_donus_id_db_de_var(self, svc):
        pid = svc.ekle({"tc_kimlik": "10000000146", "ad": "Ali", "soyad": "Kaya"})
        p = svc.getir(pid)
        assert p["ad"] == "Ali"
        assert p["soyad"] == "Kaya"
        assert p["tc_kimlik"] == "10000000146"
        assert p["durum"] == "aktif"

    def test_ayni_tc_iki_kez_eklenemez(self, svc, ali_id):
        with pytest.raises(KayitZatenVar):
            svc.ekle({"tc_kimlik": "10000000146", "ad": "Veli", "soyad": "Kaya"})

    def test_gecersiz_tc(self, svc):
        with pytest.raises(TCHatasi):
            svc.ekle({"tc_kimlik": "12345678900", "ad": "X", "soyad": "Y"})

    def test_bos_ad(self, svc):
        from app.exceptions import DogrulamaHatasi
        with pytest.raises(DogrulamaHatasi):
            svc.ekle({"tc_kimlik": "10000000146", "ad": "", "soyad": "Kaya"})

    def test_bos_soyad(self, svc):
        from app.exceptions import DogrulamaHatasi
        with pytest.raises(DogrulamaHatasi):
            svc.ekle({"tc_kimlik": "10000000146", "ad": "Ali", "soyad": ""})

    def test_tum_alanlar(self, svc):
        pid = svc.ekle({
            "tc_kimlik":         "10000000146",
            "ad":                "Ali",
            "soyad":             "Kaya",
            "dogum_tarihi":      "1985-06-15",
            "hizmet_sinifi":     "Radyasyon Görevlisi",
            "kadro_unvani":      "Teknisyen",
            "memuriyet_baslama": "2010-09-01",
            "telefon":           "05551234567",
            "e_posta":           "ali@test.com",
        })
        p = svc.getir(pid)
        assert p["dogum_tarihi"]      == "1985-06-15"
        assert p["hizmet_sinifi"]     == "Radyasyon Görevlisi"
        assert p["memuriyet_baslama"] == "2010-09-01"


# ── Getir ─────────────────────────────────────────────────────────

class TestGetir:

    def test_id_ile_getir(self, svc, ali_id):
        p = svc.getir(ali_id)
        assert p["id"] == ali_id

    def test_olmayan_id(self, svc):
        with pytest.raises(KayitBulunamadi):
            svc.getir("olmayan-id")

    def test_tc_ile_getir(self, svc, ali_id):
        p = svc.tc_ile_getir("10000000146")
        assert p["id"] == ali_id

    def test_olmayan_tc(self, svc):
        with pytest.raises(KayitBulunamadi):
            svc.tc_ile_getir("10000000146")


# ── Listele ───────────────────────────────────────────────────────

class TestListele:

    def test_bos_liste(self, svc):
        assert svc.listele() == []

    def test_iki_personel(self, svc):
        svc.ekle({"tc_kimlik": "10000000146", "ad": "Ali",  "soyad": "Kaya"})
        svc.ekle({"tc_kimlik": "14522068356", "ad": "Veli", "soyad": "Ak"})
        assert len(svc.listele()) == 2

    def test_soyad_sirasi(self, svc):
        svc.ekle({"tc_kimlik": "10000000146", "ad": "Ali",  "soyad": "Zorlu"})
        svc.ekle({"tc_kimlik": "14522068356", "ad": "Veli", "soyad": "Ak"})
        liste = svc.listele()
        assert liste[0]["soyad"] == "Ak"
        assert liste[1]["soyad"] == "Zorlu"

    def test_aktif_only_filtresi(self, svc):
        pid = svc.ekle({"tc_kimlik": "10000000146", "ad": "Ali", "soyad": "Kaya"})
        svc.pasife_al(pid, "2026-01-01")
        assert len(svc.listele(aktif_only=True))  == 0
        assert len(svc.listele(aktif_only=False)) == 1


# ── Güncelle ──────────────────────────────────────────────────────

class TestGuncelle:

    def test_alan_guncelleme(self, svc, ali_id):
        svc.guncelle(ali_id, {"telefon": "05559876543"})
        p = svc.getir(ali_id)
        assert p["telefon"] == "05559876543"

    def test_tc_degistirilemez(self, svc, ali_id):
        svc.guncelle(ali_id, {"tc_kimlik": "99999999999"})
        p = svc.getir(ali_id)
        assert p["tc_kimlik"] == "10000000146"   # değişmedi

    def test_olmayan_personel(self, svc):
        with pytest.raises(KayitBulunamadi):
            svc.guncelle("olmayan", {"ad": "Yeni"})


# ── Pasife Al ─────────────────────────────────────────────────────

class TestPasifeAl:

    def test_pasif(self, svc, ali_id):
        svc.pasife_al(ali_id, "2026-01-01", "Emeklilik")
        p = svc.getir(ali_id)
        assert p["durum"]          == "ayrildi"
        assert p["ayrilik_tarihi"] == "2026-01-01"
        assert p["ayrilik_nedeni"] == "Emeklilik"

    def test_zaten_ayrilmis(self, svc, ali_id):
        svc.pasife_al(ali_id, "2026-01-01")
        with pytest.raises(PasifPersonelHatasi):
            svc.pasife_al(ali_id, "2026-02-01")

    def test_gecersiz_tarih(self, svc, ali_id):
        from app.exceptions import DogrulamaHatasi
        with pytest.raises(DogrulamaHatasi):
            svc.pasife_al(ali_id, "gecersiz-tarih")


# ── Sayı ──────────────────────────────────────────────────────────

class TestSay:

    def test_bos(self, svc):
        assert svc.say() == 0

    def test_iki_kayit(self, svc):
        svc.ekle({"tc_kimlik": "10000000146", "ad": "A", "soyad": "B"})
        svc.ekle({"tc_kimlik": "14522068356", "ad": "C", "soyad": "D"})
        assert svc.say() == 2

    def test_duruma_gore(self, svc):
        pid = svc.ekle({"tc_kimlik": "10000000146", "ad": "A", "soyad": "B"})
        svc.pasife_al(pid, "2026-01-01")
        assert svc.say("aktif")   == 0
        assert svc.say("ayrildi") == 1


# ── Dropdown Verileri ─────────────────────────────────────────────

class TestDropdown:

    def test_hizmet_siniflari_dolu(self, svc):
        liste = svc.hizmet_siniflari()
        assert len(liste) > 0
        assert "Radyasyon Görevlisi" in liste

    def test_kadro_unvanlari_dolu(self, svc):
        liste = svc.kadro_unvanlari()
        assert "Teknisyen" in liste

    def test_gorev_yerleri_dolu(self, svc):
        liste = svc.gorev_yerleri()
        assert len(liste) > 0
        adlar = [g["ad"] for g in liste]
        assert "Acil Radyoloji" in adlar

    def test_gorev_yeri_sua_hakki(self, svc):
        liste = svc.gorev_yerleri()
        arad = next(g for g in liste if g["ad"] == "Acil Radyoloji")
        assert arad["sua_hakki"] == 1


class TestGorevGecmisi:

    def test_gorev_gecmisi_cakismazsa_eklenir(self, svc):
        gy = svc.gorev_yerleri()[0]
        pid = svc.ekle(
            {
                "tc_kimlik": "10000000146",
                "ad": "Ali",
                "soyad": "Kaya",
            }
        )
        kid = svc.gorev_gecmisi_ekle(
            pid,
            gy["id"],
            "2024-02-01",
            "2024-02-28",
        )
        assert kid

    def test_gorev_gecmisi_cakisirsa_hata(self, svc):
        yerler = svc.gorev_yerleri()
        pid = svc.ekle(
            {
                "tc_kimlik": "10000000146",
                "ad": "Ali",
                "soyad": "Kaya",
                "gorev_yeri_id": yerler[0]["id"],
                "memuriyet_baslama": "2024-01-01",
            }
        )

        with pytest.raises(CakismaHatasi):
            svc.gorev_gecmisi_ekle(
                pid,
                yerler[1]["id"],
                "2024-01-15",
                "2024-03-01",
            )


class TestYetki:

    def test_ekle_yetkisi_yoksa_hata(self, db):
        svc = PersonelService(db, oturum={"rol": "kullanici", "yetkiler": []})
        with pytest.raises(YetkiHatasi):
            svc.ekle({"tc_kimlik": "10000000146", "ad": "Ali", "soyad": "Kaya"})

    def test_import_upsert_yetkisi_yoksa_hata(self, db):
        svc = PersonelService(db, oturum={"rol": "kullanici", "yetkiler": []})
        with pytest.raises(YetkiHatasi):
            svc.guncelle_veya_ekle_import(
                {
                    "tc_kimlik": "14522068356",
                    "ad": "Veli",
                    "soyad": "Kaya",
                }
            )
