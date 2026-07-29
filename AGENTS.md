# Agent Instructions — [Project Name]

## What This Is

[One-line description of the project. Stack, purpose, deployment context.]

## Read First

1. `PRD.md` — master product requirements index → topic PRDs in `docs/prd/`
2. `kb/concepts/` — knowledge base (canonical architecture, data models, decisions)
3. `README.md` — quick start, services, development commands

> **Source-of-truth doctrine (from PRD.md):** KB wins on semantics/behaviour; repo artifacts win on literal values; top-level PRD wins over detail PRDs.

---

## The `/goal` Orchestration Workflow (coding-agent entry point)

Every substantive request is driven through the `/goal` pipeline. The coding agent MUST capture and follow this sequence.

**Kickoff prompt:**

```
/goal <whatever user request>

use pm skill for PRD, problem triage, success criteria definition and verification policy
use karpathy skill for codebase investigation and all resource analysis
prioritize task delegation over direct execution
use opencode-plan-build-orchestrator skill for all coding tasks
```

**Subsequent prompts (run in order):**

```
## sub1 — docs/tests gap sync
check gaps in docs/ and tests/ against codebase. update + drop obsolescences accordingly.

use pm skill for PRD, problem triage, success criteria definition and verification policy.
use karpathy skill for codebase investigation and all resource analysis.
prioritize task delegation over direct execution.
use opencode-plan-build-orchestrator skill for all coding tasks.

## sub2 — local CI
run github action locally using https://github.com/nektos/act

if problems surface, use pm skill for PRD, problem triage, success criteria definition and verification policy.
use karpathy skill for codebase investigation and all resource analysis.
prioritize task delegation over direct execution.
use opencode-plan-build-orchestrator skill for all coding tasks.

## sub3 — PR + CI monitor
PR using yeet. thoroughly provide context in the PR using coding agent docs skill. lastly monitor CI/CD in PR.

if problems surface, use pm skill for PRD, problem triage, success criteria definition and verification policy.
use karpathy skill for codebase investigation and all resource analysis.
prioritize task delegation over direct execution.
use opencode-plan-build-orchestrator skill for all coding tasks.

## sub4 — merge + redeploy
squash and merge to main all test-passed PRs.
then git checkout main and pull here.
lastly do full redeployment cycle from pull to serve.

use pm skill for PRD, problem triage, success criteria definition and verification policy.
use karpathy skill for codebase investigation and all resource analysis.
prioritize task delegation over direct execution.
use opencode-plan-build-orchestrator skill for all coding tasks.
```

**Skill-to-phase mapping:**

| Phase | Skill | Output |
|-------|-------|--------|
| PRD / triage / success criteria / verification policy | `pm` (`create-prd`, `intended-vs-implemented`) | `PRD.md` section |
| Codebase & resource investigation | `karpathy-guidelines` | Evidence-based gap report |
| Task delegation | `kanban` / `delegate_task` | Kanban cards (with `skills=[...]`) |
| All coding | `opencode-plan-build-orchestrator` | plan → build → verify via subagents |

---

## Standing Orders (ALWAYS apply)

These rules apply to **every session, every agent, every prompt**.

### 1. Mandated Skills

Load and use these skills on EVERY task:

| Skill | When | Purpose |
|-------|------|---------|
| `karpathy-guidelines` | ALWAYS | Research context, clean code, surface assumptions |
| `security-best-practices` | ALWAYS | All code changes must follow security best practices |
| `webapp-testing` | Testing | Write and run comprehensive tests |
| `coding-agents-docs-guideline` | Docs | Document all changes in the repo |
| `yeet` | Git ops | All commit/push/branch operations |
| `opencode-plan-build-orchestrator` | Coding via delegate | All coding tasks MUST route through plan→build→verify |

### 2. Delegation Rules (coding discipline)

- **Every `delegate_task` call for coding work MUST include** `opencode-plan-build-orchestrator` and `karpathy-guidelines` in the subagent's goal context.
- **The orchestrator parent NEVER writes repo-tracked files directly** — all code edits go to subagents. Investigation, planning, PRD authoring, and `~/.hermes/plans/*.md` stay with the parent.
- For docs-only tasks, the parent does the edits directly.

### 3. Code Quality Rules

- **No `shell=True`** in subprocess calls — use `subprocess.run` with explicit args
- **No hardcoded secrets** — use env vars or `key_env` references
- **No wildcard patterns (`/*`)** in model config — filter them during discovery
- **No `requests` without timeout** — always set `timeout=N`
- **bash scripts must use `set -euo pipefail`** and `$()` not backticks
- **All Docker images pin tags** (no `:latest` for non-upstream images)

### 4. Verification

After any change:

```bash
# Build and start (adapt to your stack)
docker compose build && docker compose up -d

# Check health
docker compose ps

# Run tests
bash tests/run.sh

# No secrets in git diff
git diff --cached | grep -iE '(api_key|secret|token|password)' || echo "Clean"
```

### 5. PRD → Test → CI Pattern (mandatory for all PRDs)

Every PRD in `docs/prd/` must follow this structure for its Success Criteria section:

1. **Success Criteria as annotated bullets** — each SC is a bullet with an inline `_Verify:` annotation pointing to the specific test file + test ID:
   ```
   - **SC1** — <criterion>. _Verify:_ `tests/unit/example.test.ts` (AC-EXM-001).
   ```

2. **Test Mapping table** — after the SC bullets, a table mapping expected behavior → test file → test IDs:
   ```
   | Expected behavior | Test file | Test IDs |
   |---|---|---|
   | Example behavior | example.test.ts | AC-EXM-001 |
   ```

3. **CI/CD Gate section** — explicit statement of which CI job(s) run the tests:
   ```
   ## CI/CD Gate
   All tests run in CI per .github/workflows/ci.yml. No PR merges with a red test.
   ```

**Test ID convention:** `AC-<DOMAIN>-NNN` (e.g., `AC-POS-001`, `AC-WH-003`). Domain prefixes match the PRD topic.

**Three-tier test suite:** Every SC maps to one of three tiers:
- Unit + Component — `tests/unit/`
- E2E + Visual + A11y — `tests/e2e/`
- Integration — `tests/integration/`

### 6. CI/CD Pipeline — Local-First, Then Remote

```
Stage 1: LOCAL CI                Stage 2: REMOTE CI (Git repo)
─────────────────────            ──────────────────────────────
nektos/act                       GitHub Actions (.github/workflows/)
runs .github/workflows/*.yml     triggers on PR
locally via Docker               all jobs must pass
                                  blocks merge on red
        ↓                               ↓
  green → open PR  ──────→  PR CI runs  ──────→  green → merge
```

**Rule: no PR is opened with a known-red local CI run.**

---

## Repository Structure

```
.
├── AGENTS.md           # This file — agent instructions (read first)
├── PRD.md              # Master PRD index → topic PRDs in docs/prd/
├── README.md           # Quick start, services, dev commands
├── .env.example        # Environment variable template
├── .gitignore          # Standard ignores for agentic repos
├── kb/                 # Knowledge base (authoritative semantics)
│   ├── SCHEMA.md       # KB schema and conventions
│   ├── index.md        # Concept index
│   ├── concepts/       # Architecture, data models, decisions
│   │   └── example.md
│   ├── entities/       # External services, vendors, integrations
│   └── raw/            # Raw research, imported articles
├── docs/               # PRDs and project documentation
│   └── prd/
│       └── 01-example-topic.md    # Example PRD with SC pattern
├── tests/              # Three-tier test suite
│   ├── run.sh          # Master test runner
│   ├── unit/           # Unit + component tests
│   ├── e2e/            # E2E tests (bats for infra)
│   └── integration/    # Integration tests
├── scratchpads/        # Agent scratch space (gitignored except .gitkeep)
└── .github/
    └── workflows/
        └── ci.yml      # CI pipeline definition
```

## Development Commands

```bash
# Start services (adapt to your stack)
docker compose up -d

# Run tests
bash tests/run.sh

# Local CI (pre-PR)
act push
```

## Security

- Never commit `.env`, API keys, JWT secrets
- All credentials via env vars, never hardcoded
- Webhook signature verification in satellite services

## graphify

When `graphify-out/graph.json` exists, use graphify for codebase queries:

```bash
graphify query "<question>"
graphify path "<A>" "<B>"
graphify explain "<concept>"
```

After modifying code, run `graphify update .` to keep the graph current.
