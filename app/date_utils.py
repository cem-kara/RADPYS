from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Iterable

from app.config import TARIH_FORMAT, TARIH_UI


DB_DATE_FORMAT = TARIH_FORMAT
KNOWN_DATE_FORMATS = (
    TARIH_FORMAT,
    TARIH_UI,
    "%d/%m/%Y",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%Y.%m.%d",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d %H:%M:%S.%f",
    "%d.%m.%Y %H:%M:%S",
    "%d.%m.%Y %H:%M",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
)

_EXCEL_EPOCH = date(1899, 12, 30)


def parse_date(value) -> date | None:
    """Yaygın tarih gösterimlerini date nesnesine çevirir."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value).strip()
    if not text:
        return None

    # Excel serial date values are often read as numeric or numeric-like strings.
    try:
        serial = float(text)
        if 1 <= serial <= 100000:
            return _EXCEL_EPOCH + timedelta(days=int(serial))
    except (TypeError, ValueError):
        pass

    for fmt in KNOWN_DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def to_db_date(value):
    """Tarih benzeri değeri veritabanı formatına normalize eder."""
    parsed = parse_date(value)
    if not parsed:
        return value
    return parsed.strftime(DB_DATE_FORMAT)


def to_ui_date(value, fallback: str = "") -> str:
    """Tarih benzeri değeri UI formatına çevirir."""
    parsed = parse_date(value)
    if not parsed:
        return fallback if value is None else str(value)
    return parsed.strftime(TARIH_UI)


def looks_like_date_column(column_name: str) -> bool:
    """Kolon adından tarih alanı olup olmadığını sezgisel belirler."""
    if not column_name:
        return False
    name = str(column_name).strip().lower()
    return (
        name.endswith("tarih")
        or name.endswith("tarihi")
        or name.endswith("date")
        or name.endswith("_date")
    )


def normalize_date_fields(data: dict, date_fields: Iterable[str]) -> dict:
    """Seçili alanları veritabanı tarih formatına çevirilmiş kopya olarak döndürür."""
    out = dict(data or {})
    for field in date_fields or ():
        if field in out:
            out[field] = to_db_date(out.get(field))
    return out