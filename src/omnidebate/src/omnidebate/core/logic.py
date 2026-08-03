import difflib
import re

try:
    import requests
    from bs4 import BeautifulSoup

    WEB_INGEST_OK = True
except ImportError:
    WEB_INGEST_OK = False

try:
    from docx import Document

    DOCX_OK = True
except ImportError:
    DOCX_OK = False


def bool_search(cards: list, query: str) -> list:
    """Supports AND / OR / NOT boolean logic across tag + text."""
    query = query.strip()
    if not query:
        return cards

    def token_match(card: dict, token: str) -> bool:
        haystack = (
            card.get("tag", "") + " " + card.get("text", "") + " " + card.get("citation", "")
        ).lower()
        token = token.lower().strip()
        if not token:
            return True
        words = re.findall(r"\w+", haystack)
        if token in haystack:
            return True
        return bool(difflib.get_close_matches(token, words, n=1, cutoff=0.75))

    # Split on OR first (lowest precedence)
    or_parts = re.split(r"\bOR\b", query, flags=re.IGNORECASE)

    def match_or_clause(card: dict, clause: str) -> bool:
        # Split on AND
        and_parts = re.split(r"\bAND\b", clause, flags=re.IGNORECASE)
        for part in and_parts:
            part = part.strip()
            if part.upper().startswith("NOT "):
                token = part[4:].strip()
                if token_match(card, token):
                    return False
            else:
                if not token_match(card, part):
                    return False
        return True

    return [c for c in cards if any(match_or_clause(c, clause) for clause in or_parts)]


def smart_cite(author: str, year: str, title: str, source: str) -> str:
    """Generate a standardised citation string."""
    parts = []
    if author:
        parts.append(author.strip())
    if year:
        parts.append(f"({year.strip()})")
    if title:
        parts.append(f'"{title.strip()}"')
    if source:
        parts.append(f"— {source.strip()}")
    return ", ".join(parts) if parts else "Unknown Source"


def impact_tree(card: dict) -> str:
    """Generate a high-fidelity ASCII impact flow from card text."""
    text = card.get("text", "").lower()
    nodes = []

    # Intelligence: Causal Keyword Mapping
    if any(w in text for w in ["gdp", "economy", "trade", "market", "jobs", "cost", "billion"]):
        nodes.append("💰 Economic Resilience ==> GDP Growth ==> Market Stability")
    if any(
        w in text
        for w in [
            "health",
            "death",
            "disease",
            "poverty",
            "rights",
            "welfare",
            "mental",
        ]
    ):
        nodes.append("🧑 Human Capital --> Quality of Life (!) Terminal Impact")
    if any(
        w in text
        for w in [
            "war",
            "conflict",
            "nato",
            "nuclear",
            "security",
            "threat",
            "military",
        ]
    ):
        nodes.append("⚔️ Global Security ==> Deterrence (!) Existential Risk")
    if any(
        w in text
        for w in [
            "climate",
            "carbon",
            "environment",
            "ocean",
            "biodiversity",
            "emission",
        ]
    ):
        nodes.append("🌍 Climate Stability --> Resource Security --> Bio-Survival")
    if any(w in text for w in ["ai", "tech", "data", "compute", "semiconductor", "innovation"]):
        nodes.append("⚡ Tech Hegemony ==> Structural Advantage ==> Economic Power")

    if not nodes:
        nodes.append("❓ Unmapped Causal Chain — Tag more keywords")

    tag = card.get("tag", "Claim")
    lines = [f" {card['side']} ────────▶ {tag.upper()}"]
    for i, n in enumerate(nodes):
        prefix = " └─" if i == len(nodes) - 1 else " ├─"
        lines.append(f"{prefix} {n}")
    return "\n".join(lines)


def scrape_url(url: str) -> tuple[str, str]:
    """Returns (title, body_text). Raises on failure."""
    if not WEB_INGEST_OK:
        raise RuntimeError("requests and beautifulsoup4 are not installed.")
    resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.title.string.strip() if soup.title else url
    # Get meaningful paragraphs
    paras = [p.get_text(" ", strip=True) for p in soup.find_all("p") if len(p.get_text()) > 60]
    body = " ".join(paras[:8])  # First 8 paragraphs
    return title, body


def summarize_with_ollama(text: str, endpoint: str, model: str) -> tuple[str, str]:
    """AI Forensic Summarization using local Ollama. Returns (suggested_tag, summary)."""
    if not WEB_INGEST_OK:
        raise RuntimeError("Requests not available.")

    prompt = (
        "Analyze this debate evidence. Output ONLY in the following format:\n"
        "TAG: [A short 5-8 word summary of the main claim]\n"
        "BRIEF: [A concise bulleted summary of the Warrants and terminal Impacts]\n\n"
        f"TEXT: {text[:3000]}"
    )

    payload = {"model": model, "prompt": prompt, "stream": False}
    resp = requests.post(f"{endpoint}/api/generate", json=payload, timeout=25)
    resp.raise_for_status()
    raw_response = resp.json().get("response", "")

    # Simple semantic extraction
    tag = "AI Summarized"
    brief = raw_response

    if "TAG:" in raw_response:
        parts = raw_response.split("BRIEF:")
        tag = parts[0].replace("TAG:", "").strip()
        if len(parts) > 1:
            brief = parts[1].strip()

    return tag, brief


def weigh_evidence(card_a: dict, card_b: dict) -> dict:
    """Phase 101: AI-driven impact comparison logic."""
    a_score = card_a.get("tier", 1) * 10 + len(card_a.get("text", "")) / 100
    b_score = card_b.get("tier", 1) * 10 + len(card_b.get("text", "")) / 100
    return {
        "winner": "A" if a_score > b_score else "B",
        "score_diff": abs(a_score - b_score),
    }


def cross_link_motions(target_motion_id: int) -> list:
    """Phase 102: Find related cards across different motions."""
    return []


def parse_verbatim_docx(filepath: str) -> list[dict]:
    """Extracts debate cards from a Verbatim/CaseXC .docx file using style heuristics."""
    if not DOCX_OK:
        raise RuntimeError("python-docx is not installed.")

    doc = Document(filepath)
    cards = []
    current_card = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        style_name = para.style.name.lower()

        # Heuristics for Verbatim/CaseXC styles
        # Verbatim often uses styles like 'Tag', 'Cite', 'Card'
        is_tag = (
            "tag" in style_name
            or para.style.font.bold
            or (para.style.font.size and para.style.font.size.pt > 12)
        )

        # Robustness: Check if any run in paragraph is bold
        if not is_tag:
            for run in para.runs:
                if run.bold:
                    is_tag = True
                    break

        if is_tag:
            if current_card and current_card["text"]:
                cards.append(current_card)
            current_card = {
                "tag": text,
                "citation": "",
                "text": "",
                "side": "AFF",
                "tier": 1,
                "language": "EN",
                "timestamp": "",
            }
            continue

        if not current_card:
            continue

        # Detect Cite (usually the paragraph immediately following a tag)
        if not current_card["citation"]:
            current_card["citation"] = text
            continue

        # Append to Body
        current_card["text"] += text + "\n"

    if current_card and current_card["text"]:
        cards.append(current_card)

    return cards


def summarize_offline(text: str, title: str = "") -> tuple[str, str]:
    """Summarizes debate text offline using heuristics.
    Extracts a 5-8 word suggested tag and a bulleted summary of Warrants & Impacts.
    """
    # 1. Suggested Tag: 5-8 words from title or first sentence
    source_text = title if (title and len(title.split()) >= 3) else text
    sentences = re.split(r"(?<=[.!?])\s+", source_text)

    cand_words = []
    for s in sentences:
        clean_s = re.sub(r"[^\w\s-]", " ", s).strip()
        words = [w for w in clean_s.split() if w]
        if len(words) >= 5:
            cand_words = words
            break

    if not cand_words:
        clean_all = re.sub(r"[^\w\s-]", " ", source_text).strip()
        cand_words = [w for w in clean_all.split() if w]

    if len(cand_words) > 8:
        tag = " ".join(cand_words[:7])
    elif len(cand_words) < 5:
        if len(cand_words) >= 3:
            tag = " ".join(cand_words)
        else:
            tag = "Strategic debate evidence card analysis"
    else:
        tag = " ".join(cand_words)

    # Normalize tag capitalisation/spacing
    tag = tag.strip()

    # 2. Warrants & Impacts: Select top 3 sentences based on debate keywords
    all_sentences = re.split(r"(?<=[.!?])\s+", text)
    weighted_sentences = []

    keywords = [
        "leads to",
        "because",
        "causes",
        "gdp",
        "warming",
        "extinction",
        "results in",
        "therefore",
        "consequently",
        "proves",
        "shows",
        "climate",
        "conflict",
        "threat",
        "economic",
        "crisis",
    ]

    for s in all_sentences:
        s_clean = s.strip().replace("\n", " ")
        if len(s_clean) < 15:
            continue
        weight = 0
        s_lower = s_clean.lower()
        for kw in keywords:
            if kw in s_lower:
                weight += s_lower.count(kw) * 2

        # Length penalty to favor concise sentences
        if len(s_clean) > 180:
            weight -= 1

        weighted_sentences.append((weight, s_clean))

    weighted_sentences.sort(key=lambda x: x[0], reverse=True)
    top_sentences = [s for w, s in weighted_sentences[:3]]

    if not top_sentences:
        top_sentences = [s.strip() for s in all_sentences[:3] if len(s.strip()) > 10]

    brief_bullets = "\n".join(f"- {s}" for s in top_sentences)
    return tag, brief_bullets
