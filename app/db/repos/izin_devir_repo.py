# -*- coding: utf-8 -*-
"""app/db/repos/izin_devir_repo.py — İzin devir/bakiye referans tablosu."""
from __future__ import annotations
from app.db.repos.base import BaseRepo


class IzinDevirRepo(BaseRepo):
    """izin_devir tablosu CRUD. Sadece SQL — iş mantığı yok."""

    def getir(self, personel_id: str, yil: int) -> dict | None:
        return self._db.fetchone(
            "SELECT * FROM izin_devir WHERE personel_id=? AND yil=?",
            (personel_id, int(yil)),
        )

    def listele(self, yil: int | None = None) -> list[dict]:
        if yil:
            return self._db.fetchall(
                "SELECT d.*, p.ad, p.soyad, p.tc_kimlik "
                "FROM izin_devir d "
                "JOIN personel p ON p.id = d.personel_id "
                "WHERE d.yil=? ORDER BY p.soyad, p.ad",
                (int(yil),),
            )
        return self._db.fetchall(
            "SELECT d.*, p.ad, p.soyad, p.tc_kimlik "
            "FROM izin_devir d "
            "JOIN personel p ON p.id = d.personel_id "
            "ORDER BY d.yil DESC, p.soyad, p.ad"
        )

    def kaydet(self, personel_id: str, yil: int, hak_gun: int, devir_gun: int) -> str:
        """Kayıt yoksa ekler, varsa günceller (upsert)."""
        mevcut = self.getir(personel_id, yil)
        if mevcut:
            self._db.execute(
                "UPDATE izin_devir SET hak_gun=?, devir_gun=? "
                "WHERE personel_id=? AND yil=?",
                (int(hak_gun), int(devir_gun), personel_id, int(yil)),
            )
            return str(mevcut.get("id") or "")
        pk = self._new_id()
        self._db.execute(
            "INSERT INTO izin_devir (id, personel_id, yil, hak_gun, devir_gun) "
            "VALUES (?,?,?,?,?)",
            (pk, personel_id, int(yil), int(hak_gun), int(devir_gun)),
        )
        return pk
