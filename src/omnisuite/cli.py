"""OmniSuite CLI — Unified entry point for OmniDebate and OmniFormat.

Usage:
    omnisuite --app debate    Launch OmniDebate workstation
    omnisuite --app format    Launch OmniFormat document compiler
    omnisuite --version       Show version
"""

import argparse
import sys


def main(argv: list[str] | None = None) -> None:
    """Main entry point for the OmniSuite CLI."""
    parser = argparse.ArgumentParser(
        prog="omnisuite",
        description="OmniSuite — Digital Grandmaster Ecosystem",
    )
    parser.add_argument(
        "--app",
        choices=["debate", "format"],
        default="debate",
        help="launch 'debate' (OmniDebate) or 'format' (OmniFormat)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_get_version()}",
    )
    args, remaining = parser.parse_known_args(argv)

    # Import and run setup before launching any app
    from omnishared.config import run_setup_dirs
    from omnishared.database.manager import setup_db

    run_setup_dirs()
    setup_db()

    if args.app == "debate":
        from omnidebate.main import main as debate_main

        debate_main()
    elif args.app == "format":
        from omniformat.main import main as format_main

        format_main()


def _get_version() -> str:
    """Get version from package metadata or fall back to __version__."""
    try:
        from importlib.metadata import version

        return version("omnisuite")
    except Exception:
        from omnisuite import __version__

        return __version__


if __name__ == "__main__":
    main()
