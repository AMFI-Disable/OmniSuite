# 🏛️ OmniSuite

<div align="center">

**The High-Fidelity Terminal Workstation For Forensic Research & Case Compilation**  
*Unified command-line and Textual interface engineered for competitive forensicians, debate research, and tournament strategy.*

[![Platform: macOS & Linux](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-blue.svg?style=flat-square&logo=linux)](https://linux.org)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square&logo=python)](https://python.org)
[![Status: Archived](https://img.shields.io/badge/Status-Archived%20%2F%20Read--Only-inactive.svg?style=flat-square)](https://github.com/AMFI-Disable/OmniSuite)
[![Release: v1.0.0](https://img.shields.io/badge/Release-v1.0.0-blue.svg?style=flat-square&logo=github)](https://github.com/AMFI-Disable/OmniSuite/releases)
[![Tests: Passing](https://img.shields.io/badge/Tests-Passing%20(100%25)-success.svg?style=flat-square&logo=github-actions)](https://github.com/AMFI-Disable/OmniSuite/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](license)
[![Privacy: Local Storage](https://img.shields.io/badge/Privacy-100%25%20Local%20SQLite-purple.svg?style=flat-square)](#privacy-and-storage)

</div>

> [!NOTE]
> **Project Archived & Sunset Notice**
> OmniSuite has reached end-of-life and is officially archived. The final stable release is [v1.0.0](https://github.com/AMFI-Disable/OmniSuite/releases/tag/v1.0.0). The repository remains available in read-only mode for historical reference. No further updates, issues, or pull requests will be accepted.

---

## ⚡ Quick Install

```bash
pip install omnisuite
```

Or install from source for development:

```bash
git clone https://github.com/AMFI-Disable/OmniSuite.git
cd OmniSuite
pip install -e "src/omnishared" -e "src/omnidebate" -e "src/omniformat"
```

---

## 🚀 Key Commands

```bash
# Launch forensic research workstation
omnisuite --app debate

# Launch document compiler
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
| :--- | :--- | :--- | :--- |
| Glassmorphic dark UI | Clean white interface | Arctic blue-gray | Warm solarized palette |

Switch themes from Settings (`F5`).

---

## 🎯 Supported Debate Formats

| Format | Speeches | Style |
| :--- | :--- | :--- |
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

## 🐳 Docker Deployment

```bash
docker compose up -d
docker compose run --rm omnisuite --app debate
```

---

## 🧪 Automated Testing And Verification <a id="automated-testing"></a>

```bash
# Setup virtual environment and test dependencies
python3 -m venv .venv && source .venv/bin/activate
pip install -e "src/omnishared" -e "src/omnidebate" -e "src/omniformat"
pip install ruff pytest pytest-asyncio

# Run test suite
pytest --tb=short -q

# Code quality and formatting lint
ruff check . && ruff format --check .
```

---

## 🛡️ Privacy And Storage Guarantees <a id="privacy-and-storage"></a>

- **100% Local SQLite Storage**: All forensic research, cards, debate flows, and brief metadata are stored locally on device.
- **Zero Telemetry**: No tracking cookies, third-party network pings, or telemetry reporting.
- **Local AI Execution**: Ollama integration executes inference entirely against local models without cloud leaks.

---

## 📄 License And Terms <a id="license-and-terms"></a>

Licensed under the [MIT License](license). Copyright (c) 2026 AMFI-Disable.
