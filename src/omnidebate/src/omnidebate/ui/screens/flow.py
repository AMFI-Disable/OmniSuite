"""Debate Flow Screen — Multi-Column Argument Flowing Interface.

The #1 missing feature in debate TUIs: a real-time, keyboard-driven flowing
interface that lets debaters track arguments across speeches in a structured
column layout (e.g., 4 columns for PF: Pro Case, Con Case, Pro Rebuttal,
Con Rebuttal).

Each column is a scrollable list of flow entries (short argument summaries),
and entries can be linked to cards in the vault or marked as responses to
earlier arguments with visual ``←`` indicators.

© 2026 OmniSuite. Built for the Digital Grandmaster.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, ListItem, ListView, Static


# ── Data Structures ──────────────────────────────────────────────────────────


@dataclass
class FlowEntry:
    """A single argument entry inside a flow column.

    Attributes:
        text: Short argument summary.
        linked_card_id: Optional reference to a card in the evidence vault.
        response_to: Optional index of the entry this responds to (within the
            *previous* column), enabling cross-column response arrows.
    """

    text: str
    linked_card_id: Optional[int] = None
    response_to: Optional[int] = None


# Default column definitions for Public Forum (PF) format.
DEFAULT_COLUMNS: list[dict[str, str]] = [
    {"name": "Pro Case", "side": "pro"},
    {"name": "Con Case", "side": "con"},
    {"name": "Pro Rebuttal", "side": "pro"},
    {"name": "Con Rebuttal", "side": "con"},
]


# ── Widgets ──────────────────────────────────────────────────────────────────


class FlowColumn(Vertical):
    """A single scrollable column within the flow sheet.

    Manages its own list of :class:`FlowEntry` objects and maintains a cursor
    for the currently-selected entry.
    """

    DEFAULT_CSS = """
    FlowColumn {
        width: 1fr;
        height: 1fr;
        border: solid $surface-lighten-2;
        padding: 0 1;
    }
    FlowColumn.pro {
        background: $primary-background-darken-3;
        border: solid $primary-darken-2;
    }
    FlowColumn.con {
        background: $error-background-darken-3;
        border: solid $error-darken-2;
    }
    FlowColumn .flow-column-header {
        text-style: bold;
        width: 100%;
        content-align: center middle;
        padding: 0 1;
        margin-bottom: 1;
    }
    FlowColumn.pro .flow-column-header {
        color: $primary-lighten-2;
    }
    FlowColumn.con .flow-column-header {
        color: $error-lighten-2;
    }
    FlowColumn .flow-entry {
        padding: 0 1;
        height: auto;
    }
    FlowColumn .flow-entry.selected {
        background: $accent-darken-1;
        text-style: bold;
    }
    FlowColumn .flow-entry .response-arrow {
        color: $warning;
    }
    FlowColumn .flow-entry .link-badge {
        color: $success;
    }
    FlowColumn.active {
        border: heavy $accent;
    }
    """

    def __init__(
        self,
        column_name: str,
        side: str,
        column_index: int,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.column_name = column_name
        self.side = side
        self.column_index = column_index
        self.entries: list[FlowEntry] = []
        self.cursor: int = -1  # -1 = no selection
        self.add_class(side)

    def compose(self) -> ComposeResult:
        """Render the column header and entry list."""
        side_icon = "🔵" if self.side == "pro" else "🔴"
        yield Label(
            f"{side_icon} {self.column_name.upper()}",
            classes="flow-column-header",
        )
        yield ListView(id=f"flow-list-{self.column_index}")

    # ── Entry Management ─────────────────────────────────────────────────

    def add_entry(self, entry: FlowEntry) -> None:
        """Append *entry* to this column and refresh the display."""
        self.entries.append(entry)
        self.cursor = len(self.entries) - 1
        self._refresh_entries()

    def edit_entry(self, index: int, new_text: str) -> None:
        """Update the text of the entry at *index*."""
        if 0 <= index < len(self.entries):
            self.entries[index].text = new_text
            self._refresh_entries()

    def delete_entry(self, index: int) -> None:
        """Remove the entry at *index* and adjust the cursor."""
        if 0 <= index < len(self.entries):
            self.entries.pop(index)
            if self.cursor >= len(self.entries):
                self.cursor = len(self.entries) - 1
            self._refresh_entries()

    def link_entry(self, index: int, card_id: int) -> None:
        """Attach a vault card ID to the entry at *index*."""
        if 0 <= index < len(self.entries):
            self.entries[index].linked_card_id = card_id
            self._refresh_entries()

    def move_cursor(self, delta: int) -> None:
        """Move the cursor up (``-1``) or down (``+1``)."""
        if not self.entries:
            return
        self.cursor = max(0, min(len(self.entries) - 1, self.cursor + delta))
        self._refresh_entries()

    # ── Display ──────────────────────────────────────────────────────────

    def _refresh_entries(self) -> None:
        """Rebuild the :class:`ListView` contents from ``self.entries``."""
        try:
            lv = self.query_one(f"#flow-list-{self.column_index}", ListView)
            lv.clear()
        except Exception:
            return

        for idx, entry in enumerate(self.entries):
            parts: list[str] = []

            # Response arrow indicator
            if entry.response_to is not None:
                parts.append(f"← [{entry.response_to + 1}]")

            # Main text
            parts.append(entry.text)

            # Linked-card badge
            if entry.linked_card_id is not None:
                parts.append(f"🔗{entry.linked_card_id}")

            display = " ".join(parts)
            label = Label(display, classes="flow-entry")
            if idx == self.cursor:
                label.add_class("selected")
            lv.mount(ListItem(label))

    def set_active(self, active: bool) -> None:
        """Toggle the ``active`` CSS class on this column."""
        self.set_class(active, "active")


# ── Input Modals ─────────────────────────────────────────────────────────────


class FlowInputOverlay(Vertical):
    """Inline input overlay for adding / editing flow entries.

    This avoids pushing a full modal screen — the overlay sits inside the
    flow sheet itself.
    """

    DEFAULT_CSS = """
    FlowInputOverlay {
        dock: bottom;
        height: auto;
        max-height: 5;
        background: $surface;
        border-top: solid $accent;
        padding: 0 2;
    }
    FlowInputOverlay Label {
        margin-right: 1;
    }
    """

    def __init__(self, prompt: str = "Entry text:", input_id: str = "flow-input"):
        super().__init__()
        self.prompt = prompt
        self.input_id = input_id

    def compose(self) -> ComposeResult:
        yield Label(self.prompt)
        yield Input(placeholder="Type argument summary…", id=self.input_id)


# ── Main Screen ─────────────────────────────────────────────────────────────


class FlowScreen(Screen):
    """Multi-column debate flow screen.

    Provides a real-time, keyboard-driven flowing interface for tracking
    arguments across speeches in a structured column layout.

    Default layout is PF (Public Forum) with four columns:
    Pro Case · Con Case · Pro Rebuttal · Con Rebuttal.

    Keyboard shortcuts
    ------------------
    - ``Enter`` — add new entry to current column
    - ``Tab`` / ``Shift+Tab`` — move between columns
    - ``Up`` / ``Down`` — navigate entries within a column
    - ``e`` — edit selected entry
    - ``d`` — delete selected entry
    - ``l`` — link entry to a vault card
    - ``x`` — export flow to markdown
    - ``Escape`` — back to main
    """

    BINDINGS = [
        Binding("enter", "add_entry", "Add Entry", show=True),
        Binding("tab", "next_column", "Next Column", show=True),
        Binding("shift+tab", "prev_column", "Prev Column", show=True),
        Binding("up", "cursor_up", "Move Up", show=False),
        Binding("down", "cursor_down", "Move Down", show=False),
        Binding("e", "edit_entry", "Edit", show=True),
        Binding("d", "delete_entry", "Delete", show=True),
        Binding("l", "link_card", "Link Card", show=True),
        Binding("x", "export_flow", "Export MD", show=True),
        Binding("escape", "go_back", "Back", show=True),
    ]

    DEFAULT_CSS = """
    FlowScreen {
        layout: vertical;
    }
    #flow-columns {
        height: 1fr;
    }
    #flow-status-bar {
        dock: bottom;
        height: 1;
        background: $surface;
        padding: 0 2;
        color: $text-muted;
    }
    """

    def __init__(
        self,
        columns: list[dict[str, str]] | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.column_defs = columns or DEFAULT_COLUMNS
        self.active_column: int = 0
        self._input_mode: str | None = None  # "add", "edit", "link", "response"

    # ── Compose ──────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        """Build the flow screen layout: Header → columns → status bar → Footer."""
        yield Header(show_clock=True)

        with Horizontal(id="flow-columns"):
            for idx, col_def in enumerate(self.column_defs):
                yield FlowColumn(
                    column_name=col_def["name"],
                    side=col_def.get("side", "pro"),
                    column_index=idx,
                    id=f"flow-col-{idx}",
                )

        yield Static("", id="flow-status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Activate the first column on mount."""
        self._set_active_column(0)

    # ── Column Navigation ────────────────────────────────────────────────

    def _get_column(self, index: int) -> FlowColumn:
        """Return the :class:`FlowColumn` widget at *index*."""
        return self.query_one(f"#flow-col-{index}", FlowColumn)

    def _set_active_column(self, index: int) -> None:
        """Deactivate the current column and activate column *index*."""
        for i in range(len(self.column_defs)):
            self._get_column(i).set_active(i == index)
        self.active_column = index
        self._update_status()

    def action_next_column(self) -> None:
        """Move focus to the next column (wraps around)."""
        new = (self.active_column + 1) % len(self.column_defs)
        self._set_active_column(new)

    def action_prev_column(self) -> None:
        """Move focus to the previous column (wraps around)."""
        new = (self.active_column - 1) % len(self.column_defs)
        self._set_active_column(new)

    # ── Cursor Navigation ────────────────────────────────────────────────

    def action_cursor_up(self) -> None:
        """Move the cursor up within the active column."""
        self._get_column(self.active_column).move_cursor(-1)
        self._update_status()

    def action_cursor_down(self) -> None:
        """Move the cursor down within the active column."""
        self._get_column(self.active_column).move_cursor(1)
        self._update_status()

    # ── Entry Management ─────────────────────────────────────────────────

    def action_add_entry(self) -> None:
        """Show inline input to add a new flow entry."""
        if self._input_mode is not None:
            return  # Already in an input mode
        self._input_mode = "add"
        overlay = FlowInputOverlay(
            prompt=f"New entry for [{self.column_defs[self.active_column]['name']}]:",
            input_id="flow-input",
        )
        self.mount(overlay)
        self.call_after_refresh(lambda: self.query_one("#flow-input", Input).focus())

    def action_edit_entry(self) -> None:
        """Show inline input to edit the selected flow entry."""
        col = self._get_column(self.active_column)
        if col.cursor < 0 or col.cursor >= len(col.entries):
            self.app.notify("No entry selected to edit.", severity="warning")
            return
        if self._input_mode is not None:
            return
        self._input_mode = "edit"
        current_text = col.entries[col.cursor].text
        overlay = FlowInputOverlay(prompt="Edit entry:", input_id="flow-input")
        self.mount(overlay)

        def _prefill() -> None:
            inp = self.query_one("#flow-input", Input)
            inp.value = current_text
            inp.focus()

        self.call_after_refresh(_prefill)

    def action_delete_entry(self) -> None:
        """Delete the selected entry from the active column."""
        col = self._get_column(self.active_column)
        if col.cursor < 0 or col.cursor >= len(col.entries):
            self.app.notify("No entry selected to delete.", severity="warning")
            return
        deleted_text = col.entries[col.cursor].text
        col.delete_entry(col.cursor)
        self.app.notify(f"Deleted: {deleted_text[:40]}…", severity="information")
        self._update_status()

    def action_link_card(self) -> None:
        """Show inline input to link a vault card ID to the selected entry."""
        col = self._get_column(self.active_column)
        if col.cursor < 0 or col.cursor >= len(col.entries):
            self.app.notify("No entry selected to link.", severity="warning")
            return
        if self._input_mode is not None:
            return
        self._input_mode = "link"
        overlay = FlowInputOverlay(
            prompt="Enter card ID to link:", input_id="flow-input"
        )
        self.mount(overlay)
        self.call_after_refresh(lambda: self.query_one("#flow-input", Input).focus())

    @on(Input.Submitted, "#flow-input")
    def _handle_input_submit(self, event: Input.Submitted) -> None:
        """Process submission from the inline input overlay."""
        value = event.value.strip()
        col = self._get_column(self.active_column)

        if self._input_mode == "add" and value:
            # Check for response syntax: ">N actual text" links to entry N-1
            response_to: int | None = None
            text = value
            if value.startswith(">"):
                parts = value[1:].split(" ", 1)
                try:
                    response_to = int(parts[0]) - 1  # User-facing is 1-based
                    text = parts[1] if len(parts) > 1 else value
                except (ValueError, IndexError):
                    text = value
                    response_to = None

            entry = FlowEntry(text=text, response_to=response_to)
            col.add_entry(entry)
            self.app.notify("Entry added.", severity="information")

        elif self._input_mode == "edit" and value:
            col.edit_entry(col.cursor, value)
            self.app.notify("Entry updated.", severity="information")

        elif self._input_mode == "link" and value:
            try:
                card_id = int(value)
                col.link_entry(col.cursor, card_id)
                self.app.notify(f"Linked to card #{card_id}.", severity="success")
            except ValueError:
                self.app.notify("Invalid card ID.", severity="error")

        self._dismiss_input()
        self._update_status()

    def _dismiss_input(self) -> None:
        """Remove the inline input overlay and reset input mode."""
        self._input_mode = None
        try:
            overlay = self.query_one(FlowInputOverlay)
            overlay.remove()
        except Exception:
            pass

    # ── Export ────────────────────────────────────────────────────────────

    def action_export_flow(self) -> None:
        """Export the entire flow to a markdown file."""
        md = self._generate_markdown()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"flow_export_{timestamp}.md"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(md)
            self.app.notify(
                f"Flow exported to {filename}", severity="success"
            )
        except OSError as exc:
            self.app.notify(f"Export failed: {exc}", severity="error")

    def _generate_markdown(self) -> str:
        """Build a markdown table from all flow columns.

        Returns:
            A markdown string with one column per speech and rows for each
            entry.  Response arrows and card links are preserved.
        """
        lines: list[str] = []
        lines.append("# Debate Flow Export")
        lines.append("")
        lines.append(
            f"_Generated {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}_"
        )
        lines.append("")

        # Determine maximum entry count across columns for table rows
        columns = [
            self._get_column(i) for i in range(len(self.column_defs))
        ]
        max_rows = max((len(c.entries) for c in columns), default=0)

        if max_rows == 0:
            lines.append("_No entries recorded._")
            return "\n".join(lines)

        # Table header
        header = "| " + " | ".join(c.column_name for c in columns) + " |"
        separator = "| " + " | ".join("---" for _ in columns) + " |"
        lines.append(header)
        lines.append(separator)

        # Table body
        for row_idx in range(max_rows):
            cells: list[str] = []
            for col in columns:
                if row_idx < len(col.entries):
                    entry = col.entries[row_idx]
                    parts: list[str] = []
                    if entry.response_to is not None:
                        parts.append(f"← [{entry.response_to + 1}]")
                    parts.append(entry.text)
                    if entry.linked_card_id is not None:
                        parts.append(f"(card#{entry.linked_card_id})")
                    cells.append(" ".join(parts))
                else:
                    cells.append("")
            lines.append("| " + " | ".join(cells) + " |")

        lines.append("")
        return "\n".join(lines)

    # ── Navigation ───────────────────────────────────────────────────────

    def action_go_back(self) -> None:
        """Dismiss any open overlay or pop back to the main screen."""
        if self._input_mode is not None:
            self._dismiss_input()
            return
        self.app.pop_screen()

    # ── Status Bar ───────────────────────────────────────────────────────

    def _update_status(self) -> None:
        """Refresh the bottom status bar with current context."""
        col = self._get_column(self.active_column)
        entry_info = ""
        if col.entries and 0 <= col.cursor < len(col.entries):
            entry = col.entries[col.cursor]
            entry_info = f" │ Entry {col.cursor + 1}/{len(col.entries)}"
            if entry.linked_card_id is not None:
                entry_info += f" │ 🔗 Card #{entry.linked_card_id}"
            if entry.response_to is not None:
                entry_info += f" │ ← responds to [{entry.response_to + 1}]"
        elif not col.entries:
            entry_info = " │ (empty)"

        status = f"Column: {col.column_name} ({col.side.upper()}){entry_info}"
        try:
            self.query_one("#flow-status-bar", Static).update(status)
        except Exception:
            pass
