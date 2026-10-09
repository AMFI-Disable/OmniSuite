"""Argument Tree Visualization Screen — ASCII Impact Chain Explorer.

Displays argument structures as expandable/collapsible trees using Textual's
built-in :class:`Tree` widget.  Nodes follow the debate hierarchy:

    Contention → Warrant → Impact

Each node shows its label, an impact score (computed by :class:`OracleEngine`),
and a card count.  Nodes are color-coded by impact score:
green (high, ≥70) → yellow (medium, 30–69) → red (low, <30).

© 2026 OmniSuite. Built for the Digital Grandmaster.
"""

from __future__ import annotations

import contextlib
import datetime
from dataclasses import dataclass, field

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, Static, Tree
from textual.widgets.tree import TreeNode

# ── Data Structures ──────────────────────────────────────────────────────────


@dataclass
class ArgumentNode:
    """Data payload attached to each tree node.

    Attributes:
        label: Human-readable node label (contention, warrant, or impact).
        impact_score: Heuristic score 0–100 from OracleEngine analysis.
        card_count: Number of evidence cards linked to this node.
        linked_card_ids: Set of vault card IDs linked to this node.
        node_type: One of ``"contention"``, ``"warrant"``, ``"impact"``,
            or ``"general"``.
    """

    label: str
    impact_score: int = 50
    card_count: int = 0
    linked_card_ids: set[int] = field(default_factory=set)
    node_type: str = "general"


# ── Helpers ──────────────────────────────────────────────────────────────────


def _score_color(score: int) -> str:
    """Return a Rich color name based on impact score thresholds.

    - ≥ 70 → green
    - 30–69 → yellow
    - < 30 → red
    """
    if score >= 70:
        return "green"
    elif score >= 30:
        return "yellow"
    return "red"


def _format_node_label(data: ArgumentNode) -> str:
    """Build the display string for a tree node.

    Format: ``[score] Label  (N cards)``
    """
    color = _score_color(data.impact_score)
    cards_suffix = (
        f"  ({data.card_count} card{'s' if data.card_count != 1 else ''})"
        if data.card_count
        else ""
    )
    return f"[{color}][{data.impact_score:3d}][/{color}] {data.label}{cards_suffix}"


# ── Input Overlay ────────────────────────────────────────────────────────────


class TreeInputOverlay(Vertical):
    """Inline input overlay for adding / editing tree nodes.

    Sits at the bottom of the screen without pushing a full modal.
    """

    DEFAULT_CSS = """
    TreeInputOverlay {
        dock: bottom;
        height: auto;
        max-height: 5;
        background: $surface;
        border-top: solid $accent;
        padding: 0 2;
    }
    TreeInputOverlay Label {
        margin-right: 1;
    }
    """

    def __init__(self, prompt: str = "Node label:", input_id: str = "tree-input"):
        super().__init__()
        self.prompt = prompt
        self.input_id = input_id

    def compose(self) -> ComposeResult:
        yield Label(self.prompt)
        yield Input(placeholder="Enter label…", id=self.input_id)


# ── Main Screen ──────────────────────────────────────────────────────────────


class ArgumentTreeScreen(Screen):
    """ASCII argument tree visualization screen.

    Provides an expandable/collapsible tree view of debate argument structures
    following the Contention → Warrant → Impact hierarchy.

    Keyboard shortcuts
    ------------------
    - ``a`` — add child node under the selected node
    - ``e`` — edit the selected node's label
    - ``d`` — delete the selected node (with confirmation)
    - ``Enter`` — expand / collapse the selected node
    - ``c`` — link a vault card to the selected node
    - ``s`` — set impact score for the selected node
    - ``x`` — export tree to markdown outline
    - ``Escape`` — back to main screen
    """

    BINDINGS = [
        Binding("a", "add_child", "Add Child", show=True),
        Binding("e", "edit_node", "Edit Node", show=True),
        Binding("d", "delete_node", "Delete", show=True),
        Binding("c", "link_card", "Link Card", show=True),
        Binding("s", "set_score", "Set Score", show=True),
        Binding("x", "export_tree", "Export MD", show=True),
        Binding("escape", "go_back", "Back", show=True),
    ]

    DEFAULT_CSS = """
    ArgumentTreeScreen {
        layout: vertical;
    }
    #tree-container {
        height: 1fr;
        border: solid $surface-lighten-2;
        padding: 1;
    }
    #tree-status-bar {
        dock: bottom;
        height: 1;
        background: $surface;
        padding: 0 2;
        color: $text-muted;
    }
    """

    def __init__(
        self,
        initial_data: dict | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.initial_data = initial_data
        self._input_mode: str | None = None  # "add", "edit", "link", "score"
        self._pending_delete: TreeNode | None = None

    # ── Compose ──────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        """Build the tree screen layout."""
        yield Header(show_clock=True)

        with Vertical(id="tree-container"):
            yield Label(
                "🌳  ARGUMENT TREE  ·  Contention → Warrant → Impact",
                id="tree-title",
            )
            yield Tree("Case Structure", id="argument-tree")

        yield Static("", id="tree-status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Populate the tree with initial data or a starter template."""
        tree = self.query_one("#argument-tree", Tree)
        tree.show_root = True
        tree.guide_depth = 3

        if self.initial_data:
            self._load_tree_from_dict(tree.root, self.initial_data)
        else:
            self._build_starter_template(tree)

        tree.root.expand_all()
        self._update_status()

    def _build_starter_template(self, tree: Tree) -> None:
        """Create a default starter template for a new argument tree."""
        root_data = ArgumentNode(label="Case Structure", impact_score=50, node_type="general")
        tree.root.data = root_data
        tree.root.set_label(_format_node_label(root_data))

        # Contention 1
        c1_data = ArgumentNode(label="Contention 1", impact_score=50, node_type="contention")
        c1 = tree.root.add(_format_node_label(c1_data), data=c1_data)
        w1_data = ArgumentNode(label="Warrant", impact_score=50, node_type="warrant")
        c1.add(_format_node_label(w1_data), data=w1_data)
        i1_data = ArgumentNode(label="Impact", impact_score=50, node_type="impact")
        c1.add(_format_node_label(i1_data), data=i1_data)

        # Contention 2
        c2_data = ArgumentNode(label="Contention 2", impact_score=50, node_type="contention")
        c2 = tree.root.add(_format_node_label(c2_data), data=c2_data)
        w2_data = ArgumentNode(label="Warrant", impact_score=50, node_type="warrant")
        c2.add(_format_node_label(w2_data), data=w2_data)
        i2_data = ArgumentNode(label="Impact", impact_score=50, node_type="impact")
        c2.add(_format_node_label(i2_data), data=i2_data)

    def _load_tree_from_dict(self, parent: TreeNode, data: dict) -> None:
        """Recursively build tree nodes from a nested dictionary.

        Expected dictionary format::

            {
                "label": "Contention 1",
                "impact_score": 75,
                "card_count": 3,
                "node_type": "contention",
                "children": [ ... ]
            }
        """
        node_data = ArgumentNode(
            label=data.get("label", "Unnamed"),
            impact_score=data.get("impact_score", 50),
            card_count=data.get("card_count", 0),
            node_type=data.get("node_type", "general"),
        )
        parent.data = node_data
        parent.set_label(_format_node_label(node_data))

        for child_dict in data.get("children", []):
            child_node_data = ArgumentNode(
                label=child_dict.get("label", "Unnamed"),
                impact_score=child_dict.get("impact_score", 50),
                card_count=child_dict.get("card_count", 0),
                node_type=child_dict.get("node_type", "general"),
            )
            child = parent.add(_format_node_label(child_node_data), data=child_node_data)
            # Recurse into grandchildren
            for grandchild_dict in child_dict.get("children", []):
                self._load_tree_from_dict(child, grandchild_dict)

    # ── Node Operations ──────────────────────────────────────────────────

    def _get_selected_node(self) -> TreeNode | None:
        """Return the currently highlighted node in the tree, or ``None``."""
        tree = self.query_one("#argument-tree", Tree)
        return tree.cursor_node

    def action_add_child(self) -> None:
        """Show inline input to add a child node under the selected node."""
        node = self._get_selected_node()
        if node is None:
            self.app.notify("No node selected.", severity="warning")
            return
        if self._input_mode is not None:
            return
        self._input_mode = "add"
        overlay = TreeInputOverlay(
            prompt=f"New child under [{node.data.label}]:", input_id="tree-input"
        )
        self.mount(overlay)
        self.call_after_refresh(lambda: self.query_one("#tree-input", Input).focus())

    def action_edit_node(self) -> None:
        """Show inline input to edit the selected node's label."""
        node = self._get_selected_node()
        if node is None:
            self.app.notify("No node selected.", severity="warning")
            return
        if self._input_mode is not None:
            return
        self._input_mode = "edit"
        overlay = TreeInputOverlay(prompt="Edit node label:", input_id="tree-input")
        self.mount(overlay)

        current_label = node.data.label

        def _prefill() -> None:
            inp = self.query_one("#tree-input", Input)
            inp.value = current_label
            inp.focus()

        self.call_after_refresh(_prefill)

    def action_delete_node(self) -> None:
        """Delete the selected node after confirmation.

        First press marks the node for deletion; second press confirms.
        """
        node = self._get_selected_node()
        if node is None:
            self.app.notify("No node selected.", severity="warning")
            return
        if node.is_root:
            self.app.notify("Cannot delete the root node.", severity="error")
            return

        if self._pending_delete is node:
            # Confirmed — remove the node
            label = node.data.label if node.data else "node"
            node.remove()
            self._pending_delete = None
            self.app.notify(f"Deleted: {label}", severity="information")
            self._update_status()
        else:
            # First press — ask for confirmation
            self._pending_delete = node
            self.app.notify(
                f"Press 'd' again to confirm deleting: {node.data.label}",
                severity="warning",
            )

    def action_link_card(self) -> None:
        """Show inline input to link a vault card ID to the selected node."""
        node = self._get_selected_node()
        if node is None:
            self.app.notify("No node selected.", severity="warning")
            return
        if self._input_mode is not None:
            return
        self._input_mode = "link"
        overlay = TreeInputOverlay(prompt="Enter card ID to link:", input_id="tree-input")
        self.mount(overlay)
        self.call_after_refresh(lambda: self.query_one("#tree-input", Input).focus())

    def action_set_score(self) -> None:
        """Show inline input to set the impact score for the selected node."""
        node = self._get_selected_node()
        if node is None:
            self.app.notify("No node selected.", severity="warning")
            return
        if self._input_mode is not None:
            return
        self._input_mode = "score"
        overlay = TreeInputOverlay(prompt="Impact score (0–100):", input_id="tree-input")
        self.mount(overlay)

        def _prefill() -> None:
            inp = self.query_one("#tree-input", Input)
            inp.value = str(node.data.impact_score)
            inp.focus()

        self.call_after_refresh(_prefill)

    @on(Input.Submitted, "#tree-input")
    def _handle_input_submit(self, event: Input.Submitted) -> None:
        """Process submission from the inline input overlay."""
        value = event.value.strip()
        node = self._get_selected_node()

        if self._input_mode == "add" and value and node is not None:
            # Infer node type from parent depth
            depth = 0
            parent = node
            while parent.parent is not None:
                depth += 1
                parent = parent.parent
            type_map = {0: "contention", 1: "warrant", 2: "impact"}
            node_type = type_map.get(depth, "general")

            child_data = ArgumentNode(label=value, impact_score=50, node_type=node_type)
            node.add(_format_node_label(child_data), data=child_data)
            node.expand()
            self.app.notify(f"Added: {value}", severity="information")

        elif self._input_mode == "edit" and value and node is not None:
            node.data.label = value
            node.set_label(_format_node_label(node.data))
            self.app.notify("Node updated.", severity="information")

        elif self._input_mode == "link" and value and node is not None:
            try:
                card_id = int(value)
                node.data.linked_card_ids.add(card_id)
                node.data.card_count = len(node.data.linked_card_ids)
                node.set_label(_format_node_label(node.data))
                self.app.notify(
                    f"Linked card #{card_id} to {node.data.label}.",
                    severity="success",
                )
            except ValueError:
                self.app.notify("Invalid card ID.", severity="error")

        elif self._input_mode == "score" and value and node is not None:
            try:
                score = max(0, min(100, int(value)))
                node.data.impact_score = score
                node.set_label(_format_node_label(node.data))
                self.app.notify(
                    f"Score set to {score} for {node.data.label}.",
                    severity="information",
                )
            except ValueError:
                self.app.notify("Invalid score (must be 0–100).", severity="error")

        self._dismiss_input()
        self._update_status()

    def _dismiss_input(self) -> None:
        """Remove the inline input overlay and reset input mode."""
        self._input_mode = None
        try:
            overlay = self.query_one(TreeInputOverlay)
            overlay.remove()
        except Exception:
            pass

    # ── Tree Events ──────────────────────────────────────────────────────

    @on(Tree.NodeHighlighted, "#argument-tree")
    def _on_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        """Update status bar when a new node is highlighted."""
        # Clear pending delete if user moves to a different node
        if self._pending_delete is not None and self._pending_delete is not event.node:
            self._pending_delete = None
        self._update_status()

    # ── Export ────────────────────────────────────────────────────────────

    def action_export_tree(self) -> None:
        """Export the argument tree to a markdown outline file."""
        tree = self.query_one("#argument-tree", Tree)
        md = self._generate_markdown(tree.root, depth=0)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tree_export_{timestamp}.md"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("# Argument Tree Export\n\n")
                f.write(f"_Generated {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n")
                f.write(md)
            self.app.notify(f"Tree exported to {filename}", severity="success")
        except OSError as exc:
            self.app.notify(f"Export failed: {exc}", severity="error")

    def _generate_markdown(self, node: TreeNode, depth: int) -> str:
        """Recursively generate a markdown outline from the tree.

        Args:
            node: The tree node to render.
            depth: Current indentation depth.

        Returns:
            A markdown string with nested bullet points.
        """
        lines: list[str] = []
        indent = "  " * depth

        if node.data is not None:
            data: ArgumentNode = node.data
            score_str = f"[{data.impact_score}]"
            cards_str = f" ({data.card_count} cards)" if data.card_count else ""
            type_badge = f" `{data.node_type}`" if data.node_type != "general" else ""
            lines.append(f"{indent}- **{data.label}** {score_str}{cards_str}{type_badge}")
        else:
            lines.append(f"{indent}- {node.label}")

        for child in node.children:
            lines.append(self._generate_markdown(child, depth + 1))

        return "\n".join(lines)

    # ── Navigation ───────────────────────────────────────────────────────

    def action_go_back(self) -> None:
        """Dismiss any open overlay or pop back to the main screen."""
        if self._input_mode is not None:
            self._dismiss_input()
            return
        self.app.pop_screen()

    # ── Status Bar ───────────────────────────────────────────────────────

    def _update_status(self) -> None:
        """Refresh the bottom status bar with selected node information."""
        node = self._get_selected_node()
        if node is None or node.data is None:
            status = "No node selected"
        else:
            data: ArgumentNode = node.data
            _score_color(data.impact_score)
            children_count = len(node.children)
            status = (
                f"Node: {data.label} │ Type: {data.node_type} │ "
                f"Score: {data.impact_score} │ Cards: {data.card_count} │ "
                f"Children: {children_count}"
            )

        with contextlib.suppress(Exception):
            self.query_one("#tree-status-bar", Static).update(status)
