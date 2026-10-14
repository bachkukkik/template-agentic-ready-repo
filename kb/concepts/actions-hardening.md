---
title: Actions Hardening
created: 2026-10-14
updated: 2026-10-14
type: concept
tags: [ops, architecture]
sources: [raw/articles/quality-controls-audit-dossier.md]
confidence: high
---

# Actions Hardening

GitHub Actions supply-chain hygiene, as practiced by peer repos (89% of sampled
workflows set top-level `permissions:`; 6/7 MIT-side repos SHA-pin). The four
codifiable rules, all checkable by grep: ^[raw/articles/quality-controls-audit-dossier.md]

1. **Explicit top-level `permissions:`** — `permissions: {}` (deny-all) at workflow
   level, elevate per job only where needed. Missing key inherits the repo default,
   which may include write scope.
2. **SHA-pin every `uses:`** — mutable tags can be re-pointed to attacker code;
   comment the version (`actions/checkout@<sha> # v4.x.y`). Deviations live in an
   explicit allowlist-debt register (reason + retire condition), never silent.
3. **`persist-credentials: false` on checkout** — the default persists the
   GITHUB_TOKEN into `.git/config`; read-only jobs don't need it.
4. **No `pull_request_target`** — keep triggers on `pull_request`.

Tooling: **zizmor** (workflow static analysis; SARIF mode exits 0 regardless of
findings — gate on annotations or alert rulesets) and **actionlint** (expression
type-checks + ShellCheck/pyflakes inside `run:` blocks). Dependabot's
`github-actions` ecosystem is the standing counterweight that keeps pins current.

Related: [[quality-controls]], [[scanning-without-advanced-security]]
