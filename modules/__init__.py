# -*- coding: utf-8 -*-
"""
modules/__init__.py — Tüm modül tanımlarını otomatik yükler.

load_all() çağrısı modules/ altındaki her .py dosyasını import eder.
Her dosya kendi register() çağrısını yapar.
Yeni modül eklemek = modules/ altına yeni .py oluşturmak.
"""
from __future__ import annotations
import importlib, pkgutil, pathlib


def load_all() -> None:
    pkg_dir  = pathlib.Path(__file__).parent
    pkg_name = __name__
    for _, name, _ in pkgutil.iter_modules([str(pkg_dir)]):
        importlib.import_module(f"{pkg_name}.{name}")
