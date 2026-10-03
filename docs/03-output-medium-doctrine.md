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

- `AGENTS.md` carries the `### 7. Output-Medium Escalation` standing order, and its body names all five rungs, the `render → parse` rule, the `discardable` rule and the `(funnel rule 6)` pointer — AC-OM-001 passes.
- `AGENTS.md` is 19,723 characters against the 20,000-character cap (277 characters of headroom), so the added order does not truncate the file — AC-CTX-001 passes.
- The raw source body's sha256 (`21961aa8…`) equals its frontmatter `sha256`, so the stage-2 provenance is intact and unedited since ingest — AC-OM-002 passes.
- The concept page exists, cites `raw/articles/karpathy-output-medium-escalation.md` in its `sources:` frontmatter, and appears in `kb/index.md` under both Concepts and Raw Sources — AC-OM-003 passes.
- The full default suite is green: 7 unit tests + 3 integration tests, `RESULT: PASSED`.
- All four harness entry-point symlinks resolve (`CLAUDE.md`, `.github/copilot-instructions.md`, `.claude/skills`, `.claude/plugins`), and the secret-scan grep over tracked `.md` files is clean.

## What Fails

- **E2E tier needs the running stack:** `bash tests/run.sh` with no flag reports the e2e tier as `SKIPPED (needs a running service)`, and `bash tests/run.sh --with-e2e` against a stack that is not up fails with `service "service" is not running` — the bats E2E cases reach the container only through `docker compose exec`.
- **CI jobs are verified by command, not under `act`:** the four CI jobs were exercised by running their commands directly — `pytest`, the secret-scan grep, and the symlink / tracked-path checks — rather than through `act`. `act -l` parses `ci.yml` and lists every job, but no runner image is cached on this host, so the act-level job graph and runner image were not exercised.
- **AC-OM-001 is a token tripwire, not a semantic one:** it asserts the literal tokens `prose`, `diagram`, `html`, `explainer video`, `controlled English`/`ASD-STE100`, `render → parse`, `discardable` and `funnel rule 6`. A §7 rewrite that preserves the rule's meaning but changes its wording turns red.
- **The concept page is single-sourced and partly assumption:** `kb/concepts/output-medium-escalation.md` carries `confidence: medium`, and the four older Karpathy principles it lists (Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution) are `[ASSUMPTION]` — no raw ingest for them exists in this repo.

## Resolution

- **E2E tier needs the running stack:** start the service first and wait for health, then run the tier — `docker compose up -d --build && bash tests/run.sh --with-e2e`. The default invocation deliberately skips it so a routine run needs no container.
- **CI jobs are verified by command, not under `act`:** run `act push -j unit -j integration -j secret-scan -j doctrine` on a host with a cached runner image and not serving this compose project (never `-j e2e` — see AGENTS.md §6). Until that run exists, treat the direct-command runs as the evidence for those four jobs.
- **AC-OM-001 is a token tripwire, not a semantic one:** when rewriting §7, keep the literal tokens AC-OM-001 names, or update the test in the same change — the tripwire is the contract between the standing order and the review gate, so the two move together.
- **The concept page is single-sourced and partly assumption:** it stays `confidence: medium` and the four principles stay `[ASSUMPTION]` until a `kb/raw/` ingest backs them; promotion is a `kb/raw/` add plus a `llm-wiki ./kb/` regeneration.

## Verdict

**partial** — The doctrine verifies end to end across all three layers it spans: the §7 standing order ships inside the 20,000-character cap, the raw source's sha256 matches its frontmatter, the concept page is indexed, and the seven unit tests — three of them the doctrine's own tripwires — are green. The open limits are that the E2E tier depends on the compose stack being up, the four CI jobs were verified by their commands rather than under `act`, AC-OM-001 asserts tokens not meaning, and the supporting knowledge remains single-sourced and assumption-flagged.
