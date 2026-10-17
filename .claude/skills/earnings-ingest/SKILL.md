---
name: earnings-ingest
description: Turn one company's quarterly results filing from SEC EDGAR into a validated, independently audited data file and numbers sheet, then stop at Gate A for the owner's approval. Use for any watchlist ticker when a new earnings release is out or a past quarter is needed.
argument-hint: "<TICKER> [period, e.g. FY2026Q3]"
arguments: [ticker, period]
disable-model-invocation: true
---

# /earnings-ingest $ticker $period

Accuracy is the product. A wrong number on screen costs more trust than a late video, so every step below either produces a traceable number or stops. The run ends at **Gate A**: the owner approves the numbers sheet, and only then can anything be rendered.

The ID for this quarter is `<TICKER>-<period>`, for example `AAPL-FY2026Q4`. The period is the company's **fiscal** label. If `$period` is empty, use the latest results filing.

## 0. Preconditions (stop and say what's missing)

- `.env` has a real `SEC_USER_AGENT`, not the placeholder from `.env.example`. If it's still the placeholder, ask the owner for their name and email, write it to `.env`, and never echo it back.
- `$ticker` is in `config/watchlist.yaml`. Read its entry: CIK, fiscal year end, line mapping, segments. If `cik` is null or `verified: false`, fill and verify that entry first (CIK from `https://www.sec.gov/files/company_tickers.json` via `scripts/sec_client.py`).
- The scripts exist: `scripts/sec_client.py`, `find_releases.py`, `parse_release.py`, `validate.py`, `audit_diff.py`, `approve.py`. If any is missing, say that Phase 3 builds it and stop. Don't improvise a one-off scraper; the scripts carry the fair-access rules and are tested.

Run Python as `.venv/Scripts/python.exe` from the repo root.

## 1. Find the filing

```bash
.venv/Scripts/python.exe scripts/find_releases.py $ticker --period "$period"
```

It reads `data.sec.gov/submissions/CIK##########.json` and finds the results filing: an 8-K whose items include 2.02 (a 6-K for foreign private issuers), then the earnings-release exhibit in the filing folder (usually EX-99.1). Show the owner one line: form, filing date, accession, exhibit URL, fiscal period, and its calendar months.

If several exhibits could be the release (some companies split the press release and a financial supplement), list them and pick the one with the income statement. Note the choice in the data file's `notes`.

## 2. Download and cache

`sec_client.py` handles every request: the `SEC_USER_AGENT` header, under 10 requests per second, an on-disk cache in `data/raw/<TICKER>/<period>/`, and backoff on 403, 429 and 5xx. Keep the raw files exactly as downloaded; the auditor and any later correction work from them.

## 3. Extract to normalized JSON

```bash
.venv/Scripts/python.exe scripts/parse_release.py $ticker "$period"
```

This writes `data/normalized/<ID>.json` against `schemas/earnings.schema.json`. What matters:

- **Labels exactly as printed.** `label_as_printed` is the row label character for character. The `locator` is the table title plus that row label. Someone must be able to find the number in the PDF or HTML in seconds.
- **Scale and unit from the table header** ("in millions, except per-share data"), never assumed.
- **Current quarter and the prior-year quarter from the same release.** YoY comes only from that prior-year column, never from last year's release, which may have been restated.
- **Basis on every line:** GAAP unless the table says otherwise. Non-GAAP figures come only from the company's reconciliation table and are labeled.
- **Segments** come from the release's segment table. If the release has no segment detail (it's only in the 10-Q or a supplement), mark segments `"not in release"`, record that, and ask the owner: show total revenue only, or wait for the 10-Q.
- **Company-specific shapes** come from the watchlist mapping. If a company prints no gross-profit line (Amazon) or no cost of revenue (Visa, McDonald's), never invent one. A derived subtotal goes in `derived` with `"our_calculation": true`.
- **Guidance:** paraphrase it in our own words with its locator. Never copy a sentence.

If the parser can't map a line, stop and show the table rather than guessing. Fix the mapping in `config/watchlist.yaml`, then rerun.

## 4. Validate

```bash
.venv/Scripts/python.exe scripts/validate.py data/normalized/<ID>.json
```

Each identity applies only where the company reports those lines:
- segments sum to total revenue (within rounding of the printed scale)
- revenue − cost of revenue = gross profit
- gross profit − operating expenses = operating income
- YoY recomputed from the prior-year column

A failure isn't automatically an error. Companies have eliminations, "corporate and other", and rounding. But every exception needs a written reason in the numbers sheet, tied to a line in the release. If you can't explain it from the source, treat it as an error.

## 5. Independent audit (numbers-auditor)

The auditor proves we read the filing correctly. That proof only works if the auditor never sees our numbers, so its prompt must contain **only**:

1. the path to the raw release file in `data/raw/<TICKER>/<period>/`;
2. the list of line items to find: ids and plain descriptions (for example `revenue_total: total net sales/revenue`, `segment:<name>`), plus "current quarter and the same quarter last year".

Don't pass values, the normalized file path, the numbers sheet, or earlier conversation. A hook also blocks the auditor from reading anything outside raw filings.

Delegate with the Agent tool, `subagent_type: numbers-auditor`. Save its JSON reply to `out/<ID>/auditor.json`, then compare:

```bash
.venv/Scripts/python.exe scripts/audit_diff.py data/normalized/<ID>.json out/<ID>/auditor.json --out out/<ID>/audit.md
```

Values must match exactly after scale normalization, for both periods. For each mismatch, re-read the raw source yourself and find out who's wrong. Fix the parser or mapping if it's us. Never copy the auditor's number across without checking the source. Rerun steps 3–5 until `audit.md` shows zero unresolved mismatches. **An unresolved mismatch blocks Gate A.** Report it to the owner instead of presenting the sheet as ready.

## 6. Numbers sheet

Write `out/<ID>/numbers-sheet.md` from `references/numbers-sheet-template.md`. It's the page the owner approves, often on a phone, so keep it scannable:

- header: company, ticker, fiscal period + calendar months, filing, form, filed date, exhibit link
- one table: line · value (formatted as on screen, e.g. `\$94.9B`) · prior year · YoY · basis · locator
- derived values marked "our calculation", with the formula
- validation results, each exception with its reason
- audit result: matches, mismatches resolved, how
- guidance paraphrase with locator
- open questions for the owner (segments missing, ambiguous exhibit, restatements)

Also add the SHA-256 of `data/normalized/<ID>.json`, so the owner can see the approval covers this exact file.

## 7. Gate A (stop here)

If this session can publish artifacts, publish the numbers sheet as a **private** artifact so the owner can approve from their phone, and give the link. Otherwise give the file paths.

Then stop. Don't render, draft captions or write an approval. The approval is written only when the owner explicitly approves this ID in chat:

```bash
.venv/Scripts/python.exe scripts/approve.py <ID> --by "<owner name>"
```

That writes `data/normalized/<ID>.approval.json` with the file's SHA-256. Any later edit to the data file invalidates it and needs a new Gate A.

## Output

```
data/raw/<TICKER>/<period>/        raw filing (cache, gitignored)
data/normalized/<ID>.json          validated data
out/<ID>/auditor.json              auditor's blind extraction
out/<ID>/audit.md                  diff: ours vs auditor
out/<ID>/numbers-sheet.md          for Gate A
```

Finish with a short report: filing found, validation result, audit result, open questions, and "waiting at Gate A".
