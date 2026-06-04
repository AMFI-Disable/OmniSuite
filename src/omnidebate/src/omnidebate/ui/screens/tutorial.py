from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Static, Button
from textual.containers import Vertical, ScrollableContainer


class TutorialScreen(ModalScreen):
    """Interactive Onboarding Tutorial for First-Time Users."""

    def compose(self) -> ComposeResult:
        with Vertical(id="tutorial-dialog"):
            yield Label("🏆  WELCOME TO OMNIDEBATE ACADEMY", classes="tutorial-title")
            with ScrollableContainer():
                yield Static(
                    "\n[bold]1. The Motion Navigator (Left)[/]\nCreate and select your debate motions here. Use [Archive] to keep your vault clean.\n"
                )
                yield Static(
                    "[bold]2. Evidence Feed (Center)[/]\nThis is your library. Click any card to see full citations and impact mappings.\n"
                )
                yield Static(
                    "[bold]3. Chronos Engine (Right)[/]\nYour debate HUD. Track speech time and prep reservoirs for all formats (PF, LD, Policy).\n"
                )
                yield Static(
                    "[bold]4. Boolean Search [S][/]\nSearch thousands of cards in milliseconds using standard logical operators.\n"
                )
                yield Static(
                    "[bold]5. Web Ingest [W][/]\nPaste a URL to instantly scrape evidence into your active motion.\n"
                )
                yield Static(
                    "[bold]6. Gladiator Drill [D][/]\nTest your memory. Master your evidence using our spaced-repetition trainer.\n"
                )
            yield Button("🚀 START RESEARCHING", variant="success", id="btn-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close":
            self.dismiss()
