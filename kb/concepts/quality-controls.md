---
title: Quality Controls
created: 2026-10-14
updated: 2026-10-14
type: concept
tags: [ops, decision]
sources: [raw/articles/quality-controls-audit-dossier.md]
confidence: high
---

# Quality Controls

The repo's quality-control posture splits into two halves: what is **codified**
(enforced by scripts and CI) and what is **advisory** (routed by files and
settings). The doctrine target, set by the maintainer, is that the large majority
of quality control is codified rules — test tiers, workflow-hygiene greps, PR-lint
checks — with human/agent judgment reserved for the residue.

## Codified gates (existing)

Three test tiers ([[qc-test-tiers]]) plus a secret-scan job (tracked credential
files, hardcoded assignments, `.credentials/` ignore probe) and a doctrine job
(harness symlinks resolve; funnel tracked; no secret values under `kb/`). CI runs
on `pull_request` + `push` to main.

## Gaps (verified 2026-10-14)

- Zero reviews across 13/13 merged PRs; no branch protection or rulesets — any
  push to `main` bypasses every gate ([[github-merge-gates]]).
- Workflows inherit default token scope (no top-level `permissions:`) and pin
  actions by mutable tag ([[actions-hardening]]).
- No dependency scanning, Dependabot, SECURITY.md, CODEOWNERS, PR template,
  zizmor, CodeQL, or lint entry point ([[scanning-without-advanced-security]]).

## Industry norm (14-repo peer survey)

Of 14 popular MIT/Apache-2.0 repos: top-level `permissions:` on 89% of sampled
workflows; SHA-pinned actions in 6/7 MIT-side repos; SECURITY.md 10/14;
CODEOWNERS 10/14; PR template 8/14; Dependabot 8/14; gitleaks/trufflehog in CI
0/14 (native secret scanning covers public repos). Mature repos also publish
AI-contribution policies — astral-sh requires disclosure and bars autonomous
agents ("We do not allow autonomous agents to be used for contributing to our
projects"). ^[raw/articles/quality-controls-audit-dossier.md]

## Codification rule (doctrine)

A control lands as **script + test + CI job** (or as a free, verifiable repo
setting) — never as prose alone. Peer-consensus threshold for adoption: ≥60% or
a published baseline (OpenSSF Scorecard). Advisory artifacts (CODEOWNERS, PR
template) are shipped but labelled advisory. The 20%-judgment residue: merge
decisions, design trade-offs, and AI-contribution stewardship.

Related: [[qc-test-tiers]], [[github-merge-gates]], [[actions-hardening]],
[[scanning-without-advanced-security]]
