#!/usr/bin/env python3
"""Char-per-line audit — the 80-column guard for prose and source text.

Stdlib-only. Measures the width of every line that carries prose: markdown
under docs/, plus README.md and AGENTS.md. Markdown is stripped before it is
measured — code fences, tables, headings, blockquote markers, list markers
and footnote references never count — so a wide table or a long URL in a
fence is exempt by construction. Any other file type is measured raw,
character for character, because a .py or a .yml has no markdown exemptions
to honour.

Strict by default: it exits 1 when any measured line is over --max-chars, so
the cap is a hard gate and a reflow cannot quietly regress. --advisory is the
staged-adoption escape hatch — it prints the same report and exits 0.

One exemption is structural rather than stylistic. An over-cap measured line
carrying a whitespace-delimited token wider than the cap — a long URL, a bare
link — is exempt, because no whitespace wrap can bring that token under the
cap: it classifies as `unbreakable` and never affects the exit code. A line of
ordinary words is always an offender: every token fits, so a wrap fixes it.

Offenders print as 'file:line: [N chars] first 80 chars', capped at 20
lines. No config files, no fixer, no reflow. Keep it dumb and readable.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKDOWN = (".md", ".markdown")
# The two entry documents outside docs/ that the funnel treats as prose too.
EXTRA_FILES = ("README.md", "AGENTS.md")
MAX_SHOWN = 20
# Markers come off a line only after it survived the fence, table and skip.
BLOCKQUOTE = re.compile(r"^\s*>\s?")
LIST_MARKER = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
FOOTNOTE = re.compile(r"\[\^?\d+\]")


def prose_lines(text):
    """Return (line number, prose text) for markdown, exemptions removed."""
    out, in_fence = [], False
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith("|"):
            continue
        line = BLOCKQUOTE.sub("", raw)
        line = LIST_MARKER.sub("", line)
        line = FOOTNOTE.sub("", line)
        if line.strip():
            out.append((number, line.strip()))
    return out


def raw_lines(text):
    """Return (line number, raw line) for a non-markdown file — no cuts."""
    return list(enumerate(text.splitlines(), start=1))


def collect_default_inputs():
    """Return (base, files): docs/**/*.md plus README.md and AGENTS.md.

    Symlinks are skipped, so the CLAUDE.md alias of AGENTS.md is never counted
    twice. Nothing outside docs/ is scanned except those two entry documents.
    """
    base = REPO_ROOT if (REPO_ROOT / "docs").is_dir() else Path.cwd()
    files = [path for path in sorted((base / "docs").rglob("*.md"))
             if path.is_file() and not path.is_symlink()]
    for name in EXTRA_FILES:
        path = base / name
        if path.is_file() and not path.is_symlink():
            files.append(path)
    return base, files


def display_path(path, base):
    """Return path relative to base when it lives under it, else as given."""
    try:
        return str(Path(path).relative_to(base))
    except ValueError:
        return str(path)


def classify(body, max_chars):
    """Return 'ok', 'over' or 'unbreakable' for one measured line.

    An over-cap line is exempt when it carries a token wider than the cap —
    a long URL — because no whitespace wrap can bring that token under the
    cap, so the line is 'unbreakable'. A line of ordinary words is always an
    offender: every token fits, so wrapping can fix it.
    """
    if len(body) <= max_chars:
        return "ok"
    widest = max(len(token) for token in body.split())
    return "unbreakable" if widest > max_chars else "over"


def scan_file(path, max_chars, base):
    """Return (row, over, unbreakable) for one file.

    ``over`` holds the wrap-able offenders, ``unbreakable`` the lines carrying
    a token the cap cannot reach. Only ``over`` is a finding.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    reader = prose_lines if path.suffix.lower() in MARKDOWN else raw_lines
    measured = reader(text)
    over = [(number, body) for number, body in measured
            if classify(body, max_chars) == "over"]
    unbreakable = [(number, body) for number, body in measured
                   if classify(body, max_chars) == "unbreakable"]
    widths = [len(body) for _, body in measured]
    row = {
        "file": display_path(path, base),
        "lines": len(measured),
        "over": len(over),
        "worst": max(widths, default=0),
        "unbreakable": len(unbreakable),
    }
    return row, over, unbreakable


def offender_text(path, number, body):
    """Format one offender: 'file:line: [N chars] first 80 chars'."""
    return f"{path}:{number}: [{len(body)} chars] {body[:80]}"


def print_table(rows):
    """Print the per-file table: one row per file, worst width last."""
    print(f"{'file':<44} {'lines':>6} {'over':>6} {'worst':>6}")
    for row in rows:
        print(f"{row['file']:<44} {row['lines']:>6} {row['over']:>6} "
              f"{row['worst']:>6}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="audit-chars.py",
        description="Fail when a measured source line is over --max-chars.",
    )
    parser.add_argument(
        "inputs", nargs="*", metavar="FILE",
        help="files to audit (default: docs/**/*.md + README.md + AGENTS.md)",
    )
    parser.add_argument(
        "--max-chars", type=int, default=80,
        help="maximum measured line width in characters (default: 80)",
    )
    parser.add_argument(
        "--advisory", action="store_true",
        help="report the offenders without failing (default: exit 1)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="emit one JSON object instead of the human report",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="print the per-file table even when nothing is over",
    )
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    base, default_files = collect_default_inputs()
    # Explicit inputs resolve against base (absolute paths pass through).
    files = [base / name for name in args.inputs] or default_files
    missing = [str(path) for path in files if not path.is_file()]
    if missing:
        for name in missing:
            print(f"error: input file not found: {name}", file=sys.stderr)
        return 1

    rows, offenders, unbreakable = [], [], []
    for path in files:
        row, over, lone = scan_file(path, args.max_chars, base)
        rows.append(row)
        offenders.extend((row["file"], number, body)
                         for number, body in over)
        unbreakable.extend(lone)

    lines = sum(row["lines"] for row in rows)
    over_total = len(offenders)
    lone_total = len(unbreakable)
    worst = max((row["worst"] for row in rows), default=0)
    fail = over_total > 0 and not args.advisory
    share = (100.0 * over_total / lines) if lines else 0.0

    if args.json:
        print(json.dumps({
            "max_chars": args.max_chars,
            "advisory": bool(args.advisory),
            "totals": {"files": len(rows), "lines": lines,
                       "over": over_total, "worst": worst,
                       "unbreakable": lone_total},
            "files": rows,
        }, indent=2))
        return 1 if fail else 0

    if args.verbose or over_total:
        print_table(rows)
    print(f"lines over {args.max_chars} chars: {over_total}/{lines} = "
          f"{share:.1f}%")
    if lone_total:
        print(f"unbreakable: {lone_total} "
              f"(token wider than {args.max_chars})")
    if not over_total:
        note = (f"; {lone_total} unbreakable" if lone_total else "")
        print(f"OK: every measured line is within {args.max_chars} chars "
              f"({lines} lines){note}")
        return 0
    print(f"\noffenders (over {args.max_chars} chars):")
    for path, number, body in offenders[:MAX_SHOWN]:
        print(offender_text(path, number, body))
    if over_total > MAX_SHOWN:
        print(f"... {over_total - MAX_SHOWN} more")
    if args.advisory:
        print("advisory only: --advisory reports without failing; drop it "
              "to hold the cap")
    return 1 if fail else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(1)
