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
- `$ticker` is in `config/watchlist.yaml`. Read its entry: CIK, fiscal year end, `tables`/`lines`/`segments` mapping, `segments_status`, `data_notes`. If `verified` isn't true, run `scripts/verify_watchlist.py --write --skip-ir` first.
- If the entry says `ingest: manual` (Tesla, Airbnb: their 8-K exhibit has no HTML financial tables), stop and tell the owner: the numbers have to come from the company's IR deck or shareholder letter, read by hand, or from the 10-Q.
- Don't improvise a one-off scraper; the scripts in `scripts/` carry the fair-access rules and are tested (`.venv/Scripts/python.exe -m pytest -q`).

Run Python as `.venv/Scripts/python.exe` from the repo root.

## 1. Find the filing

```bash
.venv/Scripts/python.exe scripts/find_releases.py $ticker --period "$period"
```

It reads `data.sec.gov/submissions/CIK##########.json`, finds the 8-Ks whose items include 2.02, ties each to a fiscal period through the company's own 10-Q/10-K period ends, and picks the full results release: filings made within 10 days of quarter end are preliminary updates (Tesla's deliveries) and are skipped, and the original 8-K wins over an 8-K/A. Add `--download` to cache every EX-99 exhibit plus `filing.json` in `data/raw/<TICKER>/<period>/`. Show the owner one line: form, filing date, accession, exhibit URL, fiscal period and calendar months, and any `warnings` (several 2.02 filings, several EX-99 exhibits, an estimated period end).

For the newest quarter the 10-Q isn't filed yet, so the period end is estimated; `parse_release.py` confirms it from the release's own column header. Some companies keep their statements in a second exhibit (McDonald's EX-99.2 supplement); the mapping names it with `exhibit:`.

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

If the parser can't map a line, it stops and lists the rows that are there. Look at the table (`.venv/Scripts/python.exe scripts/tables.py <exhibit> --grep "<text>"`), fix the mapping in `config/watchlist.yaml` with the label exactly as printed, then rerun. Mapping conventions:
- line ids: `revenue_*`, `cost_*`, `cost_of_revenue_total`, `gross_profit`, `opex_*`, `operating_expenses_total`, `costs_and_expenses_total` (totals that include cost of revenue), `op_plus_*` (items inside operating income, e.g. equity-investee income), `operating_income`, `income_before_tax`, `income_tax`, `net_income_consolidated`, `nci`, `net_income` (attributable to the company), `eps_diluted`
- `expense_printed_negative: true` when the company prints a cost, tax or minority interest as a negative number (Disney, Netflix, Walmart's NCI); the value stays as printed
- a printed dash counts as 0; `optional: true` for lines that come and go
- `computed: [gross_profit]` when the company prints cost of revenue but no gross profit; it appears only as "our calculation"
- `segments_status: single_segment` or `pending_mapping` when segments aren't mapped yet; the numbers sheet then asks the owner

## 4. Validate

```bash
.venv/Scripts/python.exe scripts/validate.py data/normalized/<ID>.json
```

Each identity applies only where the company reports those lines, for both quarters, within the rounding of the printed scale:
- revenue, cost and opex components sum to their totals
- revenue − cost of revenue = gross profit
- operating income from gross profit − opex, revenue − total costs, or revenue − cost of revenue − Σ opex (plus `op_plus_*`)
- pre-tax income − tax = net income (consolidated when minority interests exist), and consolidated − minority interest = attributable
- each segment breakdown sums to its printed total and to revenue
- YoY and margins recomputed from the same release's prior-year column

A failure isn't automatically an error. Companies have eliminations, "corporate and other", and rounding. But every exception needs a written reason in the numbers sheet, tied to a line in the release. If you can't explain it from the source, treat it as an error.

## 5. Independent audit (numbers-auditor)

The auditor proves we read the filing correctly. That proof only works if the auditor never sees our numbers, so its prompt must contain **only**:

1. the path to the raw release file in `data/raw/<TICKER>/<period>/`;
2. the list of line items to find, generated so it carries no values and no mapped labels:
   `.venv/Scripts/python.exe scripts/audit_diff.py --request <ID>`

Don't pass values, the normalized file path, the numbers sheet, or earlier conversation. A hook also blocks the auditor from reading anything outside raw filings.

Delegate with the Agent tool, `subagent_type: numbers-auditor`. Save its JSON reply to `out/<ID>/auditor.json`, then compare:

```bash
.venv/Scripts/python.exe scripts/audit_diff.py <ID> out/<ID>/auditor.json
```

This writes `out/<ID>/audit.md` and `out/<ID>/audit.json` (with the SHA-256 of the data file it audited, so `approve.py` can tell a stale audit). Remind the auditor that Grep and Glob need an explicit path inside the raw folder; the guard blocks anything else.

Values must match exactly after scale normalization, for both periods. For each mismatch, re-read the raw source yourself and find out who's wrong. Fix the parser or mapping if it's us. Never copy the auditor's number across without checking the source. Rerun steps 3–5 until `audit.md` shows zero unresolved mismatches. **An unresolved mismatch blocks Gate A.** Report it to the owner instead of presenting the sheet as ready.

## 6. Numbers sheet

```bash
.venv/Scripts/python.exe scripts/numbers_sheet.py <ID>
```

It builds `out/<ID>/numbers-sheet.md` (layout in `references/numbers-sheet-template.md`) from the data file, the validation checks and `audit.json`, so the owner reads exactly what will be rendered. It's the page the owner approves, often on a phone. It contains:

- header: company, ticker, fiscal period + calendar months, filing, form, filed date, exhibit link
- one table: line · value (formatted as on screen, e.g. `\$94.9B`) · prior year · YoY · basis · locator
- derived values marked "our calculation", with the formula
- validation results, each exception with its reason
- audit result: matches, mismatches resolved, how
- guidance paraphrase with locator
- open questions for the owner (segments missing, ambiguous exhibit, restatements)

It shows the SHA-256 of `data/normalized/<ID>.json`, so the owner can see the approval covers this exact file. Add the guidance paraphrase to the data file before generating it (`guidance` with a locator), and read the auditor's warnings: one-off items in the prior-year quarter (Apple's 2024 State Aid tax charge) change what a fair on-screen comparison is.

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
