# -*- coding: utf-8 -*-
"""tests/test_rbac.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import pytest

from app.rbac import (
    kullanici_avatar,
    modul_gorunur_mu,
    rol,
    rol_eylem_haritasi,
    rol_modul_haritasi,
    yetki_gerektir,
    yetki_var_mi,
)
from app.exceptions import YetkiHatasi


class TestRbacModul:

    def test_admin_tum_modulleri_gorur(self):
        oturum = {"rol": "admin"}
        assert modul_gorunur_mu(oturum, "dashboard") is True
        assert modul_gorunur_mu(oturum, "ayarlar") is True

    def test_kullanici_sistem_modullerini_goremez(self):
        oturum = {"rol": "kullanici"}
        assert modul_gorunur_mu(oturum, "dashboard") is True
        assert modul_gorunur_mu(oturum, "personel") is True
        assert modul_gorunur_mu(oturum, "ayarlar") is False
        assert modul_gorunur_mu(oturum, "kullanici_giris") is False


class TestRbacEylem:

    def test_admin_personel_pasife_alabilir(self):
        assert yetki_var_mi({"rol": "admin"}, "personel.pasife_al") is True

    def test_yonetici_personel_pasife_alamaz(self):
        assert yetki_var_mi({"rol": "yonetici"}, "personel.pasife_al") is False

    def test_kullanici_personel_guncelleyemez(self):
        assert yetki_var_mi({"rol": "kullanici"}, "personel.guncelle") is False


class TestRbacYardimcilar:

    def test_rol_yoksa_kullanici_doner(self):
        assert rol(None) == "kullanici"
        assert rol({}) == "kullanici"

    def test_modul_haritasi_kopya_doner(self):
        harita = rol_modul_haritasi()
        assert "admin" in harita
        assert "kullanici" in harita
        kullanici_once = set(harita["kullanici"] or set())
        harita["kullanici"].add("ayarlar")
        tekrar = rol_modul_haritasi()
        assert set(tekrar["kullanici"] or set()) == kullanici_once

    def test_eylem_haritasi_kopya_doner(self):
        harita = rol_eylem_haritasi()
        assert "admin" in harita
        assert "kullanici" in harita
        harita["kullanici"].add("personel.ekle")
        tekrar = rol_eylem_haritasi()
        assert "personel.ekle" not in tekrar["kullanici"]

    def test_kullanici_avatar_turkce_buyutme_kullanir(self):
        assert kullanici_avatar({"ad": "ilker in"}) == "İİ"

    def test_yetki_gerektir_yetki_yoksa_hata_firlatir(self):
        with pytest.raises(YetkiHatasi):
            yetki_gerektir({"rol": "kullanici"}, "kullanici.guncelle")
