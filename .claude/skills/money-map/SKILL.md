---
name: money-map
description: Render an approved quarter into the Earnings Maps deliverables (the money-map MP4, two covers and a carousel) with HyperFrames, run visual QA, then stop at Gate B for the owner to watch. Use only after Gate A has approved the numbers for that ID.
argument-hint: "<TICKER-PERIOD, e.g. AAPL-FY2026Q4>"
arguments: [id]
disable-model-invocation: true
---

# /money-map $id

This turns approved numbers into the video people share. Two things matter most. Every figure on screen is the approved figure, byte for byte from the data file. And the final frame works as a screenshot someone sends a friend. The run ends at **Gate B**: the owner watches the MP4.

## 0. Preconditions (stop and say what's missing)

- `data/normalized/$id.json` and `data/normalized/$id.approval.json` exist, and the SHA-256 of the data file equals the approval's `sha256`. `scripts/render.mjs` checks this itself and refuses to run otherwise. Don't work around it. A mismatch means the data changed after approval, so go back to Gate A.
- `brand/tokens.json` has `status` other than `draft`, and `voice.voice` is set. If it's still a draft, Gate 2 hasn't happened: say so and stop.

Run everything from the repo root. HyperFrames commands go through `npx hyperframes` (pinned in `package.json`). Never run `publish`, `cloud`, `lambda`, `auth`, `usage`, `skills` or `init`; they're denied in settings because they reach HeyGen or AWS, read the Claude login, or install unreviewed skills.

For composition rules (data attributes, one paused GSAP timeline, determinism), read the `hyperframes-core` skill. For timing and easing, read `hyperframes-animation`. For the CLI loop, read `hyperframes-cli`.

## 1. The story comes from the view model

`scripts/money_map_model.py $id` turns the approved data file into `out/$id/build/model.json`, and every on-screen and spoken string goes through `scripts/fmt.py`. Don't hand-write numbers anywhere. What it decides:

- **Hook:** "<Company> made $X in 3 months." The number is revenue in revenue blue.
- **Flow:** segments → revenue → cost of revenue and gross profit → operating expenses and operating income → tax and other → net income. It skips any step the company doesn't report. Subtotals the company doesn't print are labelled "our calculation". An operating loss ends the map, shown hatched in the cost colour as the hero.
- **Insight:** the fastest-growing big segment, unless the auditor flagged it as not like-for-like (acquisition, one-off), otherwise the operating margin change. Prior year only, never consensus.
- **End:** call to action, source line, disclaimer; the final frame holds still as the screenshot.
- **Short formats:** `formats.dollar_split` (cents of each $1 of revenue; only when every step is positive) and `formats.kpi_cards` (revenue, operating income or loss, net income or loss, diluted EPS).

If the story reads wrong, fix the model or its tests, not the output files.

## 2. Build, voice and render

```bash
node scripts/render.mjs $id --video                         # money map (needs Gate A)
node scripts/render.mjs $id --video --format dollar-split   # ~20 s, optional
node scripts/render.mjs $id --video --format kpi-cards      # ~20 s, optional
```

Each run: re-checks the approval hash and `brand/tokens.json` `status: final`, rebuilds the model and the layout (`scripts/layout.mjs`: d3-sankey, measured labels, `layout.json`), synthesizes one Kokoro line per beat with `npx hyperframes tts` (cached by text, normalized to -15 LUFS), times every beat from the measured clip lengths (`build/beats-<format>.json`; money map 25–35 s, short formats 15–35 s; the voice speeds up slightly before it runs over), builds the HyperFrames page, lints it, and renders `out/$id/<format>.mp4` (30 fps, H.264 + AAC). It also rewrites `out/$id/script.md`: every figure beside its data field, and each built format's voice lines with time windows.

Never use HeyGen or ElevenLabs voices; media-use isn't installed for that reason. Everything the voice says is also on screen, because most people watch muted. Music, if any: only a track whose license covers commercial social use, recorded in `out/$id/sources.md`. No license, no music.

Then the stills (same approval gate):

```bash
node scripts/stills.mjs $id
```

This writes `cover-9x16.png` (the map's final frame), `cover-4x5.png` and `carousel/01.png` … `06.png` (1080×1350: cover, map, segments or costs, margins, where $1 goes, sources + call to action).

For composition rules, read `hyperframes-core`; for timing and easing, `hyperframes-animation`; for the CLI loop, `hyperframes-cli`.

## 3. Rules every frame keeps

On screen, in every video (brief §2.1 rule 6):
- company name + ticker (our type, no logo)
- period with calendar months, e.g. "Fiscal Q4 2026 (Jul–Sep 2026)"
- "Source: [Company] earnings release, filed [date]"
- GAAP / non-GAAP labels where they apply
- "our calculation" on any subtotal the company doesn't print
- "Not investment advice"

Readability floor: labels ≥ 44 px, key numbers ≥ 72 px, ≤ 7 words on screen at once, each number held ≥ 1.5 s, text inside the safe zone in `brand/tokens.json` (top 154, bottom 384, right 130 px). Number format comes from `fmt.py`: `$94.9B`, millions below $1B, `+6%` / `−3%` with a real minus sign.

## 4. Visual QA (before showing anyone)

```bash
node scripts/qa.mjs $id
```

For each built format this snapshots keyframes at 0, 25, 50, 75 and 100% into `out/$id/qa/<format>/`, runs `npx hyperframes check` (lint, runtime errors, overflow, overlaps, WCAG contrast), checks the safe zone and footer widths from the layout geometry, and checks the MP4 (1080×1920, 30 fps, H.264 + AAC, length, size, -18 to -10 LUFS, true peak ≤ -1 dBTP). It writes `out/$id/qa.md` and exits 1 if anything needs fixing. Two kinds of finding are expected and listed separately: during the insight beat the map is dimmed on purpose, and the insight panel fully covers some dimmed labels. A label the panel only partly covers is a real issue.

The script doesn't replace your eyes. **Look at each keyframe, cover and carousel slide yourself** with the Read tool, and check:

- no clipping or labels touching (descenders included)
- every number matches `script.md`, which matches the data file
- the voice never pins a number on the wrong thing (read the voice table in `script.md` as a listener would)
- required lines present on the end card and the cover footer
- the final frame reads as a standalone screenshot

Fix the model, layout or template and re-render until all of it passes.

## 5. Gate B (stop here)

If this session can publish artifacts, publish a **private** preview page (the MP4 or keyframes, the covers, the carousel, and a link to the numbers sheet) so the owner can review from a phone. Otherwise give the file paths.

Then stop. Don't draft captions or post. After the owner approves the MP4, the next step is `/post-pack $id`.

## Output

```
out/$id/money-map.mp4    (+ dollar-split.mp4, kpi-cards.mp4 when built)
out/$id/cover-9x16.png, cover-4x5.png
out/$id/carousel/01.png … 06.png
out/$id/script.md        on-screen text + VO lines, each number with its data path
out/$id/qa.md            what visual QA checked
out/$id/sources.md       filing + music license + voice (Kokoro TTS, AI label on)
out/$id/build/           composition, layout, VO (gitignored)
```
