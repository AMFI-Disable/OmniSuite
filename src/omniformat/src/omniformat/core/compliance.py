"""OmniFormat Core Markdown Compliance & Lint Engine.

Evaluates Markdown files for structure, readability, link integrity, and formatting style rules
aligned with standard markdownlint conventions (MD001, MD002, MD004, MD009, MD010, MD011, MD012,
MD018, MD034, MD040, MD041, MD047). Provides automated fixing utilities.
© 2026 OmniSuite. Built for the Digital Grandmaster.
"""

import re

# Supported tags for HTML balancing rule MD033
SUPPORTED_HTML_TAGS = {"u", "b", "i", "strong", "em", "code", "kbd", "sub", "sup"}


def count_syllables(text: str) -> int:
    """Helper to estimate syllable counts for readability scoring."""
    words = re.findall(r"\b[a-zA-Z]+\b", text)
    syllables = 0
    for w in words:
        w = w.lower()
        if not w:
            continue
        # Simple vowel-group based count
        count = len(re.findall(r"[aeiouy]+", w))
        if w.endswith("e"):
            count = max(1, count - 1)
        syllables += max(1, count)
    return syllables


def calculate_readability(text: str) -> int:
    """Calculate Flesch Reading Ease score (0-100)."""
    words = re.findall(r"\b\w+\b", text)
    sentences = re.split(r"[.!?]+", text)
    sentences = [s for s in sentences if s.strip()]

    num_words = len(words)
    num_sentences = len(sentences)
    if num_words == 0 or num_sentences == 0:
        return 100

    num_syllables = count_syllables(text)

    # Flesch Reading Ease Formula
    fre = 206.835 - 1.015 * (num_words / num_sentences) - 84.6 * (num_syllables / num_words)
    return max(0, min(100, int(round(fre))))


def check_html_tags(text: str) -> list[str]:
    """Verify inline HTML elements are balanced correctly."""
    tokens = re.split(r"(</?[a-zA-Z0-9]+>)", text)
    stack = []
    warnings = []

    for token in tokens:
        if not token:
            continue
        if token.startswith("<") and token.endswith(">"):
            is_closing = token.startswith("</")
            tag_name = token[2:-1].lower() if is_closing else token[1:-1].lower()
            if tag_name not in SUPPORTED_HTML_TAGS:
                continue

            if is_closing:
                if not stack:
                    warnings.append(f"MD033: Mismatched closing HTML tag </{tag_name}>")
                elif stack[-1] != tag_name:
                    if tag_name in stack:
                        idx = len(stack) - 1 - stack[::-1].index(tag_name)
                        for t in stack[idx + 1 :]:
                            warnings.append(f"MD033: Unclosed HTML tag <{t}>")
                        stack = stack[:idx]
                    else:
                        warnings.append(f"MD033: Mismatched closing HTML tag </{tag_name}>")
                else:
                    stack.pop()
            else:
                stack.append(tag_name)

    for t in stack:
        warnings.append(f"MD033: Unclosed HTML tag <{t}>")

    return warnings


def analyze_markdown(text: str) -> dict:
    """Scans raw markdown text and returns scores (0-100) and list of lint warnings."""
    warnings = []

    # 1. READABILITY SCORE
    readability_score = calculate_readability(text)
    if readability_score < 30:
        warnings.append(
            f"Readability warning: Flesch Reading Ease score ({readability_score}) is < 30 (extremely difficult/unreadable)"
        )
    elif readability_score > 80:
        warnings.append(
            f"Readability warning: Flesch Reading Ease score ({readability_score}) is > 80 (very easy)"
        )

    # 2. HEADING STRUCTURE SCORE
    heading_score = 100
    headings = []
    lines = text.splitlines()

    for line_idx, line in enumerate(lines, 1):
        if line.startswith("#"):
            match = re.match(r"^(#+)(.*)$", line)
            if match:
                hashes, content = match.groups()
                level = len(hashes)
                headings.append((level, content, line_idx))

                # MD018: No space after hash
                if content and not content.startswith(" "):
                    heading_score = max(0, heading_score - 10)
                    warnings.append(f"MD018 (Line {line_idx}): Space missing after header hashes")

    if headings:
        # MD002 / MD041: First heading in file should be a top-level heading (H1)
        if headings[0][0] != 1:
            heading_score = max(0, heading_score - 20)
            warnings.append(
                f"MD002 (Line {headings[0][2]}): First heading must be a top-level heading (#)"
            )

        # MD001: Heading levels should only increment by one level at a time
        prev_level = None
        for level, content, line_idx in headings:
            if prev_level is not None:
                if level - prev_level > 1:
                    heading_score = max(0, heading_score - 25)
                    warnings.append(
                        f"MD001 (Line {line_idx}): non-sequential heading level transition (H{prev_level} to H{level})"
                    )
            prev_level = level

    # 3. STYLE CONSISTENCY SCORE
    style_score = 100
    has_star_list = False
    has_dash_list = False
    has_tabs = False
    has_trailing = False
    consecutive_blank = 0
    max_consecutive_blank = 0
    missing_code_lang = False

    for line_idx, line in enumerate(lines, 1):
        # MD010: Hard tabs
        if "\t" in line:
            has_tabs = True

        # MD009: Trailing spaces
        if re.search(r"[ \t]+$", line):
            # Exclude markdown trailing double-space linebreaks
            if not line.endswith("  "):
                has_trailing = True

        # MD004: Unordered list styles
        if re.match(r"^\s*\*\s+", line):
            has_star_list = True
        elif re.match(r"^\s*\-\s+", line):
            has_dash_list = True

        # MD012: Multiple consecutive blank lines
        if not line.strip():
            consecutive_blank += 1
            if consecutive_blank > max_consecutive_blank:
                max_consecutive_blank = consecutive_blank
        else:
            consecutive_blank = 0

        # MD040: Code block language specification
        if line.startswith("```") and not line.endswith("```") and len(line.strip()) == 3:
            missing_code_lang = True

    if has_tabs:
        style_score = max(0, style_score - 15)
        warnings.append("MD010: Hard tabs detected in document")
    if has_trailing:
        style_score = max(0, style_score - 15)
        warnings.append("MD009: Trailing spaces found at ends of lines")
    if has_star_list and has_dash_list:
        style_score = max(0, style_score - 20)
        warnings.append("MD004: Mixed unordered list symbols (both * and - used)")
    if max_consecutive_blank > 1:
        style_score = max(0, style_score - 15)
        warnings.append("MD012: Multiple consecutive blank lines found")
    if missing_code_lang:
        style_score = max(0, style_score - 20)
        warnings.append("MD040: Fenced code blocks must specify a syntax language")

    # MD047: File should end with a single newline
    if text and not text.endswith("\n"):
        style_score = max(0, style_score - 10)
        warnings.append("MD047: File should end with a single newline character")

    # Mismatched/unclosed markdown bold/italic styles (MD037 / MD038)
    clean_text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    clean_text = re.sub(r"`[^`\n]+`", "", clean_text)

    # Check bold **
    if clean_text.count("**") % 2 != 0:
        style_score = max(0, style_score - 15)
        warnings.append("MD037: Mismatched or unclosed markdown bold style '**'")

    # Check bold __
    if clean_text.count("__") % 2 != 0:
        style_score = max(0, style_score - 15)
        warnings.append("MD037: Mismatched or unclosed markdown bold style '__'")

    # Check italic *
    temp = clean_text.replace("**", "")
    temp = re.sub(r"^\s*\*\s+", "", temp)
    temp = re.sub(r"\n\s*\*\s+", "\n", temp)
    if temp.count("*") % 2 != 0:
        style_score = max(0, style_score - 10)
        warnings.append("MD038: Mismatched or unclosed markdown italic style '*'")

    # Check italic _
    temp = clean_text.replace("__", "")
    flanked_underscores = len(re.findall(r"\w_\w", temp))
    total_underscores = temp.count("_")
    formatting_underscores = total_underscores - flanked_underscores * 2
    if formatting_underscores % 2 != 0:
        style_score = max(0, style_score - 10)
        warnings.append("MD038: Mismatched or unclosed markdown italic style '_'")

    # 4. LINK HEALTH SCORE
    link_score = 100

    # MD011: Reversed link syntax (text)[url]
    reversed_links = re.findall(r"\([^)]+\)\[[^\]]+\]", text)
    if reversed_links:
        link_score = max(0, link_score - len(reversed_links) * 25)
        for link in reversed_links:
            warnings.append(f"MD011: Reversed link syntax found: {link}")

    # MD034: Bare URLs used
    bare_urls = re.findall(r"(?<![\[<(])https?://[^\s>\]]+", text)
    if bare_urls:
        link_score = max(0, link_score - len(bare_urls) * 15)
        for url in bare_urls:
            warnings.append(f"MD034: Bare URL found: {url}")

    # Inline HTML tag check (MD033)
    html_warnings = check_html_tags(text)
    if html_warnings:
        style_score = max(0, style_score - len(html_warnings) * 15)
        warnings.extend(html_warnings)

    return {
        "readability_score": readability_score,
        "heading_score": heading_score,
        "style_score": style_score,
        "link_score": link_score,
        "warnings": warnings,
    }


def normalize_heading_levels(text: str) -> str:
    """Ensures heading levels do not skip levels."""
    lines = text.splitlines()
    fixed_lines = []
    prev_level = 0
    for line in lines:
        if line.startswith("#"):
            match = re.match(r"^(#+)(.*)$", line)
            if match:
                hashes, content = match.groups()
                level = len(hashes)
                if prev_level > 0 and level - prev_level > 1:
                    level = prev_level + 1
                    hashes = "#" * level
                prev_level = level
                fixed_lines.append(hashes + content)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    return "\n".join(fixed_lines)


def fix_mismatched_markdown_styles(text: str) -> str:
    """Balances odd numbers of bold or italic markers per paragraph."""
    paragraphs = text.split("\n\n")
    fixed_paragraphs = []

    for para in paragraphs:
        clean_para = re.sub(r"```.*?```", "", para, flags=re.DOTALL)
        clean_para = re.sub(r"`[^`\n]+`", "", clean_para)

        # Check bold **
        double_star_count = clean_para.count("**")
        if double_star_count % 2 != 0:
            para = para.rstrip() + "**"
            clean_para = clean_para.rstrip() + "**"

        # Check bold __
        double_under_count = clean_para.count("__")
        if double_under_count % 2 != 0:
            para = para.rstrip() + "__"
            clean_para = clean_para.rstrip() + "__"

        # Check italic *
        temp = clean_para.replace("**", "")
        temp = re.sub(r"^\s*\*\s+", "", temp)
        temp = re.sub(r"\n\s*\*\s+", "\n", temp)
        single_star_count = temp.count("*")
        if single_star_count % 2 != 0:
            para = para.rstrip() + "*"
            clean_para = clean_para.rstrip() + "*"

        # Check italic _
        temp = clean_para.replace("__", "")
        flanked_underscores = len(re.findall(r"\w_\w", temp))
        total_underscores = temp.count("_")
        formatting_underscores = total_underscores - flanked_underscores * 2
        if formatting_underscores % 2 != 0:
            para = para.rstrip() + "_"

        fixed_paragraphs.append(para)

    return "\n\n".join(fixed_paragraphs)


def auto_correct_markdown(text: str) -> str:
    """Auto-fixes formatting errors in raw markdown content."""
    if not text:
        return ""

    # Normalize headings first so they don't skip levels
    text = normalize_heading_levels(text)

    # Balance unclosed markdown styles paragraph by paragraph
    text = fix_mismatched_markdown_styles(text)

    lines = text.splitlines()
    fixed_lines = []

    for line in lines:
        # MD010: Hard tabs to 4 spaces
        line = line.replace("\t", "    ")

        # MD009: Strip trailing spaces (unless double space for markdown linebreak)
        if line.endswith("  ") and not line.endswith("   "):
            line = line[:-2].rstrip() + "  "
        else:
            line = line.rstrip()

        # MD018: Add space after header hash (e.g. ##Heading -> ## Heading)
        line = re.sub(r"^(#+)([^#\s])", r"\1 \2", line)

        # MD004: Standardize unordered list bullet style to '-'
        line = re.sub(r"^(\s*)\*\s+", r"\1- ", line)

        fixed_lines.append(line)

    # MD012: Collapse consecutive blank lines to at most one blank line
    fixed_content = "\n".join(fixed_lines)
    fixed_content = re.sub(r"\n\n\n+", "\n\n", fixed_content)

    # MD011: Fix reversed links (text)[url] -> [text](url)
    fixed_content = re.sub(r"\(([^)]+)\)\[([^\]]+)\]", r"[\1](\2)", fixed_content)

    # MD033: Balance HTML tags (by closing any unclosed tags at end of file)
    fixed_content = balance_html_strings(fixed_content)

    # MD047: Ensure file ends with a single newline
    if not fixed_content.endswith("\n"):
        fixed_content += "\n"

    return fixed_content


def balance_html_strings(text: str) -> str:
    """Helper to auto-close any unclosed HTML tags from the stack."""
    tokens = re.split(r"(</?[a-zA-Z0-9]+>)", text)
    stack = []
    result = []

    for token in tokens:
        if not token:
            continue
        if token.startswith("<") and token.endswith(">"):
            is_closing = token.startswith("</")
            tag_name = token[2:-1].lower() if is_closing else token[1:-1].lower()

            if tag_name not in SUPPORTED_HTML_TAGS:
                result.append(token)
                continue

            if is_closing:
                if tag_name in stack:
                    while stack:
                        top = stack.pop()
                        result.append(f"</{top}>")
                        if top == tag_name:
                            break
                else:
                    # Strip unmatched closing tag
                    pass
            else:
                stack.append(tag_name)
                result.append(f"<{tag_name}>")
        else:
            result.append(token)

    while stack:
        top = stack.pop()
        result.append(f"</{top}>")

    return "".join(result)


def detect_and_parse_forensics(text: str) -> dict:
    """Detects if a markdown text is an OmniDebate strategic brief and extracts metadata."""
    is_brief = False
    if (
        "# 🏛️ STRATEGIC BRIEF:" in text
        or "Generated by OmniDebate" in text
        or "<!-- OMNIDEBATE" in text
        or "<!-- OMNISUITE-DEBATE" in text
    ):
        is_brief = True

    if not is_brief:
        return {"is_brief": False}

    aff_count = len(re.findall(r"\[AFF\]", text, re.IGNORECASE))
    neg_count = len(re.findall(r"\[NEG\]", text, re.IGNORECASE))
    total_cards = aff_count + neg_count

    t3_count = 0
    lines = text.splitlines()
    for line in lines:
        stars_count = line.count("⭐") + line.count("★")
        if ("[AFF]" in line.upper() or "[NEG]" in line.upper()) and stars_count >= 3:
            t3_count += 1

    return {
        "is_brief": True,
        "total_cards": total_cards,
        "aff_count": aff_count,
        "neg_count": neg_count,
        "t3_count": t3_count,
    }
