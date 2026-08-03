from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static


class ExitSummaryScreen(ModalScreen):
    """Premium Session Wrap-up displayed before quitting."""

    def __init__(self, stats: dict):
        super().__init__()
        self.stats = stats

    def compose(self) -> ComposeResult:
        with Vertical(id="exit-dialog"):
            yield Label("🚩 SESSION SUMMARY", classes="exit-title")
            yield Static(f"• Cards added: {self.stats['cards']}", classes="exit-stat")
            yield Static(f"• Drills initiated: {self.stats['drills']}", classes="exit-stat")
            yield Static("• System State: STABLE", classes="exit-stat")
            yield Static("\nAre you sure you want to exit OmniDebate?", classes="hud-label")
            with Horizontal(classes="drill-footer"):
                yield Button("✖ EXIT", variant="error", id="btn-quit")
                yield Button("↩ RESUME", variant="default", id="btn-resume")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-quit":
            self.app.exit()
        else:
            self.dismiss()
