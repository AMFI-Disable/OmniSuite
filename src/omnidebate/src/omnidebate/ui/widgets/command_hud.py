from typing import Optional
from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.timer import Timer
from textual.widgets import Button, Label, Select, Static


class CommandHUD(Static):
    """Consolidated full-width Command HUD with Timer, Prep, and Round State."""

    _speech_secs: int = reactive(0)
    _prep_secs: int = reactive(0)
    _speech_total: int = 0
    _timer_running: bool = False
    _prep_running: bool = False
    _tick_handle: Optional[Timer] = None

    def __init__(
        self, formats: dict, default_format: str = "Public Forum", *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.formats = formats
        self.format_name = default_format
        self._speech_idx = 0
        self._reset_format()

    def _reset_format(self) -> None:
        fmt = self.formats.get(self.format_name, {})
        self._speeches = fmt.get("speeches", [])
        self._prep_secs = fmt.get("prep_time_seconds", 180)
        self._prep_total = self._prep_secs
        self._speech_idx = 0
        self._load_current_speech()

    def _load_current_speech(self) -> None:
        if self._speeches and self._speech_idx < len(self._speeches):
            sp = self._speeches[self._speech_idx]
            self._speech_secs = sp["duration_seconds"]
            self._speech_total = sp["duration_seconds"]
            self._speech_name = sp["name"]
        else:
            self._speech_secs = 0
            self._speech_total = 0
            self._speech_name = "ROUND COMPLETE"

    def compose(self) -> ComposeResult:
        yield Label("[ ⏱️ ROUND CONTROL ]", classes="zone-header")

        with Vertical(id="hud-format-section", classes="hud-section"):
            yield Label("DEBATE FORMAT", classes="hud-label")
            yield Select(
                [(n, n) for n in self.formats],
                value=self.format_name,
                id="sel-format",
            )

        with Vertical(id="hud-speech-section", classes="hud-section"):
            yield Label("ACTIVE SPEECH", classes="hud-label")
            yield Label(
                f"CURRENT: {self._speech_name.upper()}",
                id="lbl-speech-name",
                classes="hud-state-text",
            )
            yield Label("00:00", id="lbl-speech-time", classes="hud-big-time")
            yield Static("", id="hud-progress")

        with Vertical(id="hud-prep-section", classes="hud-section"):
            yield Label("PREP RESERVOIR", classes="hud-label")
            yield Label("03:00", id="lbl-prep-time", classes="hud-big-time")

        with Vertical(id="hud-controls-section"):
            yield Button("▶ START SPEECH", id="btn-speech-toggle", variant="success")
            yield Button("🧪 START PREP", id="btn-prep-toggle", variant="success")
            yield Button("⏭ NEXT", id="btn-speech-next", variant="primary")
            yield Button(
                "🎙️ PREP SCREEN", id="btn-speech-prep-workspace", variant="primary"
            )
            yield Button("↺ RESET", id="btn-reset-fmt", variant="default")

    def on_mount(self) -> None:
        self._refresh_labels()
        self._tick_handle = self.set_interval(1, self._tick)

    def _tick(self) -> None:
        if self._timer_running and self._speech_secs > 0:
            self._speech_secs -= 1
            if self._speech_secs == 0:
                self.app.notify("SPEECH TIME EXPIRED", severity="error")
                self._timer_running = False
        if self._prep_running and self._prep_secs > 0:
            self._prep_secs -= 1
            if self._prep_secs == 0:
                self.app.notify("PREP TIME EXPIRED", severity="error")
                self._prep_running = False
        self._refresh_labels()

    def _fmt_time(self, secs: int) -> str:
        m, s = divmod(max(secs, 0), 60)
        return f"{m:02d}:{s:02d}"

    def _refresh_labels(self) -> None:
        st = self.query_one("#lbl-speech-time", Label)
        st.update(self._fmt_time(self._speech_secs))
        st.set_class(self._timer_running, "hud-running")
        st.set_class(self._speech_secs == 0 and self._speech_total > 0, "hud-expired")

        pt = self.query_one("#lbl-prep-time", Label)
        pt.update(self._fmt_time(self._prep_secs))
        pt.set_class(self._prep_running, "hud-running")

        sn = self.query_one("#lbl-speech-name", Label)
        sn.update(f"CURRENT: {self._speech_name.upper()}")

        pb = self.query_one("#hud-progress", Static)
        if self._speech_total > 0:
            pct = (self._speech_secs / self._speech_total) * 100
            bar_len = 15
            filled = int((self._speech_secs / self._speech_total) * bar_len)
            bar = "█" * filled + "░" * (bar_len - filled)
            pb.update(f"PROGRESS: [{bar}] {int(pct)}%")
        else:
            pb.update("")

        try:
            btn_speech = self.query_one("#btn-speech-toggle", Button)
            if self._timer_running:
                btn_speech.label = "⏸ PAUSE SPEECH"
                btn_speech.variant = "warning"
            else:
                btn_speech.label = "▶ START SPEECH"
                btn_speech.variant = "success"
        except Exception:
            pass

        try:
            btn_prep = self.query_one("#btn-prep-toggle", Button)
            if self._prep_running:
                btn_prep.label = "⏸ PAUSE PREP"
                btn_prep.variant = "warning"
            else:
                btn_prep.label = "🧪 START PREP"
                btn_prep.variant = "success"
        except Exception:
            pass

    @on(Select.Changed, "#sel-format")
    def format_changed(self, event: Select.Changed) -> None:
        if event.value:
            self.format_name = event.value
            self._timer_running = False
            self._prep_running = False
            self._reset_format()
            self._refresh_labels()

    def speech_toggle(self) -> None:
        if self._speech_secs > 0:
            self._timer_running = not self._timer_running
            if self._timer_running:
                self._prep_running = False
            self._refresh_labels()

    def prep_toggle(self) -> None:
        if self._prep_secs > 0:
            self._prep_running = not self._prep_running
            if self._prep_running:
                self._timer_running = False
            self._refresh_labels()

    @on(Button.Pressed, "#btn-speech-toggle")
    def on_btn_speech_toggle(self) -> None:
        self.speech_toggle()

    @on(Button.Pressed, "#btn-prep-toggle")
    def on_btn_prep_toggle(self) -> None:
        self.prep_toggle()

    @on(Button.Pressed, "#btn-speech-next")
    def speech_next(self) -> None:
        self._timer_running = False
        self._speech_idx = min(self._speech_idx + 1, len(self._speeches) - 1)
        self._load_current_speech()
        self._refresh_labels()

    @on(Button.Pressed, "#btn-reset-fmt")
    def reset_fmt(self) -> None:
        self._timer_running = False
        self._prep_running = False
        self._reset_format()
        self._refresh_labels()
