"""Configurable keybindings system for OmniSuite.

Loads user keybindings from ``config/keybindings.yaml``, falling
back to sensible defaults.  Supports a vim-mode toggle that
remaps navigation keys to hjkl.
"""

from __future__ import annotations

import os
from typing import Dict, Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

from omnishared.config.config import get_workspace_path


# ─── File path ──────────────────────────────────────────────────────────────────
KEYBINDINGS_FILE: str = get_workspace_path("config", "keybindings.yaml")


# ─── Default keybindings ────────────────────────────────────────────────────────
_DEFAULTS: Dict[str, Dict[str, str]] = {
    "navigation": {
        "up": "up",
        "down": "down",
        "left": "left",
        "right": "right",
        "page_up": "pageup",
        "page_down": "pagedown",
        "home": "home",
        "end": "end",
        "back": "escape",
        "select": "enter",
        "tab_next": "tab",
        "tab_prev": "shift+tab",
    },
    "search": {
        "open_search": "ctrl+f",
        "next_result": "ctrl+n",
        "prev_result": "ctrl+p",
        "clear_search": "escape",
    },
    "card_management": {
        "new_card": "ctrl+n",
        "delete_card": "ctrl+d",
        "edit_card": "ctrl+e",
        "duplicate_card": "ctrl+shift+d",
        "tag_card": "ctrl+t",
        "export_card": "ctrl+x",
        "toggle_star": "ctrl+s",
    },
    "timer": {
        "start_pause": "space",
        "reset": "r",
        "next_speech": "n",
        "prev_speech": "p",
    },
    "global": {
        "quit": "ctrl+q",
        "help": "f1",
        "command_palette": "ctrl+shift+p",
        "toggle_sidebar": "ctrl+b",
        "toggle_dark_mode": "ctrl+shift+t",
        "quick_notes": "ctrl+shift+n",
    },
}

# Vim-mode overrides for navigation keys
_VIM_OVERRIDES: Dict[str, str] = {
    "up": "k",
    "down": "j",
    "left": "h",
    "right": "l",
    "page_up": "ctrl+u",
    "page_down": "ctrl+d",
    "home": "g,g",
    "end": "shift+g",
}

# Module-level cache to avoid re-reading YAML on every call
_cache: Optional[Dict] = None


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge *override* into a copy of *base*.

    Values in *override* take precedence.  Nested dicts are merged
    rather than replaced wholesale.
    """
    merged = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_keybindings(*, force_reload: bool = False) -> Dict:
    """Load keybindings from ``config/keybindings.yaml``.

    Returns the merged result of built-in defaults and any user
    overrides.  The file is only read once and cached; pass
    ``force_reload=True`` to re-read from disk.

    Returns:
        Nested dict with sections: navigation, search,
        card_management, timer, global, plus a top-level
        ``vim_mode`` boolean.
    """
    global _cache  # noqa: PLW0603
    if _cache is not None and not force_reload:
        return _cache

    # Start with built-in defaults
    bindings: Dict = {
        "vim_mode": False,
        **{section: dict(keys) for section, keys in _DEFAULTS.items()},
    }

    # Layer on YAML overrides
    if yaml and os.path.exists(KEYBINDINGS_FILE):
        try:
            with open(KEYBINDINGS_FILE) as fh:
                user_cfg = yaml.safe_load(fh)
            if isinstance(user_cfg, dict):
                bindings = _deep_merge(bindings, user_cfg)
        except Exception:
            pass  # corrupt / unreadable — stick with defaults

    # Apply vim-mode navigation remapping if enabled
    if bindings.get("vim_mode", False):
        nav = bindings.get("navigation", {})
        for action, vim_key in _VIM_OVERRIDES.items():
            nav[action] = vim_key
        bindings["navigation"] = nav

    _cache = bindings
    return bindings


def get_keybinding(action: str, section: str | None = None) -> str:
    """Look up the key string for a named action.

    The *action* is searched in the given *section* first, then across
    all sections if *section* is ``None`` or the action was not found
    in the specified section.

    Args:
        action: Keybinding action name (e.g. ``"new_card"``).
        section: Optional section to search first (e.g. ``"card_management"``).

    Returns:
        Key string (e.g. ``"ctrl+n"``), or an empty string when the
        action is unknown.
    """
    bindings = load_keybindings()

    # Try the explicit section first
    if section and section in bindings:
        mapping = bindings[section]
        if isinstance(mapping, dict) and action in mapping:
            return mapping[action]

    # Fall through all sections
    for _sec, mapping in bindings.items():
        if isinstance(mapping, dict) and action in mapping:
            return mapping[action]

    return ""


def is_vim_mode() -> bool:
    """Return whether vim-mode navigation is currently enabled.

    Reads from the cached keybindings; call ``load_keybindings()``
    first if the file may have changed on disk.
    """
    bindings = load_keybindings()
    return bool(bindings.get("vim_mode", False))
