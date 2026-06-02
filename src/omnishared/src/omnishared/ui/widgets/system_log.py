from textual.app import ComposeResult
from textual.widgets import Label, Static


class SystemLog(Static):
    """Scrolling activity ticker for real-time system feedback."""

    def compose(self) -> ComposeResult:
        yield Label("📜 SYSTEM KERNEL", classes="log-header")
        yield Static("", id="log-text", classes="log-content")

    def on_mount(self) -> None:
        self._logs: list[str] = ["🏛️  KERNEL ONLINE", "> System ready."]
        self._refresh_log()

    def _refresh_log(self) -> None:
        self.query_one("#log-text", Static).update("\n".join(self._logs[:5]))

    def log_activity(self, message: str) -> None:
        from datetime import datetime

        now = datetime.now().strftime("%H:%M:%S")
        self._logs.insert(0, f"> [{now}] {message}")
        try:
            self.query_one("#log-text", Static).update("\n".join(self._logs[:5]))
        except Exception:
            pass
