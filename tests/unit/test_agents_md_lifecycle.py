"""Unit tier — the Lifecycle pipeline's own tripwire. IDs: AC-LC-0NN.

Hermetic: a handful of file reads and the stdlib only — no subprocess, no service
import, no transport. The subject of these tests is a tracked document (the Lifecycle
section of AGENTS.md), not the example service.

AGENTS.md's *Lifecycle — Zero to Deployment* section is the coding-agent entry point: a
harness reads it and pastes its fenced blocks verbatim as the kickoff prompt and the
subsequent sub blocks. Each AC pins one half of that contract — the section exists and
orders its two stages (AC-LC-001), the Development stage still names the D0–D4 steps with
their skills (AC-LC-002), and the Delivery stage still carries every pastable sub block,
UAT variant included, without re-duplicating the shared footer (AC-LC-003).
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_MD = REPO_ROOT / "AGENTS.md"

# Anchor on the exact heading text: a rename or a renumber is invisible to an agent
# scanning AGENTS.md for the entry point, which is exactly the drift to catch.
LIFECYCLE_HEADING = "## Lifecycle — Zero to Deployment (coding-agent entry point)"
DEVELOPMENT_HEADING = "### Development stage — idea → implemented"
DELIVERY_HEADING = "### Delivery stage — ship to UAT or production"

# The Development table's step labels. They are the cross-harness contract: a harness
# without /goal prompts "go through D0-D4" and pastes the sub blocks by name.
DEVELOPMENT_STEPS = ["| D0 |", "| D1 |", "| D2 |", "| D3 |", "| D4 |"]

# The four default delivery sub blocks a harness pastes verbatim, in run order.
DELIVERY_SUBS = [
    "## sub1 — docs/tests gap sync",
    "## sub2 — local CI",
    "## sub3 — PR + CI monitor",
    "## sub4 — merge + redeploy",
]

# The opt-in UAT variant: a repo with a `uat` branch replaces sub4 with these, so the
# contract becomes sub1–sub5.
UAT_SUBS = [
    "## sub4 — merge to uat + redeploy",
    "## sub5 — promote uat → main",
]

# The shared footer is appended to the kickoff AND every sub block in the prose — but
# stored ONCE as a fenced block. The dedupe is load-bearing for the 20k-char context-file
# budget (AC-CTX-003 headroom): re-duplicating the footer spends that headroom for nothing.
SHARED_FOOTER_LINES = [
    "use pm skills for PRD, problem triage, success criteria definition and verification policy.",
    "use karpathy skill for codebase investigation and all resource analysis.",
    "prioritize task delegation over direct execution.",
    "use opencode-plan-build-orchestrator skill for all coding tasks.",
]


def _section_body(text: str, heading: str) -> str:
    """Return *heading*'s body, up to the next markdown heading outside a code fence.

    A plain "next heading of any level" scan is wrong for the Delivery stage: its sub
    blocks are labelled with '## subN' lines that live INSIDE ``` fences, so they are
    pastable prompt text, not section boundaries. Tracking the fence toggle keeps those
    lines in the body while still stopping at the next real heading ('### Running the
    pipeline without /goal').
    """
    assert heading in text, (
        f"AGENTS.md has no '{heading}' heading, so its section cannot be sliced for "
        "inspection. Every AC in this file resolves its claims by exact heading text; a "
        f"renamed or removed heading hides the section from agents too. Remedy: restore "
        f"'{heading}' in AGENTS.md."
    )
    body = []
    in_fence = False
    for line in text[text.index(heading) + len(heading) :].split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
            body.append(line)
            continue
        if not in_fence and re.match(r"#{1,6} ", line):
            break
        body.append(line)
    return "\n".join(body)


def test_ac_lc_001_lifecycle_section_exists_and_orders_its_stages():
    """AC-LC-001: AGENTS.md carries the Lifecycle heading and both stage subheadings, Development before Delivery."""
    text = AGENTS_MD.read_text(encoding="utf-8")
    assert LIFECYCLE_HEADING in text, (
        f"AGENTS.md has no '{LIFECYCLE_HEADING}' heading. The Lifecycle section is the "
        "coding-agent entry point — the single place telling an agent which pipeline to "
        "run and in what order — so without the exact heading an agent scanning AGENTS.md "
        f"never finds it. Remedy: restore the heading '{LIFECYCLE_HEADING}' in AGENTS.md."
    )

    for stage in (DEVELOPMENT_HEADING, DELIVERY_HEADING):
        assert stage in text, (
            f"AGENTS.md Lifecycle section is missing the stage subheading '{stage}'. The "
            "sequence the coding agent MUST follow is two stages — Development (idea → "
            "implemented) then Delivery (ship to UAT or production) — and each stage only "
            "exists under its own subheading. Remedy: restore the subheading in AGENTS.md."
        )

    dev_at = text.index(DEVELOPMENT_HEADING)
    deliv_at = text.index(DELIVERY_HEADING)
    assert dev_at < deliv_at, (
        f"AGENTS.md lists '{DELIVERY_HEADING}' before '{DEVELOPMENT_HEADING}' "
        f"(offsets {deliv_at} then {dev_at}). The stages run in that order: an agent "
        "follows Development — idea → implemented before Delivery — ship to UAT or "
        "production, so a swapped layout sends it to open PRs (sub3) against a change "
        "that sub1–sub2 never implemented. Remedy: put the Development stage above the "
        "Delivery stage in AGENTS.md."
    )


def test_ac_lc_002_development_stage_names_every_step_and_its_skill():
    """AC-LC-002: the Development stage body lists D0–D4 in order and names both step skills."""
    text = AGENTS_MD.read_text(encoding="utf-8")
    section = _section_body(text, DEVELOPMENT_HEADING)

    missing = [step for step in DEVELOPMENT_STEPS if step not in section]
    assert not missing, (
        f"the Development stage table is missing row(s) {missing}. D0–D4 is the "
        "cross-harness contract an agent walks (entry → intent → gaps → implement → "
        "empirical docs), and a harness with no /goal prompts those labels verbatim; a "
        "dropped row silently shortens the pipeline for every agent. Remedy: restore the "
        "missing '| Dn |' rows of the Development table in AGENTS.md."
    )

    idx = [section.index(step) for step in DEVELOPMENT_STEPS]
    assert idx == sorted(idx), (
        f"the Development stage rows are out of order: "
        f"{dict(zip(DEVELOPMENT_STEPS, idx))}. The steps are sequential — D2 diffs Gaps "
        "against what D1's PRD intends, D3 implements, D4 records the empirical verdict — "
        "so a reordered table tells an agent to document before it builds. Remedy: sort "
        "the '| Dn |' rows D0 → D4 in the Development table."
    )

    for skill, step in (
        ("opencode-plan-build-orchestrator", "the implement step (D3)"),
        ("coding-agents-docs-guideline", "the empirical-docs step (D4)"),
    ):
        assert skill in section, (
            f"the Development stage body does not name '{skill}', the skill of {step}. "
            "The Do column is what an agent executes, so a step stripped of its skill is "
            "a step an agent improvises — and funnel rule 8 makes skill gates absolute "
            f"(a missing harness mechanism is no waiver). Remedy: restore '{skill}' in "
            "the relevant Dn row of AGENTS.md."
        )


def test_ac_lc_003_delivery_stage_carries_subs_uat_and_single_footer():
    """AC-LC-003: the Delivery stage holds sub1–sub4 in order plus the opt-in UAT variant, and the shared footer appears exactly once."""
    text = AGENTS_MD.read_text(encoding="utf-8")
    section = _section_body(text, DELIVERY_HEADING)

    missing = [sub for sub in DELIVERY_SUBS if sub not in section]
    assert not missing, (
        f"the Delivery stage is missing {missing}. sub1–sub4 are the four blocks a "
        "harness pastes verbatim in run order (gap sync → local CI → PR + CI monitor → "
        "merge + redeploy), so a missing block is a delivery step every agent silently "
        "skips. Remedy: restore the '## subN' block in the Delivery stage fenced block "
        "of AGENTS.md."
    )

    idx = [section.index(sub) for sub in DELIVERY_SUBS]
    assert idx == sorted(idx), (
        f"the Delivery stage sub blocks are out of order: "
        f"{dict(zip(DELIVERY_SUBS, idx))}. They run in sequence — sub2's local CI gates "
        "the PR sub3 opens, which sub4 then merges — so a swapped pair tells an agent to "
        "merge a PR that was never CI-checked. Remedy: sort the '## subN' blocks "
        "sub1 → sub4 in the Delivery stage of AGENTS.md."
    )

    for uat in UAT_SUBS:
        assert uat in section, (
            f"the Delivery stage does not carry the UAT variant block '{uat}'. A repo "
            "with a `uat` branch + UAT stack replaces sub4 with it, making the contract "
            "sub1–sub5; without the block such a repo has no promote-to-main step at all. "
            "Remedy: restore the '## sub4 — merge to uat + redeploy' and "
            "'## sub5 — promote uat → main' blocks in AGENTS.md."
        )

    assert "opt-in" in section, (
        "the Delivery stage does not mark the UAT variant as opt-in. The variant is only "
        "correct for a repo that has a `uat` branch; without the marker an agent applies "
        "sub5 to a repo with no uat branch and stalls. Remedy: keep the '(opt-in)' label "
        "on the UAT variant paragraph in AGENTS.md."
    )

    duplicates = {
        line: text.count(line)
        for line in SHARED_FOOTER_LINES
        if text.count(line) != 1
    }
    assert not duplicates, (
        f"shared footer line(s) occur != 1 time in AGENTS.md: {duplicates}. The footer is "
        "appended to the kickoff and every sub block in the PROSE, but stored once as a "
        "fenced block; re-duplicating it spends the finite 20k-char context-file headroom "
        "that AGENTS.md's budget guards (AC-CTX-003) for no new instruction. Remedy: keep "
        "each footer line in the single 'Shared footer' fenced block and cite it by name "
        "elsewhere."
    )
