"""Unit tier — the codified quality controls. IDs: AC-QC-0NN.

Hermetic: file reads + the stdlib only — no subprocess, no network, no service
import. The subjects are tracked config files (workflows, governance files), not
the example service.

This is the machine-checkable half of PRD 06's 80/20 codification split
(docs/prd/06-quality-controls.md): workflow hygiene (AC-QC-001..004), governance
files (AC-QC-005..008), the CI aggregate/static-analysis jobs (AC-QC-009, 010) and
a meta-assertion that the hygiene checks are enforced, not prose (AC-QC-012).

AC-QC-011 (the `main` ruleset) is a platform setting, verified post-merge via
`gh api repos/.../rulesets` — it cannot be asserted from the tree.
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
GITHUB_DIR = REPO_ROOT / ".github"

# AC-QC-002 debt register. Every `uses:` must be SHA-pinned (40-hex) OR named here.
# An entry needs a REASON and a RETIRE CONDITION (kb/concepts/actions-hardening.md):
# a bare allowlist is a silent, unbounded exception. Empty is the healthy state.
ALLOWLIST = {}


def _workflow_files():
    """Every `.yml` under .github/workflows/, sorted for a stable order."""
    return sorted(WORKFLOWS_DIR.glob("*.yml"))


def _workflow_texts():
    """Mapping of workflow filename -> file text."""
    return {p.name: p.read_text(encoding="utf-8") for p in _workflow_files()}


# ── AC-QC-001..004 helpers, shared with the AC-QC-012 meta-assertion ──────────

def _top_level_permissions_violations(workflows):
    """AC-QC-001: a `permissions:` line at column 0 (workflow level) per file.

    Missing key inherits the repo default, which may include write scope; job-level
    blocks are indented and do not satisfy this.
    """
    return [name for name, text in workflows.items()
            if not any(re.match(r"^permissions:", line) for line in text.splitlines())]


def _unpinned_uses_violations(workflows):
    """AC-QC-002: every `uses:` ref is `<owner>/<repo>@<40-hex>` or in ALLOWLIST."""
    violations = []
    for name, text in workflows.items():
        for ref in re.findall(r"uses:\s*(\S+)", text):
            if ref in ALLOWLIST:
                continue
            _, _, rev = ref.rpartition("@")
            if not re.fullmatch(r"[0-9a-f]{40}", rev):
                violations.append((name, ref))
    return violations


def _checkout_persist_violations(workflows):
    """AC-QC-003: one `persist-credentials: false` per `actions/checkout` step.

    The default persists GITHUB_TOKEN into `.git/config`; a read-only job does not
    need it. Counting equality holds the rule for every checkout step at once.
    """
    violations = []
    for name, text in workflows.items():
        checkouts = text.count("actions/checkout@")
        persists = text.count("persist-credentials: false")
        if checkouts != persists:
            violations.append(f"{name}: {checkouts} checkout(s) vs {persists} persist-credentials")
    return violations


def _pull_request_target_violations(workflows):
    """AC-QC-004: no workflow uses the `pull_request_target` trigger."""
    return [name for name, text in workflows.items() if "pull_request_target" in text]


def _job_block(text, job):
    """Return the YAML text of one top-level job (2-space indent) in a workflow."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(rf"^  {re.escape(job)}:\s*$", line):
            start = i
            break
    assert start is not None, f"job {job!r} not found in workflow"
    block = [lines[start]]
    for line in lines[start + 1:]:
        if re.match(r"^  \S", line):  # next job key at 2-space indent
            break
        block.append(line)
    return "\n".join(block)


def _needed_jobs(block):
    """Extract the `needs:` list from a job block (inline or block-sequence)."""
    inline = re.search(r"^\s*needs:\s*\[([^\]]*)\]", block, re.M)
    if inline:
        return {j.strip() for j in inline.group(1).split(",") if j.strip()}
    seq = re.search(r"^\s*needs:\s*\n((?:\s*-\s*\S+\s*\n?)+)", block, re.M)
    if seq:
        return set(re.findall(r"-\s*(\S+)", seq.group(1)))
    return set()


# ── AC-QC-001..004 ────────────────────────────────────────────────────────────

def test_ac_qc_001_every_workflow_sets_top_level_permissions():
    assert _workflow_files(), "no workflow files found under .github/workflows/"
    violations = _top_level_permissions_violations(_workflow_texts())
    assert not violations, (
        f"workflows without a top-level `permissions:` block: {violations}. An omitted "
        "permissions key inherits the repo default token scope, which may include write "
        "access. Set `permissions: {}` at workflow level and elevate per job "
        "(kb/concepts/actions-hardening.md)."
    )


def test_ac_qc_002_every_uses_is_sha_pinned():
    violations = _unpinned_uses_violations(_workflow_texts())
    assert not violations, (
        f"unpinned `uses:` refs: {violations}. A mutable tag can be re-pointed to "
        "attacker code; pin to a full 40-hex commit SHA with a `# vX` comment, or add a "
        "justified entry to ALLOWLIST (reason + retire condition) "
        "(kb/concepts/actions-hardening.md)."
    )


def test_ac_qc_003_every_checkout_disables_credential_persistence():
    violations = _checkout_persist_violations(_workflow_texts())
    assert not violations, (
        f"checkout steps missing `persist-credentials: false`: {violations}. The default "
        "writes GITHUB_TOKEN into .git/config; a read-only job does not need it "
        "(kb/concepts/actions-hardening.md)."
    )


def test_ac_qc_004_no_pull_request_target_trigger():
    violations = _pull_request_target_violations(_workflow_texts())
    assert not violations, (
        f"workflows using the pull_request_target trigger: {violations}. It runs with a "
        "write token against untrusted PR code — keep triggers on `pull_request` "
        "(kb/concepts/actions-hardening.md)."
    )


# ── AC-QC-005..008 governance files ───────────────────────────────────────────

def test_ac_qc_005_pr_template_exists_with_ai_disclosure():
    path = GITHUB_DIR / "pull_request_template.md"
    assert path.is_file(), "`.github/pull_request_template.md` is missing (AC-QC-005)"
    text = path.read_text(encoding="utf-8")
    assert "- [ ] This PR was authored with AI assistance" in text, (
        "the PR template must carry an AI-assistance disclosure checkbox "
        "(`- [ ] This PR was authored with AI assistance (agent name)`)"
    )


def test_ac_qc_006_dependabot_covers_actions_pip_docker():
    path = GITHUB_DIR / "dependabot.yml"
    assert path.is_file(), "`.github/dependabot.yml` is missing (AC-QC-006)"
    text = path.read_text(encoding="utf-8")
    try:
        import yaml
    except ImportError:
        ecosystems = set(re.findall(r"package-ecosystem:\s*(\S+)", text))
        assert re.search(r"^version:\s*2", text, re.M), "dependabot.yml must declare version: 2"
    else:
        doc = yaml.safe_load(text)
        assert doc.get("version") == 2, "dependabot.yml must declare version: 2"
        ecosystems = {u.get("package-ecosystem") for u in doc.get("updates", [])}
    missing = {"github-actions", "pip", "docker"} - ecosystems
    assert not missing, (
        f"dependabot.yml is missing ecosystems: {sorted(missing)}. github-actions keeps "
        "the SHA pins current; pip covers tests/; docker covers the service image "
        "(kb/concepts/scanning-without-advanced-security.md)."
    )


def test_ac_qc_007_security_md_exists_at_root():
    path = REPO_ROOT / "SECURITY.md"
    assert path.is_file(), "`SECURITY.md` is missing at the repo root (AC-QC-007)"
    text = path.read_text(encoding="utf-8")
    assert len(text.strip()) >= 200, "SECURITY.md is trivially small (AC-QC-007)"
    assert "report" in text.lower(), (
        "SECURITY.md must state how to report a vulnerability (AC-QC-007)"
    )


def test_ac_qc_008_codeowners_owns_itself_and_workflows():
    path = GITHUB_DIR / "CODEOWNERS"
    assert path.is_file(), "`.github/CODEOWNERS` is missing (AC-QC-008)"
    text = path.read_text(encoding="utf-8")
    patterns = [
        line.split()[0]
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert any(p.endswith("CODEOWNERS") for p in patterns), (
        "CODEOWNERS must own its own path (AC-QC-008): add `/.github/CODEOWNERS @owner`"
    )
    assert "/.github/workflows/" in patterns, (
        "CODEOWNERS must own `/.github/workflows/` (AC-QC-008)"
    )


# ── AC-QC-009, 010 CI-side jobs ───────────────────────────────────────────────

def test_ac_qc_009_ci_defines_aggregate_gate():
    ci = _workflow_texts()["ci.yml"]
    block = _job_block(ci, "qc-gate")
    assert re.search(r"^    if: always\(\)\s*$", block, re.M), (
        "the qc-gate job must carry a job-level `if: always()` so it runs even when an "
        "upstream tier fails or is skipped (AC-QC-009)"
    )
    assert _needed_jobs(block) == {"unit", "integration", "e2e", "secret-scan", "doctrine"}, (
        "qc-gate must `needs:` unit, integration, e2e, secret-scan and doctrine — a failed "
        "tier SKIPS its downstream jobs and `skipped` counts as passing, so only this "
        "always-running aggregate job carries the required check "
        "(kb/concepts/qc-test-tiers.md)"
    )


def test_ac_qc_010_ci_defines_fatal_zizmor_job():
    ci = _workflow_texts()["ci.yml"]
    block = _job_block(ci, "zizmor")
    assert "zizmor" in block, "the zizmor job must run the zizmor linter (AC-QC-010)"
    assert "--min-severity low" in block, (
        "zizmor must run with `--min-severity low` (AC-QC-010)"
    )
    assert "sarif" not in block.lower(), (
        "zizmor must fail CI on findings (annotations mode), not SARIF-only — SARIF mode "
        "exits 0 regardless of findings (kb/concepts/actions-hardening.md)"
    )


# ── AC-QC-012 the codification meta-assertion ─────────────────────────────────

def test_ac_qc_012_workflow_hygiene_is_codified():
    """The 80/20 split: workflow hygiene is enforced by assertion, not prose."""
    workflows = _workflow_texts()
    assert workflows, "no workflow files found — cannot assert workflow hygiene"
    violations = (
        _top_level_permissions_violations(workflows)
        + _unpinned_uses_violations(workflows)
        + _checkout_persist_violations(workflows)
        + _pull_request_target_violations(workflows)
    )
    assert not violations, (
        f"workflow hygiene violations while re-running AC-QC-001..004: {violations}"
    )
    # Codification also covers the AGENTS.md context-budget doctrine: that budget
    # test must remain present, so both halves of the codified layer are asserted.
    assert (REPO_ROOT / "tests/unit/test_agents_md_budget.py").is_file(), (
        "tests/unit/test_agents_md_budget.py is gone — the AGENTS.md budget half of the "
        "codified layer is no longer enforced (AC-QC-012)"
    )
    assert Path(__file__).is_file()
