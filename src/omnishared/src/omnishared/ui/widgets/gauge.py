from typing import Optional

from rich.text import Text
from textual.widgets import Static


class GaugeBar(Static):
    """Color-graded horizontal gauge bar for strategic metrics.

    Renders a labeled progress bar with color that shifts from
    red (critical) through amber (caution) to green (optimal).
    """

    def __init__(
        self,
        label: str = "METRIC",
        value: int = 0,
        icon: str = "█",
        bar_width: int = 20,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._label = label
        self._value = max(0, min(100, value))
        self._icon = icon
        self._bar_width = bar_width

    def set_value(self, value: int, label: Optional[str] = None) -> None:
        """Update the gauge value (0-100) and optionally the label."""
        self._value = max(0, min(100, value))
        if label is not None:
            self._label = label
        self.refresh()

    def render(self) -> Text:
        """Render the gauge as a Rich Text object with dynamic coloring."""
        v = self._value
        filled = int((v / 100) * self._bar_width)
        empty = self._bar_width - filled

        if v < 40:
            bar_color = "#ef4444"
            status = "▼"
        elif v < 75:
            bar_color = "#f59e0b"
            status = "●"
        else:
            bar_color = "#10b981"
            status = "▲"

        text = Text()
        text.append(f"{self._label:<12} ", style="bold")
        text.append("[", style="dim")
        text.append(self._icon * filled, style=f"bold {bar_color}")
        text.append("░" * empty, style="#334155")
        text.append("]", style="dim")
        text.append(f" {v:>3}% {status}", style=f"bold {bar_color}")
        return text
