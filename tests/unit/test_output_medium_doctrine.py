"""Unit tier — the output-medium doctrine's own tripwire. IDs: AC-OM-0NN.

Hermetic: a handful of file reads and the stdlib only — no subprocess, no service
import, no transport. The subjects of these tests are tracked documents (the standing
order in AGENTS.md, the immutable raw source, the kb concept page and its index), not
the example service.

Each AC pinpoints a claim the PRD (docs/prd/03-output-medium-doctrine.md) makes about
the doctrine, so a drift in any one of the three layers it spans — the instruction
file, stage-2 raw knowledge, stage-3 confirmed knowledge — turns red here.
"""
import hashlib
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_MD = REPO_ROOT / "AGENTS.md"
RAW_SOURCE = REPO_ROOT / "kb" / "raw" / "articles" / "karpathy-output-medium-escalation.md"
CONCEPT_PAGE = REPO_ROOT / "kb" / "concepts" / "output-medium-escalation.md"
KB_INDEX = REPO_ROOT / "kb" / "index.md"

# The standing order is pointer-based and lives as section 7 of AGENTS.md's Standing
# Orders. Anchor on the exact heading text so a renumber or a rename is caught, then
# slice out only that section's body (up to the next markdown heading of any level) so
# the claims below cannot be satisfied by words that appear elsewhere in the file.
SECTION_HEADING = "### 7. Output-Medium Escalation"


def _section_body(text: str, heading: str) -> str:
    """Return the text from *heading* up to the next markdown heading, or the end."""
    start = text.index(heading) + len(heading)
    rest = text[start:]
    nxt = re.search(r"\n#{1,6} ", rest)
    return rest[: nxt.start()] if nxt else rest


def _frontmatter(text: str) -> str:
    """Return the frontmatter block (between the first pair of '---' fences)."""
    assert text.startswith("---"), "file does not open with a '---' frontmatter fence"
    end = text.index("\n---", 3)
    return text[3:end]


def test_ac_om_001_agents_md_carries_output_medium_standing_order():
    """AC-OM-001: AGENTS.md §7 names the ladder rungs, render → parse, and discardable."""
    text = AGENTS_MD.read_text(encoding="utf-8")
    assert SECTION_HEADING in text, (
        f"AGENTS.md has no '{SECTION_HEADING}' heading. The output-medium escalation "
        "standing order is the pointer-based §7 of Standing Orders (docs/prd/"
        "03-output-medium-doctrine.md SC-om-2); without the exact heading an agent "
        "scanning the standing orders never sees the rule. Remedy: restore the heading "
        "'### 7. Output-Medium Escalation' in AGENTS.md."
    )
    section = _section_body(text, SECTION_HEADING).lower()

    missing = [
        token
        for token in ("prose", "diagram", "html", "explainer video")
        if token not in section
    ]
    if "controlled english" not in section and "asd-ste100" not in section:
        missing.append("controlled English (or ASD-STE100)")
    assert not missing, (
        "AGENTS.md §7 does not name every rung of the medium ladder; missing: "
        f"{missing}. The doctrine's one line is 'prose → STE-style controlled English → "
        "diagram → HTML page → explainer video' (docs/prd/03-output-medium-doctrine.md "
        "SC-om-2). A rung dropped from the standing order is a rung agents will never "
        "climb. Remedy: restore the named rungs in the §7 line of AGENTS.md."
    )

    assert "render → parse" in section, (
        "AGENTS.md §7 does not state the render → parse verification rule (the literal "
        "'render → parse'). The doctrine's constraint is that every rung is code/text "
        "rendered by a deterministic program and verified by parse, never by looking — "
        "this is what makes the upper rungs usable to a non-visual engine. Remedy: keep "
        "'verified by render → parse' in the §7 line of AGENTS.md."
    )

    assert "discardable" in section, (
        "AGENTS.md §7 does not carry the discardable-artifact rule (the word "
        "'discardable'). The doctrine treats large custom artifacts as built once in "
        "scratchpads/ and never cited (docs/prd/03-output-medium-doctrine.md SC-om-2); "
        "without the word an agent has no cue to keep them out of tracked evidence. "
        "Remedy: restore '**discardable**' in the §7 line of AGENTS.md."
    )

    assert "funnel rule 6" in section, (
        "AGENTS.md §7 does not cite funnel rule 6, the rule that 'scratchpads/ is never "
        "cited'. The discardable-artifact rule is only coherent next to its pointer — "
        "the artifact may be built in scratchpads/ precisely because funnel rule 6 "
        "forbids citing it. Remedy: keep the '(funnel rule 6)' pointer in the §7 line "
        "of AGENTS.md."
    )


def test_ac_om_002_raw_source_sha256_matches_frontmatter():
    """AC-OM-002: the raw source body's sha256 equals its frontmatter sha256 value."""
    assert RAW_SOURCE.is_file(), (
        f"raw source missing at {RAW_SOURCE.relative_to(REPO_ROOT)}. Funnel stage 2 "
        "(kb/raw/) is the immutable provenance for the doctrine; without the file the "
        "PRD's SC-om-3 has nothing to verify against. Remedy: re-ingest the source."
    )
    text = RAW_SOURCE.read_text(encoding="utf-8")
    fm = _frontmatter(text)

    match = re.search(r"^sha256:\s*([0-9a-f]{64})\s*$", fm, re.MULTILINE)
    assert match, (
        "raw source frontmatter has no well-formed 'sha256: <64 lowercase hex>' line. "
        "The frontmatter sha256 is the ingest's integrity record; without it a later "
        "edit to the body is undetectable (funnel rule 3: kb/raw/ is add-or-archive). "
        "Remedy: record the body hash in the frontmatter."
    )
    recorded = match.group(1)

    # Convention established at ingest: the body is everything after the closing '---'
    # fence, with the separator blank line(s) stripped. The hash is taken over that
    # lstripped text, so the exact bytes are "the article", not the fence spacing.
    body = text[text.index("\n---", 3) + 4 :].lstrip("\n")
    actual = hashlib.sha256(body.encode("utf-8")).hexdigest()

    assert actual == recorded, (
        f"raw source body sha256 {actual} does not match the frontmatter sha256 "
        f"{recorded}. The body has been edited since ingest — which violates funnel "
        "rule 3 (kb/raw/ is append-or-archive, never edited in place). Remedy: restore "
        "the original body, or archive this file to kb/_archive/ and add a corrected "
        "raw source in its place, then update the frontmatter hash."
    )


def test_ac_om_003_concept_page_indexed_and_cites_raw():
    """AC-OM-003: the concept page exists, cites the raw source, and is indexed twice."""
    assert CONCEPT_PAGE.is_file(), (
        f"concept page missing at {CONCEPT_PAGE.relative_to(REPO_ROOT)}. Stage 3 "
        "(kb/) is the confirmed-knowledge layer the PRD grounds in; without the page "
        "the PRD's SC-om-4 is unsupported. Remedy: regenerate kb/ with the llm-wiki "
        "skill after the raw source is in place."
    )
    page = CONCEPT_PAGE.read_text(encoding="utf-8")
    fm = _frontmatter(page)

    raw_rel = "raw/articles/karpathy-output-medium-escalation.md"
    assert "sources:" in fm and raw_rel in fm, (
        f"concept page frontmatter does not cite '{raw_rel}' in its sources:. Every "
        "stage-3 page must declare the stage-2 raw knowledge it was synthesized from "
        "(funnel rule 2: grounding direction is downward). Remedy: add the raw source "
        "to the page's 'sources:' frontmatter."
    )

    index = KB_INDEX.read_text(encoding="utf-8")
    concept_row = "concepts/output-medium-escalation.md"
    assert concept_row in index, (
        f"kb/index.md has no Concepts row pointing at '{concept_row}'. The index is "
        "the stage-3 catalog agents read first; an unindexed concept page is invisible "
        "(dry-run: run /llm-wiki ./kb/ to regenerate index.md). Remedy: regenerate or "
        "repair the index."
    )
    assert raw_rel in index, (
        f"kb/index.md has no Raw Sources row pointing at '{raw_rel}'. Both halves of "
        "the provenance chain — the synthesized page and the raw it cites — must be "
        "cataloged. Remedy: regenerate kb/index.md so the raw source and its concept "
        "page both appear."
    )
