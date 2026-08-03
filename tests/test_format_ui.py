import os

import pytest
from omniformat.ui.app import OmniFormat


@pytest.fixture
def sample_md_file(tmp_path):
    md_content = "# Heading\n##Header\nline\twith\ttabs\n"
    file_path = tmp_path / "test.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    return str(file_path)


@pytest.mark.asyncio
async def test_omniformat_ui_compliance(sample_md_file):
    app = OmniFormat(target_file=sample_md_file)
    async with app.run_test() as pilot:
        # Verify target file loaded
        assert app.active_file_path == sample_md_file

        # Linter metrics should reflect errors
        # ##Header is missing a space (headings_score < 100)
        # line\twith\ttabs has hard tabs (style_score < 100)
        headings_val = app.query_one("#gauge-headings")._value
        style_val = app.query_one("#gauge-style")._value
        assert headings_val < 100
        assert style_val < 100

        # Trigger auto-fix shortcut (ctrl+f)
        await pilot.press("ctrl+f")
        await pilot.pause()

        # Telemetry should update to 100% compliance
        new_headings_val = app.query_one("#gauge-headings")._value
        new_style_val = app.query_one("#gauge-style")._value
        assert new_headings_val == 100
        assert new_style_val == 100


@pytest.mark.asyncio
async def test_omniformat_ui_compile(sample_md_file, tmp_path):
    app = OmniFormat(target_file=sample_md_file)
    async with app.run_test() as pilot:
        # Change template selection
        select_template = app.query_one("#sel-template")
        select_template.value = "html_dark"
        await pilot.pause()

        # Press compile button
        await pilot.click("#btn-compile")
        await pilot.pause()

        # Compiled file should exist next to the source file
        html_path = os.path.splitext(sample_md_file)[0] + "_compiled_cyberdark.html"
        assert os.path.exists(html_path)
