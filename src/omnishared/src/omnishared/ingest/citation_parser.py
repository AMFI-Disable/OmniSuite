"""OmniShared Citation Parser Engine.

Provides advanced multi-format parsing for APA, MLA, Chicago, Harvard, and BibTeX citations.
Extracts structured components including authors, publication year, title, journal/container,
volume, issue, pages, DOI, URL, and entry type.

© 2026 OmniSuite. Built for the Digital Grandmaster.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class CitationFormat(str, Enum):
    APA = "APA"
    MLA = "MLA"
    CHICAGO = "CHICAGO"
    HARVARD = "HARVARD"
    BIBTEX = "BIBTEX"
    UNKNOWN = "UNKNOWN"


@dataclass
class ParsedCitation:
    format: CitationFormat
    raw_citation: str
    authors: list[str] = field(default_factory=list)
    primary_author_last_name: str = ""
    year: str = ""
    date: str = ""
    title: str = ""
    container_title: str = ""  # Journal, Book, or Website name
    volume: str = ""
    issue: str = ""
    pages: str = ""
    publisher: str = ""
    doi: str = ""
    url: str = ""
    entry_type: str = "article"  # article, book, webpage, techreport, etc.
    confidence: float = 0.0
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert the ParsedCitation dataclass to a clean dictionary."""
        return {
            "format": self.format.value
            if isinstance(self.format, CitationFormat)
            else str(self.format),
            "raw_citation": self.raw_citation,
            "authors": list(self.authors),
            "primary_author_last_name": self.primary_author_last_name,
            "year": self.year,
            "date": self.date,
            "title": self.title,
            "container_title": self.container_title,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "publisher": self.publisher,
            "doi": self.doi,
            "url": self.url,
            "entry_type": self.entry_type,
            "confidence": self.confidence,
            "extra": self.extra,
        }


# ---------------------------------------------------------------------------
# Regex Helpers & Extractors
# ---------------------------------------------------------------------------

_DOI_REGEX = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", re.IGNORECASE)
_URL_REGEX = re.compile(r"https?://[^\s>\"\']+", re.IGNORECASE)
_YEAR_REGEX = re.compile(r"\b(18|19|20|21)\d{2}[a-z]?\b")


def extract_doi(text: str) -> str:
    """Extract DOI string from text if present."""
    match = _DOI_REGEX.search(text)
    if match:
        doi = match.group(0).rstrip(".,;")
        return doi
    return ""


def extract_url(text: str) -> str:
    """Extract first HTTP/HTTPS URL from text."""
    match = _URL_REGEX.search(text)
    if match:
        url = match.group(0).rstrip(".,;")
        return url
    return ""


def extract_year(text: str) -> str:
    """Extract 4-digit publication year from text."""
    match = _YEAR_REGEX.search(text)
    return match.group(0) if match else ""


def parse_author_last_name(author_str: str) -> str:
    """Extract last name from an author name string."""
    if not author_str:
        return ""
    clean = author_str.strip()
    # Format: Last, First M.
    if "," in clean:
        return clean.split(",")[0].strip()
    # Format: First M. Last
    parts = clean.split()
    if parts:
        return parts[-1].strip()
    return clean


def normalize_authors(raw_authors: Any) -> list[str]:
    """Clean and normalize list of author strings."""
    if isinstance(raw_authors, str):
        # Split on ' and ', '&', or ';'
        chunks = re.split(r"\s+and\s+|\s*&\s*|\s*;\s*", raw_authors, flags=re.IGNORECASE)
        authors = [c.strip() for c in chunks if c.strip()]
    elif isinstance(raw_authors, list):
        authors = [str(a).strip() for a in raw_authors if str(a).strip()]
    else:
        authors = []
    return authors


# ---------------------------------------------------------------------------
# Format Detection Engine
# ---------------------------------------------------------------------------


def detect_citation_format(text: str) -> CitationFormat:
    """Detect the most likely citation format for a raw citation string.

    Args:
        text: Raw citation string.

    Returns:
        CitationFormat enum value.
    """
    clean = text.strip()
    if not clean:
        return CitationFormat.UNKNOWN

    # 1. BibTeX Check
    if clean.startswith("@") and "{" in clean:
        return CitationFormat.BIBTEX

    # 2. MLA Check: Quoted title + container/vol/no/pp or "and" between authors with quotes
    if (re.search(r'["“][^"”]+["”]', clean) or re.search(r"['‘][^'’]+['’]", clean)) and re.search(
        r"\b(vol\.|no\.|pp\.|p\.)\b", clean, re.IGNORECASE
    ):
        return CitationFormat.MLA

    # 3. APA Check: (YYYY) or (YYYY, Month DD) + Journal, vol(issue), pages
    if re.search(r"\((18|19|20|21)\d{2}[a-z]?\)", clean) and (
        "&" in clean or re.search(r"\d+\(\d+\)", clean) or "https://doi.org" in clean
    ):
        return CitationFormat.APA

    # 4. Chicago Check: Author. Year. "Title." or Journal Volume, no. Issue (Year): pages
    if re.search(r":\s*\d+(?:–|-)\d+", clean) and (
        re.search(r"\(\d{4}\)", clean) or re.search(r'["“].*?["”]', clean)
    ):
        return CitationFormat.CHICAGO

    # 5. Harvard Check: Authors, YYYY. Title. Journal, vol(issue), pp.XX-YY
    if re.search(r"\b(18|19|20|21)\d{2}\.\s+[A-Z]", clean) or (
        re.search(r",\s*(18|19|20|21)\d{2}\.", clean) and "pp." in clean
    ):
        return CitationFormat.HARVARD

    # Secondary heuristic matches
    if re.search(r'["“][^"”]{3,}["”]', clean):
        return CitationFormat.MLA
    if re.search(r"\((18|19|20|21)\d{2}\)", clean):
        return CitationFormat.APA

    return CitationFormat.UNKNOWN


# ---------------------------------------------------------------------------
# Individual Parsers
# ---------------------------------------------------------------------------


def _parse_bibtex(text: str) -> ParsedCitation:
    """Parse BibTeX format string."""
    doi = extract_doi(text)
    url = extract_url(text)

    # Match @entry_type{key, ...}
    match = re.match(r"@([A-Za-z0-9_]+)\s*[\{\(]\s*([^,\s]+)?\s*,?\s*(.*)", text, re.DOTALL)
    if not match:
        return ParsedCitation(
            format=CitationFormat.BIBTEX,
            raw_citation=text,
            doi=doi,
            url=url,
            confidence=0.5,
        )

    entry_type = match.group(1).lower()
    body = match.group(3)

    fields: dict[str, str] = {}
    # Parse key = {value} or key = "value" or key = value
    pattern = re.compile(
        r"([a-zA-Z0-9_-]+)\s*=\s*(?:\{((?:[^{}]|\{[^{}]*\})*)\}|\"([^\"]*)\"|([^\s,{}]+))"
    )
    for m in pattern.finditer(body):
        k = m.group(1).lower()
        val = (
            m.group(2)
            if m.group(2) is not None
            else (m.group(3) if m.group(3) is not None else m.group(4))
        )
        if val is not None:
            # Clean inner linebreaks and spaces
            val_clean = re.sub(r"\s+", " ", val.strip())
            fields[k] = val_clean

    raw_author = fields.get("author", fields.get("editor", ""))
    authors = normalize_authors(raw_author)
    primary_last = parse_author_last_name(authors[0]) if authors else ""

    year = fields.get("year", extract_year(text))
    title = fields.get("title", "").strip("{}")
    container = fields.get("journal", fields.get("booktitle", fields.get("publisher", ""))).strip(
        "{}"
    )
    volume = fields.get("volume", "")
    issue = fields.get("number", fields.get("issue", ""))
    pages = fields.get("pages", "").replace("--", "-")
    publisher = fields.get("publisher", fields.get("institution", fields.get("school", "")))
    cite_doi = fields.get("doi", doi)
    cite_url = fields.get("url", url)

    return ParsedCitation(
        format=CitationFormat.BIBTEX,
        raw_citation=text,
        authors=authors,
        primary_author_last_name=primary_last,
        year=year,
        title=title,
        container_title=container,
        volume=volume,
        issue=issue,
        pages=pages,
        publisher=publisher,
        doi=cite_doi,
        url=cite_url,
        entry_type=entry_type,
        confidence=0.95,
        extra=fields,
    )


def _parse_apa(text: str) -> ParsedCitation:
    """Parse APA format string.

    Format: Authors (Year). Title. Journal/Container, Volume(Issue), Pages. DOI/URL
    """
    doi = extract_doi(text)
    url = extract_url(text)
    year = ""
    authors: list[str] = []
    title = ""
    container = ""
    volume = ""
    issue = ""
    pages = ""

    # Match Year in Parentheses: (2020). or (2020, May 12).
    year_match = re.search(r"\(((?:18|19|20|21)\d{2}[a-z]?)(?:,\s*[^)]+)?\)", text)
    if year_match:
        year = year_match.group(1)
        author_part = text[: year_match.start()].strip().rstrip(".")
        authors = normalize_authors(author_part)
        remainder = text[year_match.end() :].strip().lstrip(". ")
    else:
        remainder = text

    # Extract title, container, volume, issue, pages from remainder
    # Look for Volume(Issue), Pages pattern: e.g. 15(2), 45-67 or 15(2), pp. 45-67
    vol_iss_match = re.search(
        r"(\d+)\s*\(([^)]+)\)\s*,\s*(?:pp?\.\s*)?(\d+(?:–|-)\d+|\d+)", remainder
    )
    if vol_iss_match:
        volume = vol_iss_match.group(1)
        issue = vol_iss_match.group(2)
        pages = vol_iss_match.group(3)
        before_vol = remainder[: vol_iss_match.start()].strip().rstrip(",")
    else:
        # Check for pages only
        page_match = re.search(r"(?:pp?\.\s*)?(\d+(?:–|-)\d+)", remainder)
        if page_match:
            pages = page_match.group(1)
            before_vol = remainder[: page_match.start()].strip().rstrip(",")
        else:
            before_vol = remainder

    # Split before_vol into Title and Container
    # Usually Title ends with a period
    title_parts = before_vol.split(".")
    if len(title_parts) >= 2:
        title = title_parts[0].strip()
        container = ".".join(title_parts[1:]).strip().rstrip(",")
    else:
        title = before_vol.strip()

    # Clean URL/DOI out of container/title
    if url and url in container:
        container = container.replace(url, "").strip().rstrip(".")
    if url and url in title:
        title = title.replace(url, "").strip().rstrip(".")

    primary_last = parse_author_last_name(authors[0]) if authors else ""

    return ParsedCitation(
        format=CitationFormat.APA,
        raw_citation=text,
        authors=authors,
        primary_author_last_name=primary_last,
        year=year,
        title=title,
        container_title=container,
        volume=volume,
        issue=issue,
        pages=pages,
        doi=doi,
        url=url,
        entry_type="article" if container else "book",
        confidence=0.85 if (year and authors) else 0.6,
    )


def _parse_mla(text: str) -> ParsedCitation:
    """Parse MLA format string.

    Format: Authors. "Title of Article." Container Title, vol. 15, no. 2, 2020, pp. 45-67.
    """
    doi = extract_doi(text)
    url = extract_url(text)
    year = extract_year(text)
    authors: list[str] = []
    title = ""
    container = ""
    volume = ""
    issue = ""
    pages = ""

    # Match Quoted Title: "Title." or “Title.”
    quote_match = re.search(r'["“]([^"”]+)["”]', text)
    if quote_match:
        title = quote_match.group(1).strip().rstrip(".")
        author_part = text[: quote_match.start()].strip().rstrip(".")
        authors = normalize_authors(author_part)
        remainder = text[quote_match.end() :].strip().lstrip(",. ")
    else:
        # Fallback split on period
        parts = text.split(".")
        if len(parts) >= 3:
            authors = normalize_authors(parts[0])
            title = parts[1].strip()
            remainder = ".".join(parts[2:])
        else:
            remainder = text

    # Extract vol., no., pp.
    vol_match = re.search(r"\bvol\.\s*(\d+)", remainder, re.IGNORECASE)
    if vol_match:
        volume = vol_match.group(1)
    no_match = re.search(r"\bno\.\s*(\d+)", remainder, re.IGNORECASE)
    if no_match:
        issue = no_match.group(1)
    pp_match = re.search(r"\bpp?\.\s*(\d+(?:–|-)\d+|\d+)", remainder, re.IGNORECASE)
    if pp_match:
        pages = pp_match.group(1)

    # Container title is text before vol./no./pp./year in remainder
    cut_idx = len(remainder)
    for m in [vol_match, no_match, pp_match]:
        if m and m.start() < cut_idx:
            cut_idx = m.start()
    container_part = remainder[:cut_idx].strip().rstrip(",")
    if container_part:
        container = container_part

    primary_last = parse_author_last_name(authors[0]) if authors else ""

    return ParsedCitation(
        format=CitationFormat.MLA,
        raw_citation=text,
        authors=authors,
        primary_author_last_name=primary_last,
        year=year,
        title=title,
        container_title=container,
        volume=volume,
        issue=issue,
        pages=pages,
        doi=doi,
        url=url,
        entry_type="article" if container else "misc",
        confidence=0.85 if title else 0.6,
    )


def _parse_chicago(text: str) -> ParsedCitation:
    """Parse Chicago format string.

    Format: Authors. Year. "Title." Journal Volume, no. Issue: pages.
    """
    doi = extract_doi(text)
    url = extract_url(text)
    year = extract_year(text)
    authors: list[str] = []
    title = ""
    container = ""
    volume = ""
    issue = ""
    pages = ""

    quote_match = re.search(r'["“]([^"”]+)["”]', text)
    if quote_match:
        title = quote_match.group(1).strip().rstrip(".")
        author_part = text[: quote_match.start()].strip().rstrip(".")
        # Clean year from author part if Chicago Author-Date style
        author_part = re.sub(r"\b(18|19|20|21)\d{2}[a-z]?\b", "", author_part).strip().rstrip(".")
        authors = normalize_authors(author_part)
        remainder = text[quote_match.end() :].strip().lstrip(",. ")
    else:
        remainder = text

    vol_iss_match = re.search(r"(\d+)\s*(?:,\s*no\.\s*(\d+)|\s*\(([^)]+)\))", remainder)
    if vol_iss_match:
        volume = vol_iss_match.group(1)
        issue = vol_iss_match.group(2) or vol_iss_match.group(3) or ""
        container = remainder[: vol_iss_match.start()].strip().rstrip(",")

    page_match = re.search(r":\s*(\d+(?:–|-)\d+|\d+)", remainder)
    if page_match:
        pages = page_match.group(1)

    primary_last = parse_author_last_name(authors[0]) if authors else ""

    return ParsedCitation(
        format=CitationFormat.CHICAGO,
        raw_citation=text,
        authors=authors,
        primary_author_last_name=primary_last,
        year=year,
        title=title,
        container_title=container,
        volume=volume,
        issue=issue,
        pages=pages,
        doi=doi,
        url=url,
        entry_type="article" if container else "book",
        confidence=0.8 if (authors or title) else 0.5,
    )


def _parse_harvard(text: str) -> ParsedCitation:
    """Parse Harvard format string.

    Format: Authors, YYYY. Title of article. Journal of Forensics, 15(2), pp.45-67.
    """
    doi = extract_doi(text)
    url = extract_url(text)
    year = extract_year(text)
    authors: list[str] = []
    title = ""
    container = ""
    volume = ""
    issue = ""
    pages = ""

    year_match = re.search(r",?\s*\b((?:18|19|20|21)\d{2}[a-z]?)\b\.", text)
    if year_match:
        year = year_match.group(1)
        author_part = text[: year_match.start()].strip()
        authors = normalize_authors(author_part)
        remainder = text[year_match.end() :].strip()
    else:
        remainder = text

    parts = remainder.split(".")
    if parts:
        title = parts[0].strip()
        if len(parts) > 1:
            container = parts[1].strip()

    vol_iss_match = re.search(r"(\d+)\s*\(([^)]+)\)", remainder)
    if vol_iss_match:
        volume = vol_iss_match.group(1)
        issue = vol_iss_match.group(2)

    pp_match = re.search(r"\bpp?\.\s*(\d+(?:–|-)\d+|\d+)", remainder, re.IGNORECASE)
    if pp_match:
        pages = pp_match.group(1)

    primary_last = parse_author_last_name(authors[0]) if authors else ""

    return ParsedCitation(
        format=CitationFormat.HARVARD,
        raw_citation=text,
        authors=authors,
        primary_author_last_name=primary_last,
        year=year,
        title=title,
        container_title=container,
        volume=volume,
        issue=issue,
        pages=pages,
        doi=doi,
        url=url,
        entry_type="article" if container else "misc",
        confidence=0.8 if year else 0.5,
    )


def _parse_fallback(text: str) -> ParsedCitation:
    """Generic fallback parser for unstructured citation text."""
    doi = extract_doi(text)
    url = extract_url(text)
    year = extract_year(text)

    # Heuristic author extraction from first segment
    parts = [p.strip() for p in text.split(".") if p.strip()]
    authors: list[str] = []
    title = ""
    container = ""

    if parts:
        # If first part looks like author name(s)
        if len(parts[0].split()) <= 6 and not parts[0].startswith("http"):
            authors = normalize_authors(parts[0])
        else:
            title = parts[0]

        if len(parts) > 1 and not title:
            title = parts[1]
        if len(parts) > 2:
            container = parts[2]

    primary_last = parse_author_last_name(authors[0]) if authors else ""

    return ParsedCitation(
        format=CitationFormat.UNKNOWN,
        raw_citation=text,
        authors=authors,
        primary_author_last_name=primary_last,
        year=year,
        title=title,
        container_title=container,
        doi=doi,
        url=url,
        entry_type="misc",
        confidence=0.4,
    )


# ---------------------------------------------------------------------------
# Public Entry Point
# ---------------------------------------------------------------------------


def parse_citation(raw_citation: str, fmt: Optional[CitationFormat] = None) -> ParsedCitation:
    """Parse a raw citation string into a structured ParsedCitation object.

    Args:
        raw_citation: Text of the citation.
        fmt: Optional explicit CitationFormat enum or string. If None, format is auto-detected.

    Returns:
        ParsedCitation object with populated fields.
    """
    if not raw_citation or not raw_citation.strip():
        return ParsedCitation(format=CitationFormat.UNKNOWN, raw_citation="", confidence=0.0)

    clean_text = raw_citation.strip()

    if fmt is None:
        target_fmt = detect_citation_format(clean_text)
    elif isinstance(fmt, str):
        try:
            target_fmt = CitationFormat(fmt.upper())
        except ValueError:
            target_fmt = CitationFormat.UNKNOWN
    else:
        target_fmt = fmt

    try:
        if target_fmt == CitationFormat.BIBTEX:
            return _parse_bibtex(clean_text)
        elif target_fmt == CitationFormat.APA:
            return _parse_apa(clean_text)
        elif target_fmt == CitationFormat.MLA:
            return _parse_mla(clean_text)
        elif target_fmt == CitationFormat.CHICAGO:
            return _parse_chicago(clean_text)
        elif target_fmt == CitationFormat.HARVARD:
            return _parse_harvard(clean_text)
        else:
            return _parse_fallback(clean_text)
    except Exception:
        # Resilient fallback if any regex or slicing fails
        return _parse_fallback(clean_text)
