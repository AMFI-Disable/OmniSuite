"""Breadcrumb navigation widget for screen path display.

Renders a single-line breadcrumb trail like
``OmniDebate > Motions > Card #42 > Edit`` with the current
(rightmost) segment rendered in bold.
"""

from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widgets import Static

# ─── Styling constants ──────────────────────────────────────────────────────────
_SEPARATOR = " › "
_COLOR_SEGMENT = "#94a3b8"
_COLOR_ACTIVE = "#e2e8f0"
_COLOR_SEP = "#475569"


class Breadcrumb(Static):
    """Single-line breadcrumb navigation showing the current screen path.

    The path is maintained as a list of label strings.  The last
    element is considered the *active* segment and is rendered in bold.

    Reactive properties:
        path (list[str]): The ordered breadcrumb segments.

    Example::

        crumb = Breadcrumb()
        crumb.set_path(["OmniDebate", "Motions", "Card #42", "Edit"])

        # Later, navigate deeper:
        crumb.push("Tags")

        # Go back one level:
        crumb.pop()
    """

    path: reactive[list] = reactive(list, always_update=True)

    def __init__(
        self,
        initial_path: list[str] | None = None,
        **kwargs,
    ) -> None:
        """Initialise the Breadcrumb widget.

        Args:
            initial_path: Optional starting path segments.
            **kwargs: Forwarded to ``Static.__init__``.
        """
        super().__init__(**kwargs)
        if initial_path:
            self.path = list(initial_path)

    # ── Public API ───────────────────────────────────────────────────────────

    def push(self, label: str) -> None:
        """Append a new segment to the breadcrumb trail.

        Args:
            label: Display text for the new segment.
        """
        new_path = list(self.path)
        new_path.append(label)
        self.path = new_path

    def pop(self) -> str | None:
        """Remove and return the last segment, or None if empty.

        Returns:
            The removed label, or ``None`` when the path is already empty.
        """
        if not self.path:
            return None
        new_path = list(self.path)
        removed = new_path.pop()
        self.path = new_path
        return removed

    def set_path(self, labels: list[str]) -> None:
        """Replace the entire breadcrumb path.

        Args:
            labels: Ordered list of segment labels.
        """
        self.path = list(labels)

    def clear(self) -> None:
        """Remove all segments from the breadcrumb."""
        self.path = []

    # ── Rendering ────────────────────────────────────────────────────────────

    def render(self) -> Text:
        """Render the breadcrumb as a styled Rich Text line."""
        if not self.path:
            return Text("—", style="dim")

        text = Text()
        last_idx = len(self.path) - 1

        for idx, segment in enumerate(self.path):
            if idx == last_idx:
                # Active (current) segment — bold and bright
                text.append(segment, style=f"bold {_COLOR_ACTIVE}")
            else:
                text.append(segment, style=_COLOR_SEGMENT)

            if idx < last_idx:
                text.append(_SEPARATOR, style=_COLOR_SEP)

        return text

    # ── Watcher ──────────────────────────────────────────────────────────────

    def watch_path(self, value: list) -> None:
        """Refresh the display whenever the path changes."""
        self.refresh()
