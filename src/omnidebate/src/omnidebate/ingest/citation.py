"""OmniDebate Citation Ingest Workstation.

Provides advanced citation format parsing (APA, MLA, Chicago, Harvard, BibTeX),
debate card citation header formatting, structured research card metadata extraction,
and vault ingestion integration.

© 2026 OmniSuite. Built for the Digital Grandmaster.
"""

import os
import re
from datetime import datetime, timezone
from typing import Any, Optional, Union

from omnishared.database import add_card
from omnishared.ingest import (
    CitationFormat,
    ParsedCitation,
    extract_card_metadata,
)
from omnishared.ingest import (
    parse_citation as parse_shared_citation,
)


def parse_citation(text: str, fmt: Optional[Union[str, CitationFormat]] = None) -> dict[str, Any]:
    """Parse a raw citation string into a structured dictionary.

    Args:
        text: Raw citation text (APA, MLA, Chicago, Harvard, BibTeX, or raw text).
        fmt: Optional citation format name or enum.

    Returns:
        Dictionary containing parsed citation fields.
    """
    parsed = parse_shared_citation(text, fmt=fmt)
    return parsed.to_dict()


def format_author_name(author_str: str) -> str:
    """Convert 'Last, First M.' to 'First M. Last' for clean display."""
    if not author_str:
        return ""
    if "," in author_str:
        parts = author_str.split(",", 1)
        return f"{parts[1].strip()} {parts[0].strip()}".strip()
    return author_str


def format_debate_citation(
    parsed: Union[dict[str, Any], ParsedCitation], qualifications: str = ""
) -> str:
    """Format a parsed citation into a standardized competitive debate card header.

    Example output:
        Hanson '26 (Jane Hanson, PhD, Journal of Forensics, vol. 12, no. 3, "The Future of Forensics", pp. 45-67)

    Args:
        parsed: ParsedCitation object or dictionary representation.
        qualifications: Optional author qualification override/addition.

    Returns:
        Formatted debate citation header string.
    """
    p_dict = parsed if isinstance(parsed, dict) else parsed.to_dict()

    last_name = p_dict.get("primary_author_last_name") or "Anon"
    year_str = str(p_dict.get("year", ""))
    yr_short = year_short(year_str)

    header_tag = f"{last_name} '{yr_short}" if yr_short else last_name

    # Build parentheses details
    authors_list = p_dict.get("authors", [])
    if authors_list:
        formatted_authors = [format_author_name(a) for a in authors_list]
        author_str = ", ".join(formatted_authors)
    else:
        author_str = format_author_name(last_name)

    parts = [author_str]

    if qualifications:
        parts.append(qualifications)

    container = p_dict.get("container_title")
    if container:
        parts.append(container)

    vol = p_dict.get("volume")
    iss = p_dict.get("issue")
    if vol and iss:
        parts.append(f"vol. {vol}, no. {iss}")
    elif vol:
        parts.append(f"vol. {vol}")

    title = p_dict.get("title")
    if title:
        parts.append(f'"{title}"')

    pages = p_dict.get("pages")
    if pages:
        parts.append(f"pp. {pages}")

    doi = p_dict.get("doi")
    url = p_dict.get("url")
    if doi:
        parts.append(f"https://doi.org/{doi}" if not doi.startswith("http") else doi)
    elif url:
        parts.append(url)

    details = ", ".join([p for p in parts if p])
    return f"{header_tag} ({details})"


def year_short(year_str: str) -> str:
    """Convert 4-digit year string to 2-digit short year string."""
    clean = re.sub(r"\D", "", year_str)
    if len(clean) == 4:
        return clean[2:]
    return clean


def extract_research_card(
    raw_citation: str,
    card_text: str = "",
    motion_id: Optional[int] = None,
    side: str = "AFF",
) -> dict[str, Any]:
    """Extract full structured research card and return normalized vault card dictionary.

    Args:
        raw_citation: Raw citation string or BibTeX block.
        card_text: Card body text.
        motion_id: Optional SQLite motion ID.
        side: Default debate side ('AFF' or 'NEG').

    Returns:
        Dictionary ready for vault insertion or compilation:
        {
            "tag": tagline,
            "citation": formatted_citation,
            "text": card_text,
            "side": side,
            "language": "EN",
            "tier": credibility_tier,
            "mastery": 0,
            "timestamp": ISO timestamp,
            "metadata": ResearchCardMetadata dict,
        }
    """
    card_meta = extract_card_metadata(raw_citation, card_text=card_text, default_side=side)
    formatted_cite = format_debate_citation(
        card_meta.raw_citation_data,
        qualifications=", ".join(card_meta.author_qualifications),
    )

    card_dict: dict[str, Any] = {
        "tag": card_meta.tag,
        "citation": formatted_cite if len(formatted_cite) > 10 else raw_citation,
        "text": card_text if card_text.strip() else card_meta.summary,
        "side": card_meta.side,
        "language": "EN",
        "tier": card_meta.credibility_tier,
        "mastery": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()[:19],
        "metadata": card_meta.to_dict(),
    }

    if motion_id is not None:
        card_dict["motion_id"] = motion_id

    return card_dict


def batch_parse_citations(citations: list[str]) -> list[dict[str, Any]]:
    """Batch parse multiple citation strings into structured dictionaries.

    Args:
        citations: List of raw citation strings.

    Returns:
        List of parsed citation dictionaries.
    """
    return [parse_citation(c) for c in citations if c and c.strip()]


def parse_bibtex_file(content_or_filepath: str) -> list[dict[str, Any]]:
    """Parse a BibTeX file path or raw string containing multiple BibTeX entries.

    Args:
        content_or_filepath: File path to .bib file or raw string containing BibTeX content.

    Returns:
        List of research card dictionaries extracted from the BibTeX entries.
    """
    if os.path.exists(content_or_filepath) and os.path.isfile(content_or_filepath):
        with open(content_or_filepath, encoding="utf-8", errors="replace") as fh:
            content = fh.read()
    else:
        content = content_or_filepath

    # Split by @entry_type{
    entry_starts = list(re.finditer(r"@([A-Za-z0-9_]+)\s*[\{\(]", content))
    if not entry_starts:
        return []

    cards: list[dict[str, Any]] = []
    for i, match in enumerate(entry_starts):
        start = match.start()
        end = entry_starts[i + 1].start() if i + 1 < len(entry_starts) else len(content)
        block = content[start:end].strip()

        if block:
            card = extract_research_card(block)
            cards.append(card)

    return cards


def ingest_citation_to_vault(
    motion_id: int,
    raw_citation: str,
    card_text: str = "",
    side: str = "AFF",
) -> dict[str, Any]:
    """Extract research card metadata and insert the card into the evidence vault database.

    Args:
        motion_id: Target motion ID in SQLite database.
        raw_citation: Citation text or BibTeX entry.
        card_text: Card body text.
        side: Debate side ('AFF' or 'NEG').

    Returns:
        The ingested card dictionary.
    """
    card = extract_research_card(raw_citation, card_text=card_text, motion_id=motion_id, side=side)
    add_card(motion_id, card)
    return card
