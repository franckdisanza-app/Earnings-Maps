# Numbers sheet: {Company} ({TICKER}) {fiscal_label}

**Period:** {fiscal_label} ({calendar_label}) · **Filing:** {form} filed {filing_date} · accession {accession}
**Source:** [{exhibit}]({url}) · **Scale:** {currency} {scale}
**Data file:** `data/normalized/{ID}.json` · SHA-256 `{sha256}`

## Lines

| Line | This quarter | Same quarter last year | YoY | Basis | Locator (table · row as printed) |
| --- | ---: | ---: | ---: | --- | --- |
| Revenue | {value, e.g. $X.XB} | {prior} | {±N%} | GAAP | {table title} · "{row label as printed}" |
| … | | | | | |

## Segments

| Segment | This quarter | Last year | YoY | Locator |
| --- | ---: | ---: | ---: | --- |

Segments sum to {sum} vs total revenue {total}: {pass / difference and reason}.

## Our calculations (labeled "our calculation" on screen)

| Value | Formula | Result |
| --- | --- | ---: |

## Validation

| Check | Result | Note |
| --- | --- | --- |
| Segments = total revenue | ✅ / ⚠️ | |
| Revenue − cost of revenue = gross profit | ✅ / n/a | |
| Gross profit − opex = operating income | ✅ / n/a | |
| YoY recomputed from prior-year column | ✅ | |

## Audit (numbers-auditor, blind)

{n} values checked · {m} matched · {k} mismatches resolved (how) · **{u} unresolved**. Full diff: `out/{ID}/audit.md`.

## Guidance (our paraphrase)

{paraphrase} · locator: {table/section · sentence location}

## Questions for the owner

- {e.g. segment detail not in the release: show total only, or wait for the 10-Q?}

---
Reply "approve {ID}" to pass Gate A. Any later change to the data file needs a new approval.
