from typing import List, Optional
from rich.text import Text
from textual.widgets import Static

# Unicode block elements for sub-character vertical resolution
_BARS = " ▁▂▃▄▅▆▇█"


class SparklineBar(Static):
    """Compact inline sparkline chart using Unicode block elements.

    Renders a series of values as a tiny bar chart with color-grading.
    Usage: SparklineBar(values=[3, 7, 2, 9, 5], label="VELOCITY")
    """

    def __init__(
        self,
        values: Optional[List[int]] = None,
        label: str = "",
        max_val: int = 10,
        color_low: str = "#ef4444",
        color_mid: str = "#f59e0b",
        color_high: str = "#10b981",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._values = values or []
        self._label = label
        self._max_val = max_val
        self._color_low = color_low
        self._color_mid = color_mid
        self._color_high = color_high

    def set_values(self, values: List[int], max_val: Optional[int] = None) -> None:
        """Update the sparkline data and trigger a re-render."""
        self._values = values
        if max_val is not None:
            self._max_val = max_val
        self.refresh()

    def render(self) -> Text:
        """Render the sparkline as a Rich Text object with inline color."""
        if not self._values:
            return Text(f"{self._label}: ── no data ──", style="dim")

        text = Text()
        if self._label:
            text.append(f"{self._label} ", style="bold")
        text.append("│", style="dim")

        mx = max(self._max_val, max(self._values), 1)
        for v in self._values:
            normalized = min(v / mx, 1.0)
            idx = int(normalized * (len(_BARS) - 1))
            char = _BARS[idx]

            if normalized < 0.35:
                color = self._color_low
            elif normalized < 0.7:
                color = self._color_mid
            else:
                color = self._color_high

            text.append(char, style=color)

        text.append("│", style="dim")
        return text
