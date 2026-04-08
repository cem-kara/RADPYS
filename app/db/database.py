# -*- coding: utf-8 -*-
"""app/db/database.py — SQLite bağlantı yöneticisi."""
from __future__ import annotations
import sqlite3, time, logging
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger("radpys.db")


class Database:
    """
    Tek SQLite bağlantısı.
    isolation_level=None → autocommit modu.
    Transaction bloğu dışında her yazma otomatik commit edilir.
    Transaction bloğu içinde BEGIN/COMMIT/ROLLBACK manuel yönetilir.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(
            str(self.path),
            check_same_thread=False,
            timeout=30,
            isolation_level=None,   # autocommit
        )
        self._conn.row_factory = sqlite3.Row
        self._in_tx = False

        for p in (
            "PRAGMA journal_mode=WAL",
            "PRAGMA foreign_keys=ON",
            "PRAGMA synchronous=NORMAL",
            "PRAGMA cache_size=-8192",
            "PRAGMA temp_store=MEMORY",
        ):
            self._conn.execute(p)
        logger.info(f"DB açıldı: {self.path}")

    # ── Sorgular ──────────────────────────────────────────────────

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """SQL çalıştırır. autocommit modunda zaten transaction'sız commit olur."""
        for attempt in range(5):
            try:
                return self._conn.execute(sql, params)
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and attempt < 4:
                    time.sleep(0.1 * (attempt + 1))
                    continue
                raise

    def executemany(self, sql: str, params_list: list) -> None:
        if not self._in_tx:
            self._conn.execute("BEGIN")
        self._conn.executemany(sql, params_list)
        if not self._in_tx:
            self._conn.execute("COMMIT")

    def fetchall(self, sql: str, params: tuple = ()) -> list[dict]:
        return [dict(r) for r in self._conn.execute(sql, params).fetchall()]

    def fetchone(self, sql: str, params: tuple = ()) -> dict | None:
        r = self._conn.execute(sql, params).fetchone()
        return dict(r) if r else None

    def fetchval(self, sql: str, params: tuple = (), default=None):
        r = self._conn.execute(sql, params).fetchone()
        return r[0] if r else default

    # ── Transaction ───────────────────────────────────────────────

    @contextmanager
    def transaction(self):
        """
        Atomik işlem bloğu.
        İç içe çağrılabilir — iç çağrılar savepoint kullanır.
        """
        if self._in_tx:
            # İç içe: savepoint
            sp = f"sp{id(self) & 0xFFFF}"
            self._conn.execute(f"SAVEPOINT {sp}")
            try:
                yield self
                self._conn.execute(f"RELEASE SAVEPOINT {sp}")
            except Exception:
                self._conn.execute(f"ROLLBACK TO SAVEPOINT {sp}")
                self._conn.execute(f"RELEASE SAVEPOINT {sp}")
                raise
        else:
            # Dış transaction
            self._in_tx = True
            self._conn.execute("BEGIN")
            try:
                yield self
                self._conn.execute("COMMIT")
            except Exception:
                try:
                    self._conn.execute("ROLLBACK")
                except Exception:
                    pass
                raise
            finally:
                self._in_tx = False

    # ── Yardımcılar ───────────────────────────────────────────────

    def tablo_var_mi(self, tablo: str) -> bool:
        return bool(self.fetchval(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            (tablo,)
        ))

    def sutun_var_mi(self, tablo: str, sutun: str) -> bool:
        return any(r["name"] == sutun
                   for r in self.fetchall(f"PRAGMA table_info({tablo})"))

    def __enter__(self): return self
    def __exit__(self, *_): self.close()

    def close(self):
        try:
            self._conn.close()
            logger.info(f"DB kapatıldı: {self.path}")
        except Exception:
            pass
