---
title: CodeGraph
created: 2026-09-16
updated: 2026-09-16
type: entity
tags: [integration]
sources: [raw/articles/codegraph-mcp-code-intelligence.md]
confidence: high
---

# CodeGraph

[colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) — local-first
code-intelligence CLI + MCP server; the primary graph search for coding agents in
this repo. Deterministic tree-sitter → SQLite (WAL + FTS5) symbol/edge graph. MIT,
30+ languages, 11 agent installer targets (hermes, opencode, claude, cursor, codex,
gemini, antigravity, kiro, copilot vscode/cli/jetbrains).

## Key facts (v1.6.0, as of 2026-09-16)

- MCP surface: **one tool by design** — `codegraph_explore` (symbol-bag query →
  call path + relevant source + blast-radius summary in one call). Upstream: one
  strong tool steers agents better than a menu of narrow ones. The other 7
  (node/search/callers/callees/impact/files/status) stay functional but are
  **unlisted by default** — CLI twins, or re-enable via `CODEGRAPH_MCP_TOOLS`
  (e.g. `CODEGRAPH_MCP_TOOLS=explore,node,search,callers`).
- CLI: `install, uninstall, init, uninit, index, sync, status, ui, unlock, query,
  explore, node, files, callers, callees, impact, affected, daemon, telemetry,
  upgrade, version, serve --mcp` (hidden stdio MCP entry). The CLI twins serve
  non-MCP harnesses (e.g. a DeepSeek harness).
- Per-project index in `.codegraph/` — local artifact, gitignored (here and
  upstream). Native file watcher auto-syncs on save; `codegraph sync` in fresh
  sessions. `codegraph init` builds the graph in one step.
- Harness wiring: Hermes → `$HERMES_HOME/config.yaml` `mcp_servers.codegraph`
  **plus** `platform_toolsets.cli` `mcp-codegraph` (missing the toolset line
  filters tools out of CLI sessions); opencode → `opencode.jsonc`
  `mcp.servers.codegraph` (`codemode: false` keeps explore on the native tool
  list); Claude → `./.mcp.json` / `~/.claude.json` (`alwaysLoad: true`); any
  other MCP client → stdio `codegraph serve --mcp`.
- Telemetry: anonymous rollups only (no code/paths), default ON, opt-out via
  `DO_NOT_TRACK=1` / `CODEGRAPH_TELEMETRY=0` / `codegraph telemetry off`. CI
  sets `DO_NOT_TRACK=1`.
- Vendor A/B (7 repos, median of 4, Claude-Code arm): −35% cost, −57% tokens,
  −46% time, −71% tool calls vs without.
- Health (2026-09-16): 71,092★ / 4,567 forks; 46 npm releases since 2026-01-18;
  pushed the day of research. Single primary maintainer.

## Role in this repo

Primary agent graph search (see the `## codegraph` section in `AGENTS.md`).
Covers code structure: flow tracing, callers/callees, impact, affected tests
(`git diff --name-only | codegraph affected --stdin`). Framework route awareness
(Express, Next.js, Rails, FastAPI, Django, Spring, Gin, …) plus heuristic
dynamic-dispatch edges marked `provenance: 'heuristic'`. Static analysis is
**silent (not wrong)** on reactive/reconciler runtimes (Halo, MediatR, Vue Proxy).

## Related

- [[agent-code-graph-search]] — the job this tool fills
- [[codegraph-vs-graphify]] — comparison with the incumbent + coexistence verdict
