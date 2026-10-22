"""Unit tier — compose host-port contract. IDs: AC-EXM-004, AC-EXM-005.

Hermetic: `git ls-files` plus file reads — no docker, no network, no service
import. The subjects are the tracked compose files and the tracked `.gitignore`.

A template is cloned to start many projects, and several derived projects may
share one Docker host. A tracked host port therefore collides. Host access stays
a per-deployment opt-in through the gitignored override file
(docs/01-service-architecture.md).
"""
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

UNTRACKED_OPT_IN = "docker-compose.override.yml"


def _tracked_compose_files():
    """Every tracked compose file at the repo root, via `git ls-files`."""
    result = subprocess.run(
        ["git", "ls-files", "docker-compose*.yml"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"`git ls-files` failed in {REPO_ROOT}: {result.stderr.strip()}"
    )
    files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert files, (
        "no tracked compose files found — `git ls-files 'docker-compose*.yml'` "
        f"returned nothing in {REPO_ROOT}"
    )
    return files


def _ports_mappings(text):
    """Line numbers whose stripped content opens a `ports:` mapping."""
    hits = []
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if stripped == "ports:" or stripped.startswith("ports:"):
            hits.append(number)
    return hits


def test_ac_exm_004_no_tracked_compose_file_binds_a_host_port():
    """AC-EXM-004: no tracked compose file carries a `ports:` mapping."""
    files = _tracked_compose_files()
    assert "docker-compose.yml" in files, (
        f"the base compose file is not in the tracked set: {files}"
    )
    violations = []
    for name in files:
        text = (REPO_ROOT / name).read_text(encoding="utf-8")
        for number in _ports_mappings(text):
            violations.append(f"{name}:{number}")
    assert not violations, (
        f"a `ports:` mapping is tracked in: {violations} — host port binding is "
        f"opt-in via a gitignored {UNTRACKED_OPT_IN}, never tracked."
    )


def test_ac_exm_005_override_path_is_gitignored():
    """AC-EXM-005: the documented host-port opt-in path stays gitignored."""
    text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines()]
    ignored = any(
        line == UNTRACKED_OPT_IN or line.startswith(UNTRACKED_OPT_IN) for line in lines
    )
    assert ignored, (
        f"`.gitignore` does not ignore {UNTRACKED_OPT_IN} — the documented "
        f"host-port opt-in path must stay gitignored."
    )
