---
title: Output-medium escalation
created: 2026-10-03
updated: 2026-10-03
type: concept
tags: [decision, ops]
sources: [raw/articles/karpathy-output-medium-escalation.md]
confidence: medium
---

# Output-medium escalation

Output-medium escalation is the choice — for a given piece of model-generated content —
to consume it at the richest useful rung of a medium ladder instead of default prose.
Every rung is still text the model authors; the reader's cost falls as the rung climbs.

## The ladder

From the source post ^[raw/articles/karpathy-output-medium-escalation.md], each rung is
presented as "even better" than the one below:

1. **Prose** — the default medium.
2. **Controlled English (ASD-STE100-style)** — a controlled-language specification
   originally written for aerospace maintenance documentation. The post reports it
   "comes with heavy constraints on clean writing style that I often find a lot more
   readable", and suggests asking for "80% of the way to ASD-STE100" because the spec
   is quite stringent. The attached reference sheet gives the binding limits: procedural
   sentence max 20 words, descriptive max 25, noun cluster max 3 words, one instruction
   per sentence.
3. **Diagram / image** — "a lot easier to process, parse, and understand" than writing.
4. **HTML web page** — a beautiful, interactive webpage; the post cites LLMs' growing
   frontend skill for beautiful experiences and animations.
5. **Explainer video** — the format the author is "most bullish on": fully custom,
   bespoke explainer videos on any arbitrary topic (the example prompt asks for a
   "3b1b style video explainer" with an API-key audio narration, or free/local
   alternatives).

Escalation is per-task, not a mandate to always climb; the rung is chosen by what the
reader must extract.

## Meta-thesis

Two claims carry the ladder, both from the post's summary:

- As LLMs get better they do more of the legwork autonomously, and "a lot more of our
  work will rise up the abstractions into oversight and understanding."
- Because intelligence and code are increasingly abundant, you can ask for "large,
  custom, discardable software artifacts (e.g. web apps, video explainers) that would
  have never made sense to create before."

So the artifact is not decoration. It is the means by which the human stays in
oversight of the model's legwork, and it is **discardable** — built to explain one
thing once, then thrown away. That disposability is what makes the rich rung affordable:
it was never going to be maintained.

## Code-first constraint (this repo's reading)

[ASSUMPTION] the raw post does not state this constraint; it is this repo's reading of
what the ladder requires of an agent stack, and owns the auditable half.

The constraint is that **every rung is code/text, never a bitmap the model must inspect**:

- the model emits code/text (markdown, DOT/Mermaid, HTML/CSS/JS, a video composition);
- a deterministic program renders it;
- the artifact is verified by **parse**, not by looking — SVG/DOM structure, pixel
  buffers, `ffprobe` — so a non-visual LLM engine can drive the whole ladder.

This is the same move as deterministic extraction elsewhere in this stack: the model
authors an artifact, a program — not the model's eyes — determines whether it is
correct. Absent this constraint the upper rungs are unusable to a non-visual engine,
because "did it render?" would be unanswerable.

## The six principles, and what escalation adds

The source grounds two principles. The other four are the repo's `karpathy-guidelines`
coding guidance, recorded here for the relationship — [ASSUMPTION] no raw ingest yet.

| # | Principle | Grounded in |
|---|---|---|
| 1 | Think Before Coding | `karpathy-guidelines` (host skill) — [ASSUMPTION] |
| 2 | Simplicity First | `karpathy-guidelines` (host skill) — [ASSUMPTION] |
| 3 | Surgical Changes | `karpathy-guidelines` (host skill) — [ASSUMPTION] |
| 4 | Goal-Driven Execution | `karpathy-guidelines` (host skill) — [ASSUMPTION] |
| 5 | Output-medium escalation | the raw source ^[raw/articles/karpathy-output-medium-escalation.md] |
| 6 | Discardable artifacts | the raw source ^[raw/articles/karpathy-output-medium-escalation.md] |

Principles 1–4 govern **production** — how the model writes code: plan first, keep it
simple, change only what the goal needs, execute against a stated goal. Principles 5–6
govern **consumption** — what the model delivers and how the human reads it.

The last two *extend* the first four rather than sit beside them. If the code legwork is
autonomous and goal-scoped (1–4), the human's remaining job is oversight and
understanding; the escalated medium is what carries that understanding, and the shortcut
of a discardable artifact is only safe because the change itself was surgical and
goal-verified. Simple production earns the right to a rich, throwaway explanation.

## Provenance

- Raw: `raw/articles/karpathy-output-medium-escalation.md` —
  `source_url: https://x.com/karpathy/status/2105819303471976479`, ingested 2026-10-02,
  body sha256 `21961aa850036fc5ca5003bdd655b6cf7a9f5d004ce6f0c51bb29ab686b0785c`.
- Secondary coverage and the attached ASD-STE100 sheet are recorded in the raw file.

## Related

- [[agent-code-graph-search]] — deterministic extraction is the same code-first move as
  render → parse: a program, not the model, produces the artifact agents consume.
- [[codegraph]] — the implementation adopted in this repo for the code-graph half.
