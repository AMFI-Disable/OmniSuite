"""OmniShared Ingest Package.

Provides shared ingestion components for citation parsing and research card metadata extraction.

© 2026 OmniSuite. Built for the Digital Grandmaster.
"""

from omnishared.ingest.card_metadata import (
    ResearchCardMetadata,
    calculate_credibility,
    detect_debate_side,
    extract_card_metadata,
    extract_qualifications,
    extract_warrants,
    generate_debate_tag,
)
from omnishared.ingest.citation_parser import (
    CitationFormat,
    ParsedCitation,
    detect_citation_format,
    extract_doi,
    extract_url,
    extract_year,
    parse_citation,
)

__all__ = [
    "CitationFormat",
    "ParsedCitation",
    "detect_citation_format",
    "extract_doi",
    "extract_url",
    "extract_year",
    "parse_citation",
    "ResearchCardMetadata",
    "extract_card_metadata",
    "extract_qualifications",
    "extract_warrants",
    "generate_debate_tag",
    "calculate_credibility",
    "detect_debate_side",
]
