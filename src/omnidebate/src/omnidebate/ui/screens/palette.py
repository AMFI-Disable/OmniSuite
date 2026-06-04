from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, ListView, ListItem, Label
from textual.containers import Vertical
from omnidebate.core.database import search_cards_fts


class CommandPaletteScreen(ModalScreen):
    """Phase 3200: High-speed Omni-Search Palette."""

    def compose(self) -> ComposeResult:
        with Vertical(id="palette-container"):
            yield Input(
                placeholder="🔍 OMNI-SEARCH: Type keywords to find any card...",
                id="palette-input",
            )
            yield ListView(id="palette-results")

    @on(Input.Changed, "#palette-input")
    def search_all(self, event: Input.Changed) -> None:
        results = search_cards_fts(event.value)
        lv = self.query_one("#palette-results", ListView)
        lv.clear()
        for r in results[:10]:
            item = ListItem(
                Label(f"[{r['side']}] {r['tag']} — {r['motion_name']}"),
                classes="result-item",
            )
            item._card_data = r
            lv.mount(item)

    @on(ListView.Selected, "#palette-results")
    def select_result(self, event: ListView.Selected) -> None:
        self.dismiss(getattr(event.item, "_card_data", None))
