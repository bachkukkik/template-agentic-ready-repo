# PRD 01 — Example Topic

> This demonstrates the PRD structure with Success Criteria, Test Mapping, and CI/CD Gate.
> Replace with actual project requirements.

## Context

[Problem statement, target users, constraints.]

## Success Criteria

- **SC1** — The system shall route a known path to its handler. _Verify:_ `tests/unit/test_routing.py` (AC-EXM-001..003).

- **SC2** — The running container shall answer `/health` and `/`. _Verify:_ `tests/e2e/example.bats` (AC-EXM-101, AC-EXM-102).

- **SC3** — The service shall serve those routes over a real socket, out of process. _Verify:_ `tests/integration/test_service_endpoints.py` (AC-EXM-201..203).

## Test Mapping

| Expected behavior | Test file | Test IDs |
|---|---|---|
| `/health`, `/`, and an unknown path map to 200/200/404 | `tests/unit/test_routing.py` | AC-EXM-001, AC-EXM-002, AC-EXM-003 |
| The container answers `/health` and `/` | `tests/e2e/example.bats` | AC-EXM-101, AC-EXM-102 |
| The out-of-process service answers over HTTP | `tests/integration/test_service_endpoints.py` | AC-EXM-201, AC-EXM-202, AC-EXM-203 |

The hundreds digit encodes the tier — `0NN` unit, `1NN` e2e, `2NN` integration
(AGENTS.md §5).

## Assumptions

- [ASSUMPTION] [Assumption 1]
- [ASSUMPTION] [Assumption 2]

## Confidence

**Medium** — Based on [source].

## CI/CD Gate

All tests run in CI per `.github/workflows/ci.yml`. No PR merges with a red test.
