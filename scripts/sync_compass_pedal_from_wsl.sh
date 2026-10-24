#!/usr/bin/env bash
# Sync ~/.openclaw/workspace → carbon-silicon-canonical when PUSH_ME.txt exists.
set -euo pipefail

WS="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
REPO="${CANONICAL_REPO:-/mnt/e/carbon-silicon-canonical}"
BRANCH="${CANONICAL_BRANCH:-main}"
MARKER="$WS/PUSH_ME.txt"

if [[ ! -f "$MARKER" ]]; then
  echo "No PUSH_ME.txt under $WS — skip push (勘录未就绪)."
  exit 0
fi

COMMIT_MSG="${COMMIT_MSG:-[HB] compass-pedal-survey 2026-10-23T20:00+08:00 · ledger/logs/protocols sync · U1-U4 PENDING (no closure)}"
if [[ -f "$WS/COMMIT_MSG.txt" ]]; then
  COMMIT_MSG="$(cat "$WS/COMMIT_MSG.txt")"
elif [[ -f "$WS/HB-COMMIT-MSG.txt" ]]; then
  COMMIT_MSG="$(cat "$WS/HB-COMMIT-MSG.txt")"
fi

cd "$REPO"
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull origin "$BRANCH"

rsync -a --delete --exclude '__pycache__/' "$WS/ledger/" "$REPO/compass-pedal-ledger/"
if [[ -d "$WS/audit" ]]; then
  rsync -a --delete "$WS/audit/" "$REPO/compass-pedal-audit/"
elif [[ -d "$WS/logs" ]]; then
  rsync -a --delete "$WS/logs/" "$REPO/compass-pedal-audit/"
fi
if [[ -d "$WS/原稿" ]]; then
  rsync -a --delete "$WS/原稿/" "$REPO/compass-pedal-manuscripts/"
fi

git add compass-pedal-ledger compass-pedal-audit compass-pedal-manuscripts 2>/dev/null || true
if [[ -z "$(git status --porcelain)" ]]; then
  echo "Nothing to commit after sync; check workspace layout." >&2
  exit 1
fi

export GIT_AUTHOR_NAME="黄清佳 | 碳硅道统"
export GIT_AUTHOR_EMAIL="73703285+liu-hui-ming@users.noreply.github.com"
export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME"
export GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"

git commit -m "$COMMIT_MSG"
git push origin "$BRANCH"
rm -f "$MARKER"
echo "Pushed and removed PUSH_ME.txt"
