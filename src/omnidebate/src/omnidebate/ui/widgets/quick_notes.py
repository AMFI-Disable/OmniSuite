from textual import on
from textual.app import ComposeResult
from textual.widgets import Label, Static, TextArea

from omnidebate.core.database import get_metadata, set_metadata


class QuickNotes(Static):
    """A pinned sticky-note widget with live-save persistence."""

    def compose(self) -> ComposeResult:
        yield Label("📌 QUICK NOTES")
        initial_text = get_metadata("quick_notes", "")
        yield TextArea(initial_text, id="notes-area")

    @on(TextArea.Changed, "#notes-area")
    def save_notes(self, event: TextArea.Changed) -> None:
        self.add_class("notes-saving")
        if hasattr(self, "_save_timer"):
            self._save_timer.stop()
        self._save_timer = self.set_timer(1.0, lambda: self.remove_class("notes-saving"))
        set_metadata("quick_notes", event.text_area.text)
