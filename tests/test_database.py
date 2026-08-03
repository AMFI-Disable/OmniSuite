import os

import pytest
from omnidebate.core.database import (
    add_card,
    add_motion,
    delete_card,
    get_trash,
    list_motions,
    read_vault,
    restore_trash,
    setup_db,
)


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


def test_motions():
    mid = add_motion("Test Motion")
    motions = list_motions()
    assert len(motions) == 1
    assert motions[0]["name"] == "Test Motion"
    assert motions[0]["id"] == mid


def test_cards():
    mid = add_motion("Test Motion")
    card_data = {
        "tag": "Test Tag",
        "citation": "Source 2023",
        "side": "AFF",
        "text": "Evidence content",
        "language": "EN",
        "tier": 1,
    }
    add_card(mid, card_data)
    cards = read_vault(mid)
    assert len(cards) == 1
    assert cards[0]["tag"] == "Test Tag"


def test_soft_delete_and_restore():
    mid = add_motion("Test Motion")
    card_data = {"tag": "To Delete", "side": "AFF", "text": "...", "citation": "..."}
    add_card(mid, card_data)

    cards = read_vault(mid)
    cid = cards[0]["id"]

    delete_card(cid, mid)
    assert len(read_vault(mid)) == 0

    trash = get_trash()
    assert len(trash) == 1
    assert trash[0]["card"]["tag"] == "To Delete"

    restore_trash(trash[0]["id"])
    assert len(read_vault(mid)) == 1
    assert read_vault(mid)[0]["tag"] == "To Delete"
