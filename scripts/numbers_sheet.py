"""Write out/<ID>/numbers-sheet.md, the page the owner approves at Gate A.

    python scripts/numbers_sheet.py <ID>

Built from the data file, validate.py's checks and out/<ID>/audit.json, so what the owner
reads is exactly what will be rendered.
"""

from __future__ import annotations

import hashlib
import json
import sys

from common import data_path, out_dir
from earnings_model import Earnings
from fmt import line_value, money, percent, yoy
from validate import validate_file

NAMES = {
    "revenue_total": "Revenue",
    "cost_of_revenue_total": "Cost of revenue",
    "gross_profit": "Gross profit",
    "operating_expenses_total": "Operating expenses",
    "costs_and_expenses_total": "Total costs and expenses",
    "operating_income": "Operating income",
    "other_income": "Other income/expense",
    "income_before_tax": "Pre-tax income",
    "income_tax": "Income tax",
    "net_income": "Net income",
    "eps_diluted": "Diluted EPS",
}


def name(line_id: str, label: str) -> str:
    if line_id in NAMES:
        return NAMES[line_id]
    if line_id.startswith("segments_total_"):
        return f"Total ({line_id.removeprefix('segments_total_')} breakdown)"
    for p, d in (("revenue_", "Revenue · "), ("cost_", "Cost · "), ("opex_", "Opex · ")):
        if line_id.startswith(p):
            return d + label
    return label


def build(id_: str) -> str:
    path = data_path(id_)
    data = Earnings.model_validate_json(path.read_text(encoding="utf-8"))
    _, checks = validate_file(path)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    audit_path = out_dir(id_) / "audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.exists() else None
    p, r, c = data.period, data.release, data.company

    md = [
        f"# Numbers sheet: {c.name} ({c.ticker}) {p.fiscal_label}",
        "",
        f"**Period:** {p.display} · {p.start_date} to {p.end_date} ({p.weeks:g} weeks)  ",
        f"**Filing:** {r.form} (items {', '.join(r.items)}) filed {r.filing_date} · accession {r.accession}  ",
        f"**Source:** [{r.exhibit}]({r.url}) · figures as printed, {data.currency} {data.scale} unless noted  ",
        f"**Data file:** `data/normalized/{id_}.json` · SHA-256 `{sha}`",
        "",
        "## Lines",
        "",
        "| Line | This quarter | Same quarter last year | YoY | Basis | Locator (table · row as printed) |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for l in data.lines:
        loc = f"{l.locator.table_title[:70]} · {(l.locator.section + ' › ') if l.locator.section else ''}\"{l.locator.row_label}\""
        md.append(f"| {name(l.id, l.label_as_printed)} | {line_value(l.value, l.unit, l.scale)} | {line_value(l.prior_year_value, l.unit, l.scale)} | {yoy(l.value, l.prior_year_value)} | {l.basis} | {loc} |")

    md += ["", "## Segments", ""]
    if data.segments_status == "single_segment":
        md.append("The company reports a single segment.")
    elif data.segments_status == "not_in_release":
        md.append("**Segment detail is not in this release.** Show total revenue only, or wait for the 10-Q?")
    for g in sorted({s.group for s in data.segments}):
        segs = [s for s in data.segments if s.group == g]
        md += [f"**By {g}**", "", "| Segment | This quarter | Last year | YoY | Locator |", "| --- | ---: | ---: | ---: | --- |"]
        for s in segs:
            md.append(f"| {s.name} | {money(s.value, s.scale)} | {money(s.prior_year_value, s.scale)} | {yoy(s.value, s.prior_year_value)} | {s.locator.table_title[:50]} · \"{s.label_as_printed}\" |")
        md.append("")

    d = data.derived
    md += ["## Derived values", "", "| Value | This quarter | Last year | How |", "| --- | ---: | ---: | --- |"]
    if d.revenue_yoy is not None:
        md.append(f"| Revenue growth | {yoy(data.line('revenue_total').value, data.line('revenue_total').prior_year_value)} | | from the same release's prior-year column |")
    for label, ratio, how in (("Gross margin", d.gross_margin, "gross profit ÷ revenue"), ("Operating margin", d.operating_margin, "operating income ÷ revenue"), ("Net margin", d.net_margin, "net income ÷ revenue")):
        if ratio:
            md.append(f"| {label} | {percent(ratio.current, 1)} | {percent(ratio.prior_year, 1)} | {how} |")
    for cl in d.computed_lines:
        md.append(f"| {cl.label} (**our calculation**) | {money(cl.value, cl.scale)} | {money(cl.prior_year_value, cl.scale)} | {cl.formula} |")

    md += ["", "## Validation", "", "| Check | Result | Detail |", "| --- | --- | --- |"]
    for ch in checks:
        mark = {"pass": "✅", "fail": "❌", "exception": "⚠️ explained", "n/a": "n/a"}[ch.status]
        md.append(f"| {ch.id} | {mark} | {ch.detail[:160]} |")

    md += ["", "## Audit (numbers-auditor, blind)", ""]
    if not audit:
        md.append("**Not run yet. Gate A can't pass without it.**")
    else:
        stale = audit["data_sha256"] != sha
        md.append(f"{audit['checked']} values checked · {audit['matched']} matched · **{audit['unresolved']} unresolved**{' · ⚠️ STALE: audited a different version of the file' if stale else ''}. Full diff: `out/{id_}/audit.md`.")
        for ld in audit.get("label_differences", []):
            md.append(f"- label differs (values match): {ld}")

    md += ["", "## Guidance (our paraphrase)", ""]
    md.append(f"{data.guidance.paraphrase} · locator: {data.guidance.locator}" if data.guidance else "None recorded.")

    questions = []
    if data.segments_status == "not_in_release":
        questions.append("Segment detail isn't in the release: total revenue only, or wait for the 10-Q?")
    questions += [n for n in data.notes]
    if audit and audit.get("auditor_warnings"):
        questions += [f"Auditor warning: {w}" for w in audit["auditor_warnings"]]
    md += ["", "## Notes and questions for the owner", ""]
    md += [f"- {q}" for q in questions] or ["- None."]
    md += ["", "---", f"Reply **\"approve {id_}\"** to pass Gate A. Any later change to the data file needs a new approval.", ""]
    return "\n".join(md)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    id_ = args[0]
    out = out_dir(id_)
    out.mkdir(parents=True, exist_ok=True)
    (out / "numbers-sheet.md").write_text(build(id_), encoding="utf-8", newline="\n")
    print(f"wrote out/{id_}/numbers-sheet.md")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
