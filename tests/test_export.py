import os
import pytest
from omnidebate.core.database import setup_db, add_motion, add_card
from omnidebate.core.export import export_brief_markdown


@pytest.fixture(autouse=True)
def test_env(tmp_path):
    db_file = tmp_path / "test_vault.db"
    os.environ["EVIDENCE_VAULT_DB"] = str(db_file)
    setup_db()
    # Mock exports dir
    exports_dir = tmp_path / "exports"
    exports_dir.mkdir()
    from omnidebate.core import config

    original_exports_dir = config.EXPORTS_DIR
    config.EXPORTS_DIR = str(exports_dir)

    yield

    config.EXPORTS_DIR = original_exports_dir
    if "EVIDENCE_VAULT_DB" in os.environ:
        del os.environ["EVIDENCE_VAULT_DB"]


def test_export():
    mid = add_motion("Test Motion")
    add_card(mid, {"tag": "AFF Card", "side": "AFF", "text": "...", "citation": "..."})
    add_card(mid, {"tag": "NEG Card", "side": "NEG", "text": "...", "citation": "..."})

    fname = export_brief_markdown(mid, "Test Motion")
    assert os.path.exists(fname)
    with open(fname, "r") as f:
        content = f.read()
        assert "TEST MOTION" in content
        assert "AFF CARD" in content
        assert "NEG CARD" in content
