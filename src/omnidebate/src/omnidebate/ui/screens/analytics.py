from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Static, Button, DataTable
from textual.containers import Vertical, Horizontal
from omnidebate.core.database import list_motions, read_vault, get_velocity_stats


class AnalyticsScreen(ModalScreen):
    """Global Strategic Dashboard with Research Velocity and Contribution Heatmap."""

    def compose(self) -> ComposeResult:
        with Vertical(id="stats-dialog"):
            yield Label(
                "📊  STRATEGIC DASHBOARD & RESEARCH VELOCITY", classes="stats-title"
            )

            yield Label(
                "🗓️  CONTRIBUTION HEATMAP (Simulation)", classes="section-header"
            )
            yield Static(id="heatmap-view")

            yield Label("📈  7-DAY RESEARCH VELOCITY", classes="section-header")
            yield Static(id="velocity-graph")

            yield Label("🏛️  MOTION LIBRARY AUDIT", classes="section-header")
            yield DataTable(id="stats-table")

            with Horizontal(classes="dashboard-footer"):
                yield Button("CLOSE [ESC]", variant="primary", id="btn-close")

    def safe_update(self, selector: str, value: str) -> None:
        """Safely update a widget if it exists, otherwise fail silent."""
        try:
            self.query_one(selector).update(value)
        except Exception:
            pass

    def on_mount(self) -> None:
        try:
            self._render_heatmap()

            stats = get_velocity_stats()
            max_v = max(stats) if stats else 1
            graph_lines = []
            for h in range(4, -1, -1):
                line = ""
                for val in stats:
                    bar_h = int((val / max_v) * 4) if max_v > 0 else 0
                    line += "  █  " if bar_h >= h else "     "
                graph_lines.append(line)

            graph_text = (
                "\n".join(graph_lines)
                + "\n"
                + "  "
                + "  ".join(["T-" + str(i) for i in range(6, -1, -1)])
            )
            self.safe_update("#velocity-graph", graph_text)

            table = self.query_one(DataTable)
            table.cursor_type = "row"
            table.add_columns("ID", "MOTION", "CARDS", "BALANCE", "STATUS")

            for m in list_motions(include_archives=True):
                try:
                    cards = read_vault(m["id"])
                    aff = len([c for c in cards if c["side"] == "AFF"])
                    neg = len([c for c in cards if c["side"] == "NEG"])
                    status = (
                        " [green]READY[/] " if len(cards) > 8 else " [yellow]PREP[/] "
                    )
                    table.add_row(
                        f"#{m['id']}",
                        m["name"].upper(),
                        str(len(cards)),
                        f"{aff}/{neg}",
                        status,
                    )
                except Exception:
                    continue
        except Exception:
            pass

    def _render_heatmap(self) -> None:
        try:
            import random

            grid = []
            colors = ["#1e293b", "#064e3b", "#065f46", "#059669", "#10b981"]
            for day in range(7):
                row = ""
                for week in range(12):
                    activity = random.randint(0, 4)
                    color = colors[activity]
                    row += f"[{color}]■ [/]"
                grid.append(row)

            self.safe_update("#heatmap-view", "\n".join(grid))
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close":
            self.dismiss()
