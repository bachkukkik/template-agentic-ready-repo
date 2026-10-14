---
title: Scanning Without Advanced Security
created: 2026-10-14
updated: 2026-10-14
type: concept
tags: [ops, integration]
sources: [raw/articles/quality-controls-audit-dossier.md]
confidence: high
---

# Scanning Without Advanced Security

Everything in the secret/dependency scanning layer is free on this public,
personal-account repo. The layering: ^[raw/articles/quality-controls-audit-dossier.md]

| Layer | Control |
|-------|---------|
| Prevention | GitHub push protection (default-on for public repos; verify it stays on) |
| Detect (platform) | Native secret scanning — automatic, free on public repos |
| Detect (generic shapes) | The repo's own regex job — GitHub's free detectors cover provider tokens, NOT generic `api_key=...` shapes; keep both |
| Deps — detect/fix | Dependabot (`pip` + `docker` + `github-actions` ecosystems; free on all plans) |
| Deps — PR gate | dependency-review-action (free on public repos; fails PR on new vulnerable deps) |
| Container | Trivy on the Dockerfile (base image is digest-unpinned; lockfile scanners can't see OS CVEs) |
| Workflow lint | actionlint |

Gotchas verified in research:

- **History scans need `fetch-depth: 0`** — a tree-only scan (`git ls-files`) is
  blind to secrets added then removed.
- **Baselines/allowlists are debt registers**: every entry needs a reason and a
  retire condition; a blanket baseline has documented cases of suppressing live
  production secrets. Never auto-baseline.
- **OSV-Scanner does not auto-discover `requirements.txt`** — name the lockfile
  explicitly or it silently reports clean.
- **gitleaks-action needs a licence on org-owned repos** (personal: free); the CLI
  is MIT and licence-clean everywhere. TruffleHog is AGPL-3.0.

Related: [[quality-controls]], [[actions-hardening]]
