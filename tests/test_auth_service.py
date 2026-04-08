# -*- coding: utf-8 -*-
"""tests/test_auth_service.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from app.db.database import Database
from app.db.migrations import run as migrate
from app.exceptions import DogrulamaHatasi, KayitZatenVar, YetkiHatasi
from app.services.auth_service import AuthService


@pytest.fixture
def db(tmp_path):
    d = Database(tmp_path / "test.db")
    migrate(d)
    yield d
    d.close()


@pytest.fixture
def svc(db):
    return AuthService(db)


class TestGiris:

    def test_admin_giris_basarili(self, svc):
        oturum = svc.giris_yap("admin", "admin123")
        assert oturum["ad"] == "admin"
        assert oturum["rol"] == "admin"
        assert "kullanici.olustur" in oturum["yetkiler"]

    def test_hatali_parola(self, svc):
        with pytest.raises(DogrulamaHatasi):
            svc.giris_yap("admin", "yanlis")


class TestKullaniciYonetimi:

    def test_admin_kullanici_ekleyebilir(self, svc):
        admin = svc.giris_yap("admin", "admin123")
        kid = svc.kullanici_ekle(admin, {
            "ad": "tekniker1",
            "parola": "guclu123",
            "rol": "kullanici",
        })
        assert kid and len(kid) == 32

    def test_ayni_ad_ile_eklenemez(self, svc):
        admin = svc.giris_yap("admin", "admin123")
        svc.kullanici_ekle(admin, {
            "ad": "tekniker1",
            "parola": "guclu123",
            "rol": "kullanici",
        })
        with pytest.raises(KayitZatenVar):
            svc.kullanici_ekle(admin, {
                "ad": "tekniker1",
                "parola": "guclu123",
                "rol": "kullanici",
            })

    def test_normal_kullanici_ekleyemez(self, svc):
        user = svc.giris_yap("kullanici", "kullanici123")
        with pytest.raises(YetkiHatasi):
            svc.kullanici_ekle(user, {
                "ad": "xuser",
                "parola": "guclu123",
                "rol": "kullanici",
            })

    def test_yonetici_listeleyebilir_ama_ekleyemez(self, svc):
        yonetici = svc.giris_yap("yonetici", "yonetici123")
        rows = svc.kullanici_listele(yonetici)
        assert len(rows) >= 3

        with pytest.raises(YetkiHatasi):
            svc.kullanici_ekle(yonetici, {
                "ad": "testx",
                "parola": "guclu123",
                "rol": "kullanici",
            })

    def test_admin_rol_gunceller(self, svc):
        admin = svc.giris_yap("admin", "admin123")
        kid = svc.kullanici_ekle(admin, {
            "ad": "roltest",
            "parola": "guclu123",
            "rol": "kullanici",
        })
        svc.kullanici_rol_guncelle(admin, kid, "yonetici")
        row = svc.kullanici_getir(admin, kid)
        assert row["rol"] == "yonetici"

    def test_admin_pasife_alir_ve_aktif_eder(self, svc):
        admin = svc.giris_yap("admin", "admin123")
        kid = svc.kullanici_ekle(admin, {
            "ad": "aktiftest",
            "parola": "guclu123",
            "rol": "kullanici",
        })

        svc.kullanici_pasife_al(admin, kid)
        row = svc.kullanici_getir(admin, kid)
        assert int(row["aktif"]) == 0

        svc.kullanici_aktif_et(admin, kid)
        row2 = svc.kullanici_getir(admin, kid)
        assert int(row2["aktif"]) == 1
