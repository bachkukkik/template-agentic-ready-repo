# Security Policy

## Scope

This repository is a **template**: it ships no hosted service, no user data, and
no live secrets. A report is most useful when it targets something the template
itself configures — a workflow, a pinned action, a scanning gap, or a default a
downstream project would inherit.

## Reporting a vulnerability

Use **GitHub private vulnerability reporting** on this repository
(Security → Advisories → *Report a vulnerability*). Do not open a public issue
for a suspected vulnerability. Include the affected file(s) or commit, a
reproduction, and the impact you believe it has. Expect an acknowledgement within
a few days — this is a single-maintainer project.

## Secrets

No live secret is ever committed. Credentials come from the environment or the
gitignored `.credentials/` directory, and only `.example` shapes are tracked —
enforced by the `secret-scan` CI job. See `AGENTS.md` § *Security*. If a secret
did land in the tree, report it privately as above: because `kb/raw/` is
add-only, a value there requires rotation, not just deletion.
