# -*- coding: utf-8 -*-
"""Personel detay sekmeleri icin kayit ve olusturma yardimcilari."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

from PySide6.QtWidgets import QWidget

from ui.pages.personel.detail_tabs.dozimetre_tab import PersonelDozimetreTab
from ui.pages.personel.detail_tabs.fhsz_bilgileri_tab import PersonelFhszBilgileriTab
from ui.pages.personel.detail_tabs.izin_bilgileri_tab import PersonelIzinBilgileriTab
from ui.pages.personel.detail_tabs.nobet_mesai_tab import PersonelNobetMesaiTab
from ui.pages.personel.detail_tabs.saglik_tab import PersonelSaglikTab

if TYPE_CHECKING:
    from ui.pages.personel.personel_detay import PersonelDetayPage


TabFactory = Callable[["PersonelDetayPage", object], QWidget]


@dataclass(frozen=True)
class DetailTabRegistration:
    """Detay sayfasina eklenecek sekme tanimi."""

    tab_id: str
    label: str
    factory: TabFactory
    refresh_on_sections: frozenset[str] = field(default_factory=frozenset)


def _izin_tab_factory(host: "PersonelDetayPage", db) -> QWidget:
    return PersonelIzinBilgileriTab(
        db=db,
        personel_id_getter=lambda: host._personel_id,
        memuriyet_baslama_getter=lambda: host._current_memuriyet_baslama_iso(),
        alert_callback=lambda msg: host._alert.goster(msg, "warning"),
        parent=host,
    )


def _nobet_mesai_tab_factory(host: "PersonelDetayPage", db) -> QWidget:
    return PersonelNobetMesaiTab(parent=host)


def _fhsz_tab_factory(host: "PersonelDetayPage", db) -> QWidget:
    return PersonelFhszBilgileriTab(
        db=db,
        personel_id_getter=lambda: host._personel_id,
        parent=host,
    )


def _saglik_tab_factory(host: "PersonelDetayPage", db) -> QWidget:
    return PersonelSaglikTab(
        db=db,
        personel_id_getter=lambda: host._personel_id,
        parent=host,
    )


def _dozimetre_tab_factory(host: "PersonelDetayPage", db) -> QWidget:
    return PersonelDozimetreTab(
        db=db,
        personel_id_getter=lambda: host._personel_id,
        parent=host,
    )


def build_detail_tab_registrations() -> list[DetailTabRegistration]:
    """Varsayilan personel detay sekmeleri."""
    return [
        DetailTabRegistration(
            tab_id="izinler",
            label="Izinler",
            factory=_izin_tab_factory,
            refresh_on_sections=frozenset({"kurumsal"}),
        ),
        DetailTabRegistration(
            tab_id="nobet_mesai",
            label="Nobet ve Mesai",
            factory=_nobet_mesai_tab_factory,
        ),
        DetailTabRegistration(
            tab_id="fhsz",
            label="Fiili Hizmet",
            factory=_fhsz_tab_factory,
        ),
        DetailTabRegistration(
            tab_id="saglik",
            label="Saglik",
            factory=_saglik_tab_factory,
        ),
        DetailTabRegistration(
            tab_id="dozimetre",
            label="Dozimetre",
            factory=_dozimetre_tab_factory,
        ),
    ]
