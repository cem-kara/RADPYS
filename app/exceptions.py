# -*- coding: utf-8 -*-
"""
app/exceptions.py
─────────────────
Uygulama exception hiyerarşisi.

Kullanım (servis):
    raise LimitHatasi("Yıllık izin kalan: 5 gün, talep: 10 gün")

Kullanım (UI):
    try:
        svc.izin_kaydet(veri)
    except LimitHatasi as e:
        AlertBar.goster(self, str(e), tur="warning")
    except IsKuraliHatasi as e:
        AlertBar.goster(self, str(e), tur="danger")
    except AppHatasi as e:
        AlertBar.goster(self, str(e), tur="danger")
"""


class AppHatasi(Exception):
    """
    Tüm uygulama hatalarının tabanı.
    Bu sınıfı yakalamak tüm uygulama hatalarını yakalar.
    """


# ── Doğrulama ─────────────────────────────────────────────────────

class DogrulamaHatasi(AppHatasi):
    """
    Girdi doğrulama hatası.
    Kullanıcıya gösterilir, işlem iptal edilir.

    Örnekler:
        - Geçersiz TC kimlik no
        - Boş zorunlu alan
        - Geçersiz tarih formatı
    """


class TCHatasi(DogrulamaHatasi):
    """TC Kimlik No algoritma doğrulama hatası."""


# ── İş Kuralı ─────────────────────────────────────────────────────

class IsKuraliHatasi(AppHatasi):
    """
    İş kuralı ihlali.
    Kullanıcıya açıklayıcı mesajla gösterilir.
    """


class LimitHatasi(IsKuraliHatasi):
    """
    İzin limiti aşımı.

    Örnek:
        raise LimitHatasi(
            "Yıllık izin kalan: 5 gün, "
            "talep edilen: 10 gün"
        )
    """


class CakismaHatasi(IsKuraliHatasi):
    """
    Tarih çakışması — aynı aralıkta başka kayıt var.

    Örnek:
        raise CakismaHatasi(
            "2026-03-01 – 2026-03-10 aralığında "
            "mevcut bir Yıllık İzin kaydı bulunuyor."
        )
    """


class PasifPersonelHatasi(IsKuraliHatasi):
    """
    Pasif personel üzerinde işlem yapmaya çalışıldı.
    """


class YetkiHatasi(IsKuraliHatasi):
    """
    Kullanıcının bu işlemi yapmaya yetkisi yok.
    """


# ── Veri ──────────────────────────────────────────────────────────

class KayitBulunamadi(AppHatasi):
    """
    İstenen kayıt veritabanında yok.

    Örnek:
        raise KayitBulunamadi(f"Personel bulunamadı: {tc}")
    """


class KayitZatenVar(AppHatasi):
    """
    Eklenmek istenen kayıt zaten mevcut (UNIQUE ihlali).

    Örnek:
        raise KayitZatenVar(f"Bu TC zaten kayıtlı: {tc}")
    """


# ── Sistem ────────────────────────────────────────────────────────

class VTHatasi(AppHatasi):
    """Veritabanı erişim hatası."""


class DosyaHatasi(AppHatasi):
    """Dosya okuma/yazma/yükleme hatası."""


class KonfigurasyonHatasi(AppHatasi):
    """Uygulama yapılandırma hatası."""
