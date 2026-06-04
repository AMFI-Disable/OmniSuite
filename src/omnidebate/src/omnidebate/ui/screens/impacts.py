from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static

from omnidebate.core.logic import impact_tree


class ImpactMapScreen(ModalScreen):
    """Show High-Fidelity ASCII impact tree for the selected card."""

    def __init__(self, card: dict):
        super().__init__()
        self.card = card

    def compose(self) -> ComposeResult:
        with Vertical(id="impact-dialog"):
            yield Label("🗺️  STRATEGIC IMPACT VISUALIZER", id="impact-title")
            yield Static(impact_tree(self.card), id="impact-tree")
            yield Button("CLOSE [ESC]", variant="primary", id="btn-close")

    @on(Button.Pressed, "#btn-close")
    def close(self) -> None:
        self.dismiss(None)
