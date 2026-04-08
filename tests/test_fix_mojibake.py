# -*- coding: utf-8 -*-
"""tests/test_fix_mojibake.py - docstring odakli mojibake testleri."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from script.fix_mojibake import fix_content, fix_python_docstrings


def test_fix_python_docstrings_module_ve_fonksiyon_docstringlerini_duzeltir():
    kaynak = '''"""DÃ¶kÃ¼man basligi"""


def ornek():
    """FonkÃ§iyon aÃ§iklamasi"""
    return 1
'''

    duzeltilmis, steps = fix_python_docstrings(kaynak)

    assert '"""Döküman basligi"""' in duzeltilmis
    assert '"""Fonkçiyon açiklamasi"""' in duzeltilmis
    assert steps


def test_fix_content_python_dosyasinda_docstringleri_yakalar():
    kaynak = '''def sabit():
    return 1


def belge():
    """DÃ¶kÃ¼man metni"""
    return 2
'''

    duzeltilmis, steps = fix_content(kaynak, file_path="ornek.py")

    assert '"""Döküman metni"""' in duzeltilmis
    assert any("docstring" in step for step in steps)
