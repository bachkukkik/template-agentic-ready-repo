# 06 — Quality Controls (Codified Review & QC Gates)

> Funnel stage 4. Grounded in `kb/concepts/quality-controls.md` (overview),
> `kb/concepts/github-merge-gates.md`, `kb/concepts/actions-hardening.md`,
> `kb/concepts/scanning-without-advanced-security.md`, `kb/concepts/qc-test-tiers.md`.
> Raw evidence: `kb/raw/articles/quality-controls-audit-dossier.md` (verified
> inventory, 3 research tracks, 14-repo MIT/Apache peer survey).

## Problem

The repo's quality controls are test-heavy but gate-free: three test tiers run in
CI, yet 13/13 merged PRs had zero reviews and `main` has no branch protection —
a direct `git push` bypasses every gate. Workflows inherit default token scope,
pin actions by mutable tag, and there is no dependency scanning, governance file,
or workflow linter. Peer repos (14 surveyed) ship all of these. Critically, the
existing gates that DO exist are enforced; the missing ones must also land as
**executable rules**, not prose.

## Codification doctrine (the 80/20 rule)

The maintainer's directive: quality control and review must be **predominantly
rule-based** — codified as script + test + CI job, in the same spirit as the
existing `AGENTS.md < 20KB` budget test. Target split: **≥80% of controls
machine-checkable**, ≤20% human/agent judgment (merge decisions, design
trade-offs, AI-contribution stewardship). Advisory artifacts (CODEOWNERS, PR
template) are shipped and labelled advisory — they route, they don't gate.

Success criteria below are numbered `AC-QC-0NN` (unit tier — all controls here
are pure logic: file existence, grep patterns, pytest assertions).

## Success Criteria

| ID | Criterion | Grounded in |
|----|-----------|-------------|
| AC-QC-001 | Every workflow file sets a top-level `permissions:` block | [[actions-hardening]] (89% peer consensus) |
| AC-QC-002 | Every `uses:` in every workflow is SHA-pinned (40-hex), or listed in an allowlist-debt register with reason + retire condition | [[actions-hardening]] (6/7 peer repos) |
| AC-QC-003 | Every `actions/checkout` step sets `persist-credentials: false` | [[actions-hardening]] |
| AC-QC-004 | No workflow uses the `pull_request_target` trigger | [[actions-hardening]] |
| AC-QC-005 | `.github/pull_request_template.md` exists and demands: scope, test evidence, AI-disclosure checkbox | [[quality-controls]] (8/14 peers; AI-disclosure = astral-sh/TypeScript norm) |
| AC-QC-006 | `.github/dependabot.yml` covers `github-actions`, `pip`, `docker` ecosystems | [[scanning-without-advanced-security]] (8/14 peers) |
| AC-QC-007 | `SECURITY.md` exists at repo root with a reporting contact (no live secrets) | [[quality-controls]] (10/14 peers) |
| AC-QC-008 | `CODEOWNERS` exists, owns itself + `.github/workflows/` + `AGENTS.md`; labelled advisory in-file | [[github-merge-gates]] (10/14 peers) |
| AC-QC-009 | An aggregate CI gate job (`if: always()`) fails unless unit+integration+e2e+secret-scan+doctrine all succeeded | [[qc-test-tiers]] (skipped≠passing trap) |
| AC-QC-010 | A zizmor job runs workflow static analysis; findings fail CI (annotations mode, not SARIF-only) | [[actions-hardening]] (4/14 peers, rising) |
| AC-QC-011 | Branch protection/ruleset on `main`: require PR, require the aggregate gate check (strict), block force-push/deletion | [[github-merge-gates]] (Scorecard Tier-1 baseline) |
| AC-QC-012 | The 80/20 codification split holds: every control in AC-QC-001..010 is enforced by a pytest assertion or CI job, not prose | [[quality-controls]] doctrine |

**Deliberately NOT adopted** (peer data says no): gitleaks/trufflehog Actions jobs
(0/14 peers; native secret scanning is free on public repos; the hand-rolled
generic-shape regex job stays — it covers a class GitHub's free tier misses);
required approvals ≥1 (structurally unsatisfiable for one human — revisit when a
second reviewer exists); merge queue (org-only).

_Verify: `tests/unit/test_quality_controls.py` (all AC-QC-0NN unit assertions) + `.github/workflows/ci.yml` `qc-gate` job (AC-QC-009) + `gh api repos/.../rulesets` (AC-QC-011, verified post-merge)._

## Test Mapping

| SC | Test file | Test ID |
|----|-----------|---------|
| AC-QC-001..010, 012 | `tests/unit/test_quality_controls.py` | `test_ac_qc_001` … `test_ac_qc_012` |
| AC-QC-009 | `.github/workflows/ci.yml` `qc-gate` job | CI-side; asserted structurally by `test_ac_qc_009` |
| AC-QC-011 | GitHub settings (ruleset via gh api) | verified post-merge by command, recorded in `docs/06-*.md` |

## CI/CD Gate

The `unit` job runs `tests/unit/test_quality_controls.py`; the new `qc-gate`
aggregate job must pass before merge (required check). No PR merges with a red
test.

## Confidence

High — every control is backed by verified current-state evidence plus first-hand
peer-repo data; adoption threshold (≥60% peer consensus or published baseline) met
by every adopted control.

## Assumptions

- [ASSUMPTION] Single-maintainer workflow continues: self-merge after green CI is
  the intended path; required approvals intentionally off.
- [ASSUMPTION] zizmor/actionlint run via pinned third-party actions; if supply-chain
  posture of those actions degrades, fall back to pipx/git-ref installs inside the job.
