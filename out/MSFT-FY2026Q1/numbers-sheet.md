# Numbers sheet: Microsoft (MSFT) FY2026Q1

**Period:** Fiscal Q1 2026 (Jul–Sep 2025) · 2025-07-01 to 2025-09-30 (13.1 weeks)  
**Filing:** 8-K (items 2.02, 7.01, 9.01) filed 2025-10-29 · accession 0001193125-25-256310  
**Source:** [EX-99.1](https://www.sec.gov/Archives/edgar/data/789019/000119312525256310/msft-ex99_1.htm) · figures as printed, USD millions unless noted  
**Data file:** `data/normalized/MSFT-FY2026Q1.json` · SHA-256 `ed42db073943afe236b748a75328b7db2f6655b8cde64a82af364e603d132af2`

## Lines

| Line | This quarter | Same quarter last year | YoY | Basis | Locator (table · row as printed) |
| --- | ---: | ---: | ---: | --- | --- |
| Revenue · Product | $15.9B | $15.3B | +4% | GAAP | INCOME STATEMENTS (In millions, except per share amounts) (Unaudited) · Revenue: › "Product" |
| Revenue · Service and other | $61.8B | $50.3B | +23% | GAAP | INCOME STATEMENTS (In millions, except per share amounts) (Unaudited) · Revenue: › "Service and other" |
| Revenue | $77.7B | $65.6B | +18% | GAAP | INCOME STATEMENTS (In millions, except per share amounts) (Unaudited) · Revenue: › "Total revenue" |
| Cost · Product | $2.9B | $3.3B | −11% | GAAP | INCOME STATEMENTS (In millions, except per share amounts) (Unaudited) · Cost of revenue: › "Product" |
| Cost · Service and other | $21.1B | $16.8B | +26% | GAAP | INCOME STATEMENTS (In millions, except per share amounts) (Unaudited) · Cost of revenue: › "Service and other" |
| Cost of revenue | $24.0B | $20.1B | +20% | GAAP | INCOME STATEMENTS (In millions, except per share amounts) (Unaudited) · Cost of revenue: › "Total cost of revenue" |
| Gross profit | $53.6B | $45.5B | +18% | GAAP | INCOME STATEMENTS (In millions, except per share amounts) (Unaudited) · "Gross margin" |
| Opex · Research and development | $8.1B | $7.5B | +8% | GAAP | INCOME STATEMENTS (In millions, except per share amounts) (Unaudited) · "Research and development" |
| Opex · Sales and marketing | $5.7B | $5.7B | 0% | GAAP | INCOME STATEMENTS (In millions, except per share amounts) (Unaudited) · "Sales and marketing" |
| Opex · General and administrative | $1.8B | $1.7B | +8% | GAAP | INCOME STATEMENTS (In millions, except per share amounts) (Unaudited) · "General and administrative" |
| Operating income | $38.0B | $30.6B | +24% | GAAP | INCOME STATEMENTS (In millions, except per share amounts) (Unaudited) · "Operating income" |
| Other income/expense | −$3.7B | −$283M | n/m | GAAP | INCOME STATEMENTS (In millions, except per share amounts) (Unaudited) · "Other expense, net" |
| Pre-tax income | $34.3B | $30.3B | +13% | GAAP | INCOME STATEMENTS (In millions, except per share amounts) (Unaudited) · "Income before income taxes" |
| Income tax | $6.6B | $5.6B | +17% | GAAP | INCOME STATEMENTS (In millions, except per share amounts) (Unaudited) · "Provision for income taxes" |
| Net income | $27.7B | $24.7B | +12% | GAAP | INCOME STATEMENTS (In millions, except per share amounts) (Unaudited) · "Net income" |
| Diluted EPS | $3.72 | $3.30 | +13% | GAAP | INCOME STATEMENTS (In millions, except per share amounts) (Unaudited) · Earnings per share: › "Diluted" |
| Total (segment breakdown) | $77.7B | $65.6B | +18% | GAAP | SEGMENT RESULTS (In millions) (Unaudited) · Total › "Revenue" |

## Segments

**By segment**

| Segment | This quarter | Last year | YoY | Locator |
| --- | ---: | ---: | ---: | --- |
| Productivity and Business Processes | $33.0B | $28.3B | +17% | SEGMENT RESULTS (In millions) (Unaudited) · "Revenue" |
| Intelligent Cloud | $30.9B | $24.1B | +28% | SEGMENT RESULTS (In millions) (Unaudited) · "Revenue" |
| More Personal Computing | $13.8B | $13.2B | +4% | SEGMENT RESULTS (In millions) (Unaudited) · "Revenue" |

## Derived values

| Value | This quarter | Last year | How |
| --- | ---: | ---: | --- |
| Revenue growth | +18% | | from the same release's prior-year column |
| Gross margin | 69.0% | 69.4% | gross profit ÷ revenue |
| Operating margin | 48.9% | 46.6% | operating income ÷ revenue |
| Net margin | 35.7% | 37.6% | net income ÷ revenue |

## Validation

| Check | Result | Detail |
| --- | --- | --- |
| schema | ✅ | matches schemas/earnings.schema.json |
| revenue_components | ✅ | revenue_product + revenue_service |
| cost_components | ✅ | cost_product + cost_service |
| gross_profit | ✅ | revenue_total − cost_of_revenue_total |
| operating_income | ✅ | gross_profit − Σ opex |
| net_income | ✅ | income_before_tax − income_tax |
| segments_sum:segment | ✅ | 3 segment items sum to total revenue |
| revenue_yoy | ✅ | +18.4310% from prior-year column |
| operating_margin | ✅ | recomputed from lines |
| net_margin | ✅ | recomputed from lines |

## Audit (numbers-auditor, blind)

20 values checked · 20 matched · **0 unresolved**. Full diff: `out/MSFT-FY2026Q1/audit.md`.

## Guidance (our paraphrase)

None recorded.

## Notes and questions for the owner

- Auditor warning: Column headers span rows: 'Three Months Ended<br>September 30,' over '2025' / '2024'.
- Auditor warning: Sales and marketing prints 5,717 in both the 2025 and 2024 columns; verified as printed.
- Auditor warning: Other income line is labeled 'Other expense, net'; both values in parentheses.
- Auditor warning: Non-GAAP reconciliation tables exclude the 'Impact from investments in OpenAI' (non-GAAP net income $30,833 / $25,190; diluted EPS $4.13 / $3.37); not used.
- Auditor warning: msft-ex99_2.htm is a blog post with no financial tables; msft-ex99_3.htm contains only slide images.
- Auditor warning: Each year's opex lines sum to the 'Operating expenses' total in SEGMENT RESULTS (15,669 / 14,934).

---
Reply **"approve MSFT-FY2026Q1"** to pass Gate A. Any later change to the data file needs a new approval.
