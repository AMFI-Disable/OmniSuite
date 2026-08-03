from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Static


class SplashScreen(ModalScreen):
    """Premium Hollywood-style ASCII Splash Screen for OmniFormat."""

    LOGO = r"""
 ██████╗ ███╗   ███╗███╗   ██╗██╗███████╗ ██████╗ ██████╗ ███╗   ███╗ █████╗ ████████╗
██╔═══██╗████╗ ████║████╗  ██║██║██╔════╝██╔═══██╗██╔══██╗████╗ ████║██╔══██╗╚══██╔══╝
██║   ██║██╔████╔██║██╔██╗ ██║██║█████╗  ██║   ██║██████╔╝██╔████╔██║███████║   ██║   
██║   ██║██║╚██╔╝██║██║╚██╗██║██║██╔══╝  ██║   ██║██╔══██╗██║╚██╔╝██║██╔══██║   ██║   
╚██████╔╝██║ ╚═╝ ██║██║ ╚████║██║██║     ╚██████╔╝██║  ██║██║ ╚═╝ ██║██║  ██║   ██║   
 ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   
    """

    def compose(self) -> ComposeResult:
        yield Static(self.LOGO, id="splash-logo")
        yield Label("OMNIFORMAT v1.0.0", id="splash-loading")
        yield Label("░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░", id="splash-bar")
        yield Label("© 2026 OmniSuite. Built for the Digital Grandmaster.", id="splash-footer")

    def on_mount(self) -> None:
        self.set_timer(2.5, self.exit_splash)
        self._progress = 0
        self.set_interval(0.05, self._update_progress)

    def _update_progress(self) -> None:
        self._progress += 5
        if self._progress <= 100:
            filled = int(self._progress / 100 * 40)
            bar = "█" * filled + "░" * (40 - filled)
            self.query_one("#splash-bar", Label).update(bar)

            steps = [
                "🎬 A DIGITAL GRANDMASTER PRODUCTION...",
                "⚡ MOUNTING MARKDOWN LEXICAL PARSER...",
                "🔍 SYNCING DOCUMENT STYLE COMPLIANCE MATRIX...",
                "✨ COMPILING STYLESHEETS & TELEMETRY MODULES...",
                "🚀 OMNIFORMAT WORKSTATION ENGAGED.",
            ]
            step_idx = min(int(self._progress / 20), len(steps) - 1)
            self.query_one("#splash-loading", Label).update(steps[step_idx])

    def exit_splash(self) -> None:
        self.dismiss()
