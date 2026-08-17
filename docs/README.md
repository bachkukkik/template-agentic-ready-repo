# docs/ — Empirical Status Index

> Funnel stage 6 catalog (see *Document Funnel* in `AGENTS.md`). One row per
> `docs/NN-slug.md`. **Maintained via the `coding-agents-docs-guideline` skill** —
> the same skill invocation that writes or updates a doc updates its row here.
>
> Scope: this file indexes the **empirical layer only**.
> - Intent (`docs/prd/`) is indexed by [PRD.md](../PRD.md#quick-reference) — do not duplicate it here.
> - Gaps (`docs/gaps/`) are transient and self-listing — see [docs/gaps/README.md](gaps/README.md).
> - Knowledge (`kb/`) has its own llm-wiki catalog — see [kb/index.md](../kb/index.md).

## Status Docs

| # | Topic | Verdict | Updated | Covers | PRD | Gaps |
|---|-------|---------|---------|--------|-----|------|
| 01 | [Service Architecture](01-service-architecture.md) | partial | 2026-08-03 | `service/`, `docker-compose.yml`, `tests/` | [01-example-topic](prd/01-example-topic.md) | — |

`01` is `partial`, not `works`: its *What Fails* lists cold-start latency, no host port
binding, and `tests/integration/example.test.ts` being a no-op stub.

**Verdict vocabulary** — copy the net verdict from the doc's own *Verdict* section:

| Verdict | Meaning |
|---------|---------|
| `works` | Verified end to end; no known failures |
| `partial` | Some paths verified, some fail — *What Fails* section is non-empty |
| `broken` | Primary path fails; do not build on it until resolved |
| `stale` | Last verification predates a change to the code it covers — re-verify before citing |

## Rules

1. **Every `docs/NN-*.md` has exactly one row.** A doc with no row is invisible to the
   next agent; a row with no doc is a lie. Both are defects.
2. **`NN` is unique and shared across the funnel.** `docs/NN-slug.md`,
   `docs/prd/NN-*.md`, and `docs/gaps/NN-*.md` reuse the same number for the same
   topic, so an agent can walk intent → gap → reality by number alone.
3. **`Updated` is the last *verification* date**, not the last text edit. Editing prose
   does not refresh it; re-running the verification commands does.
4. **A `stale` or `broken` verdict is a required read** before touching the code it
   covers — that is the point of this file.
