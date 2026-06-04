from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, Label
from textual.containers import Vertical


class SplashScreen(ModalScreen):
    """Premium Hollywood-style splash screen boot sequence for OmniDebate."""

    LOGO = r"""
 ██████╗ ███╗   ███╗███╗   ██╗██╗██████╗ ███████╗██████╗  █████╗ ████████╗███████╗
██╔═══██╗████╗ ████║████╗  ██║██║██╔══██╗██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██╔════╝
██║   ██║██╔████╔██║██╔██╗ ██║██║██║  ██║█████╗  ██████╔╝███████║   ██║   █████╗  
██║   ██║██║╚██╔╝██║██║╚██╗██║██║██║  ██║██╔══╝  ██╔══██╗██╔══██║   ██║   ██╔══╝  
╚██████╔╝██║ ╚═╝ ██║██║ ╚████║██║██████╔╝███████╗██████╔╝██║  ██║   ██║   ███████╗
 ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝╚═════╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝
"""

    def compose(self) -> ComposeResult:
        with Vertical(id="splash-container"):
            yield Static(self.LOGO, id="splash-logo")
            yield Label("OMNIDEBATE v1.0.0 — DEBATE COMMAND CENTER", id="splash-status")
            yield Label(
                "[ SYSTEM ] Booting protocol initialized...", id="splash-log-line"
            )
            yield Label(
                "BOOT LOAD: [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0%",
                id="splash-bar",
            )
            yield Label(
                "© 2026 OmniSuite. Built for the Digital Grandmaster.",
                id="splash-footer",
            )

    def on_mount(self) -> None:
        self.set_timer(2.0, self.exit_splash)
        self._progress = 0
        self.set_interval(0.04, self._update_progress)

    def _update_progress(self) -> None:
        self._progress += 2
        if self._progress <= 100:
            filled = int(self._progress / 100 * 40)
            bar = "█" * filled + "░" * (40 - filled)
            self.query_one("#splash-bar", Label).update(
                f"BOOT LOAD: [{bar}] {self._progress}%"
            )

            # Hollywood-style cyber decryption & boot sequence log timeline
            logs = {
                0: "[ DECRYPT ] Initializing digital handshake protocol...",
                4: "[ DECRYPT ] Shaking encryption keys (AES-256-GCM)...",
                8: "[ DECRYPT ] Handshake established. Access credentials read.",
                12: "[ SECURITY ] Clearance verified: GRANDMASTER (LEVEL 5) APPROVED.",
                16: "[ DATABASE ] Connecting SQLite Neural Vault core...",
                20: "[ DATABASE ] Ingesting 10 active debate motions...",
                24: "[ DATABASE ] Ingesting 100 high-density forensic cards...",
                28: "[ DATABASE ] Rebuilding Full-Text Search (FTS5) indexes...",
                32: "[ DATABASE ] Integrity audit: 0 vulnerabilities found.",
                36: "[ ORACLE ] Booting heuristic strategy analysis pipeline...",
                40: "[ ORACLE ] Calibrating semantic concept vector mappings...",
                44: "[ ORACLE ] Syncing victory-road prediction weights...",
                48: "[ ORACLE ] Neural SPAR model calibration complete.",
                52: "[ COCKPIT ] Synthesizing 5-zone tactical workspace layout...",
                60: "[ COCKPIT ] Applying high-contrast theme layout configurations...",
                68: "[ COCKPIT ] Initializing speech prep countdown widgets...",
                72: "[ COCKPIT ] Syncing active round state control HUD...",
                76: "[ COCKPIT ] Registering clipboard copy action listeners...",
                80: "[ SYSTEM ] Running complete system diagnostic check...",
                84: "[ SYSTEM ] All systems nominal. Preparing main viewport...",
                88: "[ SYSTEM ] Launching OmniDebate Strategic Cockpit...",
                92: "[ SYSTEM ] Cockpit fully online.",
                96: "> WELCOME BACK, GRANDMASTER.",
            }

            msg = logs[0]
            for pct in sorted(logs.keys()):
                if self._progress >= pct:
                    msg = logs[pct]

            self.query_one("#splash-log-line", Label).update(msg)

    def exit_splash(self) -> None:
        self.dismiss()
