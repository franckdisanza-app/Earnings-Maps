---
name: newsletter-issue
description: Compile one week of approved Earnings Maps breakdowns into a beehiiv-ready newsletter issue (Markdown and email-safe HTML) with the week in one chart, three to five company breakdowns, one number to remember, a sponsor placeholder, next week's reporting calendar, and the disclaimer and corrections. Use it whenever the owner asks for the weekly issue, a newsletter draft, or issue #0, for an ISO week like 2026-W43.
argument-hint: "<YYYY-WW, e.g. 2026-W43>"
arguments: [week]
---

# /newsletter-issue $week

The newsletter is where the money comes from, through sponsors first and then a paid tier, so it has to be worth opening every Sunday. It goes out **Sunday 15:00 Zurich** (09:00 New York; 10:00 during Oct 25–Nov 1). It carries the full breakdowns the videos only hint at. This skill writes a draft; the owner pastes it into beehiiv's editor and sends it. Nothing here publishes or sends.

## 0. Gather the week

- The week is ISO 8601 (`2026-W43` = Monday to Sunday). Accept `2026-43` too.
- **Breakdowns:** every `data/normalized/<ID>.json` whose release `filing_date` falls in that week **and** has a matching `<ID>.approval.json` (`scripts/approve.py --verify <ID>`). An unapproved quarter never goes in. If fewer than three are approved, say so and ask whether to send a shorter issue or wait.
- **Stills:** the money map still for each ID (`out/<ID>/cover-4x5.png`, or the final frame).
- **Calendar:** next week's reports from `data/calendar/latest.json` (made by `/earnings-calendar`). If it's older than three days, flag it; the owner runs `/earnings-calendar` to refresh it.
- **Corrections:** entries in `CORRECTIONS.md` dated in this week.
- **Issue number:** the next number after the latest folder in `newsletter/issues/`. The first issue is #0.

## 1. Structure (this order, from the brief)

1. **The week in one chart:** one cross-company view built only from approved numbers, such as YoY revenue growth or operating margin side by side for the week's companies. Make it a static PNG with the brand tokens (`newsletter/issues/$week/week-chart.png`), plus a one-sentence takeaway.
2. **Three to five company breakdowns.** Each one has:
   - heading: Company (TICKER) · fiscal period (calendar months)
   - the still money map
   - three bullets: **what grew**, **what shrank**, **what management guided** (our paraphrase, never a copied sentence)
   - "Source: [Company] earnings release, filed [date]" linked to the exhibit URL
3. **One number to remember:** a single approved figure with one line of context.
4. **Sponsor:** placeholder block `[SPONSOR: name, 2–3 lines, link]`. Leave it empty; the owner fills it.
5. **Next week's reporting calendar:** company, date, before/after market, time in Zurich, "unconfirmed" where it is.
6. **Disclaimer and corrections:** "Not investment advice. Figures come from company filings; subtotals marked 'our calculation' are ours." Then this week's corrections, or "No corrections this week."

Comparisons are with the prior year and company guidance only, never consensus. No buy/sell/hold language, price targets or share-price predictions.

## 2. Write it

- `newsletter/issues/$week/issue.md`: the canonical draft.
- `newsletter/issues/$week/issue.html`: email-safe HTML. Single column, max-width 600 px, inline styles only, system font stack with Inter first, images as `<img>` with alt text and `[UPLOAD: filename]` src placeholders (beehiiv hosts images after upload), no scripts or external CSS.
- `newsletter/issues/$week/meta.md`: subject line (≤ 50 chars) plus 2 alternates, preview text (≤ 90 chars), send time (Sunday 15:00 Europe/Zurich, with the date), and the list of image files to upload.

Run the `humanizer` skill over the prose: keep every number, ticker, period and link unchanged, and check the numbers before and after.

## 3. Review and hand off

Delegate to the `compliance-reviewer` subagent with the issue files, the week's data files and their raw folders. Save its report to `newsletter/issues/$week/compliance.md`. Fix the findings and run it again until it passes.

Then tell the owner: issue number, which companies are in, the subject line, anything missing (sponsor, a stale calendar, fewer than three breakdowns), and that it's ready to paste into beehiiv for Sunday 15:00. If the beehiiv MCP is connected, it can be used read-only to pull last issue's open and click numbers into `STATUS.md`. It never creates, edits or sends a post.
