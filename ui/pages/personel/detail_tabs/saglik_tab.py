# -*- coding: utf-8 -*-
"""Saglik sekmesi iskeleti."""
from __future__ import annotations

from ui.pages.personel.detail_tabs.placeholder_tab import PersonelDetailPlaceholderTab


class PersonelSaglikTab(PersonelDetailPlaceholderTab):
    def __init__(self, parent=None):
        super().__init__(
            title="Saglik",
            subtitle="Muayene ve saglik takip kayitlari bu sekmede olacak.",
            parent=parent,
        )
