"""OmniShared Structured Research Card Metadata Extractor.

Extracts structured research metadata from raw evidence cards and citations,
including author qualifications, argument warrants, debate taglines,
debate side heuristics, credibility tiers, and quality scores.

© 2026 OmniSuite. Built for the Digital Grandmaster.
"""

import re
from dataclasses import dataclass, field
from typing import Any

from omnishared.ingest.citation_parser import (
    ParsedCitation,
    parse_citation,
)


@dataclass
class ResearchCardMetadata:
    citation_header: str  # Short debate cite header e.g. "Smith '20"
    full_citation: str
    tag: str  # Tagline / argument summary
    warrants: list[str]  # Key claims / warrants
    side: str  # "AFF" or "NEG"
    author_qualifications: list[str]  # Degrees, titles, affiliations
    primary_author: str
    author_last_name: str
    year: str
    publication: str  # Journal, Book, Website
    title: str
    doi_or_url: str
    credibility_tier: int  # 1 (Academic/Peer-reviewed), 2 (Think Tank/Gov), 3 (Web)
    quality_score: float  # 0.0 - 1.0 overall score
    keywords: list[str]
    summary: str
    raw_citation_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "citation_header": self.citation_header,
            "full_citation": self.full_citation,
            "tag": self.tag,
            "warrants": list(self.warrants),
            "side": self.side,
            "author_qualifications": list(self.author_qualifications),
            "primary_author": self.primary_author,
            "author_last_name": self.author_last_name,
            "year": self.year,
            "publication": self.publication,
            "title": self.title,
            "doi_or_url": self.doi_or_url,
            "credibility_tier": self.credibility_tier,
            "quality_score": round(self.quality_score, 3),
            "keywords": list(self.keywords),
            "summary": self.summary,
            "raw_citation_data": self.raw_citation_data,
        }


# ---------------------------------------------------------------------------
# Qualification & Credibility Extraction
# ---------------------------------------------------------------------------

_QUALIFICATION_PATTERNS = [
    re.compile(
        r"\b(Ph\.?D\.?|M\.?D\.?|J\.?D\.?|M\.?A\.?|M\.?S\.?|B\.?A\.?|B\.?S\.?)\b", re.IGNORECASE
    ),
    re.compile(
        r"\b(Professor|Prof\.|Associate Professor|Assistant Professor)\s+of\s+[A-Za-z\s]+",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(Senior Fellow|Research Fellow|Fellow|Director|Senior Economist|Analyst)\s+at\s+[A-Za-z\s]+",
        re.IGNORECASE,
    ),
    re.compile(r"\b(Chair|Head|Dean)\s+of\s+[A-Za-z\s]+", re.IGNORECASE),
    re.compile(
        r"\b(Nobel Laureate|Economist|Sociologist|Political Scientist|Juris Doctor)\b",
        re.IGNORECASE,
    ),
]


def extract_qualifications(text: str) -> list[str]:
    """Extract academic credentials, degrees, and professional titles from text.

    Args:
        text: Text to search for qualifications.

    Returns:
        List of qualification strings.
    """
    if not text:
        return []

    quals: list[str] = []
    for pattern in _QUALIFICATION_PATTERNS:
        for match in pattern.finditer(text):
            val = match.group(0).strip().strip(",.;()")
            if val and val not in quals:
                quals.append(val)

    return quals


def calculate_credibility(
    parsed_cite: ParsedCitation, quals: list[str], text: str = ""
) -> tuple[int, float]:
    """Calculate credibility tier (1, 2, or 3) and overall quality score (0.0 to 1.0).

    Tier 1: Peer-reviewed journal / university press / DOI present / high quals.
    Tier 2: Government / think-tank / news report.
    Tier 3: Web article / blog / incomplete citation info.

    Returns:
        Tuple of (tier, quality_score).
    """
    score = 0.4  # Base score

    # Check DOI / URL
    if parsed_cite.doi:
        score += 0.2
    elif parsed_cite.url:
        score += 0.1

    # Check Authors
    if parsed_cite.authors:
        score += 0.15

    # Check Qualifications
    if quals:
        score += 0.15

    # Check Publication Container
    container_lower = parsed_cite.container_title.lower()
    is_academic = any(
        kw in container_lower
        for kw in [
            "journal",
            "press",
            "review",
            "quarterly",
            "university",
            "nature",
            "science",
            "ieee",
            "nber",
        ]
    )
    is_thinktank_or_gov = any(
        kw in container_lower
        for kw in [
            "brookings",
            "rand",
            "imf",
            "oecd",
            "world bank",
            "csis",
            "un",
            "report",
            "working paper",
        ]
    )

    if is_academic or parsed_cite.doi:
        score += 0.2
        tier = 1
    elif is_thinktank_or_gov or len(quals) > 0:
        score += 0.1
        tier = 2
    else:
        tier = 3 if score < 0.65 else 2

    # Check Recency
    if parsed_cite.year:
        try:
            yr = int(re.sub(r"\D", "", parsed_cite.year)[:4])
            if yr >= 2020:
                score += 0.1
            elif yr >= 2015:
                score += 0.05
        except ValueError:
            pass

    score = max(0.0, min(1.0, score))
    return tier, score


# ---------------------------------------------------------------------------
# Debate Specific Extractors (Tag, Warrants, Side, Keywords)
# ---------------------------------------------------------------------------

_WARRANT_SIGNALS = [
    "leads to",
    "causes",
    "results in",
    "proves that",
    "consequently",
    "therefore",
    "demonstrates",
    "increases",
    "decreases",
    "reduces",
    "prevents",
    "threatens",
    "is essential",
    "because",
    "requires",
]

_DEBATE_KEYWORDS = [
    "extinction",
    "gdp",
    "economy",
    "warming",
    "climate",
    "solvency",
    "hegemony",
    "security",
    "war",
    "escalation",
    "poverty",
    "rights",
    "proliferation",
    "biodiversity",
    "inflation",
    "sanctions",
    "trade",
    "sovereignty",
]


def extract_warrants(text: str, max_warrants: int = 3) -> list[str]:
    """Extract key argument warrants from card body text.

    Args:
        text: Card body text.
        max_warrants: Maximum number of warrants to extract.

    Returns:
        List of warrant bullet strings.
    """
    if not text:
        return []

    # Clean and split into sentences
    raw_sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 20]

    scored_sentences: list[tuple[float, str]] = []
    for sentence in sentences:
        s_lower = sentence.lower()
        score = 0.0

        # Score based on warrant signal phrases
        for signal in _WARRANT_SIGNALS:
            if signal in s_lower:
                score += 2.0

        # Score based on debate domain keywords
        for kw in _DEBATE_KEYWORDS:
            if kw in s_lower:
                score += 1.0

        # Prefer moderate sentence length (15 to 40 words)
        word_count = len(sentence.split())
        if 15 <= word_count <= 45:
            score += 1.0

        if score > 0:
            scored_sentences.append((score, sentence))

    scored_sentences.sort(key=lambda x: x[0], reverse=True)

    top_warrants = [s[1] for s in scored_sentences[:max_warrants]]
    if not top_warrants and sentences:
        top_warrants = sentences[:max_warrants]

    return top_warrants


def generate_debate_tag(text: str, title: str = "") -> str:
    """Generate a concise debate tagline (5 to 8 words).

    Args:
        text: Body text of the card.
        title: Title of article/citation if available.

    Returns:
        Formatted tagline string.
    """
    if title and 3 <= len(title.split()) <= 10:
        clean_title = re.sub(r"[^\w\s-]", "", title).strip()
        words = clean_title.split()
        return " ".join(words[:8]).capitalize()

    warrants = extract_warrants(text, max_warrants=1)
    if warrants:
        first_warrant = warrants[0]
        # Clean punctuation
        clean = re.sub(r"[^\w\s-]", "", first_warrant).strip()
        words = clean.split()
        if len(words) >= 5:
            return " ".join(words[:7]).capitalize()

    # Fallback to text start
    clean = re.sub(r"[^\w\s-]", "", text).strip()
    words = clean.split()
    if words:
        return " ".join(words[:6]).capitalize()
    return "Evidence Card Claim"


def detect_debate_side(text: str, title: str = "", default_side: str = "AFF") -> str:
    """Detect debate side preference ('AFF' or 'NEG') using heuristic keyword analysis.

    Args:
        text: Body text.
        title: Article title.
        default_side: Fallback side if ambiguous.

    Returns:
        'AFF' or 'NEG'.
    """
    combined = f"{title} {text}".lower()

    aff_signals = [
        "solves",
        "imperative",
        "beneficial",
        "effective",
        "significantly improves",
        "vital to",
        "supports",
        "promotes",
        "mitigates risk",
        "succeeds",
    ]
    neg_signals = [
        "disaster",
        "counterproductive",
        "fails",
        "backfires",
        "catastrophic",
        "exacerbates",
        "risks war",
        "unintended consequences",
        "harmful",
        "flawed",
    ]

    aff_score = sum(combined.count(sig) for sig in aff_signals)
    neg_score = sum(combined.count(sig) for sig in neg_signals)

    if aff_score > neg_score:
        return "AFF"
    elif neg_score > aff_score:
        return "NEG"
    return default_side.upper()


def extract_keywords(text: str, title: str = "") -> list[str]:
    """Extract domain keywords present in text."""
    combined = f"{title} {text}".lower()
    found: list[str] = []
    for kw in _DEBATE_KEYWORDS:
        if kw in combined and kw not in found:
            found.append(kw)
    return found


# ---------------------------------------------------------------------------
# Main Card Metadata Extraction Entry Point
# ---------------------------------------------------------------------------


def extract_card_metadata(
    raw_citation: str, card_text: str = "", default_side: str = "AFF"
) -> ResearchCardMetadata:
    """Extract full structured research card metadata from citation and text.

    Args:
        raw_citation: Raw citation string or BibTeX block.
        card_text: Card body text.
        default_side: Fallback side ('AFF' or 'NEG').

    Returns:
        ResearchCardMetadata dataclass object.
    """
    parsed_cite = parse_citation(raw_citation)

    # Extract author qualifications from citation and card text
    quals = extract_qualifications(f"{raw_citation} {card_text[:500]}")

    # Calculate credibility tier and quality score
    tier, quality_score = calculate_credibility(parsed_cite, quals, card_text)

    # Format debate citation header: e.g. "Smith '20" or "Smith 2020"
    last_name = parsed_cite.primary_author_last_name or "Anon"
    yr_short = parsed_cite.year[-2:] if len(parsed_cite.year) == 4 else parsed_cite.year
    cite_header = f"{last_name} '{yr_short}" if yr_short else last_name

    # Extract warrants and tagline
    warrants = extract_warrants(card_text)
    tag = generate_debate_tag(card_text, parsed_cite.title)

    # Detect side and keywords
    side = detect_debate_side(card_text, parsed_cite.title, default_side=default_side)
    keywords = extract_keywords(card_text, parsed_cite.title)

    primary_author = parsed_cite.authors[0] if parsed_cite.authors else last_name
    doi_or_url = parsed_cite.doi or parsed_cite.url

    summary = f"{cite_header}: {tag} (Tier {tier}, Score {quality_score:.2f})"

    return ResearchCardMetadata(
        citation_header=cite_header,
        full_citation=parsed_cite.raw_citation,
        tag=tag,
        warrants=warrants,
        side=side,
        author_qualifications=quals,
        primary_author=primary_author,
        author_last_name=last_name,
        year=parsed_cite.year,
        publication=parsed_cite.container_title,
        title=parsed_cite.title,
        doi_or_url=doi_or_url,
        credibility_tier=tier,
        quality_score=quality_score,
        keywords=keywords,
        summary=summary,
        raw_citation_data=parsed_cite.to_dict(),
    )
