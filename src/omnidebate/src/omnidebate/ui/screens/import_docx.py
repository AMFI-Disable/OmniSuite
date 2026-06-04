import os
import datetime
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

from omnidebate.core.database import add_card
from omnidebate.core.logic import parse_verbatim_docx, DOCX_OK


class DocxIngestScreen(ModalScreen):
    """Import debate cards from a Verbatim/CaseXC .docx file."""

    def __init__(self, motion_id: int):
        super().__init__()
        self.motion_id = motion_id

    def compose(self) -> ComposeResult:
        with Container(id="di-dialog"):
            yield Label("📂 DOCX Import (Verbatim/CaseXC)")
            yield Label("Enter absolute path to .docx file:")
            yield Input(
                placeholder="/path/to/evidence.docx",
                id="di-path",
                tooltip="Full system path to the .docx file.",
            )
            with Horizontal():
                yield Button(
                    "🚀 Import",
                    variant="success",
                    id="di-import",
                    tooltip="Parse and import all cards from the document.",
                )
                yield Button(
                    "✖ Cancel",
                    variant="error",
                    id="di-cancel",
                    tooltip="Close without importing.",
                )
            yield Static("", id="di-status")

    @on(Button.Pressed, "#di-cancel")
    def cancel(self) -> None:
        self.dismiss(False)

    @on(Button.Pressed, "#di-import")
    def run_import(self) -> None:
        if not DOCX_OK:
            self.app.notify("python-docx is not installed.", severity="error")
            return

        path = self.query_one("#di-path", Input).value.strip()
        if not path or not os.path.exists(path):
            self.app.notify("Invalid file path.", severity="warning")
            return

        self.query_one("#di-status", Static).update("⏳ Parsing document...")

        try:
            cards = parse_verbatim_docx(path)
            if not cards:
                self.app.notify("No cards detected in document.", severity="warning")
                self.dismiss(False)
                return

            today = datetime.date.today().strftime("%Y-%m-%d")
            for c in cards:
                c["timestamp"] = today
                add_card(self.motion_id, c)

            self.app.notify(f"✅ Imported {len(cards)} cards!", severity="information")
            self.dismiss(True)
        except Exception as e:
            self.query_one("#di-status", Static).update(f"❌ Error: {e}")
