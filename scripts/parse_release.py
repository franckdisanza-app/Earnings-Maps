"""Extract one quarter from a cached earnings release into data/normalized/<ID>.json.

    python scripts/parse_release.py AAPL FY2025Q4
    python scripts/parse_release.py AAPL FY2025Q4 --stdout     # print instead of writing
    python scripts/parse_release.py AAPL FY2025Q4 --file tests/fixtures/apple/raw/x.htm --filing tests/fixtures/apple/raw/filing.json

The company's line mapping comes from config/watchlist.yaml (`tables`, `lines`, `segments`).
Labels must match exactly as printed; when a mapped label isn't found, the run stops and
lists the labels that are there, instead of guessing.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import datetime as dt

from common import ROOT, company, data_path, raw_dir
from earnings_model import ComputedLine, Derived, Earnings, Line, Locator, Ratio, Segment
from tables import Table, extract_tables

STATEMENT_HINT = re.compile(r"statements? of|balance sheets?|income statements?|segment|results|reconciliation|summary|revenue|net sales|operations", re.I)


class MappingError(SystemExit):
    pass


def heading(t: Table) -> str:
    """Short table title for locators: the statement name plus its scale note."""
    parts = [p.strip() for p in t.title.split(" | ") if p.strip()]
    for i in range(len(parts) - 1, -1, -1):
        p = parts[i]
        if p.startswith("(") and not p.lower().startswith("(in "):
            continue
        if STATEMENT_HINT.search(p) and len(p) < 160:
            nxt = parts[i + 1] if i + 1 < len(parts) and parts[i + 1].lower().startswith("(in ") else ""
            return (p + (" " + nxt if nxt else "")).strip()
    return parts[-1] if parts else f"table {t.index}"


def as_list(v) -> list[str]:
    if v is None:
        return []
    return [v] if isinstance(v, str) else list(v)


def table_matches(t: Table, spec) -> bool:
    if isinstance(spec, str):
        spec = {"title": spec}
    title = t.title.lower()
    if any(s.lower() not in title for s in as_list(spec.get("title"))):
        return False
    if any(s.lower() in title for s in as_list(spec.get("exclude"))):
        return False
    labels = {r.label for r in t.rows}
    return all(r in labels for r in as_list(spec.get("has_rows")))


def pick_columns(t: Table, period_end: dt.date | None) -> tuple[int, int, str, str]:
    quarters = t.quarter_columns()
    if not quarters:
        raise MappingError(f"table {t.index} ({heading(t)}) has no three-month columns")
    if period_end:
        cur = [c for c in quarters if abs((c.end_date - period_end).days) <= 3]
    else:
        latest = max(c.end_date for c in quarters)
        cur = [c for c in quarters if c.end_date == latest]
    if not cur:
        found = ", ".join(sorted({str(c.end_date) for c in quarters}))
        raise MappingError(f"no three-month column ending {period_end} in {heading(t)} (found {found})")
    current = cur[0]
    prior = [c for c in quarters if 350 <= (current.end_date - c.end_date).days <= 380]
    if not prior:
        raise MappingError(f"no prior-year three-month column in {heading(t)}")
    return current.index, prior[0].index, current.header, prior[0].header


def find_row(t: Table, spec: dict):
    labels = as_list(spec.get("label"))
    sections = as_list(spec.get("section"))
    contains = spec.get("section_contains")
    hits = [
        r for r in t.rows
        if r.label in labels
        and (not sections or r.section in sections)
        and (not contains or (r.section and contains.lower() in r.section.lower()))
    ]
    if not hits:
        avail = "\n    ".join(f"[{r.section or ''}] {r.label}" for r in t.rows)
        raise MappingError(f"label {labels} (section {sections or contains or 'any'}) not found in {heading(t)}. Rows:\n    {avail}")
    return hits[0]


def scale_for(t: Table, default: str) -> str:
    if t.scale:
        return t.scale
    blob = " ".join(r.section or "" for r in t.rows[:3]) + " " + " ".join(" ".join(t.grid[h]) for h in range(min(len(t.grid), 12)))
    m = re.search(r"in\s+(millions|thousands|billions)", blob, re.I)
    return m.group(1).lower() if m else default


def ratio(num, den) -> float | None:
    if num is None or not den:
        return None
    return num / den


def build(ticker: str, period: str, exhibit: pathlib.Path, filing: dict) -> Earnings:
    entry = company(ticker)
    if not entry.get("tables") or not entry.get("lines"):
        raise MappingError(f"{ticker} has no line mapping in config/watchlist.yaml yet; run scripts/tables.py on the release and add one")
    tables = extract_tables(exhibit.read_bytes())
    period_end = dt.date.fromisoformat(filing["period_end"])

    def table_for(name: str) -> Table:
        spec = entry["tables"][name]
        for t in tables:
            if table_matches(t, spec):
                try:
                    pick_columns(t, period_end)
                    return t
                except MappingError:
                    continue
        raise MappingError(f"no table matches {name!r} = {spec!r} with a column ending {period_end}")

    cache: dict[str, Table] = {}

    def get_table(name: str) -> Table:
        if name not in cache:
            cache[name] = table_for(name)
        return cache[name]

    # The income statement's own column header is the authority for the period end.
    income = get_table(entry.get("primary_table", "income"))
    cur_col, _, _, _ = pick_columns(income, period_end)
    confirmed_end = income.columns[cur_col].end_date
    notes = []
    if "estimated" in filing.get("period_end_source", ""):
        notes.append(f"Period end {confirmed_end} confirmed from the release's column header (find_releases had estimated {period_end}).")

    default_scale = scale_for(income, "millions")
    lines: list[Line] = []
    for id_, spec in entry["lines"].items():
        t = get_table(spec.get("table", "income"))
        cur, prior, cur_h, prior_h = pick_columns(t, confirmed_end)
        row = find_row(t, spec)
        v, pv = row.values.get(cur), row.values.get(prior)
        if v is None or v.value is None:
            if spec.get("optional"):
                continue
            raise MappingError(f"{id_}: no current-quarter value for {row.label!r} in {heading(t)}")
        unit = spec.get("unit", "USD")
        lines.append(Line(
            id=id_,
            label_as_printed=row.label,
            value=v.value,
            prior_year_value=pv.value if pv else None,
            unit=unit,
            scale=spec.get("scale", "units" if unit == "USD/share" else scale_for(t, default_scale)),
            basis=spec.get("basis", "GAAP"),
            locator=Locator(table_title=heading(t), row_label=row.label, section=row.section, column_current=cur_h, column_prior_year=prior_h),
            printed_negative=v.negative,
        ))

    segments: list[Segment] = []
    for group in entry.get("segments", []) or []:
        t = get_table(group["table"])
        cur, prior, cur_h, prior_h = pick_columns(t, confirmed_end)
        for item in group["items"]:
            row = find_row(t, item)
            v, pv = row.values.get(cur), row.values.get(prior)
            if v is None or v.value is None:
                raise MappingError(f"segment {item['name']}: no current-quarter value in {heading(t)}")
            segments.append(Segment(
                group=group["group"],
                name=item["name"],
                label_as_printed=row.label,
                value=v.value,
                prior_year_value=pv.value if pv else None,
                scale=scale_for(t, default_scale),
                locator=Locator(table_title=heading(t), row_label=row.label, section=row.section, column_current=cur_h, column_prior_year=prior_h),
            ))
        if group.get("total"):
            row = find_row(t, group["total"])
            total = row.values.get(cur)
            lines.append(Line(
                id=f"segments_total_{group['group']}",
                label_as_printed=row.label,
                value=total.value,
                prior_year_value=row.values.get(prior).value if row.values.get(prior) else None,
                scale=scale_for(t, default_scale),
                locator=Locator(table_title=heading(t), row_label=row.label, section=row.section, column_current=cur_h, column_prior_year=prior_h),
            ))

    by_id = {l.id: l for l in lines}

    def val(i, prior=False):
        l = by_id.get(i)
        return None if l is None else (l.prior_year_value if prior else l.value)

    computed: list[ComputedLine] = []
    for c in entry.get("computed", []) or []:
        if c == "gross_profit" and "gross_profit" not in by_id and val("revenue_total") is not None and val("cost_of_revenue_total") is not None:
            pv = val("revenue_total", True) - val("cost_of_revenue_total", True) if val("revenue_total", True) is not None and val("cost_of_revenue_total", True) is not None else None
            computed.append(ComputedLine(id="gross_profit", label="Gross profit", formula="revenue_total − cost_of_revenue_total",
                                         value=val("revenue_total") - val("cost_of_revenue_total"), prior_year_value=pv, scale=by_id["revenue_total"].scale))
    gp = val("gross_profit") if "gross_profit" in by_id else next((c.value for c in computed if c.id == "gross_profit"), None)
    gp_prior = val("gross_profit", True) if "gross_profit" in by_id else next((c.prior_year_value for c in computed if c.id == "gross_profit"), None)
    rev, rev_p = val("revenue_total"), val("revenue_total", True)
    derived = Derived(
        revenue_yoy=(rev / rev_p - 1) if rev is not None and rev_p else None,
        gross_margin=Ratio(current=ratio(gp, rev), prior_year=ratio(gp_prior, rev_p)) if gp is not None else None,
        operating_margin=Ratio(current=ratio(val("operating_income"), rev), prior_year=ratio(val("operating_income", True), rev_p)) if "operating_income" in by_id else None,
        net_margin=Ratio(current=ratio(val("net_income"), rev), prior_year=ratio(val("net_income", True), rev_p)) if "net_income" in by_id else None,
        computed_lines=computed,
    )

    from fiscal import calendar_label, display_period, fiscal_year_quarter, parse_label, weeks_between

    fy, q = parse_label(period)
    start = dt.date.fromisoformat(filing["period_start"])
    cal = calendar_label(start, confirmed_end)
    rel_ex = filing["release_exhibit"]
    if entry.get("segments_status") == "single_segment":
        seg_status = "single_segment"
    elif segments:
        seg_status = "in_release"
    else:
        seg_status = "not_in_release"
    notes.extend(entry.get("data_notes", []) or [])
    return Earnings(
        company={"ticker": ticker, "name": entry["name"], "cik": int(filing["cik"])},
        period={
            "fiscal_label": period, "fiscal_year": fy, "fiscal_quarter": q,
            "start_date": start, "end_date": confirmed_end, "start_date_source": filing["period_start_source"],
            "calendar_label": cal, "display": display_period(fy, q, cal), "weeks": round(weeks_between(start, confirmed_end), 1),
        },
        scale=default_scale,
        release={
            "form": filing["form"], "filing_date": filing["filing_date"], "accession": filing["accession"],
            "items": filing.get("items", []), "url": rel_ex["url"], "exhibit": rel_ex["type"],
            "local_path": exhibit.resolve().relative_to(ROOT).as_posix() if exhibit.resolve().is_relative_to(ROOT) else str(exhibit),
        },
        lines=lines,
        segments_status=seg_status,
        segments=segments,
        derived=derived,
        notes=notes,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ticker")
    ap.add_argument("period")
    ap.add_argument("--file", type=pathlib.Path, help="exhibit path (default: from data/raw/<T>/<period>/filing.json)")
    ap.add_argument("--filing", type=pathlib.Path, help="filing.json path")
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args(argv)
    ticker, period = args.ticker.upper(), args.period
    filing_path = args.filing or raw_dir(ticker, period) / "filing.json"
    if not filing_path.exists():
        raise SystemExit(f"{filing_path} missing; run find_releases.py {ticker} --period {period} --download first")
    filing = json.loads(filing_path.read_text(encoding="utf-8"))
    exhibit = args.file or filing_path.parent / filing["release_exhibit"]["document"]
    data = build(ticker, period, exhibit, filing)
    text = data.model_dump_json(indent=2) + "\n"
    if args.stdout:
        sys.stdout.write(text)
    else:
        out = data_path(f"{ticker}-{period}")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {out.relative_to(ROOT).as_posix()} ({len(data.lines)} lines, {len(data.segments)} segments)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
