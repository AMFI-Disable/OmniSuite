import os

try:
    import yaml
except ImportError:
    yaml = None


def find_workspace_root() -> str:
    """Traverse directories upward to find the repository workspace root containing pyproject.toml."""
    current = os.path.abspath(os.path.dirname(__file__))
    while True:
        if os.path.exists(os.path.join(current, "pyproject.toml")):
            with open(os.path.join(current, "pyproject.toml")) as f:
                content = f.read()
                if "[tool.uv.workspace]" in content or "omnisuite" in content:
                    return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.getcwd()
        current = parent


WORKSPACE_ROOT = find_workspace_root()


def get_workspace_path(*paths: str) -> str:
    return os.path.join(WORKSPACE_ROOT, *paths)


# ─── Paths ────────────────────────────────────────────────────────────────────
DEBATES_DIR = get_workspace_path("data", "debates")
BACKUPS_DIR = get_workspace_path("data", "backups")
EXPORTS_DIR = get_workspace_path("data", "exports")
TRASH_FILE = os.path.join(DEBATES_DIR, ".trash.json")
FORMATS_FILE = get_workspace_path("config", "formats.json")
CONFIG_FILE = get_workspace_path("config", "config.yaml")
ALEMBIC_INI_FILE = get_workspace_path("config", "alembic.ini")


def run_setup_dirs() -> None:
    for d in [
        DEBATES_DIR,
        BACKUPS_DIR,
        EXPORTS_DIR,
        os.path.join(DEBATES_DIR, "archives"),
    ]:
        os.makedirs(d, exist_ok=True)


def load_config() -> dict:
    defaults = {
        "version": "1.0.0",
        "timer": {"default_format": "Public Forum"},
        "export": {"auto_snapshot": True},
        "ui": {"dark_mode": True, "screen_reader_mode": False},
        "ai": {"ollama_endpoint": "http://localhost:11434", "ollama_model": "llama3"},
    }
    config = defaults
    if yaml and os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                config = {**defaults, **yaml.safe_load(f)}
        except Exception:
            pass

    # Environment variable override for container routing
    if "OLLAMA_ENDPOINT" in os.environ:
        if "ai" not in config:
            config["ai"] = {}
        config["ai"]["ollama_endpoint"] = os.environ["OLLAMA_ENDPOINT"]

    return config


def save_config(config: dict) -> None:
    if not yaml:
        return
    try:
        with open(CONFIG_FILE, "w") as f:
            yaml.safe_dump(config, f, default_flow_style=False)
    except Exception:
        pass
