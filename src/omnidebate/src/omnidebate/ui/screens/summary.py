from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Markdown, Label
from textual.containers import Vertical, ScrollableContainer
from omnidebate.core.database import read_vault
from omnidebate.core.oracle import OracleEngine


class SynthesisScreen(ModalScreen):
    """Phase 2500: Automated Strategic Briefing Engine."""

    def __init__(self, motion_id: int, motion_name: str):
        super().__init__()
        self.motion_id = motion_id
        self.motion_name = motion_name

    def compose(self) -> ComposeResult:
        with Vertical(id="synth-dialog"):
            yield Label(
                f"📄 STRATEGIC SYNTHESIS: {self.motion_name}", classes="synth-header"
            )
            yield ScrollableContainer(Markdown(id="synth-md"))
            yield Button("CLOSE [ESC]", id="btn-close", variant="error")

    def on_mount(self) -> None:
        cards = read_vault(self.motion_id)
        aff = [c for c in cards if c["side"] == "AFF"]
        neg = [c for c in cards if c["side"] == "NEG"]

        brief = f"# STRATEGIC BRIEF: {self.motion_name}\n\n"
        brief += f"## 📊 FORCE MULTIPLIERS\n- **AFF STRENGTH:** {len(aff)} Cards\n- **NEG STRENGTH:** {len(neg)} Cards\n\n"

        brief += "## ⚔️ CRITICAL CLASH POINTS\n"
        # Intelligent Synthesis Logic
        for a_card in aff[:3]:
            clashes = OracleEngine.detect_clash(a_card, neg)
            if clashes:
                brief += f"### {a_card['tag']}\n- **OPPOSITION:** {clashes[0]['tag']}\n"

        brief += "\n\n---\n© 2026 OmniSuite. Built for the Digital Grandmaster."

        self.query_one("#synth-md", Markdown).update(brief)

    @on(Button.Pressed, "#btn-close")
    def close_synth(self) -> None:
        self.dismiss()
