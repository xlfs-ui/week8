#!/usr/bin/env sh
set -eu

# Always run from the script directory.
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR"

make run