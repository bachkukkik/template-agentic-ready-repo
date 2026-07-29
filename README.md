# Agentic Ready Repo Template

> Starter skeleton for agent-driven development. Follows the slash-storefront doctrine: AGENTS.md → PRD.md → kb/ → tests/ → CI.

## Quick Start

```bash
# Clone and set up
git clone <repo-url>
cd template-agentic-ready-repo

# Start services
docker compose up -d

# Run tests
bash tests/run.sh

# Local CI (pre-PR)
act push
```

## Services

| Service | Port | Technology | Purpose |
|---------|------|------------|---------|
| service | 8000 | Python 3.12 stdlib HTTP | Example microservice with /health, / endpoints |

## Repository Structure

```
.
├── AGENTS.md              # Agent instructions (read first)
├── PRD.md                 # Master PRD → topic PRDs in docs/prd/
├── README.md              # This file
├── .env.example           # Environment variable template
├── .gitignore             # Standard ignores for agentic repos
├── docker-compose.yml     # Service orchestration
├── service/               # Python microservice
│   ├── Dockerfile
│   ├── src/main.py        # HTTP server with /health and /
│   └── tests/test_main.py # pytest (unit + integration)
├── kb/                    # Knowledge base
│   ├── SCHEMA.md          # KB conventions
│   ├── index.md           # Concept index
│   ├── concepts/          # Architecture decisions
│   └── entities/          # External services
├── docs/prd/              # Topic PRDs with SC + test mapping
├── tests/                 # Three-tier test suite
│   ├── run.sh             # Master test runner
│   ├── unit/              # Unit tests
│   ├── e2e/               # E2E (bats)
│   └── integration/       # Integration tests
├── scratchpads/           # Agent scratch space (gitignored)
└── .github/workflows/     # CI pipeline
```

## Testing

```bash
# All tests
bash tests/run.sh

# Unit tests (pytest)
python3 -m pytest service/tests/ -v

# E2E (bats, requires running Docker service)
bats tests/e2e/
```

## License

MIT
