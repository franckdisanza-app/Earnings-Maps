# Audit: V-FY2025Q4

Blind re-extraction from `data/raw/V/FY2025Q4/q42025earningsrelease.htm`, compared with `data/normalized/V-FY2025Q4.json` (SHA-256 `e9676b6a29833ad7…`).

Run via: numbers-auditor project subagent (read-only tools, CLAUDE.md omitted, PreToolUse guard limiting reads to data/raw/), 2026-10-17; a first pass via a general-purpose agent with the same instructions matched value for value.

**14 values checked · 14 matched · 0 unresolved**

| Item | Ours (current / prior year) | Auditor | Match | Auditor locator |
| --- | --- | --- | --- | --- |
| revenue_total | 10,724 / 9,617 | 10724 / 9617 (millions) | ✅ | Visa Consolidated Statements of Operations (unaudited) · Net revenue |
| opex_personnel | 1,742 / 1,609 | 1742 / 1609 (millions) | ✅ | Visa Consolidated Statements of Operations (unaudited) · Personnel |
| opex_marketing | 576 / 551 | 576 / 551 (millions) | ✅ | Visa Consolidated Statements of Operations (unaudited) · Marketing |
| opex_network | 239 / 208 | 239 / 208 (millions) | ✅ | Visa Consolidated Statements of Operations (unaudited) · Network and processing |
| opex_professional | 256 / 192 | 256 / 192 (millions) | ✅ | Visa Consolidated Statements of Operations (unaudited) · Professional fees |
| opex_da | 316 / 274 | 316 / 274 (millions) | ✅ | Visa Consolidated Statements of Operations (unaudited) · Depreciation and amortization |
| opex_ga | 544 / 424 | 544 / 424 (millions) | ✅ | Visa Consolidated Statements of Operations (unaudited) · General and administrative |
| opex_litigation | 903 / 10 | 903 / 10 (millions) | ✅ | Visa Consolidated Statements of Operations (unaudited) · Litigation provision |
| operating_expenses_total | 4,576 / 3,268 | 4576 / 3268 (millions) | ✅ | Visa Consolidated Statements of Operations (unaudited) · Total operating expenses |
| operating_income | 6,148 / 6,349 | 6148 / 6349 (millions) | ✅ | Visa Consolidated Statements of Operations (unaudited) · Operating income |
| income_before_tax | 6,223 / 6,372 | 6223 / 6372 (millions) | ✅ | Visa Consolidated Statements of Operations (unaudited) · Income before income taxes |
| income_tax | 1,133 / 1,054 | 1133 / 1054 (millions) | ✅ | Visa Consolidated Statements of Operations (unaudited) · Income tax provision |
| net_income | 5,090 / 5,318 | 5090 / 5318 (millions) | ✅ | Visa Consolidated Statements of Operations (unaudited) · Net income |
| eps_diluted | 2.62 / 2.65 | 2.62 / 2.65 (units) | ✅ | Visa Consolidated Statements of Operations (unaudited) · Class A common stock |

## Auditor warnings

- No segment table; Visa reports no segments. Revenue by type appears only in the INCOME STATEMENT SUMMARY with the current quarter and YoY %, no prior-year dollar amounts.
- INCOME STATEMENT SUMMARY mixes GAAP and non-GAAP (non-GAAP total operating expenses 3,611, net income 5,803, EPS 2.98); not used.
- Litigation provision 903 vs 10 is as printed; non-GAAP measures exclude it.
- 'Visa Quarterly Results of Operations (unaudited)' matches every GAAP value above for both quarter columns.
- Several row labels carry a trailing space in the HTML; trimmed.
- The non-GAAP reconciliation removes (899) for litigation provision, which differs from the 903 GAAP line; don't compare the two directly.
