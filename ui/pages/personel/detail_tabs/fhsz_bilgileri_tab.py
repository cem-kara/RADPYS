# -*- coding: utf-8 -*-
"""FHSZ bilgileri sekmesi iskeleti."""
from __future__ import annotations

from ui.pages.personel.detail_tabs.placeholder_tab import PersonelDetailPlaceholderTab


class PersonelFhszBilgileriTab(PersonelDetailPlaceholderTab):
    def __init__(self, parent=None):
        super().__init__(
            title="FHSZ Bilgileri",
            subtitle="FHSZ donemleri ve puantaj detaylari bu sekmeye eklenecek.",
            parent=parent,
        )
