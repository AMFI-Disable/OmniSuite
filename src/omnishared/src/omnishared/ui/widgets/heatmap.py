import datetime
from typing import Dict, Optional
from rich.text import Text
from textual.widgets import Static

_HEAT_CHARS = "░▒▓█"
_HEAT_COLORS = ["#1e293b", "#065f46", "#059669", "#10b981", "#34d399"]


class HeatmapGrid(Static):
    """GitHub-style contribution heatmap for research activity tracking.

    Renders a compact grid where each cell represents one day,
    color-coded by activity level.
    """

    def __init__(
        self,
        daily_counts: Optional[Dict[str, int]] = None,
        weeks: int = 12,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._daily_counts = daily_counts or {}
        self._weeks = weeks

    def set_data(self, daily_counts: Dict[str, int]) -> None:
        """Update the heatmap data. Keys are 'YYYY-MM-DD' strings."""
        self._daily_counts = daily_counts
        self.refresh()

    def render(self) -> Text:
        """Render the heatmap as a Rich Text grid."""
        text = Text()
        text.append("RESEARCH ACTIVITY ", style="bold #94a3b8")
        text.append("(last 12 weeks)\n", style="dim")

        today = datetime.date.today()
        day_labels = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

        # Header: week numbers
        text.append("   ", style="dim")
        for w in range(self._weeks):
            if w % 4 == 0:
                text.append(f"W{self._weeks - w:<2}", style="dim")
            else:
                text.append("   ", style="dim")
        text.append("\n")

        # Build grid: 7 rows (days) x N columns (weeks)
        max_count = max(self._daily_counts.values(), default=1) or 1

        for day_idx in range(7):
            text.append(f"{day_labels[day_idx]} ", style="dim")
            for week_offset in range(self._weeks - 1, -1, -1):
                d = today - datetime.timedelta(
                    days=today.weekday() - day_idx + (week_offset * 7)
                )
                date_key = d.strftime("%Y-%m-%d")
                count = self._daily_counts.get(date_key, 0)

                # Normalize to 0-4 range
                if count == 0:
                    level = 0
                else:
                    level = min(4, int((count / max_count) * 4) + 1)

                char = _HEAT_CHARS[min(level, len(_HEAT_CHARS) - 1)]
                color = _HEAT_COLORS[min(level, len(_HEAT_COLORS) - 1)]
                text.append(f"{char}  ", style=color)

            text.append("\n")

        # Legend
        text.append("   Less ", style="dim")
        for ch, co in zip(_HEAT_CHARS, _HEAT_COLORS):
            text.append(ch, style=co)
        text.append(" More", style="dim")

        return text
