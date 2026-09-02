#!/usr/bin/env bats
# E2E smoke test — exec into the running Docker container
# Run from the repo root with: bats tests/e2e/

REPO_ROOT="$(cd "$(dirname "$BATS_TEST_FILENAME")/../.." && pwd)"

@test "AC-EXM-101: service /health returns 200" {
  docker compose -f "$REPO_ROOT/docker-compose.yml" exec -T service \
    python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
}

@test "AC-EXM-102: service / returns 200" {
  docker compose -f "$REPO_ROOT/docker-compose.yml" exec -T service \
    python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')"
}
