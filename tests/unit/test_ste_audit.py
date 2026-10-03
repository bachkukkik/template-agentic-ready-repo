"""Unit tier — the STE-style audit tripwire. IDs: AC-STE-0NN (docs/prd/05-ste-audit.md).

Hermetic: the auditor is loaded by path and driven in-process with main(argv) — no
subprocess, no service import, no transport. AC-STE-001 asserts the repo's real docs
stay above the 80% floor; AC-STE-002 proves the auditor discriminates (and that fenced
code is exempt); AC-STE-003 pins the CLI contract.
"""
import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "audit-ste.py"


def _load_audit_ste():
    """Load scripts/audit-ste.py by path (it is a CLI, not an importable package)."""
    spec = importlib.util.spec_from_file_location("audit_ste", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ste = _load_audit_ste()


def test_ste_audit_real_docs_pass_threshold():
    """AC-STE-001: the repo's real docs pass at the default 80% threshold (exit 0)."""
    # Defaults resolve against REPO_ROOT (collect_default_inputs anchors there), so
    # this holds regardless of the pytest invocation directory.
    assert ste.main([]) == 0, (
        "the repo's own docs fell below the default 80% within-limit threshold "
        "(`python3 scripts/audit-ste.py`). A doc edit that drops the repo below 80% "
        "must fail CI before merge — remedy by shortening over-limit sentences in "
        "docs/*.md or README.md, per docs/prd/05-ste-audit.md."
    )


def test_ste_audit_discriminates_and_exempts_fences(tmp_path, capsys):
    """AC-STE-002: a long sentence fails at threshold 80 but passes at 50; fences are exempt."""
    # One over-limit prose sentence (60 words) + one short sentence => 1/2 = 50% within.
    long_sentence = " ".join(["alpha"] * 60) + "."
    # A 60-word line inside a fence must NOT count: if it did, the share would fall to
    # 1/3 = 33% and the threshold-50 run below would fail.
    fenced_line = " ".join(["fencedbeta"] * 60)
    doc = tmp_path / "sample.md"
    doc.write_text(
        f"{long_sentence}\n\n"
        "This short sentence stays within the limit.\n\n"
        f"```\n{fenced_line}\n```\n",
        encoding="utf-8",
    )

    # Default threshold 80: 50% within is below it -> exit 1, offender named.
    assert ste.main([str(doc)]) == 1
    out = capsys.readouterr().out
    assert str(doc) in out, "the offender line must name the offending file"
    assert "60w" in out, "the offender line must carry the sentence word count"
    assert "alpha" in out, "the long prose sentence must be printed as an offender"
    assert "fencedbeta" not in out, "a 60-word line inside a code fence must be exempt"

    # Threshold 50: the same doc now passes (50% >= 50) -> exit 0.
    assert ste.main([str(doc), "--threshold", "50"]) == 0


def test_ste_audit_cli_contract(tmp_path, capsys):
    """AC-STE-003: --help exits 0; a missing input file exits 1 and names the path."""
    with pytest.raises(SystemExit) as excinfo:
        ste.main(["--help"])
    assert excinfo.value.code == 0

    missing = tmp_path / "does-not-exist.md"
    assert ste.main([str(missing)]) == 1
    err = capsys.readouterr().err
    assert str(missing) in err, "the error message must name the missing path"
