"""Unit tests for OmniSuite Web Viewer application server."""

import json
import os
import time
import urllib.request

import pytest
from omnishared.database import add_card, add_motion, setup_db

from omnisuite.web import OmniWebServer


@pytest.fixture
def test_db_path(tmp_path):
    db_file = str(tmp_path / "web_test_vault.db")
    os.environ["EVIDENCE_VAULT_DB"] = db_file
    setup_db()
    mid = add_motion("Web Server Motion")
    add_card(
        mid,
        {
            "tag": "Web Tag",
            "citation": "Web Citation 2026",
            "side": "AFF",
            "text": "Web evidence text",
        },
    )
    yield db_file
    if os.path.exists(db_file):
        os.remove(db_file)


@pytest.fixture
def running_server(test_db_path):
    server = OmniWebServer(host="127.0.0.1", port=0, db_path=test_db_path)
    server.start()
    time.sleep(0.1)
    yield server
    server.stop()


def _http_request(url: str, method: str = "GET", data: dict | None = None) -> tuple[int, dict | str]:
    headers = {}
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read().decode("utf-8")
            if "application/json" in content_type:
                return resp.status, json.loads(raw)
            return resp.status, raw
    except urllib.error.HTTPError as err:
        raw = err.read().decode("utf-8")
        try:
            return err.code, json.loads(raw)
        except Exception:
            return err.code, raw


def test_web_server_lifecycle(test_db_path):
    server = OmniWebServer(host="127.0.0.1", port=0, db_path=test_db_path)
    assert not server.is_running
    server.start()
    assert server.is_running
    assert server.port > 0
    server.stop()
    assert not server.is_running


def test_web_viewer_html(running_server):
    status, body = _http_request(f"{running_server.url}/")
    assert status == 200
    assert "<title>OmniSuite Web Viewer</title>" in body


def test_api_status(running_server):
    status, body = _http_request(f"{running_server.url}/api/status")
    assert status == 200
    assert body["status"] == "ok"
    assert body["version"] == "1.0.0"
    assert body["motion_count"] >= 1
    assert body["card_count"] >= 1


def test_api_motions(running_server):
    status, motions = _http_request(f"{running_server.url}/api/motions")
    assert status == 200
    assert isinstance(motions, list)
    assert len(motions) >= 1
    assert motions[0]["name"] == "Web Server Motion"

    # POST new motion
    status, res = _http_request(
        f"{running_server.url}/api/motions",
        method="POST",
        data={"name": "New Web Motion"},
    )
    assert status == 201
    assert res["status"] == "created"
    assert "id" in res

    # Verify new motion is listed
    _, updated_motions = _http_request(f"{running_server.url}/api/motions")
    names = [m["name"] for m in updated_motions]
    assert "New Web Motion" in names


def test_api_cards_crud(running_server):
    # Get initial motions
    _, motions = _http_request(f"{running_server.url}/api/motions")
    mid = motions[0]["id"]

    # GET cards
    status, cards = _http_request(f"{running_server.url}/api/cards?motion_id={mid}")
    assert status == 200
    assert len(cards) >= 1
    cid = cards[0]["id"]

    # GET single card
    status, card = _http_request(f"{running_server.url}/api/cards/{cid}")
    assert status == 200
    assert card["id"] == cid

    # POST new card
    status, res = _http_request(
        f"{running_server.url}/api/cards",
        method="POST",
        data={
            "motion_id": mid,
            "tag": "Created Card",
            "citation": "New Citation",
            "side": "NEG",
            "text": "Card created via REST API",
        },
    )
    assert status == 201

    # PUT update card
    status, res = _http_request(
        f"{running_server.url}/api/cards/{cid}",
        method="PUT",
        data={
            "tag": "Updated Web Tag",
            "citation": "Updated Citation",
            "side": "AFF",
            "text": "Updated text via API",
            "language": "EN",
            "mastery": 3,
            "tier": 1,
            "timestamp": "2026-08-09T10:00:00Z",
        },
    )
    assert status == 200
    assert res["status"] == "updated"

    # DELETE card
    status, res = _http_request(
        f"{running_server.url}/api/cards/{cid}?motion_id={mid}",
        method="DELETE",
    )
    assert status == 200
    assert res["status"] == "deleted"


def test_api_sync_endpoint(running_server):
    # GET sync changeset
    status, changeset = _http_request(f"{running_server.url}/api/sync")
    assert status == 200
    assert "vault_checksum" in changeset
    assert "motions" in changeset
    assert "cards" in changeset

    # POST sync changeset
    new_changeset = {
        "schema_version": "1.0",
        "motions": [{"id": 99, "name": "Synced Motion", "is_archived": 0}],
        "cards": [
            {
                "id": 999,
                "motion_id": 99,
                "tag": "Synced Tag",
                "citation": "Synced Citation",
                "side": "AFF",
                "text": "Synced text",
                "language": "EN",
                "mastery": 1,
                "tier": 1,
                "timestamp": "2026-08-09T10:00:00Z",
            }
        ],
    }
    status, res = _http_request(
        f"{running_server.url}/api/sync",
        method="POST",
        data=new_changeset,
    )
    assert status == 200
    assert res["status"] == "ok"
    assert res["stats"]["inserted_motions"] == 1
    assert res["stats"]["inserted_cards"] == 1


def test_cli_web_parser():
    from omnisuite.cli import main

    # Test parser help or version without crashing
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
