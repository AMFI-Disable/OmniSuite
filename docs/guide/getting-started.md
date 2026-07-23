# Getting Started with OmniSuite

Welcome to **OmniSuite** — the Digital Grandmaster Ecosystem for competitive forensicians, debaters, and researchers.

## Installation

### From PyPI (Recommended)

```bash
pip install omnisuite
```

### From Source

```bash
git clone https://github.com/amfi-disable/OmniSuite.git
cd OmniSuite
pip install -e "src/omnishared" -e "src/omnidebate" -e "src/omniformat"
```

### Verify Installation

```bash
omnisuite --version
```

## Quick Start

### Launch OmniDebate (Research Workstation)

```bash
omnisuite --app debate
```

### Launch OmniFormat (Document Compiler)

```bash
omnisuite --app format
```

## First Run

On first launch, OmniSuite will:

1. **Create data directories** — `data/debates/`, `data/backups/`, `data/exports/`
2. **Initialize the database** — Creates and migrates the SQLite vault
3. **Display the splash screen** — Shows system status and navigation hints

## Creating Your First Motion

1. Launch OmniDebate: `omnisuite --app debate`
2. Press `n` to create a new motion (resolution)
3. Enter the motion text (e.g., "Resolved: The United States should adopt a carbon tax")
4. Press `Enter` to confirm

## Adding Evidence Cards

1. Select a motion from the main screen
2. Press `a` to add a new card
3. Fill in:
   - **Tag**: A short claim (e.g., "Carbon tax reduces emissions 40%")
   - **Citation**: Author, year, source
   - **Side**: AFF (Affirmative) or NEG (Negative)
   - **Text**: The full evidence text
4. Press `Save` to add the card to your vault

## Navigation

| Key | Action |
|-----|--------|
| `↑/↓` | Navigate lists |
| `Enter` | Select / confirm |
| `Escape` | Go back |
| `?` | Help screen |
| `Ctrl+P` | Command palette |
| `s` | Search |
| `a` | Add card |
| `e` | Edit selected |
| `d` | Delete selected |
| `x` | Export brief |

## AI Integration (Optional)

OmniSuite integrates with [Ollama](https://ollama.ai) for local AI features:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3

# Start the server
ollama serve
```

OmniSuite will auto-detect the Ollama server and enable AI features like card summarization, counter-argument generation, and case analysis.

## Next Steps

- [Card Management Guide](card-management.md)
- [Debate Flow Guide](debate-flow.md)
- [Export & Import Guide](export-import.md)
- [AI Features Guide](ai-features.md)
- [Keyboard Shortcuts Reference](keybindings.md)
