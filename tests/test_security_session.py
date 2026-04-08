# -*- coding: utf-8 -*-
"""tests/test_security_session.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.security.session import build_session


def test_build_session_rol_ve_yetkileri_ekler():
    row = {
        "id": "u1",
        "ad": "admin",
        "rol": "admin",
        "son_giris": "2026-01-01 10:00:00",
    }
    oturum = build_session(row)

    assert oturum["id"] == "u1"
    assert oturum["ad"] == "admin"
    assert oturum["rol"] == "admin"
    assert "kullanici.olustur" in oturum["yetkiler"]


def test_build_session_rol_yoksa_kullanici_varsayilir():
    row = {
        "id": "u2",
        "ad": "isimsiz",
        "son_giris": None,
    }
    oturum = build_session(row)

    assert oturum["rol"] == "kullanici"
    assert isinstance(oturum["yetkiler"], list)
