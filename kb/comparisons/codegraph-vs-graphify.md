---
title: CodeGraph vs graphify
created: 2026-09-16
updated: 2026-09-16
type: comparison
tags: [decision, integration]
sources: [raw/articles/codegraph-mcp-code-intelligence.md]
confidence: high
---

# CodeGraph vs graphify

Why: the template needed a **primary graph search for coding agents**. graphify
was the incumbent (`## graphify` section in AGENTS.md); [[codegraph]] was the
challenger (research of 2026-09-16, see
`raw/articles/codegraph-mcp-code-intelligence.md`).

## Comparison (2026-09-16)

| Dimension | [[codegraph]] | graphify |
|---|---|---|
| Primary surface | MCP (8 tools) + 11 installer targets | `/graphify` skill + CLI; MCP is an opt-in `[mcp]` extra (`python -m graphify.serve`) |
| Artifact scope | code (30+ languages) | code + docs + SQL schemas + configs + PDFs |
| Index | `.codegraph/` SQLite — local, gitignored | `graphify-out/graph.json` — committable |
| Sync | native file watcher, live | `graphify update .` after changes |
| Impact analysis | callers/callees/impact/affected-tests (`--stdin`) | — (query/path/explain/triage) |
| Edge metadata | `provenance: 'heuristic'` on synthesized edges | confidence score (inferred vs certain) per edge |
| Framework routes | yes (Express/Next.js/Rails/FastAPI/Django/Spring/Gin/…) | — |
| Runtime | Node (bundled; engines ≥20 <25) | Python (uv/pipx, `graphifyy`) |

## Verdict (this repo)

**Coexist.** [[codegraph]] = primary agent graph search for code structure —
it is the only tool in the set that is agent-wired (installer per harness),
live (watcher), and impact-aware (affected-test tracing), which is exactly the
job coding agents do. graphify = optional knowledge graph for non-code
artifacts (docs/SQL/PDFs) and the committable-graph-file niche. Both are
local-first, deterministic, AST-based — they do not compete for the same job.
Recorded in the `## codegraph` section of `AGENTS.md`, with graphify demoted to
the optional `### graphify` subsection (still conditional on
`graphify-out/graph.json`).

**Caveats.** codegraph is young (repo created 2026-01-18; 46 releases) with a
single primary maintainer, and its benchmarks are vendor-run (Claude-Code arm).
graphify's CLI was broken on this host at research time (root-owned uv shim →
Permission denied) — a data point on runtime fragility, not on design.

## Related

- [[codegraph]] · [[agent-code-graph-search]]
