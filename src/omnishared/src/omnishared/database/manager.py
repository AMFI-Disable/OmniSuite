import datetime
import glob
import json
import os
import shutil
import sqlite3

from omnishared.config import ALEMBIC_INI_FILE, BACKUPS_DIR, DEBATES_DIR
from omnishared.database.connection import get_connection, get_db_path


def setup_db():
    """Hardened database synthesis using Alembic migrations."""
    from alembic import command
    from alembic.config import Config

    if "EVIDENCE_VAULT_DB" not in os.environ:
        os.makedirs(DEBATES_DIR, exist_ok=True)

    alembic_cfg = Config(ALEMBIC_INI_FILE)

    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
    has_alembic = c.fetchone()

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='motions'")
    has_motions = c.fetchone()
    conn.close()

    if not has_alembic and has_motions:
        command.stamp(alembic_cfg, "dbb22ea86f29")

    command.upgrade(alembic_cfg, "head")


def search_cards_fts(query: str) -> list[dict]:
    """Executes optimized full-text searches across all vaulted evidence using SQLite FTS5."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            """
            SELECT c.* FROM cards c
            JOIN cards_fts f ON c.id = f.rowid
            WHERE cards_fts MATCH ?
            ORDER BY rank
        """,
            (query,),
        )
        results = [dict(row) for row in c.fetchall()]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()
    return results


def migrate_json_to_sqlite():
    setup_db()
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM motions")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    for fp in glob.glob(os.path.join(DEBATES_DIR, "*.json")):
        if fp.endswith(".trash.json"):
            continue
        name = os.path.basename(fp)[:-5].replace("_", " ").title()
        c.execute("INSERT INTO motions (name, is_archived) VALUES (?, 0)", (name,))
        motion_id = c.lastrowid
        try:
            with open(fp) as f:
                cards = json.load(f)
                for card in cards:
                    c.execute(
                        """
                        INSERT INTO cards (motion_id, tag, citation, side, text, language, mastery, tier, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            motion_id,
                            card.get("tag", ""),
                            card.get("citation", ""),
                            card.get("side", "AFF"),
                            card.get("text", ""),
                            card.get("language", "EN"),
                            card.get("mastery", 0),
                            card.get("tier", 1),
                            card.get("timestamp", ""),
                        ),
                    )
        except Exception:
            pass

    for fp in glob.glob(os.path.join(DEBATES_DIR, "archives", "*.json")):
        name = os.path.basename(fp)[:-5].replace("_", " ").title()
        c.execute("INSERT INTO motions (name, is_archived) VALUES (?, 1)", (name,))
        motion_id = c.lastrowid
        try:
            with open(fp) as f:
                cards = json.load(f)
                for card in cards:
                    c.execute(
                        """
                        INSERT INTO cards (motion_id, tag, citation, side, text, language, mastery, tier, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            motion_id,
                            card.get("tag", ""),
                            card.get("citation", ""),
                            card.get("side", "AFF"),
                            card.get("text", ""),
                            card.get("language", "EN"),
                            card.get("mastery", 0),
                            card.get("tier", 1),
                            card.get("timestamp", ""),
                        ),
                    )
        except Exception:
            pass

    trash_file = os.path.join(DEBATES_DIR, ".trash.json")
    if os.path.exists(trash_file):
        try:
            with open(trash_file) as f:
                trash_items = json.load(f)
                for item in trash_items:
                    c.execute(
                        "INSERT INTO trash (motion_id, card_json, deleted_at) VALUES (?, ?, datetime('now'))",
                        (-1, json.dumps(item.get("card", {}))),
                    )
        except Exception:
            pass

    conn.commit()
    conn.close()


def snapshot():
    """Create a timestamped backup of the vault database."""
    db_path = get_db_path()
    if not os.path.exists(db_path):
        return
    os.makedirs(BACKUPS_DIR, exist_ok=True)
    today = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(BACKUPS_DIR, f"vault_{today}.db.bak")
    shutil.copy2(db_path, dst)


def list_motions(include_archives: bool = False) -> list[dict]:
    try:
        conn = get_connection()
        c = conn.cursor()
        if include_archives:
            c.execute("SELECT id, name, is_archived FROM motions ORDER BY name")
        else:
            c.execute(
                "SELECT id, name, is_archived FROM motions WHERE is_archived = 0 ORDER BY name"
            )
        results = [
            {"id": row["id"], "name": row["name"], "archived": bool(row["is_archived"])}
            for row in c.fetchall()
        ]
        conn.close()
        return results
    except Exception:
        return []


def add_motion(name: str) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO motions (name, is_archived) VALUES (?, 0)", (name,))
    conn.commit()
    motion_id = c.lastrowid
    conn.close()
    return motion_id


def archive_motion(motion_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE motions SET is_archived = 1 WHERE id = ?", (motion_id,))
    conn.commit()
    conn.close()


def is_motion_archived(motion_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT is_archived FROM motions WHERE id = ?", (motion_id,))
    row = c.fetchone()
    conn.close()
    return bool(row["is_archived"]) if row else False


def rename_motion(motion_id: int, new_name: str) -> None:
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE motions SET name = ? WHERE id = ?", (new_name, motion_id))
    conn.commit()
    conn.close()


def delete_motion(motion_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM cards WHERE motion_id = ?", (motion_id,))
    c.execute("DELETE FROM motions WHERE id = ?", (motion_id,))
    conn.commit()
    conn.close()


def get_motion_name(motion_id: int) -> str:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM motions WHERE id = ?", (motion_id,))
    row = c.fetchone()
    conn.close()
    return row["name"] if row else "Unknown"


def read_vault(motion_id: int) -> list:
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM cards WHERE motion_id = ?", (motion_id,))
        cards = [dict(row) for row in c.fetchall()]
        conn.close()
        return cards
    except Exception:
        return []


def read_all_cards() -> list:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT c.*, m.name as _motion FROM cards c LEFT JOIN motions m ON c.motion_id = m.id"
    )
    cards = [dict(row) for row in c.fetchall()]
    conn.close()
    return cards


def add_card(motion_id: int, card_data: dict) -> None:
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO cards (motion_id, tag, citation, side, text, language, mastery, tier, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                motion_id,
                card_data.get("tag", ""),
                card_data.get("citation", ""),
                card_data.get("side", "AFF"),
                card_data.get("text", ""),
                card_data.get("language", "EN"),
                card_data.get("mastery", 0),
                card_data.get("tier", 1),
                card_data.get("timestamp", ""),
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def update_card(card_id: int, card_data: dict) -> None:
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            """
            UPDATE cards SET tag = ?, citation = ?, side = ?, text = ?, language = ?, mastery = ?, tier = ?, timestamp = ?
            WHERE id = ?
        """,
            (
                card_data.get("tag", ""),
                card_data.get("citation", ""),
                card_data.get("side", "AFF"),
                card_data.get("text", ""),
                card_data.get("language", "EN"),
                card_data.get("mastery", 0),
                card_data.get("tier", 1),
                card_data.get("timestamp", ""),
                card_id,
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def delete_card(card_id: int, motion_id: int) -> None:
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM cards WHERE id = ?", (card_id,))
        row = c.fetchone()
        if row:
            c.execute(
                "INSERT INTO trash (motion_id, card_json, deleted_at) VALUES (?, ?, datetime('now'))",
                (motion_id, json.dumps(dict(row))),
            )
            c.execute("DELETE FROM cards WHERE id = ?", (card_id,))
        conn.commit()
        conn.close()
    except Exception:
        pass


def increment_mastery(card_id: int) -> None:
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE cards SET mastery = mastery + 1 WHERE id = ? AND mastery < 5",
            (card_id,),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def get_trash() -> list:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM trash ORDER BY id DESC")
    trash = [
        {
            "id": row["id"],
            "motion_id": row["motion_id"],
            "card": json.loads(row["card_json"]),
        }
        for row in c.fetchall()
    ]
    conn.close()
    return trash


def restore_trash(trash_id: int) -> dict:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM trash WHERE id = ?", (trash_id,))
    row = c.fetchone()
    card_data = None
    if row:
        motion_id = row["motion_id"]
        card = json.loads(row["card_json"])
        c.execute(
            """
            INSERT INTO cards (motion_id, tag, citation, side, text, language, mastery, tier, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                motion_id,
                card.get("tag", ""),
                card.get("citation", ""),
                card.get("side", "AFF"),
                card.get("text", ""),
                card.get("language", "EN"),
                card.get("mastery", 0),
                card.get("tier", 1),
                card.get("timestamp", ""),
            ),
        )
        c.execute("DELETE FROM trash WHERE id = ?", (trash_id,))
        card_data = card
    conn.commit()
    conn.close()
    return card_data


def get_velocity_stats() -> list[int]:
    """Calculates research volume and velocity over a 7-day rolling window."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT date(timestamp) as day, COUNT(*) as count
        FROM cards
        WHERE timestamp >= date('now', '-7 days')
        GROUP BY day
        ORDER BY day DESC
    """)
    stats = {row["day"]: row["count"] for row in c.fetchall()}
    conn.close()

    results = []
    for i in range(7):
        d = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        results.append(stats.get(d, 0))
    return results[::-1]
