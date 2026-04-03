#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║       EVIDENCE VAULT  v4.0.0  "Grand Nexus"          ║
║       High-Performance Debate Operating System       ║
╚══════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import datetime
import difflib
import glob
import json
import os
import random
import re
import shutil
import sys
import textwrap
import time
import threading
from typing import Optional

# ─── Optional dependencies (warn gracefully) ─────────────────────────────────
try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

try:
    import requests
    from bs4 import BeautifulSoup
    WEB_INGEST_OK = True
except ImportError:
    WEB_INGEST_OK = False

# ─── Textual / Rich ──────────────────────────────────────────────────────────
try:
    from rich.text import Text
    from textual import on, work
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Container, Horizontal, Vertical, VerticalScroll
    from textual.reactive import reactive
    from textual.screen import ModalScreen, Screen
    from textual.timer import Timer
    from textual.widgets import (
        Button,
        DataTable,
        Footer,
        Header,
        Input,
        Label,
        ListItem,
        ListView,
        Markdown,
        Select,
        Static,
        TextArea,
    )
except ImportError:
    print("Missing dependencies. Run:\n  python3 -m pip install textual rich")
    sys.exit(1)

# ─── Paths ────────────────────────────────────────────────────────────────────
DEBATES_DIR = "debates"
BACKUPS_DIR = "backups"
EXPORTS_DIR = "exports"
TRASH_FILE  = os.path.join(DEBATES_DIR, ".trash.json")
FORMATS_FILE = "formats.json"
CONFIG_FILE  = "config.yaml"

# ─── Helpers ──────────────────────────────────────────────────────────────────

def run_setup_dirs() -> None:
    for d in [DEBATES_DIR, BACKUPS_DIR, EXPORTS_DIR, os.path.join(DEBATES_DIR, "archives")]:
        os.makedirs(d, exist_ok=True)

def load_config() -> dict:
    defaults = {
        "version": "4.0.0",
        "timer": {"default_format": "Public Forum"},
        "export": {"auto_snapshot": True},
    }
    if yaml and os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return {**defaults, **yaml.safe_load(f)}
        except Exception:
            pass
    return defaults

def load_formats() -> dict:
    if os.path.exists(FORMATS_FILE):
        try:
            with open(FORMATS_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    # Fallback built-in
    return {
        "Public Forum": {
            "prep_time_seconds": 180,
            "speeches": [
                {"name": "Opening Statement (Team A)", "duration_seconds": 240},
                {"name": "Opening Statement (Team B)", "duration_seconds": 240},
                {"name": "Crossfire",                  "duration_seconds": 180},
                {"name": "Rebuttal (Team A)",           "duration_seconds": 240},
                {"name": "Rebuttal (Team B)",           "duration_seconds": 240},
                {"name": "Crossfire",                   "duration_seconds": 180},
                {"name": "Summary (Team A)",            "duration_seconds": 180},
                {"name": "Summary (Team B)",            "duration_seconds": 180},
                {"name": "Grand Crossfire",             "duration_seconds": 180},
                {"name": "Final Focus (Team A)",        "duration_seconds": 120},
                {"name": "Final Focus (Team B)",        "duration_seconds": 120},
            ],
        },
        "Lincoln-Douglas": {
            "prep_time_seconds": 240,
            "speeches": [
                {"name": "Affirmative Constructive",        "duration_seconds": 360},
                {"name": "Cross-Examination (Neg asking)",  "duration_seconds": 180},
                {"name": "Negative Constructive",           "duration_seconds": 420},
                {"name": "Cross-Examination (Aff asking)",  "duration_seconds": 180},
                {"name": "First Affirmative Rebuttal",      "duration_seconds": 240},
                {"name": "Negative Rebuttal",               "duration_seconds": 360},
                {"name": "Second Affirmative Rebuttal",     "duration_seconds": 180},
            ],
        },
        "Policy": {
            "prep_time_seconds": 480,
            "speeches": [
                {"name": "1AC",          "duration_seconds": 480},
                {"name": "CX (2NC asks)","duration_seconds": 180},
                {"name": "1NC",          "duration_seconds": 480},
                {"name": "CX (1AC asks)","duration_seconds": 180},
                {"name": "2AC",          "duration_seconds": 480},
                {"name": "CX (1NC asks)","duration_seconds": 180},
                {"name": "2NC",          "duration_seconds": 480},
                {"name": "CX (2AC asks)","duration_seconds": 180},
                {"name": "1NR",          "duration_seconds": 300},
                {"name": "1AR",          "duration_seconds": 300},
                {"name": "2NR",          "duration_seconds": 300},
                {"name": "2AR",          "duration_seconds": 300},
            ],
        },
    }

def read_vault(filepath: str) -> list:
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath) as f:
            return json.load(f)
    except Exception:
        return []

def write_vault(filepath: str, cards: list) -> None:
    with open(filepath, "w") as f:
        json.dump(cards, f, indent=2)

def snapshot(filepath: str) -> None:
    """Create a .bak timestamped snapshot before destructive ops."""
    if not os.path.exists(filepath):
        return
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    dst = os.path.join(BACKUPS_DIR, f"{os.path.basename(filepath)}.{ts}.bak")
    shutil.copy2(filepath, dst)

def get_trash() -> list:
    if not os.path.exists(TRASH_FILE):
        return []
    try:
        with open(TRASH_FILE) as f:
            return json.load(f)
    except Exception:
        return []

def save_trash(trash: list) -> None:
    with open(TRASH_FILE, "w") as f:
        json.dump(trash, f, indent=2)

def list_motions(include_archives: bool = False) -> list[dict]:
    patterns = [os.path.join(DEBATES_DIR, "*.json")]
    if include_archives:
        patterns.append(os.path.join(DEBATES_DIR, "archives", "*.json"))
    files = []
    for p in patterns:
        files += glob.glob(p)
    results = []
    for fp in sorted(files):
        if fp.endswith(".trash.json"):
            continue
        name = os.path.basename(fp)[:-5].replace("_", " ").title()
        archived = "archives" in fp
        results.append({"name": name, "file": fp, "archived": archived})
    return results

def bool_search(cards: list, query: str) -> list:
    """Supports AND / OR / NOT boolean logic across tag + text."""
    query = query.strip()
    if not query:
        return cards

    def token_match(card: dict, token: str) -> bool:
        haystack = (card.get("tag", "") + " " + card.get("text", "") + " " +
                    card.get("citation", "")).lower()
        token = token.lower().strip()
        if not token:
            return True
        words = re.findall(r"\w+", haystack)
        if token in haystack:
            return True
        return bool(difflib.get_close_matches(token, words, n=1, cutoff=0.75))

    # Split on OR first (lowest precedence)
    or_parts = re.split(r"\bOR\b", query, flags=re.IGNORECASE)

    def match_or_clause(card: dict, clause: str) -> bool:
        # Split on AND
        and_parts = re.split(r"\bAND\b", clause, flags=re.IGNORECASE)
        for part in and_parts:
            part = part.strip()
            if part.upper().startswith("NOT "):
                token = part[4:].strip()
                if token_match(card, token):
                    return False
            else:
                if not token_match(card, part):
                    return False
        return True

    return [c for c in cards if any(match_or_clause(c, clause) for clause in or_parts)]

def smart_cite(author: str, year: str, title: str, source: str) -> str:
    """Generate a standardised citation string."""
    parts = []
    if author:
        parts.append(author.strip())
    if year:
        parts.append(f"({year.strip()})")
    if title:
        parts.append(f'"{title.strip()}"')
    if source:
        parts.append(f"— {source.strip()}")
    return ", ".join(parts) if parts else "Unknown Source"

def impact_tree(card: dict) -> str:
    """Generate a simple ASCII impact map from card text."""
    text = card.get("text", "").lower()
    nodes = []
    if any(w in text for w in ["gdp", "economy", "trade", "market", "jobs", "cost", "billion"]):
        nodes.append("💰 Economic Impact")
    if any(w in text for w in ["health", "death", "disease", "poverty", "rights", "welfare", "mental"]):
        nodes.append("🧑 Social Impact")
    if any(w in text for w in ["climate", "carbon", "environment", "ocean", "biodiversity", "emission"]):
        nodes.append("🌍 Environmental Impact")
    if not nodes:
        nodes.append("❓ Unmapped — Add keywords to classify")

    tag = card.get("tag", "Claim")
    lines = [f"┌── [{card['side']}] {tag}"]
    for i, n in enumerate(nodes):
        prefix = "└──" if i == len(nodes) - 1 else "├──"
        lines.append(f"│   {prefix} {n}")
    return "\n".join(lines)

def scrape_url(url: str) -> tuple[str, str]:
    """Returns (title, body_text). Raises on failure."""
    resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.title.string.strip() if soup.title else url
    # Get meaningful paragraphs
    paras = [p.get_text(" ", strip=True) for p in soup.find_all("p") if len(p.get_text()) > 60]
    body = " ".join(paras[:8])  # First 8 paragraphs
    return title, body

def export_brief_markdown(filepath: str, motion_name: str) -> str:
    cards = read_vault(filepath)
    aff   = [c for c in cards if c["side"] == "AFF"]
    neg   = [c for c in cards if c["side"] == "NEG"]
    today = datetime.date.today().strftime("%Y-%m-%d")
    fname = os.path.join(EXPORTS_DIR, f"brief_{motion_name.lower().replace(' ', '_')}_{today}.md")

    with open(fname, "w") as out:
        out.write(f"# 🏛️ DEBATE BRIEF — {motion_name.upper()}\n")
        out.write(f"> Generated: {today} | Evidence Vault v4.0.0 Grand Nexus\n\n")
        out.write("---\n\n## 📋 TABLE OF CONTENTS\n\n")
        out.write("### AFFIRMATIVE\n")
        for i, c in enumerate(aff, 1):
            star = "⭐ " if c.get("tier") == 3 else ""
            out.write(f"{i}. {star}**{c['tag'].upper()}** — *{c['citation']}*\n")
        out.write("\n### NEGATIVE\n")
        for i, c in enumerate(neg, 1):
            star = "⭐ " if c.get("tier") == 3 else ""
            out.write(f"{i}. {star}**{c['tag'].upper()}** — *{c['citation']}*\n")
        out.write("\n---\n\n")

        for section_label, section_cards in [("AFFIRMATIVE", aff), ("NEGATIVE", neg)]:
            out.write(f"## ⚖️ {section_label}\n\n")
            for c in sorted(section_cards, key=lambda x: -x.get("tier", 1)):
                star = "⭐ " if c.get("tier") == 3 else ""
                out.write(f"### {star}[{c['side']}] {c['tag'].upper()}\n")
                out.write(f"**Source:** {c['citation']}  \n")
                out.write(f"**Tier:** {'⭐' * c.get('tier', 1)} | **Language:** {c.get('language','EN')} | **Date Added:** {c.get('timestamp','—')}\n\n")
                out.write(f"> {c['text']}\n\n")
                out.write(f"```\n{impact_tree(c)}\n```\n\n---\n\n")

    return fname

# ══════════════════════════════════════════════════════════════════════════════
#  MODAL SCREENS
# ══════════════════════════════════════════════════════════════════════════════

class AddCardScreen(ModalScreen):
    """Full-screen modal for adding / editing a card."""

    DEFAULT_CSS = """
    AddCardScreen {
        align: center middle;
    }
    #add-card-dialog {
        width: 72;
        height: auto;
        background: $surface;
        border: double $primary;
        padding: 1 2;
    }
    #add-card-dialog Label { margin-bottom: 0; color: $text-muted; }
    #add-card-dialog Input { margin-bottom: 1; }
    #add-card-dialog TextArea { height: 6; margin-bottom: 1; }
    #btn-row { align: center middle; height: 3; }
    #btn-row Button { margin: 0 1; }
    """

    def __init__(self, vault_path: str, card: Optional[dict] = None):
        super().__init__()
        self.vault_path = vault_path
        self.card = card  # None = add mode, dict = edit mode

    def compose(self) -> ComposeResult:
        c = self.card or {}
        with Container(id="add-card-dialog"):
            yield Label("─── Add / Edit Evidence Card ───")
            yield Label("Tag  (short claim)")
            yield Input(value=c.get("tag", ""),       placeholder="e.g. Economic growth outweighs", id="inp-tag")
            yield Label("Citation  (Author, Year, Source)")
            yield Input(value=c.get("citation", ""),  placeholder='e.g. Smith (2023), "Trade Wars"', id="inp-cite")
            yield Label("Author  |  Year  (for Smart Cite builder — optional)")
            with Horizontal():
                yield Input(value="", placeholder="Author", id="inp-author", classes="half")
                yield Input(value="", placeholder="Year",   id="inp-year",   classes="half")
            yield Label("Side")
            yield Select(
                [("AFF – Affirmative", "AFF"), ("NEG – Negative", "NEG")],
                value=c.get("side", "AFF"),
                id="sel-side",
            )
            yield Label("Language")
            yield Select(
                [("English", "EN"), ("German", "DE"), ("Spanish", "ES")],
                value=c.get("language", "EN"),
                id="sel-lang",
            )
            yield Label("Tier  (1 = normal · 3 = ⭐ priority)")
            yield Select(
                [("1 – Standard", "1"), ("2 – Important", "2"), ("3 – ⭐ Priority", "3")],
                value=str(c.get("tier", 1)),
                id="sel-tier",
            )
            yield Label("Evidence Text")
            yield TextArea(c.get("text", ""), id="inp-text")
            with Horizontal(id="btn-row"):
                yield Button("💾 Save",   variant="success", id="btn-save")
                yield Button("🔑 Smart Cite", variant="primary", id="btn-cite")
                yield Button("✖ Cancel",  variant="error",   id="btn-cancel")

    @on(Button.Pressed, "#btn-cancel")
    def cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-cite")
    def build_cite(self) -> None:
        author = self.query_one("#inp-author", Input).value
        year   = self.query_one("#inp-year",   Input).value
        tag    = self.query_one("#inp-tag",     Input).value
        result = smart_cite(author, year, tag, "")
        self.query_one("#inp-cite", Input).value = result

    @on(Button.Pressed, "#btn-save")
    def save_card(self) -> None:
        tag  = self.query_one("#inp-tag",  Input).value.strip()
        cite = self.query_one("#inp-cite", Input).value.strip()
        text = self.query_one("#inp-text", TextArea).text.strip()
        side = self.query_one("#sel-side", Select).value or "AFF"
        lang = self.query_one("#sel-lang", Select).value or "EN"
        tier = int(self.query_one("#sel-tier", Select).value or "1")

        if not tag or not text:
            self.app.notify("Tag and evidence text are required.", severity="warning")
            return

        cards = read_vault(self.vault_path)

        if self.card:
            # Edit mode
            for existing in cards:
                if existing["id"] == self.card["id"]:
                    existing.update({"tag": tag, "citation": cite, "text": text,
                                     "side": side, "language": lang, "tier": tier,
                                     "timestamp": datetime.date.today().strftime("%Y-%m-%d")})
                    break
        else:
            # Add mode
            new_id = max((c.get("id", 0) for c in cards), default=0) + 1
            cards.append({
                "id": new_id, "tag": tag, "citation": cite, "side": side,
                "text": text, "language": lang, "mastery": 0, "tier": tier,
                "timestamp": datetime.date.today().strftime("%Y-%m-%d"),
            })

        write_vault(self.vault_path, cards)
        self.dismiss(True)


class AddMotionScreen(ModalScreen):
    """Modal for creating a new debate motion."""

    DEFAULT_CSS = """
    AddMotionScreen { align: center middle; }
    #motion-dialog {
        width: 60; height: auto;
        background: $surface; border: double $accent;
        padding: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="motion-dialog"):
            yield Label("🗂️  Create New Motion")
            yield Input(placeholder="e.g. Universal Basic Income", id="inp-motion-name")
            with Horizontal(id="btn-row"):
                yield Button("✅ Create", variant="success", id="btn-ok")
                yield Button("✖ Cancel", variant="error",   id="btn-cancel")

    @on(Button.Pressed, "#btn-cancel")
    def cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-ok")
    def create(self) -> None:
        name = self.query_one("#inp-motion-name", Input).value.strip()
        if not name:
            self.app.notify("Motion name cannot be empty.", severity="warning")
            return
        filename = name.lower().replace(" ", "_").replace("/", "") + ".json"
        filepath = os.path.join(DEBATES_DIR, filename)
        if not os.path.exists(filepath):
            write_vault(filepath, [])
        self.dismiss(filepath)


class SearchScreen(ModalScreen):
    """Boolean Omni-Search across all loaded cards."""

    DEFAULT_CSS = """
    SearchScreen { align: center middle; }
    #search-dialog {
        width: 80; height: 36;
        background: $surface; border: double $primary;
        padding: 1 2;
    }
    #search-results { height: 1fr; border: solid $boost; padding: 1; overflow-y: auto; }
    """

    def __init__(self, vault_path: str):
        super().__init__()
        self.vault_path = vault_path

    def compose(self) -> ComposeResult:
        with Container(id="search-dialog"):
            yield Label("🔍 Boolean Omni-Search  (AND / OR / NOT supported)")
            with Horizontal():
                yield Input(placeholder='e.g.  "economic growth" AND NOT recession', id="inp-query")
                yield Button("Search", variant="primary", id="btn-search")
            yield Select(
                [("Current Motion Only", "local"), ("Global (all motions + archives)", "global")],
                value="local", id="sel-scope",
            )
            yield Static("", id="search-results")
            yield Button("✖ Close", variant="error", id="btn-close")

    @on(Button.Pressed, "#btn-close")
    def close(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-search")
    def do_search(self) -> None:
        query   = self.query_one("#inp-query",  Input).value
        scope   = self.query_one("#sel-scope",  Select).value

        if scope == "global":
            files = glob.glob(os.path.join(DEBATES_DIR, "*.json")) + \
                    glob.glob(os.path.join(DEBATES_DIR, "archives", "*.json"))
            files = [f for f in files if not f.endswith(".trash.json")]
            all_cards = []
            for fp in files:
                for c in read_vault(fp):
                    c["_motion"] = os.path.basename(fp)[:-5].replace("_", " ").title()
                    all_cards.append(c)
        else:
            all_cards = read_vault(self.vault_path)
            for c in all_cards:
                c["_motion"] = ""

        results = bool_search(all_cards, query)

        lines = [f"Found **{len(results)}** card(s)\n"]
        for c in results:
            star  = "⭐ " if c.get("tier") == 3 else ""
            badge = f"[{c['side']}]"
            motion_info = f"  _({c['_motion']})_" if c.get("_motion") else ""
            lines.append(f"**{badge} {star}{c['tag']}**{motion_info}")
            lines.append(f"> {c['text'][:120]}{'…' if len(c['text'])>120 else ''}")
            lines.append("")

        self.query_one("#search-results", Static).update("\n".join(lines))


class DrillScreen(ModalScreen):
    """Gladiator Drill Mode — spaced-repetition card quiz."""

    DEFAULT_CSS = """
    DrillScreen { align: center middle; }
    #drill-dialog {
        width: 78; height: 34;
        background: $surface; border: double $warning;
        padding: 1 2;
    }
    #drill-card { border: solid $primary; padding: 1; height: 12; overflow-y: auto; }
    #drill-rating { align: center middle; height: 3; }
    """

    def __init__(self, vault_path: str, weak_only: bool = False):
        super().__init__()
        self.vault_path = vault_path
        self.weak_only  = weak_only
        self.current_card: Optional[dict] = None
        self.revealed = False

    def compose(self) -> ComposeResult:
        with Container(id="drill-dialog"):
            yield Label("⚔️  GLADIATOR DRILL MODE" + ("  ·  WEAK POINTS ONLY" if self.weak_only else ""))
            yield Static("Loading...", id="drill-tag")
            yield Static("", id="drill-cite")
            yield Static("", id="drill-card")
            with Horizontal(id="drill-rating"):
                for i in range(1, 6):
                    yield Button(str(i), id=f"btn-rate-{i}", variant="primary")
            with Horizontal():
                yield Button("👁  Reveal", variant="success",  id="btn-reveal")
                yield Button("➡  Next",   variant="primary",  id="btn-next")
                yield Button("✖  Exit",   variant="error",    id="btn-exit")

    def on_mount(self) -> None:
        self._load_card()

    def _load_card(self) -> None:
        cards = read_vault(self.vault_path)
        if self.weak_only:
            cards = [c for c in cards if c.get("mastery", 0) <= 2]
        if not cards:
            self.query_one("#drill-tag", Static).update("🏆 All cards mastered! No cards remaining.")
            return
        self.current_card = random.choice(cards)
        self.revealed = False
        c = self.current_card
        side_icon = "🟢" if c["side"] == "AFF" else "🔴"
        self.query_one("#drill-tag",  Static).update(f"{side_icon} [{c['side']}] {c['tag'].upper()}")
        self.query_one("#drill-cite", Static).update(f"Source: {c['citation']}")
        self.query_one("#drill-card", Static).update("[ Press REVEAL to display evidence ]")

    @on(Button.Pressed, "#btn-reveal")
    def reveal(self) -> None:
        if self.current_card and not self.revealed:
            self.revealed = True
            self.query_one("#drill-card", Static).update(self.current_card["text"])

    @on(Button.Pressed, "#btn-next")
    def next_card(self) -> None:
        self._load_card()

    @on(Button.Pressed, "#btn-exit")
    def exit_drill(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id and event.button.id.startswith("btn-rate-"):
            rating = int(event.button.id.split("-")[-1])
            if self.current_card:
                cards = read_vault(self.vault_path)
                for c in cards:
                    if c["id"] == self.current_card["id"]:
                        c["mastery"] = rating
                        break
                write_vault(self.vault_path, cards)
                self.app.notify(f"Mastery {rating}/5 saved.", severity="information")
                self._load_card()


class WebIngestScreen(ModalScreen):
    """Scrape a URL and ingest its content as a new evidence card."""

    DEFAULT_CSS = """
    WebIngestScreen { align: center middle; }
    #wi-dialog {
        width: 74; height: auto;
        background: $surface; border: double $success;
        padding: 1 2;
    }
    #wi-preview { height: 8; border: solid $boost; padding: 1; overflow-y: auto; }
    """

    def __init__(self, vault_path: str):
        super().__init__()
        self.vault_path = vault_path
        self._scraped_title = ""
        self._scraped_body  = ""

    def compose(self) -> ComposeResult:
        with Container(id="wi-dialog"):
            yield Label("🌐 Web Ingest  —  Scrape URL into Vault")
            yield Input(placeholder="https://...", id="wi-url")
            with Horizontal():
                yield Button("🔍 Fetch", variant="primary", id="wi-fetch")
                yield Button("✖ Cancel", variant="error",  id="wi-cancel")
            yield Static("", id="wi-status")
            yield Label("Preview (first 500 chars):")
            yield Static("No content fetched yet.", id="wi-preview")
            yield Label("Tag for this evidence:")
            yield Input(placeholder="e.g. Trade deficit argument", id="wi-tag")
            yield Label("Side:")
            yield Select([("AFF", "AFF"), ("NEG", "NEG")], value="AFF", id="wi-side")
            yield Label("Tier:")
            yield Select(
                [("1 – Standard", "1"), ("2 – Important", "2"), ("3 – ⭐ Priority", "3")],
                value="1", id="wi-tier",
            )
            with Horizontal():
                yield Button("💾 Ingest to Vault", variant="success", id="wi-save")

    @on(Button.Pressed, "#wi-cancel")
    def cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#wi-fetch")
    def fetch(self) -> None:
        if not WEB_INGEST_OK:
            self.app.notify("Install requests + beautifulsoup4 for web ingest.", severity="error")
            return
        url = self.query_one("#wi-url", Input).value.strip()
        if not url:
            self.app.notify("Enter a URL first.", severity="warning")
            return
        self.query_one("#wi-status", Static).update("⏳ Fetching…")
        try:
            title, body = scrape_url(url)
            self._scraped_title = title
            self._scraped_body  = body
            self.query_one("#wi-status",  Static).update(f"✅ Fetched: {title}")
            self.query_one("#wi-preview", Static).update(body[:500] + ("…" if len(body) > 500 else ""))
            self.query_one("#wi-tag",     Input).value = title[:80]
        except Exception as e:
            self.query_one("#wi-status", Static).update(f"❌ Error: {e}")

    @on(Button.Pressed, "#wi-save")
    def save(self) -> None:
        if not self._scraped_body:
            self.app.notify("Fetch a URL first.", severity="warning")
            return
        tag     = self.query_one("#wi-tag",   Input).value.strip() or self._scraped_title
        side    = self.query_one("#wi-side",  Select).value or "AFF"
        tier    = int(self.query_one("#wi-tier", Select).value or "1")
        url_val = self.query_one("#wi-url",   Input).value.strip()

        cards  = read_vault(self.vault_path)
        new_id = max((c.get("id", 0) for c in cards), default=0) + 1
        cards.append({
            "id": new_id, "tag": tag,
            "citation": f"Web Ingest — {url_val}",
            "side": side, "text": self._scraped_body[:2000],
            "language": "EN", "mastery": 0, "tier": tier,
            "timestamp": datetime.date.today().strftime("%Y-%m-%d"),
        })
        write_vault(self.vault_path, cards)
        self.app.notify(f"✅ Ingested: '{tag}'", severity="information")
        self.dismiss(True)


class ImpactMapScreen(ModalScreen):
    """Show ASCII impact tree for the selected card."""

    DEFAULT_CSS = """
    ImpactMapScreen { align: center middle; }
    #impact-dialog {
        width: 60; height: auto;
        background: $surface; border: double $secondary;
        padding: 1 2;
    }
    #impact-tree { font-family: monospace; padding: 1; border: solid $boost; }
    """

    def __init__(self, card: dict):
        super().__init__()
        self.card = card

    def compose(self) -> ComposeResult:
        with Container(id="impact-dialog"):
            yield Label("🗺️  Impact Map")
            yield Static(impact_tree(self.card), id="impact-tree")
            yield Button("✖ Close", variant="error", id="btn-close")

    @on(Button.Pressed, "#btn-close")
    def close(self) -> None:
        self.dismiss(None)


# ══════════════════════════════════════════════════════════════════════════════
#  TIMER HUD WIDGET
# ══════════════════════════════════════════════════════════════════════════════

class TimerHUD(Static):
    """Self-contained Live Prep HUD with speech timer and prep reservoir."""

    DEFAULT_CSS = """
    TimerHUD { height: auto; }
    .hud-label   { text-align: center; text-style: bold; color: $text-muted; }
    .hud-time    { text-align: center; text-style: bold; font-size: 2; }
    .hud-bar     { text-align: center; color: $success; }
    .hud-prep    { text-align: center; color: $warning; text-style: bold; }
    .hud-running { color: $success; }
    .hud-expired { color: $error; text-style: bold; }
    """

    _speech_secs: int   = reactive(0)
    _prep_secs:   int   = reactive(0)
    _speech_total:int   = 0
    _timer_running:bool = False
    _prep_running: bool = False
    _tick_handle: Optional[Timer] = None

    def __init__(self, formats: dict, default_format: str = "Public Forum"):
        super().__init__()
        self.formats = formats
        self.format_name = default_format
        self._speech_idx = 0
        self._reset_format()

    def _reset_format(self) -> None:
        fmt = self.formats.get(self.format_name, {})
        self._speeches    = fmt.get("speeches", [])
        self._prep_secs   = fmt.get("prep_time_seconds", 180)
        self._prep_total  = self._prep_secs
        self._speech_idx  = 0
        self._load_current_speech()

    def _load_current_speech(self) -> None:
        if self._speeches and self._speech_idx < len(self._speeches):
            sp = self._speeches[self._speech_idx]
            self._speech_secs  = sp["duration_seconds"]
            self._speech_total = sp["duration_seconds"]
            self._speech_name  = sp["name"]
        else:
            self._speech_secs  = 0
            self._speech_total = 0
            self._speech_name  = "Round Complete"

    def compose(self) -> ComposeResult:
        fmt_options = [(name, name) for name in self.formats]
        yield Label("⏱️  CHRONOS ENGINE", classes="hud-label")
        yield Select(fmt_options, value=self.format_name, id="sel-format")
        yield Label("", id="lbl-speech-name",  classes="hud-label")
        yield Label("00:00", id="lbl-speech-time", classes="hud-time")
        yield Label("", id="lbl-speech-bar",   classes="hud-bar")
        yield Label("──── PREP RESERVOIR ────", classes="hud-label")
        yield Label("03:00", id="lbl-prep-time",   classes="hud-prep")
        with Horizontal(id="timer-btns"):
            yield Button("▶ Speech",  id="btn-speech-start", variant="success")
            yield Button("■ Stop",    id="btn-speech-stop",  variant="error")
            yield Button("⏭ Next",    id="btn-speech-next",  variant="primary")
        with Horizontal(id="prep-btns"):
            yield Button("▶ Prep",   id="btn-prep-start", variant="warning")
            yield Button("■ Stop",   id="btn-prep-stop",  variant="error")
        yield Button("↺ Reset Format", id="btn-reset-fmt",  variant="default")

    def on_mount(self) -> None:
        self._refresh_labels()
        self._tick_handle = self.set_interval(1, self._tick)

    def _tick(self) -> None:
        if self._timer_running and self._speech_secs > 0:
            self._speech_secs -= 1
            if self._speech_secs == 0:
                self._timer_running = False
                self.app.notify("⚠️  TIME EXPIRED!", severity="warning")
        if self._prep_running and self._prep_secs > 0:
            self._prep_secs -= 1
            if self._prep_secs == 0:
                self._prep_running = False
                self.app.notify("⚠️  PREP TIME EXHAUSTED!", severity="error")
        self._refresh_labels()

    def _fmt_time(self, secs: int) -> str:
        m, s = divmod(max(secs, 0), 60)
        return f"{m:02d}:{s:02d}"

    def _progress_bar(self, current: int, total: int, width: int = 20) -> str:
        if total == 0:
            return "─" * width
        filled = int((current / total) * width)
        return "█" * filled + "░" * (width - filled)

    def _refresh_labels(self) -> None:
        self.query_one("#lbl-speech-name",  Label).update(
            f"  {self._speech_name}"
            if hasattr(self, "_speech_name") else "")
        st = self.query_one("#lbl-speech-time", Label)
        st.update(self._fmt_time(self._speech_secs))
        st.set_class(self._timer_running, "hud-running")
        st.set_class(self._speech_secs == 0 and self._speech_total > 0, "hud-expired")
        self.query_one("#lbl-speech-bar",  Label).update(
            self._progress_bar(self._speech_secs, self._speech_total))
        self.query_one("#lbl-prep-time",   Label).update(
            f"PREP  {self._fmt_time(self._prep_secs)}")

    @on(Select.Changed, "#sel-format")
    def format_changed(self, event: Select.Changed) -> None:
        if event.value:
            self.format_name   = event.value
            self._timer_running = False
            self._prep_running  = False
            self._reset_format()
            self._refresh_labels()
            self.app.notify(f"Format: {self.format_name}", severity="information")

    @on(Button.Pressed, "#btn-speech-start")
    def speech_start(self) -> None:
        if self._speech_secs > 0:
            self._timer_running = True

    @on(Button.Pressed, "#btn-speech-stop")
    def speech_stop(self) -> None:
        self._timer_running = False

    @on(Button.Pressed, "#btn-speech-next")
    def speech_next(self) -> None:
        self._timer_running = False
        self._speech_idx    = min(self._speech_idx + 1, len(self._speeches) - 1)
        self._load_current_speech()
        self._refresh_labels()

    @on(Button.Pressed, "#btn-prep-start")
    def prep_start(self) -> None:
        if self._prep_secs > 0:
            self._prep_running = True

    @on(Button.Pressed, "#btn-prep-stop")
    def prep_stop(self) -> None:
        self._prep_running = False

    @on(Button.Pressed, "#btn-reset-fmt")
    def reset_fmt(self) -> None:
        self._timer_running = False
        self._prep_running  = False
        self._reset_format()
        self._refresh_labels()
        self.app.notify("Format reset.", severity="information")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

class GrandNexus(App):
    """Evidence Vault v4.0.0 — Grand Nexus Debate Operating System."""

    TITLE = "Evidence Vault  v4.0.0  ╠  Grand Nexus"

    CSS = """
    /* ── Layout ──────────────────────────────────────────────── */
    Screen { layers: base overlay; }

    #main-layout { height: 1fr; }

    #left-pane {
        width: 22;
        border-right: solid $primary;
        background: $surface-darken-1;
        padding: 0 1;
    }
    #center-pane {
        width: 1fr;
        padding: 0 1;
    }
    #right-pane {
        width: 30;
        border-left: solid $primary;
        background: $surface-darken-1;
        padding: 0 1;
    }

    /* ── Pane headers ─────────────────────────────────────────── */
    .pane-title {
        text-align: center;
        text-style: bold;
        background: $primary-darken-1;
        color: $text;
        padding: 0 1;
        margin-bottom: 1;
        width: 100%;
    }

    /* ── Motion list ──────────────────────────────────────────── */
    #motion-list { height: 1fr; }
    .motion-item Label { color: $text; }
    .archived-item Label { color: $text-muted; text-style: italic; }

    /* ── Evidence list ────────────────────────────────────────── */
    #evidence-list { height: 40%; }

    /* ── Card detail ──────────────────────────────────────────── */
    #card-detail {
        height: 1fr;
        border: solid $boost;
        padding: 1;
        margin-top: 1;
        overflow-y: auto;
    }

    /* ── Footer toolbar ───────────────────────────────────────── */
    #toolbar {
        height: 3;
        background: $surface-darken-2;
        align: center middle;
        padding: 0 1;
    }
    #toolbar Button { margin: 0 1; min-width: 12; height: 1; }

    /* ── Motion action buttons ────────────────────────────────── */
    #motion-actions { height: 9; }
    #motion-actions Button { width: 100%; height: 1; margin-bottom: 0; }

    /* ── Timer pane ───────────────────────────────────────────── */
    TimerHUD { height: 1fr; }
    #timer-btns Button,
    #prep-btns  Button { height: 1; margin: 0; min-width: 6; }
    #timer-btns,
    #prep-btns  { height: 3; margin-top: 1; }
    """

    BINDINGS = [
        Binding("q",     "quit",         "Quit"),
        Binding("n",     "new_card",      "New Card"),
        Binding("s",     "open_search",   "Search"),
        Binding("d",     "start_drill",   "Drill"),
        Binding("w",     "web_ingest",    "Web Ingest"),
        Binding("e",     "export_brief",  "Export Brief"),
        Binding("m",     "new_motion",    "New Motion"),
        Binding("ctrl+z","undo_delete",   "Undo Delete"),
        Binding("i",     "impact_map",    "Impact Map"),
    ]

    active_filepath:  reactive[str]  = reactive("")
    active_motion:    reactive[str]  = reactive("— None Selected —")
    selected_card:    reactive[Optional[dict]] = reactive(None)

    def __init__(self):
        super().__init__()
        run_setup_dirs()
        self._config  = load_config()
        self._formats = load_formats()

    # ── Compose ───────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="main-layout"):

            # ── LEFT: Motion Navigator ──────────────────────────────────────
            with Vertical(id="left-pane"):
                yield Label("📂 Motions", classes="pane-title")
                yield ListView(id="motion-list")
                with Vertical(id="motion-actions"):
                    yield Button("➕ New Motion",  id="btn-new-motion",   variant="success")
                    yield Button("🗄 Archive",      id="btn-archive",      variant="default")
                    yield Button("✏ Rename",       id="btn-rename-motion",variant="default")
                    yield Button("🗑 Delete Motion",id="btn-del-motion",   variant="error")

            # ── CENTER: Evidence Feed ──────────────────────────────────────
            with Vertical(id="center-pane"):
                yield Label("📜 Evidence Feed", classes="pane-title")
                yield ListView(id="evidence-list")
                yield Markdown("_Select a motion, then pick a card to view details._", id="card-detail")

            # ── RIGHT: Timer HUD ───────────────────────────────────────────
            with Vertical(id="right-pane"):
                yield TimerHUD(
                    formats=self._formats,
                    default_format=self._config.get("timer", {}).get("default_format", "Public Forum"),
                )

        # ── Toolbar ────────────────────────────────────────────────────────
        with Horizontal(id="toolbar"):
            yield Button("➕ Card [N]",    id="btn-add-card",    variant="success")
            yield Button("✏ Edit Card",   id="btn-edit-card",   variant="primary")
            yield Button("🗑 Delete Card", id="btn-del-card",    variant="error")
            yield Button("↩ Undo [^Z]",   id="btn-undo",        variant="warning")
            yield Button("🔍 Search [S]", id="btn-search",      variant="primary")
            yield Button("🌐 Ingest [W]", id="btn-ingest",      variant="primary")
            yield Button("⚔ Drill [D]",  id="btn-drill",       variant="warning")
            yield Button("🗺 Impact [I]", id="btn-impact",      variant="default")
            yield Button("📤 Export [E]", id="btn-export",      variant="default")

        yield Footer()

    # ── Mount: populate motion list ──────────────────────────────────────────

    def on_mount(self) -> None:
        self._reload_motions()

    def _reload_motions(self, select_path: str = "") -> None:
        ml = self.query_one("#motion-list", ListView)
        ml.clear()
        for m in list_motions(include_archives=True):
            count    = len(read_vault(m["file"]))
            suffix   = " [arch]" if m["archived"] else ""
            li = ListItem(Label(f"{'📁' if not m['archived'] else '🗂'} {m['name']}{suffix}  ({count})"))
            li._motion_data = m  # type: ignore[attr-defined]
            if m["archived"]:
                li.add_class("archived-item")
            else:
                li.add_class("motion-item")
            ml.append(li)
            if select_path and m["file"] == select_path:
                pass  # future: auto-select

    # ── Motion selection ─────────────────────────────────────────────────────

    @on(ListView.Selected, "#motion-list")
    def motion_selected(self, event: ListView.Selected) -> None:
        item = event.item
        m: dict = getattr(item, "_motion_data", None)
        if m:
            self.active_filepath = m["file"]
            self.active_motion   = m["name"]
            self._reload_evidence()
            self.sub_title = f"Motion: {m['name']}"

    # ── Evidence population ──────────────────────────────────────────────────

    def _reload_evidence(self) -> None:
        el = self.query_one("#evidence-list", ListView)
        el.clear()
        if not self.active_filepath:
            return
        for c in read_vault(self.active_filepath):
            star  = "⭐" if c.get("tier") == 3 else "  "
            icon  = "🟢" if c["side"] == "AFF" else "🔴"
            label = f"{icon} {star} [{c['id']:>3}] {c['tag'][:40]}"
            li    = ListItem(Label(label))
            li._card_data = c  # type: ignore[attr-defined]
            el.append(li)

    @on(ListView.Selected, "#evidence-list")
    def card_selected(self, event: ListView.Selected) -> None:
        c: dict = getattr(event.item, "_card_data", None)
        if c:
            self.selected_card = c
            self._show_card(c)

    def _show_card(self, c: dict) -> None:
        tier_stars = "⭐" * c.get("tier", 1)
        md_text = (
            f"## [{c['side']}] {c['tag']}\n\n"
            f"**Source:** {c['citation']}  \n"
            f"**Tier:** {tier_stars} | **Lang:** {c.get('language','EN')} "
            f"| **Mastery:** {c.get('mastery',0)}/5 | **Added:** {c.get('timestamp','—')}\n\n"
            f"---\n\n{c['text']}"
        )
        self.query_one("#card-detail", Markdown).update(md_text)

    # ── Toolbar button routing ───────────────────────────────────────────────

    @on(Button.Pressed, "#btn-add-card")
    def action_new_card(self) -> None:
        if not self.active_filepath:
            self.notify("Select or create a motion first.", severity="warning"); return
        self.push_screen(AddCardScreen(self.active_filepath), self._after_card_edit)

    @on(Button.Pressed, "#btn-edit-card")
    def btn_edit_card(self) -> None:
        if not self.selected_card:
            self.notify("Select a card to edit.", severity="warning"); return
        self.push_screen(AddCardScreen(self.active_filepath, self.selected_card), self._after_card_edit)

    @on(Button.Pressed, "#btn-del-card")
    def btn_del_card(self) -> None:
        self._delete_selected_card()

    @on(Button.Pressed, "#btn-undo")
    def btn_undo(self) -> None:
        self.action_undo_delete()

    @on(Button.Pressed, "#btn-search")
    def btn_search(self) -> None:
        self.action_open_search()

    @on(Button.Pressed, "#btn-ingest")
    def btn_ingest(self) -> None:
        self.action_web_ingest()

    @on(Button.Pressed, "#btn-drill")
    def btn_drill(self) -> None:
        self.action_start_drill()

    @on(Button.Pressed, "#btn-impact")
    def btn_impact(self) -> None:
        self.action_impact_map()

    @on(Button.Pressed, "#btn-export")
    def btn_export(self) -> None:
        self.action_export_brief()

    # ── Motion management buttons ────────────────────────────────────────────

    @on(Button.Pressed, "#btn-new-motion")
    def action_new_motion(self) -> None:
        self.push_screen(AddMotionScreen(), self._after_new_motion)

    def _after_new_motion(self, result) -> None:
        if result:
            self._reload_motions(select_path=result)
            self.notify("Motion created!", severity="information")

    @on(Button.Pressed, "#btn-archive")
    def btn_archive(self) -> None:
        if not self.active_filepath:
            self.notify("No motion selected.", severity="warning"); return
        if "archives" in self.active_filepath:
            self.notify("Already archived.", severity="warning"); return
        snapshot(self.active_filepath)
        dst = os.path.join(DEBATES_DIR, "archives", os.path.basename(self.active_filepath))
        shutil.move(self.active_filepath, dst)
        self.active_filepath = ""
        self.active_motion   = "— None Selected —"
        self._reload_motions()
        self.notify("Motion archived.", severity="information")

    @on(Button.Pressed, "#btn-rename-motion")
    def btn_rename_motion(self) -> None:
        if not self.active_filepath:
            self.notify("No motion selected.", severity="warning"); return
        # Reuse AddMotion for name prompt
        def _do_rename(new_name) -> None:
            if new_name and isinstance(new_name, str):
                # new_name here is a filepath — derive name from it
                base = os.path.basename(new_name)[:-5].replace("_","  ").title()
                self.notify(f"Renamed to {base}")
        # We'll just prompt inline via notify for now — a rename modal is a future iteration
        self.notify("Rename: Create a new motion and use Archive on the old one.", severity="information")

    @on(Button.Pressed, "#btn-del-motion")
    def btn_del_motion(self) -> None:
        if not self.active_filepath:
            self.notify("No motion selected.", severity="warning"); return
        snapshot(self.active_filepath)
        os.remove(self.active_filepath)
        self.active_filepath = ""
        self.active_motion   = "— None Selected —"
        self._reload_motions()
        self.query_one("#evidence-list", ListView).clear()
        self.query_one("#card-detail",   Markdown).update("_Motion deleted._")
        self.notify("Motion deleted. Snapshot saved to backups/", severity="warning")

    # ── Card CRUD ─────────────────────────────────────────────────────────────

    def _after_card_edit(self, result) -> None:
        if result:
            self._reload_evidence()
            self.notify("Card saved!", severity="information")

    def _delete_selected_card(self) -> None:
        if not self.selected_card or not self.active_filepath:
            self.notify("Select a card to delete.", severity="warning"); return
        snapshot(self.active_filepath)
        cards = read_vault(self.active_filepath)
        to_del = next((c for c in cards if c["id"] == self.selected_card["id"]), None)
        if to_del:
            cards.remove(to_del)
            write_vault(self.active_filepath, cards)
            trash = get_trash()
            trash.append({"motion_file": self.active_filepath, "card": to_del})
            save_trash(trash)
            self.selected_card = None
            self._reload_evidence()
            self.query_one("#card-detail", Markdown).update("_Card moved to trash. Press Ctrl+Z to undo._")
            self.notify("Card deleted (soft). Ctrl+Z to undo.", severity="warning")

    def action_undo_delete(self) -> None:
        trash = get_trash()
        if not trash:
            self.notify("Nothing in trash.", severity="warning"); return
        item = trash.pop()
        save_trash(trash)
        fp   = item["motion_file"]
        card = item["card"]
        cards = read_vault(fp)
        cards.append(card)
        write_vault(fp, cards)
        self._reload_evidence()
        self.notify(f"Recovered: '{card['tag']}'", severity="information")

    # ── Screen actions ────────────────────────────────────────────────────────

    def action_open_search(self) -> None:
        if not self.active_filepath:
            self.notify("Select a motion first.", severity="warning"); return
        self.push_screen(SearchScreen(self.active_filepath))

    def action_start_drill(self) -> None:
        if not self.active_filepath:
            self.notify("Select a motion first.", severity="warning"); return
        self.push_screen(DrillScreen(self.active_filepath, weak_only=False))

    def action_web_ingest(self) -> None:
        if not self.active_filepath:
            self.notify("Select a motion first.", severity="warning"); return
        self.push_screen(WebIngestScreen(self.active_filepath), self._after_card_edit)

    def action_impact_map(self) -> None:
        if not self.selected_card:
            self.notify("Select a card to map.", severity="warning"); return
        self.push_screen(ImpactMapScreen(self.selected_card))

    def action_export_brief(self) -> None:
        if not self.active_filepath:
            self.notify("Select a motion first.", severity="warning"); return
        fname = export_brief_markdown(self.active_filepath, self.active_motion)
        self.notify(f"📤 Brief exported: {fname}", severity="information")


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    run_setup_dirs()
    GrandNexus().run()
