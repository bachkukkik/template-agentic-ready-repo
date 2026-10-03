---
title: Karpathy coding guidelines
created: 2026-10-03
updated: 2026-10-03
type: concept
tags: [decision, ops]
sources: [raw/articles/karpathy-guidelines-skill.md]
confidence: high
---

# Karpathy coding guidelines

Four behavioral guidelines that reduce common LLM coding mistakes, derived from
Andrej Karpathy's observations on LLM coding pitfalls: **Think Before Coding**
(state assumptions, surface tradeoffs), **Simplicity First** (minimum change, nothing
speculative), **Surgical Changes** (touch only what the request requires), and
**Goal-Driven Execution** (define verifiable success criteria, loop until verified).
^[raw/articles/karpathy-guidelines-skill.md]

## Relation to the output-medium doctrine

The [[output-medium-escalation]] doctrine extends these four with two more principles:
output-medium escalation itself (consume the richest useful rung — prose → controlled
English → diagram → HTML → video) and discardable artifacts (large custom artifacts
built in `scratchpads/`, never cited). All six are cited together as "the Karpathy
principles" in this repo's doctrine; the first four are carried by the vendored
`karpathy-guidelines` skill (`.agents/skills/root-cause` sits alongside it as the
evidence gate), the last two by `AGENTS.md` §7.

## Repo bindings

- **Stage 5 writer** — the document funnel assigns `docs/gaps/NN-*.md` authoring to
  `karpathy-guidelines` (funnel table in `AGENTS.md`), because gap reports are
  evidence-based diagnoses, exactly its discipline.
- **Standing Order §1** — mandated always-on skill, alongside
  [[agent-code-graph-search]] as the investigation tool it pairs with.

## Open questions

None. The four guidelines are stable; the 2026-10-02 output-medium post is their only
recorded extension.
