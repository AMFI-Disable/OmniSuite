export const siteConfig = {
  "title": "OmniSuite",
  "repoUrl": "https://github.com/AMFI-Disable/OmniSuite",
  "category": "CLI & Developer Tool",
  "accent": "#FBC02D",
  "tagline": "High-fidelity terminal workstation and Textual TUI engineered for competitive debate research, card retrieval, and case compilation.",
  "primaryCta": {
    "label": "Quick Install",
    "href": "#quick-start"
  },
  "secondaryCta": {
    "label": "View on GitHub",
    "href": "https://github.com/AMFI-Disable/OmniSuite"
  },
  "quickCmd": "git clone https://github.com/AMFI-Disable/OmniSuite.git && cd OmniSuite && uv sync && uv run omnisuite",
  "features": [
    {
      "title": "OmniDebate Workstation",
      "desc": "Instant AFF/NEG card search, tagging, and crossfire retrieval inside a fast Textual terminal UI."
    },
    {
      "title": "OmniFormat Compiler",
      "desc": "Automated brief compilation and document formatting processor for tournament-ready evidence packets."
    },
    {
      "title": "SQLite + SQLAlchemy",
      "desc": "Reliable local-first relational storage backed by SQLAlchemy ORM and Alembic schema migrations."
    },
    {
      "title": "Docker & Theme Support",
      "desc": "Ships with Docker Compose support, custom TUI themes, and optional AI-assisted research workflows."
    }
  ],
  "steps": [
    {
      "title": "Ingest & Index Evidence",
      "desc": "Parses debate cards, citations, and tags into a structured local SQLite database."
    },
    {
      "title": "Instant Crossfire Search",
      "desc": "Filters AFF/NEG arguments in milliseconds via keyboard-driven Textual panels."
    },
    {
      "title": "Compile Tournament Briefs",
      "desc": "Exports formatted cases and evidence blocks through OmniFormat."
    }
  ],
  "installCmds": [
    {
      "label": "Install with uv (Recommended)",
      "cmd": "git clone https://github.com/AMFI-Disable/OmniSuite.git && cd OmniSuite && uv sync"
    },
    {
      "label": "Launch Workstation",
      "cmd": "uv run omnisuite"
    }
  ],
  "requirements": [
    "Python 3.10+",
    "macOS or Linux (or Docker)",
    "uv package manager"
  ]
} as const;
