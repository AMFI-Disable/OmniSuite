"""Tests for AI tools module.

Uses mocking to avoid requiring an Ollama server.
"""

import pytest
from unittest.mock import patch, MagicMock
from omnidebate.core.ai_tools import (
    summarize_card,
    generate_counter_arguments,
    analyze_impact_chain,
    score_case_strength,
    find_evidence_gaps,
    generate_case_outline,
    generate_cross_questions,
    rewrite_for_clarity,
)


SAMPLE_CARD_TEXT = (
    "Carbon pricing mechanisms have been shown to reduce emissions by up to 40% "
    "in jurisdictions that implement them. Smith et al. (2023) found that a $50/ton "
    "carbon tax in British Columbia reduced fuel consumption by 19% over 10 years "
    "without measurable economic harm."
)


@pytest.fixture
def mock_ai_response():
    """Mock the generate_completion function."""
    with patch("omnidebate.core.ai_tools.generate_completion") as mock:
        mock.return_value = "AI response text"
        yield mock


@pytest.fixture
def mock_ai_offline():
    """Mock Ollama being offline."""
    with patch("omnidebate.core.ai_tools.generate_completion") as mock:
        from omnishared.ai.client import OllamaOfflineError
        mock.side_effect = OllamaOfflineError("Ollama not running")
        yield mock


# ─── Happy Path ───────────────────────────────────────────────────────────────


class TestAIToolsOnline:
    def test_summarize_card(self, mock_ai_response):
        result = summarize_card(SAMPLE_CARD_TEXT)
        assert result == "AI response text"
        mock_ai_response.assert_called_once()

    def test_generate_counter_arguments(self, mock_ai_response):
        result = generate_counter_arguments(SAMPLE_CARD_TEXT)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_counter_with_side(self, mock_ai_response):
        result = generate_counter_arguments(SAMPLE_CARD_TEXT, side="aff")
        assert result == "AI response text"

    def test_analyze_impact_chain(self, mock_ai_response):
        result = analyze_impact_chain(SAMPLE_CARD_TEXT)
        assert result == "AI response text"

    def test_score_case_strength(self, mock_ai_response):
        cards = [{"tag": "Card 1", "text": SAMPLE_CARD_TEXT, "side": "AFF"}]
        result = score_case_strength(cards)
        assert result == "AI response text"

    def test_score_case_empty_cards(self, mock_ai_response):
        result = score_case_strength([])
        assert isinstance(result, str)

    def test_find_evidence_gaps(self, mock_ai_response):
        cards = [{"tag": "Card 1", "text": SAMPLE_CARD_TEXT}]
        result = find_evidence_gaps(cards, "Carbon tax reduces emissions")
        assert result == "AI response text"

    def test_generate_case_outline(self, mock_ai_response):
        result = generate_case_outline("Carbon tax reduces emissions", "AFF")
        assert result == "AI response text"

    def test_generate_case_outline_with_format(self, mock_ai_response):
        result = generate_case_outline("Motion text", "NEG", format_name="Lincoln-Douglas")
        assert result == "AI response text"

    def test_generate_cross_questions(self, mock_ai_response):
        result = generate_cross_questions(SAMPLE_CARD_TEXT)
        assert result == "AI response text"

    def test_rewrite_for_clarity(self, mock_ai_response):
        result = rewrite_for_clarity(SAMPLE_CARD_TEXT)
        assert result == "AI response text"


# ─── Offline / Error Handling ─────────────────────────────────────────────────


class TestAIToolsOffline:
    """All AI tools must gracefully handle OllamaOfflineError."""

    def test_summarize_card_offline(self, mock_ai_offline):
        result = summarize_card(SAMPLE_CARD_TEXT)
        assert isinstance(result, str)
        assert len(result) > 0
        # Should not raise — returns a descriptive error string

    def test_counter_args_offline(self, mock_ai_offline):
        result = generate_counter_arguments(SAMPLE_CARD_TEXT)
        assert isinstance(result, str)

    def test_impact_chain_offline(self, mock_ai_offline):
        result = analyze_impact_chain(SAMPLE_CARD_TEXT)
        assert isinstance(result, str)

    def test_case_strength_offline(self, mock_ai_offline):
        result = score_case_strength([{"tag": "t", "text": "txt"}])
        assert isinstance(result, str)

    def test_evidence_gaps_offline(self, mock_ai_offline):
        result = find_evidence_gaps([], "motion")
        assert isinstance(result, str)

    def test_case_outline_offline(self, mock_ai_offline):
        result = generate_case_outline("motion", "AFF")
        assert isinstance(result, str)

    def test_cross_questions_offline(self, mock_ai_offline):
        result = generate_cross_questions(SAMPLE_CARD_TEXT)
        assert isinstance(result, str)

    def test_rewrite_offline(self, mock_ai_offline):
        result = rewrite_for_clarity(SAMPLE_CARD_TEXT)
        assert isinstance(result, str)
