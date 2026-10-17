"""Gate A: record the owner's approval of one quarter's numbers.

    python scripts/approve.py <ID> --by "<owner name>"   # only after the owner says "approve <ID>" in chat
    python scripts/approve.py --verify <ID>              # exit 0 if the approval matches the data file
    python scripts/approve.py --status <ID>

Writes data/normalized/<ID>.approval.json with the SHA-256 of the exact data file. It refuses
to approve a file that fails validation or whose audit is missing, stale (audited a different
version of the file) or has unresolved mismatches. Any later edit to the data file breaks
--verify, and the render refuses to run.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import sys

from common import approval_path, data_path, out_dir


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(id_: str) -> tuple[bool, str]:
    data, appr = data_path(id_), approval_path(id_)
    if not data.exists():
        return False, f"{data} missing"
    if not appr.exists():
        return False, f"no approval for {id_} (Gate A not passed)"
    record = json.loads(appr.read_text(encoding="utf-8"))
    current = sha256(data)
    if record.get("sha256") != current:
        return False, f"{id_} changed after approval (approved {record.get('sha256', '')[:12]}…, now {current[:12]}…); needs a new Gate A"
    return True, f"{id_} approved by {record['approved_by']} at {record['approved_at']} (sha256 {current[:12]}…)"


def preconditions(id_: str) -> list[str]:
    from validate import validate_file

    problems = []
    path = data_path(id_)
    if not path.exists():
        return [f"{path} missing"]
    _, checks = validate_file(path)
    failed = [c.id for c in checks if c.status == "fail"]
    if failed:
        problems.append("validation fails: " + ", ".join(failed))
    audit = out_dir(id_) / "audit.json"
    if not audit.exists():
        problems.append("no audit (out/<ID>/audit.json); run the numbers-auditor and audit_diff.py")
    else:
        a = json.loads(audit.read_text(encoding="utf-8"))
        if a.get("data_sha256") != sha256(path):
            problems.append("audit is stale: it checked a different version of the data file")
        if a.get("unresolved", 1):
            problems.append(f"audit has {a.get('unresolved')} unresolved item(s)")
    return problems


def approve(id_: str, by: str) -> int:
    problems = preconditions(id_)
    if problems:
        print("Refusing to approve " + id_ + ":\n  - " + "\n  - ".join(problems), file=sys.stderr)
        return 1
    path = data_path(id_)
    record = {
        "id": id_,
        "file": path.name,
        "sha256": sha256(path),
        "approved_by": by,
        "approved_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "approved_via": "owner's explicit approval in chat (Gate A)",
    }
    approval_path(id_).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"approved {id_}: sha256 {record['sha256'][:12]}…")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) == 2 and args[0] in ("--verify", "--status"):
        ok, msg = verify(args[1])
        print(msg)
        return 0 if ok else 1
    if len(args) == 3 and args[1] == "--by" and args[2].strip():
        return approve(args[0], args[2].strip())
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
