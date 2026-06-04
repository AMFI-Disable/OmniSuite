import random
from typing import Optional
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static

from omnidebate.core.database import read_vault, update_card


class DrillScreen(ModalScreen):
    """Gladiator Drill Mode — spaced-repetition card quiz."""

    def __init__(self, motion_id: int, weak_only: bool = False):
        super().__init__()
        self.motion_id = motion_id
        self.weak_only = weak_only
        self.current_card: Optional[dict] = None
        self.revealed = False

    def compose(self) -> ComposeResult:
        with Container(id="drill-dialog"):
            yield Label(
                "⚔️  GLADIATOR DRILL MODE"
                + ("  ·  WEAK POINTS ONLY" if self.weak_only else "")
            )
            yield Static("Loading...", id="drill-tag")
            yield Static("", id="drill-cite")
            yield Static("", id="drill-card")
            with Horizontal(id="drill-rating"):
                yield Button("1: Poor", id="btn-rate-1", variant="error")
                yield Button("2: Weak", id="btn-rate-2", variant="warning")
                yield Button("3: Fair", id="btn-rate-3", variant="default")
                yield Button("4: Good", id="btn-rate-4", variant="primary")
                yield Button("5: Perfect", id="btn-rate-5", variant="success")
            with Horizontal(classes="drill-footer"):
                yield Button("👁  REVEAL CARD", variant="success", id="btn-reveal")
                yield Button("➡  NEXT CARD", variant="primary", id="btn-next")
                yield Button("✖  EXIT ARENA", variant="error", id="btn-exit")

    def on_mount(self) -> None:
        self._load_card()

    def _load_card(self) -> None:
        cards = read_vault(self.motion_id)
        if self.weak_only:
            cards = [c for c in cards if c.get("mastery", 0) <= 2]
        if not cards:
            self.query_one("#drill-tag", Static).update(
                "🏆 All cards mastered! No cards remaining."
            )
            return
        self.current_card = random.choice(cards)
        self.revealed = False
        c = self.current_card
        side_icon = "🟢" if c["side"] == "AFF" else "🔴"
        self.query_one("#drill-tag", Static).update(
            f"{side_icon} [{c['side']}] {c['tag'].upper()}"
        )
        self.query_one("#drill-cite", Static).update(f"Source: {c['citation']}")
        self.query_one("#drill-card", Static).update(
            "[ Press REVEAL to display evidence ]"
        )

    @on(Button.Pressed, "#btn-reveal")
    def reveal(self) -> None:
        if self.current_card and not self.revealed:
            self.revealed = True
            self.query_one("#drill-card", Static).update(self.current_card["text"])

    @on(Button.Pressed, "#btn-next")
    def next_card(self) -> None:
        self._load_card()

    @on(Button.Pressed, "#btn-exit")
    def exit_drill(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id and event.button.id.startswith("btn-rate-"):
            rating = int(event.button.id.split("-")[-1])
            if self.current_card:
                self.current_card["mastery"] = rating
                update_card(self.current_card["id"], self.current_card)
                self.app.notify(f"Mastery {rating}/5 saved.", severity="information")
                self._load_card()
