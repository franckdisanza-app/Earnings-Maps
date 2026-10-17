"""PreToolUse guard for the numbers-auditor subagent.

The auditor's independence is the point of the audit, so it may read raw filings only:
  data/raw/**  and  tests/fixtures/<case>/raw/**
Everything else (normalized data, numbers sheets, out/, approvals, expected test results)
is blocked. Grep and Glob must name an allowed path explicitly; an omitted path would
search the whole repo.

Exit 0 = allow, exit 2 = block (stderr is shown to the subagent).
"""

import json
import os
import re
import sys


def project_root() -> str:
    return os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def to_native(path: str) -> str:
    # Git Bash style /c/Users/... -> C:/Users/...
    m = re.match(r"^/([a-zA-Z])/(.*)$", path)
    if m and os.name == "nt":
        return f"{m.group(1).upper()}:/{m.group(2)}"
    return path


def allowed(path: str, cwd: str, root: str) -> bool:
    if not path:
        return False
    path = to_native(path)
    if not os.path.isabs(path):
        path = os.path.join(cwd or root, path)
    real = os.path.realpath(path)
    try:
        rel = os.path.relpath(real, root)
    except ValueError:  # different drive
        return False
    parts = rel.replace("\\", "/").split("/")
    if parts[0] == "..":
        return False
    if parts[:2] == ["data", "raw"]:
        return True
    if len(parts) >= 4 and parts[:2] == ["tests", "fixtures"] and parts[3] == "raw":
        return True
    return False


def block(reason: str) -> None:
    print(f"numbers-auditor guard: {reason} Only raw filings (data/raw/, tests/fixtures/<case>/raw/) may be read.", file=sys.stderr)
    sys.exit(2)


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except Exception:
        block("could not parse the tool call.")
    tool = event.get("tool_name", "")
    params = event.get("tool_input") or {}
    cwd = event.get("cwd") or ""
    root = project_root()

    if tool == "Read":
        target = params.get("file_path", "")
    elif tool in ("Grep", "Glob"):
        target = params.get("path", "")
        if not target:
            block(f"{tool} needs an explicit path.")
        if ".." in str(params.get("pattern", "")) or ".." in str(params.get("glob", "")):
            block("patterns may not climb out of the folder.")
    else:
        block(f"tool {tool} is not available to the auditor.")

    if not allowed(target, cwd, root):
        block(f"{target!r} is outside the raw filings.")
    sys.exit(0)


if __name__ == "__main__":
    main()
