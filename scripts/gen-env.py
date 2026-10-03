#!/usr/bin/env python3
"""Generate .env from .env.example — a fresh copy or a value-carrying update."""
import argparse
import re
import sys
from pathlib import Path

TEMPLATE_NAME = ".env.example"
ENV_NAME = ".env"
ENV_NEW_NAME = ".env.new"
_KEY_LINE = re.compile(r"^(?:export[ \t]+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
_KEY_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")


class _ArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that exits 1 (not 2) on usage errors."""

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(1, f"{self.prog}: error: {message}\n")


def parse_env(text):
    """Map each KEY in .env text to its verbatim value after the first '='.

    Blank and comment lines are ignored; an optional 'export ' prefix is
    stripped; the value keeps quotes and trailing characters unchanged.
    """
    values = {}
    for line in text.splitlines():
        body = line.lstrip()
        if not body or body.startswith("#"):
            continue
        if body.startswith("export "):
            body = body[len("export "):].lstrip()
        eq = body.find("=")
        if eq <= 0:
            continue
        key = body[:eq].strip()
        if not _KEY_NAME.match(key):
            continue
        values[key] = body[eq + 1:]
    return values


def render_update(template_text, values):
    """Return (.env.new text, dropped keys).

    Each template line is kept verbatim; a KEY= line whose key exists in
    values gets that value spliced in after the first '='. Keys in values but
    absent from the template are dropped and returned by name.
    """
    lines = []
    used = set()
    for line in template_text.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        match = _KEY_LINE.match(body)
        if match:
            key = match.group(1)
            used.add(key)
            if key in values:
                lines.append(body[: body.index("=") + 1] + values[key] + ending)
                continue
        lines.append(line)
    dropped = [key for key in values if key not in used]
    return "".join(lines), dropped


def write_fresh(force):
    """Write .env as a byte-identical copy of the template."""
    template = Path(TEMPLATE_NAME)
    target = Path(ENV_NAME)
    if not template.is_file():
        print(f"error: {TEMPLATE_NAME} not found", file=sys.stderr)
        return 1
    if target.exists() and not force:
        print(f"error: {ENV_NAME} exists; use --force to overwrite", file=sys.stderr)
        return 1
    target.write_bytes(template.read_bytes())
    print(f"wrote {ENV_NAME}")
    return 0


def write_update(force):
    """Write .env.new from the template, carrying values from the existing .env."""
    template = Path(TEMPLATE_NAME)
    source = Path(ENV_NAME)
    target = Path(ENV_NEW_NAME)
    if not template.is_file():
        print(f"error: {TEMPLATE_NAME} not found", file=sys.stderr)
        return 1
    if not source.is_file():
        print(f"error: {ENV_NAME} not found; nothing to carry", file=sys.stderr)
        return 1
    if target.exists() and not force:
        print(f"error: {target} exists; use --force to overwrite", file=sys.stderr)
        return 1
    values = parse_env(source.read_bytes().decode("utf-8"))
    new_text, dropped = render_update(template.read_bytes().decode("utf-8"), values)
    target.write_bytes(new_text.encode("utf-8"))
    print(f"wrote {ENV_NEW_NAME}")
    if dropped:
        print(f"dropped keys (not in {TEMPLATE_NAME}): " + ", ".join(dropped))
    return 0


def build_parser():
    parser = _ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fresh", action="store_true",
                      help="write .env as a copy of .env.example")
    mode.add_argument("--update", action="store_true",
                      help="write .env.new from .env.example, carrying .env values")
    parser.add_argument("--force", action="store_true",
                        help="overwrite an existing target")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.fresh:
        return write_fresh(args.force)
    return write_update(args.force)


if __name__ == "__main__":
    sys.exit(main())
