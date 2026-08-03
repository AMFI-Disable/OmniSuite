"""Tests for extended database operations (V1.0.0 features).

Tests card tags, ratings, edit history, flow persistence,
export logging, and vault statistics.
"""

import os

import pytest
from omnidebate.core.database import add_card, add_motion, read_vault, setup_db
from omnishared.database.extended import (
    add_card_tag,
    delete_flow,
    get_card_history,
    get_card_tags,
    get_cards_by_rating,
    get_cards_by_tag,
    get_export_history,
    get_motion_statistics,
    get_vault_statistics,
    list_all_tags,
    list_flows,
    load_flow,
    log_card_change,
    log_export,
    remove_card_tag,
    save_flow,
    set_card_rating,
)


@pytest.fixture(autouse=True)
def test_db(tmp_path):
    db_file = tmp_path / "test_vault.db"
    os.environ["EVIDENCE_VAULT_DB"] = str(db_file)
    setup_db()
    yield
    if db_file.exists():
        os.remove(db_file)
    if "EVIDENCE_VAULT_DB" in os.environ:
        del os.environ["EVIDENCE_VAULT_DB"]


@pytest.fixture
def motion_with_cards(test_db):
    """Create a motion with two cards for testing."""
    mid = add_motion("Test Motion")
    add_card(
        mid,
        {
            "tag": "AFF card",
            "citation": "Smith 2023",
            "side": "AFF",
            "text": "Aff evidence",
            "tier": 2,
        },
    )
    add_card(
        mid,
        {
            "tag": "NEG card",
            "citation": "Jones 2023",
            "side": "NEG",
            "text": "Neg evidence",
            "tier": 1,
        },
    )
    cards = read_vault(mid)
    return mid, cards


# ─── Card Tags ────────────────────────────────────────────────────────────────


class TestCardTags:
    def test_add_tag(self, motion_with_cards):
        _, cards = motion_with_cards
        card_id = cards[0]["id"]
        add_card_tag(card_id, "economy")
        tags = get_card_tags(card_id)
        assert "economy" in tags

    def test_tags_are_lowercased(self, motion_with_cards):
        _, cards = motion_with_cards
        card_id = cards[0]["id"]
        add_card_tag(card_id, "Economy")
        tags = get_card_tags(card_id)
        assert "economy" in tags
        assert "Economy" not in tags

    def test_duplicate_tag_ignored(self, motion_with_cards):
        _, cards = motion_with_cards
        card_id = cards[0]["id"]
        add_card_tag(card_id, "trade")
        add_card_tag(card_id, "trade")
        tags = get_card_tags(card_id)
        assert tags.count("trade") == 1

    def test_multiple_tags(self, motion_with_cards):
        _, cards = motion_with_cards
        card_id = cards[0]["id"]
        add_card_tag(card_id, "economy")
        add_card_tag(card_id, "trade")
        add_card_tag(card_id, "growth")
        tags = get_card_tags(card_id)
        assert len(tags) == 3
        assert set(tags) == {"economy", "trade", "growth"}

    def test_remove_tag(self, motion_with_cards):
        _, cards = motion_with_cards
        card_id = cards[0]["id"]
        add_card_tag(card_id, "economy")
        remove_card_tag(card_id, "economy")
        tags = get_card_tags(card_id)
        assert "economy" not in tags

    def test_get_cards_by_tag(self, motion_with_cards):
        _, cards = motion_with_cards
        add_card_tag(cards[0]["id"], "shared-tag")
        add_card_tag(cards[1]["id"], "shared-tag")
        tagged = get_cards_by_tag("shared-tag")
        assert len(tagged) == 2

    def test_list_all_tags(self, motion_with_cards):
        _, cards = motion_with_cards
        add_card_tag(cards[0]["id"], "economy")
        add_card_tag(cards[0]["id"], "trade")
        add_card_tag(cards[1]["id"], "economy")
        all_tags = list_all_tags()
        tag_names = {t["tag_name"] for t in all_tags}
        assert "economy" in tag_names
        assert "trade" in tag_names
        # economy has 2 cards, should be first
        assert all_tags[0]["tag_name"] == "economy"
        assert all_tags[0]["card_count"] == 2

    def test_get_cards_by_nonexistent_tag(self, motion_with_cards):
        result = get_cards_by_tag("nonexistent-tag-xyz")
        assert result == []


# ─── Card Ratings ─────────────────────────────────────────────────────────────


class TestCardRatings:
    def test_set_rating(self, motion_with_cards):
        _, cards = motion_with_cards
        card_id = cards[0]["id"]
        set_card_rating(card_id, 5)
        rated = get_cards_by_rating(5)
        assert any(c["id"] == card_id for c in rated)

    def test_rating_clamped_to_range(self, motion_with_cards):
        _, cards = motion_with_cards
        card_id = cards[0]["id"]
        # Should clamp to 5
        set_card_rating(card_id, 10)
        rated = get_cards_by_rating(5)
        assert any(c["id"] == card_id for c in rated)
        # Should clamp to 0
        set_card_rating(card_id, -3)
        rated = get_cards_by_rating(1)
        assert not any(c["id"] == card_id for c in rated)

    def test_get_cards_by_min_rating(self, motion_with_cards):
        _, cards = motion_with_cards
        set_card_rating(cards[0]["id"], 4)
        set_card_rating(cards[1]["id"], 2)
        high_rated = get_cards_by_rating(3)
        assert any(c["id"] == cards[0]["id"] for c in high_rated)
        assert not any(c["id"] == cards[1]["id"] for c in high_rated)

    def test_rating_zero_unrated(self, motion_with_cards):
        _, cards = motion_with_cards
        # New cards default to 0 (unrated)
        all_cards = read_vault(motion_with_cards[0])
        for card in all_cards:
            assert card.get("rating", 0) == 0


# ─── Card History ─────────────────────────────────────────────────────────────


class TestCardHistory:
    def test_log_change(self, motion_with_cards):
        _, cards = motion_with_cards
        card_id = cards[0]["id"]
        log_card_change(card_id, "tag", "Old Tag", "New Tag")
        history = get_card_history(card_id)
        assert len(history) == 1
        assert history[0]["field"] == "tag"
        assert history[0]["old_value"] == "Old Tag"
        assert history[0]["new_value"] == "New Tag"

    def test_multiple_changes_tracked(self, motion_with_cards):
        _, cards = motion_with_cards
        card_id = cards[0]["id"]
        log_card_change(card_id, "tag", "Old", "New")
        log_card_change(card_id, "citation", "Smith", "Jones")
        log_card_change(card_id, "text", "old text", "new text")
        history = get_card_history(card_id)
        assert len(history) == 3

    def test_history_ordered_newest_first(self, motion_with_cards):
        _, cards = motion_with_cards
        card_id = cards[0]["id"]
        log_card_change(card_id, "tag", "A", "B")
        log_card_change(card_id, "tag", "B", "C")
        history = get_card_history(card_id)
        # Newest first
        assert history[0]["new_value"] == "C"
        assert history[1]["new_value"] == "B"

    def test_history_empty_for_new_card(self, motion_with_cards):
        _, cards = motion_with_cards
        history = get_card_history(cards[0]["id"])
        assert history == []


# ─── Flows ────────────────────────────────────────────────────────────────────


class TestFlows:
    def test_save_and_load_flow(self, motion_with_cards):
        mid, _ = motion_with_cards
        flow_data = {
            "Pro Case": ["Arg 1", "Arg 2"],
            "Con Case": ["Counter A"],
        }
        flow_id = save_flow(mid, "Round 1 Flow", flow_data)
        loaded = load_flow(flow_id)
        assert loaded is not None
        assert loaded["name"] == "Round 1 Flow"
        assert loaded["flow_data"] == flow_data

    def test_update_existing_flow(self, motion_with_cards):
        mid, _ = motion_with_cards
        flow_id = save_flow(mid, "My Flow", {"col": ["a"]})
        save_flow(mid, "My Flow", {"col": ["a", "b"]})
        loaded = load_flow(flow_id)
        assert loaded["flow_data"] == {"col": ["a", "b"]}

    def test_list_flows(self, motion_with_cards):
        mid, _ = motion_with_cards
        save_flow(mid, "Flow 1", {})
        save_flow(mid, "Flow 2", {})
        flows = list_flows(mid)
        assert len(flows) == 2

    def test_delete_flow(self, motion_with_cards):
        mid, _ = motion_with_cards
        flow_id = save_flow(mid, "Temp Flow", {})
        delete_flow(flow_id)
        assert load_flow(flow_id) is None

    def test_load_nonexistent_flow(self, test_db):
        assert load_flow(99999) is None

    def test_list_flows_for_motion(self, motion_with_cards):
        mid, _ = motion_with_cards
        mid2 = add_motion("Other Motion")
        save_flow(mid, "Flow A", {})
        save_flow(mid2, "Flow B", {})
        flows = list_flows(mid)
        assert len(flows) == 1
        assert flows[0]["name"] == "Flow A"


# ─── Export Log ───────────────────────────────────────────────────────────────


class TestExportLog:
    def test_log_and_retrieve_export(self, motion_with_cards):
        mid, _ = motion_with_cards
        log_export(mid, "Verbatim DOCX", "/tmp/brief.docx", 15)
        history = get_export_history()
        assert len(history) == 1
        assert history[0]["format"] == "Verbatim DOCX"
        assert history[0]["card_count"] == 15

    def test_multiple_exports(self, motion_with_cards):
        mid, _ = motion_with_cards
        log_export(mid, "Verbatim DOCX", "/tmp/a.docx", 10)
        log_export(mid, "Markdown", "/tmp/b.md", 8)
        log_export(mid, "JSON", "/tmp/c.json", 12)
        history = get_export_history()
        assert len(history) == 3

    def test_export_history_limit(self, motion_with_cards):
        mid, _ = motion_with_cards
        for i in range(10):
            log_export(mid, "CSV", f"/tmp/f{i}.csv", i)
        history = get_export_history(limit=5)
        assert len(history) == 5

    def test_export_includes_motion_name(self, motion_with_cards):
        mid, _ = motion_with_cards
        log_export(mid, "HTML", "/tmp/x.html", 5)
        history = get_export_history()
        assert history[0]["motion_name"] == "Test Motion"


# ─── Statistics ───────────────────────────────────────────────────────────────


class TestVaultStatistics:
    def test_vault_statistics_basic(self, motion_with_cards):
        stats = get_vault_statistics()
        assert stats["total_cards"] == 2
        assert stats["active_motions"] == 1
        assert stats["aff_cards"] == 1
        assert stats["neg_cards"] == 1

    def test_vault_statistics_empty(self, test_db):
        stats = get_vault_statistics()
        assert stats["total_cards"] == 0
        assert stats["active_motions"] == 0

    def test_motion_statistics(self, motion_with_cards):
        mid, _ = motion_with_cards
        stats = get_motion_statistics(mid)
        assert stats["total_cards"] == 2
        assert stats["aff_cards"] == 1
        assert stats["neg_cards"] == 1

    def test_statistics_after_adding_more_motions(self, test_db):
        mid1 = add_motion("Motion 1")
        mid2 = add_motion("Motion 2")
        add_card(mid1, {"tag": "t", "text": "text", "side": "AFF"})
        add_card(mid2, {"tag": "t", "text": "text", "side": "NEG"})
        stats = get_vault_statistics()
        assert stats["total_cards"] == 2
        assert stats["active_motions"] == 2
        assert stats["aff_cards"] == 1
        assert stats["neg_cards"] == 1
