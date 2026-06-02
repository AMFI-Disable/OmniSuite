#!/usr/bin/env python3
import sys
import os


def main():
    if len(sys.argv) < 2:
        print("Usage: before_commit_hook.py <aux_file>", file=sys.stderr)
        sys.exit(1)

    aux_file = sys.argv[1]
    if not aux_file or not os.path.exists(aux_file):
        if not aux_file:
            sys.exit(0)
        print(f"Error: Auxiliary file '{aux_file}' not found.", file=sys.stderr)
        sys.exit(1)

    with open(aux_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find checkin-comment block
    try:
        start_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == "checkin-comment":
                start_idx = i + 1
                break

        if start_idx != -1:
            comment_lines = lines[start_idx:]
            original_comment = "".join(comment_lines).strip()

            # Check if there are any uppercase characters
            if any(char.isupper() for char in original_comment):
                print(
                    "\n❌ ERROR: Commit message must be in all lowercase letters.",
                    file=sys.stderr,
                )
                print(f'Rejected message: "{original_comment}"\n', file=sys.stderr)
                sys.exit(1)
    except SystemExit:
        sys.exit(1)
    except Exception as e:
        print(f"Error in hook script: {e}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
