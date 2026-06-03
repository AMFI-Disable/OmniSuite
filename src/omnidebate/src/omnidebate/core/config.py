# Proxy to omnishared.config to preserve backwards compatibility for apps/omnidebate

from omnishared.config import (
    DEBATES_DIR,
    BACKUPS_DIR,
    EXPORTS_DIR,
    TRASH_FILE,
    FORMATS_FILE,
    CONFIG_FILE,
    run_setup_dirs,
)
from omnishared.formats.loader import load_formats


# Allow overriding CONFIG_FILE at module level (like the tests do)
def load_config() -> dict:
    import omnishared.config.config as shared_config

    orig = shared_config.CONFIG_FILE
    shared_config.CONFIG_FILE = CONFIG_FILE
    try:
        return shared_config.load_config()
    finally:
        shared_config.CONFIG_FILE = orig


def save_config(config: dict) -> None:
    import omnishared.config.config as shared_config

    orig = shared_config.CONFIG_FILE
    shared_config.CONFIG_FILE = CONFIG_FILE
    try:
        shared_config.save_config(config)
    finally:
        shared_config.CONFIG_FILE = orig


__all__ = [
    "DEBATES_DIR",
    "BACKUPS_DIR",
    "EXPORTS_DIR",
    "TRASH_FILE",
    "FORMATS_FILE",
    "CONFIG_FILE",
    "run_setup_dirs",
    "load_config",
    "save_config",
    "load_formats",
]
