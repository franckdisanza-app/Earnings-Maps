# Audit: MSFT-FY2026Q1

Blind re-extraction from `data/raw/MSFT/FY2026Q1/msft-ex99_1.htm`, compared with `data/normalized/MSFT-FY2026Q1.json` (SHA-256 `ed42db073943afe2…`).

Run via: numbers-auditor project subagent (read-only tools, CLAUDE.md omitted, PreToolUse guard limiting reads to data/raw/), 2026-10-17; a first pass via a general-purpose agent with the same instructions matched value for value.

**20 values checked · 20 matched · 0 unresolved**

| Item | Ours (current / prior year) | Auditor | Match | Auditor locator |
| --- | --- | --- | --- | --- |
| revenue_product | 15,922 / 15,272 | 15922 / 15272 (millions) | ✅ | INCOME STATEMENTS · Product |
| revenue_service | 61,751 / 50,313 | 61751 / 50313 (millions) | ✅ | INCOME STATEMENTS · Service and other |
| revenue_total | 77,673 / 65,585 | 77673 / 65585 (millions) | ✅ | INCOME STATEMENTS · Total revenue |
| cost_product | 2,922 / 3,294 | 2922 / 3294 (millions) | ✅ | INCOME STATEMENTS · Product |
| cost_service | 21,121 / 16,805 | 21121 / 16805 (millions) | ✅ | INCOME STATEMENTS · Service and other |
| cost_of_revenue_total | 24,043 / 20,099 | 24043 / 20099 (millions) | ✅ | INCOME STATEMENTS · Total cost of revenue |
| gross_profit | 53,630 / 45,486 | 53630 / 45486 (millions) | ✅ | INCOME STATEMENTS · Gross margin |
| opex_rd | 8,146 / 7,544 | 8146 / 7544 (millions) | ✅ | INCOME STATEMENTS · Research and development |
| opex_sm | 5,717 / 5,717 | 5717 / 5717 (millions) | ✅ | INCOME STATEMENTS · Sales and marketing |
| opex_ga | 1,806 / 1,673 | 1806 / 1673 (millions) | ✅ | INCOME STATEMENTS · General and administrative |
| operating_income | 37,961 / 30,552 | 37961 / 30552 (millions) | ✅ | INCOME STATEMENTS · Operating income |
| other_income | (3,660) / (283) | -3660 / -283 (millions) | ✅ | INCOME STATEMENTS · Other expense, net |
| income_before_tax | 34,301 / 30,269 | 34301 / 30269 (millions) | ✅ | INCOME STATEMENTS · Income before income taxes |
| income_tax | 6,554 / 5,602 | 6554 / 5602 (millions) | ✅ | INCOME STATEMENTS · Provision for income taxes |
| net_income | 27,747 / 24,667 | 27747 / 24667 (millions) | ✅ | INCOME STATEMENTS · Net income |
| eps_diluted | 3.72 / 3.3 | 3.72 / 3.3 (units) | ✅ | INCOME STATEMENTS · Diluted |
| segments_total_segment | 77,673 / 65,585 | 77673 / 65585 (millions) | ✅ | SEGMENT RESULTS · Revenue |
| segment:segment:Productivity and Business Processes | 33,020 / 28,317 | 33020 / 28317 (millions) | ✅ | SEGMENT RESULTS · Revenue |
| segment:segment:Intelligent Cloud | 30,897 / 24,092 | 30897 / 24092 (millions) | ✅ | SEGMENT RESULTS · Revenue |
| segment:segment:More Personal Computing | 13,756 / 13,176 | 13756 / 13176 (millions) | ✅ | SEGMENT RESULTS · Revenue |

## Auditor warnings

- Column headers span rows: 'Three Months Ended<br>September 30,' over '2025' / '2024'.
- Sales and marketing prints 5,717 in both the 2025 and 2024 columns; verified as printed.
- Other income line is labeled 'Other expense, net'; both values in parentheses.
- Non-GAAP reconciliation tables exclude the 'Impact from investments in OpenAI' (non-GAAP net income $30,833 / $25,190; diluted EPS $4.13 / $3.37); not used.
- msft-ex99_2.htm is a blog post with no financial tables; msft-ex99_3.htm contains only slide images.
- Each year's opex lines sum to the 'Operating expenses' total in SEGMENT RESULTS (15,669 / 14,934).
