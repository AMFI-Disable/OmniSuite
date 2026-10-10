"""OmniDebate Import Engine — Multi-format data import and export.

Supports importing debate evidence cards from CSV, JSON, URLs, PDFs,
and the system clipboard. Exports to CSV and JSON backup formats.
All import functions return normalized card dicts with keys:
  tag, citation, text, side, language.

© 2026 OmniSuite. Built for the Digital Grandmaster.
"""

import csv
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

_VALID_SIDES = {"AFF", "NEG", "PRO", "CON"}


def _normalize_card(raw: dict) -> dict:
    """Normalize a raw card dict into the canonical schema.

    Args:
        raw: Dictionary with potential card fields in various casings.

    Returns:
        A dict with keys: tag, citation, text, side, language.
    """
    # Case-insensitive key lookup helper
    lower_map = {k.lower().strip(): v for k, v in raw.items()}

    tag = str(lower_map.get("tag", "Untitled")).strip()
    citation = str(lower_map.get("citation", lower_map.get("cite", ""))).strip()
    text = str(lower_map.get("text", lower_map.get("body", ""))).strip()

    side_raw = str(lower_map.get("side", "AFF")).strip().upper()
    if side_raw in ("PRO", "AFF"):
        side = "AFF"
    elif side_raw in ("CON", "NEG"):
        side = "NEG"
    elif side_raw in _VALID_SIDES:
        side = side_raw
    else:
        side = "AFF"

    language = str(lower_map.get("language", lower_map.get("lang", "en"))).strip()

    return {
        "tag": tag,
        "citation": citation,
        "text": text,
        "side": side,
        "language": language,
    }


# ---------------------------------------------------------------------------
# CSV import / export
# ---------------------------------------------------------------------------


def import_from_csv(filepath: str) -> list[dict]:
    """Import debate evidence cards from a CSV file.

    Expected columns (case-insensitive): tag, citation, text, side.
    Optional column: language (defaults to 'en').

    Args:
        filepath: Absolute or relative path to the CSV file.

    Returns:
        A list of normalized card dicts.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the CSV is empty or missing required columns.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"CSV file not found: {filepath}")

    cards: list[dict] = []
    with open(filepath, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file is empty or has no header: {filepath}")

        # Validate that at least 'tag' and 'text' columns exist
        lower_fields = {f.lower().strip() for f in reader.fieldnames}
        if "tag" not in lower_fields or "text" not in lower_fields:
            raise ValueError(
                f"CSV must contain at least 'tag' and 'text' columns. Found: {reader.fieldnames}"
            )

        for row in reader:
            if any(v and v.strip() for v in row.values()):
                cards.append(_normalize_card(row))

    return cards


def export_to_csv(cards: list[dict], filepath: str) -> str:
    """Export debate evidence cards to a CSV file.

    Args:
        cards: List of card dicts to export.
        filepath: Destination file path.

    Returns:
        The absolute path to the written CSV file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    fieldnames = ["tag", "citation", "text", "side", "language"]
    with open(filepath, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for card in cards:
            normalized = _normalize_card(card)
            writer.writerow(normalized)

    return os.path.abspath(filepath)


# ---------------------------------------------------------------------------
# JSON import / export
# ---------------------------------------------------------------------------


def import_from_json(filepath: str) -> list[dict]:
    """Import debate evidence cards from a JSON backup file.

    Accepts either a JSON array of card objects or a JSON object with
    a 'cards' key containing an array.

    Args:
        filepath: Path to the JSON file.

    Returns:
        A list of normalized card dicts.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the JSON structure is invalid.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"JSON file not found: {filepath}")

    with open(filepath, encoding="utf-8") as fh:
        data = json.load(fh)

    if isinstance(data, list):
        raw_cards = data
    elif isinstance(data, dict):
        raw_cards = data.get("cards", data.get("evidence", []))
        if not isinstance(raw_cards, list):
            raise ValueError(
                f"JSON object must contain a 'cards' array. Got type: {type(raw_cards).__name__}"
            )
    else:
        raise ValueError(f"Expected JSON array or object, got {type(data).__name__}")

    return [_normalize_card(card) for card in raw_cards if isinstance(card, dict)]


def export_to_json(cards: list[dict], filepath: str) -> str:
    """Export a full vault backup to a JSON file.

    Writes a JSON object with metadata and a 'cards' array.

    Args:
        cards: List of card dicts to export.
        filepath: Destination file path.

    Returns:
        The absolute path to the written JSON file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    payload: dict[str, Any] = {
        "omnisuite_version": "V1.0.0",
        "export_type": "vault_backup",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "card_count": len(cards),
        "cards": [_normalize_card(c) for c in cards],
    }

    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)

    return os.path.abspath(filepath)


# ---------------------------------------------------------------------------
# URL import (web scraping)
# ---------------------------------------------------------------------------


def import_from_url(url: str) -> dict:
    """Fetch a URL and extract article text as a debate evidence card.

    Uses requests + BeautifulSoup to scrape article content, then
    auto-generates a tag line and citation from the page metadata.

    Args:
        url: The web URL to fetch.

    Returns:
        A single normalized card dict with extracted content.

    Raises:
        ConnectionError: If the URL cannot be fetched.
        ValueError: If no usable text is extracted.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise ImportError(
            "URL import requires 'requests' and 'beautifulsoup4' packages. "
            "Install them with: pip install requests beautifulsoup4"
        ) from exc

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36 OmniSuite/1.0"
            )
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ConnectionError(f"Failed to fetch URL '{url}': {exc}") from exc

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract title for tag
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else "Imported Article"

    # Extract author / publication for citation
    author_meta = soup.find("meta", attrs={"name": "author"}) or soup.find(
        "meta", attrs={"property": "article:author"}
    )
    author = author_meta.get("content", "").strip() if author_meta else ""

    date_meta = soup.find("meta", attrs={"property": "article:published_time"}) or soup.find(
        "meta", attrs={"name": "date"}
    )
    pub_date = date_meta.get("content", "")[:10] if date_meta else ""

    citation_parts = [p for p in [author, pub_date, url] if p]
    citation = " — ".join(citation_parts) if citation_parts else url

    # Extract article body text
    # Try common article containers first
    article_el = (
        soup.find("article")
        or soup.find("div", class_="article-body")
        or soup.find("div", class_="entry-content")
        or soup.find("main")
    )

    paragraphs = article_el.find_all("p") if article_el else soup.find_all("p")

    body_parts = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if len(text) > 30:  # Skip trivially short paragraphs
            body_parts.append(text)

    body_text = "\n\n".join(body_parts)

    if not body_text.strip():
        raise ValueError(f"No usable article text extracted from: {url}")

    # Truncate the tag to a reasonable length
    tag = title[:120] if len(title) > 120 else title

    return _normalize_card(
        {
            "tag": tag,
            "citation": citation,
            "text": body_text,
            "side": "AFF",
            "language": "en",
        }
    )


# ---------------------------------------------------------------------------
# PDF import
# ---------------------------------------------------------------------------


def import_from_pdf(filepath: str) -> list[str]:
    """Extract text pages from a PDF file.

    Tries to use the system 'pdftotext' utility (from poppler-utils)
    for high-quality extraction. Falls back to a basic binary read
    heuristic if pdftotext is not available.

    Args:
        filepath: Path to the PDF file.

    Returns:
        A list of strings, one per extracted page (or a single-element
        list for the fallback extractor).

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        RuntimeError: If text extraction fails completely.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"PDF file not found: {filepath}")

    # Attempt 1: pdftotext (poppler-utils)
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", filepath, "-"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Split on form-feed characters (page breaks)
            raw_pages = result.stdout.split("\f")
            pages = [p.strip() for p in raw_pages if p.strip()]
            if pages:
                return pages
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass  # pdftotext not installed or timed out — fall through

    # Attempt 2: Basic binary heuristic extraction
    try:
        with open(filepath, "rb") as fh:
            raw_bytes = fh.read()

        # Decode as latin-1 to avoid codec errors on binary data
        raw_text = raw_bytes.decode("latin-1", errors="replace")

        # Extract text between BT (begin text) and ET (end text) PDF operators
        import re

        text_blocks = re.findall(r"\(([^)]+)\)", raw_text)
        extracted = " ".join(
            block for block in text_blocks if len(block) > 3 and any(c.isalpha() for c in block)
        )

        if extracted.strip():
            return [extracted.strip()]

    except Exception as exc:
        raise RuntimeError(f"Failed to extract text from PDF '{filepath}': {exc}") from exc

    raise RuntimeError(
        f"No text could be extracted from PDF: {filepath}. "
        "Ensure the PDF contains selectable text (not scanned images). "
        "For best results, install pdftotext: brew install poppler"
    )


# ---------------------------------------------------------------------------
# Clipboard import
# ---------------------------------------------------------------------------


def import_from_clipboard() -> str:
    """Read text content from the system clipboard.

    Uses pbpaste on macOS and xclip on Linux.

    Returns:
        The clipboard text content.

    Raises:
        RuntimeError: If clipboard access fails or clipboard is empty.
    """
    system = platform.system()

    if system == "Darwin":
        cmd = ["pbpaste"]
    elif system == "Linux":
        cmd = ["xclip", "-selection", "clipboard", "-o"]
    else:
        raise RuntimeError(
            f"Clipboard import is not supported on {system}. "
            "Supported platforms: macOS (pbpaste), Linux (xclip)."
        )

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            stderr_msg = result.stderr.strip()
            raise RuntimeError(
                f"Clipboard command failed (exit {result.returncode}): "
                f"{stderr_msg or 'unknown error'}"
            )

        content = result.stdout
        if not content or not content.strip():
            raise RuntimeError("Clipboard is empty.")

        return content

    except FileNotFoundError:
        tool = "pbpaste" if system == "Darwin" else "xclip"
        raise RuntimeError(
            f"Clipboard tool '{tool}' not found. "
            f"{'It should be pre-installed on macOS.' if system == 'Darwin' else 'Install with: sudo apt install xclip'}"
        ) from None
    except subprocess.TimeoutExpired:
        raise RuntimeError("Clipboard access timed out.") from None
