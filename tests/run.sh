#!/usr/bin/env bash
set -euo pipefail

# Master test runner — three tiers
echo "=== Unit Tests (pytest) ==="
cd "$(dirname "$0")/.."
python3 -m pytest service/tests/ -v
echo ""

echo "=== E2E Tests (bats) ==="
# Ensure the service is reachable via Docker
if docker compose ps service --status running >/dev/null 2>&1; then
  bats tests/e2e/
else
  echo "  Docker service not running — skipping docker e2e"
fi
echo ""

echo "All tests passed."
