---
source_url: https://github.com/bachkukkik/template-agentic-ready-repo
topic: code review and quality controls — current state and industry practice
captured: 2026-10-14
ingested: 2026-10-14
sha256: bc977db4b4ec5a1f6feba696d86c41f08e06410664ede9d64f6c07e8ca0339b3
scope: consolidated dossier for the qc-audit (AGENTS.md funnel stage 2, kb/raw)
---

# Quality-controls audit dossier — template-agentic-ready-repo

Consolidated raw dossier. Three parts: (1) verified current-state inventory of this
repo, (2) control-track research (review controls, Actions hardening, secret/dependency
scanning), (3) peer-repo survey of popular MIT and Apache-2.0 repos. Every claim in
parts 2-3 carries a URL; part 1 carries the command or path that produced it.

## Part 1 — Current-state inventory (verified 2026-10-14, worktree at d54a213)

### What the repo already has

| Gate | Evidence |
|------|----------|
| Unit tier | `.github/workflows/ci.yml` job `unit` — pytest `tests/unit`, timeout 5m |
| Integration tier | `.github/workflows/ci.yml` job `integration` — pytest `tests/integration`, needs `unit` |
| E2E tier | `.github/workflows/ci.yml` job `e2e` — docker compose up + health wait + bats `tests/e2e/` |
| Secret scan (files) | `ci.yml` job `secret-scan` — no tracked `.credentials/` (except `*.example`), no `.env`, no `*.pem|key|p12` |
| Secret scan (assignments) | `ci.yml` — hardcoded secret-assignment grep over `*.py *.sh *.js *.ts *.yml *.yaml *.md` |
| `.credentials/` ignore probe | `ci.yml` — creates a probe file, asserts `git check-ignore` |
| Doctrine integrity | `ci.yml` job `doctrine` — harness symlinks resolve; funnel paths tracked, not gitignored; no secret values under `kb/` |
| Squash-only merge | repo setting `allow_squash_merge: true` (verified via `gh api`) |

### Verified gaps (what the audit must close)

| Gap | Evidence |
|-----|----------|
| Zero reviews on all merged PRs | `gh pr list --state merged --limit 20` → 13 PRs, every `reviews: 0`, no reviewDecision |
| No branch protection / rulesets | `gh api .../branches/main/protection` → 404 "Branch not protected"; `/rulesets` → `[]` |
| No workflow token permissions | No workflow sets a top-level `permissions:` block (grep of `.github/workflows/*.yml`) |
| Tag-pinned actions | `uses: actions/checkout@v4`, `actions/setup-python@v5` — tags, not commit SHAs |
| No dependency scanning | No Dependabot config, no `dependency-review-action`, no OSV/Trivy anywhere in tree |
| No CODEOWNERS | `find` returns nothing matching CODEOWNERS |
| No PR template | No `.github/pull_request_template*` in tree |
| No SECURITY.md | Not in tree |
| No gitleaks / zizmor / CodeQL / actionlint | Not in tree |
| No lint entry point | No `.pre-commit-config.yaml`, no `scripts/lint.sh`, no shellcheck/yamllint/hadolint configs |

### Platform constraints (verified via gh api)

- Repo is **public**, Apache-2.0, single-maintainer.
- Branch protection **is available** (public repo on GitHub Free): 404 was "Branch not
  protected", not the Free-plan 403 "Upgrade required".
- `delete_branch_on_merge: false`, `allow_auto_merge: false`.

## Part 2 — Control-track research

### Track A — review controls & quality gates (solo/agent-driven public repo)

Key findings (full detail with sources in the research notes, summarized here):

1. **Branch protection + rulesets are free on public repos.** Verified: `/protection` → 404
   "Branch not protected" (not a plan 403), `/rulesets` → `[]`. The blocker is enablement, not billing.
   Sources: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule · https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
2. **Rulesets are the right primitive:** layering with most-restrictive-wins, toggleable without
   deletion, and **publicly readable** — an outside auditor (or this repo's own CI doctrine job)
   can prove the merge gate exists without admin access. (same sources)
3. **"Require a pull request before merging" is solo-satisfiable** (author may merge own PR);
   it makes the doctrine's PR+CI path structural instead of aspirational.
   Source: https://github.com/ossf/scorecard/issues/2727
4. **GitHub forbids approving your own PR** → "required approvals ≥1" is structurally
   unsatisfiable for one human. Options: real second reviewer / admin bypass list / path-scoped
   requirement / documented auto-approve proxy (labelled honestly as NOT independent review).
   Sources: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners · https://github.com/netresearch/enterprise-readiness-skill/blob/main/skills/enterprise-readiness/references/scorecard-playbook.md
5. **Required status checks treat `skipped` as passing.** ci.yml chains unit → integration → e2e
   via `needs:`; a failed upstream skips later jobs which then count as green. Fix: require an
   `if: always()` aggregate gate job instead of the skippable tier jobs.
   Source: https://docs.github.com/en/pull-requests/reference/status-checks
6. **Merge queue is org-only** — personal account can't use it; strict "up to date before merging"
   is the available substitute. Source: https://github.com/github/docs/blob/main/data/reusables/gated-features/merge-queue.md
7. **CODEOWNERS is advisory until paired with "Require review from Code Owners"**; it should own
   itself and `.github/workflows/` so an agent cannot silently re-point the guardrails.
8. **Agent-only review correlates with worse outcomes:** 3,109 agentic PRs — CRA-only review
   merged 45.2% vs 68.4% human-only; 92% of CRAs below-60% signal-to-noise. Direction: keep a
   human gate; concentrate review on tests/security/build-config.
   Sources: https://arxiv.org/html/2604.03196 · https://arxiv.org/html/2609.17598
9. **PR template standardizes agent-authored PR context** and is read from the default branch.
   Source: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository

### Track B — Actions hardening

Key findings (peer data in Part 3 corroborates; primary sources):

1. **Least-privilege `permissions:` on every workflow; read-only default** — missing key inherits
   repo default (may include write `contents`). ci.yml declares none (verified).
   Source: https://docs.github.com/en/actions/reference/security/secure-use
2. **Pin third-party actions by full commit SHA** — mutable tags can be re-pointed
   (tj-actions/changed-files compromise is canonical). Scorecard Pinned-Dependencies check.
   Sources: https://docs.github.com/en/actions/reference/security/secure-use · https://github.com/ossf/scorecard/blob/main/docs/checks.md
3. **zizmor** detects workflow-level flaws (template injection, pwn requests, excessive
   permissions); peer repos run it in CI (airflow ×14, ruff ×14, otel ×11, uv ×4). Source: https://woodruffw.github.io/zizmor/
4. **Never `pull_request_target` + untrusted checkout**; actions/checkout@v7+ and a 2026-06
   GitHub default-event-policy block the common unsafe shapes; keep triggers on `pull_request`.
   Sources: https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target · https://github.blog/changelog/2026-06-18-safer-pull_request_target-defaults-for-github-actions-checkout/
5. **Workflow hardening is codifiable**: a CI check can grep every workflow for a top-level
   `permissions:` block and non-SHA `uses:` (with an explicit allowlist-debt register) — turning
   the 89%-of-peer-workflows consensus into an enforced rule.
6. **`persist-credentials: false` on every checkout** — actions/checkout persists the GITHUB_TOKEN
   in `.git/config` by default (zizmor `artipacked` audit); these jobs never push, so the persisted
   credential is pure risk. Source: https://woodruffw.github.io/zizmor/
7. **`permissions: {}` idiom** at workflow top level (deny all), elevating per-job only where
   needed (a zizmor SARIF job needs `security-events: write`).
8. **zizmor SARIF caveat**: zizmor exits 0 regardless of findings when uploading SARIF — gate on
   annotations mode or on the code-scanning alert ruleset instead. Source: track research, https://woodruffw.github.io/zizmor/
9. **Workflow dependency lockfiles** (`.github/workflows/actions.lock` via `gh actions-lock`) pin
   transitive deps, but are public-preview / EC-listed — verify availability before adopting;
   per-action SHA pins remain the portable answer.
   Sources: https://docs.github.com/en/actions/concepts/security/workflow-dependency-lockfiles · https://docs.github.com/en/actions/how-tos/secure-your-work/lock-workflow-dependencies

### Track C — secret & dependency scanning without Advanced Security

Key findings:

1. **GitHub-native secret scanning is automatic + free on public repos**; push protection default-on
   for new public repos and for all free user accounts. Complements, does not replace, the
   hand-rolled regex job (generic secret shapes are paid-tier for GitHub; the repo's regex covers them).
   Sources: https://docs.github.com/en/code-security/how-tos/secure-your-secrets/detect-secret-leaks/enable-secret-scanning · https://github.blog/changelog/2024-03-11-secret-scanning-and-push-protection-are-enabled-by-default-on-new-public-repositories/ · https://github.blog/changelog/2024-02-29-push-protection-is-enabled-for-free-users-on-github/
2. **gitleaks-action needs a licence key on ORG-owned repos; personal accounts free** — invoking the
   gitleaks CLI directly is the licence-clean route for a template. Source: https://github.com/gitleaks/gitleaks-action
3. **Baselines/allowlists are debt**: documented case of a gitleaks baseline suppressing live
   production secrets; allowlist entries need reason + retire condition (matches repo doctrine on
   ignore lists). Source: https://woitzik.dev/blog/gitleaks-baseline-suppressing-live-secrets/
4. **History scans need `fetch-depth: 0`** — current secret-scan job checks only the working tree
   (`git ls-files`), blind to secrets added then removed. Source: https://safeguard.sh/resources/blog/how-to-set-up-secrets-scanning-in-git-repositories
5. **Dependabot is free on every plan** — ecosystems pip + docker + github-actions all supported;
   alerts + security updates need only dependency graph (default-on for public). PRs need no
   Advanced Security. Sources: https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories
6. **dependency-review-action is free on public repos** — fails the PR on newly introduced
   vulnerable deps. Source: https://github.com/actions/dependency-review-action
7. **OSV-Scanner**: free, no quota; BUT directory scans do not auto-discover `requirements.txt` —
   must name the lockfile explicitly or it silently reports clean. Sources: https://google.github.io/osv-scanner/github-action/ · https://github.com/google/osv-scanner/issues/1266
8. **Trivy closes the container layer** — `service/Dockerfile` is `FROM python:3.12-slim`
   (unpinned digest); lockfile scanners never see OS-package CVEs. Source: https://github.com/aquasecurity/trivy-action
9. **actionlint** lints workflows incl. ShellCheck/pyflakes inside `run:` blocks — free, quota-free.
   Source: https://github.com/rhysd/actionlint
10. **TruffleHog is AGPL-3.0** (licence note for the template); verified-secrets weekly sweep is its
    niche vs gitleaks' fast PR gate. Source: https://github.com/trufflesecurity/trufflehog

## Part 3 — Peer-repo survey (first-hand, read-only gh api, 2026-10-14)

Cohorts: MIT = facebook/react, microsoft/vscode, nodejs/node (NOASSERTION), vercel/next.js,
astral-sh/ruff, denoland/deno; Apache-2.0 = kubernetes/kubernetes, apache/airflow,
envoyproxy/envoy, ossf/scorecard, sigstore/cosign, astral-sh/uv,
open-telemetry/opentelemetry-collector. microsoft/TypeScript is Apache-2.0, not MIT —
counted on the Apache side (license verified per repo via `repos/O/R --jq .license.spdx_id`).
All calls read-only; no forks/stars/comments/issues.

### Workflow stats (top-level `permissions:` and pinning, sampled all *.yml/*.yaml in .github/workflows)

| Repo | wf files | top perms | uses SHA/total | CodeQL | zizmor | scorecard | dep-review | actionlint | harden-runner |
|------|---------|-----------|----------------|--------|--------|-----------|------------|------------|---------------|
| kubernetes/kubernetes | 0 (Prow/test-infra, not Actions) | — | — | — | — | — | — | — | — |
| apache/airflow | 56 | 54 | — | 8 | 14 | 0 | 2 | 0 | 0 |
| envoyproxy/envoy | 63 | 62 | — | 21 | 0 | 1 | 1 | 0 | 0 |
| ossf/scorecard | 15 | 14 | — | 13 | 0 | 3 | 1 | 0 | 15 |
| sigstore/cosign | 17 | 14 | — | 10 | 0 | 3 | 0 | 0 | 0 |
| astral-sh/uv | 46 | 43 | — | 0 | 4 | 0 | 0 | 0 | 0 |
| otel-collector | 37 | 37 | — | 10 | 11 | 2 | 0 | 3 | 0 |
| facebook/react | 26 | 26 | 7/203 | 0 | 0 | 0 | 0 | 0 | 0 |
| microsoft/vscode | 15 | 10 | 101/101 | 6 | 0 | 0 | 0 | 0 | 0 |
| nodejs/node | 45 | 45 | 142/142 | 9 | 0 | 6 | 0 | 0 | 1 |
| vercel/next.js | 29 | 15 | 138/139 | 0 | 0 | 0 | 0 | 0 | 0 |
| astral-sh/ruff | 23 | 20 | 323/323 | 0 | 14 | 0 | 0 | 0 | 0 |
| denoland/deno | 11 | 1 | 375/375 | 0 | 0 | 0 | 0 | 0 | 0 |
| microsoft/TypeScript | 13 | 13 | 80/80 | 5 | 0 | 4 | 0 | 0 | 0 |

Aggregates: top-level `permissions:` on **354/396 workflows (89%)**; SHA pinning ≥86% in
**6/7** MIT-side repos (facebook/react is the outlier at 3%); CodeQL in **8/14** repos;
zizmor in **4/14** (airflow, ruff, uv, otel); scorecard-action in **6/14**;
dependency-review-action in **3/14**; gitleaks/trufflehog in Actions: **0/14** — peer repos
rely on GitHub-native secret scanning (free + automatic on public repos), not Actions scanners.

### Governance files (existence verified per path)

| Control | Present | Count |
|---------|---------|-------|
| CODEOWNERS / OWNERS | k8s(root OWNERS), airflow, envoy, scorecard, cosign, otel, vscode, node, next.js, ruff | 10/14 |
| SECURITY.md | k8s, airflow, envoy, scorecard, uv, react, vscode, node, deno, TypeScript | 10/14 |
| PR template | k8s, airflow, scorecard, uv, react, node, ruff, deno | 8/14 |
| dependabot.yml | airflow, envoy, scorecard, cosign, react, vscode, node, TypeScript | 8/14 |
| pre-commit config | airflow, ruff | 2/14 |

### AI-contribution policy (direct quotes, fetched raw)

astral-sh/.github `AI_POLICY.md` (required by both astral-sh/ruff and astral-sh/uv):

> "We require a human in the loop who understands the work produced by AI. **We do not
> allow autonomous agents to be used for contributing to our projects.** We will close
> any pull requests that we believe were created autonomously."
> "AI should not be used to generate comments when communicating with maintainers."

astral-sh/ruff `CONTRIBUTING.md` §Use of AI: "If your contribution does not follow the
policy, it will be closed." … "a successful contribution should still be carefully
reviewed by you and the summary editorialized before submitting a PR."

microsoft/TypeScript `CONTRIBUTING.md`: AI-authored PRs without disclosure are "closed
without review". (Mature-repo norm: disclosure required, human must understand the change.)

### Consensus applied to this repo (implement only >=60% or published-baseline controls)

| Control | Peer consensus | Verdict for template-agentic-ready-repo |
|---------|---------------|------------------------------------------|
| Top-level `permissions:` in workflows | 89% of workflows | **Implement + codify** (CI grep check) |
| SHA-pinned actions | 6/7 MIT-side repos | **Implement + codify** (CI check with explicit allowlist-debt register) |
| SECURITY.md | 10/14 | Implement |
| CODEOWNERS | 10/14 | Implement (advisory, single-maintainer; routes agents + humans) |
| PR template | 8/14 | Implement + codify the demanded sections (pr-lint job checks body) |
| Dependabot (actions+pip+docker) | 8/14 | Implement |
| CodeQL | 8/14, free on public | Implement |
| zizmor | 4/14, rising | Implement as CI job |
| gitleaks/trufflehog in Actions | 0/14 | Do NOT add — GitHub-native secret scanning covers public repos free; keep the hand-rolled job |
| GitHub-native secret scanning + push protection | default-on for public repos | Enable/verify in settings |
| Branch protection + required checks | baseline (Scorecard Tier-1) | Enable via gh api (user approved full scope) |
| AI-disclosure rule | astral-sh + TypeScript norm | Implement as codified pr-lint checkbox, not a closing policy (single-maintainer repo) |

## Part 4 — Refinements from the full research reports (post-append, same day)

1. **Push protection is layered, not monolithic.** Account/user-level push protection is free
   and on by default for pushes to public repos — but generates **no alert record**, and
   *repo-level* push protection (bypass audit trail, bypass reasons) requires paid GitHub
   Secret Protection. Net: prevention exists client-side; auditable enforcement must come
   from the CI secret-scan job. Sources: https://docs.github.com/en/code-security/concepts/secret-security/push-protection · https://github.blog/news-insights/product-news/push-protection-is-generally-available-and-free-for-all-public-repositories/
2. **gitleaks is feature-complete** (security patches only); maintainer successor is
   **Betterleaks** (MIT). If a scanner action is ever adopted, pin gitleaks-action@v3
   (Node 24; v2 stops working 2026-09-16). Validates the peer-derived decision NOT to add
   gitleaks here (0/14 peers; native scanning + the hand-rolled regex stay).
   Sources: https://github.com/gitleaks/gitleaks · https://github.com/betterleaks/betterleaks · https://github.com/gitleaks/gitleaks-action/releases
3. **Solo-maintainer protection posture has named precedents**: BaseCoat solo-dev profile
   and mssql-mcp ADR-0033 both set required_approving_review_count = 0 WITH enforce-admins
   ON, dismiss-stale ON, empty bypass list — "requiring one review on a solo project is
   either blocking or rubber-stamping (theater, not security)", explicitly accepting the
   Scorecard review-heuristic deduction. This is the PRD's AC-QC-011 posture.
   Sources: https://ivegamsft.github.io/basecoat/guides/solo-dev-profile/ · https://github.com/codegiveness/mssql-mcp/blob/main/docs/adr/0033-branch-protection-posture-for-solo-maintained-project.md
4. **Code-review limits toggle**: public repos default to allowing ANY user to approve;
   restrict approvals to users with read access+ BEFORE any approval requirement could
   otherwise be satisfied by a drive-by account. Source: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-pull-request-reviews-in-your-repository
5. **A green job that is not a REQUIRED check is advisory only** — the dependency-review
   docs make the coupling explicit; every gate must be wired into the ruleset as a required
   check or it never blocked anything. Source: https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/manage-your-dependency-security/configure-dependency-review-action
6. **Scorecard Branch-Protection tiers**: Tier 1 = block force-push + deletion (the PRD's
   AC-QC-011 minimum); EnforceAdmins scores false if ANY bypass actor exists on any rule —
   ship rulesets with an empty bypass list. Source: https://github.com/ossf/scorecard/blob/main/docs/checks.md
7. **commitlint-style squash-message check** is a codifiable add for later (squash commits
   are the only main-branch record; currently unvalidated). Source: https://commitlint.js.org/guides/ci-setup.html
