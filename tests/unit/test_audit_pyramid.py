"""Unit tier — the potato-pyramid gate. IDs: AC-PYR-0NN (scripts/audit_pyramid.py).

Hermetic: the auditor is loaded by path and driven in-process with
main(argv, root=tmp_path) over a synthetic tree — no network, no service import.
AC-PYR-001 proves every foundation fires on known slop; AC-PYR-002 proves a clean
tree stays green; AC-PYR-003 pins the --json contract; AC-PYR-004 runs the CLI on
the repo itself, so the unit tier holds the gate; AC-PYR-005 pins the exact
MAX-CONSEC run and its budget override; AC-PYR-006 proves the real-repo totals
include EXTRA_FILES; AC-PYR-007 proves the comment budget applies to every
scanned file, so a tiny over-budget file is no longer exempt.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "audit_pyramid.py"

# Every foundation fires at least once here: banned patterns, an unlinked TODO,
# a commented-out def, an over-budget comment block (13 comment / 13 code lines,
# a 10-line run at line 24), and a 3-line run at line 35 that must stay silent
# along with the linked TODO.
SLOPPY = '''"""Sloppy module — every foundation fires at least once."""
import subprocess


def run(cmd):
    return subprocess.run(cmd, shell=True)


def fetch(url):
    return requests.get(url)


def parse(text):
    return eval(text)


def swallow():
    try:
        return 1
    except:
        return 0


# TODO tidy this up
# def old_helper(x):
#     return x
# legacy note one, kept for the ratio.
# legacy note two, kept for the ratio.
# legacy note three, kept for the ratio.
# legacy note four, kept for the ratio.
# legacy note five, kept for the ratio.
# legacy note six, kept for the ratio.
# TODO ABC-123 is the linked one.

# short prose note one.
# short prose note two.
# short prose note three.
'''

# A config template whose comment block is over budget: the line-based path
# counts it exactly like code, so 20 of 23 lines is 87%.
FAT_ENV = "".join(f"# legacy note {number}.\n" for number in range(1, 21)) + (
    "APP_NAME=myproject\nDEBUG=false\nPORT=8000\n")

CLEAN = '''"""Helper module — referenced by the unit tier and free of slop."""


def greet(name):
    return f"hello {name}"
'''

# A 5-counted-line module that is nonetheless over budget: 2 comment lines
# against 3 code lines is 40%, so the budget reaches below any size floor.
TINY_OVER = """# one.
# two.
def add(a, b):
    return a
VALUE = add(1, 2)
"""

# The same shape under budget: 2 comment lines against 10 code lines is 17%.
TINY_UNDER = "# one.\n# two.\n" + "".join(f"VALUE_{number} = {number}\n" for number in range(10))


def _load_audit_pyramid():
    """Load scripts/audit_pyramid.py by path (it is a CLI, not a package)."""
    spec = importlib.util.spec_from_file_location("audit_pyramid", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(root, relative, text):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _sloppy_tree(root):
    """A tree where all three foundations must fail, plus one linked TODO."""
    _write(root, "service/pkg/sloppy.py", SLOPPY)
    _write(root, "scripts/orphan.py", "VALUE = 1\n")
    _write(root, "tests/unit/test_orphan.py", '"""Mentions nothing useful."""\n')
    _write(root, ".env.example", FAT_ENV)


def _clean_tree(root):
    """A tree where all three foundations pass."""
    _write(root, "service/pkg/helper.py", CLEAN)
    _write(root, "tests/unit/test_helper.py", '"""Covers helper.greet."""\n')


pyramid = _load_audit_pyramid()


def test_pyramid_flags_each_foundation(tmp_path, capsys):
    """AC-PYR-001: known slop in every foundation exits 1 and names each rule."""
    _sloppy_tree(tmp_path)
    assert pyramid.main([], root=tmp_path) == 1
    out = capsys.readouterr().out

    for expected in (
        "sloppy.py:6: SHELL-TRUE",          # shell argument enabled
        "sloppy.py:10: NO-TIMEOUT",         # requests.get with no timeout=
        "sloppy.py:14: DYNAMIC-EVAL",       # eval() on a name, not a literal
        "sloppy.py:20: BARE-EXCEPT",        # bare except:
        "sloppy.py:24: TODO-UNLINKED",      # TODO with no ticket
        "sloppy.py:25: DEAD-CODE-COMMENT",  # commented-out def
        "sloppy.py:24: MAX-CONSEC 10 consecutive comment lines (budget 3)",
        "sloppy.py:0: COMMENT-BUDGET",      # 50% comment ratio, 26 lines
        ".env.example:0: COMMENT-BUDGET",   # non-py file, line-based path
        ".env.example:1: MAX-CONSEC 20 consecutive comment lines (budget 3)",
        "orphan.py:0: UNVERIFIED-MODULE",   # no test names orphan
    ):
        assert expected in out, f"missing finding: {expected}\n{out}"

    assert "ABC-123" not in out, "a TODO carrying a ticket id must stay silent"
    assert "sloppy.py:35: MAX-CONSEC" not in out, "a 3-line run is within budget"
    assert "OK: 3 foundations green" not in out


def test_pyramid_clean_tree_passes(tmp_path, capsys):
    """AC-PYR-002: a slop-free tree with a test reference exits 0 and says so."""
    _clean_tree(tmp_path)
    assert pyramid.main([], root=tmp_path) == 0
    out = capsys.readouterr().out
    assert "OK: 3 foundations green" in out
    assert "SHELL-TRUE" not in out and "UNVERIFIED-MODULE" not in out


def test_pyramid_json_contract(tmp_path, capsys):
    """AC-PYR-003: --json parses, carries rule ids and totals, same exit code."""
    _sloppy_tree(tmp_path)
    assert pyramid.main(["--json"], root=tmp_path) == 1
    payload = json.loads(capsys.readouterr().out)

    assert [section["foundation"] for section in payload["foundations"]] == [
        "1-codebase-constraints", "2-static-analysis", "3-verification",
    ]
    findings = [item for section in payload["foundations"] for item in section["findings"]]
    for rule in ("SHELL-TRUE", "COMMENT-BUDGET", "MAX-CONSEC",
                 "DEAD-CODE-COMMENT", "UNVERIFIED-MODULE"):
        assert any(rule in item for item in findings), f"{rule} missing from --json output"
    assert payload["totals"]["files"] == 3
    assert payload["totals"]["findings"] == len(findings)


def test_pyramid_real_repo_gate():
    """AC-PYR-004: the CLI on this repo exits 0 — the unit tier holds the gate."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)], cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        "the repo's own tracked code violated a foundation "
        "(`python3 scripts/audit_pyramid.py`):\n" + result.stdout + result.stderr
    )
    assert "OK: 3 foundations green" in result.stdout


def test_pyramid_max_consec_exact_run(tmp_path, capsys):
    """AC-PYR-005: a 7-line run fires once at its first line; 3 lines stay silent."""
    consec_runs = "# one.\n" * 7 + "\n" + "# two.\n" * 3 + "\nVALUE = 1\n"
    _write(tmp_path, "service/pkg/consec.py", consec_runs)
    _write(tmp_path, "tests/unit/test_consec.py", '"""Covers consec."""\n')

    assert pyramid.main([], root=tmp_path) == 1
    out = capsys.readouterr().out
    assert "consec.py:1: MAX-CONSEC 7 consecutive comment lines (budget 3)" in out
    assert "consec.py:9: MAX-CONSEC" not in out
    # 10 comment lines against 1 code line: budgeted now that no file is exempt.
    assert "consec.py:0: COMMENT-BUDGET 91% comment ratio over 20% (10/11)" in out

    # Silence both rules to prove the block budget alone is what this AC pins.
    assert pyramid.main(["--max-comment-block", "7", "--max-comment-ratio", "1"],
                        root=tmp_path) == 0
    out = capsys.readouterr().out
    assert "MAX-CONSEC" not in out and "COMMENT-BUDGET" not in out


def test_pyramid_real_repo_totals_include_extra_files():
    """AC-PYR-006: the real-repo run counts both EXTRA_FILES in its totals."""
    for name in pyramid.EXTRA_FILES:
        assert (REPO_ROOT / name).is_file(), f"missing budgeted file: {name}"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"], cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["totals"]["files"] >= 6


def test_pyramid_budgets_tiny_files(tmp_path, capsys):
    """AC-PYR-007: the comment budget applies to every scanned file, however small."""
    assert pyramid.MIN_LINES_FOR_RATIO == 0, "no size floor: every file is budgeted"
    _write(tmp_path, "service/pkg/tiny_over.py", TINY_OVER)
    _write(tmp_path, "service/pkg/tiny_under.py", TINY_UNDER)
    _write(tmp_path, "tests/unit/test_tiny.py",
           '"""Covers tiny_over and tiny_under, small and budgeted all the same."""\n')

    assert pyramid.main([], root=tmp_path) == 1
    out = capsys.readouterr().out
    # 2 comment / 3 code lines, 5 total — far below the old 20-line floor.
    assert "tiny_over.py:0: COMMENT-BUDGET 40% comment ratio over 20% (2/5)" in out
    assert "tiny_under.py" not in out, "a tiny file under budget must stay silent"

    # The ratio, not the size, is what decides: 40% clears a 50% budget.
    assert pyramid.main(["--max-comment-ratio", "0.5"], root=tmp_path) == 0
    out = capsys.readouterr().out
    assert "OK: 3 foundations green" in out and "COMMENT-BUDGET" not in out
