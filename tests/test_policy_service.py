# -*- coding: utf-8 -*-
"""tests/test_policy_service.py — PolicyService testleri"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.db.database import Database
from app.db.migrations import run as migrate
from app.services.auth_service import AuthService
from app.services.policy_service import PolicyService
from app.exceptions import YetkiHatasi


@pytest.fixture
def db(tmp_path):
    d = Database(tmp_path / "test.db")
    migrate(d)
    yield d
    d.close()


@pytest.fixture
def admin_oturum(db):
    svc = AuthService(db)
    return svc.giris_yap("admin", "admin123")


@pytest.fixture
def yonetici_oturum(db):
    svc = AuthService(db)
    return svc.giris_yap("yonetici", "yonetici123")


@pytest.fixture
def svc(db):
    return PolicyService(db)


class TestModulSetiGetir:

    def test_yonetici_varsayilan_izinleri_var(self, svc):
        izinler = svc.modul_seti_getir("yonetici")
        assert izinler is not None
        assert "dashboard" in izinler
        assert "personel"  in izinler

    def test_kullanici_varsayilan_izinleri_sinirli(self, svc):
        izinler = svc.modul_seti_getir("kullanici")
        assert izinler is not None
        assert "dashboard"   in izinler
        assert "dokumanlar"  in izinler
        assert "nobet" not in izinler

    def test_olmayan_rol_none_doner(self, svc):
        izinler = svc.modul_seti_getir("olmayan_rol")
        assert izinler is None


class TestRolModulleriniKaydet:

    def test_admin_yonetici_izinlerini_guncelleyebilir(
        self, svc, admin_oturum
    ):
        yeni_set = {"dashboard", "personel"}
        svc.rol_modullerini_kaydet(admin_oturum, "yonetici", yeni_set)
        guncellendi = svc.modul_seti_getir("yonetici")
        assert guncellendi is not None
        assert "dashboard" in guncellendi
        assert "personel"  in guncellendi
        # Daha önce izinli olan ama artık olmayan modül
        assert "izin" not in guncellendi

    def test_admin_rolunu_guncellemek_yasak(self, svc, admin_oturum):
        with pytest.raises(YetkiHatasi):
            svc.rol_modullerini_kaydet(admin_oturum, "admin", {"dashboard"})

    def test_yetersiz_yetki_ile_guncelleme_yasak(self, svc, yonetici_oturum):
        with pytest.raises(YetkiHatasi):
            svc.rol_modullerini_kaydet(
                yonetici_oturum, "kullanici", {"dashboard"}
            )

    def test_bos_set_kaydedilebilir(self, svc, admin_oturum):
        svc.rol_modullerini_kaydet(admin_oturum, "kullanici", set())
        guncellendi = svc.modul_seti_getir("kullanici")
        assert guncellendi is not None
        assert len(guncellendi) == 0


class TestTumRolModulleri:

    def test_tum_roller_donuyor(self, svc):
        harita = svc.tum_rol_modulleri()
        assert "yonetici"  in harita
        assert "kullanici" in harita

    def test_admin_none_veya_dolu_set(self, svc):
        harita = svc.tum_rol_modulleri()
        # admin ya None (tüm modüller) ya da dolu set olmalı
        admin_izin = harita.get("admin")
        # Herhangi bir falsy olmayan değer veya None kabul edilir
        # (admin için tüm modüller izinli)
        assert admin_izin is None or len(admin_izin) > 0
