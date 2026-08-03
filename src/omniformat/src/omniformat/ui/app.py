"""OmniFormat v1.0.0 — Standalone Markdown Formatting & Styling Workstation.

Decoupled TUI application for formatting, linting, and compiling Markdown files.
© 2026 OmniSuite. Built for the Digital Grandmaster.
"""

import importlib.resources
import os

from omniformat.core.compiler import (
    compile_to_docx,
    compile_to_html,
    parse_markdown_to_outline,
    prettify_markdown_file,
)
from omniformat.core.compliance import analyze_markdown, detect_and_parse_forensics
from omniformat.core.outline import (
    OutlineNode,
    parse_markdown_to_tree,
    serialize_tree_to_markdown,
)
from omniformat.ui.screens.splash import SplashScreen
from omnishared.config import load_config, run_setup_dirs
from omnishared.ui.widgets import (
    GaugeBar,
    QuickNotes,
    SparklineBar,
    SystemLog,
)
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Collapsible,
    DirectoryTree,
    Footer,
    Input,
    Label,
    ListItem,
    ListView,
    Markdown,
    Select,
    Static,
    TextArea,
    Tree,
)


class OmniFormat(App):
    """The central controller for the OmniFormat Markdown Workstation."""

    TITLE = "OmniFormat v1.0.0 - Standalone Workstation"
    CSS_PATH = [
        str(importlib.resources.files("omnishared.ui").joinpath("tcss", "theme.tcss")),
        "omniformat.tcss",
    ]

    BINDINGS = [
        Binding("q", "quit", "Exit"),
        Binding("c", "compile_document", "Compile/Export File"),
        Binding("ctrl+d", "toggle_debug", "Debug Mode"),
        Binding("ctrl+f", "auto_fix_formatting", "Auto-Fix Formatting"),
        Binding("e", "toggle_edit_mode", "Toggle Edit Mode"),
        Binding("ctrl+up", "move_up", "Move Outline Item Up", show=False),
        Binding("ctrl+down", "move_down", "Move Outline Item Down", show=False),
    ]

    active_file_path = reactive(None)
    selected_template = reactive("markdown")
    debug_mode = reactive(False)
    is_edit_mode = reactive(False)

    def __init__(self, target_file: str = None):
        super().__init__()
        run_setup_dirs()
        self._config = load_config()
        self.initial_target_file = target_file
        self.outline = []
        self.outline_tree = None

    def compose(self) -> ComposeResult:
        yield Static("📂 EXPLORER > 🧬 PREVIEW > 📊 STATUS: READY", id="breadcrumb-bar")

        with Horizontal(id="main-layout"):
            # Zone Left: WORKSPACE FILE EXPLORER
            with Vertical(id="zone-alpha", classes="tactical-zone"):
                yield Label("[ 🏛️ WORKSPACE FILE TREE ]", classes="zone-header")
                yield DirectoryTree(".", id="file-tree")

                yield Label("[ 🗂️ FORMATTING TEMPLATE ]", classes="zone-header")
                yield Select(
                    [
                        ("Prettify Markdown (.md)", "markdown"),
                        ("Styled HTML - Dark (.html)", "html_dark"),
                        ("Styled HTML - Light (.html)", "html_light"),
                        ("Word Document (.docx)", "docx"),
                    ],
                    value="markdown",
                    id="sel-template",
                )

            # Zone Center: MARKDOWN DOCUMENT PREVIEW
            with Vertical(id="zone-beta", classes="tactical-zone"):
                yield Label("[ 🧬 MARKDOWN DOCUMENT PREVIEW ]", classes="zone-header")
                yield Markdown(
                    "# SELECT A MARKDOWN FILE\nSelect a `.md` file from the workspace tree to view, format, and lint.",
                    id="doc-preview",
                )
                yield TextArea(id="doc-editor")
                with Horizontal(id="compile-actions"):
                    yield Button("⚡ COMPILE / EXPORT", id="btn-compile", variant="primary")
                    yield Button("📝 EDIT MODE", id="btn-toggle-edit", variant="default")
                    yield Button("🔧 AUTO-FIX LINT", id="btn-autofix", variant="warning")

            # Zone Right: MARKDOWN LINT TELEMETRY
            with Vertical(id="zone-gamma", classes="tactical-zone"):
                yield Label("[ 🔮 LINT COMPLIANCE ]", classes="zone-header")
                yield GaugeBar(label="READABILITY (FRE)", id="gauge-readability", value=100)
                yield GaugeBar(label="HEADING STRUCTURE", id="gauge-headings", value=100)
                yield GaugeBar(label="STYLE CONSISTENCY", id="gauge-style", value=100)
                yield GaugeBar(label="LINK HEALTH", id="gauge-links", value=100)

                yield Label("[ ⚠️ COMPLIANCE REPORT ]", classes="hud-group-label")
                yield ListView(id="warnings-list")

                with Collapsible(
                    title="🗂️ OUTLINE BUILDER",
                    collapsed=False,
                    id="outline-builder-panel",
                ):
                    yield Tree("Strategic Brief", id="outline-tree")
                    with Horizontal(classes="outline-controls"):
                        yield Button("📁 Add Heading", id="btn-add-folder", variant="success")
                        yield Button("▲ Up", id="btn-move-up", variant="primary")
                    with Horizontal(classes="outline-controls"):
                        yield Button("▼ Down", id="btn-move-down", variant="primary")
                        yield Button("✖ Remove", id="btn-delete-outline", variant="error")

                with Collapsible(
                    title="📊 DEBATE FORENSICS",
                    collapsed=True,
                    id="debate-forensics-panel",
                ):
                    yield Label("Total Cards: 0", id="lbl-forensics-total")
                    yield Label("🟢 AFF Cards: 0", id="lbl-forensics-aff")
                    yield Label("🔴 NEG Cards: 0", id="lbl-forensics-neg")
                    yield Label("⭐ Tier-3 Priority: 0", id="lbl-forensics-t3")

                with Collapsible(
                    title="🕒 REVISION HISTORY",
                    collapsed=True,
                    id="revision-history-panel",
                ):
                    yield Static("No active diff.", id="revision-history-diff")

                with Collapsible(
                    title="🤖 AI ASSISTANT",
                    collapsed=True,
                    id="ai-assistant-panel",
                ):
                    yield Label("Status: Checking...", id="lbl-ai-status")
                    yield Select(
                        [
                            ("Improve Card Tag", "improve_tag"),
                            ("Detect Argument Gaps", "detect_gaps"),
                            ("Proofread Document", "proofread"),
                        ],
                        value="improve_tag",
                        id="sel-ai-action",
                    )
                    yield Button("⚡ RUN AI ASSIST", id="btn-run-ai", variant="primary")
                    yield Static("AI suggestions will appear here.", id="lbl-ai-output")

                yield Label("📈 COMPILATION VELOCITY", classes="hud-group-label")
                yield SparklineBar(
                    values=[1, 2, 4, 3, 5, 6, 8], label="COMPILES", id="compile-history"
                )

                with Collapsible(title="🎤 TACTICAL COMMAND", collapsed=False):
                    yield SystemLog()
                    yield Static("LOG: Ready.", id="timeline-log")

                with Collapsible(title="📌 QUICK NOTES", collapsed=True):
                    yield QuickNotes()

        yield Footer()

    def on_mount(self) -> None:
        if not os.environ.get("PYTEST_CURRENT_TEST"):
            self.call_after_refresh(lambda: self.push_screen(SplashScreen()))
        self.query_one("#doc-editor").display = False
        self._update_compliance()
        self.check_ai_status_on_load()
        # If passed target_file via CLI, resolve and select it
        if self.initial_target_file and os.path.exists(self.initial_target_file):
            abs_path = os.path.abspath(self.initial_target_file)
            if abs_path.endswith(".md"):
                self.active_file_path = abs_path
                self._update_preview()
            else:
                self.toast("Only Markdown (.md) files are supported.")

    def on_collapsible_expanded(self, event: Collapsible.Expanded) -> None:
        """Accordion collapsible behavior."""
        for collapsible in self.query(Collapsible):
            if collapsible != event.collapsible:
                collapsible.collapsed = True

    @on(DirectoryTree.FileSelected, "#file-tree")
    def file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Loads the selected file if it is Markdown."""
        path = str(event.path)
        if path.endswith(".md"):
            self.active_file_path = path
            self._update_preview()
        else:
            self.toast("Unsupported format. Please select a Markdown (.md) file.")

    @on(Select.Changed, "#sel-template")
    def template_changed(self, event: Select.Changed) -> None:
        if event.value:
            self.selected_template = event.value

    @on(Button.Pressed, "#btn-autofix")
    def autofix_btn_pressed(self) -> None:
        self.action_auto_fix_formatting()

    def _update_compliance(self) -> None:
        """Runs the linter and updates the telemetry gauges."""
        if not self.active_file_path or not os.path.exists(self.active_file_path):
            self.query_one("#gauge-readability").set_value(100)
            self.query_one("#gauge-headings").set_value(100)
            self.query_one("#gauge-style").set_value(100)
            self.query_one("#gauge-links").set_value(100)
            wl = self.query_one("#warnings-list", ListView)
            wl.clear()
            wl.mount(ListItem(Label("No document loaded.")))
            try:
                self.query_one("#debate-forensics-panel", Collapsible).display = False
            except Exception:
                pass
            return

        try:
            with open(self.active_file_path, encoding="utf-8") as f:
                content = f.read()
            self._run_live_lint(content)
        except Exception as e:
            self._log_error(f"Linter analysis failed: {e}")

    def _update_preview(self) -> None:
        """Reads file contents and renders them in the Markdown viewer."""
        if not self.active_file_path or not os.path.exists(self.active_file_path):
            return

        try:
            with open(self.active_file_path, encoding="utf-8") as f:
                content = f.read()

            filename = os.path.basename(self.active_file_path)
            self.query_one("#doc-preview", Markdown).update(content)
            self._safe_update(
                "#breadcrumb-bar",
                f"📂 {filename} > LINTING COMPLIANCE READY",
            )
            self.outline_tree = parse_markdown_to_tree(content)
            self.outline = parse_markdown_to_outline(content)
            self._rebuild_outline_list()
            self._update_compliance()
            self._update_revision_history()
        except Exception as e:
            self._log_error(f"Failed to read file: {e}")

    @on(Button.Pressed, "#btn-compile")
    def compile_btn_pressed(self) -> None:
        self.action_compile_document()

    def action_compile_document(self) -> None:
        """Compiles or exports the active Markdown document."""
        if not self.active_file_path or not os.path.exists(self.active_file_path):
            self.toast("Load a markdown file first.")
            return

        self.toast(f"Compiling as {self.selected_template.upper()}...")
        try:
            out_file = None
            if self.selected_template == "markdown":
                out_file = prettify_markdown_file(self.active_file_path)
            elif self.selected_template == "html_dark":
                out_file = compile_to_html(self.active_file_path, theme="cyberdark")
            elif self.selected_template == "html_light":
                out_file = compile_to_html(self.active_file_path, theme="warmpaper")
            elif self.selected_template == "docx":
                out_file = compile_to_docx(self.active_file_path)

            if out_file:
                rel_path = os.path.relpath(out_file, start=os.getcwd())
                log_widget = self.query_one(SystemLog)
                log_widget.log_activity(f"Compiled document: {rel_path}")
                self.notify(f"Compiled successfully to: {rel_path}", severity="success")
                self._update_preview()
        except Exception as e:
            self._log_error(f"Compilation failed: {e}")
            self.notify(f"Compilation failed: {e}", severity="error")

    def action_auto_fix_formatting(self) -> None:
        """Autocorrects all formatting violations in the active Markdown file."""
        if not self.active_file_path or not os.path.exists(self.active_file_path):
            self.toast("Load a markdown file first.")
            return

        try:
            prettify_markdown_file(self.active_file_path)
            self._update_preview()
            log_widget = self.query_one(SystemLog)
            filename = os.path.basename(self.active_file_path)
            log_widget.log_activity(f"Auto-fixed formatting for: {filename}")
            self.notify("Successfully auto-fixed formatting errors!", severity="success")
        except Exception as e:
            self._log_error(f"Auto-fix failed: {e}")
            self.notify(f"Auto-fix failed: {e}", severity="error")

    def action_toggle_debug(self) -> None:
        self.debug_mode = not self.debug_mode
        state = "ENABLED" if self.debug_mode else "DISABLED"
        try:
            logger = self.query_one(SystemLog)
            logger.log_activity(f"DEBUG MODE: {state}")
            self.notify(f"Debug Mode: {state}", severity="warning")
        except Exception:
            pass

    def toast(self, message: str) -> None:
        self.notify(message, timeout=2)

    def _safe_update(self, selector: str, value: str) -> None:
        try:
            self.query_one(selector).update(value)
        except Exception:
            pass

    def _log_error(self, msg: str) -> None:
        try:
            self.query_one(SystemLog).log_activity(f"ERROR: {msg}")
        except Exception:
            pass

    @on(Button.Pressed, "#btn-toggle-edit")
    def toggle_edit_btn_pressed(self) -> None:
        self.action_toggle_edit_mode()

    def action_toggle_edit_mode(self) -> None:
        """Toggle between Markdown preview and live editor mode."""
        if not self.active_file_path:
            self.toast("Select a markdown file first.")
            return
        self.is_edit_mode = not self.is_edit_mode

    def watch_is_edit_mode(self, is_edit: bool) -> None:
        """React to edit mode changes by toggling widget visibility and loading content."""
        try:
            preview = self.query_one("#doc-preview")
            editor = self.query_one("#doc-editor", TextArea)
            btn = self.query_one("#btn-toggle-edit", Button)
            header = self.query_one("#zone-beta .zone-header", Label)

            preview.display = not is_edit
            editor.display = is_edit

            if is_edit:
                btn.label = "🧬 PREVIEW MODE"
                header.update("[ 📝 LIVE MARKDOWN EDITOR ]")
                # Load content
                if self.active_file_path and os.path.exists(self.active_file_path):
                    with open(self.active_file_path, encoding="utf-8") as f:
                        editor.text = f.read()
                else:
                    editor.text = ""
                editor.focus()
            else:
                btn.label = "📝 EDIT MODE"
                header.update("[ 🧬 MARKDOWN DOCUMENT PREVIEW ]")
                # Reload file contents into preview
                if self.active_file_path and os.path.exists(self.active_file_path):
                    with open(self.active_file_path, encoding="utf-8") as f:
                        preview.update(f.read())
        except Exception:
            pass

    @on(TextArea.Changed, "#doc-editor")
    def editor_changed(self, event: TextArea.Changed) -> None:
        """Triggers live linting immediately and debounces saving."""
        if not self.active_file_path:
            return

        filename = os.path.basename(self.active_file_path)
        self._safe_update(
            "#breadcrumb-bar",
            f"📂 {filename} > ⏳ Unsaved Changes...",
        )

        # Reactive live compliance updates
        new_text = event.text_area.text
        self._run_live_lint(new_text)

        # Debounced saving
        self._debounce_save(new_text)

    def _debounce_save(self, text: str) -> None:
        if hasattr(self, "_save_timer") and self._save_timer:
            self._save_timer.cancel()
        self._save_timer = self.set_timer(1.5, lambda: self._save_file(text))

    def _save_file(self, text: str) -> None:
        """Saves editor text to file system, updates preview, and refreshes Fossil diff."""
        if not self.active_file_path or not os.path.exists(self.active_file_path):
            return

        try:
            with open(self.active_file_path, "w", encoding="utf-8") as f:
                f.write(text)

            filename = os.path.basename(self.active_file_path)
            self._safe_update(
                "#breadcrumb-bar",
                f"📂 {filename} > ✅ Saved",
            )
            # Update the markdown preview widget so when user toggles back it is updated
            self.query_one("#doc-preview", Markdown).update(text)
            # Refresh Fossil diff
            self._update_revision_history()
        except Exception as e:
            self._log_error(f"Auto-save failed: {e}")

    def _run_live_lint(self, content: str) -> None:
        """Evaluates raw content in real-time to update compliance gauges and warnings list."""
        try:
            report = analyze_markdown(content)

            self.query_one("#gauge-readability").set_value(report["readability_score"])
            self.query_one("#gauge-headings").set_value(report["heading_score"])
            self.query_one("#gauge-style").set_value(report["style_score"])
            self.query_one("#gauge-links").set_value(report["link_score"])

            wl = self.query_one("#warnings-list", ListView)
            wl.clear()

            if not report["warnings"]:
                wl.mount(ListItem(Label("✅ Markdown compliant! (No lint errors)")))
            else:
                for warning in report["warnings"]:
                    wl.mount(ListItem(Label(warning)))

            # Update debate forensics
            forensics = detect_and_parse_forensics(content)
            panel = self.query_one("#debate-forensics-panel", Collapsible)
            if forensics["is_brief"]:
                panel.display = True
                self.query_one("#lbl-forensics-total", Label).update(
                    f"Total Cards: {forensics['total_cards']}"
                )
                self.query_one("#lbl-forensics-aff", Label).update(
                    f"🟢 AFF Cards: {forensics['aff_count']}"
                )
                self.query_one("#lbl-forensics-neg", Label).update(
                    f"🔴 NEG Cards: {forensics['neg_count']}"
                )
                self.query_one("#lbl-forensics-t3", Label).update(
                    f"⭐ Tier-3 Priority: {forensics['t3_count']}"
                )
                panel.collapsed = False
            else:
                panel.display = False
                panel.collapsed = True
        except Exception as e:
            self._log_error(f"Live lint analysis failed: {e}")

    def _update_revision_history(self) -> None:
        """Fetch and parse fossil diff, displaying styled additions and deletions."""
        if not self.active_file_path or not os.path.exists(self.active_file_path):
            self.query_one("#revision-history-diff", Static).update("No file loaded.")
            return

        import subprocess

        import rich.text
        from omnishared.config.config import WORKSPACE_ROOT

        try:
            cmd = ["fossil", "diff", "--unified", self.active_file_path]
            res = subprocess.run(cmd, cwd=WORKSPACE_ROOT, capture_output=True, text=True, timeout=5)

            diff_text = rich.text.Text()
            if res.returncode == 0 and res.stdout.strip():
                lines = res.stdout.splitlines()
                for line in lines:
                    if (
                        line.startswith("+++")
                        or line.startswith("---")
                        or line.startswith("Index:")
                        or line.startswith("===")
                    ):
                        diff_text.append(line + "\n", style="#94a3b8")
                    elif line.startswith("+"):
                        diff_text.append(line + "\n", style="bold #4ade80")
                    elif line.startswith("-"):
                        diff_text.append(line + "\n", style="bold #ef4444")
                    elif line.startswith("@@"):
                        diff_text.append(line + "\n", style="#38bdf8")
                    else:
                        diff_text.append(line + "\n")
            elif res.returncode == 0:
                diff_text.append("No changes detected in this revision.", style="italic #94a3b8")
            else:
                error_msg = res.stderr.strip() or f"fossil exit code {res.returncode}"
                diff_text.append(f"Fossil error:\n{error_msg}", style="bold #ef4444")

            self.query_one("#revision-history-diff", Static).update(diff_text)
        except Exception as e:
            self.query_one("#revision-history-diff", Static).update(
                f"Fossil diff unavailable:\n{e}"
            )

    @work(exclusive=True, thread=True)
    def check_ai_status_on_load(self) -> None:
        from omnishared.ai import check_ollama_status
        from omnishared.config import load_config

        config = load_config()
        model = config.get("ai", {}).get("ollama_model", "llama3")
        is_online = check_ollama_status()
        self.call_from_thread(self._update_ai_status_ui, is_online, model)

    def _update_ai_status_ui(self, is_online: bool, model: str) -> None:
        try:
            status_lbl = self.query_one("#lbl-ai-status", Label)
            if is_online:
                status_lbl.update(f"🟢 AI: Online ({model})")
            else:
                status_lbl.update("🔴 AI: Offline (Fallbacks active)")
        except Exception:
            pass

    @on(Button.Pressed, "#btn-run-ai")
    @work(exclusive=True, thread=True)
    def run_ai_action(self) -> None:
        """Run the selected AI Assistant action asynchronously."""
        from omnishared.ai import check_ollama_status, generate_completion

        # 1. Check if a markdown file is loaded
        if not self.active_file_path or not os.path.exists(self.active_file_path):
            self.call_from_thread(self.toast, "Please load a markdown file first.")
            return

        # 2. Get the active text
        content = ""
        try:
            is_edit = self.is_edit_mode
            if is_edit:
                content = self.query_one("#doc-editor", TextArea).text
            else:
                with open(self.active_file_path, encoding="utf-8") as f:
                    content = f.read()
        except Exception as e:
            self.call_from_thread(self.toast, f"Error reading document: {e}")
            return

        if not content.strip():
            self.call_from_thread(self.toast, "Document is empty.")
            return

        # Get selected action
        action = "improve_tag"
        try:
            action = self.query_one("#sel-ai-action", Select).value
        except Exception:
            pass

        # Update output to show progress
        self.call_from_thread(self._update_ai_output, "🤖 Thinking...")

        # Run action
        is_online = check_ollama_status()
        if not is_online:
            self.call_from_thread(
                self._update_ai_output,
                "❌ AI is Offline.\nHeuristic Fallback: Please ensure Ollama is running locally with 'llama3' model loaded.",
            )
            return

        prompt = ""
        system_prompt = "You are a professional forensic debate AI assistant and editor."
        if action == "improve_tag":
            prompt = (
                "Suggest a better 5-8 word tag for the following debate card or text. "
                "The tag should summarize the core warrant and claim clearly.\n\n"
                f"TEXT:\n{content[:2000]}\n\n"
                "Provide ONLY the tag, nothing else."
            )
        elif action == "detect_gaps":
            prompt = (
                "Scan the following text/argument brief for missing links, logical fallacies, or warrant gaps.\n\n"
                f"CONTENT:\n{content[:3000]}\n\n"
                "Provide a short bulleted list of 2-3 specific strategic argument gaps/improvements."
            )
        elif action == "proofread":
            prompt = (
                "Proofread the following text for spelling, grammar, stylistic consistency, and structure.\n\n"
                f"CONTENT:\n{content[:3000]}\n\n"
                "Provide a summary of suggestions followed by the polished/improved text."
            )

        try:
            result = generate_completion(prompt, system_prompt=system_prompt)
            self.call_from_thread(self._update_ai_output, result)
        except Exception as e:
            self.call_from_thread(self._update_ai_output, f"❌ Error during AI generation:\n{e}")

    def _rebuild_outline_list(self) -> None:
        """Repopulates the #outline-tree widget from the self.outline_tree."""
        try:
            tree = self.query_one("#outline-tree", Tree)
        except Exception:
            self.call_after_refresh(self._rebuild_outline_list)
            return

        try:
            selected_path = []
            cursor = tree.cursor_node
            if cursor and cursor != tree.root:
                curr = cursor
                while curr and curr != tree.root:
                    selected_path.append(curr.label.plain)
                    curr = curr.parent
            selected_path.reverse()

            tree.clear()
            if not self.outline_tree:
                return

            tree.root.label = f"🏛️ {self.outline_tree.title or 'Strategic Brief Outline'}"
            tree.root.data = self.outline_tree

            def add_nodes(tree_node, outline_node):
                for child in outline_node.children:
                    if child.node_type == "folder":
                        label = f"📁 {child.title}"
                    elif child.node_type == "card":
                        label = f"📄 [{child.data.get('side', 'AFF')}] {child.data.get('tag', '')}"
                    else:
                        snippet = child.data.get("text", "").replace("\n", " ")[:20]
                        label = f"📝 {snippet}..."

                    sub_node = tree_node.add(label, data=child, expand=True)
                    add_nodes(sub_node, child)

            add_nodes(tree.root, self.outline_tree)
            tree.root.expand()

            if selected_path:
                curr = tree.root
                for label_text in selected_path:
                    found = False
                    for child in curr.children:
                        if child.label.plain == label_text:
                            curr = child
                            found = True
                            break
                    if not found:
                        break
                if curr and curr != tree.root:
                    tree.select_node(curr)

        except Exception as e:
            self._log_error(f"Failed to rebuild outline tree: {e}")

    def _save_outline_changes(self) -> None:
        """Saves current self.outline_tree to the active markdown file and refreshes UI."""
        if not self.active_file_path or not self.outline_tree:
            return
        try:
            new_md = serialize_tree_to_markdown(self.outline_tree)
            with open(self.active_file_path, "w", encoding="utf-8") as f:
                f.write(new_md)
            if self.is_edit_mode:
                self.query_one("#doc-editor", TextArea).text = new_md
            self._update_preview()
        except Exception as e:
            self._log_error(f"Failed to save outline changes: {e}")

    @on(Button.Pressed, "#btn-add-folder")
    def on_add_folder(self) -> None:
        self.action_add_folder()

    @on(Button.Pressed, "#btn-delete-outline")
    def on_delete_outline(self) -> None:
        self.action_delete_outline()

    @on(Button.Pressed, "#btn-move-up")
    def on_move_up_btn(self) -> None:
        self.action_move_up()

    @on(Button.Pressed, "#btn-move-down")
    def on_move_down_btn(self) -> None:
        self.action_move_down()

    def find_parent_node(self, current: OutlineNode, target: OutlineNode) -> OutlineNode | None:
        for child in current.children:
            if child is target:
                return current
            res = self.find_parent_node(child, target)
            if res:
                return res
        return None

    def action_add_folder(self) -> None:
        """Prompt user for a folder name and insert it into the outline tree."""
        if not self.active_file_path or not self.outline_tree:
            self.toast("No active document loaded.")
            return

        def on_submit(folder_title: str | None) -> None:
            if folder_title:
                tree = self.query_one("#outline-tree", Tree)
                cursor = tree.cursor_node
                if not cursor or cursor == tree.root:
                    parent_node = self.outline_tree
                    idx = len(parent_node.children)
                else:
                    target = cursor.data
                    if target.node_type == "folder":
                        parent_node = target
                        idx = len(parent_node.children)
                    else:
                        parent_node = (
                            self.find_parent_node(self.outline_tree, target) or self.outline_tree
                        )
                        idx = parent_node.children.index(target) + 1

                level = parent_node.level + 1 if parent_node.level < 3 else 3
                new_node = OutlineNode("folder", folder_title, level=level)
                parent_node.children.insert(idx, new_node)
                self._save_outline_changes()

        self.push_screen(PromptModal("➕ ADD SUBHEADING / FOLDER", ""), on_submit)

    def action_delete_outline(self) -> None:
        """Delete the currently selected outline node."""
        if not self.active_file_path or not self.outline_tree:
            self.toast("No active document loaded.")
            return

        tree = self.query_one("#outline-tree", Tree)
        cursor = tree.cursor_node
        if not cursor or cursor == tree.root:
            self.toast("Cannot delete the root node.")
            return

        target = cursor.data
        if not target:
            return

        parent = self.find_parent_node(self.outline_tree, target)
        if not parent:
            return

        parent.children.remove(target)
        self.toast(f"Removed: {target.title or 'Text'}")
        self._save_outline_changes()

    def action_move_up(self) -> None:
        """Move the selected outline node up among siblings."""
        if not self.active_file_path or not self.outline_tree:
            return

        tree = self.query_one("#outline-tree", Tree)
        cursor = tree.cursor_node
        if not cursor or cursor == tree.root:
            return

        target = cursor.data
        if not target:
            return

        parent = self.find_parent_node(self.outline_tree, target)
        if not parent:
            return

        idx = parent.children.index(target)
        if idx > 0:
            parent.children[idx], parent.children[idx - 1] = (
                parent.children[idx - 1],
                parent.children[idx],
            )
            self._save_outline_changes()

    def action_move_down(self) -> None:
        """Move the selected outline node down among siblings."""
        if not self.active_file_path or not self.outline_tree:
            return

        tree = self.query_one("#outline-tree", Tree)
        cursor = tree.cursor_node
        if not cursor or cursor == tree.root:
            return

        target = cursor.data
        if not target:
            return

        parent = self.find_parent_node(self.outline_tree, target)
        if not parent:
            return

        idx = parent.children.index(target)
        if idx < len(parent.children) - 1:
            parent.children[idx], parent.children[idx + 1] = (
                parent.children[idx + 1],
                parent.children[idx],
            )
            self._save_outline_changes()

    def _update_ai_output(self, text: str) -> None:
        try:
            self.query_one("#lbl-ai-output", Static).update(text)
        except Exception:
            pass


class PromptModal(ModalScreen[str]):
    """A clean, styled modal prompt for text input."""

    def __init__(self, title: str, default_value: str = ""):
        super().__init__()
        self.dialog_title = title
        self.default_value = default_value

    def compose(self) -> ComposeResult:
        with Vertical(id="prompt-dialog"):
            yield Label(self.dialog_title, classes="prompt-title")
            yield Input(value=self.default_value, id="prompt-input")
            with Horizontal(classes="prompt-actions"):
                yield Button("💾 SAVE", variant="success", id="btn-save")
                yield Button("✖ CANCEL", variant="default", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#prompt-input", Input).focus()

    @on(Button.Pressed, "#btn-save")
    @on(Input.Submitted, "#prompt-input")
    def submit(self) -> None:
        val = self.query_one("#prompt-input", Input).value.strip()
        if val:
            self.dismiss(val)
        else:
            self.dismiss()

    @on(Button.Pressed, "#btn-cancel")
    def cancel(self) -> None:
        self.dismiss()


if __name__ == "__main__":
    OmniFormat().run()
