#!/usr/bin/env bash
set -euo pipefail

OPENCODE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHELL_RC="${HOME}/.zshrc"
SHELL_PROFILE="${HOME}/.zprofile"
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

install_to_file() {
  local target_file="$1"

  if [[ -f "$target_file" ]] && grep -qF "$MARKER_BEGIN" "$target_file"; then
    printf 'already installed in %s\n' "$target_file"
    return 0
  fi

  cat >> "$target_file" <<EOF

$MARKER_BEGIN
export PATH="$OPENCODE_DIR/bin:\$PATH"
$MARKER_END
EOF

  printf 'installed launcher path in %s\n' "$target_file"
}

install_to_file "$SHELL_RC"

if [[ "${SHELL:-}" != *"bash" ]]; then
  install_to_file "$SHELL_PROFILE"
fi

printf 'restart terminal or run: source %s\n' "$SHELL_RC"
