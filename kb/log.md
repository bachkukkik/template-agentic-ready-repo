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
| 2026-10-03 | ingest | raw/articles/karpathy-output-medium-escalation.md | Karpathy output-medium escalation: ladder prose → ASD-STE100 → diagram → HTML → explainer video; meta-thesis large/custom/discardable artifacts; body sha256 verified 21961aa8… |
| 2026-10-03 | create | concepts/output-medium-escalation.md | Layer-2 concept: ladder, meta-thesis, code-first render→parse constraint, six principles and how escalation extends the first four |
| 2026-10-03 | ingest | raw/articles/karpathy-guidelines-skill.md | Vendored karpathy-guidelines skill (four principles) ingested as the primary source; body sha256 6e22cc54… round-trip verified |
| 2026-10-03 | create | concepts/karpathy-coding-guidelines.md | Layer-2 concept: the four guidelines, their relation to output-medium-escalation, repo bindings (funnel stage-5 writer, Standing Order §1); upgrades the six-principles claim from [ASSUMPTION] to grounded |
