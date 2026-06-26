import os
import pytest
from textual.app import App
from omnidebate.core.database import setup_db, add_motion, add_card, read_vault
from omnidebate.core.oracle import OracleEngine
from omnidebate.ui.screens.compare import CompareScreen


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


class CompareTestApp(App):
    """Test harness to mount CompareScreen."""

    def __init__(self, card_a, card_b):
        super().__init__()
        self.card_a = card_a
        self.card_b = card_b

    def on_mount(self):
        self.push_screen(CompareScreen(self.card_a, self.card_b))


def test_weigh_evidence():
    """Verify that weigh_evidence correctly scores cards with varying tier/mastery levels."""
    card_a = {
        "tag": "Carbon Tax Good",
        "citation": "Smith 2026",
        "text": "A carbon tax reduces emissions because since it provides strong economic incentives.",
        "side": "AFF",
        "tier": 3,
        "mastery": 3,
    }
    card_b = {
        "tag": "Carbon Tax Bad",
        "citation": "Jones 2025",
        "text": "Carbon taxes are bad.",
        "side": "NEG",
        "tier": 1,
        "mastery": 0,
    }

    result = OracleEngine.weigh_evidence(card_a, card_b)

    assert result["winner"] == "A"
    assert result["score_a"] > result["score_b"]
    assert result["resilience_a"] > result["resilience_b"]
    assert result["warrant_density_a"] > result["warrant_density_b"]

    # Test reverse
    card_a["tier"] = 1
    card_a["mastery"] = 0
    card_b["tier"] = 3
    card_b["mastery"] = 3

    result_reverse = OracleEngine.weigh_evidence(card_a, card_b)
    assert result_reverse["winner"] == "B"
    assert result_reverse["score_b"] > result_reverse["score_a"]


@pytest.mark.asyncio
async def test_compare_modal_mounting():
    """Verify compare modal mounting and UI layout structure."""
    card_a = {
        "id": 1,
        "tag": "AFF Card",
        "citation": "Cite A",
        "text": "Card text A",
        "side": "AFF",
        "tier": 2,
    }
    card_b = {
        "id": 2,
        "tag": "NEG Card",
        "citation": "Cite B",
        "text": "Card text B",
        "side": "NEG",
        "tier": 2,
    }

    app = CompareTestApp(card_a, card_b)
    async with app.run_test():
        # Check containers and title
        assert app.screen.query_one("#compare-container")
        assert app.screen.query_one("#compare-title")
        assert app.screen.query_one("#verdict-banner")

        # Check side-by-side panes
        assert app.screen.query_one("#pane-card-a")
        assert app.screen.query_one("#pane-card-b")

        # Check metrics gauges
        assert app.screen.query_one("#gauge-res-a")
        assert app.screen.query_one("#gauge-warr-a")
        assert app.screen.query_one("#gauge-fact-a")
        assert app.screen.query_one("#gauge-res-b")
        assert app.screen.query_one("#gauge-warr-b")
        assert app.screen.query_one("#gauge-fact-b")

        # Check resolution buttons
        assert app.screen.query_one("#btn-prior-a")
        assert app.screen.query_one("#btn-prior-b")
        assert app.screen.query_one("#btn-equalize")
        assert app.screen.query_one("#btn-close")


@pytest.mark.asyncio
async def test_resolution_decisions_db():
    """Verify database update logic upon selecting conflict resolution paths."""
    mid = add_motion("Climate Change")
    card_a_data = {
        "tag": "AFF Card",
        "citation": "Smith 2026",
        "side": "AFF",
        "text": "AFF text content...",
        "tier": 2,
    }
    card_b_data = {
        "tag": "NEG Card",
        "citation": "Jones 2026",
        "side": "NEG",
        "text": "NEG text content...",
        "tier": 2,
    }

    add_card(mid, card_a_data)
    add_card(mid, card_b_data)

    cards = read_vault(mid)
    card_a = cards[0]
    card_b = cards[1]

    # 1. Test Prioritize A
    app_a = CompareTestApp(card_a, card_b)
    async with app_a.run_test() as pilot:
        await pilot.click("#btn-prior-a")

    updated_cards = read_vault(mid)
    # Check that Card A is promoted to 3 and Card B is demoted to 1
    assert next(c for c in updated_cards if c["id"] == card_a["id"])["tier"] == 3
    assert next(c for c in updated_cards if c["id"] == card_b["id"])["tier"] == 1

    # Restore tiers to 2
    card_a["tier"] = 2
    card_b["tier"] = 2

    # 2. Test Prioritize B
    app_b = CompareTestApp(card_a, card_b)
    async with app_b.run_test() as pilot:
        await pilot.click("#btn-prior-b")

    updated_cards = read_vault(mid)
    assert next(c for c in updated_cards if c["id"] == card_a["id"])["tier"] == 1
    assert next(c for c in updated_cards if c["id"] == card_b["id"])["tier"] == 3

    # Restore tiers to 2
    card_a["tier"] = 2
    card_b["tier"] = 2

    # 3. Test Equalize
    app_eq = CompareTestApp(card_a, card_b)
    async with app_eq.run_test() as pilot:
        await pilot.click("#btn-equalize")

    updated_cards = read_vault(mid)
    assert next(c for c in updated_cards if c["id"] == card_a["id"])["tier"] == 2
    assert next(c for c in updated_cards if c["id"] == card_b["id"])["tier"] == 2
