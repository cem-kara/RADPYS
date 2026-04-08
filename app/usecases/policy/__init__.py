# -*- coding: utf-8 -*-
"""Policy use-case fonksiyonlari."""

from app.usecases.policy.rol_modullerini_kaydet import execute as rol_modullerini_kaydet
from app.usecases.policy.tum_rol_modulleri_getir import execute as tum_rol_modulleri_getir

__all__ = ["rol_modullerini_kaydet", "tum_rol_modulleri_getir"]
