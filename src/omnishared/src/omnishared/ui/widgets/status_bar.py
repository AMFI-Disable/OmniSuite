"""Rich status bar widget showing vault statistics.

Displays a compact single-line bar with card count, motion count,
AI status, current debate format, and timer state.  Automatically
refreshes every 5 seconds.
"""

from __future__ import annotations

from typing import Optional

from rich.text import Text
from textual.timer import Timer as TextualTimer
from textual.widgets import Static


# ─── Styling constants ──────────────────────────────────────────────────────────
_COLOR_LABEL = "#94a3b8"
_COLOR_VALUE = "#e2e8f0"
_COLOR_ONLINE = "#10b981"
_COLOR_OFFLINE = "#ef4444"
_COLOR_SEP = "#334155"

_REFRESH_INTERVAL = 5.0  # seconds


def _query_card_count() -> int:
    """Return the number of evidence cards in the vault database.

    Falls back to 0 if the table doesn't exist or any error occurs.
    """
    try:
        from omnishared.database.connection import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM sqlite_master "
            "WHERE type='table' AND name='cards'"
        )
        if cursor.fetchone()[0] == 0:
            conn.close()
            return 0
        cursor.execute("SELECT COUNT(*) FROM cards")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


def _query_motion_count() -> int:
    """Return the number of debate motions in the vault database.

    Falls back to 0 if the table doesn't exist or any error occurs.
    """
    try:
        from omnishared.database.connection import get_connection

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM sqlite_master "
            "WHERE type='table' AND name='motions'"
        )
        if cursor.fetchone()[0] == 0:
            conn.close()
            return 0
        cursor.execute("SELECT COUNT(*) FROM motions")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


def _check_ai_online() -> bool:
    """Check whether the local Ollama AI backend is reachable."""
    try:
        from omnishared.ai.client import check_ollama_status

        return check_ollama_status()
    except Exception:
        return False


def _get_current_format() -> str:
    """Read the default debate format from configuration."""
    try:
        from omnishared.config import load_config

        config = load_config()
        return config.get("timer", {}).get("default_format", "Public Forum")
    except Exception:
        return "Public Forum"


class StatusBar(Static):
    """Compact status bar showing vault statistics and system state.

    Automatically refreshes every 5 seconds.  Designed to sit at the
    bottom of any screen.

    Displayed sections:
        • 🃏 Cards — evidence card count
        • 📋 Motions — motion count
        • 🤖 AI — Ollama online / offline
        • 📐 Format — current debate format
        • ⏱  Timer — timer state summary

    Example::

        class MyScreen(Screen):
            def compose(self) -> ComposeResult:
                yield StatusBar(id="status")
    """

    def __init__(
        self,
        timer_widget=None,
        **kwargs,
    ) -> None:
        """Initialise the StatusBar.

        Args:
            timer_widget: Optional reference to a ``RoundTimer`` instance.
                When provided, the status bar includes timer state.
            **kwargs: Forwarded to ``Static.__init__``.
        """
        super().__init__(**kwargs)
        self._timer_widget = timer_widget
        self._refresh_timer: Optional[TextualTimer] = None

        # Cached values to avoid blocking the UI thread
        self._card_count: int = 0
        self._motion_count: int = 0
        self._ai_online: bool = False
        self._format_name: str = "Public Forum"

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        """Start the periodic refresh cycle on mount."""
        self._poll_stats()
        self._refresh_timer = self.set_interval(
            _REFRESH_INTERVAL, self._poll_stats, pause=False
        )

    def on_unmount(self) -> None:
        """Stop the refresh timer when removed from the DOM."""
        if self._refresh_timer is not None:
            self._refresh_timer.stop()
            self._refresh_timer = None

    # ── Public API ───────────────────────────────────────────────────────────

    def set_timer_widget(self, timer_widget) -> None:
        """Attach a RoundTimer instance for state display.

        Args:
            timer_widget: A ``RoundTimer`` widget reference.
        """
        self._timer_widget = timer_widget
        self.refresh()

    def force_refresh(self) -> None:
        """Manually trigger an immediate data refresh."""
        self._poll_stats()

    # ── Rendering ────────────────────────────────────────────────────────────

    def render(self) -> Text:
        """Render the status bar as a single Rich Text line."""
        text = Text()
        sep = Text(" │ ", style=_COLOR_SEP)

        # ── Cards ────────────────────────────────────────────────────────
        text.append("🃏 ", style=_COLOR_LABEL)
        text.append(f"{self._card_count}", style=f"bold {_COLOR_VALUE}")
        text.append(" cards", style=_COLOR_LABEL)

        text.append_text(sep)

        # ── Motions ──────────────────────────────────────────────────────
        text.append("📋 ", style=_COLOR_LABEL)
        text.append(f"{self._motion_count}", style=f"bold {_COLOR_VALUE}")
        text.append(" motions", style=_COLOR_LABEL)

        text.append_text(sep)

        # ── AI status ────────────────────────────────────────────────────
        text.append("🤖 AI ", style=_COLOR_LABEL)
        if self._ai_online:
            text.append("● online", style=f"bold {_COLOR_ONLINE}")
        else:
            text.append("○ offline", style=f"bold {_COLOR_OFFLINE}")

        text.append_text(sep)

        # ── Format ───────────────────────────────────────────────────────
        text.append("📐 ", style=_COLOR_LABEL)
        text.append(self._format_name, style=f"bold {_COLOR_VALUE}")

        # ── Timer (optional) ─────────────────────────────────────────────
        if self._timer_widget is not None:
            text.append_text(sep)
            text.append("⏱  ", style=_COLOR_LABEL)
            try:
                remaining = max(0.0, self._timer_widget.time_remaining)
                mins, secs = divmod(int(remaining), 60)
                if self._timer_widget.is_paused:
                    text.append(f"{mins:02d}:{secs:02d} ⏸", style="bold #f59e0b")
                elif self._timer_widget.is_running:
                    text.append(f"{mins:02d}:{secs:02d} ▶", style=f"bold {_COLOR_ONLINE}")
                else:
                    text.append(f"{mins:02d}:{secs:02d} ■", style="dim")
            except Exception:
                text.append("--:--", style="dim")

        return text

    # ── Internals ────────────────────────────────────────────────────────────

    def _poll_stats(self) -> None:
        """Refresh cached statistics from database and AI backend."""
        try:
            self._card_count = _query_card_count()
        except Exception:
            pass

        try:
            self._motion_count = _query_motion_count()
        except Exception:
            pass

        try:
            self._ai_online = _check_ai_online()
        except Exception:
            self._ai_online = False

        try:
            self._format_name = _get_current_format()
        except Exception:
            pass

        self.refresh()
