import contextlib

from omnishared.ui.widgets import GaugeBar
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Markdown

from omnidebate.core.database import update_card
from omnidebate.core.oracle import OracleEngine


class CompareScreen(ModalScreen):
    """Side-by-Side Comparison of conflicting evidence cards with DB resolution controls."""

    def __init__(self, card_a: dict, card_b: dict):
        super().__init__()
        self.card_a = card_a
        self.card_b = card_b
        # Run comparative heuristics
        self.diagnostics = OracleEngine.weigh_evidence(self.card_a, self.card_b)

    def compose(self) -> ComposeResult:
        with Vertical(id="compare-container"):
            yield Label("⚔️  STRATEGIC CONFLICT RESOLUTION", id="compare-title")

            # Oracle Verdict Banner
            verdict_badge = self._get_verdict_badge()
            yield Label(verdict_badge, id="verdict-banner")

            with Horizontal(id="compare-panes-row"):
                # Left Pane: Card A
                with Vertical(classes="compare-pane", id="pane-card-a"):
                    yield Label(
                        f"📄 CARD A: {self.card_a['side']} (Tier {self.card_a.get('tier', 1)})",
                        classes="pane-header-label",
                    )
                    yield Markdown(self._fmt_card(self.card_a))

                    yield Label("📊 HEURISTIC METRICS:", classes="metrics-section-label")
                    yield GaugeBar(
                        label="RESILIENCE",
                        value=self.diagnostics["resilience_a"],
                        id="gauge-res-a",
                    )
                    yield GaugeBar(
                        label="WARRANT D.",
                        value=self.diagnostics["warrant_density_a"],
                        id="gauge-warr-a",
                    )
                    yield GaugeBar(
                        label="FACT SCORE",
                        value=self.diagnostics["fact_score_a"],
                        id="gauge-fact-a",
                    )

                    yield Label("🎯 CROSS-EXAM QUESTIONS:", classes="metrics-section-label")
                    cx_a = OracleEngine.generate_cx_questions(self.card_a)
                    for q in cx_a:
                        yield Label(f"• {q}", classes="cx-question-label")

                    yield Label("🛡️ REBUTTAL SPEECH BLOCK:", classes="metrics-section-label")
                    reb_a = OracleEngine.synthesize_rebuttal_block(self.card_a)
                    for r in reb_a:
                        if not r.startswith("#"):
                            yield Label(r, classes="rebuttal-block-label")

                # Right Pane: Card B
                with Vertical(classes="compare-pane", id="pane-card-b"):
                    yield Label(
                        f"📄 CARD B: {self.card_b['side']} (Tier {self.card_b.get('tier', 1)})",
                        classes="pane-header-label",
                    )
                    yield Markdown(self._fmt_card(self.card_b))

                    yield Label("📊 HEURISTIC METRICS:", classes="metrics-section-label")
                    yield GaugeBar(
                        label="RESILIENCE",
                        value=self.diagnostics["resilience_b"],
                        id="gauge-res-b",
                    )
                    yield GaugeBar(
                        label="WARRANT D.",
                        value=self.diagnostics["warrant_density_b"],
                        id="gauge-warr-b",
                    )
                    yield GaugeBar(
                        label="FACT SCORE",
                        value=self.diagnostics["fact_score_b"],
                        id="gauge-fact-b",
                    )

                    yield Label("🎯 CROSS-EXAM QUESTIONS:", classes="metrics-section-label")
                    cx_b = OracleEngine.generate_cx_questions(self.card_b)
                    for q in cx_b:
                        yield Label(f"• {q}", classes="cx-question-label")

                    yield Label("🛡️ REBUTTAL SPEECH BLOCK:", classes="metrics-section-label")
                    reb_b = OracleEngine.synthesize_rebuttal_block(self.card_b)
                    for r in reb_b:
                        if not r.startswith("#"):
                            yield Label(r, classes="rebuttal-block-label")

            # Footer with resolution buttons
            with Horizontal(classes="dashboard-footer", id="compare-footer"):
                yield Button("⭐ Prioritize Card A", variant="success", id="btn-prior-a")
                yield Button("⭐ Prioritize Card B", variant="error", id="btn-prior-b")
                yield Button("⚖️ Equalize (Tier 2)", variant="warning", id="btn-equalize")
                yield Button("✖ Cancel [ESC]", variant="primary", id="btn-close")

    def _get_verdict_badge(self) -> str:
        winner = self.diagnostics["winner"]
        diff = self.diagnostics["diff"]
        if winner == "A":
            return f"🟢 CARD A SUPERIOR (+{diff} points)"
        elif winner == "B":
            return f"🔴 CARD B SUPERIOR (+{diff} points)"
        else:
            return f"⚪ EVEN MATCH (Tie score: {self.diagnostics['score_a']})"

    def _fmt_card(self, c: dict) -> str:
        tag_str = c.get("tag", "").upper()
        cite_str = c.get("citation", "")
        text_str = c.get("text", "")
        return f"### {tag_str}\n**Cite:** {cite_str}\n\n{text_str}"

    @on(Button.Pressed, "#btn-prior-a")
    def prioritize_card_a(self) -> None:
        """Promote A's tier to 3 and demote B's tier to 1."""
        self.card_a["tier"] = 3
        self.card_b["tier"] = 1
        update_card(self.card_a["id"], self.card_a)
        update_card(self.card_b["id"], self.card_b)
        with contextlib.suppress(Exception):
            self.app.notify(
                f"Resolved: Promoted {self.card_a['tag']} to Tier 3, demoted {self.card_b['tag']} to Tier 1.",
                severity="success",
            )
        self.dismiss(True)

    @on(Button.Pressed, "#btn-prior-b")
    def prioritize_card_b(self) -> None:
        """Promote B's tier to 3 and demote A's tier to 1."""
        self.card_a["tier"] = 1
        self.card_b["tier"] = 3
        update_card(self.card_a["id"], self.card_a)
        update_card(self.card_b["id"], self.card_b)
        with contextlib.suppress(Exception):
            self.app.notify(
                f"Resolved: Promoted {self.card_b['tag']} to Tier 3, demoted {self.card_a['tag']} to Tier 1.",
                severity="success",
            )
        self.dismiss(True)

    @on(Button.Pressed, "#btn-equalize")
    def equalize_tiers(self) -> None:
        """Set both card tiers to 2."""
        self.card_a["tier"] = 2
        self.card_b["tier"] = 2
        update_card(self.card_a["id"], self.card_a)
        update_card(self.card_b["id"], self.card_b)
        with contextlib.suppress(Exception):
            self.app.notify("Resolved: Equalized both cards to Tier 2.", severity="info")
        self.dismiss(True)

    @on(Button.Pressed, "#btn-close")
    def close(self) -> None:
        self.dismiss(False)
