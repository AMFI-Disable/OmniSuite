from textual.app import ComposeResult
from textual.widgets import Button, Static


class SideRibbon(Static):
    """High-density vertical navigation ribbon."""

    def compose(self) -> ComposeResult:
        yield Button("🏠\nVAULT", id="rb-home", classes="ribbon-btn")
        yield Button("🔍\nFIND", id="rb-search", classes="ribbon-btn")
        yield Button("📈\nSTATS", id="rb-stats", classes="ribbon-btn")
        yield Button("⚙️\nPREFS", id="rb-pref", classes="ribbon-btn")
