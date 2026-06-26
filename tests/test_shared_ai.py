import pytest
from unittest.mock import patch, MagicMock
from omnishared.ai.client import (
    check_ollama_status,
    generate_completion,
    OllamaOfflineError,
)
from omnidebate.core.oracle import OracleEngine


@patch("requests.get")
def test_check_ollama_status_online(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp
    assert check_ollama_status() is True


@patch("requests.get")
def test_check_ollama_status_offline(mock_get):
    mock_get.side_effect = Exception("offline")
    assert check_ollama_status() is False


@patch("requests.post")
def test_generate_completion_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": "Generative output"}
    mock_post.return_value = mock_resp

    res = generate_completion("test prompt")
    assert res == "Generative output"


@patch("requests.post")
def test_generate_completion_offline(mock_post):
    mock_post.side_effect = Exception("timeout")
    with pytest.raises(OllamaOfflineError):
        generate_completion("test prompt")


@patch("omnishared.ai.check_ollama_status")
@patch("omnishared.ai.generate_completion")
def test_oracle_simulations_with_ai(mock_gen, mock_status):
    mock_status.return_value = True
    mock_gen.return_value = "OPPONENT ATTACK:\nThis is a generative attack.\n\nCOUNTER-REBUTTAL:\nThis is a generative defense."

    card = {
        "tag": "Climate Change",
        "side": "AFF",
        "text": "Climate causes extinction.",
        "mastery": 2,
        "tier": 3,
    }
    spar = OracleEngine.simulate_sparring(card)
    assert any("GENERATIVE" in line for line in spar)
    assert any("This is a generative attack" in line for line in spar)
    assert any("This is a generative defense" in line for line in spar)
