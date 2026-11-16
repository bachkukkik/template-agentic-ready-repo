# 09 — Char-per-Line Audit

## What

`scripts/audit-chars.py` measures the width of every prose line under `docs/`
plus `README.md` and `AGENTS.md`, and fails the run when any wrap-able line is
over `--max-chars` (default 80).

## Why

A line wider than 80 columns re-wraps differently in every terminal, diff
viewer and agent context window, so reading cost follows the renderer instead
of the text. The repo had no such rule: the widest measured line ran to 685
characters, and nothing failed when the next one landed. The reflow came first
and the gate second — a hard gate can only land on a corpus that passes it.

## How

Scope and exemptions:

| Input | Measured | Exempt |
|-------|----------|--------|
| `docs/**/*.md` | prose lines only | fences, tables, headings |
| `README.md` | prose lines only | blockquote, list, footnote marks |
| `AGENTS.md` | prose lines only | as above |
| any other path | raw, char for char | nothing |

Symlinks are skipped, so the `CLAUDE.md` alias of `AGENTS.md` is never counted
twice. A markdown line is stripped of its blockquote marker, list marker and
footnote references before it is measured; a non-markdown file is measured
raw, because a `.py` or `.yml` has no markdown exemptions to honour.

Flags:

| Flag | Default | Effect |
|------|---------|--------|
| `FILE...` | default scope | Measure exactly these paths. |
| `--max-chars` | `80` | Cap in characters. |
| `--advisory` | off | Report the offenders without failing. |
| `--json` | off | One JSON object instead of the report. |
| `--verbose` | off | Print the table even when clean. |

The run is strict by default: exit 1 when any wrap-able measured line is over
the cap. Offenders print as `file:line: [N chars] first 80 chars`, capped at
20 lines with a `... N more` tail. `--advisory` reports the same list and
exits 0, which is how the gate was adopted before the reflow finished.

An **unbreakable** line is an over-cap line carrying a whitespace-delimited
token wider than the cap — a long URL or bare link. No whitespace wrap can
bring that token under the cap, so the line is not an offender: it never fails
the run, it is counted separately in `totals['unbreakable']`, and it prints as
`unbreakable: U ...`. A line of ordinary words is always an offender — every
token fits the cap, so a wrap fixes it, and the exemption cannot hide it.

## Verification

```
$ python3 scripts/audit-chars.py > /dev/null
$ echo "exit=$?"
exit=0

$ python3 scripts/audit-chars.py | grep -E 'lines over|unbreakable'
lines over 80 chars: 0/1237 = 0.0%
unbreakable: 1 (token wider than 80)
```

Measured totals:

```
$ python3 scripts/audit-chars.py --json | python3 -c \
    'import json,sys; print(json.load(sys.stdin)["totals"])'
{'files': 21, 'lines': 1237, 'over': 0, 'worst': 105, 'unbreakable': 1}
```

The single unbreakable line is `README.md:32`, a 105-character line whose
`[llm-wiki spec](...)` label carries a 95-character URL token that no wrap can
shorten. The gate's own tests, on their own:

```
$ python3 -m pytest tests/unit/test_audit_chars.py -q
6 passed
```

## What Works

- The repo is 80-column clean: 0 of 1237 measured lines are over the cap, so
  the default run exits 0 and the gate holds on every push.
- The gate enforces rather than advises: a wrap-able over-cap line exits 1,
  and the `unit` job's `Machine gates` step runs the script directly, so the
  failure no longer depends on pytest being the thing that notices.
- The unbreakable exemption is narrow and pinned by `AC-CHARS-006`: a line
  carrying a token wider than the cap passes and is counted apart, while a
  120-character line of ordinary short words still fails.
- Fences, tables and headings are exempt by construction — a 120-character
  table row or fenced URL does not count, verified by `AC-CHARS-002`.
- Non-markdown input is measured raw: a 100-character source line is reported
  at its full width, verified by `AC-CHARS-004`.
- Reported paths are repo-relative; the absolute root never leaks into output.
- `--json` carries `advisory` and `totals.unbreakable` beside the per-file
  table, so a dashboard can separate real offenders from bare links.

## What Fails

- **Over-wide tokens are exempt by design.** A 300-character URL anywhere on
  a line passes, and the gate cannot tell it from a link that should have been
  a reference.
- **Tables, headings and fences are exempt by construction.** A 400-character
  table row or heading is invisible to the measure, so width discipline there
  is editorial, not enforced.
- **Non-markdown source is only measured when named explicitly.** The default
  scope is docs prose plus the two entry documents, so a `.py` or `.yml` line
  is unchecked until someone passes the path.

## Resolution

- **Over-wide-token exemption:** accept it — no wrap can shorten a token wider
  than the cap — and keep the escape structural: the line is exempt only
  because of that token, as `AC-CHARS-006` asserts; a line whose tokens all
  fit the cap still fails.
- **Structural exemptions:** leave them. A table's width is set by its
  columns and a fenced block is code that reflow would break; check wide
  tables and headings by eye at review time.
- **Source not in the default scope:** name the file when it matters —
  `python3 scripts/audit-chars.py scripts/gen-env.py` — and keep the default
  scope on prose, which is what the cap exists for.

## Verdict

`works` — the repo is 80-column clean, the gate fails rather than warns, a
bare over-wide link is counted apart instead of failing, and every behaviour
is pinned by a test; the gaps above are exemptions held open on purpose.
