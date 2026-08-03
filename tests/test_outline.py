import os

import pytest
from omniformat.core.compiler import (
    compile_outline_to_markdown,
    compile_to_docx,
    compile_to_html,
    parse_markdown_to_outline,
)
from omniformat.core.outline import (
    parse_markdown_to_tree,
    serialize_tree_to_markdown,
)
from omniformat.ui.app import OmniFormat


@pytest.fixture
def sample_outline_md(tmp_path):
    md_content = (
        "# 🏛️ STRATEGIC BRIEF: CUSTOM OUTLINE\n"
        "> **Format:** Standard Markdown Brief | **Date:** 2026-06-18\n\n"
        "---\n\n"
        "## CONTENTION 1\n\n"
        "#### ⭐ [AFF] CLIMATE RESOLUTION\n"
        "**CITE:** **IPCC 2026**  \n\n"
        "Global warming is accelerating rapidly.\n\n"
        "**IMPACT ANALYSIS:**\n"
        "```\n"
        "Catastrophic threat to biosphere.\n"
        "```\n\n"
        "## CONTENTION 2\n\n"
        "#### ⭐⭐ [AFF] ECONOMIC INCENTIVES\n"
        "**CITE:** **Stern 2026**  \n\n"
        "Transitioning to green economy is net beneficial.\n"
    )
    file_path = tmp_path / "outline_test.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    return str(file_path)


def test_tree_parsing_and_serialization(sample_outline_md):
    with open(sample_outline_md, encoding="utf-8") as f:
        content = f.read()

    tree_root = parse_markdown_to_tree(content)
    assert tree_root.node_type == "root"
    assert len(tree_root.children) == 2  # CONTENTION 1 and CONTENTION 2

    assert tree_root.children[0].node_type == "folder"
    assert tree_root.children[0].title == "CONTENTION 1"
    assert len(tree_root.children[0].children) == 1

    assert tree_root.children[0].children[0].node_type == "card"
    assert tree_root.children[0].children[0].title == "CLIMATE RESOLUTION"
    assert tree_root.children[0].children[0].data["side"] == "AFF"

    # Serialize back
    serialized = serialize_tree_to_markdown(tree_root)
    assert "## CONTENTION 1" in serialized
    assert "#### ⭐ [AFF] CLIMATE RESOLUTION" in serialized


def test_parse_and_compile_outline_compat(sample_outline_md):
    with open(sample_outline_md, encoding="utf-8") as f:
        content = f.read()

    outline = parse_markdown_to_outline(content)

    # Assert correct extraction of folders and cards
    assert len(outline) == 4
    assert outline[0]["type"] == "folder"
    assert outline[0]["title"] == "CONTENTION 1"
    assert outline[0]["level"] == 2

    assert outline[1]["type"] == "card"
    assert outline[1]["tag"] == "CLIMATE RESOLUTION"
    assert outline[1]["side"] == "AFF"
    assert outline[1]["tier"] == 1
    assert "IPCC 2026" in outline[1]["citation"]

    # Recompile back to Markdown
    recompiled = compile_outline_to_markdown(outline)
    assert "## CONTENTION 1" in recompiled
    assert "#### ⭐ [AFF] CLIMATE RESOLUTION" in recompiled


def test_hierarchical_compile_outputs(sample_outline_md):
    html_path = compile_to_html(sample_outline_md, theme="cyberdark")
    assert os.path.exists(html_path)
    with open(html_path, encoding="utf-8") as f:
        html_content = f.read()
        assert 'style="margin-left: 20px;"' in html_content
        assert 'style="margin-left: 60px;"' in html_content

    docx_path = compile_to_docx(sample_outline_md)
    assert os.path.exists(docx_path)


@pytest.mark.asyncio
async def test_outline_builder_tui_actions(sample_outline_md):
    app = OmniFormat(target_file=sample_outline_md)
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.active_file_path == sample_outline_md
        assert app.outline_tree is not None
        outline_tree = app.query_one("#outline-tree")
        root_node = outline_tree.root
        assert len(root_node.children) == 2

        # Select first child node (CONTENTION 1) and move it down
        outline_tree.select_node(root_node.children[0])
        await pilot.pause()
        app.action_move_down()
        await pilot.pause()

        # Check order of children in self.outline_tree
        assert app.outline_tree.children[1].title == "CONTENTION 1"
        assert app.outline_tree.children[0].title == "CONTENTION 2"

        # Select the node at the top and move it up (should not change)
        outline_tree.select_node(root_node.children[0])
        await pilot.pause()
        app.action_move_up()
        await pilot.pause()
        assert app.outline_tree.children[0].title == "CONTENTION 2"

        # Remove the top node (CONTENTION 2)
        app.action_delete_outline()
        await pilot.pause()
        assert len(app.outline_tree.children) == 1
        assert app.outline_tree.children[0].title == "CONTENTION 1"
