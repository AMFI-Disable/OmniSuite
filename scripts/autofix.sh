#!/bin/bash
# Standalone OmniFormat Markdown Auto-Fix Automator
# Usage: ./scripts/autofix.sh path/to/document.md

if [ -z "$1" ]; then
    echo "❌ Error: Please specify a markdown file path."
    echo "Usage: $0 path/to/document.md"
    exit 1
fi

TARGET_FILE="$1"

# Check if file exists
if [ ! -f "$TARGET_FILE" ]; then
    echo "❌ Error: File '$TARGET_FILE' does not exist."
    exit 1
fi

# Resolve absolute path of file and directory
ABS_DIR=$(cd "$(dirname "$TARGET_FILE")" && pwd)
ABS_FILE="$ABS_DIR/$(basename "$TARGET_FILE")"

# 1. Change directory to the target file's location
echo "📂 Changing directory: cd \"$ABS_DIR\""
cd "$ABS_DIR" || exit 1

# 2. Run the headless OmniFormat auto-fix command
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 "$PROJECT_DIR/omnisuite" --app format --fix "$(basename "$ABS_FILE")"
