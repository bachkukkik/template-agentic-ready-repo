# PRD 07 — Optional PR-Agent

> Funnel stage 4 (intent). The CI-hardening requirements are grounded in
> `kb/concepts/actions-hardening.md` and `kb/concepts/qc-test-tiers.md` (see
> *Source attribution*); PR-Agent-specific claims that no `kb/` page covers are
> `[ASSUMPTION]`-marked.
> Status: Accepted — dormant until PR_AGENT_ENABLED=true.

## Summary

Add an **optional, off-by-default** AI code-review job to the template. The job runs
Qodo PR-Agent on `pull_request` events and posts a review as PR comments. A repo
variable, not a secret, is the switch. A fresh clone inherits no model vendor and no
credential requirement.

## Background

An agentic PR review is the kind of capability this template should demonstrate but not
impose. PR-Agent (`qodo-ai/pr-agent`, Apache-2.0) reviews a diff and answers in the PR
thread. It is distributed as a Docker-based GitHub Action and configured through
dynaconf `SECTION__KEY` env overrides, so any OpenAI-compatible endpoint works: a
LiteLLM gateway, vLLM, Ollama or OpenRouter. The opt-in shape follows the existing
codegraph pattern in `README.md`: one commented block, one install step, no effect
until a maintainer asks for it. [ASSUMPTION] Apache-2.0 licensing and the dynaconf
override behavior are taken from the upstream project and its release notes, not from a
`kb/` page. [ASSUMPTION] A custom OpenAI-compatible base URL is the normal deployment
shape for this template's users.

## Objective

Prove, by assertions in the unit tier, that the PR-Agent integration is (a) present,
(b) pinned and least-privileged, (c) inert unless explicitly enabled, and (d) wired to
exactly three customization points: base URL, API key, model.

## Success Criteria

- **SC-pa-1** — `.github/workflows/pr-agent.yml` exists and parses as YAML, and its one
  `uses:` ref is SHA-pinned (40-hex, with a `# vX` comment), not a tag or branch
  (AC-QC-002).
  _Verify:_ `tests/unit/test_pr_agent_workflow.py` (AC-PA-001).

- **SC-pa-2** — The workflow declares `permissions: {}` at top level. The single job
  elevates to `pull-requests: write` and `issues: write`, and to nothing else
  (AC-QC-001).
  _Verify:_ `tests/unit/test_pr_agent_workflow.py` (AC-PA-002).

- **SC-pa-3** — The job carries `if: vars.PR_AGENT_ENABLED == 'true' && github.event.pull_request.head.repo.full_name == github.repository`,
  so an unset or non-`true` variable skips the job and a fork PR is skipped
  explicitly. The switch is a variable, not a secret.
  _Verify:_ `tests/unit/test_pr_agent_workflow.py` (AC-PA-003).

- **SC-pa-4** — The `env:` block maps the three customization points:
  `OPENAI__API_BASE` ← `vars.OPENAI_BASE_URL`, `OPENAI__KEY` ←
  `secrets.OPENAI_API_KEY`, `CONFIG__MODEL` ← `vars.OPENAI_DEFAULT_MODEL`. It also maps
  `GITHUB_TOKEN` ← `secrets.GITHUB_TOKEN`. `OPENAI__API_BASE` and `CONFIG__MODEL` carry
  `||` fallbacks — OpenAI's public base URL, and PR-Agent v0.49.0's `model` default
  `gpt-6.1-sol` — because an unset Actions variable interpolates to `""` and would
  otherwise override the dynaconf default. No credential is written inline.
  _Verify:_ `tests/unit/test_pr_agent_workflow.py` (AC-PA-004).

- **SC-pa-5** — `.env.example` ends with one commented `PR-Agent (optional)` section
  naming `PR_AGENT_ENABLED`, `OPENAI_BASE_URL`, `OPENAI_API_KEY` and
  `OPENAI_DEFAULT_MODEL`, all with placeholder values only. Existing keys are
  unchanged.
  _Verify:_ `tests/unit/test_pr_agent_workflow.py` (AC-PA-005).

## Test Mapping

| Expected behavior | Test file | Test IDs |
|---|---|---|
| Workflow exists, parses as YAML, action is SHA-pinned | `tests/unit/test_pr_agent_workflow.py` | AC-PA-001 |
| Deny-all top-level permissions, job elevates to PR + issue write | `tests/unit/test_pr_agent_workflow.py` | AC-PA-002 |
| Job is gated on `vars.PR_AGENT_ENABLED == 'true'` plus the same-repo fork guard | `tests/unit/test_pr_agent_workflow.py` | AC-PA-003 |
| Env wiring covers base URL, key, model, GitHub token, with `||` fallbacks and no inline credential | `tests/unit/test_pr_agent_workflow.py` | AC-PA-004 |
| `.env.example` documents the optional PR-Agent capability keys | `tests/unit/test_pr_agent_workflow.py` | AC-PA-005 |

The hundreds digit encodes the tier: `0NN` unit, `1NN` e2e, `2NN` integration
(AGENTS.md §5). All criteria here are unit-tier: a file read plus a YAML parse, no
transport and no network.

## Dormancy

The feature does nothing unless `PR_AGENT_ENABLED` is set to `true`. With the variable
unset, the job is skipped and no secret is read. With the variable set but the key
missing, the action cannot reach a model and fails safe. The job's `if:` also skips a
fork PR explicitly (`head.repo.full_name == github.repository`), so "reviews stay
same-repo" holds by construction; a fork PR never receives secrets on `pull_request`
either. The trigger stays `pull_request` and never `pull_request_target` (AC-QC-004).

## CI/CD Gate

`AC-PA-001..005` run in the **unit** job (`python3 -m pytest tests/unit -v` in
`.github/workflows/ci.yml`; locally `act push -j unit` or `bash tests/run.sh`). Any
unpinned ref, missing gate, widened permission or missing env mapping fails the unit
tier, which the `qc-gate` aggregate job (AC-QC-009) reports as red. The workflow itself
is also read by the `zizmor` job, so a mutable `uses:` ref is a second, independent
failure.

## Source attribution

- `kb/concepts/actions-hardening.md` — grounds the AC-QC-001/002/004 cross-references
  above: deny-all top-level `permissions:`, 40-hex SHA pinning of every `uses:`, and the
  ban on `pull_request_target`.
- `kb/concepts/qc-test-tiers.md` — grounds the AC-QC-009 cross-reference: an aggregate
  gate job must fail unless every tier succeeded, so a skipped job is never read as a
  pass.

## Assumptions

- [ASSUMPTION] Upstream `qodo-ai/pr-agent` v0.49.0 is Apache-2.0, its action runs
  `github_action_runner.py` in a Docker image, and it reads `SECTION__KEY` env
  overrides — taken from the pinned tag, not from a `kb/` page.
- [ASSUMPTION] `vars.OPENAI_BASE_URL`, `vars.OPENAI_DEFAULT_MODEL` and
  `secrets.OPENAI_API_KEY` are the industry-conventional names for the three
  customization points. PR-Agent never sees them directly: the workflow maps each onto
  a dynaconf `SECTION__KEY` env var. Nothing upstream requires these names.
- [ASSUMPTION] A 15-minute timeout is sufficient for a review; a large PR on a slow
  model may need more.
- [ASSUMPTION] `pull-requests: write` plus `issues: write` is the full scope PR-Agent
  needs. It reads the diff through the pull-requests scope, so `contents: read` is not
  added.

## Confidence

**Medium.** The workflow shape and its assertions are verified locally by the unit
tier. The upstream behavior behind each `[ASSUMPTION]` is unverified in this repo until
a first opted-in run produces a review comment — that run is the stage-6 observation
that would close these gaps.
