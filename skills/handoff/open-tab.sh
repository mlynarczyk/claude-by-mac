#!/usr/bin/env bash
# Open a new terminal tab running `claude` with a handoff prompt as its first message,
# in whichever terminal this session runs in: Orca (macOS or Linux) or iTerm (macOS).
#
# Usage: open-tab.sh <repo-root> <prompt-file> [extra claude args...]
# Exits 2 when the terminal is unsupported, so the caller prints the prompt instead.
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "usage: open-tab.sh <repo-root> <prompt-file> [claude args...]" >&2
  exit 64
fi
root=$1 file=$2
shift 2
[ -d "$root" ] || { echo "open-tab: no such directory: $root" >&2; exit 1; }
[ -r "$file" ] || { echo "open-tab: cannot read: $file" >&2; exit 1; }

# $(cat …) is left unexpanded here and expands in the new tab's shell, so backticks
# and $ in the prompt reach claude as text.
args=""
for a in "$@"; do args+=" $(printf '%q' "$a")"; done
cmd="cd $(printf '%q' "$root") && claude${args} \"\$(cat $(printf '%q' "$file"))\""

if [ "${TERM_PROGRAM:-}" = "Orca" ] || [ -n "${ORCA_WORKTREE_ID:-}" ]; then
  orca="${ORCA_CLI_BIN_DIR:+$ORCA_CLI_BIN_DIR/orca}"
  [ -x "${orca:-}" ] || orca=$(command -v orca) || { echo "open-tab: orca CLI not found" >&2; exit 1; }
  title="handoff: $(basename "$file" .md)"
  title=${title/handoff: handoff-/handoff: }
  # path: needs the root registered in Orca; otherwise open it in this tab's workspace,
  # since the cd in the command picks the directory either way.
  "$orca" terminal create --worktree "path:$root" --title "$title" --command "$cmd" --focus >/dev/null 2>&1 ||
    "$orca" terminal create ${ORCA_WORKTREE_ID:+--worktree "id:$ORCA_WORKTREE_ID"} \
      --title "$title" --command "$cmd" --focus >/dev/null
  echo "opened an Orca tab"
  exit 0
fi

if [ "${TERM_PROGRAM:-}" = "iTerm.app" ] && [ "$(uname)" = "Darwin" ]; then
  osascript - "$cmd" <<'EOF' >/dev/null
on run argv
  tell application "iTerm"
    activate
    tell current window
      create tab with default profile
      tell current session to write text (item 1 of argv)
    end tell
  end tell
end run
EOF
  echo "opened an iTerm tab"
  exit 0
fi

echo "open-tab: unsupported terminal (TERM_PROGRAM=${TERM_PROGRAM:-unset}); paste the prompt by hand" >&2
exit 2
