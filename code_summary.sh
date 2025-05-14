#!/bin/bash
# code_summary
#
# This script creates a code_summary.txt file in the target directory,
# containing the content of “relevant” source files (e.g. .ts, .cs, .py, etc.).
# It recurses into subdirectories and, if inside a Git repo, skips files/folders that are gitignored.
#
# Installation: 
#  - sudo mv ~/code_summary /usr/local/bin/code_summary
#  - sudo chmod +x /usr/local/bin/code_summary
# Usage: code_summary <target_directory>
# Example:
#   cd /path/to/your/repo
#   code_summary apps/api
#https://gist.github.com/juangcarmona/56698aaece7dde249550eb5b385bdfb9
# --- Check for parameter ---

if [ $# -lt 1 ]; then
    echo "Usage: $0 <target_directory>"
    exit 1
fi

TARGET_DIR="$(realpath "$1")"
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: '$TARGET_DIR' is not a directory."
    exit 1
fi

# Output file (customizable via env var)
OUTPUT="${CODE_SUMMARY_OUTPUT:-$TARGET_DIR/code_summary.txt}"
> "$OUTPUT"

ORIG_DIR="$(pwd)"
cd "$TARGET_DIR" || { echo "Cannot cd into $TARGET_DIR"; exit 1; }

# === Configuration ===
EXTENSIONS=("Dockerfile" "*.md" "*.ts" "*.js" "*.cs" "*.py" "*.php" "*.java" "*.c" "*.cpp" "*.go" "*.rb" "*.html" "*.css" "*.xml" "*.json" "*.sh")
MAX_SIZE=500000  # 500KB size cap per file (adjust or disable if needed)

# Convert EXTENSIONS to a find-compatible string
FIND_EXPR=$(printf -- '-iname "%s" -o ' "${EXTENSIONS[@]}")
FIND_EXPR="(${FIND_EXPR::-4})"  # Remove trailing -o

# Extension matcher (for git ls-files)
matches_extension() {
    local file="$1"
    for pattern in "${EXTENSIONS[@]}"; do
        [[ "$file" == $pattern ]] && return 0
    done
    return 1
}

echo "Writing summary to: $OUTPUT"

if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "Git repository detected. Using Git to get files..."
    git ls-files --exclude-standard --others --cached -z . | while IFS= read -r -d '' file; do
        if matches_extension "$file" && [ -s "$file" ] && [ "$(stat -c%s "$file")" -le "$MAX_SIZE" ]; then
            echo "==== $file ====" >> "$OUTPUT"
            cat "$file" >> "$OUTPUT"
            echo -e "\n\n" >> "$OUTPUT"
        fi
    done
else
    echo "Not a Git repo. Using find to locate files..."
    FIND_EXPR=$(printf -- '-iname "%s" -o ' "${EXTENSIONS[@]}")
    FIND_EXPR="${FIND_EXPR::-4}"
    eval "find . -type f \\( $FIND_EXPR \\) -size -${MAX_SIZE}c -print0" | while IFS= read -r -d '' file; do
        echo "==== $file ====" >> "$OUTPUT"
        cat "$file" >> "$OUTPUT"
        echo -e "\n\n" >> "$OUTPUT"
    done
fi

cd "$ORIG_DIR"
echo "✅ Code summary written to: $OUTPUT"