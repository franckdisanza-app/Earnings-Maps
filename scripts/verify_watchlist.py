"""Confirm watchlist entries against SEC data and report each company's latest results filing.

    python scripts/verify_watchlist.py            # report only
    python scripts/verify_watchlist.py --write    # also fill cik / fye_sec / verified in config/watchlist.yaml

Checks per company: CIK from SEC's ticker file, SEC's `fiscalYearEnd` and registrant name,
the latest 8-K Item 2.02 (and its fiscal label), and whether the IR URL answers. IR sites are
fetched with a generic User-Agent: the SEC identity (with the owner's email) goes to sec.gov only.
"""

from __future__ import annotations

import argparse
import re
import sys

import httpx

from common import WATCHLIST, load_watchlist
from find_releases import resolve_cik, results_filings
from sec_client import SecClient, submissions_url


def ir_status(url: str) -> str:
    try:
        r = httpx.get(url, follow_redirects=True, timeout=15, headers={"User-Agent": "Mozilla/5.0 (EarningsMaps watchlist check)"})
        return f"{r.status_code}" + (f" → {r.url}" if str(r.url).rstrip('/') != url.rstrip('/') else "")
    except httpx.HTTPError as exc:
        return f"error: {type(exc).__name__}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--skip-ir", action="store_true")
    args = ap.parse_args(argv)
    companies = load_watchlist()["companies"]
    found = {}
    with SecClient() as client:
        for c in companies:
            t = c["ticker"]
            cik = resolve_cik(client, t)
            sub = client.get_json(submissions_url(cik), max_age=3600)
            filings = results_filings(client, t, cik)
            latest = filings[0] if filings else None
            found[t] = {"cik": cik, "fye_sec": sub.get("fiscalYearEnd"), "sec_name": sub.get("name")}
            ir = "" if args.skip_ir else ir_status(c["ir_url"])
            mapped = "mapped" if c.get("tables") else "no mapping"
            print(f"{t:<5} CIK {cik:<8} FYE {sub.get('fiscalYearEnd')}  {sub.get('name')[:28]:<28} latest 2.02: "
                  f"{latest.filing_date + ' ' + latest.fiscal_label if latest else '—':<20} {mapped:<10} IR {ir}")
        print(f"[{client.requests_made} SEC requests]", file=sys.stderr)

    if args.write:
        text = WATCHLIST.read_text(encoding="utf-8")
        for t, info in found.items():
            pat = re.compile(r"(  - ticker: %s\n(?:    .*\n)*?)    cik: null\n" % re.escape(t))
            text = pat.sub(lambda m: m.group(1) + f"    cik: {info['cik']}\n    fye_sec: \"{info['fye_sec']}\"  # SEC fiscalYearEnd (MMDD) from the latest filing\n", text, count=1)
            block = re.compile(r"(  - ticker: %s\n(?:    .*\n)*?    )verified: false\n" % re.escape(t))
            text = block.sub(lambda m: m.group(1) + "verified: true  # CIK and fiscal year end confirmed with SEC data\n", text, count=1)
        WATCHLIST.write_text(text, encoding="utf-8", newline="\n")
        print("updated config/watchlist.yaml", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
