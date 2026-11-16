# 10 — File-size audit

> Status: Accepted · Confidence: high · Gate: `unit` job (pytest `tests/unit`)

## Context

A file that grows without a ceiling stops being reviewable: a 200 KB article
is skipped by reviewers and truncated by context windows, and an agent that
appends to it makes the problem worse without a single failing test. Nothing
measured tracked file size before this gate. The largest tracked file is
19830 bytes (`kb/raw/articles/quality-controls-audit-dossier.md`) — 650
bytes under a 20 KB cap, so the cap is live, not theoretical.

`[ASSUMPTION]` No `kb/` page covers file size — `grep -ril 'size cap' kb/`
returns nothing — so 20 KB is a policy choice. It is the largest round budget
that still holds the current corpus with headroom.

## Deliverable

`scripts/audit-size.py` — stdlib-only CLI:

| Flag | Default | Effect |
|------|---------|--------|
| `FILE...` | — | Measure exactly these paths instead of the scope. |
| `--max-kb` | `20.0` | Cap = `int(max_kb * 1024)` = 20480 bytes. |
| `--json` | off | One JSON object instead of table and findings. |
| `--verbose` | off | Print the per-file table even when clean. |

- Scope: exactly the regular files in `git ls-files` — 87 today out of 91
  entries, the 4 skipped being symlinks or gitlinks (`CLAUDE.md`,
  `.github/copilot-instructions.md`, `.claude/skills`, `.claude/plugins`).
  Untracked files never fail the gate. A tree that is not a git repository
  falls back to a recursive walk.
- The cap is inclusive: exactly 20480 bytes passes, 20481 fails.
- Strict by default: exit 1 when any measured file is over the cap.
- An unreadable file is a warning on stderr, counted as 0 bytes, never raised.

Success criteria:

- **SC-fs-1** — Every tracked file is within 20480 bytes, the totals agree
  with the per-file rows, and the largest row sorts first.
  _Verify:_ `tests/unit/test_audit_size.py` (`AC-SIZE-001`).
- **SC-fs-2** — The cap is inclusive: 20481 bytes fails, 20480 passes, and
  `--max-kb 30` lifts the cap over the same file.
  _Verify:_ `tests/unit/test_audit_size.py` (`AC-SIZE-002`).
- **SC-fs-3** — The default is 20.0 KB, `limit_bytes` yields 20480, `--help`
  exits 0 and a missing path exits 1.
  _Verify:_ `tests/unit/test_audit_size.py` (`AC-SIZE-003`).
- **SC-fs-4** — Positional paths replace the tracked scope rather than add
  to it.
  _Verify:_ `tests/unit/test_audit_size.py` (`AC-SIZE-004`).
- **SC-fs-5** — The auditor and its test module hold the 80-column rule.
  _Verify:_ `tests/unit/test_audit_size.py` (`AC-SIZE-005`).

`tests/unit/test_audit_size.py` — hermetic unit tier (`AC-SIZE-0NN`):

| ID | Asserts |
|----|---------|
| `AC-SIZE-001` | Real tree exit 0; over 0; largest first. |
| `AC-SIZE-002` | 20481 fails; 20480 passes; `--max-kb` lifts. |
| `AC-SIZE-003` | Default 20.0; 20480 bytes; help; bad path. |
| `AC-SIZE-004` | Explicit paths replace the scope. |
| `AC-SIZE-005` | Both new files fit 80 columns. |

## Test Mapping

| SC | Test | Tier |
|----|------|------|
| Shipped tree within cap | `AC-SIZE-001` | unit |
| Inclusive boundary and flag | `AC-SIZE-002` | unit |
| CLI contract and arithmetic | `AC-SIZE-003` | unit |
| Explicit-path override | `AC-SIZE-004` | unit |
| Sources fit the cap | `AC-SIZE-005` | unit |

## CI/CD gate

The `unit` job runs `python3 -m pytest tests/unit` on every push and PR, so
`test_size_real_repo_is_within_cap` is the gate. Unlike the width audit, this
gate is strict by default: `python3 scripts/audit-size.py` itself exits 1 on
an over-cap tracked file, so the same rule holds whether CI runs the test or
an agent runs the CLI by hand. A failure names the file and its byte count.

## Source attribution

No `kb/` page covers file size; the 20 KB budget is `[ASSUMPTION]` above.
Conventions: `AGENTS.md` §5 (PRD → Test → CI) and `PRD.md` § *Verification
Policy*. The tracked-scope rule follows funnel rule 1 (`AGENTS.md`): a
document outside stages 1–6 is a defect, and an untracked file is not part of
the doctrine the gate protects.
