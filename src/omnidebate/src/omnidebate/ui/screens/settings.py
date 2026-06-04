from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select, Switch, Input


class SettingsScreen(ModalScreen):
    """Interactive Settings with Multi-Palette support."""

    def __init__(self, config: dict, formats: list):
        super().__init__()
        self.config = config
        self.formats = formats

    def compose(self) -> ComposeResult:
        ui_cfg = self.config.get("ui", {})
        timer_cfg = self.config.get("timer", {}).get("default_format", "Public Forum")
        palette = ui_cfg.get("palette", "emerald")
        auto_snap = self.config.get("export", {}).get("auto_snapshot", True)
        user_name = self.config.get("user", {}).get("name", "")
        ai_cfg = self.config.get("ai", {})
        ollama_ep = ai_cfg.get("ollama_endpoint", "http://localhost:11434")
        ollama_md = ai_cfg.get("ollama_model", "llama3")
        screen_reader = ui_cfg.get("screen_reader_mode", False)

        with Vertical(id="settings-container"):
            yield Label("⚙️  SYSTEM CONFIGURATION", id="settings-title")

            with Horizontal(classes="settings-row"):
                yield Label("Visual Palette", classes="settings-label")
                yield Select(
                    [
                        ("Emerald Midnight", "emerald"),
                        ("Arctic Blue", "arctic"),
                        ("Volcano Red", "volcano"),
                        ("High Contrast (WCAG)", "high-contrast"),
                    ],
                    value=palette,
                    id="sel-palette",
                    tooltip="Change the application's color theme.",
                )

            with Horizontal(classes="settings-row"):
                yield Label("Default Format", classes="settings-label")
                yield Select(
                    [(f, f) for f in self.formats],
                    value=timer_cfg,
                    id="sel-def-format",
                    tooltip="Default debate format for timers.",
                )

            with Horizontal(classes="settings-row"):
                yield Label("Auto-Snapshot", classes="settings-label")
                yield Switch(
                    value=auto_snap,
                    id="sw-auto-snap",
                    tooltip="Automatically backup the database on export.",
                )

            with Horizontal(classes="settings-row"):
                yield Label("Screen Reader Mode", classes="settings-label")
                yield Switch(
                    value=screen_reader,
                    id="sw-screen-reader",
                    tooltip="Enable linear layout for better screen reader support.",
                )

            with Horizontal(classes="settings-row"):
                yield Label("User Name (Briefs)", classes="settings-label")
                yield Input(
                    value=user_name,
                    placeholder="Your Name",
                    id="in-user-name",
                    tooltip="Name appearing on forensic briefs.",
                )

            yield Label(
                "🤖 AI Configuration (Ollama Local)",
                classes="settings-label",
                id="ai-header",
            )

            with Horizontal(classes="settings-row"):
                yield Label("Endpoint URL", classes="settings-label")
                yield Input(
                    value=ollama_ep,
                    placeholder="http://localhost:11434",
                    id="in-ollama-ep",
                    tooltip="API endpoint for local Ollama server.",
                )

            with Horizontal(classes="settings-row"):
                yield Label("Model Name", classes="settings-label")
                yield Input(
                    value=ollama_md,
                    placeholder="llama3",
                    id="in-ollama-md",
                    tooltip="Local AI model name (e.g., llama3, mistral).",
                )

            with Horizontal(id="settings-btns"):
                yield Button(
                    "SAVE CHANGES",
                    variant="success",
                    id="btn-save",
                    tooltip="Save all changes to config.yaml",
                )
                yield Button(
                    "CANCEL",
                    variant="default",
                    id="btn-cancel",
                    tooltip="Discard changes and return.",
                )

    @on(Button.Pressed, "#btn-save")
    def save(self) -> None:
        new_config = {
            "timer": {
                "default_format": self.query_one("#sel-def-format", Select).value
            },
            "ui": {
                "palette": self.query_one("#sel-palette", Select).value,
                "screen_reader_mode": self.query_one("#sw-screen-reader", Switch).value,
            },
            "export": {"auto_snapshot": self.query_one("#sw-auto-snap", Switch).value},
            "user": {"name": self.query_one("#in-user-name", Input).value},
            "ai": {
                "ollama_endpoint": self.query_one("#in-ollama-ep", Input).value,
                "ollama_model": self.query_one("#in-ollama-md", Input).value,
            },
        }
        self.dismiss(new_config)

    @on(Button.Pressed, "#btn-cancel")
    def cancel(self) -> None:
        self.dismiss(None)
