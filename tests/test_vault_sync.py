"""Unit tests for SQLite database card vault synchronization mechanisms."""

import os

import pytest
from omnishared.database import add_card, add_motion, read_vault, setup_db
from omnishared.database.sync import (
    SyncStrategy,
    VaultSyncEngine,
    apply_vault_changeset,
    calculate_vault_diff,
    compute_vault_checksum,
    export_vault_changeset,
    sync_vault_databases,
)


@pytest.fixture
def create_test_db(tmp_path):
    """Fixture factory to create temporary initialized SQLite vault databases."""

    def _create(filename: str) -> str:
        db_path = str(tmp_path / filename)
        os.environ["EVIDENCE_VAULT_DB"] = db_path
        setup_db()
        return db_path

    return _create


def test_compute_vault_checksum(create_test_db):
    db_path = create_test_db("vault1.db")
    checksum1 = compute_vault_checksum(db_path)

    os.environ["EVIDENCE_VAULT_DB"] = db_path
    mid = add_motion("Climate Change Action")
    add_card(mid, {"tag": "Carbon Tax", "citation": "Smith 2024", "text": "Tax reduces emissions"})

    checksum2 = compute_vault_checksum(db_path)
    assert checksum1 != checksum2
    assert isinstance(checksum2, str)
    assert len(checksum2) == 64  # SHA256 hex string length


def test_export_vault_changeset(create_test_db):
    db_path = create_test_db("vault_export.db")
    os.environ["EVIDENCE_VAULT_DB"] = db_path

    mid = add_motion("AI Governance")
    add_card(
        mid,
        {
            "tag": "Safety Alignment",
            "citation": "Anthropic 2025",
            "side": "AFF",
            "text": "Alignment is critical",
            "language": "EN",
            "mastery": 2,
            "tier": 1,
            "timestamp": "2026-08-01T10:00:00Z",
        },
    )

    changeset = export_vault_changeset(db_path)
    assert changeset["schema_version"] == "1.0"
    assert "vault_checksum" in changeset
    assert len(changeset["motions"]) == 1
    assert changeset["motions"][0]["name"] == "AI Governance"
    assert len(changeset["cards"]) == 1
    assert changeset["cards"][0]["tag"] == "Safety Alignment"


def test_calculate_vault_diff(create_test_db):
    db_a = create_test_db("diff_a.db")
    os.environ["EVIDENCE_VAULT_DB"] = db_a
    mid_a = add_motion("Shared Motion")
    add_card(
        mid_a,
        {
            "tag": "Card A",
            "citation": "Cite A",
            "text": "Text A",
            "timestamp": "2026-08-01T10:00:00Z",
        },
    )

    db_b = create_test_db("diff_b.db")
    os.environ["EVIDENCE_VAULT_DB"] = db_b
    mid_b = add_motion("Shared Motion")
    add_card(
        mid_b,
        {
            "tag": "Card B",
            "citation": "Cite B",
            "text": "Text B",
            "timestamp": "2026-08-02T10:00:00Z",
        },
    )
    add_motion("Remote Only Motion")

    changeset_b = export_vault_changeset(db_b)

    diff = calculate_vault_diff(changeset_b, db_path=db_a)
    assert len(diff.motions_to_insert) == 1
    assert diff.motions_to_insert[0]["name"] == "Remote Only Motion"
    assert len(diff.cards_to_insert) == 1
    assert diff.cards_to_insert[0]["tag"] == "Card B"


def test_apply_vault_changeset_last_write_wins(create_test_db):
    db_a = create_test_db("apply_a.db")
    os.environ["EVIDENCE_VAULT_DB"] = db_a
    mid_a = add_motion("Motion Alpha")
    add_card(
        mid_a,
        {
            "tag": "Tag 1",
            "citation": "Old Citation",
            "side": "AFF",
            "text": "Original text",
            "timestamp": "2026-08-01T10:00:00Z",
        },
    )

    db_b = create_test_db("apply_b.db")
    os.environ["EVIDENCE_VAULT_DB"] = db_b
    mid_b = add_motion("Motion Alpha")
    add_card(
        mid_b,
        {
            "tag": "Tag 1",
            "citation": "Updated Citation",
            "side": "AFF",
            "text": "Updated text",
            "timestamp": "2026-08-05T10:00:00Z",
        },
    )
    add_card(
        mid_b,
        {
            "tag": "Tag 2",
            "citation": "New Citation",
            "side": "NEG",
            "text": "New card text",
            "timestamp": "2026-08-05T11:00:00Z",
        },
    )

    changeset_b = export_vault_changeset(db_b)
    stats = apply_vault_changeset(changeset_b, db_path=db_a, strategy=SyncStrategy.LAST_WRITE_WINS)

    assert stats["inserted_cards"] == 1
    assert stats["updated_cards"] == 1

    os.environ["EVIDENCE_VAULT_DB"] = db_a
    cards_a = read_vault(mid_a)
    assert len(cards_a) == 2

    card_tags = {c["tag"]: c for c in cards_a}
    assert card_tags["Tag 1"]["citation"] == "Updated Citation"
    assert card_tags["Tag 2"]["side"] == "NEG"


def test_apply_vault_changeset_local_wins(create_test_db):
    db_a = create_test_db("local_wins_a.db")
    os.environ["EVIDENCE_VAULT_DB"] = db_a
    mid_a = add_motion("Motion Local")
    add_card(
        mid_a,
        {
            "tag": "Tag Protected",
            "citation": "Local Citation",
            "side": "AFF",
            "text": "Local text",
            "timestamp": "2026-08-01T10:00:00Z",
        },
    )

    db_b = create_test_db("local_wins_b.db")
    os.environ["EVIDENCE_VAULT_DB"] = db_b
    mid_b = add_motion("Motion Local")
    add_card(
        mid_b,
        {
            "tag": "Tag Protected",
            "citation": "Remote Overwrite",
            "side": "AFF",
            "text": "Remote text",
            "timestamp": "2026-08-05T10:00:00Z",
        },
    )

    changeset_b = export_vault_changeset(db_b)
    stats = apply_vault_changeset(changeset_b, db_path=db_a, strategy=SyncStrategy.LOCAL_WINS)

    assert stats["updated_cards"] == 0
    assert stats["skipped"] >= 1

    os.environ["EVIDENCE_VAULT_DB"] = db_a
    cards_a = read_vault(mid_a)
    assert cards_a[0]["citation"] == "Local Citation"


def test_sync_vault_databases_p2p(create_test_db):
    db_a = create_test_db("p2p_a.db")
    os.environ["EVIDENCE_VAULT_DB"] = db_a
    mid_a = add_motion("Universal Basic Income")
    add_card(
        mid_a,
        {
            "tag": "UBI Pro",
            "citation": "Yang 2020",
            "text": "Poverty reduction",
            "timestamp": "2026-08-01T10:00:00Z",
        },
    )

    db_b = create_test_db("p2p_b.db")
    os.environ["EVIDENCE_VAULT_DB"] = db_b
    mid_b = add_motion("Universal Basic Income")
    add_card(
        mid_b,
        {
            "tag": "UBI Con",
            "citation": "Friedman 1980",
            "text": "Inflation risk",
            "timestamp": "2026-08-02T10:00:00Z",
        },
    )

    result = sync_vault_databases(db_a, db_b)

    assert "db_a_updates" in result
    assert "db_b_updates" in result

    os.environ["EVIDENCE_VAULT_DB"] = db_a
    cards_a = read_vault(mid_a)
    assert len(cards_a) == 2

    os.environ["EVIDENCE_VAULT_DB"] = db_b
    cards_b = read_vault(mid_b)
    assert len(cards_b) == 2


def test_vault_sync_engine_class(create_test_db):
    db_path = create_test_db("engine.db")
    engine = VaultSyncEngine(db_path=db_path)

    checksum = engine.get_checksum()
    assert isinstance(checksum, str)

    changeset = engine.export_changeset()
    assert changeset["vault_checksum"] == checksum

    diff = engine.calculate_diff({"motions": [], "cards": []})
    assert isinstance(diff.to_dict(), dict)
