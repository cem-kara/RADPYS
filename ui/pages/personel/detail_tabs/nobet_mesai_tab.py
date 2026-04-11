# -*- coding: utf-8 -*-
"""Nobet ve mesai sekmesi iskeleti."""
from __future__ import annotations

from ui.pages.personel.detail_tabs.placeholder_tab import PersonelDetailPlaceholderTab


class PersonelNobetMesaiTab(PersonelDetailPlaceholderTab):
    def __init__(self, parent=None):
        super().__init__(
            title="Nobet ve Mesai",
            subtitle="Nobet planlari ve mesai ozetleri bu sekmede yer alacak.",
            parent=parent,
        )
