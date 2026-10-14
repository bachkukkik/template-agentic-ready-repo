---
title: GitHub Merge Gates
created: 2026-10-14
updated: 2026-10-14
type: concept
tags: [ops, integration]
sources: [raw/articles/quality-controls-audit-dossier.md]
confidence: high
---

# GitHub Merge Gates

Platform-level controls on `main`. Free on public repos regardless of plan;
verified absent here (`/protection` → 404 "Branch not protected", `/rulesets` →
`[]`) while 13/13 merged PRs had zero reviews. ^[raw/articles/quality-controls-audit-dossier.md]

## What a solo repo can actually enforce

- **Require a PR before merging** — satisfiable by the author (self-merge allowed);
  makes the PR+CI path structural. The single highest-value gate.
- **Required status checks, strict (up-to-date)** — replaces the org-only merge queue.
  **Trap:** `skipped` counts as passing, so requiring chainable tier jobs
  (`needs:`-linked) lets a red unit tier still merge green. Require an
  always-running aggregate gate job instead.
- **Block force pushes and deletion**; require conversation resolution.
- **Required approvals ≥1 is unsatisfiable solo** — GitHub forbids self-approval.
  Options: real second reviewer, admin bypass list (declarative only), or a
  documented auto-approve bot labelled as NOT independent review. Evidence:
  agent-only review correlates with worse PR outcomes (45.2% vs 68.4% merge rate).
- **Rulesets over classic protection**: publicly readable → auditable without admin.

Related: [[quality-controls]], [[qc-test-tiers]]
