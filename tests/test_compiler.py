import os

import pytest
from omniformat.core.compiler import (
    compile_to_docx,
    compile_to_html,
    parse_inline_styles,
    parse_markdown_to_html,
    prettify_markdown_file,
)


@pytest.fixture
def sample_md_file(tmp_path):
    md_content = (
        "# Test Document\n\n"
        "This is a paragraph with **bold** text and `code`.\n\n"
        "- Bullet point 1\n"
        "- Bullet point 2\n\n"
        "```python\n"
        "print('hello')\n"
        "```\n\n"
        "| Header 1 | Header 2 |\n"
        "| --- | --- |\n"
        "| Value 1 | Value 2 |\n"
    )
    file_path = tmp_path / "sample.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    return str(file_path)


def test_parse_inline_styles():
    assert "<strong>bold</strong>" in parse_inline_styles("**bold**")
    assert "<em>italic</em>" in parse_inline_styles("*italic*")
    assert "<code>code</code>" in parse_inline_styles("`code`")
    assert '<a href="http://example.com" target="_blank">label</a>' in parse_inline_styles(
        "[label](http://example.com)"
    )


def test_parse_markdown_to_html():
    md = "# Heading\nSome paragraph.\n- Item"
    html_out = parse_markdown_to_html(md)
    assert "<h1>Heading</h1>" in html_out
    assert "<p>Some paragraph.</p>" in html_out
    assert "<ul>\n<li>Item</li>\n</ul>" in html_out


def test_compile_to_html(sample_md_file):
    html_path = compile_to_html(sample_md_file, theme="cyberdark")
    assert os.path.exists(html_path)
    with open(html_path, encoding="utf-8") as f:
        content = f.read()
        assert "<!DOCTYPE html>" in content
        assert "Test Document" in content
        assert "Bullet point 1" in content
        assert 'class="language-python"' in content


def test_compile_to_docx(sample_md_file):
    docx_path = compile_to_docx(sample_md_file)
    assert os.path.exists(docx_path)
    # python-docx should save without errors


def test_prettify_markdown_file(sample_md_file):
    # Mess up sample file with formatting issues
    bad_md = "##Heading\nline\twith\ttabs\n"
    with open(sample_md_file, "w", encoding="utf-8") as f:
        f.write(bad_md)

    prettify_markdown_file(sample_md_file)

    with open(sample_md_file, encoding="utf-8") as f:
        content = f.read()
        assert "## Heading" in content
        assert "line    with    tabs" in content
