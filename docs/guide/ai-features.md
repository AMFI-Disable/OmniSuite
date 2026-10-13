# AI Features

## Overview

OmniSuite integrates with **Ollama** to provide local, privacy-preserving AI capabilities for debate preparation. All AI processing runs on your machine — no data leaves your computer.

## Setup

### Install Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Or via Homebrew
brew install ollama
```

### Pull A Model

```bash
ollama pull llama3
```

### Start The Server

```bash
ollama serve
```

OmniSuite auto-detects the Ollama server at `http://localhost:11434`. To use a custom endpoint (e.g., Docker), set the environment variable:

```bash
export OLLAMA_ENDPOINT=http://ollama:11434
```

Or configure in `config/config.yaml`:

```yaml
ai:
  ollama_endpoint: "http://localhost:11434"
  ollama_model: "llama3"
```

## AI Tools

### Card Summarization
Automatically generate one-line tag summaries from card text. Useful for quickly tagging imported evidence.

### Counter-Argument Generator
Given a card, the AI suggests counter-arguments from the opposing perspective.

### Impact Chain Analysis
Identifies the uniqueness → link → internal link → impact chain in evidence.

### Case Strength Scorer
Rates the overall strength of your case with detailed explanations.

### Evidence Gap Finder
Analyzes your cards and identifies missing evidence areas.

### Case Outline Generator
Generates a draft case outline given a motion and side.

### Cross-Examination Questions
Generates strategic cross-fire or cross-examination questions based on evidence.

### Clarity Rewriter
Rewrites card text for improved clarity and persuasiveness.

## AI Assistant

Press `Ctrl+A` to open the interactive AI Assistant. You can chat with the AI about debate strategy using slash commands:

| Command | Description |
|---------|-------------|
| `/summarize` | Summarize card text |
| `/counter` | Generate counter-arguments |
| `/strengthen` | Suggest improvements |
| `/impact` | Analyze impact chain |
| `/brief` | Generate case outline |

## Docker Integration

For containerized deployment with AI:

```bash
docker compose up -d
docker compose run --rm omnisuite --app debate
```

This launches both OmniSuite and Ollama in a shared Docker network.
