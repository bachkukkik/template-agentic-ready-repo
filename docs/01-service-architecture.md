# 01 — Service Architecture

## What

The template repo provides a minimal Python HTTP service behind Docker Compose with a three-tier test suite (unit, integration, E2E) and a GitHub Actions CI pipeline. It demonstrates the agentic development workflow from AGENTS.md.

## Why

- New agent-driven projects need a working skeleton that enforces the doctrine from day one, not a blank repo.
- A real service with real tests proves the pipeline works before any custom code is added.
- The doc structure itself models the `coding-agents-docs-guideline` template so agents learn by example.

## How

The service lives in `service/`. It is a Python stdlib HTTP server with three endpoints:

| Endpoint | Method | Response | Purpose |
|----------|--------|----------|---------|
| `/health` | GET | `{"status":"ok"}` | Docker healthcheck + readiness probe |
| `/` | GET | `{"message":"hello"}` | Root endpoint |
| anything else | GET | `{"error":"not found"}` | 404 catch-all |

### Container image

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir pytest
EXPOSE 8000
CMD ["python", "-m", "src.main"]
```

The image is built from `service/` — the build context is the service directory, so `src/main.py` becomes `src.main` inside the container.

### Docker Compose

```yaml
services:
  service:
    build: ./service
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 5s
      timeout: 3s
      retries: 5
```

No host port binding. The service is only reachable inside the Docker network. E2E tests use `docker compose exec` to reach the container directly.

### Test tiers

| Tier | Location | Runner | Coverage |
|------|----------|--------|----------|
| Unit + integration | `service/tests/test_main.py` | pytest | HTTP endpoint behavior (AC-SVC-001..003) |
| E2E | `tests/e2e/example.bats` | bats | Docker health via `docker compose exec` (AC-E2E-001..002) |
| Integration (placeholder) | `tests/integration/example.test.ts` | — | Service-to-service tests |

Tests run sequentially through `tests/run.sh`. The runner exits non-zero on any tier failure.

### CI pipeline

```yaml
# .github/workflows/ci.yml
jobs:
  unit:          # pytest service/tests/
    needs: []
  e2e:           # docker compose up + bats
    needs: [unit]
```

The pipeline gates merge on main. Unit tests run first; E2E runs only if unit passes.

## Verification

```bash
# Build and start
cd template-agentic-ready-repo
docker compose up -d --build

# Verify container health
docker compose ps
docker compose exec service python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health'); print('ok')"

# Run all tests
bash tests/run.sh
```

All commands must return exit code 0. The test runner reports `3 passed` (pytest) + `2/2 bats` (E2E) + `All tests passed.`.

## What Works

- Docker image builds from `service/` with a single `pip install pytest` layer
- Health check endpoint responds within 50 ms under no load
- All five tests pass locally (3 pytest + 2 bats)
- Test runner exits 0 when the Docker service is running
- CI pipeline gates on unit tests before running E2E
- No secrets in git diff (`.env` excluded, `.env.example` committed)

## What Fails

- **Cold start latency:** The Python stdlib server binds in ~200 ms. The test fixture waits 1 second; slower environments may need a longer sleep.
- **Host port access:** Removing host port binding means `curl localhost:8000` fails from the host. Only `docker compose exec` reaches the service.
- **Integration test placeholder:** `tests/integration/example.test.ts` is a no-op stub with no actual coverage.

## Resolution

- **Cold start latency:** Increase the `time.sleep(1)` in the pytest fixture to `time.sleep(3)` on slow CI runners, or add a retry loop with exponential backoff.
- **Host port access:** Add `ports: ["8000:8000"]` to `docker-compose.yml` if direct host access is needed for development. The template intentionally omits it for security.
- **Integration test placeholder:** Replace the stub with actual service-to-service tests when a second service is added to the stack.

## Verdict

**partial** — The template repo covers the full agentic development lifecycle with a verified pipeline. The single Python service is intentionally minimal — it exists to prove the test and CI infrastructure works, not to be a production application; the open failures are cold-start flakiness risk, no host port binding, and a stub integration test.
