# PRD 01 — Example Topic

> This demonstrates the PRD structure with Success Criteria, Test Mapping, and CI/CD Gate.
> Replace with actual project requirements.

## Context

[Problem statement, target users, constraints.]

## Success Criteria

- **SC1** — The system shall [do something verifiable]. _Verify:_ `tests/unit/example.test.ts` (AC-EXM-001).

- **SC2** — The system shall [do something else]. _Verify:_ `tests/e2e/example.spec.ts` (AC-EXM-002).

- **SC3** — The system shall [handle an edge case]. _Verify:_ `tests/integration/example.test.ts` (AC-EXM-003).

## Test Mapping

| Expected behavior | Test file | Test IDs |
|---|---|---|
| [Behavior 1] | `tests/unit/example.test.ts` | AC-EXM-001 |
| [Behavior 2] | `tests/e2e/example.spec.ts` | AC-EXM-002 |
| [Behavior 3] | `tests/integration/example.test.ts` | AC-EXM-003 |

## Assumptions

- [ASSUMPTION] [Assumption 1]
- [ASSUMPTION] [Assumption 2]

## Confidence

**Medium** — Based on [source].

## CI/CD Gate

All tests run in CI per `.github/workflows/ci.yml`. No PR merges with a red test.
