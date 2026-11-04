# 08 — PR-Agent Live Run (First Opted-In Review)

> Funnel stage 6 (reality). Written via `coding-agents-docs-guideline`. Records the
> first real PR-Agent run on this repo (PRs #26/#27, 2026-11-04), the blocker found,
> and its resolution. Intent lives in `docs/prd/07-pr-agent-optional.md`.

## What

The optional PR-Agent job (`.github/workflows/pr-agent.yml`) was enabled on this repo
and exercised against real PRs. Opt-in configuration: repo variable
`PR_AGENT_ENABLED=true`; secret `OPENAI_API_KEY` (LiteLLM virtual key
`template-pr-agents-v3`, team-scoped, masked in logs); repo variables
`OPENAI_BASE_URL=<gateway>/v1` (this deployment's LiteLLM gateway — the concrete
value lives only in the repo variable, not in tracked files) and
`OPENAI_DEFAULT_MODEL=openai/zai/glm-5.3-flash`; repo-level `.pr_agent.toml`
declaring `custom_model_max_tokens = 32000` for the unknown gateway model.

## Why

The template shipped the feature dormant (PR #25). Proving repo correctness required
an end-to-end run: opt-in variable flips the check from *skipping* to *running*, and
the agent must post real review output through a self-hosted, non-OpenAI endpoint.

## How

1. Enabled the four GitHub settings above (key transferred server-side; value never
   entered chat or logs).
2. Opened proof PR #26 (docs-only). `AI Code Review` check flipped from
   `skipping` → running — the opt-in gate works.
3. First failing run exposed two gaps, both fixed:
   - PR-Agent refuses unknown models: `Model openai/zai/glm-5.3-flash is not defined
     in MAX_TOKENS ... or set a positive value for it in
     config.custom_model_max_tokens`. Fixed by `.pr_agent.toml` on **main**
     (PR-Agent reads repo settings from the *base branch* via the GitHub API, never
     the PR head — verified in `github_provider.get_repo_settings` of v0.49.0).
   - Base URL must include `/v1` (the OpenAI SDK appends `/chat/completions`).
4. Proof PR #27 then hit a third blocker: Cloudflare **Bot Fight Mode** on
   `<gateway>` (the same LiteLLM host) served a managed challenge to GitHub-runner IPs
   (LLM responses replaced by a "Just a moment..." HTML page). This host and browsers
   passed; only datacenter ASNs were challenged. BFM is
   auth-inappropriate here — the gateway is already key-protected — so BFM was
   **disabled** in the Cloudflare dashboard (zone `bachkukkik.com`, account
   Krichkorn@gmail.com's Account; free plan has no per-rule BFM skip).
5. Re-ran the failed job: `AI Code Review` **pass (1m24s)**.

## Verification

```bash
gh pr checks 27   # AI Code Review  pass 1m24s
gh api repos/bachkukkik/template-agentic-ready-repo/issues/27/comments --jq '.[].user.login'
# github-actions[bot] x4 — includes:
#   "## PR Reviewer Guide 🔍" (effort 1/5, no security concerns)
#   "## PR Code Suggestions ✨" (move verified-live record to stage-6 docs — followed here)
```

The suggestion content itself is the strongest evidence: the gateway model produced a
repo-aware, doctrine-correct review of this very repo.

## What Works

- Opt-in via repo variable; dormant (`skipping`) until flipped — observed on PRs #25/#26.
- Conventional naming (`OPENAI_BASE_URL` / `OPENAI_API_KEY` / `OPENAI_DEFAULT_MODEL`)
  mapped onto PR-Agent settings via dynaconf env overrides.
- Custom OpenAI-compatible gateway (LiteLLM) as model backend, team-scoped virtual key.
- `concurrency` group prevents double-posted reviews on synchronize (PR #26 run
  skipped with `Skipping action: synchronize`).
- Same-repo guard: fork PRs cannot reach the secret.

## What Fails

- Unknown model without `custom_model_max_tokens` → every tool fails
  (`MAX_TOKENS` error), action goes red.
- Base URL without `/v1` → requests hit `BASE/chat/completions` (404/HTML).
- Cloudflare Bot Fight Mode (free plan) + GitHub-hosted runners → managed challenge
  blocks the API path entirely; response body is the challenge HTML, not JSON.
- `.pr_agent.toml` on a PR branch has no effect until merged to the base branch.

## Resolution

- `.pr_agent.toml` added on main (in #26) with `custom_model_max_tokens = 32000`.
- Cloudflare Bot Fight Mode disabled for `bachkukkik.com` (2026-11-04). If it is ever
  re-enabled, runner-sourced LLM calls will fail again the same way — re-check this
  doc first.
- PRD 07 keeps intent only; this file is the empirical record (the split PR-Agent's
  first review itself suggested).

## Verdict

**Works.** The template's optional PR-Agent feature is proven end-to-end on this repo:
opt-in → gated run → gateway-backed LLM review posted as PR comments, with the three
operational pitfalls above documented for every future clone that opts in.
