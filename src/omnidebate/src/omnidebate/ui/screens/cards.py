import datetime
from typing import Optional
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, TextArea

from omnidebate.core.database import add_card, update_card
from omnidebate.core.logic import smart_cite


class AddCardScreen(ModalScreen):
    """Full-screen modal for adding / editing a card."""

    def __init__(self, motion_id: int, card: Optional[dict] = None):
        super().__init__()
        self.motion_id = motion_id
        self.card = card  # None = add mode, dict = edit mode

    def compose(self) -> ComposeResult:
        c = self.card or {}
        with Container(id="add-card-dialog"):
            yield Label("─── Add / Edit Evidence Card ───")
            yield Label("Tag  (short claim)")
            yield Input(
                value=c.get("tag", ""),
                placeholder="e.g. Economic growth outweighs",
                id="inp-tag",
            )
            yield Label("Citation  (Author, Year, Source)")
            yield Input(
                value=c.get("citation", ""),
                placeholder='e.g. Smith (2023), "Trade Wars"',
                id="inp-cite",
            )
            yield Label("Author  |  Year  (for Smart Cite builder — optional)")
            with Horizontal():
                yield Input(
                    value="", placeholder="Author", id="inp-author", classes="half"
                )
                yield Input(value="", placeholder="Year", id="inp-year", classes="half")
            yield Label("Side")
            yield Select(
                [("AFF – Affirmative", "AFF"), ("NEG – Negative", "NEG")],
                value=c.get("side", "AFF"),
                id="sel-side",
            )
            yield Label("Language")
            yield Select(
                [("English", "EN"), ("German", "DE"), ("Spanish", "ES")],
                value=c.get("language", "EN"),
                id="sel-lang",
            )
            yield Label("Tier  (1 = normal · 3 = ⭐ priority)")
            yield Select(
                [
                    ("1 – Standard", "1"),
                    ("2 – Important", "2"),
                    ("3 – ⭐ Priority", "3"),
                ],
                value=str(c.get("tier", 1)),
                id="sel-tier",
            )
            yield Label("Evidence Text")
            yield TextArea(c.get("text", ""), id="inp-text")
            with Horizontal(id="btn-row"):
                yield Button("💾 Save", variant="success", id="btn-save")
                yield Button("🔑 Smart Cite", variant="primary", id="btn-cite")
                yield Button("✖ Cancel", variant="error", id="btn-cancel")

    @on(Button.Pressed, "#btn-cancel")
    def cancel(self) -> None:
        self.dismiss(None)

    @on(Input.Changed, "#inp-cite")
    def predict_tag(self, event: Input.Changed) -> None:
        """Phase 19: Automatically suggest tags from citation data."""
        tag_inp = self.query_one("#inp-tag", Input)
        if not tag_inp.value.strip() and event.value:
            # Suggest the last meaningful part of the citation
            words = event.value.strip().split()
            if len(words) > 3:
                # Take the last 3-4 words as a potential tag
                suggestion = " ".join(words[-4:])
                tag_inp.placeholder = f"Suggest: {suggestion}"

    @on(Button.Pressed, "#btn-cite")
    def build_cite(self) -> None:
        author = self.query_one("#inp-author", Input).value
        year = self.query_one("#inp-year", Input).value
        tag = self.query_one("#inp-tag", Input).value
        result = smart_cite(author, year, tag, "")
        self.query_one("#inp-cite", Input).value = result

    @on(Button.Pressed, "#btn-save")
    def save_card(self) -> None:
        tag = self.query_one("#inp-tag", Input).value.strip()
        cite = self.query_one("#inp-cite", Input).value.strip()
        text = self.query_one("#inp-text", TextArea).text.strip()
        side = self.query_one("#sel-side", Select).value or "AFF"
        lang = self.query_one("#sel-lang", Select).value or "EN"
        tier = int(self.query_one("#sel-tier", Select).value or "1")

        if not tag or not text:
            self.app.notify("Tag and evidence text are required.", severity="warning")
            return

        card_data = {
            "tag": tag,
            "citation": cite,
            "text": text,
            "side": side,
            "language": lang,
            "tier": tier,
            "timestamp": datetime.date.today().strftime("%Y-%m-%d"),
        }

        if self.card:
            # Edit mode
            update_card(self.card["id"], card_data)
        else:
            # Add mode
            add_card(self.motion_id, card_data)

        self.dismiss(True)
