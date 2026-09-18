# KB Action Log

> Append-only. Maintained by the `llm-wiki` skill — one line per ingest, page
> create/update, query filing, or archive action. Rotate past 500 entries.
> Format: `YYYY-MM-DD | <action> | <path(s)> | <note>`

| Date | Action | Path(s) | Note |
|------|--------|---------|------|
| 2026-09-16 | ingest | raw/articles/codegraph-mcp-code-intelligence.md | CodeGraph v1.6.0 evidence: MCP surface, per-harness wiring, telemetry, .codegraph/ policy, alternatives |
| 2026-09-16 | create | entities/codegraph.md, concepts/agent-code-graph-search.md, comparisons/codegraph-vs-graphify.md | Layer-2 pages for the codegraph-as-primary-graph-search adoption; coexistence verdict vs graphify |
| 2026-09-16 | archive | raw/articles/codegraph-mcp-code-intelligence.md → _archive/raw/articles/codegraph-mcp-code-intelligence.md | v1 misstated the default MCP surface as 8 listed tools; superseded |
| 2026-09-16 | ingest | raw/articles/codegraph-mcp-code-intelligence.md | Corrected v2: one-tool-by-default MCP surface + CODEGRAPH_MCP_TOOLS (verified via live tools/list handshake) |
| 2026-09-16 | update | entities/codegraph.md, comparisons/codegraph-vs-graphify.md | Fix "8 MCP tools" claim per live verification |
