from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

from omnidebate.core.database import add_motion, rename_motion


class AddMotionScreen(ModalScreen):
    """Modal for creating or renaming a debate motion."""

    def __init__(self, motion_id: Optional[int] = None, current_name: str = ""):
        super().__init__()
        self.motion_id = motion_id
        self.current_name = current_name

    def compose(self) -> ComposeResult:
        with Container(id="motion-dialog"):
            yield Label("🗂️ " + ("Rename Motion" if self.motion_id else "Create New Motion"))
            yield Input(
                value=self.current_name,
                placeholder="e.g. Universal Basic Income",
                id="inp-motion-name",
            )
            with Horizontal(id="btn-row"):
                yield Button(
                    "✅ Save" if self.motion_id else "✅ Create",
                    variant="success",
                    id="btn-ok",
                )
                yield Button("✖ Cancel", variant="error", id="btn-cancel")

    @on(Button.Pressed, "#btn-cancel")
    def cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-ok")
    def save(self) -> None:
        name = self.query_one("#inp-motion-name", Input).value.strip()
        if not name:
            self.app.notify("Motion name cannot be empty.", severity="warning")
            return

        if self.motion_id:
            rename_motion(self.motion_id, name)
            self.dismiss(self.motion_id)
        else:
            motion_id = add_motion(name)
            self.dismiss(motion_id)


class ConfirmDeleteScreen(ModalScreen):
    """Modal for confirming deletion of a debate motion."""

    def __init__(self, name: str):
        super().__init__()
        self.motion_name = name

    def compose(self) -> ComposeResult:
        with Container(id="motion-dialog"):
            yield Label(f"⚠️ Are you sure you want to delete motion '{self.motion_name}'?")
            yield Label("This will permanently delete all evidence cards in this motion.")
            with Horizontal(id="btn-row"):
                yield Button("🗑️ Delete", variant="error", id="btn-confirm")
                yield Button("✖ Cancel", variant="default", id="btn-cancel")

    @on(Button.Pressed, "#btn-cancel")
    def cancel(self) -> None:
        self.dismiss(False)

    @on(Button.Pressed, "#btn-confirm")
    def confirm(self) -> None:
        self.dismiss(True)
