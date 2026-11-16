#!/usr/bin/env python3
"""File-size audit — the per-file cap in docs/prd/10-file-size-audit.md.

Stdlib-only. Measures every git-tracked file with os.path.getsize and fails
when one exceeds --max-kb (20 KB default, 20480 bytes). The cap is inclusive:
a file of exactly the cap passes, one byte more fails. The scope is tracked
only, so an untracked scratchpad never fails the gate, and a symlink or
gitlink is skipped — a link's own size says nothing about what it points at.

Positional FILE arguments measure exactly those paths instead of the tracked
scope: absolute paths pass through, relative ones resolve against the base
directory. That is how the unit tier drives a synthetic 20481-byte file
without writing anything inside the repo. A file that will not stat is
reported as unreadable on stderr and counted as 0 bytes, never raised.

Exit 0 when every measured file is within the cap, else 1 with each offender
printed as 'path: [N bytes] over cap M'. Keep it dumb and readable.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MAX_KB = 20.0
MAX_TABLE_ROWS = 20
SKIP_DIRS = {".git", "__pycache__"}


def limit_bytes(max_kb):
    """Return the inclusive byte cap for a kilobyte budget."""
    return int(max_kb * 1024)


def _git_paths(base):
    """Return the tracked paths git reports at base, or None if git fails."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=base, capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError, UnicodeDecodeError):
        return None
    return [name for name in out.split("\0") if name]


def _is_regular(path):
    """True for a real file — a symlink or a gitlink directory is not one."""
    return path.is_file() and not path.is_symlink()


def _walk_paths(base):
    """Fallback scope for a tree that is not a repository: a plain walk."""
    keep = []
    for path in sorted(base.rglob("*")):
        if SKIP_DIRS.intersection(path.relative_to(base).parts):
            continue
        if _is_regular(path):
            keep.append(path.relative_to(base).as_posix())
    return keep


def list_tracked(base):
    """Return (display, path) pairs for the default scope.

    git ls-files keeps untracked files out of the gate. A tree that is not a
    repository (the tests build one) falls back to a walk of the same
    directory. Both branches drop symlinks and gitlinks.
    """
    names = _git_paths(base)
    if names is None:
        names = _walk_paths(base)
    return [(name, base / name) for name in names if _is_regular(base / name)]


def measure(path):
    """Return (bytes, unreadable) for one file, without ever raising."""
    try:
        return os.path.getsize(path), False
    except OSError:
        return 0, True


def build_parser():
    parser = argparse.ArgumentParser(
        prog="audit-size.py",
        description="Fail when a git-tracked file exceeds the size cap.",
    )
    parser.add_argument(
        "inputs", nargs="*", metavar="FILE",
        help="files to measure (default: every git-tracked file)",
    )
    parser.add_argument(
        "--max-kb", type=float, default=DEFAULT_MAX_KB,
        help="per-file cap in KB, where 20 KB means 20480 bytes "
             "(default: 20)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="emit one JSON object instead of the table and findings",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="print the per-file table even when nothing is over",
    )
    return parser


def main(argv=None, root=None):
    args = build_parser().parse_args(argv)
    base = Path(root) if root else REPO_ROOT
    cap = limit_bytes(args.max_kb)

    if args.inputs:
        pairs = [(str(base / Path(name)), base / Path(name))
                 for name in args.inputs]
        missing = [name for name, path in pairs if not path.is_file()]
        for name in missing:
            print(f"error: input file not found: {name}", file=sys.stderr)
        if missing:
            return 1
        label = "files"
    else:
        pairs = list_tracked(base)
        label = "tracked files"

    rows = []
    for name, path in pairs:
        size, unreadable = measure(path)
        if unreadable:
            print(f"warning: unreadable file: {name}", file=sys.stderr)
        rows.append((name, size, size > cap))
    rows.sort(key=lambda row: (-row[1], row[0]))
    over = [row for row in rows if row[2]]
    largest, largest_name = (rows[0][1], rows[0][0]) if rows else (0, "-")
    total_bytes = sum(row[1] for row in rows)

    if args.json:
        print(json.dumps({
            "max_kb": args.max_kb,
            "max_bytes": cap,
            "totals": {
                "files": len(rows), "over": len(over),
                "largest": largest, "largest_path": largest_name,
                "total_bytes": total_bytes,
            },
            "files": [{"file": name, "bytes": size, "over": flag}
                      for name, size, flag in rows],
        }, indent=2))
        return 1 if over else 0

    if args.verbose or over:
        print(f"{'file':<56} {'bytes':>8} {'over':>5}")
        for name, size, flag in rows[:MAX_TABLE_ROWS]:
            print(f"{name:<56} {size:>8} {'yes' if flag else 'no':>5}")
        if len(rows) > MAX_TABLE_ROWS:
            print(f"... {len(rows) - MAX_TABLE_ROWS} more files not shown")
        print(f"cap: {cap} bytes  files: {len(rows)}  over: {len(over)}")

    if over:
        print(f"\nOver cap ({cap} bytes):")
        for name, size, _ in over:
            print(f"{name}: [{size} bytes] over cap {cap}")
    else:
        print(f"OK: {len(rows)} {label} within {cap} bytes "
              f"(largest {largest} B, {largest_name})")
    print(f"largest: {largest} bytes  {largest_name}")
    return 1 if over else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(1)
