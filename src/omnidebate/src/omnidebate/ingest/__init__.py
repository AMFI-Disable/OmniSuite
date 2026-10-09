"""OmniDebate Ingest Package.

Provides high-level citation parsing, research card metadata extraction,
and vault ingestion tools.

© 2026 OmniSuite. Built for the Digital Grandmaster.
"""

from omnidebate.ingest.citation import (
    batch_parse_citations,
    extract_research_card,
    format_debate_citation,
    ingest_citation_to_vault,
    parse_bibtex_file,
    parse_citation,
)

__all__ = [
    "parse_citation",
    "format_debate_citation",
    "extract_research_card",
    "batch_parse_citations",
    "parse_bibtex_file",
    "ingest_citation_to_vault",
]
