# Contributing To OmniSuite

Thank you for your interest in contributing to OmniSuite!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/AMFI-Disable/OmniSuite.git
cd OmniSuite

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e "src/omnishared"
pip install -e "src/omnidebate"
pip install -e "src/omniformat"
pip install ruff pytest pytest-asyncio mypy

# Verify
pytest --tb=short -q
```

## Code Style

- **Formatter**: ruff format (double quotes, 100-char line length)
- **Linter**: ruff check
- **Commit messages**: Lowercase conventional commits — `type:summary`
  - `feat:add debate flow screen`
  - `fix:resolve timer reset bug`
  - `refactor:extract card validation logic`
  - `docs:update getting started guide`
  - `test:add flow screen snapshot tests`
  - `chore:update dependencies`
  - `build:configure pyinstaller spec`

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_database.py
```

## Project Structure

See [Architecture](architecture.md) for the full codebase layout.

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make your changes
4. Run tests: `pytest`
5. Run linter: `ruff check . && ruff format --check .`
6. Commit with conventional message: `git commit -m "feat:add my feature"`
7. Push and open a PR

## Adding A New Screen

1. Create `src/omnidebate/src/omnidebate/ui/screens/my_screen.py`
2. Subclass `ModalScreen` or `Screen`
3. Implement `compose()` method
4. Add keybindings to `config/keybindings.yaml`
5. Wire it up in `app.py`
6. Add tests in `tests/`

## Adding A New Widget

1. Create `src/omnishared/src/omnishared/ui/widgets/my_widget.py`
2. Subclass `Widget` or `Static`
3. Export from `__init__.py`
4. Add CSS styles to the theme files
