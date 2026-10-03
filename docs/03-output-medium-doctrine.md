# 03 — Output-Medium Doctrine

## What

The output-medium doctrine is the standing order that an agent consume or produce any explanatory output at the richest useful rung of a five-medium ladder — prose → STE-style controlled English → diagram → HTML page → explainer video — with every rung authored as code/text, rendered by a deterministic program, and verified by render → parse rather than by looking.

## Why

- Explanatory output defaults to prose, but a richer medium carries the reader's understanding better; the trade is build cost, and the doctrine makes the rung a per-task choice rather than a default.
- The upper rungs are only usable to a non-visual engine if each rung is code/text a program renders and a program parses. Absent that constraint, "did it render?" is unanswerable to the agent that produced it.
- The doctrine spans three funnel layers — the instruction file, stage-2 raw knowledge, stage-3 confirmed knowledge — so a drift in any one layer is invisible without a tripwire at each.
- The standing order is added to `AGENTS.md`, which every harness auto-loads under a 20,000-character cap, so it must stay pointer-based: one line per rule plus a pointer to the detail.

## How

### The ladder

Each rung is richer than the one below it. Escalation is per-task; the rung is chosen by what the reader must extract.

| # | Rung | Grounding |
|---|------|-----------|
| 1 | Prose | the source's default medium |
| 2 | Controlled English (ASD-STE100-style) | the source; limits are procedural sentence ≤ 20 words, descriptive ≤ 25, noun cluster ≤ 3 |
| 3 | Diagram / image | the source — "easier to process, parse, and understand" |
| 4 | HTML web page | the source — interactive, frontend skill |
| 5 | Explainer video | the source — the format the author is "most bullish on" |

### Where the doctrine lives

| Funnel stage | Path | Role |
|---|---|---|
| 6 — instruction file | `AGENTS.md` § *7. Output-Medium Escalation* | the pointer-based standing order |
| 4 — intent | `docs/prd/03-output-medium-doctrine.md` | SC-om-1..4, test mapping, CI gate |
| 2 — raw knowledge | `kb/raw/articles/karpathy-output-medium-escalation.md` | verbatim source post + ASD-STE100 sheet, body sha256 recorded |
| 3 — confirmed knowledge | `kb/concepts/output-medium-escalation.md` | ladder, meta-thesis, code-first constraint, the six principles |
| guard | `tests/unit/test_output_medium_doctrine.py` | the AC-OM-0NN tripwires |

### The standing order

`AGENTS.md` carries the order as Standing Order 7, anchored by the exact heading `### 7. Output-Medium Escalation`:

> For any explanatory output, consume the richest useful rung: prose → STE-style controlled English → diagram → HTML page → explainer video — all code-first, verified by render → parse (never by looking; works with non-visual engines). Large custom artifacts are **discardable**: build them in `scratchpads/`, never cite them (funnel rule 6). Skills per project (host-level): `simple-english`, `diagrams`, `render-verify`, `explainer-video`. → `docs/prd/03-output-medium-doctrine.md`; `kb/concepts/output-medium-escalation.md`

### Code-first render → parse

The load-bearing constraint — that every rung is code/text verified by parse, never by looking — is this repo's reading, not a claim in the source post (`[ASSUMPTION]`, PRD *Assumptions*). It is the same deterministic-extraction move the repo applies elsewhere: the model authors an artifact, and a program — not the model's eyes — decides whether it is correct. SVG/DOM structure, pixel buffers and `ffprobe` are the parse targets that make the ladder usable to a non-visual engine.

### The tripwires

| ID | Asserts |
|----|---------|
| AC-CTX-001 | `AGENTS.md` is under the 20,000-character context-file cap |
| AC-OM-001 | the `### 7. Output-Medium Escalation` heading exists and its body names every ladder rung, the `render → parse` rule, the `discardable` rule and the funnel-rule-6 pointer |
| AC-OM-002 | the raw source body's sha256 equals its frontmatter `sha256` |
| AC-OM-003 | the concept page cites the raw source and is indexed in `kb/index.md` under both Concepts and Raw Sources |

All four are unit-tier (a file read and the stdlib only — no subprocess, no transport), so they run in the `unit` CI job.

## Verification

```bash
# The doctrine's three tripwires plus the cap guard — unit tier only.
pytest tests/unit -q
# -> 7 passed

# The tiers the default runner exercises (unit + integration; e2e skipped without --with-e2e)
bash tests/run.sh
# -> 7 passed / 3 passed / e2e SKIPPED / RESULT: PASSED

# The cap guard's number. Characters, not bytes — see AC-CTX-001.
LC_ALL=C.UTF-8 wc -m AGENTS.md
# -> 19723 AGENTS.md

# The standing-order anchor the tripwire keys on
grep -n '^### 7\. Output-Medium Escalation' AGENTS.md
# -> 253:### 7. Output-Medium Escalation

# The raw source integrity: body sha256 must equal the frontmatter value
python3 - <<'PY'
import hashlib
from pathlib import Path
p = Path("kb/raw/articles/karpathy-output-medium-escalation.md")
t = p.read_text(encoding="utf-8")
body = t[t.index("\n---", 3) + 4:].lstrip("\n")
print(hashlib.sha256(body.encode("utf-8")).hexdigest())
PY
# -> 21961aa850036fc5ca5003bdd655b6cf7a9f5d004ce6f0c51bb29ab686b0785c

# The full ladder, E2E included — needs the container up first.
docker compose up -d --build
bash tests/run.sh --with-e2e
```

Expected: `7 passed`; `RESULT: PASSED` with the e2e tier skipped by default; `19723`; the heading line; the hash matching the frontmatter `sha256`.

## What Works

- `bash tests/run.sh --with-e2e` starts the compose stack itself when it is down and then runs the tier green (verified: `docker compose stop service` → `--with-e2e` → `RESULT: PASSED`)
- `act push -j secret-scan` and `act push -j unit` verified green under real act on this host — the act-level job graph and runner image are exercised
- All six Karpathy principles are grounded: `karpathy-guidelines` is ingested at `kb/raw/articles/karpathy-guidelines-skill.md` (sha256 round-trip verified) and synthesized at `kb/concepts/karpathy-coding-guidelines.md`; `kb/concepts/output-medium-escalation.md` is `confidence: high` with no remaining `[ASSUMPTION]` on the principles

- `AGENTS.md` carries the `### 7. Output-Medium Escalation` standing order, and its body names all five rungs, the `render → parse` rule, the `discardable` rule and the `(funnel rule 6)` pointer — AC-OM-001 passes.
- `AGENTS.md` is 19,723 characters against the 20,000-character cap (277 characters of headroom), so the added order does not truncate the file — AC-CTX-001 passes.
- The raw source body's sha256 (`21961aa8…`) equals its frontmatter `sha256`, so the stage-2 provenance is intact and unedited since ingest — AC-OM-002 passes.
- The concept page exists, cites `raw/articles/karpathy-output-medium-escalation.md` in its `sources:` frontmatter, and appears in `kb/index.md` under both Concepts and Raw Sources — AC-OM-003 passes.
- The full default suite is green: 7 unit tests + 3 integration tests, `RESULT: PASSED`.
- All four harness entry-point symlinks resolve (`CLAUDE.md`, `.github/copilot-instructions.md`, `.claude/skills`, `.claude/plugins`), and the secret-scan grep over tracked `.md` files is clean.

## What Fails

- **AC-OM-001 is a token tripwire, not a semantic one:** it asserts the literal tokens `prose`, `diagram`, `html`, `explainer video`, `controlled English`/`ASD-STE100`, `render → parse`, `discardable` and `funnel rule 6`. A §7 rewrite that preserves the rule's meaning but changes its wording turns red. This is a design property — a tripwire must fire on the wording it anchors — recorded here so reviewers do not mistake it for a defect.

## Resolution

- **AC-OM-001 is a token tripwire, not a semantic one:** when rewriting §7, keep the literal tokens AC-OM-001 names, or update the test in the same change — the tripwire is the contract between the standing order and the review gate, so the two move together.

## Verdict

**works** — The doctrine verifies end to end across all three layers it spans: the §7 standing order ships inside the 20,000-character cap with a 581-char headroom above the AC-CTX-003 floor, the raw sources' sha256 round-trips match, the concept page is indexed at `confidence: high` with every principle grounded in a raw ingest, the unit tripwires (AC-OM-001/002/003, AC-CTX-001/002/003) are green, the e2e tier self-starts its stack, and the act jobs run green under real act. The one recorded non-defect is the token-level anchoring of AC-OM-001 — a tripwire property, not a gap.
