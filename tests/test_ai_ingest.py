import os
import pytest
from unittest.mock import patch, MagicMock
from textual.app import App
from omnidebate.core.database import setup_db
from omnidebate.core.logic import summarize_with_ollama, summarize_offline
from omnidebate.ui.screens.ingest import WebIngestScreen


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


def test_offline_summarizer_heuristics():
    # Test tag extraction and warrant extraction
    title = "Why climate change leads to economic collapse and extinction"
    text = (
        "Climate change causes global warming. This leads to severe warming. "
        "Consequently, we see a massive loss in global GDP. "
        "Extinction of key species is highly probable if warming continues. "
        "This proves that action is needed because the climate threat is real."
    )
    tag, brief = summarize_offline(text, title)

    # 5-8 words tag check
    assert len(tag.split()) >= 3 and len(tag.split()) <= 8

    # Debate keywords checks (GDP, warming, extinction, leads to, causes, because)
    # The top 3 sentences should contain some of these
    assert any(
        kw in brief.lower()
        for kw in ["gdp", "warming", "extinction", "leads to", "causes", "because"]
    )

    # Check bullet points format
    assert brief.startswith("- ")
    assert len(brief.split("\n")) <= 3


@patch("requests.post")
def test_summarize_with_ollama_mock(mock_post):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "response": "TAG: Debate Victory Road\nBRIEF: - Point A\n- Point B"
    }
    mock_post.return_value = mock_resp

    tag, brief = summarize_with_ollama(
        "Some text to summarize", "http://localhost:11434", "llama3"
    )
    assert tag == "Debate Victory Road"
    assert "- Point A" in brief


class WebIngestTestApp(App):
    def __init__(self, motion_id=1):
        super().__init__()
        self.motion_id = motion_id

    def on_mount(self):
        self.push_screen(WebIngestScreen(self.motion_id))


@pytest.mark.asyncio
@patch("omnidebate.ui.screens.ingest.scrape_url")
@patch("omnidebate.ui.screens.ingest.summarize_with_ollama")
async def test_web_ingest_screen_fallback(mock_summarize, mock_scrape):
    # Mock scrape_url to return title and body
    mock_scrape.return_value = (
        "Test Title",
        "Climate change is real. It causes warming. Consequently, extinction of species leads to crisis.",
    )

    # Mock summarize_with_ollama to fail (timeout/connection error)
    mock_summarize.side_effect = Exception("Ollama server offline")

    app = WebIngestTestApp()
    async with app.run_test() as pilot:
        # Check modal screen widgets
        screen = app.screen
        assert screen.query_one("#wi-url")
        assert screen.query_one("#wi-fetch")
        assert screen.query_one("#wi-ai")
        assert screen.query_one("#wi-cancel")
        assert screen.query_one("#wi-status")
        assert screen.query_one("#wi-preview")
        assert screen.query_one("#wi-tag")
        assert screen.query_one("#wi-save")

        # Set URL value
        url_input = screen.query_one("#wi-url")
        url_input.value = "https://example.com/debate"

        # Click Fetch to verify fetch works first
        await pilot.click("#wi-fetch")
        assert screen.query_one("#wi-tag").value == "Test Title"

        # Now click AI Summarize to trigger fallback
        await pilot.click("#wi-ai")
        await pilot.pause()

        # Status should be updated to fallback status
        status_text = str(screen.query_one("#wi-status").render())
        assert "Semantic Fallback" in status_text

        # Check that tag and preview have been updated by offline summarizer
        tag_val = screen.query_one("#wi-tag").value
        assert len(tag_val.split()) >= 3 and len(tag_val.split()) <= 8

        # Save to verify card is ingested
        await pilot.click("#wi-save")
        await pilot.pause()
