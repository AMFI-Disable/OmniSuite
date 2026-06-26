import pytest
from unittest.mock import patch
from textual.app import App
from omnidebate.ui.widgets.command_hud import CommandHUD
from omnidebate.ui.screens.speech import SpeechPrepScreen
from omnidebate.core.database import setup_db, add_motion
import os


@pytest.fixture(autouse=True)
def test_db(tmp_path):
    db_file = tmp_path / "test_vault.db"
    os.environ["EVIDENCE_VAULT_DB"] = str(db_file)
    setup_db()
    yield
    if db_file.exists():
        os.remove(db_file)
    if "EVIDENCE_VAULT_DB" in os.environ:
        del os.environ["EVIDENCE_VAULT_DB"]


# A mock format set for testing
MOCK_FORMATS = {
    "Test Format": {
        "speeches": [
            {"name": "Constructive", "duration_seconds": 240},
            {"name": "Rebuttal", "duration_seconds": 120},
        ],
        "prep_time_seconds": 180,
    }
}


class TimerTestApp(App):
    def __init__(self):
        super().__init__()
        self.formats = MOCK_FORMATS

    def compose(self):
        yield CommandHUD(self.formats, default_format="Test Format", id="hud")


@pytest.mark.asyncio
async def test_command_hud_timer_transitions():
    app = TimerTestApp()
    async with app.run_test() as pilot:
        hud = app.query_one("#hud", CommandHUD)

        # Verify initial paused state
        btn_speech = hud.query_one("#btn-speech-toggle")
        btn_prep = hud.query_one("#btn-prep-toggle")
        assert "START SPEECH" in str(btn_speech.label)
        assert "START PREP" in str(btn_prep.label)
        assert hud._timer_running is False
        assert hud._prep_running is False

        # Toggle speech directly and verify
        hud.speech_toggle()
        await pilot.pause()
        assert hud._timer_running is True
        assert hud._prep_running is False
        assert "PAUSE SPEECH" in str(btn_speech.label)
        assert "START PREP" in str(btn_prep.label)

        # Toggle prep directly (should pause speech)
        hud.prep_toggle()
        await pilot.pause()
        assert hud._timer_running is False
        assert hud._prep_running is True
        assert "START SPEECH" in str(btn_speech.label)
        assert "PAUSE PREP" in str(btn_prep.label)

        # Toggle prep directly again to pause
        hud.prep_toggle()
        await pilot.pause()
        assert hud._timer_running is False
        assert hud._prep_running is False
        assert "START SPEECH" in str(btn_speech.label)
        assert "START PREP" in str(btn_prep.label)

        # Reset
        hud.reset_fmt()
        await pilot.pause()
        assert hud._timer_running is False
        assert hud._prep_running is False


class SpeechScreenTestApp(App):
    def __init__(self):
        super().__init__()

    def on_mount(self):
        self.push_screen(SpeechPrepScreen(motion_id=1))


@pytest.mark.asyncio
@patch("omnidebate.ui.screens.speech.load_formats")
async def test_speech_prep_screen_context_labels(mock_load):
    mock_load.return_value = MOCK_FORMATS
    add_motion("Test Motion")  # Create motion 1 in db

    app = SpeechScreenTestApp()
    async with app.run_test() as pilot:
        await pilot.pause()  # Let deferred mount tasks complete
        screen = app.screen
        assert isinstance(screen, SpeechPrepScreen)

        # Verify Play/Pause button initial label
        play_btn = screen.query_one("#btn-play-pause")
        assert "PLAY SPEECH" in str(play_btn.label)

        # Click Run Aff Prep mode button
        await pilot.click("#btn-mode-aff")
        await pilot.pause()
        assert "PLAY AFF PREP" in str(play_btn.label)

        # Click Play to start Aff Prep timer
        await pilot.click("#btn-play-pause")
        await pilot.pause()
        assert "PAUSE AFF PREP" in str(play_btn.label)
        assert screen.is_paused is False

        # Verify visual class on timer display when running
        timer_display = screen.query_one("#speech-timer-display")
        assert "timer-running" in timer_display.classes
