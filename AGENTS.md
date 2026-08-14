# Agent Instructions — [Project Name]

> **This file is the single source of agent instructions for every harness.**
> `CLAUDE.md` and `.github/copilot-instructions.md` are **symlinks** to this file —
> edit `AGENTS.md` only. Repo-scoped skills and plugins live in `.agents/`, with each
> harness's own directory symlinked to it. See *Harness Adapter* below.

## What This Is

[One-line description of the project. Stack, purpose, deployment context.]

## Read First

1. `PRD.md` — master product requirements index → topic PRDs in `docs/prd/`
2. `docs/NN-slug.md` — empirical status docs (what actually works / fails). See *Planned vs Working* below.
3. `kb/concepts/` — knowledge base (canonical architecture, data models, decisions)
4. `README.md` — quick start, services, development commands

> **Source-of-truth doctrine (from PRD.md):** KB wins on semantics/behaviour; repo artifacts win on literal values; top-level PRD wins over detail PRDs.

> **Planned vs Working doctrine:** `docs/prd/` states *intent* (what we plan to build); `docs/NN-slug.md` records *verified reality* (what works, what fails, the net verdict). When the two diverge, the PRD wins on intent and the NN doc wins on behaviour. Every substantive change MUST consult the relevant NN doc and update it via the `coding-agents-docs-guideline` skill — never edit `docs/NN-slug.md` without that skill loaded.

---

## Harness Adapter

This repo is harness-neutral. It is written against **capabilities**, not against any
one agent product. Every rule below names a capability; each harness supplies its own
mechanism. If your harness lacks a mechanism, perform the capability manually — a
missing tool never waives the rule.

| Capability | Hermes | Claude Code | Copilot / other | Generic fallback |
|---|---|---|---|---|
| Entry instruction file | `AGENTS.md` (native) | `CLAUDE.md` (symlink) | `.github/copilot-instructions.md` (symlink) | read `AGENTS.md` manually |
| Repo-scoped skills / plugins | `.agents/skills`, `.agents/plugins` | same, via `.claude/skills`, `.claude/plugins` symlinks | symlink the vendor dir to `.agents/` | inline the skill's `SKILL.md` into the prompt |
| Host-level skills | `~/.hermes/skills/` | `~/.claude/skills/` | vendor-specific | — |
| Sub-agent delegation | `delegate_task` / `kanban` | `Task` tool sub-agents | vendor-specific | do the work inline, in the documented phase order |
| Plan scratch space | `~/.hermes/plans/*.md` | `scratchpads/` (gitignored) | `scratchpads/` | `scratchpads/` |
| Pipeline invocation | `/goal <request>` | prompt the phases below in order | prompt the phases below in order | prompt the phases below in order |

**Two symlink families, both pointing at one canonical source.**

Instruction entry points — every one resolves to `AGENTS.md`:

```
CLAUDE.md                        -> AGENTS.md
.github/copilot-instructions.md  -> ../AGENTS.md
```

Skill/plugin roots — `.agents/` is canonical, harness dirs point into it:

```
.agents/skills/                  # canonical, tracked
.agents/plugins/                 # canonical, tracked
.claude/skills                   -> ../.agents/skills
.claude/plugins                  -> ../.agents/plugins
```

Adding a harness = two symlinks (`ln -s AGENTS.md <entry-file>` and
`ln -s ../.agents/skills <vendor-dir>/skills`) plus a row in the table above.
Never fork the content, never duplicate a skill per harness.

Repo-scoped skills in `.agents/` are for skills this project pins. Everything the
README lists installs at **host** level by default — vendor into `.agents/skills/`
only when the version must travel with the repo.

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

### Running the pipeline without `/goal`

`/goal` is a Hermes slash command. Harnesses that lack it run the **same** pipeline by
prompting the phases in order — the `sub1`–`sub4` labels are the cross-harness contract,
so **"go through sub1-4"** is a valid instruction everywhere. Paste the blocks above
verbatim (drop the `/goal` line), or work from this table:

| # | Phase | Do | Done when |
|---|-------|----|-----------|
| kickoff | Triage | Triage the request, write/refresh the PRD section, define success criteria + verification policy | SC list exists with `_Verify:_` annotations |
| `sub1` | Docs/tests gap sync | Diff `docs/` and `tests/` against the codebase; update, and drop obsolescences | No SC without a test; no doc claiming behaviour the code lacks |
| `sub2` | Local CI | Run the GitHub Actions workflows locally with [`nektos/act`](https://github.com/nektos/act) | `act push` green |
| `sub3` | PR + CI monitor | Open the PR with full context in the body; watch remote CI to completion | Remote CI green |
| `sub4` | Merge + redeploy | Squash-merge green PRs, `git checkout main && git pull`, run the full redeploy cycle | Service healthy from a clean pull |

Report each phase's *Done when* before starting the next. If a phase surfaces a problem,
re-enter kickoff triage for that problem before continuing.

**Skill-to-phase mapping** (install per README; substitute equivalents your harness ships):

| Phase | Skill | Output |
|-------|-------|--------|
| PRD / triage / success criteria / verification policy | `pm` (see README for source) | `PRD.md` section |
| Codebase & resource investigation | `karpathy-guidelines` | Evidence-based gap report |
| Empirical doc authoring (planned vs working) | `coding-agents-docs-guideline` | `docs/NN-slug.md` |
| Task delegation | harness delegation mechanism (see adapter table) | Scoped sub-agent tasks |
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

- **Every delegated coding task MUST include** `opencode-plan-build-orchestrator` and `karpathy-guidelines` in the subagent's goal context — whatever the harness calls its delegation mechanism (see adapter table).
- **The orchestrator parent NEVER writes repo-tracked files directly** — all code edits go to subagents. Investigation, planning, PRD authoring, and plan scratch files stay with the parent.
- For docs-only tasks, the parent does the edits directly.
- **If the harness has no delegation mechanism**, the parent does the coding itself but still runs plan → build → verify as three distinct, separately-reported steps.

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
├── AGENTS.md           # This file — agent instructions (read first). CANONICAL.
├── CLAUDE.md           # symlink → AGENTS.md (Claude Code entry point)
├── .agents/            # Repo-scoped agent assets — CANONICAL
│   ├── skills/         # Skills pinned to this repo
│   └── plugins/        # Plugins pinned to this repo
├── .claude/            # skills, plugins → symlinks into ../.agents/
├── PRD.md              # Master PRD index → topic PRDs in docs/prd/
├── README.md           # Quick start, services, dev commands
├── .env.example        # Environment variable template
├── .gitignore          # Standard ignores for agentic repos
├── kb/                 # Knowledge base (authoritative semantics)
│   ├── SCHEMA.md       # KB schema and conventions
│   ├── index.md        # Concept index
│   └── concepts/       # Architecture, data models, decisions (add as needed)
├── docs/               # Two doc layers — intent + verified reality
│   ├── NN-slug.md      # Empirical status docs (What/Why/How/Verification/
│   │                   # What Works/What Fails/Resolution/Verdict).
│   │                   # Author/edit ONLY via coding-agents-docs-guideline skill.
│   └── prd/
│       └── 01-example-topic.md    # Topic PRDs with SC + test mapping (intent)
├── tests/              # Three-tier test suite
│   ├── run.sh          # Master test runner
│   ├── unit/           # Unit + component tests
│   ├── e2e/            # E2E tests (bats for infra)
│   └── integration/    # Integration tests
├── scratchpads/        # Agent scratch space (gitignored except .gitkeep)
└── .github/
    ├── copilot-instructions.md  # symlink → ../AGENTS.md
    └── workflows/
        └── ci.yml      # CI pipeline definition
```

> **Symlinks require `git config core.symlinks true`** (default off on Windows). Without
> it, clones get plain text files containing a path, and every harness entry point breaks.

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
