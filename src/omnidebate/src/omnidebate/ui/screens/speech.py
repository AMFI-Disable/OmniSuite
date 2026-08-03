"""Speech Prep Screen — Countdown Timers and Interactive Flow Grid.

Allows debaters to track speech durations, prep timers, and flow arguments.
© 2026 OmniSuite. Built for the Digital Grandmaster.
"""

from omnishared.database import increment_mastery, read_vault
from omnishared.formats.loader import load_formats
from omnishared.ui.widgets import GaugeBar
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Input,
    Label,
    ListItem,
    ListView,
    Select,
    Static,
    TextArea,
)


class SpeechPrepScreen(ModalScreen):
    """Speech Prep Timer & Column Flow Sheet."""

    BINDINGS = [
        Binding("space", "toggle_timer", "Play/Pause"),
        Binding("r", "reset_timer", "Reset Active Timer"),
        Binding("n", "next_speech", "Next Speech"),
        Binding("escape", "exit_screen", "Exit Screen"),
    ]

    def __init__(self, motion_id: int):
        super().__init__()
        self.motion_id = motion_id
        self.cards = []
        self.spoken_card_ids = set()
        self.formats = {}
        self.selected_format = ""
        self.speeches = []
        self.speech_index = 0
        self.speech_time_remaining = 0
        self.total_prep_time = 0
        self.aff_prep_remaining = 0
        self.neg_prep_remaining = 0
        self.is_paused = True
        self.active_timer_mode = "speech"  # speech, aff_prep, neg_prep

    def compose(self) -> ComposeResult:
        with Container(id="speech-dialog"):
            # Header Row
            with Horizontal(id="speech-header"):
                yield Label("🎙️  LIVE SPEECH PREP & FLOW SHEET  ·  ", id="speech-header-title")
                yield Select([], id="select-format", prompt="Select Format")

            # Active Timer Controls & Gauges Row
            with Horizontal(id="speech-controls-row"):
                # Big digital timer
                with Vertical(id="speech-timer-container"):
                    yield Label("ACTIVE SPEECH", classes="hud-group-label")
                    yield Static("No Speech", id="speech-name-display")
                    yield Static("00:00", id="speech-timer-display")

                # Active Timer Selector buttons
                with Vertical(id="speech-mode-selector"):
                    yield Button("🎤 RUN SPEECH", id="btn-mode-speech", variant="success")
                    yield Button("🟢 RUN AFF PREP", id="btn-mode-aff", variant="default")
                    yield Button("🔴 RUN NEG PREP", id="btn-mode-neg", variant="default")

                # Prep Gauges
                with Vertical(id="speech-gauges-container"):
                    yield GaugeBar(label="AFF PREP", id="gauge-aff-prep", value=100)
                    yield GaugeBar(label="NEG PREP", id="gauge-neg-prep", value=100)

                # Timer controls
                with Vertical(id="speech-actions-container"):
                    with Horizontal():
                        yield Button("▶ PLAY", id="btn-play-pause", variant="success")
                        yield Button("🔄 RESET", id="btn-reset", variant="warning")
                    with Horizontal():
                        yield Button("➡ SKIP SPEECH", id="btn-skip", variant="primary")
                        yield Button("✖ EXIT ROUND", id="btn-exit", variant="error")

            # Side-by-side Flow Sheet Column Grid
            with Horizontal(id="speech-flow-grid"):
                # Column 1: CONSTRUCTIVES
                with Vertical(classes="speech-column"):
                    yield Label(
                        "📂 CONSTRUCTIVES (Motion Cards)",
                        classes="speech-column-header",
                    )
                    yield ListView(id="constructives-list")

                # Column 2: REBUTTALS
                with Vertical(classes="speech-column"):
                    yield Label("🔥 REBUTTALS / CLASH", classes="speech-column-header")
                    yield ListView(id="rebuttals-list")
                    yield Input(placeholder="Add rebuttal point...", id="rebuttal-input")

                # Column 3: FINAL DECISION/SUMMARY
                with Vertical(classes="speech-column"):
                    yield Label("🏆 FINAL SUMMARY / DECISION", classes="speech-column-header")
                    yield TextArea(
                        id="summary-text",
                        placeholder="Note key win-condition points here...",
                    )

    def on_mount(self) -> None:
        # Load formats
        try:
            self.formats = load_formats()
        except Exception:
            self.formats = {}

        try:
            options = [(name, name) for name in self.formats.keys()]
            if options:
                self.call_after_refresh(self._set_initial_format, options[0][0])
        except Exception:
            pass

        # Load constructive cards
        self._reload_constructives()

        # Setup interval timer
        self.set_interval(1.0, self.tick)

    def _set_initial_format(self, value: str) -> None:
        try:
            select = self.query_one("#select-format", Select)
            options = [(name, name) for name in self.formats.keys()]
            select.set_options(options)
            select.value = value
        except Exception:
            pass

    def _safe_notify(self, message: str, severity: str = "information") -> None:
        try:
            self.app.notify(message, severity=severity)
        except Exception:
            pass

    def _reload_constructives(self) -> None:
        try:
            cl = self.query_one("#constructives-list", ListView)
            cl.clear()
        except Exception:
            return

        self.cards = read_vault(self.motion_id)
        if not self.cards:
            cl.mount(ListItem(Label("No cards found in motion.")))
            return

        for c in self.cards:
            cid = c["id"]
            side_icon = "🟢" if c["side"] == "AFF" else "🔴"
            status_icon = "✅ " if cid in self.spoken_card_ids else "▪ "

            tag_text = f"{status_icon}{side_icon} {c['tag']}"

            row = Horizontal(
                Label(tag_text, classes="constructive-card-label"),
                Button("Flow", id=f"flow-{cid}", classes="btn-flow-arg", variant="warning"),
                Button(
                    "Spoken",
                    id=f"spoken-{cid}",
                    classes="btn-spoken-arg",
                    variant="success",
                ),
                classes="constructive-card-row",
            )
            item = ListItem(row)
            item._card_data = c
            cl.mount(item)

    @on(Select.Changed, "#select-format")
    def format_changed(self, event: Select.Changed) -> None:
        if event.value:
            self.selected_format = event.value
            self.speeches = self.formats[self.selected_format]["speeches"]
            self.total_prep_time = self.formats[self.selected_format]["prep_time_seconds"]

            self.speech_index = 0
            self.aff_prep_remaining = self.total_prep_time
            self.neg_prep_remaining = self.total_prep_time
            self.is_paused = True

            self._update_speech_timer()
            self._update_prep_gauges()

    def _update_speech_timer(self) -> None:
        if not self.speeches:
            try:
                self.query_one("#speech-name-display", Static).update("No Speech")
                self.query_one("#speech-timer-display", Static).update("00:00")
            except Exception:
                pass
            return

        current_speech = self.speeches[self.speech_index]
        self.speech_time_remaining = current_speech["duration_seconds"]

        try:
            self.query_one("#speech-name-display", Static).update(current_speech["name"])
            self.query_one("#speech-timer-display", Static).update(
                self._format_time(self.speech_time_remaining)
            )
        except Exception:
            pass
        self.active_timer_mode = "speech"
        self._update_mode_buttons()
        self._update_play_pause_button()
        self._update_timer_visuals()

    def _update_play_pause_button(self) -> None:
        try:
            play_btn = self.query_one("#btn-play-pause", Button)
            mode_upper = self.active_timer_mode.replace("_", " ").upper()
            if self.is_paused:
                play_btn.label = f"▶ PLAY {mode_upper}"
                play_btn.variant = "success"
            else:
                play_btn.label = f"⏸ PAUSE {mode_upper}"
                play_btn.variant = "warning"
        except Exception:
            pass

    def _update_timer_visuals(self) -> None:
        try:
            td = self.query_one("#speech-timer-display", Static)
            td.set_class(not self.is_paused, "timer-running")
        except Exception:
            pass

    def _update_prep_gauges(self) -> None:
        if self.total_prep_time <= 0:
            try:
                self.query_one("#gauge-aff-prep", GaugeBar).set_value(100, label="AFF PREP 00:00")
                self.query_one("#gauge-neg-prep", GaugeBar).set_value(100, label="NEG PREP 00:00")
            except Exception:
                pass
            return

        aff_pct = int((self.aff_prep_remaining / self.total_prep_time) * 100)
        try:
            self.query_one("#gauge-aff-prep", GaugeBar).set_value(
                aff_pct, label=f"AFF PREP {self._format_time(self.aff_prep_remaining)}"
            )
        except Exception:
            pass

        neg_pct = int((self.neg_prep_remaining / self.total_prep_time) * 100)
        try:
            self.query_one("#gauge-neg-prep", GaugeBar).set_value(
                neg_pct, label=f"NEG PREP {self._format_time(self.neg_prep_remaining)}"
            )
        except Exception:
            pass

    def _update_mode_buttons(self) -> None:
        try:
            speech_btn = self.query_one("#btn-mode-speech", Button)
            aff_btn = self.query_one("#btn-mode-aff", Button)
            neg_btn = self.query_one("#btn-mode-neg", Button)

            speech_btn.variant = "success" if self.active_timer_mode == "speech" else "default"
            aff_btn.variant = "success" if self.active_timer_mode == "aff_prep" else "default"
            neg_btn.variant = "success" if self.active_timer_mode == "neg_prep" else "default"
        except Exception:
            pass

    @on(Button.Pressed, "#btn-play-pause")
    def play_pause_pressed(self) -> None:
        self.action_toggle_timer()

    @on(Button.Pressed, "#btn-reset")
    def reset_pressed(self) -> None:
        self.action_reset_timer()

    @on(Button.Pressed, "#btn-skip")
    def skip_pressed(self) -> None:
        self.action_next_speech()

    @on(Button.Pressed, "#btn-exit")
    def exit_pressed(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-mode-speech")
    def set_mode_speech(self) -> None:
        self.active_timer_mode = "speech"
        self._update_mode_buttons()
        self._update_play_pause_button()
        self._update_timer_visuals()

    @on(Button.Pressed, "#btn-mode-aff")
    def set_mode_aff(self) -> None:
        self.active_timer_mode = "aff_prep"
        self._update_mode_buttons()
        self._update_play_pause_button()
        self._update_timer_visuals()

    @on(Button.Pressed, "#btn-mode-neg")
    def set_mode_neg(self) -> None:
        self.active_timer_mode = "neg_prep"
        self._update_mode_buttons()
        self._update_play_pause_button()
        self._update_timer_visuals()

    def action_toggle_timer(self) -> None:
        self.is_paused = not self.is_paused
        self._update_play_pause_button()
        self._update_timer_visuals()

    def action_reset_timer(self) -> None:
        self.is_paused = True
        self._update_play_pause_button()
        self._update_timer_visuals()

        if self.active_timer_mode == "speech":
            if self.speeches:
                current_speech = self.speeches[self.speech_index]
                self.speech_time_remaining = current_speech["duration_seconds"]
                try:
                    self.query_one("#speech-timer-display", Static).update(
                        self._format_time(self.speech_time_remaining)
                    )
                except Exception:
                    pass
        elif self.active_timer_mode == "aff_prep":
            self.aff_prep_remaining = self.total_prep_time
            self._update_prep_gauges()
        elif self.active_timer_mode == "neg_prep":
            self.neg_prep_remaining = self.total_prep_time
            self._update_prep_gauges()

    def action_next_speech(self) -> None:
        if not self.speeches:
            return
        if self.speech_index < len(self.speeches) - 1:
            self.speech_index += 1
            self.is_paused = True
            self.active_timer_mode = "speech"

            current_speech = self.speeches[self.speech_index]
            self.speech_time_remaining = current_speech["duration_seconds"]

            try:
                self.query_one("#speech-name-display", Static).update(current_speech["name"])
                self.query_one("#speech-timer-display", Static).update(
                    self._format_time(self.speech_time_remaining)
                )
            except Exception:
                pass
            self._update_mode_buttons()
            self._update_play_pause_button()
            self._update_timer_visuals()
            self._safe_notify(
                f"Advanced to speech: {current_speech['name']}", severity="information"
            )
        else:
            self._safe_notify("Final speech reached. Debate round completed!", severity="success")

    def action_exit_screen(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id and event.button.id.startswith("spoken-"):
            card_id = int(event.button.id.split("-")[-1])
            increment_mastery(card_id)
            self.spoken_card_ids.add(card_id)
            self._safe_notify("Card marked as Spoken. Mastery incremented.", severity="success")
            self._reload_constructives()
        elif event.button.id and event.button.id.startswith("flow-"):
            card_id = int(event.button.id.split("-")[-1])
            card = next((c for c in self.cards if c["id"] == card_id), None)
            if card:
                try:
                    rl = self.query_one("#rebuttals-list", ListView)
                    clash_text = f"🔥 CLASH: [{card['side']}] {card['tag']}"
                    rl.mount(ListItem(Label(clash_text)))
                except Exception:
                    pass
                self._safe_notify(
                    f"Flowed to Rebuttals: {card['tag'][:30]}...",
                    severity="information",
                )

    @on(Input.Submitted, "#rebuttal-input")
    def add_custom_rebuttal(self, event: Input.Submitted) -> None:
        val = event.value.strip()
        if val:
            try:
                rl = self.query_one("#rebuttals-list", ListView)
                rl.mount(ListItem(Label(f"💬 {val}")))
            except Exception:
                pass
            event.input.value = ""
            self._safe_notify("Custom Rebuttal point added.", severity="information")

    @on(ListView.Selected, "#rebuttals-list")
    def remove_rebuttal(self, event: ListView.Selected) -> None:
        try:
            event.item.remove()
        except Exception:
            pass
        self._safe_notify("Rebuttal point removed.", severity="information")

    def tick(self) -> None:
        if self.is_paused:
            return

        if self.active_timer_mode == "speech":
            if self.speech_time_remaining > 0:
                self.speech_time_remaining -= 1
                try:
                    self.query_one("#speech-timer-display", Static).update(
                        self._format_time(self.speech_time_remaining)
                    )
                except Exception:
                    pass
                if self.speech_time_remaining == 0:
                    self.is_paused = True
                    self._update_play_pause_button()
                    self._update_timer_visuals()
                    self._safe_notify("Speech time expired!", severity="warning")
        elif self.active_timer_mode == "aff_prep":
            if self.aff_prep_remaining > 0:
                self.aff_prep_remaining -= 1
                self._update_prep_gauges()
                if self.aff_prep_remaining == 0:
                    self.is_paused = True
                    self._update_play_pause_button()
                    self._update_timer_visuals()
                    self._safe_notify("Affirmative Prep time expired!", severity="warning")
        elif self.active_timer_mode == "neg_prep":
            if self.neg_prep_remaining > 0:
                self.neg_prep_remaining -= 1
                self._update_prep_gauges()
                if self.neg_prep_remaining == 0:
                    self.is_paused = True
                    self._update_play_pause_button()
                    self._update_timer_visuals()
                    self._safe_notify("Negative Prep time expired!", severity="warning")

    def _format_time(self, seconds: int) -> str:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"
