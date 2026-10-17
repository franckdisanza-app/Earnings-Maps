# Numbers sheet: Apple (AAPL) FY2025Q4

**Period:** Fiscal Q4 2025 (Jul–Sep 2025) · 2025-06-29 to 2025-09-27 (13 weeks)  
**Filing:** 8-K (items 2.02, 9.01) filed 2025-10-30 · accession 0000320193-25-000077  
**Source:** [EX-99.1](https://www.sec.gov/Archives/edgar/data/320193/000032019325000077/a8-kex991q4202509272025.htm) · figures as printed, USD millions unless noted  
**Data file:** `data/normalized/AAPL-FY2025Q4.json` · SHA-256 `0807939ad06f88ac7d17e53258a73c48b5034594d69c722d2d518a32eb4bb480`

## Lines

| Line | This quarter | Same quarter last year | YoY | Basis | Locator (table · row as printed) |
| --- | ---: | ---: | ---: | --- | --- |
| Revenue · Products | $73.7B | $70.0B | +5% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · Net sales: › "Products" |
| Revenue · Services | $28.8B | $25.0B | +15% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · Net sales: › "Services" |
| Revenue | $102.5B | $94.9B | +8% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · Net sales: › "Total net sales (1)" |
| Cost · Products | $47.0B | $44.6B | +6% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · Cost of sales: › "Products" |
| Cost · Services | $7.1B | $6.5B | +10% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · Cost of sales: › "Services" |
| Cost of revenue | $54.1B | $51.1B | +6% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · Cost of sales: › "Total cost of sales" |
| Gross profit | $48.3B | $43.9B | +10% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · "Gross margin" |
| Opex · Research and development | $8.9B | $7.8B | +14% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · Operating expenses: › "Research and development" |
| Opex · Selling, general and administrative | $7.0B | $6.5B | +8% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · Operating expenses: › "Selling, general and administrative" |
| Operating expenses | $15.9B | $14.3B | +11% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · Operating expenses: › "Total operating expenses" |
| Operating income | $32.4B | $29.6B | +10% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · "Operating income" |
| Other income/expense | $377M | $19M | +1884% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · "Other income/(expense), net" |
| Pre-tax income | $32.8B | $29.6B | +11% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · "Income before provision for income taxes" |
| Income tax | $5.3B | $14.9B | −64% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · "Provision for income taxes" |
| Net income | $27.5B | $14.7B | +86% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · "Net income" |
| Diluted EPS | $1.85 | $0.97 | +91% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · Earnings per share: › "Diluted" |
| Total (category breakdown) | $102.5B | $94.9B | +8% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · (1) Net sales by category: › "Total net sales" |
| Total (geography breakdown) | $102.5B | $94.9B | +8% | GAAP | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) (In millio · (1) Net sales by reportable segment: › "Total net sales" |

## Segments

**By category**

| Segment | This quarter | Last year | YoY | Locator |
| --- | ---: | ---: | ---: | --- |
| iPhone | $49.0B | $46.2B | +6% | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (U · "iPhone" |
| Mac | $8.7B | $7.7B | +13% | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (U · "Mac" |
| iPad | $7.0B | $7.0B | +0.0% | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (U · "iPad" |
| Wearables, Home and Accessories | $9.0B | $9.0B | −0.3% | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (U · "Wearables, Home and Accessories" |
| Services | $28.8B | $25.0B | +15% | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (U · "Services" |

**By geography**

| Segment | This quarter | Last year | YoY | Locator |
| --- | ---: | ---: | ---: | --- |
| Americas | $44.2B | $41.7B | +6% | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (U · "Americas" |
| Europe | $28.7B | $24.9B | +15% | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (U · "Europe" |
| Greater China | $14.5B | $15.0B | −4% | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (U · "Greater China" |
| Japan | $6.6B | $5.9B | +12% | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (U · "Japan" |
| Rest of Asia Pacific | $8.4B | $7.4B | +14% | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (U · "Rest of Asia Pacific" |

## Derived values

| Value | This quarter | Last year | How |
| --- | ---: | ---: | --- |
| Revenue growth | +8% | | from the same release's prior-year column |
| Gross margin | 47.2% | 46.2% | gross profit ÷ revenue |
| Operating margin | 31.6% | 31.2% | operating income ÷ revenue |
| Net margin | 26.8% | 15.5% | net income ÷ revenue |

## Validation

| Check | Result | Detail |
| --- | --- | --- |
| schema | ✅ | matches schemas/earnings.schema.json |
| revenue_components | ✅ | revenue_products + revenue_services |
| cost_components | ✅ | cost_products + cost_services |
| gross_profit | ✅ | revenue_total − cost_of_revenue_total |
| opex_components | ✅ | opex_rd + opex_sga |
| operating_income | ✅ | gross_profit − operating_expenses_total |
| net_income | ✅ | income_before_tax − income_tax |
| segments_sum:category | ✅ | 5 category items sum to total revenue |
| segments_sum:geography | ✅ | 5 geography items sum to total revenue |
| revenue_yoy | ✅ | +7.9385% from prior-year column |
| operating_margin | ✅ | recomputed from lines |
| net_margin | ✅ | recomputed from lines |

## Audit (numbers-auditor, blind)

28 values checked · 28 matched · **0 unresolved**. Full diff: `out/AAPL-FY2025Q4/audit.md`.

## Guidance (our paraphrase)

None recorded.

## Notes and questions for the owner

- Auditor warning: Prior-year quarter (three months ended September 28, 2024) includes a one-time income tax charge of $10.2 billion, net, from the reversal of the European General Court's State Aid decision; GAAP prior-year provision for income taxes (14,874), net income (14,736) and diluted EPS (0.97) are not comparable. The reconciliation table gives non-GAAP adjusted figures for that quarter: tax 4,628, net income 24,982, diluted EPS 1.64. The release's headline EPS growth uses the non-GAAP prior-year figure.
- Auditor warning: Scale header: '(In millions, except number of shares, which are reflected in thousands, and per-share amounts)'.
- Auditor warning: Statement has Three and Twelve Months Ended columns with identical date headers; only three-month columns used.
- Auditor warning: Quarter length (13 vs 14 weeks) is not stated in the file.
- Auditor warning: 'Products' and 'Services' appear under both 'Net sales:' and 'Cost of sales:'; 'Services' also appears in the category breakdown. Section headings distinguish them.

---
Reply **"approve AAPL-FY2025Q4"** to pass Gate A. Any later change to the data file needs a new approval.
