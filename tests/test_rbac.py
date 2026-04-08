# -*- coding: utf-8 -*-
"""tests/test_rbac.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rbac import modul_gorunur_mu, yetki_var_mi


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
