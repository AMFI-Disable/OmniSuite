"""Extended database operations for V1.0.0 features.

Provides card tagging, rating, edit history, flow persistence,
and export logging capabilities.
"""

import datetime
import json

from omnishared.database.connection import get_connection

# ─── Card Tags ────────────────────────────────────────────────────────────────


def add_card_tag(card_id: int, tag_name: str) -> None:
    """Add a tag to a card. Silently skips if tag already exists."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id FROM card_tags WHERE card_id = ? AND tag_name = ?",
        (card_id, tag_name.strip().lower()),
    )
    if not c.fetchone():
        c.execute(
            "INSERT INTO card_tags (card_id, tag_name) VALUES (?, ?)",
            (card_id, tag_name.strip().lower()),
        )
        conn.commit()
    conn.close()


def remove_card_tag(card_id: int, tag_name: str) -> None:
    """Remove a tag from a card."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "DELETE FROM card_tags WHERE card_id = ? AND tag_name = ?",
        (card_id, tag_name.strip().lower()),
    )
    conn.commit()
    conn.close()


def get_card_tags(card_id: int) -> list[str]:
    """Get all tags for a card."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT tag_name FROM card_tags WHERE card_id = ? ORDER BY tag_name", (card_id,))
    tags = [row["tag_name"] for row in c.fetchall()]
    conn.close()
    return tags


def get_cards_by_tag(tag_name: str) -> list[dict]:
    """Get all cards with a specific tag."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        SELECT c.* FROM cards c
        JOIN card_tags t ON c.id = t.card_id
        WHERE t.tag_name = ?
        ORDER BY c.tag
        """,
        (tag_name.strip().lower(),),
    )
    cards = [dict(row) for row in c.fetchall()]
    conn.close()
    return cards


def list_all_tags() -> list[dict]:
    """List all unique tags with their card counts."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        SELECT tag_name, COUNT(*) as card_count
        FROM card_tags
        GROUP BY tag_name
        ORDER BY card_count DESC
        """
    )
    tags = [{"tag_name": row["tag_name"], "card_count": row["card_count"]} for row in c.fetchall()]
    conn.close()
    return tags


# ─── Card Rating ──────────────────────────────────────────────────────────────


def set_card_rating(card_id: int, rating: int) -> None:
    """Set a card's quality rating (0-5, where 0 = unrated)."""
    rating = max(0, min(5, rating))
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE cards SET rating = ? WHERE id = ?", (rating, card_id))
    conn.commit()
    conn.close()


def get_cards_by_rating(min_rating: int = 1) -> list[dict]:
    """Get all cards with rating >= min_rating."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM cards WHERE rating >= ? ORDER BY rating DESC",
        (min_rating,),
    )
    cards = [dict(row) for row in c.fetchall()]
    conn.close()
    return cards


# ─── Card History ─────────────────────────────────────────────────────────────


def log_card_change(card_id: int, field: str, old_value: str, new_value: str) -> None:
    """Log a change to a card field for version tracking."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO card_history (card_id, field, old_value, new_value, changed_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (card_id, field, old_value, new_value, datetime.datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_card_history(card_id: int) -> list[dict]:
    """Get the edit history for a card."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM card_history WHERE card_id = ? ORDER BY changed_at DESC",
        (card_id,),
    )
    history = [dict(row) for row in c.fetchall()]
    conn.close()
    return history


# ─── Flows ────────────────────────────────────────────────────────────────────


def save_flow(motion_id: int, name: str, flow_data: dict) -> int:
    """Save or update a debate flow."""
    conn = get_connection()
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()

    c.execute(
        "SELECT id FROM flows WHERE motion_id = ? AND name = ?",
        (motion_id, name),
    )
    existing = c.fetchone()

    if existing:
        c.execute(
            "UPDATE flows SET flow_data = ?, updated_at = ? WHERE id = ?",
            (json.dumps(flow_data), now, existing["id"]),
        )
        flow_id = existing["id"]
    else:
        c.execute(
            """
            INSERT INTO flows (motion_id, name, flow_data, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (motion_id, name, json.dumps(flow_data), now, now),
        )
        flow_id = c.lastrowid

    conn.commit()
    conn.close()
    return flow_id


def load_flow(flow_id: int) -> dict | None:
    """Load a debate flow by ID."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM flows WHERE id = ?", (flow_id,))
    row = c.fetchone()
    conn.close()
    if row:
        result = dict(row)
        result["flow_data"] = json.loads(result["flow_data"]) if result["flow_data"] else {}
        return result
    return None


def list_flows(motion_id: int = None) -> list[dict]:
    """List all flows, optionally filtered by motion."""
    conn = get_connection()
    c = conn.cursor()
    if motion_id:
        c.execute("SELECT * FROM flows WHERE motion_id = ? ORDER BY updated_at DESC", (motion_id,))
    else:
        c.execute("SELECT * FROM flows ORDER BY updated_at DESC")
    flows = [dict(row) for row in c.fetchall()]
    conn.close()
    return flows


def delete_flow(flow_id: int) -> None:
    """Delete a debate flow."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM flows WHERE id = ?", (flow_id,))
    conn.commit()
    conn.close()


# ─── Export Log ───────────────────────────────────────────────────────────────


def log_export(motion_id: int, format_name: str, filepath: str, card_count: int) -> None:
    """Log an export operation."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO export_log (motion_id, format, filepath, card_count, exported_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (motion_id, format_name, filepath, card_count, datetime.datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_export_history(limit: int = 50) -> list[dict]:
    """Get recent export history."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        SELECT e.*, m.name as motion_name
        FROM export_log e
        LEFT JOIN motions m ON e.motion_id = m.id
        ORDER BY e.exported_at DESC
        LIMIT ?
        """,
        (limit,),
    )
    history = [dict(row) for row in c.fetchall()]
    conn.close()
    return history


# ─── Statistics ───────────────────────────────────────────────────────────────


def get_vault_statistics() -> dict:
    """Get comprehensive vault statistics for the analytics dashboard."""
    conn = get_connection()
    c = conn.cursor()

    stats = {}

    # Total counts
    c.execute("SELECT COUNT(*) as count FROM cards")
    stats["total_cards"] = c.fetchone()["count"]

    c.execute("SELECT COUNT(*) as count FROM motions WHERE is_archived = 0")
    stats["active_motions"] = c.fetchone()["count"]

    c.execute("SELECT COUNT(*) as count FROM motions WHERE is_archived = 1")
    stats["archived_motions"] = c.fetchone()["count"]

    # Side balance
    c.execute("SELECT side, COUNT(*) as count FROM cards GROUP BY side")
    side_counts = {row["side"]: row["count"] for row in c.fetchall()}
    stats["aff_cards"] = side_counts.get("AFF", 0)
    stats["neg_cards"] = side_counts.get("NEG", 0)

    # Tier distribution
    c.execute("SELECT tier, COUNT(*) as count FROM cards GROUP BY tier")
    stats["tier_distribution"] = {row["tier"]: row["count"] for row in c.fetchall()}

    # Rating distribution
    c.execute("SELECT rating, COUNT(*) as count FROM cards WHERE rating > 0 GROUP BY rating")
    stats["rating_distribution"] = {row["rating"]: row["count"] for row in c.fetchall()}

    # Mastery progress
    c.execute("SELECT AVG(mastery) as avg_mastery FROM cards")
    row = c.fetchone()
    stats["avg_mastery"] = round(row["avg_mastery"], 1) if row["avg_mastery"] else 0

    c.execute("SELECT COUNT(*) as count FROM cards WHERE mastery >= 5")
    stats["mastered_cards"] = c.fetchone()["count"]

    # Language distribution
    c.execute("SELECT language, COUNT(*) as count FROM cards GROUP BY language ORDER BY count DESC")
    stats["languages"] = {row["language"]: row["count"] for row in c.fetchall()}

    # Cards per motion (top 10)
    c.execute(
        """
        SELECT m.name, COUNT(c.id) as card_count
        FROM motions m
        LEFT JOIN cards c ON m.id = c.motion_id
        WHERE m.is_archived = 0
        GROUP BY m.id
        ORDER BY card_count DESC
        LIMIT 10
        """
    )
    stats["top_motions"] = [
        {"name": row["name"], "card_count": row["card_count"]} for row in c.fetchall()
    ]

    # Recent activity (cards added per day, last 30 days)
    c.execute(
        """
        SELECT date(timestamp) as day, COUNT(*) as count
        FROM cards
        WHERE timestamp >= date('now', '-30 days')
        GROUP BY day
        ORDER BY day
        """
    )
    stats["daily_activity"] = {row["day"]: row["count"] for row in c.fetchall()}

    # Tag count
    try:
        c.execute("SELECT COUNT(DISTINCT tag_name) as count FROM card_tags")
        stats["unique_tags"] = c.fetchone()["count"]
    except Exception:
        stats["unique_tags"] = 0

    # Export count
    try:
        c.execute("SELECT COUNT(*) as count FROM export_log")
        stats["total_exports"] = c.fetchone()["count"]
    except Exception:
        stats["total_exports"] = 0

    conn.close()
    return stats


def get_motion_statistics(motion_id: int) -> dict:
    """Get statistics for a specific motion."""
    conn = get_connection()
    c = conn.cursor()

    stats = {}

    c.execute("SELECT COUNT(*) as count FROM cards WHERE motion_id = ?", (motion_id,))
    stats["total_cards"] = c.fetchone()["count"]

    c.execute(
        "SELECT side, COUNT(*) as count FROM cards WHERE motion_id = ? GROUP BY side",
        (motion_id,),
    )
    side_counts = {row["side"]: row["count"] for row in c.fetchall()}
    stats["aff_cards"] = side_counts.get("AFF", 0)
    stats["neg_cards"] = side_counts.get("NEG", 0)

    c.execute(
        "SELECT AVG(mastery) as avg FROM cards WHERE motion_id = ?",
        (motion_id,),
    )
    row = c.fetchone()
    stats["avg_mastery"] = round(row["avg"], 1) if row["avg"] else 0

    c.execute(
        "SELECT tier, COUNT(*) as count FROM cards WHERE motion_id = ? GROUP BY tier",
        (motion_id,),
    )
    stats["tier_distribution"] = {row["tier"]: row["count"] for row in c.fetchall()}

    conn.close()
    return stats
