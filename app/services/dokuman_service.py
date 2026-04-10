# -*- coding: utf-8 -*-
"""app/services/dokuman_service.py - ortak belge yukleme akisi."""
from __future__ import annotations

import shutil
from pathlib import Path

from app.config import BELGE_DIR, LookupKategori
from app.db.database import Database
from app.db.repos.belge_repo import BelgeRepo
from app.db.repos.lookup_repo import LookupRepo
from app.date_utils import to_db_date
from app.exceptions import KayitBulunamadi
from app.text_utils import sanitize_filename
from app.validators import bugun


class DokumanService:
    """Belge yukleme, listeleme ve silme servis katmani."""

    def __init__(self, db: Database):
        self._repo = BelgeRepo(db)
        self._lookup = LookupRepo(db)

    def belge_turleri(self) -> list[str]:
        return self._lookup.kategori(LookupKategori.BELGE_TUR)

    def listele(self, entity_turu: str, entity_id: str) -> list[dict]:
        return self._repo.listele(entity_turu, entity_id)

    def yukle(
        self,
        file_path: str,
        entity_turu: str,
        entity_id: str,
        tur: str,
        aciklama: str = "",
    ) -> str:
        src = Path(file_path)
        if not src.exists() or not src.is_file():
            raise KayitBulunamadi(f"Dosya bulunamadi: {file_path}")

        hedef_klasor = BELGE_DIR / sanitize_filename(entity_turu) / sanitize_filename(entity_id)
        hedef_klasor.mkdir(parents=True, exist_ok=True)

        temiz_isim = sanitize_filename(src.stem)
        hedef = hedef_klasor / f"{temiz_isim}{src.suffix.lower()}"

        i = 1
        while hedef.exists():
            hedef = hedef_klasor / f"{temiz_isim}_{i}{src.suffix.lower()}"
            i += 1

        shutil.copy2(src, hedef)

        return self._repo.ekle(
            {
                "entity_turu": entity_turu,
                "entity_id": entity_id,
                "tur": tur,
                "dosya_adi": hedef.name,
                "lokal_yol": str(hedef),
                "drive_link": "",
                "aciklama": aciklama,
                "yuklendi": to_db_date(bugun()) or bugun(),
            }
        )

    def sil(self, belge_id: str) -> None:
        row = self._repo.getir(belge_id)
        if not row:
            raise KayitBulunamadi(f"Belge bulunamadi: {belge_id}")

        lokal_yol = str(row.get("lokal_yol") or "").strip()
        if lokal_yol:
            p = Path(lokal_yol)
            if p.exists() and p.is_file():
                p.unlink()

        self._repo.sil(belge_id)
