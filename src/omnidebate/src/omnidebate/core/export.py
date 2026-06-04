"""OmniDebate Core Export and Brief Compilation Engine.

Generates beautiful briefs in Verbatim (.docx), CaseXC (.docx), Standard Brief (.md),
and Interactive Brief (.html) formats.
© 2026 OmniSuite. Built for the Digital Grandmaster.
"""

import os
import re
import datetime
import html
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from omnishared.config import EXPORTS_DIR
from omnidebate.core.database import read_vault
from omnidebate.core.logic import impact_tree


def parse_text_runs(text: str) -> list[dict]:
    """Parse text with HTML and Markdown formatting tags into styled runs."""
    # Normalize markdown bold, underline, italic to html tags
    normalized = text
    normalized = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", normalized)
    normalized = re.sub(r"__(.*?)__", r"<u>\1</u>", normalized)
    normalized = re.sub(r"\*(.*?)\*", r"<i>\1</i>", normalized)
    normalized = re.sub(r"_(.*?)_", r"<u>\1</u>", normalized)

    # Split by tags
    tokens = re.split(r"(</?[ubistrongem]+>)", normalized)

    runs = []
    curr_bold = False
    curr_underline = False
    curr_italic = False

    for token in tokens:
        if not token:
            continue
        lower_token = token.lower()
        if lower_token in ("<b>", "<strong>"):
            curr_bold = True
        elif lower_token in ("</b>", "</strong>"):
            curr_bold = False
        elif lower_token in ("<u>", "<ins>"):
            curr_underline = True
        elif lower_token in ("</u>", "</ins>"):
            curr_underline = False
        elif lower_token in ("<i>", "<em>"):
            curr_italic = True
        elif lower_token in ("</i>", "</em>"):
            curr_italic = False
        else:
            runs.append(
                {
                    "text": token,
                    "bold": curr_bold,
                    "underline": curr_underline,
                    "italic": curr_italic,
                }
            )
    return runs


def parse_citation(citation: str, minimize: bool) -> tuple[str, str]:
    """Split citation into a main bolded reference (e.g. Author & Year) and details."""
    if not citation:
        return "Unknown Source", ""

    # Heuristically split citation by first hyphen, comma, or colon
    # e.g., "Smith 2026 - PhD, Harvard" -> ("Smith 2026", "PhD, Harvard")
    parts = re.split(r"[\-\:]", citation, maxsplit=1)
    if len(parts) == 2:
        cite_bold = parts[0].strip()
        cite_details = parts[1].strip()
    else:
        # Try splitting by comma
        parts_comma = citation.split(",", 1)
        if len(parts_comma) == 2:
            cite_bold = parts_comma[0].strip()
            cite_details = parts_comma[1].strip()
        else:
            cite_bold = citation.strip()
            cite_details = ""

    if minimize:
        return cite_bold, ""
    return cite_bold, cite_details


def format_html_text(text: str) -> str:
    """Format evidence card text with CSS styles, bolding, underline, and shrunked runs."""
    runs = parse_text_runs(text)
    html_runs = []
    for r in runs:
        t_escaped = html.escape(r["text"])
        if r["bold"] or r["underline"] or r["italic"]:
            wrapped = t_escaped
            if r["bold"]:
                wrapped = f"<b>{wrapped}</b>"
            if r["underline"]:
                wrapped = f"<u>{wrapped}</u>"
            if r["italic"]:
                wrapped = f"<i>{wrapped}</i>"
            html_runs.append(wrapped)
        else:
            html_runs.append(f'<span class="shrunked">{t_escaped}</span>')
    return "".join(html_runs)


def generate_svg_flowchart(card: dict) -> str:
    """Generate visual horizontal flowchart representing the card's causal impact chains."""
    text = card.get("text", "").lower()
    chains = []

    # Check keyword mapping
    if any(
        w in text
        for w in ["gdp", "economy", "trade", "market", "jobs", "cost", "billion"]
    ):
        chains.append(
            {
                "nodes": ["Economic Resilience", "GDP Growth", "Market Stability"],
                "color": "#10b981",  # Emerald green
                "icon": "💰",
            }
        )
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
        chains.append(
            {
                "nodes": ["Human Capital", "Quality of Life", "Terminal Impact"],
                "color": "#f59e0b",  # Amber
                "icon": "🧑",
            }
        )
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
        chains.append(
            {
                "nodes": ["Global Security", "Deterrence", "Existential Risk"],
                "color": "#ef4444",  # Red
                "icon": "⚔️",
            }
        )
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
        chains.append(
            {
                "nodes": ["Climate Stability", "Resource Security", "Bio-Survival"],
                "color": "#06b6d4",  # Teal/Cyan
                "icon": "🌍",
            }
        )
    if any(
        w in text
        for w in ["ai", "tech", "data", "compute", "semiconductor", "innovation"]
    ):
        chains.append(
            {
                "nodes": ["Tech Hegemony", "Structural Advantage", "Economic Power"],
                "color": "#3b82f6",  # Blue
                "icon": "⚡",
            }
        )

    if not chains:
        chains.append(
            {
                "nodes": ["Unmapped Chain", "Tag more keywords", "Terminal Impact"],
                "color": "#64748b",  # Grey
                "icon": "❓",
            }
        )

    # Build the SVG
    box_w = 160
    box_h = 42
    gap_x = 45
    gap_y = 25

    padding_x = 10
    padding_y = 10

    num_rows = len(chains)
    svg_w = padding_x * 2 + 3 * box_w + 2 * gap_x
    svg_h = padding_y * 2 + num_rows * box_h + (num_rows - 1) * gap_y

    svg_parts = [
        f'<svg viewBox="0 0 {svg_w} {svg_h}" width="100%" height="{svg_h}" xmlns="http://www.w3.org/2000/svg" style="background: rgba(15, 23, 42, 0.4); border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05); font-family: system-ui, -apple-system, sans-serif;">'
    ]

    svg_parts.append("""
    <defs>
      <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#10b981" />
      </marker>
      <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#ef4444" />
      </marker>
      <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#3b82f6" />
      </marker>
      <marker id="arrow-teal" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#06b6d4" />
      </marker>
      <marker id="arrow-amber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#f59e0b" />
      </marker>
      <marker id="arrow-grey" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#64748b" />
      </marker>
    </defs>
    """)

    color_to_marker = {
        "#10b981": "arrow-green",
        "#ef4444": "arrow-red",
        "#3b82f6": "arrow-blue",
        "#06b6d4": "arrow-teal",
        "#f59e0b": "arrow-amber",
        "#64748b": "arrow-grey",
    }

    for row_idx, chain in enumerate(chains):
        color = chain["color"]
        marker_id = color_to_marker.get(color, "arrow-grey")
        icon = chain["icon"]

        y = padding_y + row_idx * (box_h + gap_y)

        for col_idx, node_text in enumerate(chain["nodes"]):
            x = padding_x + col_idx * (box_w + gap_x)
            display_text = f"{icon} {node_text}" if col_idx == 0 else node_text

            svg_parts.append(f"""
            <rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="6" ry="6" fill="rgba(30, 41, 59, 0.7)" stroke="{color}" stroke-width="1.5" />
            <text x="{x + box_w / 2}" y="{y + box_h / 2 + 4}" fill="#f1f5f9" font-size="10" font-weight="500" text-anchor="middle">{display_text}</text>
            """)

            if col_idx < 2:
                arrow_start_x = x + box_w
                arrow_start_y = y + box_h / 2
                arrow_end_x = arrow_start_x + gap_x
                arrow_end_y = arrow_start_y

                svg_parts.append(f"""
                <line x1="{arrow_start_x}" y1="{arrow_start_y}" x2="{arrow_end_x - 6}" y2="{arrow_end_y}" stroke="{color}" stroke-width="1.5" marker-end="url(#{marker_id})" />
                """)

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


def export_brief(
    motion_id: int,
    motion_name: str,
    template: str,
    underline_taglines: bool = True,
    minimize_citations: bool = False,
) -> str:
    """Compiles evidence cards for a motion into a formatted strategic document brief."""
    cards = read_vault(motion_id)
    today = datetime.date.today().strftime("%Y-%m-%d")
    safe_name = motion_name.lower().replace(" ", "_")

    os.makedirs(EXPORTS_DIR, exist_ok=True)

    if template == "interactive_html":
        fname = os.path.join(EXPORTS_DIR, f"brief_{safe_name}_{today}.html")
        aff_cards = [c for c in cards if c["side"] == "AFF"]
        neg_cards = [c for c in cards if c["side"] == "NEG"]
        aff_count = len(aff_cards)
        neg_count = len(neg_cards)
        total_count = len(cards)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Brief: {motion_name}</title>
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: rgba(30, 41, 59, 0.4);
            --border-color: rgba(255, 255, 255, 0.05);
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-blue: #3b82f6;
            --accent-emerald: #10b981;
            --accent-red: #ef4444;
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            min-height: 100vh;
        }}

        #sidebar {{
            width: 280px;
            background: rgba(15, 23, 42, 0.6);
            border-right: 1px solid var(--border-color);
            padding: 2rem 1.5rem;
            position: fixed;
            height: 100vh;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            backdrop-filter: blur(12px);
            z-index: 100;
        }}

        #sidebar h1 {{
            font-size: 1.2rem;
            font-weight: 700;
            margin: 0;
            color: var(--text-primary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 2px solid var(--accent-blue);
            padding-bottom: 0.5rem;
        }}

        .meta-info {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}

        .meta-item {{
            display: flex;
            justify-content: space-between;
        }}

        .meta-label {{
            color: var(--text-muted);
        }}

        #toc-nav {{
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            margin-top: 1rem;
        }}

        .nav-link {{
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.95rem;
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            transition: all 0.2s ease;
            border-left: 2px solid transparent;
        }}

        .nav-link:hover {{
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.03);
            border-left-color: var(--accent-blue);
        }}

        #search-container {{
            margin-top: auto;
        }}

        #search-input {{
            width: 100%;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 0.75rem;
            color: var(--text-primary);
            font-family: inherit;
            box-sizing: border-box;
            outline: none;
            transition: border-color 0.2s;
        }}

        #search-input:focus {{
            border-color: var(--accent-blue);
        }}

        #main-content {{
            margin-left: 280px;
            flex: 1;
            padding: 2.5rem 3rem;
            max-width: 900px;
        }}

        .section-title {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-top: 2.5rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.75rem;
        }}

        .section-title.aff {{
            color: var(--accent-emerald);
        }}

        .section-title.neg {{
            color: var(--accent-red);
        }}

        .card {{
            margin-bottom: 1.25rem;
        }}

        details {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
            backdrop-filter: blur(8px);
            transition: border-color 0.2s, background-color 0.2s;
        }}

        details[open] {{
            border-color: rgba(59, 130, 246, 0.25);
            background: rgba(30, 41, 59, 0.55);
        }}

        summary {{
            padding: 1.25rem;
            cursor: pointer;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
            list-style: none;
            outline: none;
        }}

        summary::-webkit-details-marker {{
            display: none;
        }}

        .summary-left {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .side-badge {{
            font-size: 0.75rem;
            font-weight: 800;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            text-transform: uppercase;
        }}

        .side-badge.aff {{
            background: rgba(16, 185, 129, 0.1);
            color: var(--accent-emerald);
        }}

        .side-badge.neg {{
            background: rgba(239, 68, 68, 0.1);
            color: var(--accent-red);
        }}

        .tier-stars {{
            color: #fbbf24;
            letter-spacing: 0.1em;
        }}

        .tagline {{
            color: var(--text-primary);
            font-size: 1.05rem;
        }}

        .cite-preview {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 500;
        }}

        .card-body {{
            padding: 0 1.25rem 1.25rem 1.25rem;
            border-top: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }}

        .cite-full {{
            font-size: 0.95rem;
            color: var(--text-secondary);
            border-left: 3px solid var(--accent-blue);
            padding-left: 0.75rem;
            margin: 0;
            margin-top: 1.25rem;
        }}

        .card-text {{
            line-height: 1.6;
            font-size: 1rem;
            color: var(--text-primary);
        }}

        .card-text u {{
            color: var(--text-primary);
            text-decoration: underline;
            text-decoration-thickness: 1.5px;
        }}
        .card-text b {{
            color: var(--text-primary);
            font-weight: 700;
        }}
        .card-text span.shrunked {{
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        .flowchart-container {{
            margin-top: 1rem;
        }}

        .flowchart-title {{
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        @media print {{
            body {{
                background: #ffffff !important;
                color: #000000 !important;
            }}
            #sidebar, #search-container {{
                display: none !important;
            }}
            #main-content {{
                margin-left: 0 !important;
                padding: 0 !important;
                max-width: 100% !important;
            }}
            .section-title {{
                color: #000000 !important;
                border-bottom: 2px solid #000000 !important;
                page-break-after: avoid !important;
                break-after: avoid !important;
            }}
            .card {{
                page-break-inside: avoid !important;
                break-inside: avoid !important;
                margin-bottom: 2rem !important;
                border: 1px solid #cbd5e1 !important;
                border-radius: 6px !important;
            }}
            details {{
                display: block !important;
                height: auto !important;
                border: 1px solid #cbd5e1 !important;
                background: none !important;
            }}
            details:not([open]) > *:not(summary) {{
                display: block !important;
            }}
            summary {{
                pointer-events: none !important;
                border-bottom: 1px solid #cbd5e1 !important;
                background: #f8fafc !important;
                color: #000000 !important;
                padding: 1rem !important;
            }}
            .card-body {{
                display: flex !important;
                flex-direction: column !important;
                gap: 1rem !important;
                padding: 1rem !important;
                background: none !important;
            }}
            .shrunked {{
                color: #64748b !important;
                font-size: 0.9rem !important;
            }}
            svg {{
                background: #ffffff !important;
                border: 1px solid #cbd5e1 !important;
            }}
            rect {{
                fill: #f8fafc !important;
                stroke: #475569 !important;
            }}
            text {{
                fill: #000000 !important;
            }}
            line {{
                stroke: #475569 !important;
            }}
        }}
    </style>
</head>
<body>
    <div id="sidebar">
        <h1>OmniDebate Brief</h1>
        <div class="meta-info">
            <div class="meta-item">
                <span class="meta-label">Brief:</span>
                <span>{motion_name}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Compiled:</span>
                <span>{today}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Total Cards:</span>
                <span>{total_count}</span>
            </div>
        </div>
        
        <div id="toc-nav">
            <a href="#aff-section" class="nav-link">🟢 AFFIRMATIVE ({aff_count})</a>
            <a href="#neg-section" class="nav-link">🔴 NEGATIVE ({neg_count})</a>
        </div>
        
        <div id="search-container">
            <input type="text" id="search-input" placeholder="🔍 Search cards..." />
        </div>
    </div>
    
    <div id="main-content">
        <h2>🏛️ STRATEGIC BRIEF: {motion_name.upper()}</h2>
        
        <div id="aff-section">
            <div class="section-title aff">🟢 AFFIRMATIVE CASE (PRO)</div>
"""

        def render_card_list(card_list):
            cards_html = []
            for c in card_list:
                tag = c["tag"].upper()
                if underline_taglines:
                    tag = f"<u>{tag}</u>"

                cite_bold, cite_details = parse_citation(
                    c.get("citation", ""), minimize_citations
                )
                cite_str = cite_bold
                if cite_details:
                    cite_str += f" ({cite_details})"

                body_formatted = format_html_text(c["text"])
                svg_flow = generate_svg_flowchart(c)
                stars = "★" * c.get("tier", 1)

                escaped_tag = html.escape(c.get("tag", ""))
                escaped_cite = html.escape(c.get("citation", ""))
                escaped_text = html.escape(c.get("text", ""))

                cards_html.append(f"""
            <div class="card" data-tagline="{escaped_tag}" data-citation="{escaped_cite}" data-text="{escaped_text}">
                <details>
                    <summary>
                        <div class="summary-left">
                            <span class="side-badge {c["side"].lower()}">{c["side"]}</span>
                            <span class="tier-stars">{stars}</span>
                            <span class="tagline">{tag}</span>
                        </div>
                        <span class="cite-preview">{cite_bold}</span>
                    </summary>
                    <div class="card-body">
                        <p class="cite-full"><strong>SOURCE CITE:</strong> {cite_str}</p>
                        <div class="card-text">
                            {body_formatted}
                        </div>
                        <div class="flowchart-container">
                            <div class="flowchart-title">Causal Impact Tree</div>
                            {svg_flow}
                        </div>
                    </div>
                </details>
            </div>
            """)
            return "\n".join(cards_html)

        if not aff_cards:
            html_content += "<p><em>No Affirmative cards.</em></p>"
        else:
            html_content += render_card_list(aff_cards)

        html_content += """
        </div>
        
        <div id="neg-section">
            <div class="section-title neg">🔴 NEGATIVE CASE (CON)</div>
"""

        if not neg_cards:
            html_content += "<p><em>No Negative cards.</em></p>"
        else:
            html_content += render_card_list(neg_cards)

        html_content += """
        </div>
    </div>
    
    <script>
        document.addEventListener("DOMContentLoaded", () => {
            const searchInput = document.getElementById("search-input");
            const cards = document.querySelectorAll(".card");
            
            searchInput.addEventListener("input", (e) => {
                const query = e.target.value.toLowerCase().trim();
                
                cards.forEach(card => {
                    const tagline = card.getAttribute("data-tagline").toLowerCase();
                    const citation = card.getAttribute("data-citation").toLowerCase();
                    const text = card.getAttribute("data-text").toLowerCase();
                    
                    if (tagline.includes(query) || citation.includes(query) || text.includes(query)) {
                        card.style.display = "";
                    } else {
                        card.style.display = "none";
                    }
                });
            });
        });
    </script>
</body>
</html>
"""
        with open(fname, "w", encoding="utf-8") as out:
            out.write(html_content)
        return fname

    elif template == "markdown":
        fname = os.path.join(EXPORTS_DIR, f"brief_{safe_name}_{today}.md")
        with open(fname, "w") as out:
            out.write(f"# 🏛️ STRATEGIC BRIEF: {motion_name.upper()}\n")
            out.write(f"> **Format:** Standard Markdown Brief | **Date:** {today}\n\n")

            aff_cards = [c for c in cards if c["side"] == "AFF"]
            neg_cards = [c for c in cards if c["side"] == "NEG"]
            out.write("## 🧠 STRATEGIC SYNTHESIS\n")
            out.write(
                f"- **Evidence Density:** {len(cards)} total cards ({len(aff_cards)} AFF / {len(neg_cards)} NEG)\n"
            )
            tier3 = [c for c in cards if c.get("tier") == 3]
            out.write(
                f"- **Power Index:** {len(tier3)} Tier-3 Cards ready for Impact Calculus.\n\n"
            )

            out.write("---\n\n## ⚖️ EVIDENCE REPOSITORY\n\n")

            for section_label, section_cards in [
                ("AFFIRMATIVE (PRO)", aff_cards),
                ("NEGATIVE (CON)", neg_cards),
            ]:
                out.write(f"### {section_label}\n\n")
                if not section_cards:
                    out.write("*No cards in this section.*\n\n")
                    continue
                for c in sorted(section_cards, key=lambda x: -x.get("tier", 1)):
                    stars = "⭐" * c.get("tier", 1)
                    tag = c["tag"].upper()
                    if underline_taglines:
                        tag = f"<u>{tag}</u>"

                    cite_bold, cite_details = parse_citation(
                        c.get("citation", ""), minimize_citations
                    )
                    cite_str = f"**{cite_bold}**"
                    if cite_details:
                        cite_str += f" ({cite_details})"

                    out.write(f"#### {stars} [{c['side']}] {tag}\n")
                    out.write(f"**CITE:** {cite_str}  \n\n")

                    text = c["text"]
                    text = re.sub(r"<u>(.*?)</u>", r"<u>\1</u>", text)
                    text = re.sub(r"<b>(.*?)</b>", r"**\1**", text)
                    out.write(f"{text}\n\n")

                    out.write("**IMPACT ANALYSIS:**\n")
                    out.write(f"```\n{impact_tree(c)}\n```\n\n")

            out.write(
                "\n---\n*End of Strategic Brief — Generated by OmniDebate Workstation.*"
            )
        return fname

    else:
        # DOCX formats
        doc = Document()
        for s in doc.sections:
            s.top_margin = Inches(0.75)
            s.bottom_margin = Inches(0.75)
            s.left_margin = Inches(0.75)
            s.right_margin = Inches(0.75)

        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title_p.add_run(f"🏛️ STRATEGIC BRIEF: {motion_name.upper()}")
        title_run.bold = True

        if template == "verbatim":
            title_run.font.name = "Calibri"
            title_run.font.size = Pt(18)
            title_run.font.color.rgb = RGBColor(30, 30, 30)
        else:  # casexc
            title_run.font.name = "Trebuchet MS"
            title_run.font.size = Pt(18)
            title_run.font.color.rgb = RGBColor(0, 95, 115)  # Teal

        meta_p = doc.add_paragraph()
        meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        meta_run = meta_p.add_run(
            f"Format: {template.upper()} | Date: {today} | Generated by OmniDebate"
        )
        meta_run.italic = True
        meta_run.font.size = Pt(10)
        meta_run.font.color.rgb = RGBColor(120, 120, 120)

        div_p = doc.add_paragraph()
        div_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        div_p.add_run(
            "____________________________________________________"
        ).font.color.rgb = RGBColor(200, 200, 200)

        synth_p = doc.add_paragraph()
        synth_run = synth_p.add_run("🧠 STRATEGIC SYNTHESIS\n")
        synth_run.bold = True
        synth_run.font.size = Pt(12)

        aff_cards = [c for c in cards if c["side"] == "AFF"]
        neg_cards = [c for c in cards if c["side"] == "NEG"]

        doc.add_paragraph(
            f"• Evidence Density: {len(cards)} total cards ({len(aff_cards)} AFF / {len(neg_cards)} NEG)\n"
            f"• Power Index: {len([c for c in cards if c.get('tier') == 3])} Tier-3 Cards ready for Impact Calculus.\n"
            f"• Document compiled automatically under the Digital Grandmaster guidelines."
        )

        for side_label, side_cards in [
            ("AFFIRMATIVE CASE (PRO)", aff_cards),
            ("NEGATIVE CASE (CON)", neg_cards),
        ]:
            heading_p = doc.add_paragraph()
            heading_run = heading_p.add_run(f"\n⚖️ {side_label}\n")
            heading_run.bold = True
            heading_run.font.size = Pt(14)
            if template == "casexc":
                heading_run.font.name = "Trebuchet MS"
                heading_run.font.color.rgb = RGBColor(10, 147, 150)
            else:
                heading_run.font.name = "Calibri"
                heading_run.font.color.rgb = RGBColor(0, 0, 0)

            if not side_cards:
                doc.add_paragraph("No evidence cards in this section.")
                continue

            for c in sorted(side_cards, key=lambda x: -x.get("tier", 1)):
                tag_p = doc.add_paragraph()
                stars = "★" * c.get("tier", 1)
                tag_text = f"{stars} [{c['side']}] {c['tag'].upper()}"
                tag_run = tag_p.add_run(tag_text)
                tag_run.bold = True
                tag_run.underline = underline_taglines

                cite_p = doc.add_paragraph()
                cite_bold, cite_details = parse_citation(
                    c.get("citation", ""), minimize_citations
                )

                c_bold_run = cite_p.add_run(cite_bold)
                c_bold_run.bold = True

                if cite_details:
                    cite_p.add_run(f" ({cite_details})")

                body_p = doc.add_paragraph()
                runs_data = parse_text_runs(c["text"])

                if template == "verbatim":
                    tag_run.font.name = "Calibri"
                    tag_run.font.size = Pt(12)
                    tag_run.font.color.rgb = RGBColor(0, 0, 0)

                    c_bold_run.font.name = "Calibri"
                    c_bold_run.font.size = Pt(10.5)
                    for r in cite_p.runs:
                        r.font.name = "Calibri"
                        r.font.size = Pt(10)

                    for rd in runs_data:
                        r = body_p.add_run(rd["text"])
                        r.font.name = "Calibri"
                        r.italic = rd["italic"]

                        if rd["bold"] or rd["underline"]:
                            r.bold = rd["bold"]
                            r.underline = rd["underline"]
                            r.font.size = Pt(11.5)
                            r.font.color.rgb = RGBColor(0, 0, 0)
                        else:
                            r.font.size = Pt(8.5)
                            r.font.color.rgb = RGBColor(128, 128, 128)

                else:  # casexc
                    tag_run.font.name = "Consolas"
                    tag_run.font.size = Pt(11.5)
                    tag_run.font.color.rgb = RGBColor(0, 95, 115)

                    c_bold_run.font.name = "Trebuchet MS"
                    c_bold_run.font.size = Pt(10)
                    for r in cite_p.runs:
                        r.font.name = "Trebuchet MS"
                        r.font.size = Pt(9.5)
                        r.font.color.rgb = RGBColor(80, 80, 80)

                    for rd in runs_data:
                        r = body_p.add_run(rd["text"])
                        r.font.name = "Georgia"
                        r.bold = rd["bold"]
                        r.underline = rd["underline"]
                        r.italic = rd["italic"]
                        r.font.size = Pt(10.5)
                        r.font.color.rgb = RGBColor(30, 30, 30)

                imp_p = doc.add_paragraph()
                imp_run_hdr = imp_p.add_run("   [ IMPACT DYNAMICS: ")
                imp_run_hdr.font.size = Pt(8.5)
                imp_run_hdr.font.color.rgb = RGBColor(120, 120, 120)
                imp_run_hdr.italic = True

                imp_tree_str = impact_tree(c).replace("\n", " | ").strip()
                imp_run_body = imp_p.add_run(imp_tree_str)
                imp_run_body.font.size = Pt(8.5)
                imp_run_body.font.color.rgb = RGBColor(100, 100, 100)
                imp_run_body.italic = True

                imp_run_end = imp_p.add_run(" ]")
                imp_run_end.font.size = Pt(8.5)
                imp_run_end.font.color.rgb = RGBColor(120, 120, 120)
                imp_run_end.italic = True

        fname = os.path.join(EXPORTS_DIR, f"brief_{safe_name}_{today}_{template}.docx")
        doc.save(fname)
        return fname


def export_brief_markdown(motion_id: int, motion_name: str) -> str:
    """Wrapper method keeping compatibility with existing test suites."""
    return export_brief(motion_id, motion_name, "markdown")
