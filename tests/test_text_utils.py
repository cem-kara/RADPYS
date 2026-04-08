# -*- coding: utf-8 -*-
"""tests/test_text_utils.py — Türkçe metin yardımcı testleri"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.text_utils import (
    capitalize_first_letter,
    format_phone_number,
    normalize_whitespace,
    sanitize_filename,
    turkish_lower,
    turkish_title_case,
    turkish_upper,
)


class TestTurkceDonusumler:

    def test_turkish_upper(self):
        assert turkish_upper("istanbul") == "İSTANBUL"
        assert turkish_upper("ışık") == "IŞIK"

    def test_turkish_lower(self):
        assert turkish_lower("İSTANBUL") == "istanbul"
        assert turkish_lower("IŞIK") == "ışık"

    def test_turkish_title_case(self):
        assert turkish_title_case("ahmet cem KARA") == "Ahmet Cem Kara"
        assert turkish_title_case("  istanbul   üniversitesi ") == "  İstanbul Üniversitesi "

    def test_capitalize_first_letter(self):
        assert capitalize_first_letter("merhaba dünya") == "Merhaba dünya"
        assert capitalize_first_letter("   istanbul") == "   İstanbul"


class TestMetinTemizleme:

    def test_normalize_whitespace(self):
        assert normalize_whitespace("Ahmet   Cem  KARA") == "Ahmet Cem KARA"
        assert normalize_whitespace("  tek   satir  ") == "tek satir"

    def test_format_phone_number(self):
        assert format_phone_number("05551234567") == "0555 123 45 67"
        assert format_phone_number("5551234567") == "0555 123 45 67"
        assert format_phone_number("123") == "123"

    def test_sanitize_filename(self):
        assert sanitize_filename("Rapor*2024?.pdf") == "Rapor_2024_.pdf"
        assert sanitize_filename("Hasta Raporu.pdf") == "Hasta_Raporu.pdf"