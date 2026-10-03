---
source_url: https://x.com/karpathy/status/2105819303471976479
ingested: 2026-10-02
sha256: 21961aa850036fc5ca5003bdd655b6cf7a9f5d004ce6f0c51bb29ab686b0785c
---

# Andrej Karpathy — output-medium escalation (ASD-STE100 -> diagrams -> HTML -> explainer videos)

Fetched 2026-10-02 directly from x.com via the Z.AI web reader; x.com blocks plain
server-side fetch, so this text was extracted from the post's rendered article body.
Posted 12:37 AM · Oct 2, 2026; public metrics at fetch: ~345.3K views, 341 replies,
858 reposts, 8.9K likes.

## Full post text (verbatim)

> We'll be spending a lot more time trying to understand the outputs of language models. A few thoughts, tips & tricks:
>
> Writing. Something I've had success with: Ask your LLM to explain something in ASD-STE100, it's a controlled language specification originally developed for aerospace maintenance documentation. LLMs well-versed in this language and it comes with heavy constraints on clean writing style that I often find a lot more readable. Sometimes I've tried to soften it a bit e.g. ask for "80% of the way to ASD-STE100" because the spec is quite stringent.
>
> But even better: Diagrams / images. Instead of writing, ask your LLM to create a diagram. These can be a lot easier to process, parse, and understand.
>
> But even better: Web pages. Ask for output "in HTML" to get a beautiful, interactive webpage. LLMs are getting really good at frontend and can create beautiful experiences, animations, etc.
>
> But even better: Explainer videos. The output format I am most bullish on is fully custom / bespoke explainer videos generated on any arbitrary topic. Experiment with things like "Create a 3b1b style video explainer on X. Use my ElevenLabs API key for audio narration". (you'd need an API key for the latter or you can ask your LLM to find you decent free alternatives that use your local compute). This is actually starting to work!
>
> In summary:
> - As LLMs get better, they will do more and more of the legwork autonomously, and a lot more of our work will rise up the abstractions into oversight and understanding.
> - Luckily, LLMs can help here too because as intelligence and code are increasingly abundant, you can ask for large, custom, discardable software artifacts (e.g. web apps, video explainers) that would have never made sense to create before. Push the boundaries here and you'll be surprised.

## Attached media

The post carries a one-page ASD-STE100 Simplified Technical English reference sheet,
laid out on a grid A1-D8 across six panels:

- **A — document structure.** Part 1 writing rules sections 1-9 ("Words / Noun clusters /
  Verbs / Sentences / Procedures / Descriptive writing / Safety instructions /
  Punctuation and word counts / Writing practices"); Part 2 dictionary: ~900 approved
  words (uppercase, one meaning), unapproved words (lowercase, with alternatives),
  technical names, technical verbs.
- **B — sentence anatomy.** Procedural sentence max 20 words, descriptive max 25 words,
  WARNING vs CAUTION, active voice.
- **C — approved verb forms.** Command, simple present, simple past, simple future,
  infinitive, and past-participle-as-adjective are approved; progressive -ing, perfect,
  and passive-in-procedures are not approved.
- **D — dictionary entries.** CLOSE is approved; close / commence / ensure / prior to /
  replenish / utilize / approximately are not approved.
- **E — rule limits.** Procedural sentence max 20 words, descriptive max 25 words,
  descriptive paragraph max 6 sentences, noun cluster max 3 words, max 1 instruction
  per sentence.
- **F — history.** 1979 AECMA; 1986 first AECMA Simplified English Guide; 2005 renamed
  ASD-STE100; free download since Issue 6; maintained by the ASD STEMG.

Source printed on the sheet: asd-ste100.org.

## Secondary coverage and follow-ups

- https://www.explainx.ai/blog/karpathy-understand-llm-outputs-ste100-diagrams-html-video-2026
- https://www.searchenginejournal.com/karpathy-llm-aircraft-manual-writing/591813/
- https://agihunt.info/en/p/1a0fa0c6a6c7a2d960a2111923a
- Direct precursor post: https://x.com/karpathy/status/2053872850101285137 ("structure your response as HTML", 2026-05-11)

## Why this is in the KB for this repo

This is the primary source for the repo's output-medium doctrine. The escalation ladder
is prose -> ASD-STE100 -> diagram -> HTML -> explainer video. The meta-thesis is "large,
custom, discardable software artifacts". The load-bearing constraint for this stack is
that every rung is CODE-FIRST and must work with a non-visual LLM engine.
