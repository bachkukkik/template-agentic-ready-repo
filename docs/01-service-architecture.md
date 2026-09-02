# 01 — Service Architecture

## What

The template repo provides a minimal Python HTTP service behind Docker Compose with a three-tier test suite (unit, integration, E2E) and two GitHub Actions workflows. It demonstrates the agentic development workflow from AGENTS.md.

## Why

- New agent-driven projects need a working skeleton that enforces the doctrine from day one, not a blank repo.
- A real service with real tests proves the pipeline works before any custom code is added.
- Each tier named in AGENTS.md §5 must have a runner and a CI job, or the doctrine is decorative — the skeleton is where that is proven.
- The doc structure itself models the `coding-agents-docs-guideline` template so agents learn by example.

## How

The service lives in `service/`. It is a Python stdlib HTTP server with three endpoints:

| Endpoint | Method | Response | Purpose |
|----------|--------|----------|---------|
| `/health` | GET | `{"status":"ok"}` | Docker healthcheck + readiness probe |
| `/` | GET | `{"message":"hello"}` | Root endpoint |
| anything else | GET | `{"error":"not found"}` | 404 catch-all |

Routing is a pure function, `route(path) -> (code, body)`. `Handler.do_GET` is a two-line adapter over it. The split is what makes a genuine unit tier possible: the unit tests call `route()` with no socket, and the transport is left to the integration and E2E tiers.

### Container image

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
EXPOSE 8000
CMD ["python", "-m", "src.main"]
```

The image is built from `service/` — the build context is the service directory, so `src/main.py` becomes `src.main` inside the container. The image carries no test dependencies: every tier runs outside the container (`tests/unit`, `tests/integration`) or against it (`tests/e2e`).

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

| Tier | Location | Runner | CI job | Coverage |
|------|----------|--------|--------|----------|
| Unit | `tests/unit/test_routing.py` | pytest | `unit` | `route()` path mapping (AC-EXM-001..003) |
| Integration | `tests/integration/test_service_endpoints.py` | pytest | `integration` | The service out of process over a real socket (AC-EXM-201..203) |
| E2E | `tests/e2e/example.bats` | bats | `e2e` | The running container via `docker compose exec` (AC-EXM-101..102) |

The hundreds digit of the test ID names the tier (AGENTS.md §5). `tests/conftest.py` puts `service/` on `sys.path`; `tests/requirements.txt` holds the test-only dependencies.

`tests/run.sh` runs tier 1 and tier 2 unconditionally and tier 3 only with `--with-e2e`, so the default invocation needs no running container. It accumulates failures across tiers rather than exiting at the first, and prints `RESULT: PASSED` or `RESULT: FAILED`.

### CI pipeline

```yaml
# .github/workflows/ci.yml
jobs:
  unit:          # pytest tests/unit
    needs: []
  integration:   # pytest tests/integration
    needs: [unit]
  e2e:           # docker compose up + bats
    needs: [integration]
  secret-scan:   # tracked credential files + hardcoded assignments
    needs: []
```

`sources-readonly.yml` is the second gate: it fails any PR that modifies or deletes a file under `kb/raw/**` without the `ingest` label, making funnel rule 3 structural rather than advisory.

## Verification

```bash
# Build and start
docker compose up -d --build

# Verify container health
docker compose ps --format '{{.Name}} {{.Status}}'

# Run all three tiers
bash tests/run.sh --with-e2e
```

`docker compose ps` must report `(healthy)`. The runner must print `3 passed` for unit, `3 passed` for integration, `ok 1`/`ok 2` for bats, and end with `RESULT: PASSED`.

## What Works

- Docker image builds from `service/` and reports `(healthy)` within 8 seconds of `docker compose up -d --build`
- All eight tests pass locally: 3 unit + 3 integration + 2 bats
- Every tier has both a runner in `tests/run.sh` and a job in `ci.yml` — no tier is a stub
- `bash tests/run.sh` with no flags passes without Docker running, and reports the E2E tier as skipped rather than failed
- The runtime image carries no test dependencies
- CI gates E2E behind unit and integration; `secret-scan` runs independently

## What Fails

- **Cold start latency:** The Python stdlib server binds in ~200 ms. The integration fixture waits a flat 1 second; slower environments may need longer.
- **Host port access:** With no host port binding, `curl localhost:8000` fails from the host. Only `docker compose exec` reaches the service.
- **E2E under `act`:** `act push` unqualified, or `act push -j e2e`, runs `docker compose up -d --build` against the host daemon under this repo's compose project name — on a host running this project live, that replaces the running containers.

## Resolution

- **Cold start latency:** Replace the `time.sleep(1)` in the pytest fixture with a retry loop against `/health` on slow runners.
- **Host port access:** Add `ports: ["8000:8000"]` to `docker-compose.yml` if direct host access is needed for development. The template intentionally omits it.
- **E2E under `act`:** Run `act push -j unit`, `-j integration`, `-j secret-scan` locally and exercise the E2E tier directly with `docker compose up -d --build && bash tests/run.sh --with-e2e` from a checkout that is not the deployment (AGENTS.md §6).

## Verdict

**partial** — The skeleton verifies end to end: three executable test tiers, four CI jobs, and a kb/raw gate. The single Python service is intentionally minimal; the open failures are cold-start flakiness risk, no host port binding, and an E2E job that must not be run under `act` on a host serving this compose project.
