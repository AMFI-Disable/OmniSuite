from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import Vertical
from textual import on


class CardActionScreen(ModalScreen):
    """Quick Context Menu for evidence card actions."""

    def __init__(self, card: dict):
        super().__init__()
        self.card = card

    def compose(self) -> ComposeResult:
        with Vertical(id="action-dialog"):
            yield Label(f"📄 CARD #{self.card['id']} ACTIONS", classes="pane-title")
            yield Button("📋 COPY TO CLIPBOARD", id="btn-copy", variant="primary")
            yield Button("🔗 MOVE TO MOTION", id="btn-move", variant="default")
            yield Button("⭐ PROMOTE TO TIER-3", id="btn-promote", variant="success")
            yield Button("✖ CANCEL [ESC]", id="btn-cancel", variant="error")

    @on(Button.Pressed, "#btn-cancel")
    def cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-copy")
    def copy_to_clipboard(self) -> None:
        # In a real TUI we'd use pyperclip or similar
        # For now we'll notify and return a special code
        self.dismiss(("copy", self.card))

    @on(Button.Pressed, "#btn-promote")
    def promote_card(self) -> None:
        self.dismiss(("promote", self.card))

    @on(Button.Pressed, "#btn-move")
    def move_card(self) -> None:
        self.dismiss(("move", self.card))
