"""Find a company's quarterly results filing (8-K Item 2.02) and its earnings-release exhibit.

    python scripts/find_releases.py AAPL                     # latest results release
    python scripts/find_releases.py AAPL --period FY2025Q4   # a specific fiscal quarter
    python scripts/find_releases.py AAPL --list              # recent results releases
    python scripts/find_releases.py AAPL --download          # also cache the exhibits in data/raw/

The fiscal period is tied to the filing through the company's own 10-Q/10-K period ends
(`reportDate`): a results 8-K belongs to the latest period that ended within 75 days before
it was filed. For the newest release, whose 10-Q isn't filed yet, the period end is
estimated and must be confirmed from the release's own column header (parse_release does).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import asdict, dataclass, field

from common import company, raw_dir
from fiscal import calendar_label, display_period, fiscal_label, fiscal_year_quarter, fye_month, weeks_between
from sec_client import TICKERS_URL, SecClient, filing_folder_url, submissions_url

RESULTS_FORMS = {"8-K", "8-K/A"}
PERIOD_FORMS = {"10-Q", "10-K", "10-Q/A", "10-K/A"}
MAX_LAG_DAYS = 75


@dataclass
class Exhibit:
    seq: str
    description: str
    document: str
    type: str
    size: str
    url: str


@dataclass
class ResultsFiling:
    ticker: str
    cik: int
    form: str
    accession: str
    filing_date: str
    items: list[str]
    period_end: str
    period_end_source: str
    period_start: str
    period_start_source: str
    fiscal_label: str
    fiscal_year: int
    fiscal_quarter: int
    calendar_label: str
    display: str
    weeks: float
    folder_url: str
    exhibits: list[Exhibit] = field(default_factory=list)
    release_exhibit: Exhibit | None = None
    warnings: list[str] = field(default_factory=list)


def resolve_cik(client: SecClient, ticker: str) -> int:
    data = client.get_json(TICKERS_URL, max_age=86400)
    for row in data.values():
        if row["ticker"].upper() == ticker.upper():
            return int(row["cik_str"])
    raise SystemExit(f"{ticker} not found in SEC company_tickers.json")


def rows(block: dict) -> list[dict]:
    keys = list(block.keys())
    return [dict(zip(keys, values)) for values in zip(*block.values())]


def all_filings(client: SecClient, cik: int, need_before: dt.date | None = None) -> tuple[dict, list[dict]]:
    sub = client.get_json(submissions_url(cik), max_age=600)
    filings = rows(sub["filings"]["recent"])
    for page in sub["filings"].get("files", []):
        oldest = min((f["filingDate"] for f in filings), default="9999")
        if need_before is None or oldest <= need_before.isoformat():
            break
        older = client.get_json(f"https://data.sec.gov/submissions/{page['name']}", max_age=86400)
        filings.extend(rows(older))
    return sub, filings


def is_month_end(d: dt.date) -> bool:
    return (d + dt.timedelta(days=1)).day == 1


def estimate_next_period_end(last: dt.date, history: list[dt.date]) -> dt.date:
    if history and all(is_month_end(d) for d in history[-4:]):
        month = last.month + 3
        year = last.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        nxt = dt.date(year, month % 12 + 1, 1) if month != 12 else dt.date(year + 1, 1, 1)
        return nxt - dt.timedelta(days=1)
    return last + dt.timedelta(weeks=13)


def parse_index(html: str, folder: str) -> list[Exhibit]:
    out = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S | re.I):
        cells = [re.sub(r"<[^>]+>", "", c).replace("&nbsp;", " ").strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S | re.I)]
        if len(cells) != 5:
            continue
        seq, desc, doc, typ, size = cells
        doc = doc.split()[0] if doc else doc
        if not doc or not typ:
            continue
        out.append(Exhibit(seq, desc, doc, typ, size, folder + doc))
    return out


def pick_release_exhibit(exhibits: list[Exhibit]) -> tuple[Exhibit | None, list[str]]:
    warnings = []
    ex99 = [e for e in exhibits if e.type.upper().startswith("EX-99")]
    if not ex99:
        return None, ["no EX-99 exhibit in the filing"]
    first = next((e for e in ex99 if e.type.upper() in ("EX-99.1", "EX-99.01")), ex99[0])
    if len(ex99) > 1:
        warnings.append("several EX-99 exhibits: " + ", ".join(f"{e.type} {e.document}" for e in ex99) + f"; using {first.type}")
    if not first.document.lower().endswith((".htm", ".html")):
        warnings.append(f"release exhibit is {first.document}, not HTML")
    return first, warnings


def results_filings(client: SecClient, ticker: str, cik: int, need_before: dt.date | None = None) -> list[ResultsFiling]:
    sub, filings = all_filings(client, cik, need_before)
    fy_end = fye_month(sub.get("fiscalYearEnd") or "1231")
    period_ends = sorted({dt.date.fromisoformat(f["reportDate"]) for f in filings if f["form"] in PERIOD_FORMS and f.get("reportDate")})
    out = []
    for f in filings:
        if f["form"] not in RESULTS_FORMS or "2.02" not in (f.get("items") or ""):
            continue
        filed = dt.date.fromisoformat(f["filingDate"])
        before = [e for e in period_ends if e < filed]
        warnings = []
        if before and (filed - before[-1]).days <= MAX_LAG_DAYS:
            end, end_src = before[-1], "10-Q/10-K reportDate"
            prior = [e for e in period_ends if e < end]
        elif before:
            end = estimate_next_period_end(before[-1], before)
            end_src = "estimated (10-Q not filed yet); confirm from the release's column header"
            prior = [before[-1]]
            if (filed - end).days > MAX_LAG_DAYS or end >= filed:
                warnings.append("filing date doesn't fit a quarter end; may not be a quarterly results release")
        else:
            continue
        if prior:
            start, start_src = prior[-1] + dt.timedelta(days=1), "prior period's 10-Q/10-K reportDate + 1 day"
        else:
            start, start_src = end - dt.timedelta(weeks=13) + dt.timedelta(days=1), "estimated as 13 weeks"
        fy, q = fiscal_year_quarter(end, fy_end)
        cal = calendar_label(start, end)
        out.append(
            ResultsFiling(
                ticker=ticker,
                cik=cik,
                form=f["form"],
                accession=f["accessionNumber"],
                filing_date=f["filingDate"],
                items=(f.get("items") or "").split(","),
                period_end=end.isoformat(),
                period_end_source=end_src,
                period_start=start.isoformat(),
                period_start_source=start_src,
                fiscal_label=fiscal_label(fy, q),
                fiscal_year=fy,
                fiscal_quarter=q,
                calendar_label=cal,
                display=display_period(fy, q, cal),
                weeks=round(weeks_between(start, end), 1),
                folder_url=filing_folder_url(cik, f["accessionNumber"]),
                warnings=warnings,
            )
        )
    out.sort(key=lambda r: r.filing_date, reverse=True)
    # Several 2.02 filings for one period (pre-announcements, amendments) need a human look.
    seen: dict[str, int] = {}
    for r in out:
        seen[r.fiscal_label] = seen.get(r.fiscal_label, 0) + 1
    for r in out:
        if seen[r.fiscal_label] > 1:
            r.warnings.append(f"{seen[r.fiscal_label]} Item 2.02 filings map to {r.fiscal_label}; using the earliest is usual, check")
    return out


def attach_exhibits(client: SecClient, filing: ResultsFiling) -> None:
    html = client.get(filing.folder_url + f"{filing.accession}-index.htm").decode("utf-8", "replace")
    filing.exhibits = parse_index(html, filing.folder_url)
    filing.release_exhibit, warnings = pick_release_exhibit(filing.exhibits)
    filing.warnings.extend(warnings)


def download(client: SecClient, filing: ResultsFiling) -> list[str]:
    dest = raw_dir(filing.ticker, filing.fiscal_label)
    dest.mkdir(parents=True, exist_ok=True)
    saved = []
    for ex in filing.exhibits:
        if ex.type.upper().startswith("EX-99"):
            client.get(ex.url, dest=dest / ex.document)
            saved.append(str((dest / ex.document).as_posix()))
    (dest / "filing.json").write_text(json.dumps(asdict(filing), indent=2) + "\n", encoding="utf-8", newline="\n")
    return saved


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ticker")
    ap.add_argument("--period", default="", help="fiscal label, e.g. FY2025Q4 (default: latest)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--cik", type=int)
    args = ap.parse_args(argv)

    ticker = args.ticker.upper()
    entry = company(ticker)
    with SecClient() as client:
        cik = args.cik or entry.get("cik") or resolve_cik(client, ticker)
        need_before = None
        if args.period:
            fy = int(args.period[2:6])
            need_before = dt.date(fy - 1, 1, 1)
        found = results_filings(client, ticker, int(cik), need_before)
        if args.list:
            for r in found[:12]:
                print(f"{r.filing_date}  {r.fiscal_label}  {r.display:<34} {r.accession}  period end {r.period_end} ({r.period_end_source.split(';')[0]})")
            return 0
        if args.period:
            matches = [r for r in found if r.fiscal_label == args.period]
            if not matches:
                print(f"no Item 2.02 filing found for {ticker} {args.period}", file=sys.stderr)
                return 1
            filing = sorted(matches, key=lambda r: r.filing_date)[0]
        else:
            if not found:
                print(f"no Item 2.02 filings for {ticker}", file=sys.stderr)
                return 1
            filing = found[0]
        attach_exhibits(client, filing)
        if args.download:
            download(client, filing)
        print(json.dumps(asdict(filing), indent=2))
        print(f"[{client.requests_made} SEC requests]", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
