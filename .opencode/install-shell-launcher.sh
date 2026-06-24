#!/usr/bin/env bash
set -euo pipefail

OPENCODE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHELL_RC="${HOME}/.zshrc"
MARKER_BEGIN="# >>> opencode mlflow ai-studio launcher >>>"
MARKER_END="# <<< opencode mlflow ai-studio launcher <<<"

if [[ "${SHELL:-}" == *"bash" ]]; then
  SHELL_RC="${HOME}/.bashrc"
fi

if [[ ! -f "$OPENCODE_DIR/bin/opencode" ]]; then
  printf 'error: launcher not found: %s\n' "$OPENCODE_DIR/bin/opencode" >&2
  exit 1
fi

chmod +x "$OPENCODE_DIR/bin/opencode"

if [[ -f "$SHELL_RC" ]] && grep -qF "$MARKER_BEGIN" "$SHELL_RC"; then
  printf 'already installed in %s\n' "$SHELL_RC"
  exit 0
fi

cat >> "$SHELL_RC" <<EOF

$MARKER_BEGIN
export PATH="$OPENCODE_DIR/bin:\$PATH"
$MARKER_END
EOF

printf 'installed launcher path in %s\n' "$SHELL_RC"
printf 'restart terminal or run: source %s\n' "$SHELL_RC"
