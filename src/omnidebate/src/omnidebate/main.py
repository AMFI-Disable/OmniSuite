import datetime
import sys
import traceback

from omnishared.config import run_setup_dirs

from omnidebate.core.database import setup_db
from omnidebate.ui.app import OmniDebate


def main():
    """Main Entry Point with Global Fallback Error Handling."""
    try:
        run_setup_dirs()
        setup_db()
        app = OmniDebate()
        app.run()
    except Exception as e:
        # Emergency Forensic Logging
        error_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_log = f"--- OMNIDEBATE EMERGENCY ERROR LOG [{error_time}] ---\n"
        error_log += f"EXCEPTION: {str(e)}\n"
        error_log += traceback.format_exc()
        error_log += "------------------------------------------------------\n"

        with open("emergency_error.log", "a") as f:
            f.write(error_log)

        # Clean Terminal Fallback Output
        print("\n\n" + "!" * 60)
        print("🏛️  OMNIDEBATE EMERGENCY FALLBACK SYSTEM")
        print("!" * 60)
        print(f"\nCRITICAL ERROR DETECTED: {str(e)}")
        print("\nForensic details have been logged to: emergency_error.log")
        print("\nRECOMMENDED ACTION:")
        print("1. Check the log file for specific database or UI conflicts.")
        print("2. Run 'python3 -m omnidebate.smoke_test' to verify core integrity.")
        print("3. Restart the workstation: 'python3 vault.py'")
        print("!" * 60)
        print("© 2026 OmniSuite. Built for the Digital Grandmaster.")
        print("!" * 60 + "\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
