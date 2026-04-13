# -*- coding: utf-8 -*-
"""app/db/repos/muayene_repo.py - muayene tablosu SQL katmani."""
from __future__ import annotations

from app.db.repos.base import BaseRepo


class MuayeneRepo(BaseRepo):
    """muayene tablosu sorgulari. Sadece SQL, is mantigi yok."""

    def listele(self, yil: int | None = None, personel_id: str | None = None) -> list[dict]:
        sql = (
            "SELECT m.*, p.ad, p.soyad, p.tc_kimlik, gy.ad AS birim, "
            "b.dosya_adi, b.lokal_yol, b.drive_link "
            "FROM muayene m "
            "JOIN personel p ON p.id = m.personel_id "
            "LEFT JOIN gorev_yeri gy ON gy.id = p.gorev_yeri_id "
            "LEFT JOIN belge b ON b.id = m.belge_id "
            "WHERE 1=1"
        )
        params: list = []
        if yil:
            sql += " AND strftime('%Y', m.tarih) = ?"
            params.append(str(int(yil)))
        if personel_id:
            sql += " AND m.personel_id = ?"
            params.append(str(personel_id))
        sql += " ORDER BY m.tarih DESC, p.soyad, p.ad"
        return self._db.fetchall(sql, tuple(params))

    def personel_listele(self, personel_id: str) -> list[dict]:
        return self.listele(personel_id=personel_id)

    def getir(self, muayene_id: str) -> dict | None:
        return self._db.fetchone("SELECT * FROM muayene WHERE id = ?", (muayene_id,))

    def ekle(self, veri: dict) -> str:
        mid = self._new_id()
        self._db.execute(
            "INSERT INTO muayene ("
            "id, personel_id, uzmanlik, tarih, sonraki, sonuc, notlar, belge_id, olusturuldu"
            ") VALUES (?,?,?,?,?,?,?,?,?)",
            (
                mid,
                veri["personel_id"],
                veri["uzmanlik"],
                veri["tarih"],
                veri.get("sonraki") or None,
                veri.get("sonuc") or None,
                veri.get("notlar") or None,
                veri.get("belge_id") or None,
                veri.get("olusturuldu"),
            ),
        )
        return mid

    def guncelle(self, muayene_id: str, veri: dict) -> None:
        self._db.execute(
            "UPDATE muayene SET "
            "personel_id=?, uzmanlik=?, tarih=?, sonraki=?, sonuc=?, notlar=?, belge_id=? "
            "WHERE id=?",
            (
                veri["personel_id"],
                veri["uzmanlik"],
                veri["tarih"],
                veri.get("sonraki") or None,
                veri.get("sonuc") or None,
                veri.get("notlar") or None,
                veri.get("belge_id") or None,
                muayene_id,
            ),
        )

    def sil(self, muayene_id: str) -> None:
        self._db.execute("DELETE FROM muayene WHERE id=?", (muayene_id,))
