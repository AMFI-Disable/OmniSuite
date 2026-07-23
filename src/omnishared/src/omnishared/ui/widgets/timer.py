"""Configurable countdown timer widget for debate rounds.

Provides a visual countdown with color-coded time transitions,
progress bar depletion, bell notification on expiry, and
format-aware duration presets loaded from configuration.
"""

from __future__ import annotations

import sys
from typing import Optional

from rich.text import Text
from textual.reactive import reactive
from textual.timer import Timer as TextualTimer
from textual.widgets import Static


# ─── Progress bar characters ────────────────────────────────────────────────────
_BAR_FILLED = "█"
_BAR_EMPTY = "░"

# ─── Color thresholds ───────────────────────────────────────────────────────────
_COLOR_GREEN = "#10b981"
_COLOR_YELLOW = "#f59e0b"
_COLOR_RED = "#ef4444"
_COLOR_DIM = "#334155"


def _load_format_durations(format_name: Optional[str] = None) -> dict:
    """Load speech and prep time durations for a debate format.

    Args:
        format_name: Name of the debate format (e.g. 'Public Forum').
            If None, reads timer.default_format from config.

    Returns:
        Dict with 'prep_time_seconds' and 'speeches' list, or
        a fallback dict if loading fails.
    """
    try:
        from omnishared.config import load_config
        from omnishared.formats.loader import load_formats

        if format_name is None:
            config = load_config()
            timer_cfg = config.get("timer", {})
            format_name = timer_cfg.get("default_format", "Public Forum")

        formats = load_formats()
        if format_name in formats:
            return formats[format_name]
    except Exception:
        pass

    # Fallback: generic 4-minute speech / 3-minute prep
    return {
        "prep_time_seconds": 180,
        "speeches": [
            {"name": "Speech", "duration_seconds": 240},
        ],
    }


class RoundTimer(Static):
    """Configurable countdown timer widget for debate rounds.

    Displays a large-format MM:SS countdown with a depleting progress
    bar and color transitions that shift from green to yellow to red
    as time runs out.  Emits a terminal bell when the timer expires.

    Keybindings (when focused):
        space — pause / resume
        r     — reset to original duration

    Reactive properties:
        time_remaining (float): Seconds left on the clock.
        is_running (bool): Whether the timer is actively counting down.
        is_paused (bool): Whether the timer has been paused mid-run.

    Example::

        timer = RoundTimer(duration=240, label="Rebuttal (Team A)")
        timer.start()
    """

    BINDINGS = [
        ("space", "toggle_pause", "Pause / Resume"),
        ("r", "reset_timer", "Reset"),
    ]

    # ── Reactive state ───────────────────────────────────────────────────────
    time_remaining: reactive[float] = reactive(0.0)
    is_running: reactive[bool] = reactive(False)
    is_paused: reactive[bool] = reactive(False)

    def __init__(
        self,
        duration: int = 240,
        label: str = "TIMER",
        bar_width: int = 30,
        format_name: Optional[str] = None,
        speech_index: int = 0,
        **kwargs,
    ) -> None:
        """Initialise the RoundTimer.

        Args:
            duration: Countdown length in seconds.  Overridden when
                *format_name* is provided.
            label: Display label shown above the countdown.
            bar_width: Character width of the progress bar.
            format_name: Optional debate-format name.  When set, the
                widget loads speech durations from config/formats.json.
            speech_index: Index into the format's speech list to pick
                the initial duration (ignored when *format_name* is None).
            **kwargs: Forwarded to ``Static.__init__``.
        """
        super().__init__(**kwargs)
        self._label = label
        self._bar_width = bar_width
        self._tick_timer: Optional[TextualTimer] = None
        self._bell_fired = False

        # If a format is requested, override duration from config
        if format_name is not None:
            fmt = _load_format_durations(format_name)
            speeches = fmt.get("speeches", [])
            if 0 <= speech_index < len(speeches):
                duration = speeches[speech_index].get("duration_seconds", duration)
                self._label = speeches[speech_index].get("name", label)
            else:
                # Fall back to prep time when index is out of range
                duration = fmt.get("prep_time_seconds", duration)

        self._total_duration: float = float(duration)
        self.time_remaining = float(duration)

    # ── Public API ───────────────────────────────────────────────────────────

    def start(self) -> None:
        """Start (or restart) the countdown from the current time_remaining."""
        if self.is_running and not self.is_paused:
            return  # already ticking

        self._bell_fired = False
        self.is_running = True
        self.is_paused = False

        if self._tick_timer is None:
            self._tick_timer = self.set_interval(1.0, self._tick, pause=False)
        else:
            self._tick_timer.resume()

    def pause(self) -> None:
        """Pause the countdown.  Call :meth:`resume` to continue."""
        if not self.is_running or self.is_paused:
            return
        self.is_paused = True
        if self._tick_timer is not None:
            self._tick_timer.pause()

    def resume(self) -> None:
        """Resume the countdown after a :meth:`pause`."""
        if not self.is_paused:
            return
        self.is_paused = False
        if self._tick_timer is not None:
            self._tick_timer.resume()

    def reset(self) -> None:
        """Reset the timer back to the original duration and stop."""
        self._stop_tick()
        self.time_remaining = self._total_duration
        self.is_running = False
        self.is_paused = False
        self._bell_fired = False
        self.refresh()

    def set_duration(self, seconds: int) -> None:
        """Change the total duration and reset the timer.

        Args:
            seconds: New countdown length in seconds.
        """
        self._total_duration = float(max(0, seconds))
        self.reset()

    def load_format(
        self, format_name: str, speech_index: int = 0
    ) -> None:
        """Load durations from a named debate format.

        Args:
            format_name: Debate format (e.g. 'Lincoln-Douglas').
            speech_index: Index of the speech in the format's list.
        """
        fmt = _load_format_durations(format_name)
        speeches = fmt.get("speeches", [])
        if 0 <= speech_index < len(speeches):
            self._total_duration = float(
                speeches[speech_index].get("duration_seconds", self._total_duration)
            )
            self._label = speeches[speech_index].get("name", self._label)
        else:
            self._total_duration = float(
                fmt.get("prep_time_seconds", self._total_duration)
            )
        self.reset()

    # ── Textual lifecycle ────────────────────────────────────────────────────

    def on_unmount(self) -> None:
        """Clean up the tick timer when the widget is removed."""
        self._stop_tick()

    # ── Keybinding actions ───────────────────────────────────────────────────

    def action_toggle_pause(self) -> None:
        """Toggle between pause and resume (bound to space)."""
        if not self.is_running:
            self.start()
        elif self.is_paused:
            self.resume()
        else:
            self.pause()

    def action_reset_timer(self) -> None:
        """Reset the timer (bound to r)."""
        self.reset()

    # ── Rendering ────────────────────────────────────────────────────────────

    def render(self) -> Text:
        """Render the timer as a Rich Text object with countdown and bar."""
        remaining = max(0.0, self.time_remaining)
        minutes, seconds = divmod(int(remaining), 60)
        pct = remaining / self._total_duration if self._total_duration > 0 else 0.0

        # Pick colour based on percentage remaining
        if pct > 0.50:
            color = _COLOR_GREEN
        elif pct > 0.25:
            color = _COLOR_YELLOW
        else:
            color = _COLOR_RED

        # Build display
        text = Text()
        text.append(f"⏱  {self._label}", style="bold")

        # Status badge
        if self.is_paused:
            text.append("  ⏸ PAUSED", style="bold #94a3b8")
        elif self.is_running:
            text.append("  ▶ RUNNING", style=f"bold {color}")
        else:
            text.append("  ■ READY", style="dim")
        text.append("\n")

        # Large time display
        text.append(f"   {minutes:02d}:{seconds:02d}", style=f"bold {color}")
        text.append("\n")

        # Progress bar
        filled = int(pct * self._bar_width)
        empty = self._bar_width - filled
        text.append("   [", style="dim")
        text.append(_BAR_FILLED * filled, style=f"bold {color}")
        text.append(_BAR_EMPTY * empty, style=_COLOR_DIM)
        text.append("]", style="dim")
        text.append(f" {int(pct * 100):>3}%", style=f"bold {color}")

        # Hotkey hint
        text.append("\n   ", style="dim")
        text.append("␣ pause/resume  ", style="dim")
        text.append("r reset", style="dim")

        return text

    # ── Watcher ──────────────────────────────────────────────────────────────

    def watch_time_remaining(self, value: float) -> None:
        """Refresh the display whenever ``time_remaining`` changes."""
        self.refresh()

    # ── Internals ────────────────────────────────────────────────────────────

    def _tick(self) -> None:
        """Advance the countdown by one second."""
        if self.time_remaining <= 0:
            self._on_expired()
            return

        self.time_remaining = max(0.0, self.time_remaining - 1.0)

        if self.time_remaining <= 0:
            self._on_expired()

    def _on_expired(self) -> None:
        """Handle timer expiry: stop ticking and ring the terminal bell."""
        self._stop_tick()
        self.is_running = False
        self.is_paused = False
        self.time_remaining = 0.0

        if not self._bell_fired:
            self._bell_fired = True
            # Terminal bell notification
            sys.stdout.write("\a")
            sys.stdout.flush()
            self.app.bell()

    def _stop_tick(self) -> None:
        """Stop and discard the interval timer."""
        if self._tick_timer is not None:
            self._tick_timer.stop()
            self._tick_timer = None
