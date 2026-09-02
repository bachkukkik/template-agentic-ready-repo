#!/usr/bin/env bash
# Master test runner — three tiers, per AGENTS.md §5/§6.
#
#   bash tests/run.sh              # unit + integration (no services needed)
#   bash tests/run.sh --with-e2e   # also run E2E against a running container
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

WITH_E2E=0
[ "${1:-}" = "--with-e2e" ] && WITH_E2E=1

fail=0

echo "==> Tier 1/3: unit"
python3 -m pytest tests/unit -v || fail=1

echo
echo "==> Tier 2/3: integration"
python3 -m pytest tests/integration -v || fail=1

echo
echo "==> Tier 3/3: e2e"
if [ "$WITH_E2E" -eq 0 ]; then
  echo "SKIPPED (needs a running service — re-run with --with-e2e)"
elif ! command -v bats >/dev/null 2>&1; then
  echo "SKIPPED (bats not installed: https://bats-core.readthedocs.io)"
else
  bats tests/e2e/ || fail=1
fi

echo
if [ "$fail" -ne 0 ]; then
  echo "RESULT: FAILED"
  exit 1
fi
echo "RESULT: PASSED"
