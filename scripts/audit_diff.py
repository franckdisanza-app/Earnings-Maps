"""Compare our extraction with the numbers-auditor's blind extraction.

    python scripts/audit_diff.py --request <ID>          # the item list to give the auditor
    python scripts/audit_diff.py <ID> out/<ID>/auditor.json

The request lists only ids and plain descriptions (no labels as we mapped them, no values),
so the auditor has to find each figure in the filing on its own.

The diff writes out/<ID>/audit.md and out/<ID>/audit.json. Values must match exactly
after converting both sides to units. Exit 1 while anything is unresolved.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys

from common import data_path, out_dir
from earnings_model import Earnings
from fmt import number, to_units

DESCRIPTIONS = {
    "revenue_total": "total revenue / net revenue / total net sales",
    "cost_of_revenue_total": "total cost of revenue / cost of sales",
    "gross_profit": "gross profit / gross margin (as a dollar amount)",
    "operating_expenses_total": "total operating expenses",
    "costs_and_expenses_total": "total costs and expenses",
    "operating_income": "operating income (or loss) / income (loss) from operations",
    "other_income": "other income (expense), net",
    "income_before_tax": "income before income taxes",
    "income_tax": "provision for (benefit from) income taxes",
    "net_income": "net income (loss) attributable to the company",
    "eps_diluted": "diluted earnings (loss) per share (for companies with several share classes: Class A)",
}
PREFIXES = {
    "revenue_": "revenue line: ",
    "cost_": "cost of revenue line: ",
    "opex_": "operating expense line: ",
}


ABBREVIATIONS = {
    "rd": "research and development", "sm": "sales and marketing", "ga": "general and administrative",
    "sga": "selling, general and administrative", "da": "depreciation and amortization",
}


def describe(line_id: str) -> str:
    if line_id in DESCRIPTIONS:
        return DESCRIPTIONS[line_id]
    if line_id.startswith("segments_total_"):
        return f"total of the revenue breakdown by {line_id.removeprefix('segments_total_')} (usually equals total revenue)"
    for p, d in PREFIXES.items():
        if line_id.startswith(p):
            rest = line_id.removeprefix(p)
            return d + ABBREVIATIONS.get(rest, rest.replace("_", " "))
    return line_id.replace("_", " ")


def request(data: Earnings) -> str:
    items = [f"- {l.id}: {describe(l.id)}" for l in data.lines]
    items += [f"- segment:{s.group}:{s.name}: revenue of '{s.name}' in the breakdown by {s.group}" for s in data.segments]
    return (
        "Find each item for the current quarter and the same quarter of the prior year "
        f"(three-month columns; the current quarter ends {data.period.end_date}).\n" + "\n".join(items)
    )


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


SCALES = {"units": "units", "unit": "units", "ones": "units", "thousands": "thousands", "millions": "millions", "billions": "billions"}


def norm_scale(s: str | None, unit: str) -> str:
    if unit == "USD/share":
        return "units"
    s = (s or "").lower()
    for k, v in SCALES.items():
        if k in s:
            return v
    return "units"


def diff(id_: str, auditor_path: pathlib.Path) -> tuple[str, dict]:
    path = data_path(id_)
    data = Earnings.model_validate_json(path.read_text(encoding="utf-8"))
    raw = auditor_path.read_text(encoding="utf-8")
    m = re.search(r"\{.*\}", raw, re.S)  # tolerate prose around the JSON
    aud = json.loads(m.group(0) if m else raw)
    items = {i["id"]: i for i in aud.get("items", [])}

    ours = [(l.id, l.label_as_printed, l.value, l.prior_year_value, l.unit, l.scale) for l in data.lines]
    ours += [(f"segment:{s.group}:{s.name}", s.label_as_printed, s.value, s.prior_year_value, s.unit, s.scale) for s in data.segments]

    rows, mismatched, not_found, label_diff = [], [], [], []
    for id__, label, val, pval, unit, scale in ours:
        a = items.get(id__)
        if not a or not a.get("found"):
            not_found.append(id__)
            rows.append(f"| {id__} | {number(val, scale)} / {number(pval, scale)} | not found | ❌ | |")
            continue
        a_scale = norm_scale(a.get("scale"), unit)
        ok_cur = a.get("value_current") is not None and to_units(val, scale) == to_units(float(a["value_current"]), a_scale)
        ok_pri = (pval is None and a.get("value_prior_year") is None) or (
            pval is not None and a.get("value_prior_year") is not None and to_units(pval, scale) == to_units(float(a["value_prior_year"]), a_scale))
        ok = ok_cur and ok_pri
        if not ok:
            mismatched.append(id__)
        if a.get("label_as_printed") and a["label_as_printed"].strip() != label.strip():
            label_diff.append(f"{id__}: ours '{label}' vs auditor '{a['label_as_printed']}'")
        rows.append(
            f"| {id__} | {number(val, scale)} / {number(pval, scale)} | {a.get('value_current')} / {a.get('value_prior_year')} ({a_scale}) | {'✅' if ok else '❌'} | {a.get('table_title', '')[:60]} · {a.get('label_as_printed', '')} |"
        )

    unresolved = len(mismatched) + len(not_found)
    summary = {
        "id": id_,
        "data_sha256": sha256(path),
        "auditor_file": auditor_path.as_posix(),
        "checked": len(ours),
        "matched": len(ours) - unresolved,
        "mismatched": mismatched,
        "not_found": not_found,
        "label_differences": label_diff,
        "auditor_warnings": aud.get("warnings", []),
        "unresolved": unresolved,
    }
    md = [
        f"# Audit: {id_}",
        "",
        f"Blind re-extraction from `{aud.get('source_file', '?')}`, compared with `data/normalized/{id_}.json` (SHA-256 `{summary['data_sha256'][:16]}…`).",
        "",
        *( [f"Run via: {aud['run_via']}.", ""] if aud.get("run_via") else [] ),
        f"**{summary['checked']} values checked · {summary['matched']} matched · {unresolved} unresolved**",
        "",
        "| Item | Ours (current / prior year) | Auditor | Match | Auditor locator |",
        "| --- | --- | --- | --- | --- |",
        *rows,
        "",
    ]
    if label_diff:
        md += ["## Label differences (values match; review)", "", *[f"- {d}" for d in label_diff], ""]
    if aud.get("warnings"):
        md += ["## Auditor warnings", "", *[f"- {w}" for w in aud["warnings"]], ""]
    if unresolved:
        md += ["## Unresolved — blocks Gate A", "", "Re-read the raw filing for each item and fix whichever side is wrong; never copy the auditor's number across unchecked.", ""]
    return "\n".join(md), summary


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if args[:1] == ["--request"]:
        data = Earnings.model_validate_json(data_path(args[1]).read_text(encoding="utf-8"))
        print(request(data))
        return 0
    if len(args) < 2:
        print(__doc__)
        return 2
    id_, auditor_path = args[0], pathlib.Path(args[1])
    md, summary = diff(id_, auditor_path)
    out = out_dir(id_)
    out.mkdir(parents=True, exist_ok=True)
    (out / "audit.md").write_text(md, encoding="utf-8", newline="\n")
    (out / "audit.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"{summary['matched']}/{summary['checked']} matched, {summary['unresolved']} unresolved → out/{id_}/audit.md")
    return 1 if summary["unresolved"] else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
