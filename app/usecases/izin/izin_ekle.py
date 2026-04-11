# -*- coding: utf-8 -*-
"""İzin ekleme iş akışı."""
from __future__ import annotations

from app.exceptions import CakismaHatasi, DogrulamaHatasi
from app.validators import (
    bitis_hesapla,
    parse_tarih_veya_hata,
    pozitif_sayi,
    zorunlu,
)


def execute(izin_repo, veri: dict) -> str:
    """Yeni izin kaydı ekler, oluşan ID'yi döner."""
    zorunlu(veri.get("personel_id"), "Personel")
    zorunlu(veri.get("tur"), "İzin türü")
    zorunlu(veri.get("baslama"), "Başlama tarihi")

    gun = pozitif_sayi(veri.get("gun"), "Gün sayısı")
    baslama = parse_tarih_veya_hata(veri["baslama"], "Başlama tarihi")
    bitis_str = bitis_hesapla(str(baslama), gun)

    if izin_repo.cakisan_var_mi(veri["personel_id"], str(baslama), bitis_str):
        raise CakismaHatasi(
            "Bu personel için seçilen tarih aralığında zaten aktif bir izin kaydı var."
        )

    payload = {
        "personel_id": veri["personel_id"],
        "tur": veri["tur"],
        "baslama": str(baslama),
        "gun": gun,
        "bitis": bitis_str,
        "aciklama": veri.get("aciklama") or None,
    }
    return izin_repo.ekle(payload)
