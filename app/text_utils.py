# -*- coding: utf-8 -*-
"""Türkçe metin formatlama yardımcıları."""
from __future__ import annotations

import re


_TURKISH_UPPER_MAP = str.maketrans({
    "i": "İ",
    "ı": "I",
    "ş": "Ş",
    "ğ": "Ğ",
    "ü": "Ü",
    "ö": "Ö",
    "ç": "Ç",
})

_TURKISH_LOWER_MAP = str.maketrans({
    "İ": "i",
    "I": "ı",
    "Ş": "ş",
    "Ğ": "ğ",
    "Ü": "ü",
    "Ö": "ö",
    "Ç": "ç",
})

_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*]')
_MULTIPLE_WHITESPACE = re.compile(r"\s+")


def turkish_upper(text: str) -> str:
    """Türkçe karakterleri koruyarak metni büyük harfe çevirir."""
    if not text:
        return text
    return text.translate(_TURKISH_UPPER_MAP).upper().translate(_TURKISH_UPPER_MAP)


def turkish_lower(text: str) -> str:
    """Türkçe karakterleri koruyarak metni küçük harfe çevirir."""
    if not text:
        return text
    return text.translate(_TURKISH_LOWER_MAP).lower().translate(_TURKISH_LOWER_MAP)


def turkish_title_case(text: str) -> str:
    """Her kelimenin ilk harfini Türkçe kurallarla büyütür."""
    if not text:
        return text

    leading_spaces = len(text) - len(text.lstrip())
    trailing_spaces = len(text) - len(text.rstrip())
    stripped = text.strip()
    if not stripped:
        return text

    formatted_words = []
    for word in _MULTIPLE_WHITESPACE.split(stripped):
        if not word:
            continue
        formatted_words.append(turkish_upper(word[:1]) + turkish_lower(word[1:]))

    return (" " * leading_spaces) + " ".join(formatted_words) + (" " * trailing_spaces)


def capitalize_first_letter(text: str) -> str:
    """İlk boş olmayan karakteri Türkçe kurallarla büyütür."""
    if not text:
        return text

    for index, char in enumerate(text):
        if not char.strip():
            continue
        return text[:index] + turkish_upper(char) + text[index + 1 :]
    return text


def normalize_whitespace(text: str) -> str:
    """Boşlukları normalize edip baştaki ve sondaki boşlukları temizler."""
    if not text:
        return text
    return _MULTIPLE_WHITESPACE.sub(" ", text).strip()


def format_phone_number(phone: str) -> str:
    """Telefon numarasını 0XXX XXX XX XX biçiminde döndürür."""
    if not phone:
        return phone

    digits = "".join(char for char in phone if char.isdigit())
    if len(digits) == 10 and digits[0] != "0":
        digits = f"0{digits}"
    if len(digits) != 11:
        return phone
    return f"{digits[:4]} {digits[4:7]} {digits[7:9]} {digits[9:]}"


def sanitize_filename(filename: str) -> str:
    """Windows için geçersiz dosya adı karakterlerini temizler."""
    if not filename:
        return filename

    cleaned = _INVALID_FILENAME_CHARS.sub("_", filename)
    return cleaned.replace(" ", "_")