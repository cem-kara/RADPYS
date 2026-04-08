# -*- coding: utf-8 -*-
"""tests/test_bootstrap.py — app.bootstrap testleri"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.bootstrap import dizinleri_olustur, logging_kur, veri_katmanini_hazirla


def test_dizinleri_olustur(tmp_path):
    d1 = tmp_path / "data"
    d2 = tmp_path / "logs"
    d3 = tmp_path / "data" / "belgeler"

    dizinleri_olustur([d1, d2, d3])

    assert d1.exists() and d1.is_dir()
    assert d2.exists() and d2.is_dir()
    assert d3.exists() and d3.is_dir()


def test_logging_kur_log_dosyasini_olusturur(tmp_path):
    log_path = logging_kur(tmp_path)
    assert log_path.name == "app.log"
    assert log_path.parent == tmp_path
    assert (tmp_path / "sync.log").exists()
    assert (tmp_path / "errors.log").exists()
    assert (tmp_path / "ui.log").exists()


def test_veri_katmanini_hazirla_migration_ve_tablolar(tmp_path):
    db_path = tmp_path / "bootstrap.db"
    db = veri_katmanini_hazirla(db_path)
    try:
        assert db.path == db_path
        assert db.tablo_var_mi("personel") is True
        assert db.tablo_var_mi("kullanici") is True
        assert db.fetchval("SELECT MAX(versiyon) FROM _db_versiyon") is not None
    finally:
        db.close()
