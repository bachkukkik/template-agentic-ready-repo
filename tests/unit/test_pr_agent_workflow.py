"""Unit tier — the optional PR-Agent integration's gate. IDs: AC-PA-0NN.

Hermetic: file reads plus a YAML parse — no workflow runner, no network, no
service import. The subjects are tracked config files (the workflow and
`.env.example`), and what is asserted is the *opt-in shape*: pinned, least
privileged, inert unless enabled, wired to three customization points.

PRD: docs/prd/07-pr-agent-optional.md.
"""
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pr-agent.yml"
ENV_EXAMPLE = REPO_ROOT / ".env.example"

ACTION = "qodo-ai/pr-agent"
# AC-QC-002 shape: a full 40-hex commit SHA plus the `# vX.Y.Z` provenance comment.
PINNED_ACTION = re.compile(
    rf"uses:\s*{re.escape(ACTION)}@([0-9a-f]{{40}})\s+#\s*v\d+\.\d+\.\d+"
)


def _workflow_text():
    assert WORKFLOW.is_file(), (
        "`.github/workflows/pr-agent.yml` is missing (AC-PA-001) — the optional "
        "PR-Agent integration has to ship as a tracked workflow, not as prose"
    )
    return WORKFLOW.read_text(encoding="utf-8")


def _workflow():
    try:
        return yaml.safe_load(_workflow_text())
    except yaml.YAMLError as exc:  # pragma: no cover - assertion below carries the message
        raise AssertionError(f"pr-agent.yml does not parse as YAML (AC-PA-001): {exc}")


def _env_example_text():
    assert ENV_EXAMPLE.is_file(), (
        "`.env.example` is missing (AC-PA-005) — the optional PR-Agent capability "
        "has to be documented in the tracked env template, not only in prose"
    )
    return ENV_EXAMPLE.read_text(encoding="utf-8")


def _triggers(doc):
    """`on:` is parsed as the boolean True by YAML 1.1 loaders — accept either key."""
    return doc.get("on", doc.get(True)) or {}


def _job(doc):
    jobs = doc.get("jobs") or {}
    assert list(jobs) == ["pr-agent"], (
        f"pr-agent.yml must define exactly one job named `pr-agent`, found {list(jobs)} "
        "(AC-PA-002)"
    )
    return jobs["pr-agent"]


# ── AC-PA-001..005 ────────────────────────────────────────────────────────────

def test_ac_pa_001_workflow_exists_parses_and_action_is_sha_pinned():
    text = _workflow_text()
    doc = _workflow()
    assert isinstance(doc, dict), "pr-agent.yml must parse to a mapping (AC-PA-001)"
    triggers = _triggers(doc)
    assert set(triggers) == {"pull_request"}, (
        f"pr-agent.yml must trigger on `pull_request` and nothing else — no "
        f"`pull_request_target`, which would run with a write token against "
        f"untrusted PR code (AC-PA-001, AC-QC-004) — got {sorted(triggers)}"
    )
    assert set(triggers["pull_request"]["types"]) == {
        "opened", "synchronize", "reopened", "ready_for_review"
    }, (
        f"the pull_request trigger must cover opened, synchronize, reopened and "
        f"ready_for_review (draft -> ready) — got "
        f"{triggers['pull_request']['types']} (AC-PA-001)"
    )
    match = PINNED_ACTION.search(text)
    assert match, (
        f"`{ACTION}` must be referenced as `@<40-hex sha> # vX.Y.Z`, not a tag or "
        "branch — a mutable ref can be re-pointed to attacker code (AC-PA-001, "
        "kb/concepts/actions-hardening.md)"
    )
    refs = re.findall(rf"uses:\s*{re.escape(ACTION)}@(\S+)", text)
    assert refs and all(re.fullmatch(r"[0-9a-f]{40}", rev) for rev in refs), (
        f"every `{ACTION}` ref must be a 40-hex commit SHA, got {refs} (AC-PA-001)"
    )


def test_ac_pa_002_deny_all_default_and_minimal_job_scope():
    doc = _workflow()
    assert "permissions" in doc, (
        "pr-agent.yml needs an explicit top-level `permissions:` key (AC-PA-002); an "
        "omitted key inherits the repo default, which may include write scope"
    )
    assert doc["permissions"] == {}, (
        f"the workflow-level permissions must be deny-all `{{}}`, got "
        f"{doc['permissions']!r} (AC-PA-002)"
    )
    scope = _job(doc).get("permissions")
    assert scope == {"pull-requests": "write", "issues": "write"}, (
        f"the pr-agent job must elevate to exactly `pull-requests: write` and "
        f"`issues: write` — it reviews and comments, nothing else — got {scope!r} "
        "(AC-PA-002)"
    )


def test_ac_pa_003_job_is_gated_on_the_opt_in_variable_and_same_repo():
    gate = _job(_workflow()).get("if")
    assert isinstance(gate, str) and gate, (
        f"the pr-agent job needs a job-level `if:` gate — got {gate!r} (AC-PA-003)"
    )
    opt_in = "vars.PR_AGENT_ENABLED == 'true'"
    same_repo = "github.event.pull_request.head.repo.full_name == github.repository"
    assert opt_in in gate, (
        f"the gate must include `{opt_in}` so an unset or non-`true` variable "
        f"skips the job — the feature is OFF by default — got {gate!r} (AC-PA-003)"
    )
    assert same_repo in gate, (
        f"the gate must also include `{same_repo}`, so fork PRs are skipped "
        f"explicitly and 'reviews stay same-repo' is true by construction — got "
        f"{gate!r} (AC-PA-003)"
    )
    assert gate == f"{opt_in} && {same_repo}", (
        f"the gate must be exactly the two conjuncts `{opt_in} && {same_repo}` — "
        f"got {gate!r} (AC-PA-003)"
    )


def test_ac_pa_004_env_wires_the_three_customization_points():
    env = _job(_workflow()).get("env") or {}
    expected = {
        # `||` fallbacks keep the documented minimum setup working: an unset
        # Actions variable interpolates to "", which would otherwise override
        # the dynaconf default with an empty string.
        "OPENAI__API_BASE": "${{ vars.OPENAI_BASE_URL || 'https://api.openai.com/v1' }}",
        "OPENAI__KEY": "${{ secrets.OPENAI_API_KEY }}",
        "CONFIG__MODEL": "${{ vars.OPENAI_DEFAULT_MODEL || 'gpt-6.1-sol' }}",
        "GITHUB_TOKEN": "${{ secrets.GITHUB_TOKEN }}",
    }
    for key, ref in expected.items():
        assert env.get(key) == ref, (
            f"`{key}` must map to `{ref}` — PR-Agent reads dynaconf SECTION__KEY "
            f"overrides, so the base URL, key and model are the only customization "
            f"points — got {env.get(key)!r} (AC-PA-004)"
        )
    # No value inline: every injected value is a context reference, never a literal.
    literals = {k: v for k, v in env.items() if not str(v).startswith("${{")}
    assert not literals, (
        f"env values must come from `vars.*` / `secrets.*`, never inline literals: "
        f"{literals} (AC-PA-004)"
    )


def test_ac_pa_005_env_example_documents_the_optional_capability():
    text = _env_example_text()
    assert "# ─── PR-Agent (optional) ───" in text, (
        "`.env.example` must end with a commented `# ─── PR-Agent (optional) ───` "
        "section — the capability marker, matching the existing section style "
        "(AC-PA-005)"
    )
    for key in ("PR_AGENT_ENABLED", "OPENAI_BASE_URL", "OPENAI_API_KEY",
                "OPENAI_DEFAULT_MODEL"):
        match = re.search(rf"^{key}=(.*)$", text, re.M)
        assert match, f"`.env.example` must declare `{key}=` (AC-PA-005)"
        value = match.group(1).strip()
        assert value in ("", "false", "changeme"), (
            f"`{key}` must carry a placeholder only, got {value!r} — a real value in "
            "a tracked template is a leak (AC-PA-005, funnel rule 9)"
        )
