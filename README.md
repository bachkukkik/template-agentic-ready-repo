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
├── AGENTS.md              # Agent instructions (read first) — CANONICAL
├── CLAUDE.md              # symlink → AGENTS.md
├── .agents/               # Repo-scoped agent assets — CANONICAL
│   ├── skills/            # Skills pinned to this repo
│   └── plugins/           # Plugins pinned to this repo
├── .claude/               # skills, plugins → symlinks into ../.agents/
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
├── docs/                # Two doc layers — intent + verified reality
│   ├── NN-slug.md       # Empirical status docs (What/Why/How/Works/Fails/Verdict)
│   └── prd/             # Topic PRDs with SC + test mapping (intent)
├── tests/               # Three-tier test suite
│   ├── run.sh             # Master test runner
│   ├── unit/              # Unit tests
│   ├── e2e/               # E2E (bats)
│   └── integration/       # Integration tests
├── scratchpads/           # Agent scratch space (gitignored)
└── .github/
    ├── copilot-instructions.md  # symlink → ../AGENTS.md
    └── workflows/         # CI pipeline
```

## Harness Support

`AGENTS.md` is the one instruction file. Harness entry points are symlinks to it, so
adding a harness never forks the content:

| Harness | Entry point | Skills dir |
|---|---|---|
| Hermes | `AGENTS.md` (native) | `~/.hermes/skills/` or `.agents/skills/` |
| Claude Code | `CLAUDE.md` → `AGENTS.md` | `.claude/skills` → `.agents/skills` |
| Copilot | `.github/copilot-instructions.md` → `AGENTS.md` | vendor dir → `.agents/skills` |
| Anything else | read `AGENTS.md` directly | paste `SKILL.md` into the prompt |

```bash
# Add a harness
ln -s AGENTS.md <entry-file>
ln -s ../.agents/skills <vendor-dir>/skills
```

**Windows:** run `git config core.symlinks true` before cloning, or the symlinks
land as plain text files holding a path and every entry point breaks.

## Testing

```bash
# All tests
bash tests/run.sh

# Unit tests (pytest)
python3 -m pytest service/tests/ -v

# E2E (bats, requires running Docker service)
bats tests/e2e/
```

## Recommended Agent Skills

AGENTS.md mandates several skills across its orchestration pipeline and Standing
Orders. None are vendored into this template. Two install targets:

- **Host level (default)** — `~/.hermes/skills/`, `~/.claude/skills/`. Shared across
  all your repos.
- **Repo level** — `.agents/skills/`, reachable from every harness via its symlink.
  Use when the skill version must travel with the repo.

**Always install from a neutral cwd (`cd ~` or `cd /tmp`), never from inside
this repo**, so auto-detecting installers do not pollute the working tree.

| Skill | Source | Install shape |
|-------|--------|---------------|
| `opencode-plan-build-orchestrator` | https://github.com/bachkukkik/opencode-plan-build-orchestrator | Plain skill — clone whole repo (SKILL.md + `agents/` + `references/`) |
| `coding-agents-docs-guideline` | https://github.com/bachkukkik/coding-agents-docs-guideline | Plain skill — clone whole repo (SKILL.md + `examples/`). Required to author or edit any `docs/NN-slug.md` |
| `yeet` | https://github.com/openai/skills/tree/main/skills/.curated/yeet | Plain skill — sparse-checkout `skills/.curated/yeet` (SKILL.md + `agents/` + `assets/`). Requires `gh` CLI authenticated |
| `security-best-practices` | https://github.com/openai/skills/tree/main/skills/.curated/security-best-practices | Plain skill — sparse-checkout `skills/.curated/security-best-practices` (SKILL.md + `references/`). Python / JS-TS / Go only |
| `webapp-testing` | https://github.com/anthropics/skills/blob/main/skills/webapp-testing/SKILL.md | Plain skill — sparse-checkout `skills/webapp-testing` (SKILL.md + `scripts/` + `examples/`). Playwright-based |
| `karpathy-guidelines` | https://github.com/multica-ai/andrej-karpathy-skills/blob/main/skills/karpathy-guidelines | Plain skill — single `SKILL.md` |
| `pm` | https://github.com/phuryn/pm-skills | **Caveat below** — Claude Code plugin bundle, not a plain skill |

### `pm` caveat (read before installing)

`phuryn/pm-skills` ships as a Claude Code plugin bundle: each `pm-*` directory
contains a `.claude-plugin/marketplace.json`, a `commands/` dir of slash
commands, and a `skills/` dir. It does not install as a plain `SKILL.md` skill.

If your agent host supports `.claude-plugin` bundles, install it through that
mechanism. Otherwise, extract the relevant `commands/*.md` files into your
agent's skill format manually. Sub-bundles of interest:

| Sub-bundle | Commands relevant to PRD / triage work |
|------------|----------------------------------------|
| `pm-execution` | `write-prd`, `write-stories`, `test-scenarios`, `red-team-prd`, `plan-okrs`, `sprint`, `transform-roadmap` |
| `pm-product-discovery` | `triage-requests`, `discover`, `setup-metrics`, `interview`, `brainstorm` |
| `pm-product-strategy` | `strategy`, `value-proposition`, `pricing`, `market-scan`, `business-model` |
| `pm-ai-shipping` | `derive-tests`, `document-app`, `ship-check`, `security-audit-static`, `performance-audit-static` |

### Install example (one skill)

Set `SKILL_ROOT` to your harness's skill directory, then the steps are identical:

| Target | `SKILL_ROOT` | Verify command |
|---|---|---|
| Hermes (host) | `~/.hermes/skills` | `hermes skills list \| grep <name>` |
| Claude Code (host) | `~/.claude/skills` | `ls ~/.claude/skills` |
| This repo (any harness) | `<repo>/.agents/skills` | `ls .claude/skills` — symlink resolves |

```bash
# From a neutral cwd — never from inside this repo
SKILL_ROOT=~/.claude/skills          # or ~/.hermes/skills
cd /tmp
git clone --depth 1 --filter=blob:none --sparse https://github.com/openai/skills.git
cd skills
git sparse-checkout set skills/.curated/yeet
mkdir -p "$SKILL_ROOT/yeet"
cp -r skills/.curated/yeet/{SKILL.md,agents,assets} "$SKILL_ROOT/yeet/"
```

Verify by listing the target dir — `SKILL.md` plus its subdirs must be present:

```bash
ls "$SKILL_ROOT/yeet/"
```

If your harness has no skill mechanism at all, paste the skill's `SKILL.md` into the
prompt instead. The rules in `AGENTS.md` still apply — a missing tool never waives them.

### Skill maturity and provenance

These skills come from multiple authors (user forks, OpenAI curated,
Anthropic, community). Pin to a specific commit if reproducibility matters —
the `:latest` of a skill can change its template or commands. The
`opencode-plan-build-orchestrator` and `coding-agents-docs-guideline` entries
are maintained in the user's own forks and are the canonical pair for the
docs/prd ↔ docs/NN-slug.md workflow defined in AGENTS.md.

## License

MIT
