#!/usr/bin/env bash
# Replace the OWNER / PARTNER placeholders with real GitHub usernames.
# Run once, before the first commit:  ./scripts/personalise.sh <your-username> [partner-username]
set -euo pipefail

owner="${1:?usage: personalise.sh <owner-username> [partner-username]}"
partner="${2:-}"

cd "$(dirname "$0")/.."
files=$(grep -rlwE 'OWNER|PARTNER' --exclude-dir=.git --exclude-dir=.venv --exclude='personalise.sh' --exclude='github_setup.sh' . || true)

for f in $files; do
  perl -pi -e "s/\\bOWNER\\b/${owner}/g" "$f"
  if [[ -n "$partner" ]]; then
    perl -pi -e "s/\\bPARTNER\\b/${partner}/g" "$f"
  fi
  echo "updated $f"
done

if [[ -z "$partner" ]]; then
  echo "Note: partner username not given. Re-run later with it to fill in @PARTNER."
fi
