# Architecture

## Overview

OmniSuite is a Python monorepo containing three packages that share a common data foundation:

```
OmniSuite/
├── src/
│   ├── omnisuite/          # CLI entry point (pip install target)
│   ├── omnidebate/         # OmniDebate — research workstation
│   │   └── src/omnidebate/
│   │       ├── core/       # Business logic, database, AI, export
│   │       └── ui/         # Textual screens and widgets
│   ├── omniformat/         # OmniFormat — document compiler
│   │   └── src/omniformat/
│   │       ├── core/       # Compiler, compliance engine
│   │       └── ui/         # Textual screens
│   └── omnishared/         # Shared libraries
│       └── src/omnishared/
│           ├── ai/         # Ollama client
│           ├── config/     # Config loader, path management
│           ├── database/   # SQLite manager, connection, extended ops
│           ├── formats/    # Debate format loader
│           └── ui/         # Shared Textual widgets and themes
├── config/                 # YAML/JSON configuration files
├── data/                   # Runtime data (debates, backups, migrations)
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── tests/                  # Test suite
```

## Package Dependencies

```
omnisuite (CLI)
    ├── omnidebate
    │   └── omnishared
    └── omniformat
        └── omnishared
```

`omnishared` is the foundation layer — it owns the database, config, AI client, and shared UI widgets. Both `omnidebate` and `omniformat` depend on it.

## Data Flow

```
User Input → Textual TUI → Screen Handler → Core Logic → Database
                                                ↕
                                           AI (Ollama)
                                                ↕
                                         Export Engine → .docx / .html / .md / .csv
```

## Database

- **Engine**: SQLite with FTS5 full-text search
- **ORM**: Raw `sqlite3` with `row_factory = sqlite3.Row`
- **Migrations**: Alembic (config in `config/alembic.ini`)
- **Path**: `data/debates/vault.db` (configurable via `EVIDENCE_VAULT_DB` env var)

### Schema

| Table | Purpose |
|-------|---------|
| `motions` | Debate resolutions/topics |
| `cards` | Evidence cards with metadata |
| `cards_fts` | FTS5 virtual table for full-text search |
| `card_tags` | Multi-tag support for cards |
| `card_history` | Edit tracking / versioning |
| `trash` | Soft-deleted cards for recovery |
| `metadata` | Key-value store for app state |
| `flows` | Debate flow data (JSON columns) |
| `export_log` | Export history tracking |

## UI Framework

- **Textual** (Python TUI framework)
- Custom widgets in `omnishared/ui/widgets/`: GaugeBar, SparklineBar, HeatmapGrid, RoundTimer, Breadcrumb, StatusBar, QuickNotes, SideRibbon, SystemLog
- CSS themes in `config/themes/`
- Screens are `ModalScreen` or `Screen` subclasses

## Configuration

- `config/config.yaml` — Runtime settings (timer, export, UI, AI)
- `config/formats.json` — Debate format definitions
- `config/keybindings.yaml` — Customizable keyboard shortcuts
- `config/themes/` — TCSS theme files
