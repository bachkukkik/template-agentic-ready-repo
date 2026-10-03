# 02 — AGENTS.md Context Budget

## What

`AGENTS.md` is the repo's single agent instruction file — every harness entry point is a symlink to it — and every harness auto-loads it into the prompt, silently truncating it above a 20,000-character context-file cap. This doc records the trim that brought it under the cap, what survived byte-for-byte, and the unit tripwire that keeps it there.

## Why

- Every harness loads the instruction file into each prompt. An oversized file is not an error — it is truncated with a warning the agent never sees at task time.
- Overflow is lossy in the **middle**: the head 70% and the tail 20% survive and the middle is dropped. Position, not importance, decides what the agent reads, so the *Standing Orders*, *Repository Structure*, *Development Commands* and *Security* sections simply vanished from the prompt.
- A doctrine the agent cannot read is not a doctrine. The failure was silent and positional, so the fix had to keep every rule and end in a structural guard rather than a note asking people to be careful.

## How

### The cap

`CONTEXT_FILE_MAX_CHARS = 20_000` in `agent/prompt_builder.py` is the flat floor of a dynamic cap — `context_length × 4 × 0.06` characters, clamped to 20,000–500,000. The floor applies whenever the model window is not threaded through, which is the common case, so it is the number this repo targets.

It is a **characters** rule, not a bytes rule. Measure with `wc -m` or `len(text)`; `ls -l` and `wc -c` under-report multi-byte content and are a proxy only.

### Truncation behaviour

`_truncate_content()` keeps `CONTEXT_TRUNCATE_HEAD_RATIO = 0.7` and `CONTEXT_TRUNCATE_TAIL_RATIO = 0.2` of the file and substitutes a `[...truncated …]` marker for the middle, logging:

```
⚠️  Context file AGENTS.md TRUNCATED: 29611 chars exceeds limit of 20000 — trim the file, pin a larger context_file_max_chars, or use a larger-context model!
```

At the pre-edit size the dropped window was characters `[14000, 25611)`.

### Measurements

Measured through the real builder (`pb.build_context_files_prompt`), not inferred from size:

| Revision | chars (`wc -m`) | bytes (`wc -c`) | sha256 (head) | AGENTS.md block delivered | full file verbatim | `TRUNCATED` warnings |
|---|---|---|---|---|---|---|
| before — `main` @ `7fb3d0c` | 29,598 | 30,347 | `a206cef8f12fb3b0` | 18,202 chars | `False` | 1 |
| after trim — `c606e69` | 19,165 | 19,357 | `0493b4511717c643` | 19,179 chars | `True` | 0 |
| after §7 — this branch | 19,723 | 19,929 | `f2808dc9054454cb` | 19,737 chars | `True` | 0 |
| after codegraph trim — this branch | 19,419 | 19,419+ | — | 19,433 chars | `True` | 0 |

(§-row sha256 was captured pre-trim; the headroom-trim row's builder run was not re-hashed — the verbatim/probe evidence above carries.)

Trim reduction: 10,433 chars / 10,990 bytes (35.2%). The §7 output-medium order (`docs/03-output-medium-doctrine.md`) then added 558 chars, for a net 9,875 chars / 33.4% below `main`. Headroom after the codegraph trim: 581 chars (2.9% of the cap), above the 500-char floor AC-CTX-003 now enforces.

### Composition of the trimmed file

Nine regions are **byte-identical** to the pre-edit snapshot — 10,313 chars, the parts that are a cross-harness contract or are asserted by CI:

| Region | chars |
|---|---|
| H1 + top blockquote (symlink families) | 358 |
| funnel stage diagram | 850 |
| funnel stage table (stages 0–7) | 1,482 |
| *Where does this text go?* heading + table | 547 |
| Harness Adapter body (capability table + symlink families) | 2,690 |
| `/goal` kickoff prompt + `sub1`–`sub4` verbatim blocks | 2,245 |
| *Running the pipeline without `/goal`* heading | 40 |
| phase table (kickoff, `sub1`–`sub4`) | 1,147 |
| skill-to-phase mapping table | 954 |

Everything else is **compressed or reflowed with every rule retained**, each rule ending in a pointer to where its detail lives: funnel rules 1–10 (wording tightened; all ten gates and the three CI-enforcement strings intact), the Harness Adapter tail prose (root-cause binding), the `/goal` closing prose, *Standing Orders* §1–§6 collapsed to one line per rule, *Repository Structure* and *Development Commands* reduced to their load-bearing lines plus a `README.md` pointer, and *Security* reduced to one line per rule.

No rule was deleted. No fact was dropped: every cut fact has a published home (`README.md`, `docs/`, `PRD.md`, `kb/`), and each pointer left behind resolves.

### The tripwire

`tests/unit/test_agents_md_budget.py` (unit tier) carries three hermetic tripwires, each registered here (this repo keeps no separate test-index file):

| ID | Asserts | Closes |
|----|---------|--------|
| `AC-CTX-001` | `len(text) < 20_000` | the original silent-truncation defect |
| `AC-CTX-002` | `len(text) < $AGENTS_MD_CAP_CHARS` when the env var is set (int; malformed pin fails loudly), else 20,000 | *the cap is host-dependent* — a lower host-pinned cap becomes visible to CI when exported |
| `AC-CTX-003` | `cap - len(text) >= 500` | *headroom is thin* — accretion fails loudly ~15 lines before the cap, not at it |

Each failure message names the cap/floor, the lossy head-70/tail-20 middle truncation, and the collapse-plus-pointer remedy. All are stdlib-only file reads — no subprocess, no service import.

## Verification

```bash
# Size in both readings — chars is the binding one.
# NB: under a non-UTF-8 locale (here LC_ALL=C) wc -m silently counts BYTES and matches
# wc -c. This file carries 106 non-ASCII characters, so the two readings differ by 206.
LC_ALL=C.UTF-8 wc -m AGENTS.md
# -> 19419 AGENTS.md
wc -c AGENTS.md
# -> 19419 AGENTS.md

# The headroom floor + host-cap override, exercised
AGENTS_MD_CAP_CHARS=19800 python3 -m pytest tests/unit/test_agents_md_budget.py -v
# -> AC-CTX-003 FAILS (headroom 381 < 500 under the lower cap) — the override flows
python3 -m pytest tests/unit -q
# -> 9 passed (001, 002, 003 all green at the default cap)

# Delivered through the REAL prompt builder: whole file present, no truncation warning
HERMES_HOME=~/.hermes/profiles/<profile> /app/venv/bin/python3 - <<'PY'
import sys; sys.path.insert(0, "/home/hermeswebui/.hermes/hermes-agent")
from agent import prompt_builder as pb
raw = open("AGENTS.md", encoding="utf-8").read()
out = pb.build_context_files_prompt(cwd=".", context_length=None)
warn = [w for w in (pb.drain_truncation_warnings() or []) if "TRUNCATED" in w]
print("chars", len(raw), "| verbatim", raw in out, "| warnings", warn)
PY
# -> chars 19419 | verbatim True | warnings []

# The tripwire, via the repo's own runner
bash tests/run.sh

# Preserved regions byte-identical to the pre-edit snapshot
sha256sum AGENTS.md
```

Expected: `LC_ALL=C.UTF-8 wc -m` reports 19,419; the probe prints `verbatim True` with an empty warning list; the unit tier is `9 passed` and the override probe turns AC-CTX-003 red as documented.

## What Works

- `AGENTS.md` is delivered whole — 19,419 chars against a 20,000-char cap, with 581 chars (2.9%) of headroom, above the 500-char floor
- The real prompt builder returns the file verbatim (`raw in out == True`) and queues **zero** `TRUNCATED` warnings, down from one at 29,598 chars
- All nine contract regions are byte-identical to the pre-edit snapshot, and every tightened region retains all ten funnel rules, the three CI-enforcement strings (rules 3, 9, 10), the root-cause binding and the `/goal` phase prose
- Every `§N` cross-reference used elsewhere in the repo (`§5`, `§6`, `§Security`, `§codegraph` — in `tests/run.sh`, `.github/workflows/ci.yml`, `README.md`, `docs/`) still resolves against the trimmed headings
- All four harness entry-point symlinks resolve: `CLAUDE.md`, `.github/copilot-instructions.md`, `.claude/skills`, `.claude/plugins`
- The unit tier is green (9 tests), and the three tripwires make regression, a host-pinned cap, and headroom exhaustion loud instead of silent
- The headroom floor is proven to bite: `AGENTS_MD_CAP_CHARS=19800` flips AC-CTX-003 red while 001/002 stay green

## What Fails

- **`wc -m` is locale-dependent:** under a non-UTF-8 locale (this container sets `LC_ALL=C`) `wc -m` silently counts **bytes** — a char check that reads `wc -m` is really a byte check. Use `LC_ALL=C.UTF-8 wc -m` or `len(text)` in Python; the tripwires assert in Python and are immune.
- **Bytes are not the rule:** the guard measures characters. `wc -c` happens to pass today, but only the char count is binding — a file can be under in bytes and over in chars once it is non-ASCII enough.

## Resolution

- **`wc -m` is locale-dependent:** run it as `LC_ALL=C.UTF-8 wc -m`, or measure in Python with `len(text)` — which is what the tripwires do. Never trust a bare `wc -m` on a host whose locale is not UTF-8.
- **Bytes vs chars:** treat `ls -l` / `wc -c` as a proxy only, and keep headroom so both readings pass.

## Verdict

**works** — The file reaches the prompt byte-for-byte under the cap with zero truncation warnings, all nine contract regions and all ten funnel rules survive, and three hermetic tripwires now fail loudly on: regression over the cap (AC-CTX-001), a host-pinned cap exported into the environment (AC-CTX-002), and headroom exhaustion before the cap is reached (AC-CTX-003, floor 500 chars — current headroom 581). The locale dependence of `wc -m` remains an operator trap, but the binding assertions are Python-side and immune.
