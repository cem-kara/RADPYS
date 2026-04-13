# -*- coding: utf-8 -*-
"""Personel detay sekme bileşenleri."""

from ui.pages.personel.detail_tabs.dozimetre_tab import PersonelDozimetreTab
from ui.pages.personel.detail_tabs.fhsz_bilgileri_tab import PersonelFhszBilgileriTab
from ui.pages.personel.detail_tabs.nobet_mesai_tab import PersonelNobetMesaiTab
from ui.pages.personel.detail_tabs.placeholder_tab import PersonelDetailPlaceholderTab
from ui.pages.personel.detail_tabs.registry import DetailTabRegistration, build_detail_tab_registrations
from ui.pages.personel.detail_tabs.izin_bilgileri_tab import PersonelIzinBilgileriTab
from ui.pages.personel.detail_tabs.saglik_tab import PersonelSaglikTab

__all__ = [
	"DetailTabRegistration",
	"PersonelDetailPlaceholderTab",
	"PersonelDozimetreTab",
	"PersonelNobetMesaiTab",
	"PersonelFhszBilgileriTab",
	"PersonelSaglikTab",
	"build_detail_tab_registrations",
	"PersonelIzinBilgileriTab",
]
