"""Reconcile a quarter's release figures against the XBRL facts in the company's 10-Q / 10-K.

    python scripts/reconcile_xbrl.py <ID>                 # write out/<ID>/xbrl-reconciliation.md
    python scripts/reconcile_xbrl.py <ID> --write-notes   # also log differences in the data file's notes

Earnings releases aren't XBRL-tagged; the 10-Q that follows is. Once it's filed, compare the
headline lines with SEC's companyfacts (three-month facts ending on the period end). A fiscal Q4
usually has no three-month fact, because the 10-K reports the full year; that's reported as
"no quarterly fact", not as a difference. --write-notes changes the data file, so its Gate A
approval must be renewed.
"""

from __future__ import annotations

import datetime as dt
import json
import sys

from common import data_path, out_dir
from earnings_model import Earnings
from fmt import to_units
from sec_client import SecClient, companyfacts_url

CONCEPTS = {
    "revenue_total": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "RevenuesNetOfInterestExpense"],
    "cost_of_revenue_total": ["CostOfRevenue", "CostOfGoodsAndServicesSold", "CostOfGoodsSold"],
    "gross_profit": ["GrossProfit"],
    "operating_expenses_total": ["OperatingExpenses"],
    "costs_and_expenses_total": ["CostsAndExpenses"],
    "operating_income": ["OperatingIncomeLoss"],
    "income_before_tax": ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                          "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"],
    "income_tax": ["IncomeTaxExpenseBenefit"],
    "net_income": ["NetIncomeLoss"],
    "eps_diluted": ["EarningsPerShareDiluted"],
}


def quarterly_fact(facts: dict, concepts: list[str], end: dt.date, unit: str):
    for concept in concepts:
        node = facts.get("us-gaap", {}).get(concept)
        if not node:
            continue
        for f in node.get("units", {}).get(unit, []):
            if f.get("end") != end.isoformat() or "start" not in f:
                continue
            days = (end - dt.date.fromisoformat(f["start"])).days
            if 80 <= days <= 125 and f.get("form", "").startswith(("10-Q", "10-K")):
                return concept, f
    return None, None


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    id_ = args[0]
    data = Earnings.model_validate_json(data_path(id_).read_text(encoding="utf-8"))
    with SecClient() as client:
        facts = client.get_json(companyfacts_url(data.company.cik), max_age=86400)["facts"]
    end = data.period.end_date
    rows, diffs, checked = [], [], 0
    for line in data.lines:
        if line.id not in CONCEPTS:
            continue
        unit = "USD/shares" if line.unit == "USD/share" else "USD"
        concept, fact = quarterly_fact(facts, CONCEPTS[line.id], end, unit)
        if not fact:
            rows.append(f"| {line.id} | {line.value:,} | no quarterly fact | · | |")
            continue
        checked += 1
        ours = to_units(line.value, line.scale)
        theirs = to_units(float(fact["val"]), "units")
        tol = to_units(0.5, line.scale) if line.unit != "USD/share" else 0.005
        ok = abs(ours - theirs) <= tol
        if not ok:
            diffs.append(f"{line.id}: release {line.value:,} {line.scale} vs XBRL {concept} {fact['val']:,} ({fact['form']} {fact['accn']})")
        rows.append(f"| {line.id} | {line.value:,} | {fact['val']:,} ({concept}, {fact['form']} filed {fact['filed']}) | {'✅' if ok else '❌'} | {fact['accn']} |")
    md = [
        f"# XBRL reconciliation: {id_}",
        "",
        f"Release figures vs SEC companyfacts, three-month facts ending {end}. Checked {checked}, differences {len(diffs)}.",
        "",
        "| Line | Release | XBRL | Match | Accession |",
        "| --- | ---: | --- | --- | --- |",
        *rows,
        "",
    ]
    if checked == 0:
        md.append("No three-month XBRL facts for this period (expected for a fiscal Q4, which the 10-K reports as a full year, or before the 10-Q is filed).")
    out = out_dir(id_)
    out.mkdir(parents=True, exist_ok=True)
    (out / "xbrl-reconciliation.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    print(f"{id_}: {checked} checked against XBRL, {len(diffs)} differences → out/{id_}/xbrl-reconciliation.md")
    if diffs and "--write-notes" in args:
        raw = json.loads(data_path(id_).read_text(encoding="utf-8"))
        raw["notes"] += [f"XBRL reconciliation ({dt.date.today()}): {d}" for d in diffs]
        data_path(id_).write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print("notes updated; the Gate A approval for this file must be renewed")
    return 1 if diffs else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
