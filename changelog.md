# Changelog

All notable changes to OmniSuite will be documented in this file.

---

## [1.0.1] - 2026-10-10

### 🔧 Repository & Metadata Alignment

- Updated repository ownership and documentation endpoints to `AMFI-Disable/OmniSuite`.
- Verified multi-platform CI matrix across Ubuntu and macOS runtimes.
- Refreshed package URLs in `pyproject.toml` and documentation guides.

---

## [1.0.0] - 2026-07-23

### 🏛️ Initial Public Release

The first production release of OmniSuite — the Digital Grandmaster Ecosystem for competitive forensicians, debaters, and researchers.

### Added

#### Core Platform

- Unified CLI entry point: `omnisuite --app debate|format`
- PyPI packaging: `pip install omnisuite`
- MIT license
- CI/CD pipeline (GitHub Actions: test, lint, release)
- Docker containerization with Ollama AI orchestration

#### OmniDebate — Research Workstation

- 4-zone cyber-dark TUI interface with glassmorphic design
- Card management: add, edit, delete, search, bulk operations
- Boolean search with AND/OR/NOT operators and fuzzy matching
- FTS5 full-text search with ranking
- Card tagging system with multi-tag support
- Card rating (1–5 stars)
- Card edit history tracking
- OracleEngine heuristic analysis (10 scoring dimensions)
- Speech document assembly
- Debate flow system (multi-column argument tracking)
- Argument tree visualization
- Round timer widget with format-aware timing
- Drill mode with mastery tracking and WPM speed practice
- Command palette with fuzzy filtering
- Breadcrumb navigation
- Rich status bar with live vault statistics

#### OmniFormat — Document Compiler

- Verbatim .docx export
- CaseXC .docx export
- Standard Brief .md export
- Interactive Brief .html export
- Formatting compliance engine

#### AI Integration (Ollama)

- Card summarization
- Counter-argument generation
- Impact chain analysis
- Case strength scoring
- Evidence gap finder
- Case outline generator
- Cross-examination question generator
- Clarity rewriter
- Interactive AI assistant with slash commands

#### Data Import/Export

- CSV import/export
- JSON vault backup/restore
- DOCX import (with formatting preservation)
- URL ingest (auto-extract article text)
- PDF text extraction
- Clipboard paste
- Export history logging

#### Debate Formats

- Public Forum
- Lincoln-Douglas
- Policy
- British Parliamentary
- World Schools Style
- Asian Parliamentary
- Canadian National
- European Parliamentary
- Karl Popper

#### UX

- Theme system: cyber-dark (default), light, nord, solarized
- Configurable keybindings with YAML config
- Vim-mode navigation (hjkl)
- Dynamic keybinding hints in footer
- Mouse support

#### Shared Infrastructure

- SQLite database with Alembic migrations
- Dynamic format loading from JSON config
- Shared Textual widget library (GaugeBar, SparklineBar, HeatmapGrid, RoundTimer, Breadcrumb, StatusBar, QuickNotes, SideRibbon, SystemLog)
- YAML/JSON configuration system
- Automated database backup on export

#### Documentation

- Getting started guide
- Card management guide
- Debate flow guide
- AI features guide
- Export/import guide
- Keyboard shortcuts reference
- Architecture overview
- Contributing guide
