import os
import sqlite3

from omnishared.config import DEBATES_DIR


def get_db_path() -> str:
    return os.getenv("EVIDENCE_VAULT_DB", os.path.join(DEBATES_DIR, "vault.db"))


def get_connection() -> sqlite3.Connection:
    if "EVIDENCE_VAULT_DB" not in os.environ:
        os.makedirs(DEBATES_DIR, exist_ok=True)
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def get_metadata(key: str, default: str = "") -> str:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM metadata WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row["value"] if row else default


def set_metadata(key: str, value: str) -> None:
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()
