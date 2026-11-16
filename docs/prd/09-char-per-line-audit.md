# 09 — Char-per-line audit

> Status: Accepted · Confidence: high · Gate: `unit` job (`Machine gates`)

## Context

A prose line wider than 80 columns re-wraps in every terminal, diff viewer and
agent context window, so reading cost follows the renderer instead of the text.
This repo enforced no width rule until the reflow: the widest measured line ran
to 685 characters, and nothing failed when the next one landed.

`[ASSUMPTION]` No `kb/` page covers line width — `grep -ril 'width' kb/`
returns nothing — so the 80-column default is a policy choice, not a
knowledge-backed finding. It follows the conventional terminal width and the
measure the repo's older prose already keeps.

## Deliverable

`scripts/audit-chars.py` — stdlib-only CLI:

- Default scope: `docs/**/*.md` plus `README.md` and `AGENTS.md`. Symlinks are
  skipped, so the `CLAUDE.md` alias of `AGENTS.md` is never counted twice.
- Markdown is stripped before measurement — fenced code blocks, tables,
  headings, blockquote markers, list markers and footnote references never
  count — so a wide table or a long URL inside a fence is exempt by
  construction. Every other file type is measured raw, with no exemptions.
- `--max-chars N` (default 80). The run is **strict by default**: exit 1 when
  any wrap-able measured line is over the cap, so CI can hold the line without
  a ratchet. `--advisory` reports the same offenders and exits 0, for staged
  adoption. `--json`; `--verbose`. There is no `--strict` flag.
- An over-cap measured line carrying a whitespace-delimited token wider than
  the cap — a long URL or bare link — is classified `unbreakable`: no
  whitespace wrap can bring that token under the cap, so the line is never an
  offender and never a failure. It is counted separately in
  `totals['unbreakable']` and printed as `unbreakable: U ...`. A line of
  ordinary words is always an offender, because every token fits and a wrap
  fixes the width.
- Offenders print as `file:line: [N chars] first 80 chars`, capped at 20.

Success criteria:

- **SC-cl-1** — The gate is hard: the default run exits 1 on any wrap-able
  over-cap line, and 0 on this repo, whose measured lines all fit the cap.
  _Verify:_ `tests/unit/test_audit_chars.py` (`AC-CHARS-001`).
- **SC-cl-2** — A 120-character prose line fails the default run; a fenced
  block, a table row and a heading of the same width are exempt.
  _Verify:_ `tests/unit/test_audit_chars.py` (`AC-CHARS-002`).
- **SC-cl-3** — `--help` exits 0, a missing input exits 1 naming the path, the
  documented default is 80, and `--advisory` exits 0 on an over-cap line.
  _Verify:_ `tests/unit/test_audit_chars.py` (`AC-CHARS-003`).
- **SC-cl-4** — A non-markdown file is measured raw: a 100-character source
  line is reported at its full width.
  _Verify:_ `tests/unit/test_audit_chars.py` (`AC-CHARS-004`).
- **SC-cl-5** — The auditor and its test module hold the cap they enforce.
  _Verify:_ `tests/unit/test_audit_chars.py` (`AC-CHARS-005`).
- **SC-cl-6** — An over-cap line carrying a token wider than the cap (a long
  URL) is counted as `unbreakable` and does not fail the run, whether the
  token stands alone or follows a word; a 120-character line of ordinary
  short words is an offender and does fail it.
  _Verify:_ `tests/unit/test_audit_chars.py` (`AC-CHARS-006`).

`tests/unit/test_audit_chars.py` — hermetic unit tier (`AC-CHARS-0NN`):

| ID | Asserts |
|----|---------|
| `AC-CHARS-001` | Default (strict) run exits 0: 0 over, paths relative. |
| `AC-CHARS-002` | 120-char prose fails; fence/table/heading exempt. |
| `AC-CHARS-003` | `--help` 0; missing path 1; default 80; `--advisory` 0. |
| `AC-CHARS-004` | Non-markdown raw; 100-char line named. |
| `AC-CHARS-005` | Script and test fit the 80 cap. |
| `AC-CHARS-006` | Over-wide token exempts its line; short-word prose fails. |

## Test Mapping

| SC | Test | Tier |
|----|------|------|
| Repo passes the gate at 0 over | `AC-CHARS-001` | unit |
| Discrimination and exemptions | `AC-CHARS-002` | unit |
| CLI contract and `--advisory` | `AC-CHARS-003` | unit |
| Raw path for non-markdown | `AC-CHARS-004` | unit |
| Sources fit the cap | `AC-CHARS-005` | unit |
| Unbreakable over-wide token line | `AC-CHARS-006` | unit |

## CI/CD gate

The `unit` job's `Machine gates` step runs
`python3 scripts/audit_pyramid.py`, `python3 scripts/audit-chars.py` and
`python3 scripts/audit-size.py`, so the char gate fails the job directly — a
wrap-able line over 80 characters blocks a merge without waiting on pytest.
The tests pin the behaviour; the step is the enforcement. `--advisory` is for
local adoption runs only, never for CI.

## Source attribution

No `kb/` page covers line width; the 80-column default is `[ASSUMPTION]`
above. Conventions: `AGENTS.md` §5 (PRD → Test → CI) and `PRD.md`
§ *Verification Policy*. The gate shape — one numeric cap, exit 1 on a
violation, a reporting-only flag for adoption — mirrors `scripts/audit-ste.py`
(`docs/prd/05-ste-audit.md`).
