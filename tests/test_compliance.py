from omniformat.core.compliance import (
    analyze_markdown,
    auto_correct_markdown,
    balance_html_strings,
    calculate_readability,
    check_html_tags,
)


def test_auto_correct_markdown():
    # Test hard tabs replaced with spaces (MD010)
    assert auto_correct_markdown("line\twith\ttabs") == "line    with    tabs\n"

    # Test trailing spaces stripped (MD009)
    assert auto_correct_markdown("line with space   ") == "line with space\n"
    # Keep double space for markdown linebreak
    assert auto_correct_markdown("line with break  ") == "line with break  \n"

    # Test space missing after header hash (MD018)
    assert auto_correct_markdown("##Heading") == "## Heading\n"

    # Test list symbols standardized to '-' (MD004)
    assert auto_correct_markdown("* Bullet item") == "- Bullet item\n"

    # Test consecutive blank lines collapsed (MD012)
    assert auto_correct_markdown("A\n\n\n\nB") == "A\n\nB\n"

    # Test reversed links corrected (MD011)
    assert (
        auto_correct_markdown("Check (this)[http://example.com]")
        == "Check [this](http://example.com)\n"
    )


def test_check_html_tags():
    # Balanced
    assert check_html_tags("<u>Hello <b>world</b></u>") == []
    # Unclosed
    warnings = check_html_tags("<u>Hello <b>world")
    assert len(warnings) == 2
    assert any("Unclosed HTML tag <b>" in w for w in warnings)
    # Mismatched closing
    warnings_mismatch = check_html_tags("Hello </b>")
    assert len(warnings_mismatch) == 1
    assert "Mismatched closing HTML tag </b>" in warnings_mismatch[0]


def test_balance_html_strings():
    assert balance_html_strings("<u>Hello <b>world") == "<u>Hello <b>world</b></u>"
    assert balance_html_strings("<u>Hello <b>world</u>") == "<u>Hello <b>world</b></u>"
    assert balance_html_strings("Hello </b>") == "Hello "


def test_calculate_readability():
    # Standard readable text
    text = "The quick brown fox jumps over the lazy dog. This is a very simple sentence."
    score = calculate_readability(text)
    assert score > 50  # Should be highly readable


def test_analyze_markdown():
    doc = (
        "# Top Level Heading\n\n"
        "## Sub Heading\n\n"
        "This is a paragraph with a [link](https://google.com) and some `inline code`.\n\n"
        "- Unordered list item 1\n"
        "- Unordered list item 2\n"
    )
    report = analyze_markdown(doc)
    assert report["heading_score"] == 100
    assert report["style_score"] == 100
    assert report["link_score"] == 100
    assert report["readability_score"] > 0
    assert report["warnings"] == []
