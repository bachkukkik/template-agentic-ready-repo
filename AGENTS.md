# Agent Instructions — [Project Name]

> **This file is the single source of agent instructions for every harness.**
> `CLAUDE.md` and `.github/copilot-instructions.md` are **symlinks** to this file —
> edit `AGENTS.md` only. Repo-scoped skills and plugins live in `.agents/`, with each
> harness's own directory symlinked to it. See *Harness Adapter* below.

## What This Is

[One-line description of the project. Stack, purpose, deployment context.]

Adapt the placeholders and *(adapt to your stack)* examples.

## Read First

1. *Document Funnel* below — where any writing may live; read before writing.
2. `PRD.md` — intent (stage 4) → `docs/prd/` (source-of-truth doctrine).
3. `docs/README.md` — stage-6 verdict catalog → `docs/NN-slug.md`.
4. `kb/index.md` — stage-3 knowledge catalog.
5. `README.md` — quick start, services, structure, tests, skills.

> **Three indexes, three layers, no overlap:** `kb/index.md`, `PRD.md`, `docs/README.md` (knowledge / intent / verified reality).
> **Planned vs Working:** `docs/prd/` = intent, `docs/NN-slug.md` = reality, edited only via `coding-agents-docs-guideline`. → `docs/README.md`

---

## Document Funnel (MANDATORY — every harness, every agent)

Writing flows in **one direction only** — each stage narrows and hardens what the stage above
it produced. Know which stage your output belongs to *before* writing, and never skip a stage.

```
user prompt (desire + imagination, any harness)
   │
   ▼
scratchpads/            playground, quick notes, memos, dumps   [gitignored, deletable]
   │  what survives scrutiny and is a source document
   ▼
kb/raw/                 immutable source material               [add-only, never edit]
   │  /llm-wiki ./kb/   (synthesis step — never hand-write kb/ layer-2 pages)
   ▼
kb/                     confirmed knowledge, fitted to repo purpose
   │  grounds
   ▼
PRD.md + docs/prd/      intent — what we plan to build
   │  compared against kb/ and against the codebase
   ▼
docs/gaps/              gap observations (kb ↔ prd, prd ↔ code)
   │  drives change; change gets verified
   ▼
docs/<NN-topic>.md      empirical observation — what actually works / fails
   │
   ▼
anything else           GitHub issue, or a comment on an existing issue
```

| # | Stage | Path | Contains | Mutability | Written with |
|---|-------|------|----------|------------|--------------|
| 0 | Prompt | — | User's desire and imagination, any harness | ephemeral | — |
| 1 | Scratch | `scratchpads/` | Playgrounds, quick notes, memos, throwaway analysis | free-for-all; **gitignored, deletable at any time** | any tool |
| 2 | Raw knowledge | `kb/raw/` | Immutable source documents about the project — any format (articles, papers, transcripts, assets) | **add new files or archive; never edit in place** | manual capture / ingest |
| 3 | Knowledge | `kb/` (`concepts/`, `entities/`, `comparisons/`, `queries/`, `index.md`, `log.md`) | Confirmed knowledge, synthesized and fitted to repo purpose | agent-owned; regenerated from `kb/raw/` | **`llm-wiki` on `./kb/` only** |
| 4 | Intent | `PRD.md`, `docs/prd/NN-*.md` | Requirements, success criteria, test mapping, CI gate | edit freely, must stay grounded in `kb/` | PRD skills (see mapping) |
| 5 | Gaps | `docs/gaps/NN-*.md` | Observed divergence: kb ↔ prd, or prd ↔ codebase | short-lived; closed when resolved | `karpathy-guidelines` |
| 6 | Reality | `docs/NN-slug.md` + `docs/README.md` | Empirical observation — What/Why/How/Verification/What Works/What Fails/Resolution/Verdict; `README.md` is the verdict catalog | append/update per verified run | **`coding-agents-docs-guideline` only** |
| 7 | Everything else | GitHub issues | Anything that fits no stage above | issue thread | `gh` CLI |

### Funnel rules

1. **No stray documents.** A new `.md` outside stages 1–6 is a defect — no `NOTES.md`, no `TODO.md`, no `ANALYSIS.md` at repo root. If it fits no stage, it is an **issue**: file one, or comment on the existing one.
2. **Grounding direction is downward.** A stage may assert only what an upstream stage supports: a PRD claim with no `kb/` backing is `[ASSUMPTION]`-marked or dropped, and a `docs/NN-slug.md` claim with no verification command is not a claim.
3. **`kb/raw/` is append-or-archive.** Never rewrite a raw source; superseded files move to `kb/_archive/` preserving their path. Enforced in CI by `.github/workflows/sources-readonly.yml`.
4. **`kb/` layer-2 pages are never hand-written.** Update `kb/raw/`, then run the `llm-wiki` skill against `./kb/`, following its spec strictly; vendor the revision you pin at `.agents/skills/llm-wiki/SKILL.md`.
5. **Unused knowledge is archived, not deleted.** `kb/_archive/` is the terminus for stage 2–3 material — remove it from `index.md`, replace inbound wikilinks with plain text + "(archived)", log it in `kb/log.md`.
6. **`scratchpads/` is never cited.** No tracked document may reference a scratchpad path as evidence — promote the content to `kb/raw/` first.
7. **Gaps are transient.** A `docs/gaps/` file closes by producing one of: a `kb/raw/` ingest, a PRD edit, a code change with tests, or an issue — state which in its *Resolution*, then it may be archived out of the repo.
8. **Skill gates are absolute.** Stage 3 requires `llm-wiki`; stage 6 requires `coding-agents-docs-guideline`. No harness mechanism for a skill = paste its `SKILL.md` into the prompt and follow it manually. A missing tool never waives the gate.
9. **Never write a secret into `kb/` or `docs/`.** Both are tracked and `kb/raw/` is the ingest target for exactly the material carrying live values, so a verbatim paste is the usual way a credential enters. Record *that a secret exists and where it is configured* (`.env` var name, `.credentials/` filename), never its value; redact before ingest, never after — `kb/raw/` is add-only, so a leak there costs a rotation plus an archive. Enforced in CI by the `secret-scan` job.
10. **The doctrine itself is tracked.** `AGENTS.md`, `PRD.md`, `docs/`, `kb/`, `tests/`, `.agents/`, `.github/` and the harness symlinks are versioned artifacts, not local scaffolding — a `.gitignore` entry hiding any of them empties the funnel for every agent on a fresh clone. Enforced by the `doctrine` job in `.github/workflows/ci.yml`.

### Where does this text go?

| If the writing is… | It goes to |
|---|---|
| A hunch, a scratch calculation, a paste buffer | `scratchpads/` |
| An external doc / spec / transcript that describes the project | `kb/raw/` |
| A stable fact about how this project works | `kb/raw/` → `llm-wiki ./kb/` |
| A thing we want to build | `docs/prd/` |
| "The PRD says X but the code does Y" | `docs/gaps/` |
| "I ran it; here is what worked and what failed" | `docs/NN-slug.md` |
| A bug, a question, a decision to revisit | GitHub issue / issue comment |

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
| Sub-agent delegation | `delegate_task` / `kanban` | `Task` tool sub-agents (`.claude/agents/`) | vendor-specific | do the work inline, in the documented phase order |
| Plan scratch space | `~/.hermes/plans/*.md` | `scratchpads/` (gitignored) | `scratchpads/` | `scratchpads/` |
| Code graph (structural search) | `codegraph install` → `$HERMES_HOME/config.yaml` `mcp_servers` + `mcp-codegraph` toolset | `codegraph install` → `./.mcp.json` / `~/.claude.json` | `codegraph install` (Copilot targets auto-configured) | any MCP client: stdio `codegraph serve --mcp`; no MCP → CLI (`codegraph explore/node/impact`) |
| Pipeline invocation | `/goal <request>` | prompt the phases below in order | prompt the phases below in order | prompt the phases below in order |
| KB synthesis (funnel stage 3) | `/llm-wiki ./kb/` (native skill) | invoke `llm-wiki` skill on `./kb/` | invoke `llm-wiki` skill on `./kb/` | inline `.agents/skills/llm-wiki/SKILL.md`, apply its workflow to `./kb/` by hand |
| Issue tracking (funnel stage 7) | `gh issue create` / `gh issue comment` | same | same | same |

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


`.agents/skills/` holds this project's pinned skills; everything else installs at **host**
level. This template pins `root-cause` (the root-cause gate below depends on its exact
procedure); add `llm-wiki` and domain skills per project, vendoring only when a version must
travel with the repo. `.claude/agents/investigator.md` binds the *root-cause gate* for Claude
Code: a read-only sub-agent answering "why does X fail / what does X require" from cited repo
evidence, returning an explicit "not found", not a guess. Harnesses without sub-agents run the
same procedure inline from `.agents/skills/root-cause/SKILL.md`.

---

## The `/goal` Orchestration Workflow (coding-agent entry point)

Every substantive request is driven through the `/goal` pipeline. The coding agent MUST capture and follow this sequence.

**Kickoff prompt:**

```
/goal <whatever user request>

use pm skills for PRD, problem triage, success criteria definition and verification policy
use karpathy skill for codebase investigation and all resource analysis
prioritize task delegation over direct execution
use opencode-plan-build-orchestrator skill for all coding tasks
```

**Subsequent prompts (run in order):**

```
## sub1 — docs/tests gap sync
check gaps in docs/ and tests/ against codebase. update + drop obsolescences accordingly.

use pm skills for PRD, problem triage, success criteria definition and verification policy.
use karpathy skill for codebase investigation and all resource analysis.
prioritize task delegation over direct execution.
use opencode-plan-build-orchestrator skill for all coding tasks.

## sub2 — local CI
run github action locally using https://github.com/nektos/act

if problems surface, use pm skills for PRD, problem triage, success criteria definition and verification policy.
use karpathy skill for codebase investigation and all resource analysis.
prioritize task delegation over direct execution.
use opencode-plan-build-orchestrator skill for all coding tasks.

## sub3 — PR + CI monitor
PR using yeet. thoroughly provide context in the PR using coding agent docs skill. lastly monitor CI/CD in PR.

if problems surface, use pm skills for PRD, problem triage, success criteria definition and verification policy.
use karpathy skill for codebase investigation and all resource analysis.
prioritize task delegation over direct execution.
use opencode-plan-build-orchestrator skill for all coding tasks.

## sub4 — merge + redeploy
squash and merge to main all test-passed PRs.
then git checkout main and pull here.
lastly do full redeployment cycle from pull to serve.

use pm skills for PRD, problem triage, success criteria definition and verification policy.
use karpathy skill for codebase investigation and all resource analysis.
prioritize task delegation over direct execution.
use opencode-plan-build-orchestrator skill for all coding tasks.
```

### Running the pipeline without `/goal`

`/goal` is a Hermes slash command; a harness without it runs the **same** pipeline by
prompting the phases in order — the `sub1`–`sub4` labels are the cross-harness contract, so
**"go through sub1-4"** is valid everywhere. Paste the blocks above verbatim (minus the
`/goal` line), or work from this table:

| # | Phase | Do | Done when |
|---|-------|----|-----------|
| kickoff | Triage | Triage the request, ingest any new source material to `kb/raw/` + run `llm-wiki ./kb/`, write/refresh the PRD section grounded in `kb/`, define success criteria + verification policy | SC list exists with `_Verify:_` annotations, each traceable to a `kb/` page |
| `sub1` | Docs/tests gap sync | Diff `kb/` ↔ `docs/prd/` ↔ codebase ↔ `tests/`; record divergences in `docs/gaps/`, update, and drop obsolescences | No SC without a test; no doc claiming behaviour the code lacks; every `docs/gaps/` file has a Resolution |
| `sub2` | Local CI | Run the workflows locally with [`nektos/act`](https://github.com/nektos/act) — `-j unit`, `-j integration`, `-j secret-scan`, `-j doctrine`; E2E runs directly, not under act (see §6) | those four jobs green + `bash tests/run.sh --with-e2e` green |
| `sub3` | PR + CI monitor | Open the PR with full context in the body; watch remote CI to completion | Remote CI green |
| `sub4` | Merge + redeploy | Squash-merge green PRs, `git checkout main && git pull`, run the full redeploy cycle | Service healthy from a clean pull |

Report each phase's *Done when* before starting the next; a problem surfacing re-enters kickoff triage for that problem first.

**Skill-to-phase mapping** (install per README; substitute equivalents your harness ships):

| Phase | Skill | Output |
|-------|-------|--------|
| Knowledge synthesis (funnel stage 3) | `llm-wiki` on `./kb/` | `kb/` layer-2 pages + `index.md` + `log.md` |
| PRD / triage / success criteria / verification policy | `pm` skills — `create-prd`, `identify-assumptions-*`, `test-scenarios` | `PRD.md` + `docs/prd/NN-*.md` |
| Codebase & resource investigation | `karpathy-guidelines` | Evidence-based gap report → `docs/gaps/NN-*.md` |
| Root-cause / requirement questions | `root-cause` (Claude Code: `investigator` sub-agent) | Cited answer, or explicit "not found" |
| Empirical doc authoring (planned vs working) | `coding-agents-docs-guideline` | `docs/NN-slug.md` |
| Task delegation | harness delegation mechanism (see adapter table) | Scoped sub-agent tasks |
| All coding | `opencode-plan-build-orchestrator` | plan → build → verify via subagents |

---

## Standing Orders (ALWAYS apply)

Every session, every agent, every prompt — one line per rule, detail at its pointer.

### 1. Mandated Skills
`karpathy-guidelines`+`security-best-practices` always; `webapp-testing`; `coding-agents-docs-guideline` (stage 6); `llm-wiki` (stage 3, only `kb/` writer); `root-cause` (why-questions — cited evidence); `yeet` (git); `opencode-plan-build-orchestrator`. → `README.md` skill table

### 2. Delegation Rules
`opencode-plan-build-orchestrator`+`karpathy-guidelines` in every delegated coding goal; delegate over direct execution; the parent NEVER writes repo-tracked files (docs-only excepted); no delegation mechanism ⇒ parent codes but still reports the three steps. → `README.md` § *Harness Support*

### 3. Code Quality Rules
No `shell=True`; no `requests` without `timeout=N`; no secret inline, logged, or in a tracked doc (env or the gitignored `.credentials/`); inbound webhook signatures verified before the payload is read; bash `set -euo pipefail` + `$()`; image tags pinned.

### 4. Verification
Build+start, health check, test tiers, then `git diff --cached | grep -iE '(api_key|secret|token|password)' || echo "Clean"`. → `README.md` § *Testing*, `tests/run.sh`

### 5. PRD → Test → CI Pattern
Every SC carries an inline `_Verify:` (file + ID), a Test Mapping table and a CI/CD gate; ids `AC-X-0NN` unit, `AC-X-1NN` e2e, `AC-X-2NN` integration (hundreds digit names the tier); every tier has a runner **and** a CI job; shared-infra tests are opt-in (`INTEGRATION_NEEDS_OPT_IN=1` → `RUN_INTEGRATION_TESTS=1`). → `PRD.md` § *Verification Policy*

### 6. CI/CD Pipeline — Local-First, Then Remote
**No PR opens on a known-red local run**: `act push -j unit`, `-j integration`, `-j secret-scan`, `-j doctrine`, E2E via `bash tests/run.sh --with-e2e`. **Never `act push` unqualified or `-j e2e` on a host running this project live** — the directory name is the compose project, so its `docker compose up -d --build` replaces live containers. `ci.yml` gates unit → integration → e2e + `secret-scan`/`doctrine`; `sources-readonly.yml` gates `kb/raw/**` add-only (funnel rule 3). The `doctrine` job is funnel rule 10's enforcer and the Harness Adapter's structural half. → `docs/01-service-architecture.md` § *CI pipeline*

## Repository Structure

`README.md` § *Repository Structure* holds the tree. Load-bearing: `.agents/` is canonical and tracked; `.claude -> .agents`, so `.claude/skills`/`.claude/plugins` resolve.

## Development Commands

```bash
docker compose up -d           # start services     (adapt)
bash tests/run.sh              # unit + integration
bash tests/run.sh --with-e2e   # + the container tier
act push -j unit -j integration -j secret-scan -j doctrine
```

Tier flags: `tests/run.sh`; per-tier: `README.md` *Testing*.

## Security

- **Never commit `.env`, API keys or JWT secrets** — only `.example` shapes are tracked; CI's `secret-scan` enforces it.
- Credentials come from env or the gitignored `.credentials/`, never hardcoded.
- **No live value in `kb/` or `docs/`** (funnel rule 9) — `kb/raw/` is add-only, so a leak is uneditable.
- **Inbound webhook deliveries are signature-verified before the payload is read**; a sender with no stored secret is rejected, not parsed.
- Signing secrets are keyed per sender — one sender cannot sign another's deliveries.

## codegraph

[CodeGraph](https://github.com/colbymchenry/codegraph) — **primary graph search for coding agents** (tree-sitter → SQLite over MCP).

```bash
npm i -g @colbymchenry/codegraph   # once per machine
codegraph install                  # wires agent MCP configs
codegraph init                     # once per clone
codegraph node|query|callers|callees|impact|files|status   # CLI twins
```

MCP exposes **one tool by design** — `codegraph_explore`; the other 7 are unlisted (CLI twins or `CODEGRAPH_MCP_TOOLS=…`). `codegraph sync` before trusting the graph; tests via `codegraph affected --stdin`; CI sets `DO_NOT_TRACK=1`. → `kb/entities/codegraph.md`

### graphify (optional)

Knowledge graph over **non-code** artifacts (docs, SQL, configs, PDFs) — not the graph search (= codegraph): `graphify query|path|explain`. → `kb/comparisons/codegraph-vs-graphify.md`
