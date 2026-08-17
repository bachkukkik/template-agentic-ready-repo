# docs/gaps — Gap Observations

Funnel stage 5 (see *Document Funnel* in `AGENTS.md`). A gap doc records **one
observed divergence** between two adjacent funnel stages. It is transient: it exists
to be closed.

Two kinds, and only two:

| Kind | Divergence | Typical cause |
|------|-----------|---------------|
| `kb ↔ prd` | The PRD asserts something the KB does not support, or the KB holds knowledge no PRD acts on | PRD written ahead of the knowledge, or stale intent |
| `prd ↔ code` | The codebase does not do what the PRD says, or does something no PRD asked for | drift, undocumented work, abandoned intent |

Divergence between *PRD* and *observed runtime behaviour* is not a gap doc — that is
stage 6, `docs/NN-slug.md`, authored via `coding-agents-docs-guideline`.

## Naming

```
docs/gaps/NN-slug.md      # NN = zero-padded sequence, matching docs/ and docs/prd/
```

## Required sections

```markdown
# NN — <short gap title>

**Layers:** kb ↔ prd | prd ↔ code
**Status:** open | resolved
**Opened:** YYYY-MM-DD

## Observation

What each side says, with paths and line refs for both. No interpretation.

| Side | Source | Claim |
|------|--------|-------|
| A | `kb/concepts/x.md` | ... |
| B | `docs/prd/01-topic.md:42` | ... |

## Evidence

The commands run and their output. A gap with no evidence is a hunch — it belongs in
`scratchpads/`.

## Impact

Who or what breaks if this stays open. If nothing does, close it as `wontfix`.

## Resolution

Exactly one of:

- `kb/raw/` ingest + `/llm-wiki ./kb/` — the knowledge was missing
- PRD edit — the intent was wrong or stale
- Code change + test — the code was wrong (route through the coding pipeline)
- GitHub issue #N — real, but not now

State which, link it, then flip **Status** to `resolved`.
```

## Lifecycle

```
sub1 gap sync  ──►  docs/gaps/NN-slug.md (open)
                          │
                          ▼
              resolution applied upstream
                          │
                          ▼
              Status: resolved  ──►  archived out of the repo once merged
```

Rules:

1. **One gap per file.** Two divergences = two files.
2. **No open gap survives a merge to `main` without a Resolution section.** An
   unresolvable gap becomes a GitHub issue and the file is closed pointing at it.
3. **Gaps never carry fixes.** They observe; upstream stages change.
