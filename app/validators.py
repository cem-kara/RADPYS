# -*- coding: utf-8 -*-
"""
app/validators.py
─────────────────
Doğrulama fonksiyonları ve tarih yardımcıları.
"""
from __future__ import annotations
from datetime import date, datetime
from app.config import TARIH_FORMAT, TARIH_UI
from app.exceptions import DogrulamaHatasi, TCHatasi


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
    if deger is None or deger == "":
        return None
    if isinstance(deger, date):
        return deger
    deger = str(deger).strip()
    for fmt in (TARIH_FORMAT, TARIH_UI, "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(deger, fmt).date()
        except ValueError:
            continue
    return None


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
    if d is None:
        return ""
    if isinstance(d, str):
        d = parse_tarih(d)
        if d is None:
            return ""
    return d.strftime(TARIH_UI if ui else TARIH_FORMAT)


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
