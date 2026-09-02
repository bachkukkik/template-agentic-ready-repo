# Agentic Ready Repo Template

> Starter skeleton for agent-driven development. Follows the slash-storefront doctrine: AGENTS.md → PRD.md → kb/ → tests/ → CI.

## Document Funnel

Every piece of writing in this repo has exactly one home. Writing flows one direction
only — full rules in [AGENTS.md](AGENTS.md#document-funnel-mandatory--every-harness-every-agent).

```
user prompt (any harness)
   ▼
scratchpads/          playground, notes, memos          gitignored, deletable
   ▼
kb/raw/               immutable sources, any format     add-only, never edited
   ▼  llm-wiki ./kb/
kb/                   confirmed knowledge               written ONLY by llm-wiki
   ▼
PRD.md + docs/prd/    intent, grounded in kb/           pm skills
   ▼
docs/gaps/            kb ↔ prd, prd ↔ code divergence   transient, must resolve
   ▼
docs/NN-slug.md       what actually works / fails       coding-agents-docs-guideline ONLY
   ▼
GitHub issues         everything else
```

A new `.md` that fits none of these stages is a defect — file an issue instead.
`kb/` follows the [llm-wiki spec](https://github.com/NousResearch/hermes-agent/blob/main/skills/research/llm-wiki/SKILL.md)
strictly; unused KB material is archived to `kb/_archive/`, never deleted. The add-only
rule for `kb/raw/` is enforced in CI by
[`sources-readonly.yml`](.github/workflows/sources-readonly.yml), not just by instruction.

## Quick Start

```bash
# Clone and set up
git clone <repo-url>
cd template-agentic-ready-repo

# Start services
docker compose up -d

# Run tests (unit + integration; --with-e2e adds the container tier)
bash tests/run.sh
bash tests/run.sh --with-e2e

# Local CI (pre-PR) — never `act push` unqualified on a host running this
# compose project live; the e2e job would replace its containers. See AGENTS.md §6.
act push -j unit && act push -j integration && act push -j secret-scan
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
│   └── agents/            # investigator.md — root-cause gate as a sub-agent
├── PRD.md                 # Master PRD → topic PRDs in docs/prd/
├── README.md              # This file
├── .env.example           # Environment variable template
├── .gitignore             # Standard ignores for agentic repos
├── .credentials/          # Live credential files — gitignored; only *.example tracked
├── docker-compose.yml     # Service orchestration
├── service/               # Python microservice
│   ├── Dockerfile
│   └── src/main.py        # HTTP server with /health and /; route() is pure
├── kb/                    # Knowledge base — llm-wiki layout, tracked
│   ├── SCHEMA.md          # KB conventions + tag taxonomy
│   ├── index.md           # Page catalog (llm-wiki-maintained)
│   ├── log.md             # Append-only action record (llm-wiki-maintained)
│   ├── raw/               # Immutable sources: articles/ papers/ transcripts/ assets/
│   ├── concepts/          # Architecture, decisions, topics
│   ├── entities/          # People, orgs, external services
│   ├── comparisons/       # Side-by-side analyses
│   ├── queries/           # Filed query results
│   └── _archive/          # Superseded material (never deleted)
├── docs/                # Three doc layers — intent, gaps, verified reality
│   ├── README.md        # Verdict catalog for the NN status docs
│   ├── NN-slug.md       # Empirical status docs (What/Why/How/Works/Fails/Verdict)
│   ├── gaps/            # kb ↔ prd and prd ↔ code divergences
│   └── prd/             # Topic PRDs with SC + test mapping (intent)
├── tests/               # Three-tier test suite — each tier has a runner AND a CI job
│   ├── run.sh             # Master test runner (--with-e2e adds the container tier)
│   ├── conftest.py        # Puts service/ on sys.path for the tests
│   ├── requirements.txt   # Test-only deps
│   ├── unit/              # pytest — pure logic (AC-X-0NN)
│   ├── e2e/               # bats — running container (AC-X-1NN)
│   └── integration/       # pytest — cross-process (AC-X-2NN)
├── scratchpads/           # Agent scratch space (gitignored)
└── .github/
    ├── copilot-instructions.md  # symlink → ../AGENTS.md
    └── workflows/
        ├── ci.yml                 # unit → integration → e2e + secret scan
        └── sources-readonly.yml   # kb/raw/** add-only gate
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
# All tests (unit + integration)
bash tests/run.sh

# All three tiers, against a running container
docker compose up -d --build && bash tests/run.sh --with-e2e

# One tier at a time
python3 -m pytest tests/unit -v
python3 -m pytest tests/integration -v
bats tests/e2e/            # requires the container to be up
```

Test IDs follow `AC-<DOMAIN>-NNN`, where the hundreds digit names the tier: `0NN` unit,
`1NN` e2e, `2NN` integration (AGENTS.md §5).

## Recommended Agent Skills

AGENTS.md mandates several skills across its orchestration pipeline and Standing
Orders. Only `root-cause` is vendored into this template (at `.agents/skills/root-cause/`,
because the root-cause gate and the `investigator` sub-agent depend on its exact
procedure). Install the rest yourself. Two install targets:

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
| `llm-wiki` | https://github.com/NousResearch/hermes-agent/tree/main/skills/research/llm-wiki | Plain skill — sparse-checkout `skills/research/llm-wiki`. **The only writer of `kb/` layer-2 pages.** Invoke as `/llm-wiki ./kb/` so it does not default to `~/wiki` |
| `yeet` | https://github.com/openai/skills/tree/main/skills/.curated/yeet | Plain skill — sparse-checkout `skills/.curated/yeet` (SKILL.md + `agents/` + `assets/`). Requires `gh` CLI authenticated |
| `security-best-practices` | https://github.com/openai/skills/tree/main/skills/.curated/security-best-practices | Plain skill — sparse-checkout `skills/.curated/security-best-practices` (SKILL.md + `references/`). Python / JS-TS / Go only |
| `webapp-testing` | https://github.com/anthropics/skills/blob/main/skills/webapp-testing/SKILL.md | Plain skill — sparse-checkout `skills/webapp-testing` (SKILL.md + `scripts/` + `examples/`). Playwright-based |
| `karpathy-guidelines` | https://github.com/multica-ai/andrej-karpathy-skills/blob/main/skills/karpathy-guidelines | Plain skill — single `SKILL.md` |
| `root-cause` | **vendored** at `.agents/skills/root-cause/` | Already present. Gates every "why does X fail / what does X require" answer; `.claude/agents/investigator.md` is its Claude Code binding |
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
