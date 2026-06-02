# 🏛️ OmniSuite: Digital Grandmaster Ecosystem

[![Version](https://img.shields.io/badge/Version-1.0.0-10b981?style=for-the-badge)](#)
[![Status](https://img.shields.io/badge/Status-Stable-3b82f6?style=for-the-badge)](#)
[![Website](https://img.shields.io/badge/Website-Codeberg--Pages-ff5500?style=for-the-badge)](https://awesomeoddeven-nightkeys-lunarblink.codeberg.page/OmniDebate/)

**OmniSuite** is a unified, high-fidelity ecosystem of digital workstations designed for competitive forensicians, debaters, and researchers. It coordinates forensic research, case compiling, and tournament strategy into a seamless terminal-based cyber-dark command center.

🔗 **Explore the Live Landing Page & Heuristic Oracle Simulator**: [awesomeoddeven-nightkeys-lunarblink.codeberg.page/OmniDebate](https://awesomeoddeven-nightkeys-lunarblink.codeberg.page/OmniDebate/)

---

## ✦ The Workspace Applications

OmniSuite operates as a modular, unified workspace containing specialized applications sharing a core data foundation:

### 1. 🏛️ OmniDebate (Workstation)
A production-grade strategic research workstation. It transforms the terminal into a "Digital War Room," providing real-time forensic auditing, AI-augmented synthesis, and zero-failure resilience for live tournament environments.
* **Launch Command**: `python3 omnisuite --app debate`

### 2. 📄 OmniFormat (Document Compiler)
The automated document compiling and case formatting workstation. It interfaces directly with the shared debate database to assemble formatted briefs, minimize citation layouts, and ensure strict Verbatim/CaseXC styling compliance.
* **Launch Command**: `python3 omnisuite --app format`

---

## 🤖 Shared Intelligence & Interoperability
* **Shared Database Vault**: Both apps share a centralized SQLite database (`debates/vault.db`) managed via SQLAlchemy and versioned through Alembic migrations.
* **Dynamic Formats Library**: Dynamically load formats (Public Forum, Lincoln-Douglas, Policy) from a shared configuration database.
* **Premium TUI Design System**: Styled with a cyber-dark, glassmorphic design theme using shared Textual components (`GaugeBar`, `SparklineBar`, `HeatmapGrid`).

---

## 🛠️ Installation & Deployment

OmniSuite is built for immediate deployment. No manual environment configuration is required.

1. **Launch the Applications**:
    * Launch the Debate Workstation:
      ```bash
      python3 omnisuite --app debate
      ```
    * Launch the Document Formatter:
      ```bash
      python3 omnisuite --app format
      ```

*Note: The Autonomous Workspace Bootstrap Engine will automatically synthesize a virtual environment and register all workspace modules in editable mode on first run.*

---

## ✦ Local Version Control (Fossil)

OmniSuite is configured with **Fossil** for self-contained, serverless version control. History is preserved locally in a single-file database (`../.omnisuite.fossil`) with no online accounts needed.

* **Check Status**: See modified or untracked files:
  ```bash
  fossil status
  ```
* **View Diffs**: Inspect changes in files:
  ```bash
  fossil diff
  ```
* **Record Changes**: Commit modifications to the local database:
  ```bash
  fossil commit -m "Your commit message"
  ```
* **Interactive Dashboard**: Spin up the local web-based timeline, wiki, and ticket manager:
  ```bash
  fossil ui
  ```

---

## ✦ Docker Deployment (Ollama Orchestration)

OmniSuite is fully containerized to run the workstations alongside a local **Ollama** AI service in a single Docker Compose network.

* **Build & Start Services (Background)**:
  ```bash
  docker compose up -d
  ```
  *(This launches Ollama and builds the OmniSuite image).*
  
* **Launch OmniDebate**:
  ```bash
  docker compose run --rm omnisuite --app debate
  ```
  
* **Launch OmniFormat**:
  ```bash
  docker compose run --rm omnisuite --app format
  ```
  
* **Clean Up Containers**:
  ```bash
  docker compose down
  ```

---

*© 2026 OmniSuite. Built for the Digital Grandmaster.*
