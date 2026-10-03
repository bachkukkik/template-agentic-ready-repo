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

# Set to 1 in a project whose integration tier reaches shared infrastructure — a real
# broker, a shared database, anything another team also uses. The tier then runs only
# with RUN_INTEGRATION_TESTS=1 in the environment, so a routine `bash tests/run.sh`
# cannot write to live state (AGENTS.md §5). This template's integration tests are
# hermetic, so it ships at 0.
INTEGRATION_NEEDS_OPT_IN=0

fail=0

echo "==> Tier 1/3: unit"
python3 -m pytest tests/unit -v || fail=1

echo
echo "==> Tier 2/3: integration"
if [ "$INTEGRATION_NEEDS_OPT_IN" -eq 1 ] && [ "${RUN_INTEGRATION_TESTS:-0}" != "1" ]; then
  echo "SKIPPED (this tier touches shared infrastructure — re-run with"
  echo "         RUN_INTEGRATION_TESTS=1, never against a production stack)"
else
  python3 -m pytest tests/integration -v || fail=1
fi

echo
echo "==> Tier 3/3: e2e"
if [ "$WITH_E2E" -eq 0 ]; then
  echo "SKIPPED (needs a running service — re-run with --with-e2e)"
elif ! command -v bats >/dev/null 2>&1; then
  echo "SKIPPED (bats not installed: https://bats-core.readthedocs.io)"
else
  # The e2e tier reaches the container only through `docker compose exec`, so the
  # stack must be up. Auto-start it when needed; leave it running afterwards.
  if [ -z "$(docker compose ps -q service 2>/dev/null)" ]; then
    echo "==> e2e: starting compose stack"
    if ! timeout 120 docker compose up -d --wait; then
      echo "ERROR: e2e: compose stack did not come up within 120s"
      fail=1
    fi
  fi
  if [ -z "$(docker compose ps -q service 2>/dev/null)" ]; then
    echo "ERROR: e2e: service is not running — start it with 'docker compose up -d --wait'"
    fail=1
  else
    bats tests/e2e/ || fail=1
  fi
fi

echo
if [ "$fail" -ne 0 ]; then
  echo "RESULT: FAILED"
  exit 1
fi
echo "RESULT: PASSED"
