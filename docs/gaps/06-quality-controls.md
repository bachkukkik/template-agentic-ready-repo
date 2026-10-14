# 06 — Quality Controls: PRD vs codebase

**Kind:** `prd ↔ code`
**Opened:** 2026-10-14
**PRD:** [docs/prd/06-quality-controls.md](../prd/06-quality-controls.md)
**Grounding:** `kb/raw/articles/quality-controls-audit-dossier.md` (verified inventory)

## Observed divergence

PRD 06 (accepted) specifies twelve controls (AC-QC-001..012). The codebase at
d54a213 implements none of them:

| SC | Required | Actual (verified 2026-10-14) |
|----|----------|------------------------------|
| AC-QC-001 | top-level `permissions:` in every workflow | absent in `ci.yml` + `sources-readonly.yml` |
| AC-QC-002 | SHA-pinned `uses:` (or allowlist register) | `actions/checkout@v4`, `actions/setup-python@v5` (tags, ×6) |
| AC-QC-003 | `persist-credentials: false` on checkouts | absent ×6 |
| AC-QC-004 | no `pull_request_target` | satisfied (none used) — assertion test still needed to hold the line |
| AC-QC-005 | PR template w/ scope+tests+AI-disclosure | no `.github/pull_request_template.md` |
| AC-QC-006 | dependabot: actions+pip+docker | no `.github/dependabot.yml` |
| AC-QC-007 | SECURITY.md | absent |
| AC-QC-008 | CODEOWNERS (self-owning, advisory) | absent |
| AC-QC-009 | aggregate always-run gate job | tier jobs chained by `needs:` only (skipped=passing trap) |
| AC-QC-010 | zizmor CI job | absent |
| AC-QC-011 | ruleset on main | `/rulesets` → `[]`; direct pushes to main bypass all CI |
| AC-QC-012 | 80/20 codified split | n/a until 001-010 land; then asserted by test |

Also observed (adjacent, pre-existing): `tests/unit/test_quality_controls.py`
does not exist; no lint entry point for shell/yaml.

## Resolution

Implemented in the qc-audit branch: workflow hardening + `qc-gate` aggregate +
zizmor job (AC-QC-001,002,003,004,009,010), governance files (005-008),
`tests/unit/test_quality_controls.py` (001-008,012), GitHub ruleset via gh api
post-merge (011, verified in `docs/06-quality-controls.md`). Gap closes when CI
is green on the PR and the ruleset verifies.
