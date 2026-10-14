# 06 — Quality Controls (Codified Review & QC Gates)

> Funnel stage 6 — empirical status. PRD: [docs/prd/06-quality-controls.md](prd/06-quality-controls.md).
> Gap record: [docs/gaps/06-quality-controls.md](gaps/06-quality-controls.md). Grounding:
> `kb/concepts/quality-controls.md` + 4 sibling concept pages; raw dossier
> `kb/raw/articles/quality-controls-audit-dossier.md`. Implemented in PR #15.

## What

Codified quality controls for an agent-driven, single-maintainer repo, per the
maintainer's doctrine that the large majority of QC must be rule-based (script +
test + CI job), not prose. Three layers shipped:

1. **Workflow hardening** (both workflows): top-level `permissions: {}` with
   job-level `contents: read`; all 9 `uses:` refs SHA-pinned with version
   comments; `persist-credentials: false` on all 7 checkouts; no
   `pull_request_target` (asserted).
2. **Gate architecture**: `qc-gate` aggregate job (`if: always()`, env-indirect
   `needs.<job>.result` reads) that fails unless all five tiers succeeded — the
   required check that closes GitHub's skipped=passing trap; `zizmor` job that
   fails on findings via exit code (annotations/CLI mode, not SARIF — SARIF
   always exits 0).
3. **Governance files** (advisory, labelled in-file): PR template with AI-assistance
   disclosure checkbox, Dependabot (github-actions/pip/docker, weekly), SECURITY.md
   (private vulnerability reporting), self-owning CODEOWNERS.
4. **The codified assertions**: `tests/unit/test_quality_controls.py` — 11 tests
   (AC-QC-001..010 + meta-test 012), each with verified negative controls, so the
   workflow-hygiene rules survive any future agent edit.

## Why

Verified pre-audit state: 13/13 merged PRs with zero reviews, no branch
protection/rulesets (direct pushes to main bypassed every gate), workflows
inheriting default token scope, tag-pinned actions, no dependency scanning or
governance files. Peer survey (14 popular MIT/Apache-2.0 repos, first-hand gh
api): top-level `permissions:` on 89% of sampled workflows, SHA pinning in 6/7
MIT-side repos, SECURITY.md 10/14, CODEOWNERS 10/14, Dependabot 8/14 — every
adopted control clears the ≥60% consensus bar; gitleaks/trufflehog (0/14)
deliberately not adopted. Solo-posture precedents (BaseCoat solo-dev profile,
mssql-mcp ADR-0033) validate approvals-off/protection-on with an empty bypass
list.

## How

- PRD SCs `AC-QC-001..012` in `docs/prd/06-quality-controls.md`, each with
  `_Verify:` annotations; implemented in PR #15 (commits b0144e9 + 299ee9b).
- Implementation delegated to a fresh subagent with full task text; verified by
  two-stage review (spec compliance by direct grep/pytest re-run, then quality).
- Three justified implementer deviations, all verified: gate reads results via
  env-indirection (`${{ }}` is evaluated before the shell runs, so a shell loop
  cannot index the `needs` context); zizmor job grants `contents: read` (clone
  needs it; no `security-events: write` — no SARIF); `test_ac_qc_010` added to
  close the PRD's own test-mapping range.

## Verification

| SC | Check | Result |
|----|-------|--------|
| AC-QC-001 | `grep -c '^permissions:'` on both workflows | 2/2 files |
| AC-QC-002 | every `uses:` ends 40-hex (allowlist empty) | 9/9 pinned |
| AC-QC-003 | persist-credentials count == checkout count | 7 == 7 |
| AC-QC-004 | `pull_request_target` grep | 0 hits |
| AC-QC-005..008 | file existence + content assertions | 11/11 pytest |
| AC-QC-009 | qc-gate `if: always()` + 5 needs + fail-on-non-success | simulated both paths |
| AC-QC-010 | zizmor job, failing-exit mode | present |
| AC-QC-012 | 80/20 codified split | every 001-010 control = script+test+CI |
| full suite | `python3 -m pytest tests/unit -q` | 28 passed |
| YAML | parse all three configs | ALL YAML OK |
| AC-QC-011 | ruleset via gh api (post-merge) | enabled + read back post-merge (see below) |

## AC-QC-011 post-merge verification

Ruleset `qc-main-gate` created on `main` after merge, via `gh api` POST
`/repos/bachkukkik/template-agentic-ready-repo/rulesets` (bypass list empty):
require pull request, require status check `Quality Control Gate` (strict
up-to-date), block force pushes, block deletions. Verified by GET read-back and
by exercising the gate: the follow-up docs commit went through a PR because
direct pushes to `main` are now rejected.

## What Works

- Full unit suite (28 tests incl. 11 new AC-QC assertions) — local and CI.
- All 8 PR checks green on PR #15 (run 38523046562): Unit, Integration,
  Docker E2E, Secret Scan, Doctrine Integrity, **Quality Control Gate**,
  **Workflow Static Analysis (zizmor)**, check-raw-readonly.
- zizmor passes on the hardened workflows (fail-on-findings mode) — the SHA
  pins, `permissions: {}`, and `persist-credentials: false` satisfy its
  `unpinned-uses`, `excessive-permissions`, and `artipacked` audits.
- qc-gate proves the skipped≠passing fix: it runs and evaluates every tier
  result even when upstream jobs skip.

## What Fails / Limits

- AC-QC-011 pending: ruleset enabled post-merge.
- `pipx install zizmor` in the zizmor job is itself unpinned (Scorecard
  Pinned-Dependencies debt; noted as PRD assumption).
- `service/Dockerfile` base image digest-unpinned; `bats-core` clone unattested;
  `tests/requirements.txt` not hash-pinned — logged as future Scorecard items.
- Repo-level push protection requires paid Secret Protection — account-level
  (free) stays the prevention layer; the CI secret-scan job remains the
  auditable enforcement layer.

## Resolution

AC-QC-001..010+012 close the `docs/gaps/06-quality-controls.md` divergence in
code; AC-QC-011 closes it in settings post-merge.

## Verdict

`works` — every SC verified: AC-QC-001..010+012 by pytest (28/28) + 8/8 green CI
checks on PR #15; AC-QC-011 by ruleset read-back + gate behavior (direct push
rejected). Limits section lists known, accepted debts (unpinned pipx/zizmor,
unpinned Dockerfile digest, un-hashed requirements) — none blocking.
