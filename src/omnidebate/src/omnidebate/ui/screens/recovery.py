from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Button, DataTable
from textual.containers import Vertical, Horizontal
import os
import shutil
from omnishared.config import BACKUPS_DIR
from omnishared.database import get_db_path


class RecoveryScreen(ModalScreen):
    """Database Backup & Snapshot Manager."""

    def compose(self) -> ComposeResult:
        with Vertical(id="recovery-dialog"):
            yield Label("🗄️  DATABASE SNAPSHOT MANAGER", id="recovery-title")
            yield DataTable(id="backup-table")
            with Horizontal(classes="dashboard-footer"):
                yield Button("RESTORE SELECTED", variant="success", id="btn-restore")
                yield Button("CLOSE [ESC]", variant="primary", id="btn-close")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("DATE/TIME", "FILENAME", "SIZE")

        if not os.path.exists(BACKUPS_DIR):
            return

        backups = sorted(os.listdir(BACKUPS_DIR), reverse=True)
        for b in backups:
            if not b.endswith(".bak"):
                continue
            path = os.path.join(BACKUPS_DIR, b)
            size = os.path.getsize(path) / 1024
            date = b.replace("vault_", "").replace(".db.bak", "")
            table.add_row(date, b, f"{size:.1f} KB")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close":
            self.dismiss()
        elif event.button.id == "btn-restore":
            table = self.query_one(DataTable)
            if table.cursor_row is not None:
                row = table.get_row_at(table.cursor_row)
                fname = row[1]
                self._restore(fname)

    def _restore(self, fname: str) -> None:
        src = os.path.join(BACKUPS_DIR, fname)
        dst = get_db_path()
        shutil.copy2(src, dst)
        self.app.notify(
            f"Database restored from {fname}! Restarting...", severity="success"
        )
        self.app.exit()
