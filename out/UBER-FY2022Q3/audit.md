# Audit: UBER-FY2022Q3

Blind re-extraction from `data/raw/UBER/FY2022Q3/uberq322earningspressrelea.htm`, compared with `data/normalized/UBER-FY2022Q3.json` (SHA-256 `0fa921c0466d36ab…`).

Run via: numbers-auditor project subagent (read-only tools, CLAUDE.md omitted, PreToolUse guard limiting reads to data/raw/), 2026-10-17; a first pass via a general-purpose agent with the same instructions matched value for value.

**15 values checked · 15 matched · 0 unresolved**

| Item | Ours (current / prior year) | Auditor | Match | Auditor locator |
| --- | --- | --- | --- | --- |
| revenue_total | 8,343 / 4,845 | 8343 / 4845 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS · Revenue |
| cost_of_revenue_total | 5,173 / 2,438 | 5173 / 2438 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS · Cost of revenue, exclusive of depreciation and amortization shown separately below |
| opex_operations | 617 / 475 | 617 / 475 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS · Operations and support |
| opex_sm | 1,153 / 1,168 | 1153 / 1168 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS · Sales and marketing |
| opex_rd | 760 / 493 | 760 / 493 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS · Research and development |
| opex_ga | 908 / 625 | 908 / 625 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS · General and administrative |
| opex_da | 227 / 218 | 227 / 218 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS · Depreciation and amortization |
| costs_and_expenses_total | 8,838 / 5,417 | 8838 / 5417 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS · Total costs and expenses |
| operating_income | (495) / (572) | -495 / -572 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS · Loss from operations |
| net_income | (1,206) / (2,424) | -1206 / -2424 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS · Net loss attributable to Uber Technologies, Inc. |
| eps_diluted | (0.61) / (1.28) | -0.61 / -1.28 (units) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS · Diluted |
| segments_total_segment | 8,343 / 4,845 | 8343 / 4845 (millions) | ✅ | Revenue · Total |
| segment:segment:Mobility | 3,822 / 2,205 | 3822 / 2205 (millions) | ✅ | Revenue · Mobility (1) |
| segment:segment:Delivery | 2,770 / 2,238 | 2770 / 2238 (millions) | ✅ | Revenue · Delivery (2) |
| segment:segment:Freight | 1,751 / 402 | 1751 / 402 (millions) | ✅ | Revenue · Freight (3) |

## Auditor warnings

- Every table prints the older year (2021) first; the current quarter is the second numeric column.
- Cost of revenue is printed 'exclusive of depreciation and amortization shown separately below'; no total cost of revenue including D&A.
- Two segment tables share row labels: Gross Bookings (Mobility 13,684/9,883; Delivery 13,684/12,828) and Revenue; segment revenue taken from the Revenue table.
- Not like-for-like: Q3 2022 Freight includes the Transplace acquisition (closed Nov 12, 2021); Q3 2022 Mobility revenue includes a net $1.1B benefit from the UK business model change; Q3 2021 Mobility benefited from a $123M accrual release.
- Share counts in thousands; EPS in dollars per share.
- Net loss in both quarters includes equity-investment revaluation headwinds in 'Other income (expense), net': (535) in Q3 2022 and (1,832) in Q3 2021.
