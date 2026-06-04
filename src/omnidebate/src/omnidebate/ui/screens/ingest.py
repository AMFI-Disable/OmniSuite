import datetime
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static

from omnishared.config import load_config
from omnidebate.core.database import add_card
from omnidebate.core.logic import (
    scrape_url,
    summarize_with_ollama,
    summarize_offline,
    WEB_INGEST_OK,
)


class WebIngestScreen(ModalScreen):
    """Scrape a URL and ingest its content as a new evidence card."""

    def __init__(self, motion_id: int):
        super().__init__()
        self.motion_id = motion_id
        self._scraped_title = ""
        self._scraped_body = ""

    def compose(self) -> ComposeResult:
        with Container(id="wi-dialog"):
            yield Label("🌐 Web Ingest  —  Scrape URL into Vault")
            yield Input(
                placeholder="https://...",
                id="wi-url",
                tooltip="URL of the debate evidence article.",
            )
            with Horizontal():
                yield Button(
                    "🔍 Fetch",
                    variant="primary",
                    id="wi-fetch",
                    tooltip="Extract text from the provided URL.",
                )
                yield Button(
                    "🤖 AI Summarize",
                    variant="warning",
                    id="wi-ai",
                    tooltip="Use local AI to summarize the article.",
                )
                yield Button(
                    "✖ Cancel",
                    variant="error",
                    id="wi-cancel",
                    tooltip="Close without saving.",
                )
            yield Static("", id="wi-status")
            yield Label("Preview (first 500 chars):")
            yield Static("No content fetched yet.", id="wi-preview")
            yield Label("Tag for this evidence:")
            yield Input(
                placeholder="e.g. Trade deficit argument",
                id="wi-tag",
                tooltip="Main claim or headline for this card.",
            )
            yield Label("Side:")
            yield Select(
                [("AFF", "AFF"), ("NEG", "NEG")],
                value="AFF",
                id="wi-side",
                tooltip="Select which side this evidence supports.",
            )
            yield Label("Tier:")
            yield Select(
                [
                    ("1 – Standard", "1"),
                    ("2 – Important", "2"),
                    ("3 – ⭐ Priority", "3"),
                ],
                value="1",
                id="wi-tier",
                tooltip="Strategic priority level.",
            )
            with Horizontal():
                yield Button(
                    "💾 Ingest to Vault",
                    variant="success",
                    id="wi-save",
                    tooltip="Permanently save this card to the database.",
                )

    @on(Button.Pressed, "#wi-cancel")
    def cancel(self) -> None:
        self.dismiss(None)

    def _fetch_core(self) -> bool:
        if not WEB_INGEST_OK:
            self.app.notify(
                "Install requests + beautifulsoup4 for web ingest.", severity="error"
            )
            return False
        url = self.query_one("#wi-url", Input).value.strip()
        if not url:
            self.app.notify("Enter a URL first.", severity="warning")
            return False
        self.query_one("#wi-status", Static).update("⏳ Fetching…")
        try:
            title, body = scrape_url(url)
            self._scraped_title = title
            self._scraped_body = body
            return True
        except Exception as e:
            self.query_one("#wi-status", Static).update(f"❌ Error: {e}")
            return False

    @on(Button.Pressed, "#wi-fetch")
    def fetch(self) -> None:
        if self._fetch_core():
            self.query_one("#wi-status", Static).update(
                f"✅ Fetched: {self._scraped_title}"
            )
            self.query_one("#wi-preview", Static).update(
                self._scraped_body[:500]
                + ("…" if len(self._scraped_body) > 500 else "")
            )
            self.query_one("#wi-tag", Input).value = self._scraped_title[:80]

    @on(Button.Pressed, "#wi-ai")
    def ai_summarize(self) -> None:
        if not self._fetch_core():
            return

        self.query_one("#wi-status", Static).update("🧠 [bold]AI SUMMARIZING...[/bold]")
        cfg = load_config()
        ai_cfg = cfg.get("ai", {})
        ep = ai_cfg.get("ollama_endpoint", "http://localhost:11434")
        md = ai_cfg.get("ollama_model", "llama3")

        try:
            tag, summary = summarize_with_ollama(self._scraped_body, ep, md)
            self._scraped_body = summary
            self.query_one("#wi-status", Static).update(
                "✨ [bold]AI SYNTHESIS COMPLETE[/bold]"
            )
            self.query_one("#wi-preview", Static).update(
                summary[:500] + ("…" if len(summary) > 500 else "")
            )
            self.query_one("#wi-tag", Input).value = tag
            self.app.notify("AI Summary Generated", severity="information")
        except Exception as e:
            self.app.notify(
                f"AI Failed: {e}. Falling back to offline heuristics.",
                severity="warning",
            )
            try:
                tag, summary = summarize_offline(
                    self._scraped_body, self._scraped_title
                )
                self._scraped_body = summary
                self.query_one("#wi-status", Static).update(
                    "✨ [bold]AI SYNTHESIS COMPLETE (Semantic Fallback)[/bold]"
                )
                self.query_one("#wi-preview", Static).update(
                    summary[:500] + ("…" if len(summary) > 500 else "")
                )
                self.query_one("#wi-tag", Input).value = tag
                self.app.notify(
                    "AI Summary (Heuristic Fallback)", severity="information"
                )
            except Exception as ex:
                self.query_one("#wi-status", Static).update(f"❌ Fallback Error: {ex}")
                self.fetch()

    @on(Button.Pressed, "#wi-save")
    def save(self) -> None:
        if not self._scraped_body:
            self.app.notify("Fetch a URL first.", severity="warning")
            return
        tag = self.query_one("#wi-tag", Input).value.strip() or self._scraped_title
        side = self.query_one("#wi-side", Select).value or "AFF"
        tier = int(self.query_one("#wi-tier", Select).value or "1")
        url_val = self.query_one("#wi-url", Input).value.strip()

        card_data = {
            "tag": tag,
            "citation": f"Web Ingest — {url_val}",
            "side": side,
            "text": self._scraped_body[:2000],
            "language": "EN",
            "mastery": 0,
            "tier": tier,
            "timestamp": datetime.date.today().strftime("%Y-%m-%d"),
        }

        add_card(self.motion_id, card_data)

        self.app.notify(f"✅ Ingested: '{tag}'", severity="information")
        self.dismiss(True)
