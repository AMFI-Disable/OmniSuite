import os

import pytest
from omnidebate.ui.screens.speech import SpeechPrepScreen
from omnishared.database import add_card, add_motion, read_vault, setup_db


@pytest.fixture(autouse=True)
def test_db(tmp_path):
    db_file = tmp_path / "test_vault.db"
    os.environ["EVIDENCE_VAULT_DB"] = str(db_file)
    setup_db()

    # Add a mock motion and some mock cards
    motion_id = add_motion("Test Motion")
    add_card(
        motion_id,
        {
            "tag": "Plan solves warming",
            "citation": "Jones 2024",
            "text": "The plan reduces warming dramatically.",
            "side": "AFF",
            "tier": 1,
            "language": "EN",
            "mastery": 0,
        },
    )

    yield
    if "EVIDENCE_VAULT_DB" in os.environ:
        del os.environ["EVIDENCE_VAULT_DB"]


def test_timer_state_engine():
    screen = SpeechPrepScreen(motion_id=1)

    # Setup mock speeches and durations
    screen.total_prep_time = 180
    screen.aff_prep_remaining = 180
    screen.neg_prep_remaining = 180
    screen.speech_time_remaining = 240
    screen.is_paused = True
    screen.active_timer_mode = "speech"

    # 1. Play/Pause toggle
    screen.action_toggle_timer()
    assert screen.is_paused is False

    # 2. Speech tick decrement
    screen.tick()
    assert screen.speech_time_remaining == 239
    assert screen.aff_prep_remaining == 180

    # 3. Pause
    screen.action_toggle_timer()
    assert screen.is_paused is True
    screen.tick()
    assert screen.speech_time_remaining == 239

    # 4. AFF Prep decrement
    screen.active_timer_mode = "aff_prep"
    screen.action_toggle_timer()  # Resume
    screen.tick()
    assert screen.aff_prep_remaining == 179
    assert screen.speech_time_remaining == 239  # remains unchanged

    # 5. NEG Prep decrement
    screen.active_timer_mode = "neg_prep"
    screen.tick()
    assert screen.neg_prep_remaining == 179
    assert screen.aff_prep_remaining == 179

    # 6. Reset timer (for NEG prep)
    screen.action_reset_timer()
    assert screen.neg_prep_remaining == 180
    assert screen.is_paused is True


def test_switching_active_speeches():
    screen = SpeechPrepScreen(motion_id=1)
    screen.speeches = [
        {"name": "Opening statement A", "duration_seconds": 120},
        {"name": "Opening statement B", "duration_seconds": 120},
    ]
    screen.speech_index = 0
    screen.speech_time_remaining = 120
    screen.is_paused = False

    # Advanced/Skip to next speech
    screen.action_next_speech()
    assert screen.speech_index == 1
    assert screen.speech_time_remaining == 120
    assert screen.is_paused is True
    assert screen.active_timer_mode == "speech"


def test_card_mastery_increment_on_spoken():
    screen = SpeechPrepScreen(motion_id=1)

    # Read initial card
    cards = read_vault(1)
    assert len(cards) == 1
    card = cards[0]
    assert card["mastery"] == 0

    # Mock event object to simulate button press
    class DummyButton:
        def __init__(self, id):
            self.id = id

    class DummyEvent:
        def __init__(self, id):
            self.button = DummyButton(id)

    # Trigger spoken action
    screen.cards = cards
    screen.on_button_pressed(DummyEvent(f"spoken-{card['id']}"))

    # Verify mastery in SQLite database incremented
    updated_cards = read_vault(1)
    assert updated_cards[0]["mastery"] == 1
    assert card["id"] in screen.spoken_card_ids
