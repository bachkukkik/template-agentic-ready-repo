---
source_url: https://github.com/colbymchenry/codegraph  # README + source @ v1.6.0 (commit 4871114, main)
ingested: 2026-09-16
sha256: 5ec94ec4d13194c584b8bcb435dcbb3ddecbb397d996f0e94ff91ff9d13446a4
---

## What it is

CodeGraph is a local-first code-intelligence CLI + MCP server. It parses a codebase
with tree-sitter into a deterministic (AST-derived, not LLM-summarized) symbol/edge
graph stored in per-project `.codegraph/` SQLite (node:sqlite, WAL + FTS5), and
exposes it to coding agents over MCP (stdio, newline-delimited JSON-RPC 2.0), via a
CLI with identical-output command twins, and a loopback browser viewer.

## License & status

MIT. Active as of 2026-09-16: repo pushed that day; 46 npm releases since 2026-01-18
(repo created 2026-01-18).

## Agent-facing surface

- MCP tools: `codegraph_search`, `codegraph_callers`, `codegraph_callees`,
  `codegraph_impact`, `codegraph_node`, `codegraph_explore` (primary: precise
  symbol-bag query → call path + relevant source in one call),
  `codegraph_status`, `codegraph_files`.
- CLI: `install, uninstall, init, uninit, index, sync, status, ui, unlock, query,
  explore, node, files, callers, callees, impact, affected, daemon, telemetry,
  upgrade, version, serve --mcp` (hidden MCP entry, stdio).
- `codegraph init [path]` creates `.codegraph/` and builds the full graph in one
  step; a native file watcher (FSEvents/inotify/RDCW) auto-syncs on save;
  `codegraph affected --stdin` traces changed files to affected test files (CI
  pattern: `git diff --name-only | codegraph affected --stdin`).

## Harness wiring (from `src/installer/targets/`, v1.6.0)

11 first-class installer targets in `registry.ts`: claude, cursor, codex, opencode,
hermes, gemini, antigravity, kiro, copilot-vscode, copilot-cli, copilot-jetbrains.

| Harness | Artifact | Shape |
|---|---|---|
| Hermes Agent | `$HERMES_HOME/config.yaml` (global only) | `mcp_servers.codegraph: {command: codegraph, args: [serve, --mcp], timeout: 120, connect_timeout: 60, enabled: true}` **plus** `platform_toolsets.cli` gains `- mcp-codegraph` (without it, CLI profiles with an explicit toolset list filter the tools out) |
| opencode | `~/.config/opencode/opencode.jsonc` (XDG) | `mcp.servers.codegraph: {type: local, command: [codegraph, serve, --mcp], disabled: false, codemode: false}` (codemode:false keeps explore on the native tool list) |
| Claude Code | `./.mcp.json` (project) / `~/.claude.json` (global) | `mcpServers.codegraph: {..., alwaysLoad: true}`; optional settings.json permissions + opt-in `UserPromptSubmit` prompt-hook |
| Any other MCP client (e.g. DeepSeek harness) | client's own MCP config | stdio entry `command: codegraph, args: ["serve", "--mcp"]`; non-MCP harnesses use the CLI twins |

Installer is idempotent and self-healing; MCP `initialize` instructions
(`server-instructions.ts`) are the single source of agent-facing guidance — no
instructions-file block is written into CLAUDE.md/AGENTS.md anymore (upstream
issue #529). Unindexed roots still expose the tools with success-shaped guidance
(never `isError`), so a session can start before `codegraph init`.

## Languages

30+ languages with explicit support status in README (TS/JS/TSX, Python, Go, Rust,
Java, C#, PHP, Ruby, C/C++, Swift, Kotlin, Scala, Dart, Svelte, Vue, Astro, CUDA,
Solidity, Terraform/OpenTofu, Nix, COBOL, VB.NET, Erlang, Lua, R, Delphi, …;
Objective-C partial). Framework route awareness (Express, Next.js, Rails, FastAPI,
Django, Spring, Gin, …) plus heuristic dynamic-dispatch edges (callback/observer,
EventEmitter, React re-render, JSX child, RN native↔JS) marked
`provenance:'heuristic'`.

## Governance

- Telemetry: anonymous rollups only (machine UUID, os/arch, node major, command
  counts, agent name from MCP handshake), allowlist-enforced at a public in-repo
  ingest endpoint; default ON with visible installer toggle; opt-out via
  `codegraph telemetry off`, `CODEGRAPH_TELEMETRY=0`, or `DO_NOT_TRACK=1`
  (also disables the once-daily version check; `CODEGRAPH_NO_UPDATE_CHECK=1`
  disables only that).
- Supply chain: npm provenance + signed/attested GitHub releases + SHA256SUMS;
  per-platform bundled Node runtimes (no host Node needed; engines >=20 <25).
- `.codegraph/` is gitignored upstream (their `.gitignore` line 56) — a local
  artifact; WAL grows to a soft threshold (max(256MB, index/4), capped 2GB)
  during big builds, trimmed to 64MB at rest; `CODEGRAPH_WAL_VALVE_MB` /
  `CODEGRAPH_WAL_HEAL_MB` tunables.

## Adoption evidence

- GitHub 2026-09-16: 71,092 stars, 4,567 forks, 508 open issues.
- npm: latest 1.6.0 (2026-08-26); 46 versions; release cadence ~weekly-to-biweekly.
- Vendor A/B (with vs without, 7 repos, median of 4, Claude-Code arm):
  −35% cost, −57% tokens, −46% time, −71% tool calls
  (upstream docs/benchmarks/call-sequence-analysis.md; caveat: token savings exceed
  cost savings because the without-arm's volume is mostly cache reads; vendor-run).
- Known limits: single primary maintainer; static analysis is silent (not wrong) on
  reactive/reconciler runtimes (Halo, MediatR, Vue Proxy); installer shape has
  churned historically (pre-#1698/#207/#529 migrations, now self-healing).

## Alternatives considered (2026-09-16)

| Alternative | Vs CodeGraph |
|---|---|
| graphify (Graphify-Labs/graphify; PyPI `graphifyy`) | skill/CLI-first (MCP is an opt-in `[mcp]` extra via `python -m graphify.serve`); covers non-code artifacts (docs, SQL schemas, PDFs) and emits a committable `graph.json`; no live watcher, no impact/test-affected analysis; Python/uv runtime |
| Serena MCP (oraios/serena, 29,444★) | LSP-based per-language IDE navigation + editing; license NOASSERTION |
| Sourcegraph/SCIP/LSIF | cross-repo + coverage guarantees; needs indexer/server infra |
| universal-ctags / ast-grep | pattern search/rewrite only — no graph, no flow/impact (complementary) |
| aider repo-map (48,989★) | static prompt artifact inside aider only |

Decision for the template: codegraph = primary agent graph search; graphify stays
as the optional knowledge-graph tool for non-code artifacts (coexistence).

## Evidence table

| Fact | Source |
|---|---|
| Product description, MCP tools, CLI commands, install, supported agents/languages, telemetry, `.codegraph/` gitignored, A/B numbers | https://github.com/colbymchenry/codegraph — README.md, TELEMETRY.md, .gitignore @ v1.6.0 (4871114) |
| Installer targets + exact per-harness config artifacts | upstream `src/installer/targets/registry.ts`, `hermes.ts`, `opencode.ts`, `claude.ts` @ 4871114 |
| MCP transport (stdio JSON-RPC 2.0) | upstream `src/mcp/transport.ts` @ 4871114 |
| Repo freshness (stars/forks/issues/pushed_at) | https://api.github.com/repos/colbymchenry/codegraph (queried 2026-09-16) |
| npm version history | https://registry.npmjs.org/@colbymchenry/codegraph (queried 2026-09-16) |
| graphify capability set | https://github.com/Graphify-Labs/graphify, https://pypi.org/project/graphifyy/, https://graphify.com/docs/cli |
| Serena / aider community numbers | https://api.github.com/repos/oraios/serena, https://api.github.com/repos/Aider-AI/aider (2026-09-16) |
| 2026 market framing ("choose the context model that matches the question") | sourcegraph.com/resources/context-compare; sverklo.com/blog/practical-guide-mcp-code-intelligence/ (directional) |
