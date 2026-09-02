# [Project Name] — Product Requirements Document

> Version: 0.1.0
> Date: 2026-01-01
> Status: **TEMPLATE** — Replace with project details
> Knowledge Base: `kb/`

---

## Repo Identity

This repository is the **real deployment repository** — the codebase the engineering team builds, tests, and ships to production.

**Brand:** [Project name]. Tagline: [tagline].

## Funnel Position

This PRD set is **stage 4** of the Document Funnel defined in `AGENTS.md`. It is
grounded in `kb/` (stage 3) and compared against the codebase in `docs/gaps/`
(stage 5). Any claim here with no `kb/` page behind it carries `[ASSUMPTION]` or is
dropped. Verified behaviour is never recorded here — it goes to `docs/NN-slug.md`.

## Source-of-Truth Doctrine

Three sources feed this PRD set. When they conflict, this doctrine resolves:

1. **KB wins on semantics and behaviour.** When the KB (`kb/`) and any PRD disagree on *what* something means or *how* a flow behaves, the KB is authoritative.
2. **Repo artifacts win on literal values.** For *literal* values — config values, port numbers, version strings — the repo's own files are the source of truth.
3. **Top-level PRD > detail PRD.** When this file and a `docs/prd/*.md` disagree, this file wins.

## Quick Reference

| # | Topic | Document | Status |
|---|-------|----------|--------|
| 01 | [Topic] | [docs/prd/01-topic.md](docs/prd/01-topic.md) | Template |

## Verification Policy

Every PRD topic must satisfy:

1. **Context** — clear problem statement, target users, constraints.
2. **Success criteria** — SMART metrics.
3. **Test mapping** — every SC carries an inline `_Verify:` annotation pointing to the test file + test ID.
4. **CI/CD gate** — no PR merges with a red test.
5. **Source attribution** — links to KB concept pages.
6. **Assumption flagging** — `[ASSUMPTION]` markers for unverified claims.
7. **Confidence rating** — high, medium, or low.

### Global Test Suite Structure

| Tier | Directory | Runner | CI Job | ID range | Covers |
|------|-----------|--------|--------|----------|--------|
| Unit + Component | `tests/unit/` | pytest | `unit` | `AC-X-0NN` | Pure logic, no transport |
| E2E | `tests/e2e/` | bats | `e2e` | `AC-X-1NN` | Full flows against a running container |
| Integration | `tests/integration/` | pytest | `integration` | `AC-X-2NN` | Cross-process / persistence |

**Test ID convention:** `AC-<DOMAIN>-NNN` (e.g., `AC-EXM-001`). The hundreds digit
encodes the tier, per the table above.

**CI gate:** All CI jobs must pass before merge. No PR merges with a red test.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-01 | Template created. |
| 0.2.0 | 2026-09-02 | Test tiers made executable; ID ranges encode the tier. |
