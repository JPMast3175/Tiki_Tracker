"""SQLite connection manager with WAL mode and foreign-key enforcement."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator


def _default_db_path() -> Path:
    # Walk up: database.py → db/ → tiki_tracker/ → src/ → Tiki_Tracker/
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "tiki_tracker.db"


class Database:
    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = Path(db_path) if db_path else _default_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def fetchall(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute(sql, params).fetchall()

    def fetchone(self, sql: str, params: tuple = ()) -> sqlite3.Row | None:
        with self.connect() as conn:
            return conn.execute(sql, params).fetchone()

    def execute(self, sql: str, params: tuple = ()) -> int:
        """Execute a write statement and return lastrowid (or rowcount for updates)."""
        with self.connect() as conn:
            cur = conn.execute(sql, params)
            return cur.lastrowid or cur.rowcount

    def executemany(self, sql: str, params_list: list[tuple]) -> None:
        with self.connect() as conn:
            conn.executemany(sql, params_list)
