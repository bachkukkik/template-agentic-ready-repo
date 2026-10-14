---
title: QC Test Tiers
created: 2026-10-14
updated: 2026-10-14
type: concept
tags: [ops, data-model]
sources: []
confidence: high
---

# QC Test Tiers

The repo's own verified test architecture (`tests/run.sh`, `.github/workflows/ci.yml`).
Three tiers encode the tier in the test-ID hundreds digit: unit (`tests/unit/`,
pytest, `AC-X-0NN`), integration (`tests/integration/`, pytest, `AC-X-2NN`), e2e
(`tests/e2e/`, bats against the running container, `AC-X-1NN`). Every PRD success
criterion carries an inline `_Verify:` annotation pointing at the file + ID.

The chain `unit → integration → e2e` via `needs:` has a gate-design consequence:
a failed upstream job *skips* downstream jobs, and GitHub required-check semantics
treat `skipped` as passing. A red unit tier therefore shows green downstream
checks. The fix pattern is an aggregate gate job (`if: always()`, fails unless all
tiers succeeded) that alone carries the required-check status.

Related: [[quality-controls]], [[github-merge-gates]]
