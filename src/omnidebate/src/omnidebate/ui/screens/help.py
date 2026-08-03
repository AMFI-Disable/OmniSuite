from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Label


class HelpScreen(ModalScreen):
    """Premium Help & Shortcut Reference for OmniDebate."""

    def compose(self) -> ComposeResult:
        with Vertical(id="help-dialog"):
            yield Label("⌨️  SYSTEM COMMAND REFERENCE", id="help-title")
            yield DataTable(id="help-table")
            with Horizontal(classes="dashboard-footer"):
                yield Button("CLOSE [ESC]", variant="primary", id="btn-close")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("MODULE", "KEY", "ACTION")
        table.add_rows(
            [
                ("🧭 NAV", "CTRL+K", "Global Omni-Search"),
                ("🧭 NAV", "[ / ]", "Cycle Motion Tabs"),
                ("🧭 NAV", "UP/DN", "Browse Items"),
                ("📄 DATA", "N", "Create New Card"),
                ("📄 DATA", "E", "Edit Selected Card"),
                ("📄 DATA", "S", "Boolean Search"),
                ("📄 DATA", "W", "Web Ingest/Scraper"),
                ("📄 DATA", "DEL", "Delete Card"),
                ("🧠 INTEL", "Z", "Auto-Synthesize"),
                ("🧠 INTEL", "A", "Strategic Dashboard"),
                ("🧠 INTEL", "I", "Impact Flow Map"),
                ("🧠 INTEL", "D", "Prep Drill Arena"),
                ("⚙️ SYS", "P", "Settings"),
                ("⚙️ SYS", "Q", "Exit OmniDebate"),
                ("⚙️ SYS", "?", "Open this HUD"),
            ]
        )

    @on(Button.Pressed, "#btn-close")
    def close_help(self) -> None:
        self.dismiss()
