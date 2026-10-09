"""Re-export omnisuite.web for monorepo path mapping compatibility."""

from omnisuite.web import (
    OmniWebServer,
    VaultWebHandler,
    main,
    notify_subscribers,
    run_web_server,
)

__all__ = [
    "OmniWebServer",
    "VaultWebHandler",
    "notify_subscribers",
    "run_web_server",
    "main",
]
