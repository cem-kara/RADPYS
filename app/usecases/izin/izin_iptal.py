# -*- coding: utf-8 -*-
"""İzin iptal iş akışı."""
from __future__ import annotations

from app.exceptions import IsKuraliHatasi, KayitBulunamadi


def execute(izin_repo, pk: str) -> None:
    """Aktif izni iptal eder."""
    kayit = izin_repo.getir(pk)
    if not kayit:
        raise KayitBulunamadi(f"İzin kaydı bulunamadı: {pk}")
    if kayit.get("durum") == "iptal":
        raise IsKuraliHatasi("Bu izin zaten iptal edilmiş.")
    izin_repo.iptal(pk)
