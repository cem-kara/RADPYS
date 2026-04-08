# -*- coding: utf-8 -*-
"""tests/test_date_utils.py — Tarih yardımcı testleri"""
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.date_utils import (
    DB_DATE_FORMAT,
    KNOWN_DATE_FORMATS,
    looks_like_date_column,
    normalize_date_fields,
    parse_date,
    to_db_date,
    to_ui_date,
)


class TestParseDate:

    def test_date_nesnesi(self):
        value = date(2026, 4, 8)
        assert parse_date(value) == value

    def test_datetime_nesnesi(self):
        value = datetime(2026, 4, 8, 13, 45)
        assert parse_date(value) == date(2026, 4, 8)

    def test_desteklenen_formatlar(self):
        assert parse_date("2026-04-08") == date(2026, 4, 8)
        assert parse_date("08.04.2026") == date(2026, 4, 8)
        assert parse_date("08/04/2026") == date(2026, 4, 8)
        assert parse_date("08-04-2026") == date(2026, 4, 8)
        assert parse_date("2026.04.08") == date(2026, 4, 8)

    def test_gecersiz_deger(self):
        assert parse_date(None) is None
        assert parse_date("") is None
        assert parse_date("gecersiz") is None


class TestFormatters:

    def test_to_db_date(self):
        assert to_db_date("08.04.2026") == "2026-04-08"
        assert to_db_date(date(2026, 4, 8)) == "2026-04-08"

    def test_to_db_date_parse_edilemezse_orijinal(self):
        assert to_db_date("gecersiz") == "gecersiz"

    def test_to_ui_date(self):
        assert to_ui_date("2026-04-08") == "08.04.2026"
        assert to_ui_date(date(2026, 4, 8)) == "08.04.2026"

    def test_to_ui_date_fallback(self):
        assert to_ui_date(None, fallback="-") == "-"
        assert to_ui_date("gecersiz") == "gecersiz"


class TestHelpers:

    def test_looks_like_date_column(self):
        assert looks_like_date_column("baslama_tarih") is True
        assert looks_like_date_column("izin_tarihi") is True
        assert looks_like_date_column("created_date") is True
        assert looks_like_date_column("ad_soyad") is False

    def test_normalize_date_fields(self):
        data = {
            "baslama_tarih": "08.04.2026",
            "bitis_tarih": "2026/04/10",
            "ad": "Ali",
        }
        normalized = normalize_date_fields(data, ["baslama_tarih", "bitis_tarih"])
        assert normalized == {
            "baslama_tarih": "2026-04-08",
            "bitis_tarih": "2026-04-10",
            "ad": "Ali",
        }
        assert data["baslama_tarih"] == "08.04.2026"

    def test_constants(self):
        assert DB_DATE_FORMAT == "%Y-%m-%d"
        assert "%d.%m.%Y" in KNOWN_DATE_FORMATS