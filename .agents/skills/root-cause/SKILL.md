---
name: root-cause
description: Find the real cause — of a bug or wrong behavior, or of a "why does X fail / what does X require" question — before fixing or answering. Never guess, never stop at the first plausible hit.
---

# Root Cause

**Shared rule (both tracks):** the first plausible hit is a hypothesis, not the answer. Widen before you commit — list several possible causes, or read across several sources — then rule each in or out with evidence. Stopping at the first thing that fits is the failure mode this skill exists to prevent.

## Which track?

- Requirement / setup / "why does X fail" answerable from docs, knowledge, or config → **Evidence Track**
- Live bug / test failure / wrong runtime behavior needing a code-level explanation → **Debugging Track**
- Bug that traces to an external system's unmet requirement → **Evidence first** (find the requirement), **then Debugging** (locate & fix the violating code).
- **Unsure → start Evidence.** A found requirement usually feeds the debugging anyway; guessing wrong here is cheaper than mis-starting Debugging.

## Evidence Track

**Widen:** one source is rarely the whole answer. Read across sources; a single doc may be partial, outdated, or version/context-specific. Keep reading until the sources agree or you understand why they differ.

**Gate before answering:** every claim you rely on must trace to something you actually read — not memory, not inference from a title. Check it matches the user's version/context. If sources conflict, say so; don't silently pick one.

**Stop:** if you can't find support after a real search, say what's missing rather than guess-filling. "I couldn't find X" beats a confident wrong answer.

## Debugging Track

**Rule:** don't fix until you can say "**X** causes **Y** causes symptom **Z**, and my fix changes **X**." Can't fill that in? Keep digging, don't guess.

**Widen before you dig:** list every plausible cause first (a few, not one). The first cause that fits is a hypothesis — bugs often have more than one contributing cause. Rule each in or out with evidence before committing. Digging deep into the first guess just makes a wrong guess more confident.

**Dig** by asking "why does that happen?" upstream from where the error *shows* to where it *starts*. Use only the effort the bug needs: a typo's chain is one line; an intermittent/async/multi-layer bug needs reproducing and narrowing until the cause is undeniable. Reach for logs or `git bisect` only when reasoning can't localize it.

**Stop rule:** if two fixes fail, stop trying a third — you're likely anchored on the wrong cause, or the design is wrong. Re-widen, or ask the user.

**Then:** fix the cause not the symptom; if the fix only partly helps, a cause remains — keep going. Add a regression test if the bug could return; confirm the original case works.