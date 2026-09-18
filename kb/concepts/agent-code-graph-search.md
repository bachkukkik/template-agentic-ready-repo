---
title: Agent code-graph search
created: 2026-09-16
updated: 2026-09-16
type: concept
tags: [integration, architecture]
sources: [raw/articles/codegraph-mcp-code-intelligence.md]
confidence: high
---

# Agent code-graph search

The job: let a coding agent answer structural questions ("how does X reach Y?",
"what breaks if I change Z?", "which tests are affected?") in a few fast tool
calls instead of many Read/Grep turns. The 2026 tool set splits along two axes:

- **Surface** — MCP-native (agent tool calls; e.g. [[codegraph]]) vs
  skill/CLI-first (agent invokes slash commands or CLI; MCP is an add-on; e.g.
  graphify).
- **Artifact scope** — code-only structural graphs vs knowledge graphs that also
  index docs/SQL schemas/PDFs.

## What a good implementation must provide

- **Deterministic extraction** (AST, not LLM summarization) — the graph must be
  auditable and stable across runs.
- **Sufficient output** — each answer complete enough that the agent *stops*
  reading files; that is the mechanism behind published token/call savings, not
  cache-ability.
- **Live sync** — index tracks the working tree (file watcher + on-demand
  `sync`), so it does not go stale mid-session.
- **Impact analysis** — callers/callees/impact plus changed-file → affected-test
  tracing, CI-ready via `--stdin` patterns.
- **Graceful degradation** — tools stay available pre-index with success-shaped
  guidance (never error-shaped), so sessions can start before `init`.
- **Local-first + privacy** — index never leaves the machine; telemetry
  anonymous and opt-out.

## Known limits of the class

- Static analysis cannot see dynamic dispatch (reactive/reconciler runtimes); a
  good tool is silent, not wrong — partial bridging is worse than none.
- Per-repo indexes are local artifacts unless the tool emits a stable committable
  file (e.g. graphify's `graph.json` vs codegraph's gitignored `.codegraph/`).

## Related

- [[codegraph]] — the primary implementation adopted in this repo
- [[codegraph-vs-graphify]] — the incumbent and the coexistence verdict
