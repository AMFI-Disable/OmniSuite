import argparse
import datetime
import os
import sys
import traceback

from omnishared.config import run_setup_dirs

from omniformat.ui.app import OmniFormat


def main() -> None:
    """Main Entry Point with Global Fallback Error Handling."""
    parser = argparse.ArgumentParser(description="OmniFormat Standalone Workstation")
    parser.add_argument("--app", help=argparse.SUPPRESS)
    parser.add_argument("--file", help="Path to Markdown file to format")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix markdownlint errors in-place and exit",
    )
    parser.add_argument("file_path", nargs="?", help="Optional path to Markdown file to format")
    args, unknown = parser.parse_known_args()

    target_file = args.file if args.file else args.file_path

    if args.fix:
        if not target_file:
            print("❌ Error: Please specify a file path to fix.")
            sys.exit(1)
        if not os.path.exists(target_file):
            print(f"❌ Error: File '{target_file}' does not exist.")
            sys.exit(1)
        try:
            from omniformat.core.compiler import prettify_markdown_file

            prettify_markdown_file(target_file)
            print(f"✅ Automatically fixed markdownlint errors in-place: {target_file}")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Failed to auto-fix errors: {e}")
            sys.exit(1)

    try:
        run_setup_dirs()
        app = OmniFormat(target_file=target_file)
        app.run()
    except Exception as e:
        error_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_log = f"--- OMNIFORMAT EMERGENCY ERROR LOG [{error_time}] ---\n"
        error_log += f"EXCEPTION: {str(e)}\n"
        error_log += traceback.format_exc()
        error_log += "------------------------------------------------------\n"

        with open("emergency_error_format.log", "a") as f:
            f.write(error_log)

        print("\n\n" + "!" * 60)
        print("🏛️  OMNIFORMAT EMERGENCY FALLBACK SYSTEM")
        print("!" * 60)
        print(f"\nCRITICAL ERROR DETECTED: {str(e)}")
        print("\nForensic details have been logged to: emergency_error_format.log")
        print("!" * 60)
        print("© 2026 OmniSuite. Built for the Digital Grandmaster.")
        print("!" * 60 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
