from unittest.mock import MagicMock, patch

from omnidebate.ui.screens.export_brief import ExportBriefScreen
from omniformat.core.compliance import (
    analyze_markdown,
    auto_correct_markdown,
    calculate_readability,
    detect_and_parse_forensics,
)


def test_readability_and_heading_validation():
    # 1. Test low readability FRE score alert (< 30)
    # Extremely complex academic text with very long words and sentences
    unreadable_text = (
        "The hyper-dimensionality of socio-economic structural paradigms fundamentally "
        "interconnects with institutionalized epistemological frameworks, thereby creating "
        "impenetrable systemic barriers that perpetuate historical inequities across generations."
    )
    # Check FRE calculation directly
    fre_score = calculate_readability(unreadable_text)
    assert fre_score < 30

    # Check linter warning
    report = analyze_markdown(unreadable_text)
    assert any("Readability warning" in w and "< 30" in w for w in report["warnings"])

    # 2. Test high readability FRE score alert (> 80)
    # Very simple text
    simple_text = "The cat sat on the mat. The dog saw the cat. The cat ran away. It was fun."
    fre_score_simple = calculate_readability(simple_text)
    assert fre_score_simple > 80

    report_simple = analyze_markdown(simple_text)
    assert any("Readability warning" in w and "> 80" in w for w in report_simple["warnings"])

    # 3. Test skipped heading levels (H1 to H3)
    skipped_headings = "# First Level Heading\n### Third Level Heading (Skipping H2)\n"
    report_headings = analyze_markdown(skipped_headings)
    assert any("MD001" in w and "H1 to H3" in w for w in report_headings["warnings"])

    # 4. Test auto-correct of skipped heading levels (H3 normalized to H2)
    corrected = auto_correct_markdown(skipped_headings)
    assert "## Third Level Heading" in corrected

    # 5. Test style consistency / markup safety warnings (unclosed bold/italic)
    unclosed_bold = "This is **bold but not closed. And some *italic stuff too."
    report_styles = analyze_markdown(unclosed_bold)
    assert any("MD037" in w and "bold" in w for w in report_styles["warnings"])
    assert any("MD038" in w and "italic" in w for w in report_styles["warnings"])

    # 6. Test auto-correct of unclosed bold/italic styles
    corrected_styles = auto_correct_markdown(unclosed_bold)
    assert (
        corrected_styles.strip() == "This is **bold but not closed. And some *italic stuff too.***"
    )


def test_forensic_metadata_extraction():
    # Simulated strategic debate brief with metadata headers and various cards
    brief_content = (
        "# 🏛️ STRATEGIC BRIEF: CLIMATE ACTION NOW\n"
        "> **Format:** Standard Markdown Brief | **Date:** 2026-06-06\n\n"
        "## 🧠 STRATEGIC SYNTHESIS\n"
        "- **Evidence Density:** 3 total cards\n\n"
        "### AFFIRMATIVE (PRO)\n\n"
        "#### ⭐⭐⭐ [AFF] CARBON TAX REDUCES EMISSIONS\n"
        "**CITE:** Smith 2026\n"
        "The carbon tax is <u>highly effective</u>.\n\n"
        "#### ⭐ [AFF] RENEWABLE SUBSIDIES SUPPORT TRANSITION\n"
        "**CITE:** Jones 2025\n"
        "Subsidies are necessary.\n\n"
        "### NEGATIVE (CON)\n\n"
        "#### ⭐⭐⭐ [NEG] CARBON TAX HURTS GDP\n"
        "**CITE:** Miller 2026\n"
        "Regulations destroy growth.\n"
    )

    forensics = detect_and_parse_forensics(brief_content)
    assert forensics["is_brief"] is True
    assert forensics["total_cards"] == 3
    assert forensics["aff_count"] == 2
    assert forensics["neg_count"] == 1
    assert forensics["t3_count"] == 2  # Both carbon tax cards are Tier-3 (3 stars)

    # Non-brief content detection
    non_brief = "# Random document\nThis is just a standard notes file."
    forensics_none = detect_and_parse_forensics(non_brief)
    assert forensics_none["is_brief"] is False

    # Brief detection via comment tag
    comment_brief = "<!-- OMNIDEBATE BRIEF -->\n#### ⭐⭐⭐ [AFF] CITE: TAX WORKS\n"
    forensics_comment = detect_and_parse_forensics(comment_brief)
    assert forensics_comment["is_brief"] is True
    assert forensics_comment["total_cards"] == 1
    assert forensics_comment["aff_count"] == 1
    assert forensics_comment["t3_count"] == 1


@patch("subprocess.Popen")
def test_spawn_logic_mockup(mock_popen):
    screen = ExportBriefScreen(motion_id=1, motion_name="Test Motion")
    screen.exported_file = "/absolute/path/to/exported_brief.md"

    # Dismiss mock
    screen.dismiss = MagicMock()

    # Run screen handler
    screen.open_in_omniformat()

    # Verify Popen was called with correct command sequence
    mock_popen.assert_called_once()
    args_list = mock_popen.call_args[0][0]

    assert args_list[1].endswith("omnisuite")
    assert "--app" in args_list
    assert "format" in args_list
    assert "--file" in args_list
    assert "/absolute/path/to/exported_brief.md" in args_list

    # Verify it specifies start_new_session=True for non-blocking detaching
    kwargs = mock_popen.call_args[1]
    assert kwargs.get("start_new_session") is True

    # Verify screen dismiss was called
    screen.dismiss.assert_called_once()
