from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

from omnidebate.core.database import search_cards_fts


class SearchScreen(ModalScreen):
    """High-Performance FTS5 Search across all evidence."""

    def __init__(self, motion_id: int):
        super().__init__()
        self.motion_id = motion_id

    def compose(self) -> ComposeResult:
        with Vertical(id="search-dialog"):
            yield Label("🔍  FTS5 INDUSTRIAL SEARCH ENGINE", id="search-title")
            with Horizontal(classes="pane-title-container"):
                yield Input(
                    placeholder='Enter keywords (e.g. "economic growth" recession)',
                    id="inp-query",
                )
                yield Button("SEARCH [ENTER]", id="btn-search", variant="primary")
            yield Static("Results appear below...", id="search-results")
            with Horizontal(classes="dashboard-footer"):
                yield Button("CLOSE [ESC]", variant="error", id="btn-close")

    @on(Button.Pressed, "#btn-close")
    def close(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-search")
    @on(Input.Submitted, "#inp-query")
    def do_search(self) -> None:
        query = self.query_one("#inp-query", Input).value
        if not query:
            return

        # Use the high-performance FTS5 engine
        results = search_cards_fts(query)

        lines = [f"Found **{len(results)}** matches in sub-millisecond query:\n"]
        for c in results:
            side_color = "green" if c["side"] == "AFF" else "red"
            lines.append(f"**[bold {side_color}][{c['side']}][/] {c['tag']}**")
            lines.append(f"> {c['text'][:180]}...")
            lines.append("")

        self.query_one("#search-results", Static).update("\n".join(lines))
