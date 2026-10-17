"""Check a normalized earnings file's accounting identities before anything is rendered.

    python scripts/validate.py data/normalized/AAPL-FY2025Q4.json

Each identity runs only when the company reports the lines it needs, for both the current
quarter and the prior-year quarter. Printed figures are rounded, so a sum of k printed
numbers may differ from the printed total by up to k/2 units of the printed scale.

A failed check passes only if the data file has a `validation_exceptions` entry for it with a
reason tied to the release; the numbers sheet shows that reason to the owner.
Exit code 0 = all pass, 1 = a check failed, 2 = the file doesn't match the schema.
"""

from __future__ import annotations

import json
import pathlib
import sys
from dataclasses import asdict, dataclass

from pydantic import ValidationError

from earnings_model import Earnings


@dataclass
class Check:
    id: str
    status: str  # pass | fail | exception | n/a
    detail: str


def tolerance(terms: int) -> float:
    return 0.5 * max(terms, 1) + 1e-9


def run_checks(data: Earnings) -> list[Check]:
    checks: list[Check] = []
    lines = {l.id: l for l in data.lines}

    def v(i: str, prior: bool):
        l = lines.get(i)
        return None if l is None else (l.prior_year_value if prior else l.value)

    def identity(cid: str, total_id: str, parts: list[tuple[str, int]], label: str) -> None:
        """total == Σ sign·part, for current and prior year."""
        if total_id not in lines or not parts or any(p not in lines for p, _ in parts):
            checks.append(Check(cid, "n/a", "lines not reported"))
            return
        problems = []
        for prior in (False, True):
            total = v(total_id, prior)
            vals = [v(p, prior) for p, _ in parts]
            if total is None or any(x is None for x in vals):
                problems.append(("prior year" if prior else "current") + ": missing value")
                continue
            got = sum(s * x for (p, s), x in zip(parts, vals))
            if abs(got - total) > tolerance(len(parts) + 1):
                problems.append(f"{'prior year' if prior else 'current'}: {label} = {got:,.2f} but {total_id} = {total:,.2f}")
        checks.append(Check(cid, "fail" if problems else "pass", "; ".join(problems) or label))

    ids = list(lines)
    rev_parts = [i for i in ids if i.startswith("revenue_") and i != "revenue_total"]
    cost_parts = [i for i in ids if i.startswith("cost_") and i != "cost_of_revenue_total"]
    opex_parts = [i for i in ids if i.startswith("opex_")]

    if rev_parts:
        identity("revenue_components", "revenue_total", [(i, 1) for i in rev_parts], " + ".join(rev_parts))
    if cost_parts:
        identity("cost_components", "cost_of_revenue_total", [(i, 1) for i in cost_parts], " + ".join(cost_parts))
    identity("gross_profit", "gross_profit", [("revenue_total", 1), ("cost_of_revenue_total", -1)], "revenue_total − cost_of_revenue_total")
    if opex_parts and "operating_expenses_total" in lines:
        identity("opex_components", "operating_expenses_total", [(i, 1) for i in opex_parts], " + ".join(opex_parts))
    if "gross_profit" in lines:
        if "operating_expenses_total" in lines:
            identity("operating_income", "operating_income", [("gross_profit", 1), ("operating_expenses_total", -1)], "gross_profit − operating_expenses_total")
        elif opex_parts:
            identity("operating_income", "operating_income", [("gross_profit", 1)] + [(i, -1) for i in opex_parts], "gross_profit − Σ opex")
    elif "costs_and_expenses_total" in lines:
        parts = (["cost_of_revenue_total"] if "cost_of_revenue_total" in lines else []) + opex_parts
        if parts:
            identity("costs_and_expenses", "costs_and_expenses_total", [(i, 1) for i in parts], " + ".join(parts))
        identity("operating_income", "operating_income", [("revenue_total", 1), ("costs_and_expenses_total", -1)], "revenue_total − costs_and_expenses_total")
    elif "operating_expenses_total" in lines:
        identity("operating_income", "operating_income", [("revenue_total", 1), ("operating_expenses_total", -1)], "revenue_total − operating_expenses_total")
    else:
        checks.append(Check("operating_income", "n/a", "no cost lines to check against"))
    if all(i in lines for i in ("income_before_tax", "income_tax", "net_income")):
        identity("net_income", "net_income", [("income_before_tax", 1), ("income_tax", -1)], "income_before_tax − income_tax")

    # Segments: each breakdown sums to its printed total and to total revenue.
    groups = sorted({s.group for s in data.segments})
    for g in groups:
        segs = [s for s in data.segments if s.group == g]
        for prior in (False, True):
            vals = [s.prior_year_value if prior else s.value for s in segs]
            if any(x is None for x in vals):
                checks.append(Check(f"segments_sum:{g}", "fail", "missing prior-year value"))
                break
        else:
            problems = []
            for prior in (False, True):
                total = sum(s.prior_year_value if prior else s.value for s in segs)
                for ref in (f"segments_total_{g}", "revenue_total"):
                    r = v(ref, prior)
                    if r is not None and abs(total - r) > tolerance(len(segs) + 1):
                        problems.append(f"{'prior year' if prior else 'current'}: Σ {g} = {total:,.2f} vs {ref} = {r:,.2f}")
            checks.append(Check(f"segments_sum:{g}", "fail" if problems else "pass", "; ".join(problems) or f"{len(segs)} {g} items sum to total revenue"))
    if data.segments_status == "in_release" and not data.segments:
        checks.append(Check("segments_present", "fail", "segments_status is in_release but no segments"))

    # Derived values recomputed from the same release's prior-year column.
    rev, rev_p = v("revenue_total", False), v("revenue_total", True)
    if rev is not None and rev_p:
        expect = rev / rev_p - 1
        ok = data.derived.revenue_yoy is not None and abs(data.derived.revenue_yoy - expect) < 1e-12
        checks.append(Check("revenue_yoy", "pass" if ok else "fail", f"{expect:+.4%} from prior-year column"))
    for name, num_id in (("operating_margin", "operating_income"), ("net_margin", "net_income")):
        ratio = getattr(data.derived, name)
        if ratio is None or num_id not in lines:
            continue
        ok = all(
            (r is None and (v(num_id, p) is None or not d)) or (r is not None and d and abs(r - v(num_id, p) / d) < 1e-12)
            for r, p, d in ((ratio.current, False, rev), (ratio.prior_year, True, rev_p))
        )
        checks.append(Check(name, "pass" if ok else "fail", "recomputed from lines"))

    missing_prior = [l.id for l in data.lines if l.prior_year_value is None]
    if missing_prior:
        checks.append(Check("prior_year_values", "fail", "no prior-year value: " + ", ".join(missing_prior)))

    excepted = {e.check: e for e in data.validation_exceptions}
    for c in checks:
        if c.status == "fail" and c.id in excepted:
            c.status = "exception"
            c.detail += f" — explained: {excepted[c.id].reason} ({excepted[c.id].locator})"
    return checks


def validate_file(path: pathlib.Path) -> tuple[Earnings | None, list[Check]]:
    try:
        data = Earnings.model_validate_json(path.read_text(encoding="utf-8"))
    except ValidationError as exc:
        return None, [Check("schema", "fail", str(exc))]
    return data, [Check("schema", "pass", "matches schemas/earnings.schema.json")] + run_checks(data)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    path = pathlib.Path(args[0])
    data, checks = validate_file(path)
    for c in checks:
        mark = {"pass": "✅", "fail": "❌", "exception": "⚠️", "n/a": "·"}[c.status]
        print(f"{mark} {c.id:<24} {c.detail}")
    if "--json" in args:
        out = pathlib.Path(args[args.index("--json") + 1])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps([asdict(c) for c in checks], indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    if data is None:
        return 2
    return 1 if any(c.status == "fail" for c in checks) else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
