# Audit: AAPL-FY2025Q4

Blind re-extraction by the `numbers-auditor` subagent from `scratchpad/audit/AAPL-FY2025Q4/a8-kex991q4202509272025.htm (copy of data/raw/AAPL/FY2025Q4/)`, compared with `data/normalized/AAPL-FY2025Q4.json` (SHA-256 `0807939ad06f88ac…`).

Run via: general-purpose agent given the numbers-auditor instructions verbatim (the project subagent loads in the next session); raw file copied to an empty scratch folder; guard hook not active.

**28 values checked · 28 matched · 0 unresolved**

| Item | Ours (current / prior year) | Auditor | Match | Auditor locator |
| --- | --- | --- | --- | --- |
| revenue_products | 73,716 / 69,958 | 73716 / 69958 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) · Products |
| revenue_services | 28,750 / 24,972 | 28750 / 24972 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) · Services |
| revenue_total | 102,466 / 94,930 | 102466 / 94930 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) · Total net sales (1) |
| cost_products | 47,019 / 44,566 | 47019 / 44566 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) · Products |
| cost_services | 7,106 / 6,485 | 7106 / 6485 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) · Services |
| cost_of_revenue_total | 54,125 / 51,051 | 54125 / 51051 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) · Total cost of sales |
| gross_profit | 48,341 / 43,879 | 48341 / 43879 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) · Gross margin |
| opex_rd | 8,866 / 7,765 | 8866 / 7765 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) · Research and development |
| opex_sga | 7,048 / 6,523 | 7048 / 6523 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) · Selling, general and administrative |
| operating_expenses_total | 15,914 / 14,288 | 15914 / 14288 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) · Total operating expenses |
| operating_income | 32,427 / 29,591 | 32427 / 29591 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) · Operating income |
| other_income | 377 / 19 | 377 / 19 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) · Other income/(expense), net |
| income_before_tax | 32,804 / 29,610 | 32804 / 29610 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) · Income before provision for income taxes |
| income_tax | 5,338 / 14,874 | 5338 / 14874 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) · Provision for income taxes |
| net_income | 27,466 / 14,736 | 27466 / 14736 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) · Net income |
| eps_diluted | 1.85 / 0.97 | 1.85 / 0.97 (units) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited) · Diluted |
| segments_total_category | 102,466 / 94,930 | 102466 / 94930 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)  · Total net sales |
| segments_total_geography | 102,466 / 94,930 | 102466 / 94930 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)  · Total net sales |
| segment:category:iPhone | 49,025 / 46,222 | 49025 / 46222 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)  · iPhone |
| segment:category:Mac | 8,726 / 7,744 | 8726 / 7744 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)  · Mac |
| segment:category:iPad | 6,952 / 6,950 | 6952 / 6950 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)  · iPad |
| segment:category:Wearables, Home and Accessories | 9,013 / 9,042 | 9013 / 9042 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)  · Wearables, Home and Accessories |
| segment:category:Services | 28,750 / 24,972 | 28750 / 24972 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)  · Services |
| segment:geography:Americas | 44,192 / 41,664 | 44192 / 41664 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)  · Americas |
| segment:geography:Europe | 28,703 / 24,924 | 28703 / 24924 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)  · Europe |
| segment:geography:Greater China | 14,493 / 15,033 | 14493 / 15033 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)  · Greater China |
| segment:geography:Japan | 6,636 / 5,926 | 6636 / 5926 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)  · Japan |
| segment:geography:Rest of Asia Pacific | 8,442 / 7,383 | 8442 / 7383 (millions) | ✅ | CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)  · Rest of Asia Pacific |

## Auditor warnings

- Prior-year quarter (three months ended September 28, 2024) includes a one-time income tax charge of $10.2 billion, net, from the reversal of the European General Court's State Aid decision; GAAP prior-year provision for income taxes (14,874), net income (14,736) and diluted EPS (0.97) are not comparable. The reconciliation table gives non-GAAP adjusted figures for that quarter: tax 4,628, net income 24,982, diluted EPS 1.64. The release's headline EPS growth uses the non-GAAP prior-year figure.
- Scale header: '(In millions, except number of shares, which are reflected in thousands, and per-share amounts)'.
- Statement has Three and Twelve Months Ended columns with identical date headers; only three-month columns used.
- Quarter length (13 vs 14 weeks) is not stated in the file.
- 'Products' and 'Services' appear under both 'Net sales:' and 'Cost of sales:'; 'Services' also appears in the category breakdown. Section headings distinguish them.
