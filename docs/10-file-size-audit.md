# 10 — File-Size Audit

## What

`scripts/audit-size.py` measures every git-tracked regular file and fails when
one exceeds a per-file byte cap, 20 KB by default.

## Why

A file that grows without a ceiling stops being reviewable: reviewers skip it,
context windows truncate it, and an agent asked to edit it pays for the bytes
it does not need. Before this gate the repo had no size ceiling at all — the
largest tracked file sat at 19830 bytes because nobody had written a 200 KB
one yet, not because a rule prevented it.

## How

Flags:

| Flag | Default | Effect |
|------|---------|--------|
| `FILE...` | tracked scope | Measure exactly these paths. |
| `--max-kb` | `20.0` | Cap = `int(max_kb * 1024)` bytes. |
| `--json` | off | One JSON object instead of the report. |
| `--verbose` | off | Print the table even when clean. |

Scope and boundaries:

| Rule | Behaviour |
|------|-----------|
| Default scope | regular files in `git ls-files` (87 of 91 entries) |
| Skipped | 4 symlinks/gitlinks: `CLAUDE.md`, copilot instructions, 2 dirs |
| Not in scope | untracked files never fail the gate |
| Non-git tree | falls back to a recursive walk, same skip rules |
| Cap | inclusive: 20480 passes, 20481 fails |
| Default mode | strict — exit 1 on any over-cap file |
| Unreadable file | warning on stderr, counted as 0 bytes, never raised |

The four skipped entries are `CLAUDE.md`, `.github/copilot-instructions.md`,
`.claude/skills` and `.claude/plugins`. Each is a link; a link's own size says
nothing about the file it points at, and the target is already in scope under
its real path.

## Verification

```
$ python3 scripts/audit-size.py | grep largest
largest: 19830 bytes  kb/raw/articles/quality-controls-audit-dossier.md
$ python3 scripts/audit-size.py > /dev/null; echo "exit=$?"
exit=0
```

Boundary check on a throwaway file at the repo root, removed afterwards:

```
$ head -c 20481 /dev/zero | tr '\0' x > over-probe.txt
$ python3 scripts/audit-size.py over-probe.txt | sed "s|$PWD/||" | tail -4
cap: 20480 bytes  files: 1  over: 1
Over cap (20480 bytes):
over-probe.txt: [20481 bytes] over cap 20480
largest: 20481 bytes  over-probe.txt
$ python3 scripts/audit-size.py over-probe.txt > /dev/null
$ echo "exit=$?"
exit=1
$ rm over-probe.txt
```

The gate test, on its own:

```
$ python3 -m pytest tests/unit/test_audit_size.py -q
5 passed
```

## What Works

- The shipped tree passes: 87 tracked files, none over the cap.
- The cap is inclusive and exact — 20480 bytes passes, 20481 fails, both
  asserted by `AC-SIZE-002` against files built in `tmp_path`.
- Untracked files cannot fail the gate, because the scope is `git ls-files`
  and not a walk.
- Explicit positional paths replace the scope, so a unit test can measure a
  synthetic oversize file without writing inside the repo.

## What Fails

- **The largest file sits 650 bytes under the cap.**
  `kb/raw/articles/quality-controls-audit-dossier.md` is 19830 bytes of a
  20480-byte budget, so an ingest adding more than 650 bytes fails the gate.
- **A tracked symlink's target is invisible.** The four skipped entries are
  measured nowhere: a link to a 2 MB file passes, because the link is not a
  regular file and the target is outside the tracked set.

## Resolution

- **650 bytes of headroom:** keep one raw source per file — split the dossier
  into its constituent ingests rather than growing it, archive superseded
  sections to `kb/_archive/` (funnel rule 5), and confirm with
  `python3 scripts/audit-size.py --verbose` before the commit that adds the
  ingest.
- **Symlink target invisible:** measure the target explicitly by path
  (`python3 scripts/audit-size.py <target>`) when a tracked link points at
  content the gate must hold; do not widen the default scope, because a link
  is a pointer and its target may legitimately live outside the repo.

## Verdict

`works` — the gate is strict, its scope is tracked-only and exact, and the
boundary arithmetic is pinned by tests; its one live risk is the 650 bytes of
headroom under the dossier, which the next ingest can spend.
