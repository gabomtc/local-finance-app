from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Union

from db.schema import SCHEMA_SQL

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "finance.db"


def init_db(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA_SQL)
    connection.commit()


def get_connection(db_path: Union[str, Path] = DEFAULT_DB_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    init_db(connection)
    return connection
