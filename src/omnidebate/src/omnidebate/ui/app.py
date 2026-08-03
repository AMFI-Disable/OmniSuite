"""OmniDebate v1.0.0 — Strategic Research Workstation.

The central application controller for the OmniDebate Intelligence Workstation.
Orchestrates the 4-Zone tactical UI, Strategic Oracle, and forensic analysis engine.

© 2026 OmniSuite. Built for the Digital Grandmaster.
"""

import importlib.resources
import logging
from typing import Optional

from omnishared.config import load_config, run_setup_dirs
from omnishared.formats import load_formats
from omnishared.ui.widgets import (
    GaugeBar,
    QuickNotes,
    SystemLog,
)
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Collapsible,
    Footer,
    Input,
    Label,
    ListItem,
    ListView,
    Markdown,
    Static,
    Tab,
    Tabs,
)

from omnidebate.core.database import (
    delete_card,
    delete_motion,
    increment_mastery,
    list_motions,
    read_vault,
    update_card,
)
from omnidebate.core.oracle import OracleEngine
from omnidebate.ui.screens.actions import CardActionScreen
from omnidebate.ui.screens.analytics import AnalyticsScreen
from omnidebate.ui.screens.cards import AddCardScreen
from omnidebate.ui.screens.compare import CompareScreen
from omnidebate.ui.screens.drill import DrillScreen
from omnidebate.ui.screens.export_brief import ExportBriefScreen
from omnidebate.ui.screens.help import HelpScreen
from omnidebate.ui.screens.impacts import ImpactMapScreen
from omnidebate.ui.screens.import_docx import DocxIngestScreen
from omnidebate.ui.screens.ingest import WebIngestScreen
from omnidebate.ui.screens.motions import AddMotionScreen, ConfirmDeleteScreen
from omnidebate.ui.screens.palette import CommandPaletteScreen

# Import screens
from omnidebate.ui.screens.search import SearchScreen
from omnidebate.ui.screens.settings import SettingsScreen
from omnidebate.ui.screens.speech import SpeechPrepScreen
from omnidebate.ui.screens.splash import SplashScreen
from omnidebate.ui.screens.summary import SynthesisScreen
from omnidebate.ui.widgets.command_hud import CommandHUD

# ─── Audit Registry: Maps action names to Oracle functions ───
# This replaces 15+ copy-paste methods with a single parametric dispatcher.
AUDIT_REGISTRY: dict[str, dict] = {
    "PERSUASION": {
        "emoji": "🎭",
        "metric": "RHETORICAL STRENGTH",
        "fn": "analyze_persuasion",
        "high": "Strong Rhetorical Foundation: Evidence-anchored persuasion.",
        "low": "Rhetorical Weakness: Consider reinforcing claim-warrant connectivity.",
    },
    "IMMERSION": {
        "emoji": "🌊",
        "metric": "NARRATIVE STRENGTH",
        "fn": "analyze_immersion",
        "high": "High Emotional Resonance: Terminal impact scenario is vivid.",
        "low": "Strategic Dryness: Consider adding more descriptive warrants.",
    },
    "MASTERY": {
        "emoji": "🎓",
        "metric": "STRATEGIC ALIGNMENT",
        "fn": "analyze_mastery",
        "high": "Absolute Link-Connectivity: Core win-condition piece.",
        "low": "Strategic Gap: Re-align this card's tag with the terminal impact.",
    },
    "WARRANTS": {
        "emoji": "⚖️",
        "metric": "LOGICAL DENSITY",
        "fn": "analyze_warrants",
        "high": "High Causal Density: Strong link-chain structural integrity.",
        "low": "Logical Leap Detected: Consider adding more bridge-warrants.",
    },
    "FORENSICS": {
        "emoji": "🔬",
        "metric": "DEFENSIVE STRENGTH",
        "fn": "analyze_forensics",
        "high": "High Empirical Grounding: Strong cross-ex resilience.",
        "low": "Forensic Vulnerability: Evidence may be rhetorically brittle.",
    },
    "IMPACTS": {
        "emoji": "💥",
        "metric": "TERMINAL SEVERITY",
        "fn": "analyze_impacts",
        "high": "High Magnitude: Terminal impact is structurally sound.",
        "low": "Low Magnitude: Re-weigh against more critical scenarios.",
    },
    "PROBABILITY": {
        "emoji": "🎲",
        "metric": "TRUTH-LEVEL",
        "fn": "analyze_probability",
        "high": "High Likelihood: Link-chain is empirically probable.",
        "low": "Probability Gap: Reinforce with more likelihood-warrants.",
    },
    "TIMELINE": {
        "emoji": "⏳",
        "metric": "URGENCY",
        "fn": "analyze_timeline",
        "high": "High Urgency: Terminal impact is imminent.",
        "low": "Delayed Impact: Re-align with short-term scenarios.",
    },
    "RISK": {
        "emoji": "🛡️",
        "metric": "TURN-PROBABILITY",
        "fn": "analyze_risk",
        "high": "High Defensive Stability: Low probability of link-turn.",
        "low": "Strategic Exposure: Reinforce with link-defense.",
    },
    "EVIDENCE": {
        "emoji": "📄",
        "metric": "FACT-LEVEL STRENGTH",
        "fn": "analyze_evidence",
        "high": "Strong Empirical Foundation: Factually anchored.",
        "low": "Rhetorical Overclaim: Reinforce with more data-points.",
    },
    "ARGUMENT": {
        "emoji": "🧩",
        "metric": "LOGIC-LEVEL STRENGTH",
        "fn": "analyze_argument",
        "high": "Strong Structural Connectivity: Logically anchored.",
        "low": "Structural Gap: Reinforce with more causal bridges.",
    },
    "VICTORY": {
        "emoji": "🏆",
        "metric": "BALLOT-LEVEL STRENGTH",
        "fn": "analyze_victory",
        "high": "High Ballot Impact: Core win-condition anchor piece.",
        "low": "Low Ballot Impact: Align with more terminal RFD markers.",
    },
    "SINGULARITY": {
        "emoji": "🌌",
        "metric": "RESOLUTION VELOCITY",
        "fn": "analyze_singularity",
        "high": "Absolute Win-Condition: Terminal resolution reached.",
        "low": "Partial Resolution: Reinforce with more absolute warrants.",
    },
    "SYNERGY": {
        "emoji": "🌐",
        "metric": "CROSS-MOTION CONNECTIVITY",
        "fn": "analyze_synergy",
        "high": "High Global Synergy: Terminal cross-motion bridge.",
        "low": "Partial Synergy: Reinforce with more global link-ends.",
    },
    "NARRATIVE": {
        "emoji": "📜",
        "metric": "FRAMING-LEVEL CONNECTIVITY",
        "fn": "analyze_narrative",
        "high": "High Narrative Synergy: Terminal framing-level bridge.",
        "low": "Partial Narrative: Reinforce with more framing-level anchors.",
    },
    "IMPACT 2.0": {
        "emoji": "💥",
        "metric": "RESOLUTION VELOCITY 2.0",
        "fn": "analyze_impacts_2",
        "high": "High Resolution Probability: Terminal outcome actualized.",
        "low": "Partial Resolution: Reinforce with more outcome-level anchors.",
    },
    "LINGUISTICS": {
        "emoji": "📝",
        "metric": "CREDIBILITY SCORE",
        "fn": "analyze_linguistics",
        "high": "Active Voice: Strong claim-warrant connectivity.",
        "low": "Hedging Detected: Possible strategic vulnerability.",
    },
}


class OmniDebate(App):
    """The central controller for the OmniDebate Strategic Research Workstation."""

    TITLE = "OmniDebate v1.0.0"
    CSS_PATH = [
        str(importlib.resources.files("omnishared.ui").joinpath("tcss", "theme.tcss")),
        "omnidebate.tcss",
    ]

    BINDINGS = [
        Binding("q", "quit", "Exit"),
        Binding("f", "toggle_focus", "Focus Mode"),
        Binding("s", "toggle_speech", "Speech Mode"),
        Binding("r", "generate_rebuttal", "Rebuttal"),
        Binding("ctrl+t", "open_speech_prep", "Speech Prep Timer"),
        Binding("ctrl+k", "open_palette", "Omni-Search"),
        Binding("ctrl+d", "toggle_debug", "Debug Mode"),
        Binding("h", "show_help", "Help"),
        Binding("?", "show_help", "Help", show=False),
        Binding("n", "add_card", "Add Card", show=False),
        Binding("e", "edit_card", "Edit Card", show=False),
        Binding("delete", "delete_card", "Delete Card", show=False),
        Binding("w", "web_ingest", "Web Ingest", show=False),
        Binding("z", "open_synthesis", "Auto-Synthesize", show=False),
        Binding("a", "open_matrix", "Strategic Dashboard", show=False),
        Binding("i", "open_impact_map", "Impact Flow Map", show=False),
        Binding("d", "open_drill", "Prep Drill Arena", show=False),
        Binding("space", "toggle_active_speech", "Toggle Speech", show=False),
        Binding("p", "toggle_active_prep", "Toggle Prep", show=False),
        Binding("ctrl+p", "open_settings", "Settings", show=False),
        Binding("c", "compare_card", "Compare Card", show=False),
    ]

    active_motion_id = reactive(None)
    active_motion_name = reactive("None")
    focus_mode = reactive(False)
    speech_mode = reactive(False)
    debug_mode = reactive(False)

    def __init__(self):
        super().__init__()
        run_setup_dirs()
        self._config = load_config()
        self._formats = load_formats()
        self.active_card = None

    # ─────────────────────────────────────────────
    #  COMPOSE: 4-Zone Grid Layout
    # ─────────────────────────────────────────────
    def compose(self) -> ComposeResult:
        yield Static(
            "⏱️ CONTROL > 🏛️ MOTIONS > 🧬 EVIDENCE > 🧠 BRIEFING > 🔮 ANALYTICS",
            id="breadcrumb-bar",
        )

        with Horizontal(id="main-layout"):
            # ⏱️ Zone Epsilon: ROUND CONTROL
            yield CommandHUD(self._formats, id="zone-epsilon", classes="tactical-zone")

            # 🏛️ Zone Alpha: MOTION LIBRARY
            with Vertical(id="zone-alpha", classes="tactical-zone"):
                yield Label("[ 🏛️ MOTION LIBRARY ]", classes="zone-header")
                yield ListView(id="motion-list")
                with Vertical(classes="action-deck"):
                    yield Button(
                        "+ Motion",
                        id="btn-new-motion",
                        variant="success",
                        tooltip="Create a new debate motion",
                    )
                    yield Button(
                        "🗑️ Delete",
                        id="btn-del-motion",
                        variant="error",
                        tooltip="Delete the selected motion",
                    )

            # 🧬 Zone Beta: EVIDENCE NEXUS
            with Vertical(id="zone-beta", classes="tactical-zone"):
                yield Label("[ 🧬 EVIDENCE NEXUS ]", classes="zone-header")
                yield Input(
                    placeholder="Search...",
                    id="evidence-filter",
                    tooltip="Filter evidence within this motion",
                )
                with Horizontal(classes="filter-chips"):
                    yield Button(
                        "All",
                        id="filter-all",
                        variant="default",
                        tooltip="Show all cards",
                    )
                    yield Button(
                        "Aff",
                        id="filter-aff",
                        variant="success",
                        tooltip="Show affirmative cards only",
                    )
                    yield Button(
                        "Neg",
                        id="filter-neg",
                        variant="error",
                        tooltip="Show negative cards only",
                    )
                    yield Button(
                        "Top",
                        id="filter-top",
                        variant="primary",
                        tooltip="Show top priority cards",
                    )
                yield Static("EQUILIBRIUM: [-----|-----] 50%", id="balance-meter")
                yield ListView(id="evidence-list")
                with Vertical(id="nexus-actions"):
                    yield Button(
                        "+ Add Card",
                        id="fab-add",
                        variant="primary",
                        tooltip="Add a new evidence card manually",
                    )
                    yield Button(
                        "📂 Import DOCX",
                        id="fab-docx",
                        variant="success",
                        tooltip="Import evidence from a Verbatim .docx file",
                    )
                    yield Button(
                        "⚡ Export Brief",
                        id="fab-export",
                        variant="warning",
                        tooltip="Export/compile motion evidence cards to DOCX/HTML/MD",
                    )

            # 🧠 Zone Gamma: FORENSIC BRIEF
            with Vertical(id="zone-gamma", classes="tactical-zone"):
                yield Label("[ 🧠 FORENSIC BRIEF ]", classes="zone-header")
                yield Markdown("# SELECT EVIDENCE\nAudit required.", id="card-detail")
                with Horizontal(id="brief-actions-row"):
                    yield Button("📋 Copy Link", id="btn-copy-link", variant="primary")
                    yield Button("📄 Copy Content", id="btn-copy-content", variant="success")

            # 🔮 Zone Delta: STRATEGIC ORACLE
            with Vertical(id="zone-delta", classes="tactical-zone"):
                yield Label("[ 🔮 STRATEGIC ORACLE ]", classes="zone-header")

                yield Tabs(
                    Tab("STRAT", id="tab-strat"),
                    Tab("FORENSIC", id="tab-forensic"),
                    Tab("GLOBAL", id="tab-global"),
                    id="oracle-tabs",
                )

                with Vertical(id="hud-container"):
                    # Strategic Velocity (GaugeBar widgets)
                    with Vertical(id="hud-strat", classes="hud-group"):
                        yield Label("📈 STRATEGIC VELOCITY", classes="hud-group-label")
                        yield GaugeBar(label="TENSION", id="tension-bar")
                        yield GaugeBar(label="WEIGHT", id="weight-bar")
                        yield GaugeBar(label="CLARITY", id="clarity-bar")
                        yield GaugeBar(label="SINGULARITY", id="singularity-bar")
                        yield GaugeBar(label="VICTORY", id="victory-bar")
                        yield GaugeBar(label="STRAT RISK", id="risk-bar")

                    with Vertical(id="hud-forensic", classes="hud-group hidden"):
                        yield Label("⚖️ FORENSIC DENSITY", classes="hud-group-label")
                        yield GaugeBar(label="MASTERY", id="mastery-bar")
                        yield GaugeBar(label="WARRANTS", id="warrant-bar")
                        yield GaugeBar(label="EVIDENCE", id="evidence-bar")
                        yield GaugeBar(label="FORENSICS", id="forensic-bar")

                    with Vertical(id="hud-global", classes="hud-group hidden"):
                        yield Label("🌐 GLOBAL SYNERGY", classes="hud-group-label")
                        yield GaugeBar(label="SYNERGY", id="synergy-bar")
                        yield GaugeBar(label="NARRATIVE", id="narrative-bar")
                        yield GaugeBar(label="ARGUMENT", id="argument-bar")
                        yield GaugeBar(label="IMPACTS", id="impact-bar")
                        yield GaugeBar(label="PROBABILITY", id="probability-bar")
                        yield GaugeBar(label="TIMEFRAME", id="timeline-bar")
                        yield GaugeBar(label="IMPACT 2.0", id="impact2-bar")

                # 🎤 Collapsible Tactical Command
                with Collapsible(title="🎤 TACTICAL COMMAND", collapsed=False):
                    yield SystemLog()
                    yield Static("LOG: Ready.", id="timeline-log")

                # 📌 Collapsible Quick Notes
                with Collapsible(title="📌 QUICK NOTES", collapsed=True):
                    yield QuickNotes()

        yield Footer()

    # ─────────────────────────────────────────────
    #  LIFECYCLE
    # ─────────────────────────────────────────────
    def on_mount(self) -> None:
        self.call_after_refresh(lambda: self.push_screen(SplashScreen()))
        self._apply_accessibility_settings()
        self._reload_motions()

    def on_collapsible_expanded(self, event: Collapsible.Expanded) -> None:
        """Ensure accordion behavior where expanding one collapsible collapses others."""
        for collapsible in self.query(Collapsible):
            if collapsible != event.collapsible:
                collapsible.collapsed = True

    def on_resize(self, event) -> None:
        """Responsive grid breakpoint handler — adapts layout to terminal width."""
        try:
            w = event.size.width

            zones = {
                "epsilon": self.query_one("#zone-epsilon"),
                "alpha": self.query_one("#zone-alpha"),
                "delta": self.query_one("#zone-delta"),
            }

            if w >= 180:
                # Full 5-column cockpit
                for z in zones.values():
                    z.display = True
            elif w >= 140:
                # 4-column: hide oracle
                zones["delta"].display = False
                zones["epsilon"].display = True
                zones["alpha"].display = True
            elif w >= 110:
                # 3-column: hide oracle and control
                zones["delta"].display = False
                zones["epsilon"].display = False
                zones["alpha"].display = True
            elif w >= 80:
                # 2-column: evidence + brief only
                zones["alpha"].display = False
                zones["delta"].display = False
                zones["epsilon"].display = False
            # Below 80: Textual handles overflow scrolling
        except Exception:
            pass

    def _apply_accessibility_settings(self) -> None:
        """Applies High Contrast and Screen Reader layout modes dynamically."""
        ui_cfg = self._config.get("ui", {})
        palette = ui_cfg.get("palette", "")
        screen_reader = ui_cfg.get("screen_reader_mode", False)

        try:
            self.screen.set_class(palette == "high-contrast", "high-contrast")
        except Exception:
            pass

        try:
            layout = self.query_one("#main-layout")
            layout.set_class(screen_reader, "screen-reader-optimized")
            if screen_reader:
                self.notify("Screen Reader Mode: Linear Layout Active", severity="information")
        except Exception:
            pass

    # ─────────────────────────────────────────────
    #  DATA: Motion & Evidence Loading
    # ─────────────────────────────────────────────
    def _reload_motions(self) -> None:
        ml = self.query_one("#motion-list", ListView)
        ml.clear()
        for m in list_motions():
            cards = read_vault(m["id"])
            mastery = "★" * min(5, len(cards) // 5) if cards else "☆"
            ml.mount(ListItem(Label(f"{mastery} 📁 {m['name']}")))
            ml.children[-1]._motion_data = m

    @on(ListView.Highlighted, "#motion-list")
    def motion_selected(self, event: ListView.Highlighted) -> None:
        try:
            m = getattr(event.item, "_motion_data", None)
            if m:
                self.active_motion_id = m["id"]
                self.active_motion_name = m["name"]
                self._reload_evidence()
        except Exception as e:
            self._log_error(f"Motion selection failed - {e}")

    def _reload_evidence(self) -> None:
        """Refreshes the evidence list and real-time HUD with latest forensic metrics."""
        try:
            el = self.query_one("#evidence-list", ListView)
            el.clear()
            if not self.active_motion_id:
                return

            cards = read_vault(self.active_motion_id)

            # Apply Filter Chips Logic
            mode = getattr(self, "evidence_filter_mode", "ALL")
            if mode == "AFF":
                cards = [c for c in cards if c["side"] == "AFF"]
            elif mode == "NEG":
                cards = [c for c in cards if c["side"] == "NEG"]
            elif mode == "TOP":
                cards = sorted(cards, key=lambda x: x.get("tier", 3))[:10]

            # Live text filter
            try:
                query = self.query_one("#evidence-filter", Input).value.strip().lower()
                if query:
                    cards = [
                        c for c in cards if query in c["tag"].lower() or query in c["text"].lower()
                    ]
            except Exception:
                pass

            # Balance meter
            bal = OracleEngine.calculate_balance(cards)
            self._safe_update(
                "#balance-meter",
                f"BALANCE: [{'=' * (bal // 10)}{'-' * (10 - bal // 10)}] {bal}% AFF",
            )

            # Update all GaugeBar widgets via the Oracle engine
            self._update_gauge(
                "#weight-bar", OracleEngine.calculate_strategic_weight(cards), "WEIGHT"
            )
            self._update_gauge(
                "#tension-bar",
                OracleEngine.calculate_strategic_tension(cards),
                "TENSION",
            )
            self._update_gauge(
                "#clarity-bar", OracleEngine.calculate_master_clarity(cards), "CLARITY"
            )
            self._update_gauge(
                "#mastery-bar", OracleEngine.calculate_master_mastery(cards), "MASTERY"
            )
            self._update_gauge(
                "#warrant-bar",
                OracleEngine.calculate_master_warrants(cards),
                "WARRANTS",
            )
            self._update_gauge(
                "#forensic-bar",
                OracleEngine.calculate_master_forensics(cards),
                "FORENSICS",
            )
            self._update_gauge(
                "#impact-bar", OracleEngine.calculate_master_impacts(cards), "IMPACTS"
            )
            self._update_gauge(
                "#probability-bar",
                OracleEngine.calculate_master_probability(cards),
                "PROBABILITY",
            )
            self._update_gauge(
                "#timeline-bar",
                OracleEngine.calculate_master_timeline(cards),
                "TIMEFRAME",
            )
            self._update_gauge("#risk-bar", OracleEngine.calculate_master_risk(cards), "STRAT RISK")
            self._update_gauge(
                "#evidence-bar",
                OracleEngine.calculate_master_evidence(cards),
                "EVIDENCE",
            )
            self._update_gauge(
                "#argument-bar",
                OracleEngine.calculate_master_argument(cards),
                "ARGUMENT",
            )
            self._update_gauge(
                "#victory-bar", OracleEngine.calculate_master_victory(cards), "VICTORY"
            )
            self._update_gauge(
                "#singularity-bar",
                OracleEngine.calculate_master_singularity(cards),
                "SINGULARITY",
            )
            self._update_gauge(
                "#synergy-bar", OracleEngine.calculate_master_synergy(cards), "SYNERGY"
            )
            self._update_gauge(
                "#narrative-bar",
                OracleEngine.calculate_master_narrative(cards),
                "NARRATIVE",
            )
            self._update_gauge(
                "#impact2-bar",
                OracleEngine.calculate_master_impacts_2(cards),
                "IMPACT 2.0",
            )

            for c in cards:
                tier_class = f"tier-{c.get('tier', 3)}"
                side_class = "side-aff" if c["side"] == "AFF" else "side-neg"
                row = Vertical(
                    Label(c["tag"].upper(), classes=f"card-tag {tier_class}"),
                    Static(c["text"][:120] + "...", classes="card-body"),
                    classes=side_class,
                )
                li = ListItem(row, id=f"card-{c['id']}")
                li._card_data = c
                el.mount(li)

        except Exception as e:
            self._log_error(f"Refresh failed - {e}")

    # ─────────────────────────────────────────────
    #  CARD SELECTION & FORENSIC ANALYSIS
    # ─────────────────────────────────────────────
    @on(ListView.Selected, "#evidence-list")
    def card_selected(self, event: ListView.Selected) -> None:
        """Deep forensic analysis and report generation for selected evidence."""
        try:
            c = getattr(event.item, "_card_data", None)
            if not c:
                return
            self.active_card = c

            resilience = OracleEngine.calculate_resilience(c)
            fallacies = OracleEngine.detect_fallacies(c["text"])
            all_cards = read_vault(self.active_motion_id)
            clashes = OracleEngine.detect_clash(c, all_cards)
            cx_strategy = OracleEngine.generate_cx_strategy(c)
            rebuttals = OracleEngine.synthesize_rebuttal_block(c)
            weight = OracleEngine.calculate_strategic_weight([c])

            # ─── High-Density Forensic Summary ───
            audit_md = "### 🧬 FORENSIC SUMMARY\n"
            audit_md += "| METRIC | VALUE | STATUS |\n"
            audit_md += "| :--- | :---: | :---: |\n"
            audit_md += f"| **STRAT WEIGHT** | {weight}% | {'★' * min(5, weight // 20)} |\n"
            audit_md += f"| **RESILIENCE** | {resilience}% | {'🛡️' if resilience > 70 else '⚠️'} |\n"

            if fallacies:
                audit_md += f"\n> [!WARNING]\n> **FALLACY DETECTED:** {', '.join(fallacies)}\n"
            audit_md += "\n---\n"

            if clashes:
                clash = clashes[0]
                audit_md += f"### ⚔️ NEXUS CLASH\n**COUNTER:** {clash['tag']}\n> {clash['text'][:140]}...\n\n"

            audit_md += "### 🛡️ REBUTTAL BRIEF\n" + "\n".join([f"- {r}" for r in rebuttals])
            audit_md += "\n\n### 🎤 CX INTERROGATOR\n" + "\n".join([f"- {q}" for q in cx_strategy])

            detail = self.query_one("#card-detail", Markdown)
            redacted_text = OracleEngine.auto_redact_text(c["text"])

            report = f"# {c['tag'].upper()}\n"
            report += f"**CITATION:** {c.get('citation', 'Internal Vault')}\n\n"
            report += f"{redacted_text}\n\n"

            if not self.speech_mode:
                report += audit_md

            detail.update(report)
            increment_mastery(c["id"])

            self._safe_update(
                "#breadcrumb-bar",
                f"🏛️ {self.active_motion_name} > 🧬 {c['tag'].upper()} > 🧠 BRIEFED",
            )

            log_msg = OracleEngine.log_round_progression(c["id"], 0)
            self._safe_update("#timeline-log", log_msg)

        except Exception as e:
            self._log_error(f"Card selection failed - {e}")

    # ─────────────────────────────────────────────
    #  PARAMETRIC AUDIT ENGINE (replaces 17 methods)
    # ─────────────────────────────────────────────
    def _run_card_audit(self, audit_name: str) -> None:
        """Generic audit dispatcher — replaces 17 copy-paste action_analyze_* methods."""
        el = self.query_one("#evidence-list", ListView)
        if not el.highlighted_child:
            return
        c = getattr(el.highlighted_child, "_card_data", None)
        if not c:
            return

        cfg = AUDIT_REGISTRY.get(audit_name)
        if not cfg:
            return

        oracle_fn = getattr(OracleEngine, cfg["fn"], None)
        if not oracle_fn:
            return

        score = oracle_fn(c)
        analysis = cfg["high"] if score > 70 else cfg["low"]

        md = f"# {cfg['emoji']} {audit_name} AUDIT\n\n"
        md += f"**{cfg['metric']}: {score}%**\n\n"
        md += f"### 🧩 ANALYSIS\n- {analysis}\n"

        self.query_one("#card-detail", Markdown).update(md)
        self.toast(f"{audit_name} Audit: {score}%")

    # Generate action methods dynamically from the registry
    def action_analyze_persuasion(self) -> None:
        self._run_card_audit("PERSUASION")

    def action_analyze_immersion(self) -> None:
        self._run_card_audit("IMMERSION")

    def action_analyze_mastery(self) -> None:
        self._run_card_audit("MASTERY")

    def action_analyze_warrants(self) -> None:
        self._run_card_audit("WARRANTS")

    def action_analyze_forensics(self) -> None:
        self._run_card_audit("FORENSICS")

    def action_analyze_impacts(self) -> None:
        self._run_card_audit("IMPACTS")

    def action_analyze_probability(self) -> None:
        self._run_card_audit("PROBABILITY")

    def action_analyze_timeline(self) -> None:
        self._run_card_audit("TIMELINE")

    def action_analyze_risk(self) -> None:
        self._run_card_audit("RISK")

    def action_analyze_evidence(self) -> None:
        self._run_card_audit("EVIDENCE")

    def action_analyze_argument(self) -> None:
        self._run_card_audit("ARGUMENT")

    def action_analyze_victory(self) -> None:
        self._run_card_audit("VICTORY")

    def action_analyze_singularity(self) -> None:
        self._run_card_audit("SINGULARITY")

    def action_analyze_synergy(self) -> None:
        self._run_card_audit("SYNERGY")

    def action_analyze_narrative(self) -> None:
        self._run_card_audit("NARRATIVE")

    def action_analyze_impacts_2(self) -> None:
        self._run_card_audit("IMPACT 2.0")

    def action_analyze_linguistics(self) -> None:
        self._run_card_audit("LINGUISTICS")

    # ─────────────────────────────────────────────
    #  ACTIONS: Focus, Speech, Navigation
    # ─────────────────────────────────────────────
    def action_toggle_focus(self) -> None:
        """Toggles Focus Mode: Hides Navigator, Controls and Oracle to maximize briefing space."""
        self.focus_mode = not self.focus_mode
        for zid in ["#zone-epsilon", "#zone-alpha", "#zone-beta", "#zone-delta"]:
            try:
                self.query_one(zid).display = not self.focus_mode
            except Exception:
                pass
        self.toast(f"Focus Mode: {'ENABLED' if self.focus_mode else 'DISABLED'}")

    def action_toggle_speech(self) -> None:
        """Toggles Active Speech Mode: Maximizes readability for performance."""
        self.speech_mode = not self.speech_mode
        gamma = self.query_one("#zone-gamma")
        gamma.set_class(self.speech_mode, "speech-mode")

        if self.speech_mode:
            if not self.focus_mode:
                self.action_toggle_focus()
            self.notify("ACTIVE SPEECH MODE: PERFORMANCE HUD ONLINE", severity="warning")
        else:
            if self.focus_mode:
                self.action_toggle_focus()
            self.notify("Speech Mode Disabled", severity="information")

    def action_toggle_debug(self) -> None:
        """Toggles the Forensic Debug Overlay and logs internal telemetry."""
        self.debug_mode = not self.debug_mode
        state = "ENABLED" if self.debug_mode else "DISABLED"

        logging.basicConfig(filename="omni_forensics.log", level=logging.DEBUG)
        logging.debug(f"DEBUG {state}: Heuristic Indices Snapshot")

        try:
            logger = self.query_one(SystemLog)
            logger.log_activity(f"DEBUG MODE: {state}")
            if self.debug_mode:
                logger.log_activity("> Dumping Heuristic Core...")
                self.notify("Forensic Debug Mode Active", severity="warning")
        except Exception:
            pass

    @on(Tabs.TabActivated, "#oracle-tabs")
    def handle_oracle_tabs(self, event: Tabs.TabActivated) -> None:
        """Switch between HUD groups based on the active tab."""
        for gid in ["#hud-strat", "#hud-forensic", "#hud-global"]:
            self.query_one(gid).add_class("hidden")

        tab_map = {
            "tab-strat": "#hud-strat",
            "tab-forensic": "#hud-forensic",
            "tab-global": "#hud-global",
        }
        if event.tab.id in tab_map:
            self.query_one(tab_map[event.tab.id]).remove_class("hidden")

    # ─────────────────────────────────────────────
    #  FILTER CHIPS
    # ─────────────────────────────────────────────
    @on(Button.Pressed, "#filter-all")
    def filter_all(self) -> None:
        self.evidence_filter_mode = "ALL"
        self._reload_evidence()

    @on(Button.Pressed, "#filter-aff")
    def filter_aff(self) -> None:
        self.evidence_filter_mode = "AFF"
        self._reload_evidence()

    @on(Button.Pressed, "#filter-neg")
    def filter_neg(self) -> None:
        self.evidence_filter_mode = "NEG"
        self._reload_evidence()

    @on(Button.Pressed, "#filter-top")
    def filter_top(self) -> None:
        self.evidence_filter_mode = "TOP"
        self._reload_evidence()

    @on(Input.Changed, "#evidence-filter")
    def filter_input_changed(self, event: Input.Changed) -> None:
        self._reload_evidence()

    # ─────────────────────────────────────────────
    #  STRATEGIC ACTIONS: Synthesis, Rebuttal, etc.
    # ─────────────────────────────────────────────
    def action_open_synthesis(self) -> None:
        """Open the Automated Briefing and Research Synthesis Engine."""
        if not self.active_motion_id:
            self.toast("Select a motion to synthesize.")
            return
        self.push_screen(SynthesisScreen(self.active_motion_id, self.active_motion_name))

    def action_open_palette(self) -> None:
        """Open the Global Search Palette for rapid cross-vault navigation."""
        self.push_screen(CommandPaletteScreen(), callback=self.handle_palette_select)

    @on(Button.Pressed, "#fab-docx")
    def action_import_docx(self) -> None:
        """Open the DOCX Import Modal."""
        if not self.active_motion_id:
            self.notify("Select a motion first.", severity="warning")
            return
        self.push_screen(
            DocxIngestScreen(self.active_motion_id), callback=self.handle_docx_callback
        )

    @on(Button.Pressed, "#fab-export")
    def action_export_brief(self) -> None:
        """Open the Export Brief Modal."""
        if not self.active_motion_id:
            self.notify("Select a motion first.", severity="warning")
            return
        self.push_screen(ExportBriefScreen(self.active_motion_id, self.active_motion_name))

    def handle_docx_callback(self, success: bool) -> None:
        if success:
            self._reload_evidence()

    # ─────────────────────────────────────────────
    #  UI INTERACTIONS: Help, Motions, Cards, etc.
    # ─────────────────────────────────────────────
    def action_show_help(self) -> None:
        """Open the Help & Shortcut HUD modal."""
        self.push_screen(HelpScreen())

    def action_new_motion(self) -> None:
        """Open the New Motion creation modal."""
        self.push_screen(AddMotionScreen(), callback=self.handle_motion_callback)

    def action_del_motion(self) -> None:
        """Open the Delete Motion confirmation modal."""
        if not self.active_motion_id:
            self.toast("Select a motion to delete.")
            return
        self.push_screen(
            ConfirmDeleteScreen(self.active_motion_name),
            callback=self.handle_delete_motion_callback,
        )

    def handle_delete_motion_callback(self, confirmed: bool) -> None:
        if confirmed and self.active_motion_id:
            delete_motion(self.active_motion_id)
            self.active_motion_id = None
            self.active_motion_name = "None"
            self._reload_motions()
            self._reload_evidence()
            self.toast("Motion deleted successfully.")

    def action_rename_motion(self) -> None:
        """Open the Motion rename modal."""
        if not self.active_motion_id:
            self.toast("Select a motion to rename.")
            return
        self.push_screen(
            AddMotionScreen(self.active_motion_id, self.active_motion_name),
            callback=self.handle_motion_callback,
        )

    def handle_motion_callback(self, new_motion_id: Optional[int]) -> None:
        if new_motion_id is not None:
            self._reload_motions()
            self.active_motion_id = new_motion_id
            ml = self.query_one("#motion-list", ListView)
            for idx, item in enumerate(ml.children):
                m = getattr(item, "_motion_data", None)
                if m and m["id"] == new_motion_id:
                    ml.index = idx
                    self.active_motion_name = m["name"]
                    break
            self._reload_evidence()
            self.toast("Motion updated successfully.")

    def action_add_card(self) -> None:
        """Open the Add Card modal screen."""
        if not self.active_motion_id:
            self.toast("Select a motion first.")
            return
        self.push_screen(AddCardScreen(self.active_motion_id), callback=self.handle_card_callback)

    def action_edit_card(self) -> None:
        """Open the Edit Card modal screen for the highlighted card."""
        if not self.active_motion_id:
            self.toast("Select a motion first.")
            return
        el = self.query_one("#evidence-list", ListView)
        if not el.highlighted_child:
            self.toast("Select an evidence card to edit.")
            return
        c = getattr(el.highlighted_child, "_card_data", None)
        if not c:
            return
        self.push_screen(
            AddCardScreen(self.active_motion_id, card=c),
            callback=self.handle_card_callback,
        )

    def action_delete_card(self) -> None:
        """Delete the currently selected evidence card."""
        el = self.query_one("#evidence-list", ListView)
        if not el.highlighted_child:
            self.toast("Select a card to delete.")
            return
        c = getattr(el.highlighted_child, "_card_data", None)
        if not c:
            return
        delete_card(c["id"])
        self._reload_evidence()
        self.toast("Card deleted successfully.")

    def handle_card_callback(self, success: bool) -> None:
        if success:
            self._reload_evidence()
            self.toast("Card saved successfully.")

    def action_compare_card(self) -> None:
        """Trigger evidence comparison when focused on the evidence list."""
        if not self.active_motion_id:
            self.toast("Select a motion first.")
            return
        el = self.query_one("#evidence-list", ListView)
        if not el.has_focus:
            return
        if not el.highlighted_child:
            self.toast("Select an evidence card to compare.")
            return
        card = getattr(el.highlighted_child, "_card_data", None)
        if not card:
            return

        all_cards = read_vault(self.active_motion_id)
        clashes = OracleEngine.detect_clash(card, all_cards)
        if not clashes:
            self.toast("No direct opposing clash detected for this card.")
            return

        card_b = clashes[0]
        self.push_screen(
            CompareScreen(card, card_b),
            callback=self.handle_compare_callback,
        )

    def handle_compare_callback(self, resolved: bool) -> None:
        if resolved:
            self._reload_evidence()

    def action_web_ingest(self) -> None:
        """Open the Web Ingest URL scraper modal."""
        if not self.active_motion_id:
            self.toast("Select a motion first.")
            return
        self.push_screen(WebIngestScreen(self.active_motion_id), callback=self.handle_card_callback)

    def action_open_drill(self) -> None:
        """Open the Gladiator Drill Arena modal."""
        if not self.active_motion_id:
            self.toast("Select a motion first.")
            return
        self.push_screen(DrillScreen(self.active_motion_id), callback=self.handle_drill_callback)

    def handle_drill_callback(self, result) -> None:
        self._reload_evidence()

    @on(Button.Pressed, "#btn-speech-prep-workspace")
    def open_speech_prep(self) -> None:
        self.action_open_speech_prep()

    def action_open_speech_prep(self) -> None:
        """Open the Speech Prep Screen modal."""
        if not self.active_motion_id:
            self.toast("Select a motion first.")
            return
        self.push_screen(
            SpeechPrepScreen(self.active_motion_id),
            callback=self.handle_speech_prep_callback,
        )

    def handle_speech_prep_callback(self, result) -> None:
        self._reload_evidence()

    def action_open_impact_map(self) -> None:
        """Open the ASCII Impact Map screen for the highlighted card."""
        el = self.query_one("#evidence-list", ListView)
        if not el.highlighted_child:
            self.toast("Select a card first.")
            return
        c = getattr(el.highlighted_child, "_card_data", None)
        if not c:
            return
        self.push_screen(ImpactMapScreen(c))

    def action_card_actions(self) -> None:
        """Open the context actions popup for the highlighted card."""
        el = self.query_one("#evidence-list", ListView)
        if not el.highlighted_child:
            self.toast("Select a card first.")
            return
        c = getattr(el.highlighted_child, "_card_data", None)
        if not c:
            return
        self.push_screen(CardActionScreen(c), callback=self.handle_card_action_callback)

    def handle_card_action_callback(self, action_tuple: Optional[tuple]) -> None:
        if not action_tuple:
            return
        action, card = action_tuple
        if action == "promote":
            card["tier"] = 3
            update_card(card["id"], card)
            self._reload_evidence()
            self.toast("Card promoted to Tier-3 Priority.")
        elif action == "copy":
            self.toast("Copied card text to clipboard.")
        elif action == "move":
            self.toast("Move functionality is under construction.")

    def action_open_settings(self) -> None:
        """Open the Settings & preferences panel."""
        self.push_screen(
            SettingsScreen(self._config, list(self._formats.keys())),
            callback=self.handle_settings_callback,
        )

    def action_toggle_active_speech(self) -> None:
        try:
            hud = self.query_one("#zone-epsilon", CommandHUD)
            hud.speech_toggle()
        except Exception:
            pass

    def action_toggle_active_prep(self) -> None:
        try:
            hud = self.query_one("#zone-epsilon", CommandHUD)
            hud.prep_toggle()
        except Exception:
            pass

    # ─── Button Click & List Action Dispatchers ───
    @on(Button.Pressed, "#btn-new-motion")
    def handle_btn_new_motion(self) -> None:
        self.action_new_motion()

    @on(Button.Pressed, "#btn-del-motion")
    def handle_btn_del_motion(self) -> None:
        self.action_del_motion()

    @on(Button.Pressed, "#fab-add")
    def handle_fab_add(self) -> None:
        self.action_add_card()

    @on(ListView.Selected, "#motion-list")
    def handle_motion_selected_rename(self, event: ListView.Selected) -> None:
        self.action_rename_motion()

    def handle_palette_select(self, card_data: Optional[dict]) -> None:
        try:
            if card_data:
                self.active_motion_id = card_data["motion_id"]
                self._reload_motions()
                self._reload_evidence()
                self.toast(f"Navigated to: {card_data['tag']}")
        except Exception:
            self.toast("Navigation Error")

    def action_generate_rebuttal(self) -> None:
        """Generate an automated rebuttal speech block."""
        el = self.query_one("#evidence-list", ListView)
        if not el.highlighted_child:
            return
        c = getattr(el.highlighted_child, "_card_data", None)
        if not c:
            return
        block = OracleEngine.synthesize_rebuttal_block(c)
        self.query_one("#card-detail", Markdown).update("\n".join(block))
        self.toast("Rebuttal: Speech Block Generated.")

    def action_open_matrix(self) -> None:
        """Visualize the Strategic Impact Matrix."""
        if not self.active_motion_id:
            self.toast("Select a motion first.")
            return
        cards = read_vault(self.active_motion_id)
        matrix = OracleEngine.analyze_matrix(cards)
        md = "# STRATEGIC IMPACT MATRIX\n\n"
        md += "| IMPACT | MAG (1-5) | PROB (1-5) |\n"
        md += "| :--- | :---: | :---: |\n"
        for m in matrix[:20]:
            md += f"| {m['tag'][:30]} | {'★' * m['m']} | {'●' * m['p']} |\n"
        self.query_one("#card-detail", Markdown).update(md)
        self.toast("Impact Matrix Rendered.")

    def action_predict_victory(self) -> None:
        """Execute a Win Probability Simulation."""
        if not self.active_motion_id:
            return
        cards = read_vault(self.active_motion_id)
        prob, status = OracleEngine.predict_victory(cards)
        md = f"# 🏆 VICTORY PREDICTION\n\n**WIN PROBABILITY: {prob}%**\n\n**STATUS:** {status}\n\n"
        md += "### 🧩 STRATEGIC RECOMMENDATIONS\n"
        if prob < 50:
            md += "- Urgent: Research NEG counter-arguments.\n"
        if prob > 50:
            md += "- Focus: Audit Tier 4/5 impacts to lock in the win.\n"
        self.query_one("#card-detail", Markdown).update(md)
        self.toast(f"Prediction: {prob}% Win Prob.")

    def action_generate_flow(self) -> None:
        """Generate a strategic speech flow outline."""
        if not self.active_motion_id:
            return
        cards = read_vault(self.active_motion_id)
        outline = OracleEngine.generate_flow_outline(cards)
        self.query_one("#card-detail", Markdown).update("\n".join(outline))
        self.toast("Flow-Bot: Speech Outline Generated.")

    def action_compare_motions(self) -> None:
        """Multi-motion comparative audit."""
        motions = list_motions()
        if len(motions) < 2:
            self.toast("Need at least 2 motions.")
            return
        md = "# MULTI-MOTION COMPARISON\n\n"
        md += "| MOTION | BALANCE | DEPTH | WIN PROB |\n"
        md += "| :--- | :---: | :---: | :---: |\n"
        for m in motions[:5]:
            cards = read_vault(m["id"])
            bal = OracleEngine.calculate_balance(cards)
            prob, _ = OracleEngine.predict_victory(cards)
            md += f"| {m['name'][:20]} | {bal}% AFF | {len(cards)} | {prob}% |\n"
        self.query_one("#card-detail", Markdown).update(md)
        self.toast("Comparative Audit Complete.")

    def action_calculate_road(self) -> None:
        """Map the 'Victory Road' roadmap."""
        if not self.active_motion_id:
            return
        cards = read_vault(self.active_motion_id)
        road = OracleEngine.calculate_victory_road(cards)
        self.query_one("#card-detail", Markdown).update("\n".join(road))
        self.toast("Victory Road: Mapping Complete.")

    def action_victory_road(self) -> None:
        """Alias for action_calculate_road."""
        self.action_calculate_road()

    def action_open_link_cloud(self) -> None:
        """Semantic Link-Cloud visualization."""
        motions = list_motions()
        cloud = OracleEngine.generate_link_cloud(motions)
        self.query_one("#card-detail", Markdown).update("\n".join(cloud))
        self.toast("Link-Cloud: Semantic Bridges Mapped.")

    @work(exclusive=True, thread=True)
    def action_simulate_spar(self) -> None:
        """Launch the Neural Sparring Mode."""
        el = self.query_one("#evidence-list", ListView)
        if not el.highlighted_child:
            return
        c = getattr(el.highlighted_child, "_card_data", None)
        if not c:
            return
        self.query_one("#card-detail", Markdown).update(
            "\n[ 🤖 AI is evaluating evidence sparring... ]"
        )
        spar = OracleEngine.simulate_sparring(c)
        self.query_one("#card-detail", Markdown).update("\n".join(spar))
        self.toast("Neural Sparring: Tactical Test Active.")

    @work(exclusive=True, thread=True)
    def action_simulate_judge(self) -> None:
        """Simulate a Neural Judge decision and RFD."""
        if not self.active_motion_id:
            return
        self.query_one("#card-detail", Markdown).update(
            "\n[ 🤖 AI is simulating the judge decision... ]"
        )
        cards = read_vault(self.active_motion_id)
        rfd = OracleEngine.simulate_judge(cards)
        self.query_one("#card-detail", Markdown).update("\n".join(rfd))
        self.toast("Neural Judge: Ballot Simulation Complete.")

    def action_research_queue(self) -> None:
        """Generate a strategic research queue."""
        if not self.active_motion_id:
            return
        cards = read_vault(self.active_motion_id)
        queue = OracleEngine.generate_research_queue(cards)
        self.query_one("#card-detail", Markdown).update("\n".join(queue))
        self.toast("Research Queue: Gaps Identified.")

    # ─────────────────────────────────────────────
    #  RIBBON NAVIGATION
    # ─────────────────────────────────────────────
    @on(Button.Pressed, ".ribbon-btn")
    def handle_ribbon(self, event: Button.Pressed) -> None:
        try:
            if event.button.id == "rb-search":
                if not self.active_motion_id:
                    return
                self.push_screen(SearchScreen(self.active_motion_id))
            if event.button.id == "rb-stats":
                self.push_screen(AnalyticsScreen())
            if event.button.id == "rb-pref":
                self.push_screen(
                    SettingsScreen(self._config, list(self._formats.keys())),
                    callback=self.handle_settings_callback,
                )
        except Exception as e:
            self._log_error(f"Ribbon action failed - {e}")

    def handle_settings_callback(self, new_config: Optional[dict]) -> None:
        if new_config:
            from omnishared.config import save_config

            self._config = new_config
            save_config(self._config)
            self._apply_accessibility_settings()
            self.notify("Settings Saved", severity="success")

    # ─────────────────────────────────────────────
    #  HELPERS
    # ─────────────────────────────────────────────
    def toast(self, message: str) -> None:
        self.notify(message, timeout=2)

    def _safe_update(self, selector: str, value: str) -> None:
        """Safely update a widget if it exists."""
        try:
            self.query_one(selector).update(value)
        except Exception:
            pass

    def _update_gauge(self, selector: str, value: int, label: str) -> None:
        """Update a GaugeBar widget safely."""
        try:
            gauge = self.query_one(selector, GaugeBar)
            gauge.set_value(value, label)
        except Exception:
            pass

    def _log_error(self, msg: str) -> None:
        """Log an error to the system log widget."""
        try:
            self.query_one(SystemLog).log_activity(f"ERROR: {msg}")
        except Exception:
            pass

    @on(Button.Pressed, "#btn-copy-link")
    def handle_copy_link(self) -> None:
        if not hasattr(self, "active_card") or not self.active_card:
            self.toast("Select a card first.")
            return
        import re

        citation = self.active_card.get("citation", "")
        urls = re.findall(r"https?://[^\s)]+", citation)
        link = urls[0] if urls else citation
        self.copy_to_system_clipboard(link)
        self.toast("Copied source link to system clipboard!")

    @on(Button.Pressed, "#btn-copy-content")
    def handle_copy_content(self) -> None:
        if not hasattr(self, "active_card") or not self.active_card:
            self.toast("Select a card first.")
            return
        tag = self.active_card.get("tag", "Card")
        text = self.active_card.get("text", "")
        content = f"[{tag.upper()}]\n{text}"
        self.copy_to_system_clipboard(content)
        self.toast("Copied card content to system clipboard!")

    def copy_to_system_clipboard(self, text: str) -> None:
        self.copy_to_clipboard(text)
        try:
            import subprocess
            import sys

            if sys.platform == "darwin":
                process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
                process.communicate(input=text.encode("utf-8"))
        except Exception:
            pass


if __name__ == "__main__":
    OmniDebate().run()
