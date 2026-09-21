"""Unit tier — the doctrine's own tripwire. IDs: AC-CTX-0NN.

Hermetic: one file read and the stdlib only — no subprocess, no service import, no
transport. The subject of the test is a tracked document, not the example service.
"""
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
