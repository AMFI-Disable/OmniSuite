"""OmniDebate AI Tools — LLM-powered debate assistance functions.

Provides AI-driven utilities for competitive debate preparation including
card summarization, counter-argument generation, impact chain analysis,
case strength scoring, evidence gap detection, case outlining,
cross-examination question generation, and clarity rewriting.

All functions gracefully handle OllamaOfflineError, returning a
descriptive error string instead of raising.

© 2026 OmniSuite. Built for the Digital Grandmaster.
"""

from omnishared.ai.client import OllamaOfflineError, generate_completion

# ---------------------------------------------------------------------------
# System context shared across all AI tool prompts
# ---------------------------------------------------------------------------

SYSTEM_CONTEXT = (
    "You are a world-class competitive debate coach and forensic analysis "
    "expert. You have deep knowledge of Public Forum, Lincoln-Douglas, Policy, "
    "British Parliamentary, World Schools, and all major debate formats. "
    "You understand argumentation theory: uniqueness, links, internal links, "
    "impacts, turns, solvency, topicality, and kritiks. You speak precisely "
    "and concisely. When analyzing evidence cards, focus on strategic value, "
    "warrant quality, and rhetorical effectiveness. Always structure your "
    "responses with clear headings and bullet points for readability."
)


def summarize_card(card_text: str) -> str:
    """Generate a concise one-line tag summary for a debate evidence card.

    Args:
        card_text: The full body text of the evidence card.

    Returns:
        A one-line tag summary string, or an error message if the LLM
        is unavailable.
    """
    prompt = (
        "Summarize the following debate evidence card in a single concise "
        "tagline (one sentence, under 15 words) that captures the core "
        "claim. Return ONLY the tagline, nothing else.\n\n"
        f"CARD TEXT:\n{card_text}"
    )
    try:
        return generate_completion(prompt, system_prompt=SYSTEM_CONTEXT)
    except OllamaOfflineError:
        return "[AI Offline] Unable to generate summary — Ollama is not running."


def generate_counter_arguments(card_text: str, side: str = "con") -> str:
    """Generate strategic counter-arguments against a debate evidence card.

    Args:
        card_text: The full body text of the evidence card to refute.
        side: The side generating counters — 'con'/'neg' attacks the card,
              'pro'/'aff' defends against anticipated attacks.

    Returns:
        Formatted counter-arguments string, or an error message if the
        LLM is unavailable.
    """
    side_label = "NEGATIVE/CON" if side.lower() in ("con", "neg") else "AFFIRMATIVE/PRO"
    prompt = (
        f"You are preparing {side_label} responses against the following "
        "debate evidence card. Generate 3–5 strategic counter-arguments.\n"
        "For each counter-argument, provide:\n"
        "1. A short label (e.g., 'Turn', 'Non-Unique', 'No Link')\n"
        "2. The argument itself (2–3 sentences)\n"
        "3. A suggested source area to find supporting evidence\n\n"
        f"CARD TEXT:\n{card_text}"
    )
    try:
        return generate_completion(prompt, system_prompt=SYSTEM_CONTEXT, timeout=20.0)
    except OllamaOfflineError:
        return "[AI Offline] Unable to generate counter-arguments — Ollama is not running."


def analyze_impact_chain(card_text: str) -> str:
    """Identify and map the impact chain within a debate evidence card.

    Analyzes the card for the four components of a complete impact chain:
    uniqueness, link, internal link, and terminal impact.

    Args:
        card_text: The full body text of the evidence card.

    Returns:
        A structured impact chain analysis string, or an error message
        if the LLM is unavailable.
    """
    prompt = (
        "Analyze the following debate evidence card and identify its "
        "impact chain. Break it down into these four components:\n\n"
        "1. **UNIQUENESS** — What is the current status quo that makes "
        "the argument relevant now?\n"
        "2. **LINK** — What is the causal mechanism connecting the "
        "action/policy to the consequence?\n"
        "3. **INTERNAL LINK** — What intermediate steps connect the "
        "initial link to the terminal impact?\n"
        "4. **IMPACT** — What is the terminal impact (magnitude, "
        "probability, timeframe)?\n\n"
        "If any component is missing or weak, note it explicitly. "
        "Rate the overall chain strength on a scale of 1–10.\n\n"
        f"CARD TEXT:\n{card_text}"
    )
    try:
        return generate_completion(prompt, system_prompt=SYSTEM_CONTEXT, timeout=20.0)
    except OllamaOfflineError:
        return "[AI Offline] Unable to analyze impact chain — Ollama is not running."


def score_case_strength(cards: list[dict]) -> str:
    """Rate the overall strength of a debate case across multiple cards.

    Evaluates evidence quality, argument coverage, impact diversity,
    and strategic coherence.

    Args:
        cards: List of card dicts, each containing at minimum 'tag',
               'text', and 'side' keys.

    Returns:
        A detailed case strength report string with a numerical score,
        or an error message if the LLM is unavailable.
    """
    if not cards:
        return "No cards provided. Add evidence cards to score case strength."

    # Build a compact representation to stay within token limits
    card_summaries = []
    for i, card in enumerate(cards[:20], 1):  # Cap at 20 cards for prompt size
        tag = card.get("tag", "Untitled")
        side = card.get("side", "?")
        text_preview = card.get("text", "")[:200]
        card_summaries.append(f"  {i}. [{side}] {tag}: {text_preview}...")

    cards_block = "\n".join(card_summaries)
    total = len(cards)
    aff_count = sum(1 for c in cards if c.get("side", "").upper() == "AFF")
    neg_count = sum(1 for c in cards if c.get("side", "").upper() == "NEG")

    prompt = (
        f"Evaluate the overall debate case strength given {total} evidence "
        f"cards ({aff_count} AFF, {neg_count} NEG). Score each dimension "
        "on a scale of 1–10:\n\n"
        "1. **Evidence Quality** — Are sources credible and recent?\n"
        "2. **Argument Coverage** — Are major arguments covered?\n"
        "3. **Impact Diversity** — Are impacts varied (economic, security, "
        "humanitarian)?\n"
        "4. **Strategic Coherence** — Do cards build a unified narrative?\n"
        "5. **Rebuttal Readiness** — Are there cards anticipating opposition?\n\n"
        "Provide an overall score (1–100) and a 2–3 sentence strategic "
        "recommendation.\n\n"
        f"CARDS:\n{cards_block}"
    )
    try:
        return generate_completion(prompt, system_prompt=SYSTEM_CONTEXT, timeout=25.0)
    except OllamaOfflineError:
        return "[AI Offline] Unable to score case strength — Ollama is not running."


def find_evidence_gaps(cards: list[dict], motion: str) -> str:
    """Identify missing evidence areas in a debate case.

    Analyzes the current card library against the motion to find
    strategic gaps that need additional research.

    Args:
        cards: List of card dicts with 'tag', 'text', and 'side' keys.
        motion: The debate motion/resolution text.

    Returns:
        A structured evidence gaps report, or an error message if
        the LLM is unavailable.
    """
    if not cards:
        return (
            "No cards in vault. Start by adding evidence cards for both "
            "AFF and NEG sides of the motion."
        )

    card_tags = []
    for card in cards[:30]:  # Cap for prompt size
        tag = card.get("tag", "Untitled")
        side = card.get("side", "?")
        card_tags.append(f"  - [{side}] {tag}")

    tags_block = "\n".join(card_tags)

    prompt = (
        "Given the debate motion and the current evidence library, identify "
        "3–5 critical evidence gaps that need additional research.\n\n"
        "For each gap, provide:\n"
        "1. **Gap Area** — What argument or evidence is missing\n"
        "2. **Why It Matters** — Strategic importance of filling this gap\n"
        "3. **Search Suggestions** — Keywords or source types to find "
        "relevant evidence\n"
        "4. **Priority** — High / Medium / Low\n\n"
        f"MOTION: {motion}\n\n"
        f"EXISTING CARDS:\n{tags_block}"
    )
    try:
        return generate_completion(prompt, system_prompt=SYSTEM_CONTEXT, timeout=25.0)
    except OllamaOfflineError:
        return "[AI Offline] Unable to find evidence gaps — Ollama is not running."


def generate_case_outline(motion: str, side: str, format_name: str = "Public Forum") -> str:
    """Generate a draft case outline for a given motion, side, and format.

    Produces a structured speech outline with suggested contentions,
    evidence needs, and strategic notes.

    Args:
        motion: The debate motion/resolution text.
        side: 'AFF'/'PRO' or 'NEG'/'CON'.
        format_name: Debate format name (e.g., 'Public Forum',
                     'Lincoln-Douglas', 'Policy', 'British Parliamentary').

    Returns:
        A formatted case outline string, or an error message if the
        LLM is unavailable.
    """
    side_label = side.upper()
    side_label = "AFFIRMATIVE/PRO" if side_label in ("PRO", "AFF") else "NEGATIVE/CON"

    prompt = (
        f"Generate a complete {side_label} case outline for the following "
        f"motion in {format_name} debate format.\n\n"
        "Structure the outline as:\n"
        "1. **Framework / Value Criterion** (if applicable to format)\n"
        "2. **Contention 1** — Title, claim, warrant sketch, impact\n"
        "3. **Contention 2** — Title, claim, warrant sketch, impact\n"
        "4. **Contention 3** (optional) — Title, claim, warrant sketch, "
        "impact\n"
        "5. **Anticipated Responses** — Key opponent arguments to prepare "
        "against\n"
        "6. **Evidence Needs** — Specific types of evidence to research\n\n"
        "Tailor speech times and strategy to the specified format.\n\n"
        f"MOTION: {motion}"
    )
    try:
        return generate_completion(prompt, system_prompt=SYSTEM_CONTEXT, timeout=30.0)
    except OllamaOfflineError:
        return "[AI Offline] Unable to generate case outline — Ollama is not running."


def generate_cross_questions(card_text: str) -> str:
    """Generate crossfire / cross-examination questions targeting a card.

    Produces strategic questions designed to expose weaknesses,
    force concessions, or set up future arguments.

    Args:
        card_text: The full body text of the evidence card to question.

    Returns:
        A numbered list of cross-examination questions, or an error
        message if the LLM is unavailable.
    """
    prompt = (
        "Generate 5–7 strategic cross-examination questions targeting the "
        "following debate evidence card. Each question should:\n"
        "- Be concise and answerable (not compound)\n"
        "- Have a clear strategic purpose (labeled in parentheses: "
        "'expose link gap', 'force concession', 'set up turn', "
        "'challenge source credibility', 'test uniqueness')\n"
        "- Be ordered from safest to most aggressive\n\n"
        "Format as a numbered list with the strategic purpose in "
        "parentheses after each question.\n\n"
        f"CARD TEXT:\n{card_text}"
    )
    try:
        return generate_completion(prompt, system_prompt=SYSTEM_CONTEXT, timeout=20.0)
    except OllamaOfflineError:
        return (
            "[AI Offline] Unable to generate cross-examination questions — Ollama is not running."
        )


def rewrite_for_clarity(card_text: str) -> str:
    """Rewrite evidence card text for maximum clarity and persuasiveness.

    Improves sentence structure, emphasizes key warrants, and ensures
    the argument flows logically while preserving factual content.

    Args:
        card_text: The original evidence card body text.

    Returns:
        The rewritten card text, or an error message if the LLM
        is unavailable.
    """
    prompt = (
        "Rewrite the following debate evidence card text to maximize "
        "clarity and persuasiveness. Follow these rules:\n\n"
        "1. Preserve ALL factual claims, statistics, and source "
        "attributions exactly\n"
        "2. Improve sentence structure for spoken delivery\n"
        "3. Emphasize the strongest warrants using clear causal language\n"
        "4. Ensure logical flow: claim → warrant → impact\n"
        "5. Remove filler words and redundancy\n"
        "6. Keep the same approximate length\n\n"
        "Return ONLY the rewritten text, no commentary.\n\n"
        f"ORIGINAL TEXT:\n{card_text}"
    )
    try:
        return generate_completion(prompt, system_prompt=SYSTEM_CONTEXT, timeout=20.0)
    except OllamaOfflineError:
        return "[AI Offline] Unable to rewrite card text — Ollama is not running."
