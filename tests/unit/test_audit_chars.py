"""Unit tier — the char-per-line audit. IDs: AC-CHARS-0NN
(docs/prd/09-char-per-line-audit.md).

Hermetic: the auditor is loaded by path and driven in-process with main(argv)
over tmp_path — no subprocess, no service import. AC-CHARS-001 is the hard
gate on the repo's real defaults (the cap is enforced now, not ratcheted);
AC-CHARS-002 proves the auditor discriminates and that fences, tables and
headings are exempt; AC-CHARS-003 pins the CLI contract; AC-CHARS-004 covers
the raw-line path for non-markdown files; AC-CHARS-005 audits the auditor and
this test against the cap they enforce; AC-CHARS-006 pins the unbreakable
exemption — an over-cap line carrying a token wider than the cap — and proves
it cannot hide a wrap-able line.
"""
import importlib.util
import json
import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "audit-chars.py"
TEST_FILE = REPO_ROOT / "tests" / "unit" / "test_audit_chars.py"


def _load_audit_chars():
    """Load scripts/audit-chars.py by path (it is a CLI, not a package)."""
    spec = importlib.util.spec_from_file_location("audit_chars", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(root, name, text):
    """Write one fixture file under root and return its path."""
    path = root / name
    path.write_text(text, encoding="utf-8")
    return path


def _over_count(out):
    """Return the offender count parsed from the report's summary line."""
    for line in out.splitlines():
        if line.startswith("lines over "):
            return int(line.split(": ", 1)[1].split("/")[0])
    return None


chars = _load_audit_chars()


def test_chars_holds_on_real_repo(capsys):
    """AC-CHARS-001: the real defaults are clean and the cap is enforced.

    The gate is hard now: `over` must stay at 0. One over-cap line carries
    a token wider than the cap (the README.md:32 link), so it is exempt as
    `unbreakable`, not repaired — that is the only exemption, capped at 1.
    """
    assert chars.main(["--json"]) == 0, "the real tree must pass as-is"
    out = capsys.readouterr().out
    payload = json.loads(out)

    totals = payload["totals"]
    assert totals["over"] == 0, (
        f"{totals['over']} lines are wrap-able and over the 80 cap: reflow "
        "them (`python3 scripts/audit-chars.py`) — this is a hard gate, "
        "never re-baseline it"
    )
    assert totals["lines"] > 0, "an empty default scope must not pass"
    assert totals["files"] >= 15, "the default scope must cover the docs set"
    assert payload["max_chars"] == 80
    assert payload["advisory"] is False, "strict is the default now"
    assert totals["unbreakable"] <= 1, (
        "only README.md's lone long link may be unbreakable; a new one means "
        "an unwrapped long token landed in the prose"
    )

    # Findings are repo-relative: the repo root prefix must never leak into
    # a report (it also breaks the 44-column file table's alignment).
    assert str(REPO_ROOT) not in out, "reported paths must be repo-relative"
    assert payload["files"], "the report must name the files it measured"
    for row in payload["files"]:
        assert not os.path.isabs(row["file"]), (
            f"reported path must be relative, got {row['file']!r}"
        )
        assert not row["file"].startswith("/"), (
            f"reported path must not be absolute: {row['file']!r}"
        )
    assert "README.md" in {row["file"] for row in payload["files"]}, (
        "the entry documents report as their bare repo-relative name"
    )


def test_chars_discriminates_and_exempts_markdown(tmp_path, capsys):
    """AC-CHARS-002: wide prose fails; fences, tables and headings pass."""
    prose = " ".join(["word"] * 24) + "!"
    assert len(prose) == 120, "the fixture prose is 120 chars wide"
    fenced = "f" * 120
    table = "| " + "c" * 120 + " |"
    heading = "# " + "h" * 120
    doc = _write(tmp_path, "sample.md", "\n".join([
        prose,
        "",
        "Short prose line.",
        "",
        heading,
        "",
        "```",
        fenced,
        "```",
        "",
        table,
        "",
    ]))

    # Strict by default: the over-cap prose line alone fails the run.
    assert chars.main([str(doc)]) == 1, "strict is the default"
    out = capsys.readouterr().out
    assert _over_count(out) == 1
    assert f"{doc}:1:" in out, "the offender must name the file and line 1"
    assert "[120 chars]" in out, "the offender must carry the measured width"
    assert "word word" in out, "the offender must print the line itself"
    for exempt in ("ffff", "cccc", "hhhh"):
        assert exempt not in out, f"{exempt!r} is exempt and must not print"

    # --advisory reports the same offender and exits 0.
    assert chars.main([str(doc), "--advisory"]) == 0
    advisory_out = capsys.readouterr().out
    assert f"{doc}:1:" in advisory_out, "advisory still names the offender"
    assert "advisory only" in advisory_out

    # A cap wider than the fixture clears it outright.
    assert chars.main([str(doc), "--max-chars", "200"]) == 0


def test_chars_cli_contract(tmp_path, capsys):
    """AC-CHARS-003: --help exits 0; a missing path exits 1; no --strict."""
    with pytest.raises(SystemExit) as excinfo:
        chars.main(["--help"])
    assert excinfo.value.code == 0

    missing = tmp_path / "does-not-exist.md"
    assert chars.main([str(missing)]) == 1
    err = capsys.readouterr().err
    assert str(missing) in err, "the error message must name the missing path"

    parser = chars.build_parser()
    defaults = {option: action.default
                for action in parser._actions
                for option in action.option_strings}
    assert defaults["--max-chars"] == 80, "the documented default is 80 chars"
    assert defaults["--advisory"] is False, "strict is the default"
    assert "--strict" not in defaults, "--strict was replaced by --advisory"

    # The removed flag is not silently accepted: argparse rejects it.
    with pytest.raises(SystemExit) as excinfo:
        chars.main([str(missing), "--strict"])
    assert excinfo.value.code == 2, "an unknown flag is a usage error"


def test_chars_raw_fallback_for_non_markdown(tmp_path, capsys):
    """AC-CHARS-004: a non-markdown file is measured raw, no exemptions."""
    wide = "MESSAGE = " + " ".join(["word"] * 18) + "!"
    assert len(wide) == 100
    py = _write(tmp_path, "sample.py", f"import os\n{wide}\n")

    assert chars.main([str(py)]) == 1
    out = capsys.readouterr().out
    assert f"{py}:2:" in out, "the offender must name the file and line 2"
    assert "[100 chars]" in out, "the raw width is counted in full"

    assert chars.main([str(py), "--max-chars", "120"]) == 0


def test_chars_sources_fit_the_cap():
    """AC-CHARS-005: the auditor and this test fit the cap they enforce."""
    for path in (SCRIPT, TEST_FILE):
        assert path.is_file(), f"missing: {path}"
        for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1):
            assert len(line) <= 80, (
                f"{path.name}:{number}: {len(line)} chars over the 80 cap"
            )


def test_chars_unbreakable_token_wider_than_cap(tmp_path, capsys):
    """AC-CHARS-006: a token wider than the cap exempts the line it is on.

    The exemption is structural: no whitespace wrap can bring a token wider
    than the cap under it, so the line carrying that token is exempt — alone
    or beside ordinary words. A 120-char line of short words carries no such
    token, so it stays an offender and the exemption cannot hide it.
    """
    token = "https://example.invalid/" + "p" * 96
    assert len(token) == 120, "the lone token is 120 chars wide"
    assert len(token.split()) == 1

    lone = _write(tmp_path, "lone.md", token + "\n")
    assert chars.main([str(lone), "--json"]) == 0, "an unwrappable line passes"
    payload = json.loads(capsys.readouterr().out)
    assert payload["totals"]["over"] == 0
    assert payload["totals"]["unbreakable"] == 1
    assert payload["files"][0]["unbreakable"] == 1

    assert chars.main([str(lone)]) == 0
    assert "unbreakable" in capsys.readouterr().out, (
        "the report must say the token was exempted, not silently dropped"
    )

    # The same token behind one word: two tokens, still unwrappable, so the
    # line is exempt for the same reason — the token alone exceeds the cap.
    pair = _write(tmp_path, "pair.md", "see " + token + "\n")
    assert chars.main([str(pair), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["totals"]["over"] == 0, (
        "a word plus an over-wide token cannot be wrapped under the cap"
    )
    assert payload["totals"]["unbreakable"] == 1

    # 120 chars of ordinary short words: every token fits, so wrapping fixes
    # it and the exemption must not apply.
    prose = " ".join(["word"] * 24) + "!"
    assert len(prose) == 120, "the fixture prose is 120 chars wide"
    assert max(len(word) for word in prose.split()) <= 80
    wrap = _write(tmp_path, "wrap.md", prose + "\n")
    assert chars.main([str(wrap), "--json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["totals"]["over"] == 1, (
        "wrap-able prose over the cap stays an offender"
    )
    assert payload["totals"]["unbreakable"] == 0
