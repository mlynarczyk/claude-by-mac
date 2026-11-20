#!/usr/bin/env bash
#
# Block until a PR needs its session, then print one line and exit.
#
# A session starts this in the background right after opening a PR; the
# harness wakes the session when it exits. What it prints, and what the
# session does about it, is in the pr-flow skill.
#
#   merged     exit 0
#   closed     exit 0, closed without merging
#   conflicts  exit 0, mergeable is CONFLICTING
#   error: …   exit 1, after 10 failed `gh` calls in a row
#   timeout    exit 2, after 24 hours of none of the above
#
# OPEN with MERGEABLE or UNKNOWN keeps polling: GitHub computes mergeability
# lazily, so UNKNOWN is normal right after another PR merges.
#
# Usage:
#   pr-watch.sh <pr-number> [interval-seconds]   (interval defaults to 60)

set -euo pipefail

pr=${1:-}
interval=${2:-60}

case "$pr" in
  '' | *[!0-9]*)
    sed -n '/^# Usage:/,/^$/p' "$0" | sed 's/^# \{0,1\}//'
    exit 64
    ;;
esac

deadline=$(($(date +%s) + 24 * 3600))
failures=0

while :; do
  if out=$(gh pr view "$pr" --json state,mergeable --jq '"\(.state) \(.mergeable)"' 2>&1); then
    failures=0
    case "$out" in
      MERGED*)
        echo merged
        exit 0
        ;;
      CLOSED*)
        echo closed
        exit 0
        ;;
      *" CONFLICTING")
        echo conflicts
        exit 0
        ;;
    esac
  else
    failures=$((failures + 1))
    if [ "$failures" -ge 10 ]; then
      echo "error: $(printf '%s' "$out" | tail -n 1)"
      exit 1
    fi
  fi

  if [ "$(date +%s)" -ge "$deadline" ]; then
    echo timeout
    exit 2
  fi
  sleep "$interval"
done
