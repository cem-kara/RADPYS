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
from app.services.policy_service import PolicyService


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
        assert oturum["sifre_degismeli"] is True

    def test_ilk_giris_sifre_degistirme_sonrasi_yeni_parola_ile_girer(self, svc):
        ilk = svc.giris_yap("admin", "admin123")
        assert ilk["sifre_degismeli"] is True

        svc.ilk_giris_parola_degistir(ilk["id"], "yeniparola123")

        with pytest.raises(DogrulamaHatasi):
            svc.giris_yap("admin", "admin123")

        ikinci = svc.giris_yap("admin", "yeniparola123")
        assert ikinci["sifre_degismeli"] is False
        assert ikinci["son_giris"]

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

    def test_yeni_kullanici_ilk_giriste_sifre_degistirir(self, svc):
        admin = svc.giris_yap("admin", "admin123")
        svc.ilk_giris_parola_degistir(admin["id"], "adminYENI123")

        kid = svc.kullanici_ekle(admin, {
            "ad": "ilklogin",
            "parola": "guclu123",
            "rol": "kullanici",
        })

        ilk = svc.giris_yap("ilklogin", "guclu123")
        assert ilk["id"] == kid
        assert ilk["sifre_degismeli"] is True

    def test_yeni_eklenen_role_kullanici_eklenebilir(self, db, svc):
        admin = svc.giris_yap("admin", "admin123")
        PolicyService(db).rol_ekle(admin, "teknik_sorumlu", kopyala_rol="kullanici")

        kid = svc.kullanici_ekle(admin, {
            "ad": "teknikrol",
            "parola": "guclu123",
            "rol": "teknik_sorumlu",
        })
        row = svc.kullanici_getir(admin, kid)
        assert row["rol"] == "teknik_sorumlu"
