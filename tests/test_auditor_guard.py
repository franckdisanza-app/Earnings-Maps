"""The numbers-auditor may only read raw filings; everything else must be blocked."""

import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
GUARD = ROOT / ".claude" / "hooks" / "auditor_guard.py"


def run(tool, tool_input, cwd=str(ROOT)):
    event = {"tool_name": tool, "tool_input": tool_input, "cwd": cwd}
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(ROOT)}
    proc = subprocess.run(
        [sys.executable, str(GUARD)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        env=env,
    )
    return proc.returncode


@pytest.mark.parametrize(
    "tool,tool_input",
    [
        ("Read", {"file_path": str(ROOT / "data" / "raw" / "AAPL" / "FY2026Q4" / "ex99.htm")}),
        ("Read", {"file_path": "data/raw/AAPL/FY2026Q4/ex99.htm"}),
        ("Read", {"file_path": "tests/fixtures/visa/raw/ex99.htm"}),
        ("Grep", {"pattern": "Total net sales", "path": "data/raw/AAPL"}),
        ("Glob", {"pattern": "*.htm", "path": "data/raw/AAPL/FY2026Q4"}),
    ],
)
def test_allows_raw_filings(tool, tool_input):
    assert run(tool, tool_input) == 0


@pytest.mark.parametrize(
    "tool,tool_input",
    [
        ("Read", {"file_path": "data/normalized/AAPL-FY2026Q4.json"}),
        ("Read", {"file_path": "data/normalized/AAPL-FY2026Q4.approval.json"}),
        ("Read", {"file_path": "out/AAPL-FY2026Q4/numbers-sheet.md"}),
        ("Read", {"file_path": "data/raw/../normalized/AAPL-FY2026Q4.json"}),
        ("Read", {"file_path": "tests/fixtures/visa/expected.json"}),
        ("Read", {"file_path": str(pathlib.Path.home() / ".claude" / ".credentials.json")}),
        ("Read", {"file_path": ""}),
        ("Grep", {"pattern": "Total net sales"}),
        ("Grep", {"pattern": "x", "path": "data"}),
        ("Glob", {"pattern": "*.md", "path": "out"}),
        ("Glob", {"pattern": "../../normalized/*", "path": "data/raw/AAPL"}),
        ("Bash", {"command": "cat data/normalized/x.json"}),
    ],
)
def test_blocks_everything_else(tool, tool_input):
    assert run(tool, tool_input) == 2


def test_git_bash_style_path():
    drive, rest = str(ROOT).split(":", 1)
    path = f"/{drive.lower()}{rest.replace(os.sep, '/')}/data/raw/AAPL/x.htm"
    if os.name == "nt":
        assert run("Read", {"file_path": path}) == 0


def test_malformed_input_is_blocked():
    proc = subprocess.run([sys.executable, str(GUARD)], input="not json", capture_output=True, text=True)
    assert proc.returncode == 2
