# 04 — gen-env script

> Status: Accepted · Confidence: high (requirements quoted from the user; behavior
> choices marked `[ASSUMPTION]`) · Gate: `unit` job in `.github/workflows/ci.yml`

## Context

`.env.example` evolves alongside the codebase; a deployed environment's real `.env`
drifts behind it. Reconciling by hand is error-prone: keys get renamed, comment blocks
carrying operator guidance get rewritten, and a stale `.env` silently keeps old
defaults. The repo needs one tool that regenerates `.env` from `.env.example`
line-by-line — including the exact comment blocks — either fresh (new deployment) or
as a value-carrying update (existing deployment).

User requirement (verbatim): *"Need a gen-env script that generate .env from
.env.example line-by-line including the exact comments block … Usage: gen new one for
fresh deployment. Only update the new one, keep existing one to update the existing
deployment."*

## Deliverable

`scripts/gen-env.py` — stdlib-only Python 3, no subprocess, no third-party imports.

| Mode | Invocation | Behavior |
|------|-----------|----------|
| fresh | `python3 scripts/gen-env.py --fresh` | Write `.env` as a **byte-identical** copy of `.env.example` (every line, every comment block, verbatim). |
| update | `python3 scripts/gen-env.py --update` | Write `.env.new`: the template lines from `.env.example` verbatim (comments and structure preserved), with the value of each `KEY=…` line replaced by the value that key has in the existing `.env`. Keys absent from `.env.example` are **dropped** and reported **by name only** on stdout. The existing `.env` is never modified. |
| help | `--help` | Usage text; exit 0. |

### Safety rules

- `--fresh` refuses to overwrite an existing `.env` without `--force`.
- `--update` refuses to overwrite an existing `.env.new` without `--force`.
- Dropped keys are printed as names only — values from the old `.env` are never
  echoed (they may hold secrets).
- Exit codes: `0` success, `1` usage or environment error (missing `.env.example`,
  missing `.env` for update mode, target exists without `--force`).

### Value-carry rule

`[ASSUMPTION]` A value is carried verbatim: the exact string after the first `=` of
the matching `KEY=` line in the existing `.env` (no quote normalization, no inline
comment stripping). Keys match on exact name; `export ` prefixes and blank/comment
lines in the existing `.env` are ignored.

## Success criteria

| ID | Criterion | Verify |
|----|-----------|--------|
| SC-ge-1 | Script exists at `scripts/gen-env.py`, stdlib-only, `--help` exits 0. | `tests/unit/test_gen_env.py::test_ac_gen_001_script_contract` |
| SC-ge-2 | Fresh mode output is byte-identical to `.env.example`. | `tests/unit/test_gen_env.py::test_ac_gen_002_fresh_byte_identical` |
| SC-ge-3 | Update mode output carries values key-by-key into the verbatim template, drops removed keys reporting names only, and never writes the existing `.env`. | `tests/unit/test_gen_env.py::test_ac_gen_003_update_carries_values` |
| SC-ge-4 | Refuses to clobber existing targets without `--force`; exits 1 on environment errors, 0 on success. | `tests/unit/test_gen_env.py::test_ac_gen_004_no_clobber_and_exit_codes` |
| SC-ge-5 | Values are carried verbatim after the first `=` (quotes and special characters preserved). | `tests/unit/test_gen_env.py::test_ac_gen_005_values_verbatim` |

### Test Mapping

| SC | Test (unit tier, `tests/unit/test_gen_env.py`) | Tier |
|----|------------------------------------------------|------|
| SC-ge-1..5 | `test_ac_gen_001` … `test_ac_gen_005` | unit (`AC-GEN-0NN`) |

Tests are hermetic: they import `scripts/gen-env.py` as a module (path insert, no
subprocess) and run against `tmp_path` fixtures, including a copy of the repo's real
`.env.example`.

## CI/CD gate

The `unit` job runs `pytest tests/unit` on every push and PR; a red `AC-GEN-*` test
blocks merge. No container tier involved.

## Source attribution

Requirement sourced from the user prompt (this topic's origin); no `kb/raw/` ingest —
the behavior contract is fully specified above. Funnel note: the script and its tests
are stage-5/6 outputs grounded in this PRD.

## Assumptions

- `[ASSUMPTION]` Update mode writes `.env.new` rather than editing `.env` in place —
  the "keep existing one to update the existing deployment" reading: the running
  deployment keeps its `.env` until an operator swaps in the regenerated file.
- `[ASSUMPTION]` Values carried verbatim (see *Value-carry rule*).
- `[ASSUMPTION]` A root-`README.md` one-liner in *Development Commands* documents
  discovery; no other docs changed beyond this topic and its stage-6 reality doc.
