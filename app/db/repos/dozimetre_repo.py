# -*- coding: utf-8 -*-
"""app/db/repos/dozimetre_repo.py - dozimetre tablosu SQL katmani."""
from __future__ import annotations

from app.db.repos.base import BaseRepo


class DozimetreRepo(BaseRepo):
    """dozimetre tablosu sorgulari. Sadece SQL, is mantigi yok."""

    def listele(
        self,
        yil: int | None = None,
        periyot: int | None = None,
        personel_id: str | None = None,
        birim: str | None = None,
    ) -> list[dict]:
        sql = (
            "SELECT d.*, p.ad, p.soyad, p.tc_kimlik, gy.ad AS birim "
            "FROM dozimetre d "
            "JOIN personel p ON p.id = d.personel_id "
            "LEFT JOIN gorev_yeri gy ON gy.id = p.gorev_yeri_id "
            "WHERE 1=1"
        )
        params: list = []

        if yil is not None:
            sql += " AND d.yil = ?"
            params.append(int(yil))
        if periyot is not None:
            sql += " AND d.periyot = ?"
            params.append(int(periyot))
        if personel_id:
            sql += " AND d.personel_id = ?"
            params.append(str(personel_id))
        if birim:
            sql += " AND gy.ad = ?"
            params.append(str(birim))

        sql += " ORDER BY d.yil DESC, d.periyot DESC, p.soyad, p.ad"
        return self._db.fetchall(sql, tuple(params))

    def rapor_listele(self, rapor_no: str) -> list[dict]:
        return self._db.fetchall(
            "SELECT * FROM dozimetre WHERE rapor_no = ? ORDER BY yil DESC, periyot DESC",
            (str(rapor_no or "").strip(),),
        )

    def ekle(self, veri: dict) -> str:
        did = self._new_id()
        self._db.execute(
            "INSERT INTO dozimetre ("
            "id, personel_id, rapor_no, yil, periyot, periyot_adi, "
            "dozimetre_no, tur, bolge, hp10, hp007, durum, olusturuldu"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'))",
            (
                did,
                veri["personel_id"],
                veri.get("rapor_no") or None,
                int(veri.get("yil") or 0),
                int(veri.get("periyot") or 0),
                veri.get("periyot_adi") or None,
                veri.get("dozimetre_no") or None,
                veri.get("tur") or None,
                veri.get("bolge") or None,
                veri.get("hp10"),
                veri.get("hp007"),
                veri.get("durum") or None,
            ),
        )
        return did
