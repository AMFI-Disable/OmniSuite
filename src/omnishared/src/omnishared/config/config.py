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
        "ai": {
            "provider": "ollama",
            "fallbacks": ["gemini", "openai"],
            "ollama_endpoint": "http://localhost:11434",
            "ollama_model": "llama3",
            "openai_api_key": "",
            "openai_model": "gpt-4o-mini",
            "openai_base_url": "https://api.openai.com/v1",
            "gemini_api_key": "",
            "gemini_model": "gemini-2.5-flash",
        },
    }
    config = defaults
    if yaml and os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                loaded = yaml.safe_load(f) or {}
                ai_merged = {**defaults["ai"], **loaded.get("ai", {})}
                config = {**defaults, **loaded, "ai": ai_merged}
        except Exception:
            pass

    # Environment variable overrides
    if "ai" not in config:
        config["ai"] = {}
    if "AI_PROVIDER" in os.environ:
        config["ai"]["provider"] = os.environ["AI_PROVIDER"]
    if "AI_FALLBACKS" in os.environ:
        config["ai"]["fallbacks"] = [
            f.strip() for f in os.environ["AI_FALLBACKS"].split(",") if f.strip()
        ]
    if "OLLAMA_ENDPOINT" in os.environ:
        config["ai"]["ollama_endpoint"] = os.environ["OLLAMA_ENDPOINT"]
    if "OLLAMA_MODEL" in os.environ:
        config["ai"]["ollama_model"] = os.environ["OLLAMA_MODEL"]
    if "OPENAI_API_KEY" in os.environ:
        config["ai"]["openai_api_key"] = os.environ["OPENAI_API_KEY"]
    if "OPENAI_MODEL" in os.environ:
        config["ai"]["openai_model"] = os.environ["OPENAI_MODEL"]
    if "OPENAI_BASE_URL" in os.environ:
        config["ai"]["openai_base_url"] = os.environ["OPENAI_BASE_URL"]
    if "GEMINI_API_KEY" in os.environ:
        config["ai"]["gemini_api_key"] = os.environ["GEMINI_API_KEY"]
    elif "GOOGLE_API_KEY" in os.environ:
        config["ai"]["gemini_api_key"] = os.environ["GOOGLE_API_KEY"]
    if "GEMINI_MODEL" in os.environ:
        config["ai"]["gemini_model"] = os.environ["GEMINI_MODEL"]

    return config


def save_config(config: dict) -> None:
    if not yaml:
        return
    try:
        with open(CONFIG_FILE, "w") as f:
            yaml.safe_dump(config, f, default_flow_style=False)
    except Exception:
        pass
