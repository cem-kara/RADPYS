# -*- coding: utf-8 -*-
"""
app/validators.py
─────────────────
Doğrulama fonksiyonları ve tarih yardımcıları.
"""
from __future__ import annotations
import re
from datetime import date
from app.config import TARIH_FORMAT
from app.date_utils import parse_date, to_db_date, to_ui_date
from app.exceptions import DogrulamaHatasi, TCHatasi


_EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


# ── TC Kimlik No ──────────────────────────────────────────────────

def tc_dogrula(tc: str) -> bool:
    """
    Resmi T.C. Kimlik No algoritması.

    Kurallar:
    - 11 rakam
    - İlk rakam 0 olamaz
    - 10. rakam: (tek_pozisyon_toplamı × 7 - çift_pozisyon_toplamı) % 10
    - 11. rakam: (1-9 arası rakamlar toplamı) % 10

    Returns:
        True — geçerli, False — geçersiz
    """
    tc = str(tc or "").strip()
    if len(tc) != 11 or not tc.isdigit() or tc[0] == "0":
        return False
    d = [int(c) for c in tc]
    tek  = d[0] + d[2] + d[4] + d[6] + d[8]
    cift = d[1] + d[3] + d[5] + d[7]
    if (tek * 7 - cift) % 10 != d[9]:
        return False
    if sum(d[:10]) % 10 != d[10]:
        return False
    return True


def tc_dogrula_veya_hata(tc: str) -> str:
    """
    TC'yi doğrular, geçersizse TCHatasi fırlatır.
    Geçerliyse temizlenmiş TC string'ini döner.
    """
    tc = str(tc or "").strip()
    if not tc_dogrula(tc):
        raise TCHatasi(f"Geçersiz TC Kimlik No: '{tc}'")
    return tc


def email_dogrula(email: str | None) -> bool:
    """Email formatını doğrular. Boş değer opsiyonel kabul edilir."""
    if not email:
        return True
    return bool(_EMAIL_PATTERN.match(str(email).strip()))


def telefon_dogrula(telefon: str | None) -> bool:
    """Türkiye GSM numaralarını 10 veya 11 hane olarak doğrular."""
    if not telefon:
        return True

    digits = "".join(char for char in str(telefon) if char.isdigit())
    if len(digits) == 10:
        return digits.startswith("5")
    if len(digits) == 11:
        return digits.startswith("05")
    return False


def bos_degil(deger: str | None) -> bool:
    """Değerin boş veya sadece boşluk olmadığını döndürür."""
    return bool(str(deger or "").strip())


def uzunluk_dogrula(
    deger: str | None,
    min_uzunluk: int = 0,
    max_uzunluk: int | None = None,
) -> bool:
    """Metin uzunluğunu alt ve üst sınıra göre doğrular."""
    if not deger:
        return min_uzunluk == 0

    uzunluk = len(deger)
    if uzunluk < min_uzunluk:
        return False
    if max_uzunluk is not None and uzunluk > max_uzunluk:
        return False
    return True


def sayisal_dogrula(deger: str | None) -> bool:
    """Değerin yalnızca rakamlardan oluştuğunu doğrular."""
    if not deger:
        return True
    return str(deger).isdigit()


def alfasayisal_dogrula(deger: str | None) -> bool:
    """Değerin harf, rakam ve boşluklardan oluştuğunu doğrular."""
    if not deger:
        return True
    return str(deger).replace(" ", "").isalnum()


def tarih_format_dogrula(
    deger: str | None,
    desen: str = r"^\d{2}\.\d{2}\.\d{4}$",
) -> bool:
    """Metnin verilen tarih desenine uyup uymadığını döndürür."""
    if not deger:
        return True
    return bool(re.match(desen, str(deger).strip()))


validate_tc_kimlik_no = tc_dogrula
validate_email = email_dogrula
validate_phone_number = telefon_dogrula
validate_not_empty = bos_degil
validate_length = uzunluk_dogrula
validate_numeric = sayisal_dogrula
validate_alphanumeric = alfasayisal_dogrula
validate_date_format = tarih_format_dogrula


# ── Tarih ─────────────────────────────────────────────────────────

def parse_tarih(deger: str | date | None) -> date | None:
    """
    Çeşitli formatlardan date nesnesi döner.

    Desteklenen formatlar:
        "2026-01-15"  → ISO-8601 (birincil)
        "15.01.2026"  → Türkçe UI formatı
        date nesnesi  → aynen döner

    Returns:
        date nesnesi veya None (parse edilemezse)
    """
    return parse_date(deger)


def parse_tarih_veya_hata(deger: str | None, alan_adi: str = "Tarih") -> date:
    """Parse edilemezse DogrulamaHatasi fırlatır."""
    t = parse_tarih(deger)
    if t is None:
        raise DogrulamaHatasi(
            f"{alan_adi} geçersiz tarih formatı: '{deger}'. "
            f"Beklenen: YYYY-MM-DD"
        )
    return t


def format_tarih(d: date | str | None, ui: bool = False) -> str:
    """
    date → string dönüşümü.

    Args:
        d:  date nesnesi veya string
        ui: True → "15.01.2026", False → "2026-01-15"

    Returns:
        Format string veya "" (None ise)
    """
    if ui:
        return to_ui_date(d, fallback="")
    normalized = to_db_date(d)
    return "" if normalized is None else normalized


def bugun() -> str:
    """Bugünün tarihini ISO-8601 formatında döner."""
    return date.today().strftime(TARIH_FORMAT)


def bitis_hesapla(baslama: str, gun: int) -> str:
    """
    Başlama tarihi + gün sayısı → bitiş tarihi.
    Bitiş = başlama + gun - 1 (örn: 1 günlük izin → aynı gün)
    """
    from datetime import timedelta
    t = parse_tarih_veya_hata(baslama, "Başlama tarihi")
    return format_tarih(t + timedelta(days=gun - 1))


def is_gunu_say(baslama: str, bitis: str,
                tatiller: set[str] | None = None) -> int:
    """
    İki tarih arasındaki iş günü sayısı.
    Hafta sonları ve tatiller hariçtir.

    Args:
        baslama:  "YYYY-MM-DD"
        bitis:    "YYYY-MM-DD" (dahil)
        tatiller: {"2026-01-01", ...} set'i
    """
    from datetime import timedelta
    bas = parse_tarih_veya_hata(baslama)
    bit = parse_tarih_veya_hata(bitis)
    tatiller = tatiller or set()
    sayac = 0
    gun = bas
    while gun <= bit:
        if gun.weekday() < 5 and format_tarih(gun) not in tatiller:
            sayac += 1
        gun += timedelta(days=1)
    return sayac


# ── Genel ─────────────────────────────────────────────────────────

def zorunlu(deger, alan_adi: str) -> str:
    """Boş string kontrolü. Boşsa DogrulamaHatasi fırlatır."""
    if not str(deger or "").strip():
        raise DogrulamaHatasi(f"'{alan_adi}' alanı zorunludur.")
    return str(deger).strip()


def pozitif_sayi(deger, alan_adi: str) -> int:
    """Pozitif tamsayı kontrolü."""
    try:
        v = int(deger)
        if v <= 0:
            raise ValueError
        return v
    except (TypeError, ValueError):
        raise DogrulamaHatasi(
            f"'{alan_adi}' pozitif bir sayı olmalıdır."
        )


def to_float(deger, varsayilan: float = 0.0) -> float:
    """None/boş değerleri güvenli float'a çevirir."""
    if deger is None or str(deger).strip() == "":
        return varsayilan
    try:
        return float(str(deger).replace(",", "."))
    except (ValueError, TypeError):
        return varsayilan


def to_int(deger, varsayilan: int = 0) -> int:
    """None/boş değerleri güvenli int'e çevirir."""
    try:
        return int(float(str(deger or varsayilan)))
    except (ValueError, TypeError):
        return varsayilan
