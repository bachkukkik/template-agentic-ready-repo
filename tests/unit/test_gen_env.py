"""Unit tier — gen-env script contract and safety. IDs: AC-GEN-0NN.

Hermetic: the script is imported from scripts/ by path (it is not a package and
there is no subprocess), and every case runs against tmp_path fixtures — no
service import, no transport, no real .env touched.
"""
import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "gen-env.py"


def _load_script():
    """Import scripts/gen-env.py as a module without executing main()."""
    spec = importlib.util.spec_from_file_location("gen_env", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gen_env = _load_script()


def test_ac_gen_001_script_contract():
    """AC-GEN-001: the script loads and --help exits 0."""
    assert SCRIPT.is_file()
    assert callable(gen_env.main)
    assert gen_env.build_parser() is not None
    with pytest.raises(SystemExit) as exc:
        gen_env.main(["--help"])
    assert exc.value.code == 0


def test_ac_gen_002_fresh_byte_identical(tmp_path, monkeypatch):
    """AC-GEN-002: --fresh writes .env byte-identical to the real .env.example."""
    template_bytes = (REPO_ROOT / ".env.example").read_bytes()
    (tmp_path / ".env.example").write_bytes(template_bytes)
    monkeypatch.chdir(tmp_path)

    assert gen_env.main(["--fresh"]) == 0
    assert (tmp_path / ".env").read_bytes() == template_bytes


def test_ac_gen_003_update_carries_values(tmp_path, monkeypatch, capsys):
    """AC-GEN-003: --update carries values into the verbatim template; extras drop by name."""
    template = (
        "# header comment\n"
        "KEY_A=default_a\n"
        "KEY_B=default_b\n"
        "\n"
        "# trailing comment\n"
        "KEY_C=default_c\n"
    )
    existing = (
        "KEY_A=carried_a\n"
        "# ignored comment\n"
        'KEY_B="quoted b"\n'
        "EXTRA_KEY=extra_value\n"
    )
    (tmp_path / ".env.example").write_text(template, encoding="utf-8")
    (tmp_path / ".env").write_text(existing, encoding="utf-8")
    env_before = (tmp_path / ".env").read_bytes()
    monkeypatch.chdir(tmp_path)

    assert gen_env.main(["--update"]) == 0
    out = capsys.readouterr()
    new_text = (tmp_path / ".env.new").read_text(encoding="utf-8")

    # template comments and structure verbatim
    assert "# header comment\n" in new_text
    assert "# trailing comment\n" in new_text
    # carried values (verbatim, quotes included)
    assert "KEY_A=carried_a\n" in new_text
    assert 'KEY_B="quoted b"\n' in new_text
    # key absent from .env keeps its template default
    assert "KEY_C=default_c\n" in new_text
    # extra key dropped, reported by NAME only, value never echoed
    assert "EXTRA_KEY" not in new_text
    assert "extra_value" not in new_text
    assert "EXTRA_KEY" in out.out
    assert "extra_value" not in out.out
    # the existing .env is never modified
    assert (tmp_path / ".env").read_bytes() == env_before


def test_ac_gen_004_no_clobber_and_exit_codes(tmp_path, monkeypatch):
    """AC-GEN-004: refuses to clobber without --force; exits 1 on environment errors."""
    (tmp_path / ".env.example").write_text("KEY=default\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    # fresh over an existing .env -> exit 1, target unchanged
    (tmp_path / ".env").write_bytes(b"ORIGINAL=1\n")
    assert gen_env.main(["--fresh"]) == 1
    assert (tmp_path / ".env").read_bytes() == b"ORIGINAL=1\n"

    # --force overwrites
    assert gen_env.main(["--fresh", "--force"]) == 0
    assert (tmp_path / ".env").read_bytes() == b"KEY=default\n"

    # update over an existing .env.new -> exit 1, target unchanged
    (tmp_path / ".env.new").write_bytes(b"OLD=1\n")
    assert gen_env.main(["--update"]) == 1
    assert (tmp_path / ".env.new").read_bytes() == b"OLD=1\n"

    # update with a missing .env -> exit 1
    (tmp_path / ".env").unlink()
    (tmp_path / ".env.new").unlink()
    assert gen_env.main(["--update"]) == 1

    # fresh with a missing template -> exit 1
    (tmp_path / ".env.example").unlink()
    assert gen_env.main(["--fresh", "--force"]) == 1


def test_ac_gen_005_values_verbatim(tmp_path, monkeypatch):
    """AC-GEN-005: values after the first '=' are carried byte-exact; export is recognized."""
    template = (
        "QUOTED=default\n"
        "SPACED=default\n"
        "SPECIAL=default\n"
        "UNICODE=default\n"
        "EXPORTED=default\n"
    )
    existing = (
        'QUOTED="a b"\n'
        "SPACED=  padded  \n"
        "SPECIAL=#not-a-comment=raw\n"
        "UNICODE=caf\u00e9-\U0001f600\n"
        "export EXPORTED=carried\n"
    )
    (tmp_path / ".env.example").write_text(template, encoding="utf-8")
    (tmp_path / ".env").write_text(existing, encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    assert gen_env.main(["--update"]) == 0
    new_text = (tmp_path / ".env.new").read_text(encoding="utf-8")

    assert 'QUOTED="a b"\n' in new_text
    assert "SPACED=  padded  \n" in new_text
    assert "SPECIAL=#not-a-comment=raw\n" in new_text
    assert "UNICODE=caf\u00e9-\U0001f600\n" in new_text
    assert "EXPORTED=carried\n" in new_text
