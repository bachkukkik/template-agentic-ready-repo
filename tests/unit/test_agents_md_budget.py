"""Unit tier — the doctrine's own tripwire. IDs: AC-CTX-0NN.

Hermetic: one file read and the stdlib only — no subprocess, no service import, no
transport. The subject of the test is a tracked document, not the example service.

Three guards, in escalating order: AC-CTX-001 the flat-floor cap, AC-CTX-002 the
host-pinned cap override, AC-CTX-003 the headroom floor that fails accretion LOUDLY
before the cap is ever reached.
"""
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_MD = REPO_ROOT / "AGENTS.md"

# Every harness auto-loads an agent instruction file (AGENTS.md, CLAUDE.md, .hermes.md,
# .cursorrules, SOUL.md) into each prompt and SILENTLY truncates one that exceeds the
# context-file cap. CONTEXT_FILE_MAX_CHARS = 20_000 in agent/prompt_builder.py is the flat
# floor of a dynamic cap (context_length x 4 x 0.06, clamped 20,000-500,000) and is the
# value that applies whenever the model window is not threaded through — i.e. most of the
# time. Overflow is lossy in the MIDDLE: head 70% + a [...truncated] marker + tail 20%
# survive, so position, not importance, decides what the agent sees.
#
# It is a CHARACTERS rule — measure with len() / `wc -m`. Bytes (`ls -l`, `wc -c`) are
# only a proxy: they under-report multi-byte content.
CONTEXT_FILE_MAX_CHARS = 20_000

# AC-CTX-002: the effective cap is HOST state, not repo state. A host profile may pin a
# LOWER `context_file_max_chars` than the flat floor, and that pin silently truncates a
# file AC-CTX-001 happily passes (docs/02-agents-md-context-budget.md, *What Fails*:
# "the cap is host-dependent"). Honor an explicit override so the lower cap becomes
# visible to CI whenever the host exports it; fall back to the flat floor otherwise.
CAP_ENV_VAR = "AGENTS_MD_CAP_CHARS"

# AC-CTX-003: headroom floor. The cap test only fires once the file has ALREADY crossed
# the cap — by then the middle of the file is gone. Demand a margin, so accretion fails
# the tier while the file still fits; ~500 chars is roughly 15 lines of prose.
HEADROOM_FLOOR_CHARS = 500


def _effective_cap() -> int:
    """Return the harness context-file cap in characters.

    An explicit host pin (`AGENTS_MD_CAP_CHARS`, an integer number of characters) wins;
    absent or empty, the repo targets the flat floor. A malformed pin cannot be honored
    and fails loudly rather than being silently ignored — ignoring it would assert a cap
    the host does not actually apply, which is the exact blind spot AC-CTX-002 closes.
    """
    raw = os.environ.get(CAP_ENV_VAR)
    if raw is None or raw.strip() == "":
        return CONTEXT_FILE_MAX_CHARS
    try:
        cap = int(raw)
    except ValueError:
        raise AssertionError(
            f"{CAP_ENV_VAR}={raw!r} is not an integer. The tripwire reads an explicit "
            "host-pinned context-file cap from this env var so a LOWER host limit is "
            "visible to CI (docs/02-agents-md-context-budget.md, *What Fails*: 'the cap "
            "is host-dependent'). A non-numeric value cannot be honored and is treated "
            "as a broken pin, not silently ignored. Remedy: export an integer number of "
            f"CHARACTERS (e.g. {CAP_ENV_VAR}=19800), or unset it to fall back to the "
            f"{CONTEXT_FILE_MAX_CHARS}-char flat floor."
        )
    if cap <= 0:
        raise AssertionError(
            f"{CAP_ENV_VAR}={cap} must be a positive number of characters. A non-positive "
            "cap can never hold any instruction file, so the tripwire cannot infer a "
            "meaningful limit from it. Remedy: export a positive integer "
            f"(e.g. {CAP_ENV_VAR}=19800), or unset it to use the "
            f"{CONTEXT_FILE_MAX_CHARS}-char flat floor."
        )
    return cap


def test_agents_md_fits_context_file_cap():
    """AC-CTX-001: AGENTS.md is under the harness context-file cap, in characters."""
    text = AGENTS_MD.read_text(encoding="utf-8")
    n_chars = len(text)
    n_bytes = len(text.encode("utf-8"))
    assert n_chars < CONTEXT_FILE_MAX_CHARS, (
        f"AGENTS.md is {n_chars} chars ({n_bytes} bytes), over the "
        f"{CONTEXT_FILE_MAX_CHARS}-char context-file cap. Every harness loads this file into "
        "each prompt and truncates an oversized one SILENTLY: the head 70% and the tail 20% "
        "survive and the MIDDLE is dropped, so whole sections vanish with no signal at task "
        "time. Remedy: trim AGENTS.md back under the cap (collapsing a rule to one line + a "
        "pointer rather than deleting it — see docs/02-agents-md-context-budget.md), pin a "
        "larger context_file_max_chars on the host, or use a larger-context model."
    )


def test_agents_md_respects_host_pinned_cap():
    """AC-CTX-002: AGENTS.md fits the EFFECTIVE cap, honoring a host-pinned override."""
    cap = _effective_cap()
    text = AGENTS_MD.read_text(encoding="utf-8")
    n_chars = len(text)
    n_bytes = len(text.encode("utf-8"))
    pinned = os.environ.get(CAP_ENV_VAR)
    source = (
        f"pinned by {CAP_ENV_VAR}={pinned!r}"
        if pinned not in (None, "")
        else f"the flat floor (CONTEXT_FILE_MAX_CHARS); export {CAP_ENV_VAR} to pin a lower host cap"
    )
    assert n_chars < cap, (
        f"AGENTS.md is {n_chars} chars ({n_bytes} bytes), over the effective {cap}-char "
        f"context-file cap — {source}. The cap is host state, not repo state: a host "
        "profile that pins a lower context_file_max_chars truncates a file that AC-CTX-001 "
        "passes, and the truncation is silent and mid-file (head 70% + tail 20% survive), "
        "so the Standing Orders and Security sections vanish from the prompt with no signal "
        "at task time (docs/02-agents-md-context-budget.md, *What Fails*). Remedy: trim "
        "AGENTS.md under the EFFECTIVE cap — collapse a rule to one line + a pointer to its "
        "detail rather than deleting it — or raise the host pin so it matches the file."
    )


def test_agents_md_keeps_headroom_floor():
    """AC-CTX-003: AGENTS.md keeps >= HEADROOM_FLOOR_CHARS of headroom under the cap."""
    cap = _effective_cap()
    text = AGENTS_MD.read_text(encoding="utf-8")
    n_chars = len(text)
    headroom = cap - n_chars
    assert headroom >= HEADROOM_FLOOR_CHARS, (
        f"AGENTS.md leaves only {headroom} chars of headroom under the effective {cap}-char "
        f"cap ({n_chars} chars used); the floor is {HEADROOM_FLOOR_CHARS} chars. The file "
        "still fits, but AC-CTX-001 only fires once the cap is ALREADY crossed — and an "
        "overshooting file is truncated in the MIDDLE (head 70% + tail 20% survive), so the "
        "growth that re-crosses the cap silently drops whole sections. This floor fails the "
        "tier BEFORE that happens, reserving room for ~15 lines of prose "
        "(docs/02-agents-md-context-budget.md, *What Fails*: 'headroom is thin'). Remedy: do "
        "not append — collapse the new rule to one line + a pointer to where its detail "
        "already lives, per docs/02 *Resolution*."
    )
