"""Database card vault synchronization mechanisms for OmniSuite.

Provides peer-to-peer and remote synchronization of SQLite evidence vaults,
conflict resolution strategies, changeset generation, diff calculation,
and remote sync protocol integration.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import sqlite3
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from omnishared.database.connection import get_connection, get_db_path


class SyncStrategy(str, Enum):
    """Synchronization conflict resolution strategies."""

    LAST_WRITE_WINS = "last_write_wins"
    LOCAL_WINS = "local_wins"
    REMOTE_WINS = "remote_wins"


@dataclass
class SyncDiff:
    """Represents the difference between local database state and a remote changeset."""

    motions_to_insert: list[dict[str, Any]] = field(default_factory=list)
    motions_to_update: list[dict[str, Any]] = field(default_factory=list)
    cards_to_insert: list[dict[str, Any]] = field(default_factory=list)
    cards_to_update: list[dict[str, Any]] = field(default_factory=list)
    tags_to_insert: list[dict[str, Any]] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compute_vault_checksum(db_path: str | None = None) -> str:
    """Calculates a deterministic hash representing the current vault database contents."""
    conn = _get_db_connection(db_path)
    c = conn.cursor()

    hasher = hashlib.sha256()

    try:
        # Motions checksum
        c.execute("SELECT id, name, is_archived FROM motions ORDER BY id")
        for row in c.fetchall():
            hasher.update(f"motion:{row['id']}:{row['name']}:{row['is_archived']}".encode())

        # Cards checksum
        c.execute(
            "SELECT id, motion_id, tag, citation, side, text, mastery, tier, timestamp, rating "
            "FROM cards ORDER BY id"
        )
        for row in c.fetchall():
            rating = row["rating"] if "rating" in tuple(row.keys()) else 0
            hasher.update(
                f"card:{row['id']}:{row['motion_id']}:{row['tag']}:{row['citation']}:{row['side']}:"
                f"{row['text']}:{row['mastery']}:{row['tier']}:{row['timestamp']}:{rating}".encode()
            )

        # Card Tags checksum
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='card_tags'")
        if c.fetchone():
            c.execute("SELECT card_id, tag_name FROM card_tags ORDER BY card_id, tag_name")
            for row in c.fetchall():
                hasher.update(f"tag:{row['card_id']}:{row['tag_name']}".encode())
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()

    return hasher.hexdigest()


def export_vault_changeset(
    db_path: str | None = None, since_timestamp: str | None = None
) -> dict[str, Any]:
    """Exports motions, cards, card_tags, and trash into a portable JSON-serializable changeset dictionary."""
    conn = _get_db_connection(db_path)
    c = conn.cursor()

    try:
        if since_timestamp:
            c.execute(
                "SELECT * FROM motions WHERE id IN (SELECT motion_id FROM cards WHERE timestamp >= ?)",
                (since_timestamp,),
            )
            motions = [dict(row) for row in c.fetchall()]
            c.execute("SELECT * FROM cards WHERE timestamp >= ? ORDER BY id", (since_timestamp,))
            cards = [dict(row) for row in c.fetchall()]
        else:
            c.execute("SELECT * FROM motions ORDER BY id")
            motions = [dict(row) for row in c.fetchall()]
            c.execute("SELECT * FROM cards ORDER BY id")
            cards = [dict(row) for row in c.fetchall()]

        card_tags = []
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='card_tags'")
        if c.fetchone():
            c.execute("SELECT * FROM card_tags ORDER BY id")
            card_tags = [dict(row) for row in c.fetchall()]

        trash = []
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trash'")
        if c.fetchone():
            c.execute("SELECT * FROM trash ORDER BY id")
            trash = [dict(row) for row in c.fetchall()]
    finally:
        conn.close()

    checksum = compute_vault_checksum(db_path)

    return {
        "schema_version": "1.0",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "vault_checksum": checksum,
        "motions": motions,
        "cards": cards,
        "card_tags": card_tags,
        "trash": trash,
    }


def calculate_vault_diff(remote_changeset: dict[str, Any], db_path: str | None = None) -> SyncDiff:
    """Calculates diff between local database state and a remote changeset."""
    conn = _get_db_connection(db_path)
    c = conn.cursor()

    diff = SyncDiff()

    try:
        # Fetch local motions
        c.execute("SELECT * FROM motions")
        local_motions_by_name = {row["name"]: dict(row) for row in c.fetchall()}

        # Fetch local cards
        c.execute("SELECT * FROM cards")
        [dict(row) for row in c.fetchall()]

        # Map local cards by signature: (motion_name, tag, citation, text) and tag: (motion_name, tag)
        c.execute(
            "SELECT c.*, m.name as motion_name FROM cards c LEFT JOIN motions m ON c.motion_id = m.id"
        )
        local_cards_by_sig = {}
        local_cards_by_tag = {}
        for row in c.fetchall():
            d = dict(row)
            m_name = d.get("motion_name", "")
            sig = (m_name, d.get("tag", ""), d.get("citation", ""), d.get("text", ""))
            local_cards_by_sig[sig] = d
            local_cards_by_tag[(m_name, d.get("tag", ""))] = d

        # Evaluate remote motions
        remote_motions = remote_changeset.get("motions", [])
        for r_motion in remote_motions:
            m_name = r_motion.get("name")
            if m_name not in local_motions_by_name:
                diff.motions_to_insert.append(r_motion)

        # Evaluate remote cards
        remote_cards = remote_changeset.get("cards", [])
        remote_motion_by_id = {m.get("id"): m.get("name") for m in remote_motions}

        for r_card in remote_cards:
            r_motion_name = remote_motion_by_id.get(r_card.get("motion_id"), "")
            r_tag = r_card.get("tag", "")
            sig = (r_motion_name, r_tag, r_card.get("citation", ""), r_card.get("text", ""))

            matching_local = None
            if sig in local_cards_by_sig:
                matching_local = local_cards_by_sig[sig]
            elif (r_motion_name, r_tag) in local_cards_by_tag:
                matching_local = local_cards_by_tag[(r_motion_name, r_tag)]

            if not matching_local:
                diff.cards_to_insert.append(r_card)
            else:
                # Check for update or conflict
                local_ts = matching_local.get("timestamp", "")
                remote_ts = r_card.get("timestamp", "")

                if remote_ts and remote_ts > local_ts:
                    diff.cards_to_update.append({"local": matching_local, "remote": r_card})
                elif remote_ts and local_ts and remote_ts < local_ts:
                    diff.conflicts.append(
                        {"local": matching_local, "remote": r_card, "reason": "local_newer"}
                    )
                else:
                    # Check field differences
                    differs = False
                    for field_name in (
                        "tag",
                        "citation",
                        "side",
                        "text",
                        "language",
                        "mastery",
                        "tier",
                        "rating",
                    ):
                        if field_name in r_card and r_card.get(field_name) != matching_local.get(
                            field_name
                        ):
                            differs = True
                            break
                    if differs:
                        diff.cards_to_update.append({"local": matching_local, "remote": r_card})

        # Evaluate tags
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='card_tags'")
        if c.fetchone():
            c.execute("SELECT * FROM card_tags")
            local_tags = {(row["card_id"], row["tag_name"]) for row in c.fetchall()}

            for r_tag in remote_changeset.get("card_tags", []):
                key = (r_tag.get("card_id"), r_tag.get("tag_name", "").strip().lower())
                if key not in local_tags:
                    diff.tags_to_insert.append(r_tag)

    finally:
        conn.close()

    return diff


def apply_vault_changeset(
    changeset: dict[str, Any],
    db_path: str | None = None,
    strategy: SyncStrategy | str = SyncStrategy.LAST_WRITE_WINS,
) -> dict[str, Any]:
    """Applies a remote changeset to the local vault database using the specified conflict strategy."""
    if isinstance(strategy, str):
        strategy = SyncStrategy(strategy)

    conn = _get_db_connection(db_path)
    c = conn.cursor()

    stats = {
        "inserted_motions": 0,
        "updated_motions": 0,
        "inserted_cards": 0,
        "updated_cards": 0,
        "inserted_tags": 0,
        "conflicts_resolved": 0,
        "skipped": 0,
    }

    try:
        conn.execute("BEGIN TRANSACTION")

        # 1. Motion Mapping & Sync
        c.execute("SELECT id, name, is_archived FROM motions")
        motion_map: dict[str, int] = {row["name"]: row["id"] for row in c.fetchall()}

        remote_id_to_local_motion_id: dict[int, int] = {}

        for r_motion in changeset.get("motions", []):
            r_name = r_motion.get("name")
            r_id = r_motion.get("id")
            if not r_name:
                continue

            if r_name in motion_map:
                local_id = motion_map[r_name]
                remote_id_to_local_motion_id[r_id] = local_id
                # Check if archive status needs update
                if strategy in (SyncStrategy.LAST_WRITE_WINS, SyncStrategy.REMOTE_WINS):
                    c.execute(
                        "UPDATE motions SET is_archived = ? WHERE id = ?",
                        (int(r_motion.get("is_archived", 0)), local_id),
                    )
                    stats["updated_motions"] += 1
            else:
                c.execute(
                    "INSERT INTO motions (name, is_archived) VALUES (?, ?)",
                    (r_name, int(r_motion.get("is_archived", 0))),
                )
                new_id = c.lastrowid
                motion_map[r_name] = new_id
                remote_id_to_local_motion_id[r_id] = new_id
                stats["inserted_motions"] += 1

        # Build remote motion id -> name map
        remote_motion_by_id = {m.get("id"): m.get("name") for m in changeset.get("motions", [])}

        # Map local cards by signature: (motion_name, tag, citation, text) and tag: (motion_name, tag)
        c.execute(
            "SELECT c.*, m.name as motion_name FROM cards c LEFT JOIN motions m ON c.motion_id = m.id"
        )
        local_cards_by_sig = {}
        local_cards_by_tag = {}
        for row in c.fetchall():
            d = dict(row)
            m_name = d.get("motion_name", "")
            sig = (m_name, d.get("tag", ""), d.get("citation", ""), d.get("text", ""))
            local_cards_by_sig[sig] = d
            local_cards_by_tag[(m_name, d.get("tag", ""))] = d

        # Check if rating column exists in local cards
        c.execute("PRAGMA table_info(cards)")
        has_rating_col = any(col["name"] == "rating" for col in c.fetchall())

        # Check if card_history table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='card_history'")
        has_history_table = c.fetchone() is not None

        for r_card in changeset.get("cards", []):
            r_motion_id = r_card.get("motion_id")
            r_motion_name = remote_motion_by_id.get(r_motion_id, "")
            target_motion_id = remote_id_to_local_motion_id.get(
                r_motion_id, motion_map.get(r_motion_name)
            )

            if not target_motion_id:
                # If motion wasn't found or mapped, default to inserting motion or assigning to first motion
                if r_motion_name:
                    c.execute(
                        "INSERT INTO motions (name, is_archived) VALUES (?, 0)", (r_motion_name,)
                    )
                    target_motion_id = c.lastrowid
                    motion_map[r_motion_name] = target_motion_id
                else:
                    target_motion_id = 1

            r_tag = r_card.get("tag", "")
            sig = (r_motion_name, r_tag, r_card.get("citation", ""), r_card.get("text", ""))

            matching_local = None
            if sig in local_cards_by_sig:
                matching_local = local_cards_by_sig[sig]
            elif (r_motion_name, r_tag) in local_cards_by_tag:
                matching_local = local_cards_by_tag[(r_motion_name, r_tag)]

            if not matching_local:
                # Insert new card
                if has_rating_col:
                    c.execute(
                        """
                        INSERT INTO cards (motion_id, tag, citation, side, text, language, mastery, tier, timestamp, rating)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            target_motion_id,
                            r_card.get("tag", ""),
                            r_card.get("citation", ""),
                            r_card.get("side", "AFF"),
                            r_card.get("text", ""),
                            r_card.get("language", "EN"),
                            r_card.get("mastery", 0),
                            r_card.get("tier", 1),
                            r_card.get(
                                "timestamp",
                                datetime.datetime.now(datetime.timezone.utc).isoformat(),
                            ),
                            r_card.get("rating", 0),
                        ),
                    )
                else:
                    c.execute(
                        """
                        INSERT INTO cards (motion_id, tag, citation, side, text, language, mastery, tier, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            target_motion_id,
                            r_card.get("tag", ""),
                            r_card.get("citation", ""),
                            r_card.get("side", "AFF"),
                            r_card.get("text", ""),
                            r_card.get("language", "EN"),
                            r_card.get("mastery", 0),
                            r_card.get("tier", 1),
                            r_card.get(
                                "timestamp",
                                datetime.datetime.now(datetime.timezone.utc).isoformat(),
                            ),
                        ),
                    )
                stats["inserted_cards"] += 1
            else:
                # Conflict Resolution Decision
                should_update = False
                local_ts = matching_local.get("timestamp", "")
                remote_ts = r_card.get("timestamp", "")

                if strategy == SyncStrategy.LOCAL_WINS:
                    should_update = False
                    stats["skipped"] += 1
                elif strategy == SyncStrategy.REMOTE_WINS:
                    should_update = True
                elif strategy == SyncStrategy.LAST_WRITE_WINS:
                    if not local_ts or (remote_ts and remote_ts >= local_ts):
                        should_update = True
                    else:
                        stats["conflicts_resolved"] += 1

                if should_update:
                    card_id = matching_local["id"]
                    # Record history if fields changed
                    if has_history_table:
                        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
                        for f_key in ("tag", "citation", "side", "text", "rating"):
                            if f_key in r_card and str(r_card.get(f_key)) != str(
                                matching_local.get(f_key)
                            ):
                                c.execute(
                                    "INSERT INTO card_history (card_id, field, old_value, new_value, changed_at) "
                                    "VALUES (?, ?, ?, ?, ?)",
                                    (
                                        card_id,
                                        f_key,
                                        str(matching_local.get(f_key)),
                                        str(r_card.get(f_key)),
                                        now_str,
                                    ),
                                )

                    if has_rating_col:
                        c.execute(
                            """
                            UPDATE cards SET tag=?, citation=?, side=?, text=?, language=?, mastery=?, tier=?, timestamp=?, rating=?
                            WHERE id=?
                            """,
                            (
                                r_card.get("tag", matching_local.get("tag")),
                                r_card.get("citation", matching_local.get("citation")),
                                r_card.get("side", matching_local.get("side")),
                                r_card.get("text", matching_local.get("text")),
                                r_card.get("language", matching_local.get("language")),
                                r_card.get("mastery", matching_local.get("mastery")),
                                r_card.get("tier", matching_local.get("tier")),
                                r_card.get("timestamp", matching_local.get("timestamp")),
                                r_card.get("rating", matching_local.get("rating", 0)),
                                card_id,
                            ),
                        )
                    else:
                        c.execute(
                            """
                            UPDATE cards SET tag=?, citation=?, side=?, text=?, language=?, mastery=?, tier=?, timestamp=?
                            WHERE id=?
                            """,
                            (
                                r_card.get("tag", matching_local.get("tag")),
                                r_card.get("citation", matching_local.get("citation")),
                                r_card.get("side", matching_local.get("side")),
                                r_card.get("text", matching_local.get("text")),
                                r_card.get("language", matching_local.get("language")),
                                r_card.get("mastery", matching_local.get("mastery")),
                                r_card.get("tier", matching_local.get("tier")),
                                r_card.get("timestamp", matching_local.get("timestamp")),
                                card_id,
                            ),
                        )
                    stats["updated_cards"] += 1

        # 3. Card Tags Synchronization
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='card_tags'")
        if c.fetchone():
            c.execute("SELECT card_id, tag_name FROM card_tags")
            existing_tags = {(row["card_id"], row["tag_name"]) for row in c.fetchall()}

            for r_tag in changeset.get("card_tags", []):
                card_id = r_tag.get("card_id")
                t_name = r_tag.get("tag_name", "").strip().lower()
                if card_id and t_name and (card_id, t_name) not in existing_tags:
                    c.execute(
                        "INSERT INTO card_tags (card_id, tag_name) VALUES (?, ?)",
                        (card_id, t_name),
                    )
                    existing_tags.add((card_id, t_name))
                    stats["inserted_tags"] += 1

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

    return stats


def sync_vault_databases(
    db_path_a: str, db_path_b: str, strategy: SyncStrategy | str = SyncStrategy.LAST_WRITE_WINS
) -> dict[str, Any]:
    """Performs bidirectional peer-to-peer synchronization between two SQLite vault database files."""
    changeset_a = export_vault_changeset(db_path_a)
    changeset_b = export_vault_changeset(db_path_b)

    stats_a = apply_vault_changeset(changeset_b, db_path=db_path_a, strategy=strategy)
    stats_b = apply_vault_changeset(changeset_a, db_path=db_path_b, strategy=strategy)

    return {"db_a_updates": stats_a, "db_b_updates": stats_b}


def sync_with_remote_node(
    remote_url: str,
    db_path: str | None = None,
    strategy: SyncStrategy | str = SyncStrategy.LAST_WRITE_WINS,
    auth_token: str | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    """Synchronizes local vault with a remote OmniSuite web/sync node over HTTP."""
    local_changeset = export_vault_changeset(db_path)

    # POST local changeset to remote node /api/sync
    endpoint = remote_url.rstrip("/")
    if not endpoint.endswith("/api/sync"):
        endpoint += "/api/sync"

    payload = json.dumps(local_changeset).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    if auth_token:
        req.add_header("Authorization", f"Bearer {auth_token}")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            remote_data = json.loads(resp.read().decode("utf-8"))
            remote_changeset = remote_data.get("changeset", remote_data)

            # Apply remote changeset locally
            apply_stats = apply_vault_changeset(
                remote_changeset, db_path=db_path, strategy=strategy
            )

            return {
                "status": "success",
                "remote_response": remote_data.get("status", "ok"),
                "local_updates": apply_stats,
            }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


class VaultSyncEngine:
    """Stateful synchronizer object managing local and remote vault database sync operations."""

    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path or get_db_path()

    def get_checksum(self) -> str:
        return compute_vault_checksum(self.db_path)

    def export_changeset(self, since_timestamp: str | None = None) -> dict[str, Any]:
        return export_vault_changeset(self.db_path, since_timestamp=since_timestamp)

    def calculate_diff(self, remote_changeset: dict[str, Any]) -> SyncDiff:
        return calculate_vault_diff(remote_changeset, db_path=self.db_path)

    def apply_changeset(
        self,
        changeset: dict[str, Any],
        strategy: SyncStrategy | str = SyncStrategy.LAST_WRITE_WINS,
    ) -> dict[str, Any]:
        return apply_vault_changeset(changeset, db_path=self.db_path, strategy=strategy)

    def sync_with_db(
        self, target_db_path: str, strategy: SyncStrategy | str = SyncStrategy.LAST_WRITE_WINS
    ) -> dict[str, Any]:
        return sync_vault_databases(self.db_path, target_db_path, strategy=strategy)

    def sync_with_remote(
        self,
        remote_url: str,
        strategy: SyncStrategy | str = SyncStrategy.LAST_WRITE_WINS,
        auth_token: str | None = None,
    ) -> dict[str, Any]:
        return sync_with_remote_node(
            remote_url, db_path=self.db_path, strategy=strategy, auth_token=auth_token
        )


def _get_db_connection(db_path: str | None = None) -> sqlite3.Connection:
    if db_path:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    return get_connection()
