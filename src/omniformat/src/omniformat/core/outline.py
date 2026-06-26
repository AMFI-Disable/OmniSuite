import re
import datetime


class OutlineNode:
    def __init__(
        self,
        node_type: str,
        title: str = "",
        level: int = 0,
        data: dict = None,
        children: list = None,
    ):
        self.node_type = node_type  # "root", "folder", "card", "text"
        self.title = title
        self.level = level
        self.data = (
            data or {}
        )  # stores card info like side, tier, citation, text, impact_analysis
        self.children = children or []

    def to_dict(self) -> dict:
        return {
            "node_type": self.node_type,
            "title": self.title,
            "level": self.level,
            "data": self.data,
            "children": [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "OutlineNode":
        node = cls(
            node_type=d["node_type"],
            title=d.get("title", ""),
            level=d.get("level", 0),
            data=d.get("data"),
        )
        node.children = [cls.from_dict(c) for c in d.get("children", [])]
        return node


def parse_markdown_to_tree(md_content: str) -> OutlineNode:
    root = OutlineNode("root", "Strategic Brief Outline", 0)
    stack = [root]  # stack of (node)

    lines = md_content.splitlines()
    current_card = None
    current_text_lines = []

    def flush_current_card():
        nonlocal current_card, current_text_lines
        if current_card:
            raw_text = "\n".join(current_text_lines).strip()
            # Try to extract CITE
            cite_match = re.search(
                r"\*\*CITE:\*\*\s*(.*?)(?:\n\n|\n|$)", raw_text, re.IGNORECASE
            )
            if not cite_match:
                cite_match = re.search(
                    r"CITE:\s*(.*?)(?:\n\n|\n|$)", raw_text, re.IGNORECASE
                )

            if cite_match:
                current_card.data["citation"] = cite_match.group(1).strip()
                body = raw_text.replace(cite_match.group(0), "").strip()
            else:
                current_card.data["citation"] = ""
                body = raw_text

            # Try to extract IMPACT ANALYSIS
            if "**IMPACT ANALYSIS:**" in body:
                parts = body.split("**IMPACT ANALYSIS:**")
                body = parts[0].strip()
                current_card.data["impact_analysis"] = parts[1].strip()
            elif "IMPACT ANALYSIS:" in body:
                parts = body.split("IMPACT ANALYSIS:")
                body = parts[0].strip()
                current_card.data["impact_analysis"] = parts[1].strip()
            else:
                current_card.data["impact_analysis"] = ""

            current_card.data["text"] = body

            # Find correct parent for the card (level 4)
            while len(stack) > 1 and stack[-1].level >= 4:
                stack.pop()
            stack[-1].children.append(current_card)

            current_card = None
            current_text_lines = []

    for line in lines:
        # H4 or H5 or H6 are cards
        card_match = re.match(r"^(#{4,6})\s*(.*)$", line)
        if card_match:
            flush_current_card()
            hashes, content = card_match.groups()

            # Extract stars
            stars_match = re.match(r"^([⭐★]+)\s*(.*)$", content)
            if stars_match:
                stars, content = stars_match.groups()
                tier = len(stars)
            else:
                tier = 1

            # Extract side [AFF] or [NEG]
            side_match = re.match(r"^\[(AFF|NEG)\]\s*(.*)$", content, re.IGNORECASE)
            if side_match:
                side, tag = side_match.groups()
                side = side.upper()
            else:
                side = "AFF"
                tag = content

            current_card = OutlineNode(
                node_type="card",
                title=tag.strip(),
                level=4,
                data={
                    "tag": tag.strip(),
                    "side": side,
                    "tier": tier,
                },
            )
            continue

        # H1, H2, H3 are folders
        header_match = re.match(r"^(#{1,3})\s+(.*)$", line)
        if header_match:
            flush_current_card()
            hashes, title = header_match.groups()
            level = len(hashes)
            if (
                title.strip().startswith("🏛️ STRATEGIC BRIEF")
                or "STRATEGIC BRIEF:" in title
            ):
                root.title = title.strip()
                continue

            new_folder = OutlineNode("folder", title.strip(), level=level)

            # Pop stack until we find a node with level < this level
            while len(stack) > 1 and stack[-1].level >= level:
                stack.pop()

            stack[-1].children.append(new_folder)
            stack.append(new_folder)
            continue

        if current_card is not None:
            current_text_lines.append(line)
        else:
            # Skip brief headers to avoid duplicating them
            if (
                line.strip()
                and not line.startswith("# 🏛️ STRATEGIC BRIEF:")
                and not line.startswith("> **Format:**")
                and not line.strip().startswith("---")
            ):
                new_text_node = OutlineNode(
                    "text", line.strip(), level=4, data={"text": line.strip()}
                )
                while len(stack) > 1 and stack[-1].level >= 4:
                    stack.pop()
                stack[-1].children.append(new_text_node)

    flush_current_card()
    return root


def serialize_tree_to_markdown(root: OutlineNode) -> str:
    md = []
    title = root.title
    if not title.startswith("#"):
        title = f"# {title}"
    md.append(f"{title}\n")
    md.append(
        f"> **Format:** Standard Markdown Brief | **Date:** {datetime.date.today().strftime('%Y-%m-%d')}\n\n"
    )
    md.append("---\n\n")

    def traverse(node: OutlineNode):
        if node.node_type == "folder":
            hashes = "#" * node.level
            md.append(f"{hashes} {node.title}\n\n")
        elif node.node_type == "card":
            stars = "⭐" * node.data.get("tier", 1)
            md.append(
                f"#### {stars} [{node.data.get('side', 'AFF')}] {node.data.get('tag', '').upper()}\n"
            )
            cite_str = node.data.get("citation", "")
            if cite_str:
                if not cite_str.startswith("**"):
                    cite_str = f"**{cite_str}**"
                md.append(f"**CITE:** {cite_str}  \n\n")
            md.append(f"{node.data.get('text', '')}\n\n")
            if node.data.get("impact_analysis"):
                md.append("**IMPACT ANALYSIS:**\n")
                imp = node.data["impact_analysis"].strip()
                if not imp.startswith("```"):
                    md.append(f"```\n{imp}\n```\n\n")
                else:
                    md.append(f"{imp}\n\n")
        elif node.node_type == "text":
            md.append(f"{node.data.get('text', '')}\n\n")

        for child in node.children:
            traverse(child)

    for child in root.children:
        traverse(child)

    return "".join(md)
