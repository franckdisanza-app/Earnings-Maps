# Numbers sheet: Visa (V) FY2025Q4

**Period:** Fiscal Q4 2025 (Jul–Sep 2025) · 2025-07-01 to 2025-09-30 (13.1 weeks)  
**Filing:** 8-K (items 2.02, 8.01, 9.01) filed 2025-10-28 · accession 0001403161-25-000077  
**Source:** [EX-99.1](https://www.sec.gov/Archives/edgar/data/1403161/000140316125000077/q42025earningsrelease.htm) · figures as printed, USD millions unless noted  
**Data file:** `data/normalized/V-FY2025Q4.json` · SHA-256 `e9676b6a29833ad7fb7439b79b693f043f3362693cddb671bfe9a56590608149`

## Lines

| Line | This quarter | Same quarter last year | YoY | Basis | Locator (table · row as printed) |
| --- | ---: | ---: | ---: | --- | --- |
| Revenue | $10.7B | $9.6B | +12% | GAAP | Visa Consolidated Statements of Operations (unaudited) · (in millions, except per share data) › "Net revenue" |
| Opex · Personnel | $1.7B | $1.6B | +8% | GAAP | Visa Consolidated Statements of Operations (unaudited) · Operating Expenses › "Personnel" |
| Opex · Marketing | $576M | $551M | +5% | GAAP | Visa Consolidated Statements of Operations (unaudited) · Operating Expenses › "Marketing" |
| Opex · Network and processing | $239M | $208M | +15% | GAAP | Visa Consolidated Statements of Operations (unaudited) · Operating Expenses › "Network and processing" |
| Opex · Professional fees | $256M | $192M | +33% | GAAP | Visa Consolidated Statements of Operations (unaudited) · Operating Expenses › "Professional fees" |
| Opex · Depreciation and amortization | $316M | $274M | +15% | GAAP | Visa Consolidated Statements of Operations (unaudited) · Operating Expenses › "Depreciation and amortization" |
| Opex · General and administrative | $544M | $424M | +28% | GAAP | Visa Consolidated Statements of Operations (unaudited) · Operating Expenses › "General and administrative" |
| Opex · Litigation provision | $903M | $10M | +8930% | GAAP | Visa Consolidated Statements of Operations (unaudited) · Operating Expenses › "Litigation provision" |
| Operating expenses | $4.6B | $3.3B | +40% | GAAP | Visa Consolidated Statements of Operations (unaudited) · Operating Expenses › "Total operating expenses" |
| Operating income | $6.1B | $6.3B | −3% | GAAP | Visa Consolidated Statements of Operations (unaudited) · "Operating income" |
| Pre-tax income | $6.2B | $6.4B | −2% | GAAP | Visa Consolidated Statements of Operations (unaudited) · "Income before income taxes" |
| Income tax | $1.1B | $1.1B | +7% | GAAP | Visa Consolidated Statements of Operations (unaudited) · "Income tax provision" |
| Net income | $5.1B | $5.3B | −4% | GAAP | Visa Consolidated Statements of Operations (unaudited) · "Net income" |
| Diluted EPS | $2.62 | $2.65 | −1% | GAAP | Visa Consolidated Statements of Operations (unaudited) · Diluted Earnings Per Share › "Class A common stock" |

## Segments

The company reports a single segment.
## Derived values

| Value | This quarter | Last year | How |
| --- | ---: | ---: | --- |
| Revenue growth | +12% | | from the same release's prior-year column |
| Operating margin | 57.3% | 66.0% | operating income ÷ revenue |
| Net margin | 47.5% | 55.3% | net income ÷ revenue |

## Validation

| Check | Result | Detail |
| --- | --- | --- |
| schema | ✅ | matches schemas/earnings.schema.json |
| gross_profit | n/a | lines not reported |
| opex_components | ✅ | opex_personnel + opex_marketing + opex_network + opex_professional + opex_da + opex_ga + opex_litigation |
| operating_income | ✅ | revenue_total − operating_expenses_total |
| net_income | ✅ | income_before_tax − income_tax |
| revenue_yoy | ✅ | +11.5109% from prior-year column |
| operating_margin | ✅ | recomputed from lines |
| net_margin | ✅ | recomputed from lines |

## Audit (numbers-auditor, blind)

14 values checked · 14 matched · **0 unresolved**. Full diff: `out/V-FY2025Q4/audit.md`.

## Guidance (our paraphrase)

None recorded.

## Notes and questions for the owner

- Visa reports one segment. Its release breaks net revenue into service, data processing, international transaction and other revenue less client incentives, but only for the current quarter with a printed YoY %, so revenue types aren't used until we decide how to show them.
- Auditor warning: No segment table; Visa reports no segments. Revenue by type appears only in the INCOME STATEMENT SUMMARY with the current quarter and YoY %, no prior-year dollar amounts.
- Auditor warning: INCOME STATEMENT SUMMARY mixes GAAP and non-GAAP (non-GAAP total operating expenses 3,611, net income 5,803, EPS 2.98); not used.
- Auditor warning: Litigation provision 903 vs 10 is as printed; non-GAAP measures exclude it.
- Auditor warning: 'Visa Quarterly Results of Operations (unaudited)' matches every GAAP value above for both quarter columns.
- Auditor warning: Several row labels carry a trailing space in the HTML; trimmed.
- Auditor warning: The non-GAAP reconciliation removes (899) for litigation provision, which differs from the 903 GAAP line; don't compare the two directly.

---
Reply **"approve V-FY2025Q4"** to pass Gate A. Any later change to the data file needs a new approval.
