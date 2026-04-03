# 🏛️ Evidence Vault — v4.0.0 "Grand Nexus"
> **High-Performance Debate Operating System**  
> A full-screen TUI cockpit for the competitive debate circuit.

---

## ✨ Features

| Module | Feature |
|---|---|
| **Nexus Dashboard** | 3-pane TUI — Motion Navigator · Evidence Feed · Live Prep HUD |
| **Chronos Engine** | Format profiles: Public Forum · Lincoln-Douglas · Policy |
| **Timer** | Per-speech countdown + real-time Prep Reservoir with next/reset |
| **Evidence CRUD** | Add · Edit · Soft Delete · Undo with auto-snapshot `.bak` files |
| **Boolean Search** | `AND / OR / NOT` omni-search across active + archived motions |
| **Smart Cite** | Auto-generate standardised citations from author/year inputs |
| **Spaced Repetition** | Gladiator Drill mode with 1–5 Mastery ratings |
| **Web Ingest** | Scrape any URL → auto-fill evidence card |
| **Impact Mapping** | ASCII tree: Economic · Social · Environmental classification |
| **Export** | Markdown brief with TOC, Tier-3 ⭐ prioritisation, impact maps |
| **Soft Delete / Trash** | Recover deleted cards with `Ctrl+Z` |
| **Auto-Snapshot** | `.bak` files created before every destructive operation |

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_HANDLE/Evidence-Vault-CLI.git
cd Evidence-Vault-CLI

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch
python3 vault.py
```

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|---|---|
| `N` | New evidence card |
| `S` | Boolean Omni-Search |
| `D` | Gladiator Drill mode |
| `W` | Web Ingest (scrape URL) |
| `I` | Impact Map for selected card |
| `E` | Export Markdown brief |
| `M` | New debate motion |
| `Ctrl+Z` | Undo last card deletion |
| `Q` | Quit |

---

## 📂 Project Structure

```
Evidence-Vault-CLI/
├── vault.py          # Main TUI application
├── formats.json      # Debate format profiles (PF · LD · Policy)
├── config.yaml       # User preferences
├── requirements.txt  # Python dependencies
├── debates/          # Motion JSON files
│   └── archives/     # Archived motions
├── backups/          # Auto-snapshot .bak files
└── exports/          # Generated Markdown briefs
```

---

## 🗂️ Data Schema (v4.0 — backward compatible with v3.x)

```json
{
  "id": 1,
  "tag": "Trade deficits reduce GDP",
  "citation": "Smith (2023), \"Trade Wars\" — Brookings",
  "side": "AFF",
  "text": "...",
  "language": "EN",
  "mastery": 3,
  "tier": 2,
  "timestamp": "2026-04-03"
}
```

---

## 📦 Dependencies

- [`textual`](https://github.com/Textualize/textual) — Full-screen TUI framework  
- [`rich`](https://github.com/Textualize/rich) — Terminal rendering  
- [`requests`](https://docs.python-requests.org/) + [`beautifulsoup4`](https://www.crummy.com/software/BeautifulSoup/) — Web Ingest  
- [`pyyaml`](https://pyyaml.org/) — Config file parsing

---

*Evidence Vault v4.0.0 "Grand Nexus" — Built for champions.*
