#!/usr/bin/env python3
"""STE-style audit — rung 1 of the output-medium doctrine (docs/prd/05-ste-audit.md).

Stdlib-only. Reads markdown prose — code fences, tables, headings, list markers and
footnote markers are stripped — splits it into sentences, and measures the two rules
that are machine-checkable without the ASD-STE100 dictionary (never vendored; it is
ASD's copyright): the sentence-length cap and passive-voice constructions.

Exit 0 when the share of sentences within the length cap is >= --threshold percent,
else exit 1 with every over-limit offender printed as 'file: [Nw] first 100 chars'.

No config files, no scoring beyond the two rules. Keep it dumb and readable.
"""
import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Sentences end at [.;:] + whitespace — except after a protected token: the common
# abbreviations and the section form "§ N.", where the period is not a sentence end.
PROTECTED_BEFORE_PERIOD = re.compile(
    r"(?:\b(?:e\.g|i\.e|vs|etc|cf|al|no|fig|dr|mr|mrs|ms|st|inc|ltd|jr|sr)|\§\s*\d+)\.$",
    re.IGNORECASE,
)
# be-verb + past participle. Word-boundaried and case-insensitive, per the PRD.
PASSIVE = re.compile(r"\b(is|are|was|were|be|been|being)\s+\w+(ed|en)\b", re.IGNORECASE)


def strip_markdown(text):
    """Return prose lines only: code fences, tables, headings and markers removed."""
    lines, in_fence = [], False
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith("|"):
            continue
        line = re.sub(r"^\s*>\s?", "", raw)              # blockquote marker
        line = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line)  # list marker
        line = re.sub(r"\[\^?\d+\]", "", line)           # footnote reference
        if line.strip():
            lines.append(line.strip())
    return lines


def split_sentences(lines):
    """Split prose lines into sentences, protecting common abbreviations."""
    out = []
    for line in lines:
        start = 0
        for match in re.finditer(r"[.;:]\s+", line):
            end = match.start() + 1
            if PROTECTED_BEFORE_PERIOD.search(line[:end]):
                continue
            chunk = line[start:end].strip()
            if chunk:
                out.append(chunk)
            start = match.end()
        tail = line[start:].strip()
        if tail:
            out.append(tail)
    return out


def measure(sentences, max_words):
    """Return (over-limit sentences, longest word count, passive-voice count)."""
    over = [s for s in sentences if len(s.split()) > max_words]
    longest = max((len(s.split()) for s in sentences), default=0)
    passive = sum(1 for s in sentences if PASSIVE.search(s))
    return over, longest, passive


def collect_default_inputs():
    """Return (base, files) for docs/*.md + README.md, anchored at the repo root."""
    base = REPO_ROOT if (REPO_ROOT / "docs").is_dir() else Path.cwd()
    files = sorted(base.glob("docs/*.md"))
    readme = base / "README.md"
    if readme.is_file():
        files.append(readme)
    return base, files


def build_parser():
    parser = argparse.ArgumentParser(
        prog="audit-ste.py",
        description="Audit markdown prose for STE-style sentence-length and passive-voice limits.",
    )
    parser.add_argument(
        "inputs", nargs="*", metavar="FILE",
        help="markdown files to audit (default: docs/*.md and README.md)",
    )
    parser.add_argument(
        "--max-words", type=int, default=25,
        help="descriptive sentence cap in words (default: 25)",
    )
    parser.add_argument(
        "--threshold", type=float, default=80.0,
        help="minimum share of within-limit sentences, in percent (default: 80)",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="print the per-file table even on success",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    base, default_files = collect_default_inputs()
    # Explicit inputs resolve against base (absolute paths pass through); empty -> defaults.
    files = [base / name for name in args.inputs] or default_files
    missing = [str(path) for path in files if not path.is_file()]
    if missing:
        for name in missing:
            print(f"error: input file not found: {name}", file=sys.stderr)
        return 1

    total = within = 0
    rows, offenders = [], []
    for path in files:
        sentences = split_sentences(strip_markdown(path.read_text(encoding="utf-8")))
        over, longest, passive = measure(sentences, args.max_words)
        total += len(sentences)
        within += len(sentences) - len(over)
        rows.append((path, len(sentences), len(over), longest, passive))
        offenders.extend(f"{path}: [{len(s)}w] {s[:100]}" for s in over)

    share = (100.0 * within / total) if total else 100.0
    ok = share >= args.threshold

    if args.verbose or not ok:
        print(f"{'file':<44} {'sent':>5} {'over':>5} {'max':>5} {'passive':>7}")
        for path, count, over, longest, passive in rows:
            print(f"{str(path):<44} {count:>5} {over:>5} {longest:>5} {passive:>7}")
        print(f"within-limit: {within}/{total} = {share:.1f}% (threshold {args.threshold:g}%)")

    if not ok:
        print(f"\nOffenders (over {args.max_words} words):")
        for line in offenders:
            print(line)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
