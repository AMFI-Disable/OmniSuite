import os

import pytest
from omnidebate.core.database import setup_db
from omnidebate.ui.app import OmniDebate


@pytest.fixture(autouse=True)
def test_db(tmp_path):
    db_file = tmp_path / "test_vault.db"
    os.environ["EVIDENCE_VAULT_DB"] = str(db_file)
    setup_db()
    yield
    if "EVIDENCE_VAULT_DB" in os.environ:
        del os.environ["EVIDENCE_VAULT_DB"]


@pytest.mark.asyncio
async def test_ui_mount():
    app = OmniDebate()
    async with app.run_test():
        # Verify main zones are present
        assert app.query_one("#zone-epsilon")
        assert app.query_one("#zone-alpha")
        assert app.query_one("#zone-beta")
        assert app.query_one("#zone-gamma")
        assert app.query_one("#zone-delta")

        # Verify header title
        assert "OmniDebate" in app.title


@pytest.mark.asyncio
async def test_ui_shortcuts_and_filters():
    app = OmniDebate()
    async with app.run_test() as pilot:
        # Check bindings exist
        bindings = {b.key: b.action for b in app.BINDINGS}
        assert "h" in bindings
        assert "n" in bindings
        assert "e" in bindings
        assert "delete" in bindings
        assert "w" in bindings

        # Test live search filtering
        app.active_motion_id = 1
        # Set mock evidence cards
        cards = [
            {
                "id": 1,
                "tag": "Apple card",
                "text": "Apples are red.",
                "side": "AFF",
                "tier": 1,
            },
            {
                "id": 2,
                "tag": "Banana card",
                "text": "Bananas are yellow.",
                "side": "NEG",
                "tier": 2,
            },
        ]

        # Override reload_evidence database fetch to test ui filtering in isolation
        def mock_reload():
            el = app.query_one("#evidence-list")
            el.clear()
            query = app.query_one("#evidence-filter").value.strip().lower()
            filtered = cards
            if query:
                filtered = [c for c in filtered if query in c["tag"].lower()]
            from textual.containers import Vertical
            from textual.widgets import Label, ListItem, Static

            for c in filtered:
                row = Vertical(Label(c["tag"]), Static(c["text"]))
                el.mount(ListItem(row))

        app._reload_evidence = mock_reload
        app._reload_evidence()

        # Verify both cards are present initially
        el_list = app.query_one("#evidence-list")
        assert len(el_list.children) == 2

        # Change search input value
        search_input = app.query_one("#evidence-filter")
        search_input.value = "Apple"
        await pilot.pause()

        # Verify list filtered to only Apple card
        assert len(el_list.children) == 1
