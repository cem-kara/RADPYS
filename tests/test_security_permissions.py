# -*- coding: utf-8 -*-
"""tests/test_security_permissions.py"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.exceptions import YetkiHatasi
from app.security.permissions import has_permission, require_permission
from app.security.policy import is_admin_session, require_admin_session


class TestPermissions:

    def test_has_permission_oturum_yetkilerinden_okur(self):
        oturum = {"rol": "kullanici", "yetkiler": ["kullanici.goruntule"]}
        assert has_permission(oturum, "kullanici.goruntule") is True
        assert has_permission(oturum, "kullanici.olustur") is False

    def test_has_permission_role_fallback_kullanir(self):
        assert has_permission({"rol": "admin"}, "kullanici.olustur") is True
        assert has_permission({"rol": "kullanici"}, "kullanici.olustur") is False

    def test_require_permission_yoksa_hata_firlatir(self):
        with pytest.raises(YetkiHatasi):
            require_permission({"rol": "kullanici"}, "kullanici.guncelle")


class TestPolicy:

    def test_is_admin_session(self):
        assert is_admin_session({"rol": "admin"}) is True
        assert is_admin_session({"rol": "yonetici"}) is False

    def test_require_admin_session(self):
        require_admin_session({"rol": "admin"}, "hata")
        with pytest.raises(YetkiHatasi):
            require_admin_session({"rol": "kullanici"}, "sadece admin")
