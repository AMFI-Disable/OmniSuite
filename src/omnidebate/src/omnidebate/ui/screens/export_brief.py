import os

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select, Static, Switch

from omnidebate.core.export import export_brief


class ExportBriefScreen(ModalScreen):
    """Modal screen for selecting template options and compiling debate briefs."""

    def __init__(self, motion_id: int, motion_name: str):
        super().__init__()
        self.motion_id = motion_id
        self.motion_name = motion_name

    def compose(self) -> ComposeResult:
        with Container(id="export-dialog"):
            yield Label(
                f"⚡ EXPORT STRATEGIC BRIEF: {self.motion_name.upper()}",
                classes="modal-title",
            )

            with Vertical(id="export-settings-body"):
                yield Label("Select Formatting Template:", classes="section-label")
                yield Select(
                    [
                        ("Verbatim (.docx)", "verbatim"),
                        ("CaseXC (.docx)", "casexc"),
                        ("Standard Brief (.md)", "markdown"),
                        ("Interactive HTML Brief (.html)", "interactive_html"),
                    ],
                    value="verbatim",
                    id="sel-template",
                    tooltip="Choose the document layout/format.",
                )

                with Horizontal(classes="settings-row"):
                    yield Label("Underline Taglines", classes="settings-label")
                    yield Switch(
                        value=True,
                        id="sw-underline",
                        tooltip="Underline card taglines in output.",
                    )

                with Horizontal(classes="settings-row"):
                    yield Label("Minimize Citations", classes="settings-label")
                    yield Switch(
                        value=False,
                        id="sw-minimize",
                        tooltip="Minimize citation details (Author & Year only).",
                    )

            with Horizontal(id="btn-row"):
                yield Button(
                    "🚀 Export",
                    variant="success",
                    id="btn-export",
                    tooltip="Compile and export document.",
                )
                yield Button(
                    "⚡ Open in OmniFormat",
                    variant="primary",
                    id="btn-open-format",
                    tooltip="Open the exported Markdown brief in OmniFormat.",
                )
                yield Button(
                    "✖ Cancel",
                    variant="error",
                    id="btn-cancel",
                    tooltip="Close dialog without exporting.",
                )

            yield Static("", id="export-status")

    def on_mount(self) -> None:
        self.query_one("#btn-open-format", Button).display = False

    @on(Button.Pressed, "#btn-cancel")
    def cancel(self) -> None:
        self.dismiss()

    @on(Button.Pressed, "#btn-open-format")
    def open_in_omniformat(self) -> None:
        if hasattr(self, "exported_file") and self.exported_file:
            import subprocess
            import sys

            from omnishared.config import get_workspace_path

            try:
                cmd = [
                    sys.executable,
                    get_workspace_path("omnisuite"),
                    "--app",
                    "format",
                    "--file",
                    self.exported_file,
                ]
                subprocess.Popen(cmd, start_new_session=True)
                try:
                    self.app.notify("⚡ Launching OmniFormat...", severity="info")
                except Exception:
                    pass
            except Exception as e:
                try:
                    self.app.notify(f"❌ Failed to launch OmniFormat: {e}", severity="error")
                except Exception:
                    pass
        self.dismiss()

    @on(Button.Pressed, "#btn-export")
    def run_export(self) -> None:
        btn = self.query_one("#btn-export", Button)
        if btn.label == "Close":
            self.dismiss()
            return

        template = self.query_one("#sel-template", Select).value
        underline = self.query_one("#sw-underline", Switch).value
        minimize = self.query_one("#sw-minimize", Switch).value

        # Select gives None if nothing is highlighted, but we pre-selected 'verbatim'
        if not template:
            template = "verbatim"

        self.query_one("#export-status", Static).update("⏳ Generating document brief...")

        try:
            out_file = export_brief(
                motion_id=self.motion_id,
                motion_name=self.motion_name,
                template=template,
                underline_taglines=underline,
                minimize_citations=minimize,
            )
            rel_path = os.path.relpath(out_file, start=os.getcwd())
            self.app.notify(f"✅ Brief compiled to: {rel_path}", severity="success")

            if template == "markdown":
                self.exported_file = os.path.abspath(out_file)
                self.query_one("#export-status", Static).update(
                    f"✅ Brief compiled successfully!\nFile: {rel_path}"
                )
                self.query_one("#btn-open-format", Button).display = True
                self.query_one("#btn-export", Button).label = "Close"
                self.query_one("#btn-cancel", Button).display = False
            else:
                self.dismiss()
        except Exception as e:
            self.query_one("#export-status", Static).update(f"❌ Error: {e}")
            self.app.notify(f"❌ Compilation failed: {e}", severity="error")
