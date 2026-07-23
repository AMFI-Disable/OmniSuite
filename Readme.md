# 🏛️ OmniSuite

[![Version](https://img.shields.io/badge/Version-V1.0.0-10b981?style=for-the-badge)](#)
[![PyPI](https://img.shields.io/pypi/v/omnisuite?style=for-the-badge&color=3b82f6)](https://pypi.org/project/omnisuite/)
[![Tests](https://img.shields.io/github/actions/workflow/status/amfi-disable/OmniSuite/ci.yml?style=for-the-badge&label=tests)](https://github.com/amfi-disable/OmniSuite/actions)
[![License](https://img.shields.io/badge/License-MIT-f59e0b?style=for-the-badge)](license)
[![Python](https://img.shields.io/badge/Python-3.9+-8b5cf6?style=for-the-badge)](https://python.org)

**The Digital Grandmaster Ecosystem** — a unified, high-fidelity workstation for competitive forensicians, debaters, and researchers. OmniSuite transforms the terminal into a cyber-dark command center for forensic research, case compilation, and tournament strategy.

---

## ⚡ Quick Install

```bash
pip install omnisuite
```

Or from source:

```bash
git clone https://github.com/amfi-disable/OmniSuite.git
cd OmniSuite
pip install -e "src/omnishared" -e "src/omnidebate" -e "src/omniformat"
```

## 🚀 Launch

```bash
# Research Workstation
omnisuite --app debate

# Document Compiler
omnisuite --app format
```

---

## ✦ The Applications

### 🏛️ OmniDebate — Research Workstation

A production-grade strategic research workstation. Transforms the terminal into a "Digital War Room" with real-time forensic auditing, AI-augmented synthesis, and zero-failure resilience for live tournament environments.

**Features:**
- **Evidence Vault** — SQLite-backed card management with FTS5 full-text search, boolean queries (AND/OR/NOT), and fuzzy matching
- **OracleEngine** — 10-dimension heuristic analysis (impact, narrative, clash, synergy, rhetoric, and more)
- **Debate Flow** — Multi-column argument tracking for live rounds — the only TUI flowing tool in existence
- **Round Timer** — Format-aware countdown with visual alerts and bell notifications
- **Argument Tree** — ASCII impact chain visualization with expand/collapse navigation
- **AI Assistant** — Ollama-powered card summarization, counter-argument generation, case analysis, and interactive debate prep chat
- **Drill Mode** — Spaced-repetition evidence review with mastery tracking and WPM speed practice
- **Export** — Verbatim .docx, CaseXC .docx, Markdown, Interactive HTML, CSV, JSON
- **Analytics Dashboard** — Research velocity graphs, contribution heatmaps, motion audits

### 📄 OmniFormat — Document Compiler

The automated document compilation and case formatting workstation. Interfaces directly with the shared debate database to assemble formatted briefs with strict Verbatim/CaseXC styling compliance.

---

## 🤖 AI Integration

OmniSuite integrates with [Ollama](https://ollama.ai) for local, privacy-preserving AI:

```bash
ollama pull llama3 && ollama serve
```

**AI Tools:**
- Auto-summarize cards
- Generate counter-arguments
- Analyze impact chains
- Score case strength
- Find evidence gaps
- Generate case outlines
- Create cross-examination questions
- Rewrite for clarity

---

## 🎨 Themes

| Cyber Dark (Default) | Light | Nord | Solarized |
|---|---|---|---|
| Glassmorphic dark UI | Clean white interface | Arctic blue-gray | Warm solarized palette |

Switch themes from Settings (`F5`).

---

## 🎯 Supported Debate Formats

| Format | Speeches | Style |
|--------|----------|-------|
| Public Forum | 4-min constructives, 2-min crossfire | PF |
| Lincoln-Douglas | 6/4-min constructives, 3-min cross | LD |
| Policy | 8-min constructives, 3-min cross | CX |
| British Parliamentary | 7-min speeches, 15-sec POI | BP |
| World Schools Style | 8-min speeches, 4-min reply | WSS |
| Asian Parliamentary | 7-min speeches | AP |
| Canadian National | 7-min constructives, 4-min rebuttals | CN |
| European Parliamentary | 7-min speeches | EP |
| Karl Popper | 6-min constructives, 5-min rebuttals | KP |

---

## 🐳 Docker

```bash
docker compose up -d
docker compose run --rm omnisuite --app debate
```

---

## 🛠️ Development

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -e "src/omnishared" -e "src/omnidebate" -e "src/omniformat"
pip install ruff pytest pytest-asyncio

# Test
pytest --tb=short -q

# Lint
ruff check . && ruff format --check .
```

See [Architecture](docs/dev/architecture.md) and [Contributing](docs/dev/contributing.md).

---

## ✦ Version Control (GitHub)

OmniSuite is hosted at [`amfi-disable/OmniSuite`](https://github.com/amfi-disable/OmniSuite). Commit messages follow the **conventional commits** format (`type:summary`, all lowercase).

---

## 📖 Documentation

- [Getting Started](docs/guide/getting-started.md)
- [Card Management](docs/guide/card-management.md)
- [Debate Flow](docs/guide/debate-flow.md)
- [AI Features](docs/guide/ai-features.md)
- [Export & Import](docs/guide/export-import.md)
- [Keyboard Shortcuts](docs/guide/keybindings.md)
- [Changelog](changelog.md)

---

*© 2026 OmniSuite. Built for the Digital Grandmaster.*
