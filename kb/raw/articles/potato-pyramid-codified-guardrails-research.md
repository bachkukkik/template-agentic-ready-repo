---
source_url: https://github.com/The-Focus-AI/ai-engineer-code-2026-nov/blob/main/talks/2026-11-11-all-code-is-slop-except-mine/transcript.md
video_url: https://youtu.be/O_zcc6Xl12g
topic: codified AI-agent guardrails — the potato (inverse) pyramid, 69 techniques across 6 research items
captured: 2026-11-15
ingested: 2026-11-15
sha256: ee45e9701c2a6251113f9d4ddc7aac2c8909075b122c566f7da42dca36b92599
scope: research digest (stage 2 ingest) distilled from a six-item web-research wave (69 techniques, 171 source URLs); canonical source is the talk transcript in kb/raw/transcripts/ — this digest carries the remaining evidence URLs
---

# Codified agent guardrails — potato-pyramid research digest

Lauren "poteto" Tan (SpaceXSI/xAI, Grokbot), *All Code Is Slop (Except Mine)*,
AI Engineer Code Summit 2026-11-11. Thesis: an agent's environment — not prose
rules — determines output quality. Her inverse pyramid, bottom-up:

1. **Codebase** — API design, architecture, refactoring (deterministic constraint)
2. **Static analysis** — lint, types, compilers, tests (deterministic constraint)
3. **Verification** — runtime + formal (TLA+, Lean, property-based testing)
4. **Prose** — rules/skills/AGENTS.md; smallest layer, judgment only

Verified talk facts: Grokbot shipped ~11,000 PRs/month at ~0.5% revert rate,
227 contributors, daily stable releases; banned ~99% of comments ("they go
stale easily… they're not enforceable"); banned `useEffect` outside sanctioned
APIs; "every time you correct an agent, it turns into one of these
deterministic checks"; review shrank to checking verification artifacts
(videos, screenshots, dimensions); sequencing — improve the codebase first,
clean old patterns, then strengthen verification ("if your inner coding loop
produces slop, automating it just produces more slop").

## Layer 2a — comment suppression (11 techniques; the canonical worked example)

Blanket comment ban with directive allowlist (`eslint-plugin-no-comments`,
~41k dl/wk; its `allow` array REPLACES defaults); Python comment ban
(`sloplint` SLP010, per-path opt-back-in); per-PR diff comment-ratio budget
(`IgnaceMaes/comment-ratio@v1` via `tokei`); density ceilings
(`eslint-plugin-ai-guardrails`); commented-out-code bans (Ruff `ERA`,
SonarJS `no-commented-code`, SonarQube S125); zero-budget TODO/FIXME
(`no-warning-comments` + `--max-warnings 0`, pylint W0511, Ruff `TD`/`FIX`);
linked-TODO discipline (Chromium `TODO(crbug.com/<id>)`, flake8-todos TD003);
inline-comment placement bans (ESLint core, frozen); agent-time pre-write
blocking (`agent-comment-lint`, "Your CLAUDE.md or AGENTS.md asks; this
enforces"); docstring floor paired with the comment ceiling (`interrogate
--fail-under`); repo-wide density dashboard (SonarQube `comment_lines_density`)
under a diff-level gate.

Key sources: https://www.npmjs.com/package/eslint-plugin-no-comments ·
https://github.com/OrodruinLabs/agent-comment-lint ·
https://github.com/IgnaceMaes/comment-ratio · https://github.com/galthran-wq/sloplint ·
https://docs.astral.sh/ruff/rules/commented-out-code/ ·
https://chromium.googlesource.com/chromium/src/+/refs/tags/128.0.6561.3/styleguide/todos.md ·
https://interrogate.readthedocs.io/en/latest/ ·
https://docs.sonarsource.com/sonarqube-server/user-guide/code-metrics/metrics-definition

## Layer 1+2 — banned APIs, dependency graph, architecture (14 techniques)

Symbol bans with prescriptive messages naming the sanctioned replacement
(ESLint `no-restricted-syntax`/`no-restricted-imports`/`no-restricted-properties`;
xAI bans `useEffect`, Cursor bans imperative timers); zone path bans
(`import/no-restricted-paths`); whole-repo dependency-graph gates
(`dependency-cruiser` forbidden rules, regex-not-glob paths); element-type
boundaries (`eslint-plugin-boundaries`); monorepo tag constraints
(`@nx/enforce-module-boundaries`); Python import contracts (`import-linter`)
and declared-dependency modules (`tach`); JVM bytecode architecture tests
(ArchUnit); TS architecture tests as unit tests (`tsarch`); public-API surface
control (`api-extractor` API reports, knip); suppression hygiene
(`reportUnusedDisableDirectives`, bulk-suppression ratchets).
Pitfall: land the sanctioned wrapper BEFORE banning the primitive, and put
constraint files under CODEOWNERS — agents edit them.

Key sources: https://eslint.org/docs/latest/rules/no-restricted-syntax ·
https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md ·
https://import-linter.readthedocs.io/en/stable/contract_types/forbidden/ ·
https://docs.gauge.sh/usage/configuration/ · https://www.archunit.org/userguide/html/000_Index.html ·
https://www.angulararchitects.io/en/blog/architecture-beyond-layers-tsarch-for-ai-agents/

## Layer 2b — type-system constraints (12 techniques)

Strict-by-default compiler bundles (`strict` + `noUncheckedIndexedAccess` +
`exactOptionalPropertyTypes` — NOT included by `strict`; pyright strict leaves
`reportUnnecessaryTypeIgnoreComment` off); exhaustive variants (discriminated
unions + `never`; `switch-exhaustiveness-check`; Python `assert_never`);
completeness registries (`as const satisfies`); branded types + smart
constructors; escape-hatch bans (`no-explicit-any`, `ban-ts-comment`,
`no-unsafe-type-assertion` — NOT in strictTypeChecked, must be added; Python:
`disallow_any_explicit`/basedpyright `reportAny`); suppression accounting
(PGH003, RUF100, `warn_unused_ignores`); parse-at-the-boundary schemas (zod/
valibot, Standard Schema v1; `z.input` vs `z.output` drift); type-level
regression tests (`expectTypeOf`, `@ts-expect-error` as assertion); type-
coverage budget as CI metric (`type-coverage --at-least`; Stripe's Sorbet
score). Research found a controlled experiment (arXiv:2606.01522): detailed
type-error messages measurably improve agent repair rates.

Key sources: https://typescript-eslint.io/rules/no-unsafe-type-assertion ·
https://docs.basedpyright.com/dev/benefits-over-pyright/new-diagnostic-rules/ ·
https://standardschema.dev/schema · https://vitest.dev/guide/testing-types ·
https://arxiv.org/abs/2606.01522 · https://stripe.dev/blog/sorbet-stripes-type-checker-for-ruby

## Meta-layer — correction loop, slop metrics, CI gates (15 techniques)

Correction-to-rule capture (every review correction becomes a lint rule with a
root-cause-fix message); categorical elimination via API design (the other
branch); regression-test-on-fix (LLVM Developer Policy precedent) and its
strong form — the new test must FAIL on the base commit; rule synthesis from
review history (Auto-SCAT, EMSE 2022; ICSE-SEIP 2023); new-code-only gates
with ratchets (Sonar New Code definition, ESLint bulk suppressions); delta
duplication gate (jscpd v5 `--baseline-from-ref --fail-on-new-clones`);
complexity budgets (eslint `complexity`/`max-lines`, ruff C901, xenon); patch
coverage + mutation score (codecov patch, Stryker break threshold); PR
size/churn budgets (danger.js); revert-rate tracking as the outcome metric
(DORA change failure rate; MSR 2026: AI-revert rates 6.1% vs 14.5% across
datasets — never compare vendors on one number). AI reviewers stay advisory:
nondeterministic verdicts never gate merges (OSWorld: ~78% Pass@10 but
all-10-run success ~36%).

Key sources: https://llvm.org/docs/DeveloperPolicy.html ·
https://eslint.org/blog/2025/04/introducing-bulk-suppressions/ ·
https://jscpd.dev/guides/ci · https://docs.codecov.com/docs/commit-status ·
https://stryker-mutator.io/docs/stryker-net/configuration/ ·
https://dl.acm.org/doi/full/10.1145/3793302.3793587

## Layer 3a — runtime verification (8 techniques)

Feature maps as shared vocabulary (`.features/*.yaml` + `validate --strict`
in CI; feature-map-cli); per-repo verification skills (launch/doctor/drive/
evidence/cleanup; pstack `/create-verification-skill`); CDP/MCP browser
harnesses (chrome-devtools-mcp — use `--isolated`, never a logged-in profile;
Playwright MCP); agent-recorded video/screenshot PR artifacts (`shot-scraper
video` YAML storyboards with `wait_for` assertions; Devin recordings);
agent-driven whole-build fuzzing opening fix PRs (Grokbot release routine);
reviewer-side execution passes (advisory); statechart review artifacts
(pstack `/statechart`); promoted smoke gates in branch protection (promote an
agent journey to a scripted Playwright spec once green ~2 weeks).

Key sources: https://github.com/ChromeDevTools/chrome-devtools-mcp ·
https://github.com/microsoft/playwright-mcp · https://shot-scraper.datasette.io/en/latest/video.html ·
https://simonwillison.net/2026/jun/30/shot-scraper-video/ ·
https://docs.devin.ai/work-with-devin/testing-and-recordings ·
https://github.com/cursor/plugins/tree/main/pstack/skills/create-verification-skill

## Layer 3b — formal & property-based verification (9 techniques)

TLA+/PlusCal model checking of multi-actor flows in CI (AWS since 2011; Azure
Cosmos DB; Mergify 2026: TLC over 468k states <1 min, found 2
production-latent bugs; beware vacuous invariants — prove each check fails on
a broken variant); Lean 4 proofs for small algorithmic cores (xAI's
virtualizer no-flicker; zkEVM experience: toolchain drift is the cost);
property-based testing (fast-check, Hypothesis; round-trip/idempotence/
monotonicity properties); stateful/model-based testing (`fc.commands` +
`fc.modelRun`, Hypothesis `RuleBasedStateMachine`); UI temporal properties
over DOM state (Bombadil — `always`/`eventually` specs, no-overlap,
count-stable-while-scrolling, GitHub Action); conformance/trace validation
against specs (MongoDB 2025; Datadog FETCh 2026 — a stale spec drifted for a
year); runtime invariant assertions (`tiny-invariant`, icontract/deal).

Key sources: https://cacm.acm.org/research/how-amazon-web-services-uses-formal-methods/ ·
https://mergify.com/blog/how-we-formally-verified-our-merge-queue-with-tla-plus ·
https://www.datadoghq.com/blog/engineering/continuous-formal-spec-validation/ ·
https://www.mongodb.com/company/blog/engineering/conformance-checking-at-mongodb-testing-our-code-matches-our-tla-specs ·
https://github.com/antithesishq/bombadil · https://fast-check.dev/ ·
https://hypothesis.readthedocs.io/en/latest/stateful.html

## Adoption in this repo (2026-11-15)

The gate `scripts/audit_pyramid.py` (unit-tier enforced via
`tests/unit/test_audit_pyramid.py`, AC-PYR-001..006) machine-checks the three
deterministic foundations on this repo's tracked code: banned patterns
(shell=True, requests-without-timeout, bare except, dynamic eval/exec),
per-file comment budget + unlinked-TODO + commented-out-code + max-consecutive
comment lines (default 3), and per-module test references. `.env.example` and
`.gitignore` are budgeted under the same rule. Nine skills from
[cursor/plugins](https://github.com/cursor/plugins) (MIT) carry the practice:
`correct`, `cli-for-agents`, `principle-type-system-discipline`, `no-comments`
(+ comment-sicko persona), `blast-radius`, and the verification quartet.
