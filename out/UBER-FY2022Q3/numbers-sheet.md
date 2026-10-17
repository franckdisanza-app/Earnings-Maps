# Numbers sheet: Uber (UBER) FY2022Q3

**Period:** Fiscal Q3 2022 (Jul–Sep 2022) · 2022-07-01 to 2022-09-30 (13.1 weeks)  
**Filing:** 8-K (items 2.02, 9.01) filed 2022-11-01 · accession 0001543151-22-000029  
**Source:** [EX-99.1](https://www.sec.gov/Archives/edgar/data/1543151/000154315122000029/uberq322earningspressrelea.htm) · figures as printed, USD millions unless noted  
**Data file:** `data/normalized/UBER-FY2022Q3.json` · SHA-256 `0fa921c0466d36ab2b12626dc297ef907e0a73e04d5fcd47e407ef59771fc9b1`

## Lines

| Line | This quarter | Same quarter last year | YoY | Basis | Locator (table · row as printed) |
| --- | ---: | ---: | ---: | --- | --- |
| Revenue | $8.3B | $4.8B | +72% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (In millions, except s · "Revenue" |
| Cost of revenue | $5.2B | $2.4B | +112% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (In millions, except s · Costs and expenses › "Cost of revenue, exclusive of depreciation and amortization shown separately below" |
| Opex · Operations and support | $617M | $475M | +30% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (In millions, except s · Costs and expenses › "Operations and support" |
| Opex · Sales and marketing | $1.2B | $1.2B | −1% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (In millions, except s · Costs and expenses › "Sales and marketing" |
| Opex · Research and development | $760M | $493M | +54% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (In millions, except s · Costs and expenses › "Research and development" |
| Opex · General and administrative | $908M | $625M | +45% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (In millions, except s · Costs and expenses › "General and administrative" |
| Opex · Depreciation and amortization | $227M | $218M | +4% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (In millions, except s · Costs and expenses › "Depreciation and amortization" |
| Total costs and expenses | $8.8B | $5.4B | +63% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (In millions, except s · Costs and expenses › "Total costs and expenses" |
| Operating income | −$495M | −$572M | n/m | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (In millions, except s · "Loss from operations" |
| Net income | −$1.2B | −$2.4B | n/m | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (In millions, except s · "Net loss attributable to Uber Technologies, Inc." |
| Diluted EPS | −$0.61 | −$1.28 | n/m | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (In millions, except s · Net loss per share attributable to Uber Technologies, Inc. common stockholders: › "Diluted" |
| Total (segment breakdown) | $8.3B | $4.8B | +72% | GAAP | Revenue · Revenue: › "Total" |

## Segments

**By segment**

| Segment | This quarter | Last year | YoY | Locator |
| --- | ---: | ---: | ---: | --- |
| Mobility | $3.8B | $2.2B | +73% | Revenue · "Mobility (1)" |
| Delivery | $2.8B | $2.2B | +24% | Revenue · "Delivery (2)" |
| Freight | $1.8B | $402M | +336% | Revenue · "Freight (3)" |

## Derived values

| Value | This quarter | Last year | How |
| --- | ---: | ---: | --- |
| Revenue growth | +72% | | from the same release's prior-year column |
| Operating margin | −5.9% | −11.8% | operating income ÷ revenue |
| Net margin | −14.5% | −50.0% | net income ÷ revenue |

## Validation

| Check | Result | Detail |
| --- | --- | --- |
| schema | ✅ | matches schemas/earnings.schema.json |
| gross_profit | n/a | lines not reported |
| costs_and_expenses | ✅ | cost_of_revenue_total + opex_operations + opex_sm + opex_rd + opex_ga + opex_da |
| operating_income | ✅ | revenue_total − costs_and_expenses_total |
| segments_sum:segment | ✅ | 3 segment items sum to total revenue |
| revenue_yoy | ✅ | +72.1981% from prior-year column |
| operating_margin | ✅ | recomputed from lines |
| net_margin | ✅ | recomputed from lines |

## Audit (numbers-auditor, blind)

15 values checked · 15 matched · **0 unresolved**. Full diff: `out/UBER-FY2022Q3/audit.md`.

## Guidance (our paraphrase)

None recorded.

## Notes and questions for the owner

- Uber's cost of revenue excludes depreciation and amortization, so no gross profit is computed.
- Auditor warning: Every table prints the older year (2021) first; the current quarter is the second numeric column.
- Auditor warning: Cost of revenue is printed 'exclusive of depreciation and amortization shown separately below'; no total cost of revenue including D&A.
- Auditor warning: Two segment tables share row labels: Gross Bookings (Mobility 13,684/9,883; Delivery 13,684/12,828) and Revenue; segment revenue taken from the Revenue table.
- Auditor warning: Not like-for-like: Q3 2022 Freight includes the Transplace acquisition (closed Nov 12, 2021); Q3 2022 Mobility revenue includes a net $1.1B benefit from the UK business model change; Q3 2021 Mobility benefited from a $123M accrual release.
- Auditor warning: Share counts in thousands; EPS in dollars per share.
- Auditor warning: Net loss in both quarters includes equity-investment revaluation headwinds in 'Other income (expense), net': (535) in Q3 2022 and (1,832) in Q3 2021.

---
Reply **"approve UBER-FY2022Q3"** to pass Gate A. Any later change to the data file needs a new approval.
