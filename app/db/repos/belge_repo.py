# -*- coding: utf-8 -*-
"""app/db/repos/belge_repo.py - belge tablosu SQL katmani."""
from __future__ import annotations

from app.db.repos.base import BaseRepo


class BelgeRepo(BaseRepo):
    """belge tablosu CRUD. Sadece SQL - is mantigi yok."""

    def listele(self, entity_turu: str, entity_id: str) -> list[dict]:
        return self._db.fetchall(
            "SELECT * FROM belge WHERE entity_turu=? AND entity_id=? ORDER BY yuklendi DESC",
            (entity_turu, entity_id),
        )

    def ekle(self, veri: dict) -> str:
        bid = self._new_id()
        self._db.execute(
            "INSERT INTO belge (id, entity_turu, entity_id, tur, dosya_adi, lokal_yol, drive_link, aciklama, yuklendi) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (
                bid,
                veri["entity_turu"],
                veri["entity_id"],
                veri["tur"],
                veri["dosya_adi"],
                veri.get("lokal_yol"),
                veri.get("drive_link"),
                veri.get("aciklama") or "",
                veri["yuklendi"],
            ),
        )
        return bid

    def sil(self, belge_id: str) -> None:
        self._db.execute("DELETE FROM belge WHERE id=?", (belge_id,))

    def getir(self, belge_id: str) -> dict | None:
        return self._db.fetchone("SELECT * FROM belge WHERE id=?", (belge_id,))
