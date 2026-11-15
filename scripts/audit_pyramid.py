#!/usr/bin/env python3
"""Potato-pyramid gate — layers 1-3 of Lauren Tan's inverse pyramid.

Stdlib-only. Reads the repo's tracked Python under service/ and scripts/ (git
ls-files, so untracked scratchpads never fail the gate) and checks the three
deterministic foundations that sit under prose:

  1. codebase     — the AGENTS.md §3 banned patterns: a subprocess shell
                    argument switched on, a requests call with no timeout= on
                    the same line, a bare except:, dynamic eval or exec.
  2. static       — the comment budget (comments/(comments+code) over
                    --max-comment-ratio, every scanned file), a run of more than
                    --max-comment-block consecutive comment lines, a TODO or
                    FIXME or XXX with no ticket reference, commented-out code.
  3. verification — every module stem is named somewhere under tests/.

Line-based regex over the source text, plus tokenize for the comment/code
split: documented false-positive risk, no AST and no fixer. The config files
in EXTRA_FILES (.env.example, .gitignore) get the same two comment rules,
counted line by line because no tokenizer applies to them. Prose rules
(layer 4: STE, docs doctrine) belong to other scripts.

Exit 0 when all three foundations are green, else 1 with every finding printed
as 'file:line: rule-id first 80 chars'. Keep it dumb and readable.
"""
import argparse
import io
import json
import re
import subprocess
import sys
import tokenize
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCAN_DIRS = ("service", "scripts")

BANNED = (
    ("SHELL-TRUE", re.compile(r"\bshell\s*=\s*True")),
    ("BARE-EXCEPT", re.compile(r"^\s*except\s*:")),
    ("DYNAMIC-EVAL", re.compile(r"\b(?:eval|exec)\s*\(\s*[^'\"\s)]")),
)
REQUEST_CALL = re.compile(r"\brequests\.[A-Za-z_]\w*\(")
TODO = re.compile(r"^(?:TODO|FIXME|XXX)\b")
TICKET = re.compile(r"https?://|#\d+|\b[A-Z][A-Z0-9]+-\d+\b")
DEAD_CODE = re.compile(r"^(?:if|for|while|return|import|from|def|class)\b|^[a-z_][\w.]*\s*=|^\w+\(")
SKIP_TOKENS = {
    tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
    tokenize.DEDENT, tokenize.ENCODING, tokenize.ENDMARKER,
}
MIN_LINES_FOR_RATIO = 0
EXTRA_FILES = (".env.example", ".gitignore")


def read_text(root, rel):
    """Return one scanned file's text, insensitive to stray bytes."""
    return (root / rel).read_text(encoding="utf-8", errors="replace")


def list_sources(root):
    """Return .py paths under service/ and scripts/, relative to root.

    git ls-files keeps untracked files out of the gate. A tree that is not a
    repository (the tests build one) falls back to a walk of the same dirs.
    """
    try:
        out = subprocess.run(
            ["git", "ls-files", "--", *SCAN_DIRS],
            cwd=root, capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        out = "\n".join(
            str(path.relative_to(root))
            for name in SCAN_DIRS if (root / name).is_dir()
            for path in sorted((root / name).rglob("*.py"))
        )
    return [Path(name) for name in out.splitlines()
            if name.endswith(".py") and "__pycache__" not in name]


def finding(rel, number, rule, detail):
    """Format one finding: 'file:line: rule-id first 80 chars'."""
    return f"{rel}:{number}: {rule} {detail.strip()[:80]}"


def scan_constraints(root, files):
    """Foundation 1 — banned patterns, one line-based pass per file."""
    findings = []
    for rel in files:
        for number, line in enumerate(read_text(root, rel).splitlines(), start=1):
            for rule, pattern in BANNED:
                if pattern.search(line):
                    findings.append(finding(rel, number, rule, line))
            if REQUEST_CALL.search(line) and "timeout=" not in line:
                findings.append(finding(rel, number, "NO-TIMEOUT", line))
    return findings


def comment_budget(rel, comments, code, max_ratio):
    """The COMMENT-BUDGET finding for a comment/code line count, if over.

    Every file is budgeted, whatever its size. An empty file (0 comments, 0
    code lines) has no ratio to exceed and stays silent.
    """
    total = comments + code
    if total < MIN_LINES_FOR_RATIO or not total or comments / total <= max_ratio:
        return []
    return [finding(rel, 0, "COMMENT-BUDGET",
                    f"{comments / total:.0%} comment ratio over "
                    f"{max_ratio:.0%} ({comments}/{total})")]


def scan_consecutive(rel, comment_lines, max_block):
    """One MAX-CONSEC finding per run of more than max_block comment lines."""
    findings, run = [], []
    for number in sorted(comment_lines) + [None]:
        if number is not None and (not run or number == run[-1] + 1):
            run.append(number)
            continue
        if len(run) > max_block:
            findings.append(finding(rel, run[0], "MAX-CONSEC",
                                    f"{len(run)} consecutive comment lines (budget {max_block})"))
        run = [] if number is None else [number]
    return findings


def scan_comments(rel, text, max_ratio, max_block):
    """Foundation 2 for one .py file — (comment lines, code lines, findings)."""
    code_lines, comments = set(), []
    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.COMMENT:
                comments.append(token)
            elif token.type not in SKIP_TOKENS:
                code_lines.add(token.start[0])
    except (tokenize.TokenError, IndentationError):
        return 0, 0, []
    # A comment trailing a code line is not a comment line: that line is code.
    comment_lines = {token.start[0] for token in comments} - code_lines
    findings = comment_budget(rel, len(comment_lines), len(code_lines), max_ratio)
    findings.extend(scan_consecutive(rel, comment_lines, max_block))
    for token in comments:
        body = token.string.lstrip("#").strip()
        if TODO.match(body) and not TICKET.search(body):
            findings.append(finding(rel, token.start[0], "TODO-UNLINKED", body))
        elif DEAD_CODE.match(body) and not body.endswith((".", "!", "?")):
            findings.append(finding(rel, token.start[0], "DEAD-CODE-COMMENT", body))
    return len(comment_lines), len(code_lines), findings


def scan_text_comments(rel, text, max_ratio, max_block):
    """Foundation 2 for a non-.py file — (comment lines, code lines, findings).

    No tokenizer applies to a config file, so the split is line-based: a comment
    line's lstrip starts with '#', any other non-blank line is code, and blanks
    count on neither side.
    """
    comment_lines, code = set(), 0
    for number, line in enumerate(text.splitlines(), start=1):
        body = line.lstrip()
        if not body:
            continue
        if body.startswith("#"):
            comment_lines.add(number)
        else:
            code += 1
    findings = comment_budget(rel, len(comment_lines), code, max_ratio)
    findings.extend(scan_consecutive(rel, comment_lines, max_block))
    return len(comment_lines), code, findings


def scan_verification(root, files):
    """Foundation 3 — every module stem must appear somewhere under tests/.

    Substring match on the concatenated test sources, so a stem named only in a
    test docstring still counts. Loose on purpose; it catches the orphan module.
    """
    tests = "".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted((root / "tests").rglob("*.py"))
    )
    findings = []
    for rel in files:
        stem = Path(rel).stem
        if stem == "__init__" or stem in tests:
            continue
        findings.append(f"{rel}:0: UNVERIFIED-MODULE no test references '{stem}'")
    return findings


def build_parser():
    parser = argparse.ArgumentParser(
        prog="audit_pyramid.py",
        description="Gate the deterministic foundations: constraints, static analysis, verification.",
    )
    parser.add_argument("--max-comment-ratio", type=float, default=0.20,
                        help="per-file comment budget, every scanned file (default: 0.20)")
    parser.add_argument("--max-comment-block", type=int, default=3,
                        help="max consecutive comment lines, per file (default: 3)")
    parser.add_argument("--json", action="store_true",
                        help="emit {foundations, totals} instead of human sections")
    return parser


def main(argv=None, root=None):
    args = build_parser().parse_args(argv)
    base = Path(root) if root else REPO_ROOT
    py_files = list_sources(base)
    extras = [Path(name) for name in EXTRA_FILES if (base / name).is_file()]
    files = py_files + extras

    constraint = scan_constraints(base, py_files)
    static, comment_total, code_total = [], 0, 0
    for rel in files:
        scanner = scan_comments if rel.suffix == ".py" else scan_text_comments
        comments, code, findings = scanner(rel, read_text(base, rel),
                                           args.max_comment_ratio, args.max_comment_block)
        comment_total += comments
        code_total += code
        static.extend(findings)
    verification = scan_verification(base, py_files)

    sections = (
        ("1-codebase-constraints", constraint),
        ("2-static-analysis", static),
        ("3-verification", verification),
    )
    total = len(constraint) + len(static) + len(verification)
    ratio = comment_total / (comment_total + code_total) if comment_total + code_total else 0.0

    if args.json:
        print(json.dumps({
            "foundations": [{"foundation": name, "findings": items} for name, items in sections],
            "totals": {
                "files": len(files), "findings": total,
                "comment_lines": comment_total, "code_lines": code_total,
                "comment_ratio": round(ratio, 4),
            },
        }, indent=2))
    else:
        for name, items in sections:
            print(f"== foundation {name} ==")
            for item in items or [f"OK ({len(files)} files scanned)"]:
                print(item)
        print(f"comment ratio: {comment_total}c/{code_total}k = {ratio:.1%} "
              f"(budget {args.max_comment_ratio:.0%} per file)")
        print(f"findings: {total}")
        if not total:
            print(f"OK: 3 foundations green ({len(files)} files, ratio {ratio:.1%})")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
