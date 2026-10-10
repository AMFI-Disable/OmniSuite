"""Comprehensive unit tests for citation format parsing and research card metadata extraction.

Tests APA, MLA, Chicago, Harvard, BibTeX parsing, format auto-detection,
qualification extraction, warrant identification, tagline generation, debate side heuristics,
credibility scoring, and vault ingestion.

© 2026 OmniSuite. Built for the Digital Grandmaster.
"""

import os

import pytest
from omnidebate.ingest.citation import (
    batch_parse_citations,
    extract_research_card,
    format_debate_citation,
    ingest_citation_to_vault,
    parse_bibtex_file,
)
from omnishared.database import read_vault, setup_db
from omnishared.ingest import (
    CitationFormat,
    calculate_credibility,
    detect_citation_format,
    detect_debate_side,
    extract_card_metadata,
    extract_qualifications,
    extract_warrants,
    generate_debate_tag,
)
from omnishared.ingest import (
    parse_citation as parse_shared_citation,
)


@pytest.fixture(autouse=True)
def test_db(tmp_path):
    """Setup temporary database environment for tests."""
    db_file = tmp_path / "test_citation_vault.db"
    os.environ["EVIDENCE_VAULT_DB"] = str(db_file)
    setup_db()
    yield
    if db_file.exists():
        os.remove(db_file)
    if "EVIDENCE_VAULT_DB" in os.environ:
        del os.environ["EVIDENCE_VAULT_DB"]


# ---------------------------------------------------------------------------
# Citation Format Parsing Tests
# ---------------------------------------------------------------------------


def test_parse_apa_citation():
    raw_apa = (
        "Nordhaus, W. (2018). Climate Change Economics and Global Growth. "
        "Journal of Economic Perspectives, 32(4), 45-67. https://doi.org/10.1257/jep.32.4.45"
    )
    parsed = parse_shared_citation(raw_apa)

    assert parsed.format == CitationFormat.APA
    assert "Nordhaus" in parsed.primary_author_last_name
    assert parsed.year == "2018"
    assert "Climate Change Economics" in parsed.title
    assert "Journal of Economic Perspectives" in parsed.container_title
    assert parsed.volume == "32"
    assert parsed.issue == "4"
    assert "45-67" in parsed.pages
    assert "10.1257/jep.32.4.45" in parsed.doi


def test_parse_mla_citation():
    raw_mla = (
        'Smith, John A., and Bob Jones. "The Future of Artificial Intelligence in Forensics." '
        "Journal of Debate, vol. 15, no. 2, 2020, pp. 45-67."
    )
    parsed = parse_shared_citation(raw_mla)

    assert parsed.format == CitationFormat.MLA
    assert "Smith" in parsed.primary_author_last_name
    assert len(parsed.authors) >= 2
    assert parsed.year == "2020"
    assert "Future of Artificial Intelligence" in parsed.title
    assert "Journal of Debate" in parsed.container_title
    assert parsed.volume == "15"
    assert parsed.issue == "2"
    assert "45-67" in parsed.pages


def test_parse_chicago_citation():
    raw_chicago = (
        'Stiglitz, Joseph E. 2017. "Report of the High-Level Commission on Carbon Prices." '
        "Global Economic Review 25, no. 3 (2017): 101-125."
    )
    parsed = parse_shared_citation(raw_chicago)

    assert parsed.format == CitationFormat.CHICAGO
    assert "Stiglitz" in parsed.primary_author_last_name
    assert parsed.year == "2017"
    assert "Report of the High-Level Commission" in parsed.title
    assert "101-125" in parsed.pages


def test_parse_harvard_citation():
    raw_harvard = (
        "Metcalf, G.E., 2019. Carbon Taxes in Theory and Practice. "
        "NBER Working Paper Series, 44(1), pp.12-34."
    )
    parsed = parse_shared_citation(raw_harvard)

    assert parsed.format in (CitationFormat.HARVARD, CitationFormat.APA)
    assert "Metcalf" in parsed.primary_author_last_name
    assert parsed.year == "2019"
    assert "Carbon Taxes in Theory" in parsed.title
    assert "12-34" in parsed.pages


def test_parse_bibtex_citation():
    raw_bibtex = """@article{nordhaus2018climate,
        author = {Nordhaus, William and Stern, Nicholas},
        title = {Climate Change Economics and Policy},
        journal = {American Economic Review},
        volume = {108},
        number = {8},
        pages = {1913--1945},
        year = {2018},
        doi = {10.1257/aer.2018.1913}
    }"""
    parsed = parse_shared_citation(raw_bibtex)

    assert parsed.format == CitationFormat.BIBTEX
    assert "Nordhaus" in parsed.primary_author_last_name
    assert len(parsed.authors) == 2
    assert parsed.year == "2018"
    assert parsed.title == "Climate Change Economics and Policy"
    assert parsed.container_title == "American Economic Review"
    assert parsed.volume == "108"
    assert parsed.issue == "8"
    assert parsed.pages == "1913-1945"
    assert parsed.doi == "10.1257/aer.2018.1913"
    assert parsed.entry_type == "article"


def test_citation_format_auto_detection():
    assert detect_citation_format("@article{key, title={Test}}") == CitationFormat.BIBTEX
    assert (
        detect_citation_format('Smith, J. "Title." Journal, vol. 1, no. 2, 2020, pp. 5-10.')
        == CitationFormat.MLA
    )
    assert (
        detect_citation_format(
            "Smith, J. (2020). Title. Journal, 1(2), 5-10. https://doi.org/10.1000/182"
        )
        == CitationFormat.APA
    )


def test_fallback_junk_citation():
    parsed = parse_shared_citation("Just a raw unformatted text line with no clear pattern.")
    assert parsed.format == CitationFormat.UNKNOWN
    assert parsed.confidence < 0.7
    assert parsed.raw_citation == "Just a raw unformatted text line with no clear pattern."


def test_empty_citation():
    parsed = parse_shared_citation("")
    assert parsed.format == CitationFormat.UNKNOWN
    assert parsed.confidence == 0.0


# ---------------------------------------------------------------------------
# Structured Research Card Metadata Tests
# ---------------------------------------------------------------------------


def test_qualification_extraction():
    text = (
        "Dr. Jane Hanson, PhD in Economics and Senior Fellow at Brookings Institution, "
        "argues that carbon taxes stabilize global GDP."
    )
    quals = extract_qualifications(text)
    assert any("PhD" in q for q in quals)
    assert any("Senior Fellow" in q for q in quals)


def test_warrant_extraction():
    text = (
        "Climate change causes global warming. "
        "Consequently, we see a massive loss in global GDP. "
        "Extinction of key species is highly probable if warming continues. "
        "Therefore, rapid carbon tax adoption solves the crisis."
    )
    warrants = extract_warrants(text, max_warrants=3)
    assert len(warrants) <= 3
    assert any("causes" in w or "GDP" in w or "Extinction" in w or "solves" in w for w in warrants)


def test_generate_debate_tag():
    text = "Extinction of key species leads to severe collapse of ocean biodiversity and food security."
    tag = generate_debate_tag(text, title="Oceanic Ecosystem Collapse")
    assert len(tag.split()) >= 3 and len(tag.split()) <= 10


def test_detect_debate_side():
    aff_text = "Carbon pricing is an effective, imperative tool that significantly solves warming and promotes green energy."
    neg_text = "Carbon pricing is a counterproductive disaster that backfires, exacerbates poverty, and causes economic collapse."

    assert detect_debate_side(aff_text) == "AFF"
    assert detect_debate_side(neg_text) == "NEG"


def test_calculate_credibility():
    raw_bibtex = """@article{nordhaus2018,
        author = {Nordhaus, William},
        title = {Climate Economics},
        journal = {Journal of Economic Perspectives},
        year = {2021},
        doi = {10.1257/jep.32.4.45}
    }"""
    parsed = parse_shared_citation(raw_bibtex)
    quals = ["PhD in Economics", "Professor of Economics"]

    tier, score = calculate_credibility(parsed, quals)
    assert tier == 1
    assert score >= 0.75


def test_extract_card_metadata():
    raw_cite = "Hanson, J. (2022). Artificial Intelligence in Legal Systems. Journal of Law & Tech, 10(2), 15-30. https://doi.org/10.1000/jlt.2022.10"
    card_body = (
        "Professor Jane Hanson, PhD in Law at Harvard, demonstrates that automated document "
        "compiling reduces legal prep time by 80%. Consequently, law firms achieve higher efficiency."
    )

    meta = extract_card_metadata(raw_cite, card_text=card_body, default_side="AFF")

    assert meta.citation_header == "Hanson '22"
    assert meta.credibility_tier == 1
    assert meta.quality_score > 0.7
    assert meta.side == "AFF"
    assert len(meta.author_qualifications) >= 1
    assert len(meta.warrants) >= 1


# ---------------------------------------------------------------------------
# High-Level OmniDebate Citation APIs Tests
# ---------------------------------------------------------------------------


def test_format_debate_citation():
    parsed = parse_shared_citation(
        'Hanson, Jane. "The Future of Forensics." Journal of Debate, vol. 12, no. 3, May 2026, pp. 45-67.'
    )
    formatted = format_debate_citation(parsed, qualifications="PhD in Forensics")

    assert formatted.startswith("Hanson '26")
    assert "Jane Hanson" in formatted
    assert "PhD in Forensics" in formatted
    assert '"The Future of Forensics"' in formatted
    assert "pp. 45-67" in formatted


def test_extract_research_card():
    raw_cite = "Metcalf, G. (2019). Carbon Taxes. NBER Working Paper 25911."
    card_body = "Implementing carbon taxes results in immediate reductions in carbon emissions."

    card = extract_research_card(raw_cite, card_text=card_body, side="AFF")

    assert card["side"] == "AFF"
    assert "tag" in card
    assert "citation" in card
    assert "tier" in card
    assert card["tier"] in (1, 2, 3)
    assert "metadata" in card
    assert card["metadata"]["year"] == "2019"


def test_batch_parse_citations():
    citations = [
        "Nordhaus, W. (2018). Climate Economics.",
        'Smith, J. "Forensic AI." Journal of Debate, vol. 1, no. 2, 2020, pp. 10-20.',
    ]
    results = batch_parse_citations(citations)

    assert len(results) == 2
    assert results[0]["year"] == "2018"
    assert results[1]["year"] == "2020"


def test_parse_bibtex_file_multi_entry():
    bibtex_content = """
    @article{card1,
        author = {Smith, John},
        title = {First Article},
        year = {2021},
        journal = {Journal A}
    }
    @article{card2,
        author = {Doe, Jane},
        title = {Second Article},
        year = {2022},
        journal = {Journal B}
    }
    """
    cards = parse_bibtex_file(bibtex_content)

    assert len(cards) == 2
    assert cards[0]["metadata"]["primary_author"] == "Smith, John"
    assert cards[1]["metadata"]["primary_author"] == "Doe, Jane"


def test_ingest_citation_to_vault():
    # Setup test motion in database
    from omnishared.database import add_motion

    motion_id = add_motion("Climate Change Policy")

    raw_cite = "Stiglitz, J. (2020). Carbon Economics. Brookings Review."
    body_text = "Carbon pricing solves systemic climate warming and restores economic solvency."

    ingested = ingest_citation_to_vault(motion_id, raw_cite, card_text=body_text, side="AFF")

    assert ingested["side"] == "AFF"
    assert "Stiglitz" in ingested["citation"]

    # Verify database persistence
    vault_cards = read_vault(motion_id)
    assert len(vault_cards) == 1
    assert vault_cards[0]["side"] == "AFF"
    assert "Stiglitz" in vault_cards[0]["citation"]
