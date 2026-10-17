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
- `scripts/layout.mjs`, `scripts/render.mjs` and `templates/money-map/` exist. If not, say that Phase 4 builds them and stop.

Run everything from the repo root. HyperFrames commands go through `npx hyperframes` (pinned in `package.json`). Never run `publish`, `cloud`, `lambda`, `auth`, `usage`, `skills` or `init`; they're denied in settings because they reach HeyGen or AWS, read the Claude login, or install unreviewed skills.

For composition rules (data attributes, one paused GSAP timeline, determinism), read the `hyperframes-core` skill. For timing and easing, read `hyperframes-animation`. For the CLI loop, read `hyperframes-cli`.

## 1. Plan the story from the data

Read `data/normalized/$id.json` and decide, from the numbers only:

- **Hook (0–2 s):** one of the brief's hook patterns, filled with approved values. Max ~7 words on screen. Write three variants into `out/$id/script.md`. The owner can swap hooks later via `/post-pack`.
- **Flow steps (2–18 s):** segments → revenue → cost of revenue and gross profit → operating expenses and operating income → tax and other → net income. Skip any step the company doesn't report. Never fill a missing line with a calculation unless it's in `derived` with `our_calculation: true`, and then label it "our calculation" on screen.
- **One insight (18–26 s):** the fastest-growing segment, or the margin change vs last year. Pick the one the numbers support most clearly. Compare only with the prior year and the company's own guidance, never consensus.
- **End card (26–30 s):** call to action, source line, disclaimer. The last ~2 s hold still as a clean screenshot.

Write the on-screen script (every text string, with its time window) to `out/$id/script.md`. Every number in it must trace to a field in the data file: put the JSON path beside it, for example `lines[revenue_total].value`.

## 2. Voice (Kokoro, local)

Synthesize each script line separately, so the timeline can sit on measured durations:

```bash
npx hyperframes tts "<line>" -v <tokens.voice.voice> -o out/$id/build/vo/<nn>.wav
```

Measure each file with `ffprobe` and record the durations in `out/$id/build/vo/timings.json`. The composition's timing comes from that file, not from guesses, so the voice and the numbers stay in sync, and a re-render gives the same video. Everything the voice says must also be on screen, because most people watch muted. Never use HeyGen or ElevenLabs voices; media-use isn't installed for that reason.

Music, if any: only a track whose license covers commercial social use, recorded in `out/$id/sources.md`. No license, no music.

## 3. Layout (deterministic)

```bash
node scripts/layout.mjs $id
```

This computes the Sankey layout with d3-sankey at build time and writes `out/$id/build/layout.json`: node and link coordinates, label positions, colors from the chosen theme in `brand/tokens.json`. The composition only reads these baked values. There's no layout math, randomness, clock or network at render time.

## 4. Build and check the composition

`scripts/render.mjs $id` assembles `out/$id/build/` from `templates/money-map/`: data, layout, VO timings, local GSAP (`node_modules/gsap`), Inter from `brand/fonts/`. Then:

```bash
npx hyperframes lint out/$id/build
npx hyperframes check out/$id/build
```

Fix every lint error first. A lint error switches off the layout and contrast audits, so a "clean" check means nothing until lint is clean.

On screen, in every video (brief §2.1 rule 6):
- company name + ticker (our type, no logo)
- period with calendar months, e.g. "Fiscal Q4 2026 (Jul–Sep 2026)"
- "Source: [Company] earnings release, filed [date]"
- GAAP / non-GAAP labels where they apply
- "our calculation" on any subtotal the company doesn't print
- "Not investment advice"

Readability floor: labels ≥ 44 px, key numbers ≥ 72 px, ≤ 7 words on screen at once, each number held ≥ 1.5 s, text inside the safe zone in `brand/tokens.json` (top 154, bottom 384, right 130 px). Number format comes from `tokens.format`: `\$94.9B`, millions below \$1B, `+6%` / `−3%` with a real minus sign.

## 5. Render

```bash
node scripts/render.mjs $id --video
```

This re-checks the approval hash, then calls `npx hyperframes render out/$id/build -o out/$id/money-map.mp4 --fps 30 --quality delivery`. Confirm with `ffprobe`: 1080×1920, 30 fps, H.264 + AAC, 25–35 s. If it's outside 25–35 s, adjust the plan, not the playback speed.

Then the stills:
- `cover-9x16.png` (1080×1920) and `cover-4x5.png` (1080×1350): hook plus a strong frame of the map, designed for each crop
- `carousel/01.png` … `08.png` (1080×1350, 6–8 slides): cover, money map, three insight slides, sources + call to action

## 6. Visual QA (before showing anyone)

Export keyframes at 0, 25, 50, 75 and 100% of the MP4 (`ffmpeg -ss … -frames:v 1`), plus every cover and carousel slide. **Look at each image yourself** with the Read tool, and check:

- no overflow, clipping or overlapping labels
- critical text inside the safe zone
- minimum sizes met; contrast readable on the theme background
- every number matches `script.md`, which matches the data file
- required lines present on the end card (and on the cover's footer if it shows numbers)
- the final frame reads as a standalone screenshot

Fix and re-render until all of it passes. Record what you checked in `out/$id/qa.md`.

## 7. Gate B (stop here)

If this session can publish artifacts, publish a **private** preview page (the MP4 or keyframes, the covers, the carousel, and a link to the numbers sheet) so the owner can review from a phone. Otherwise give the file paths.

Then stop. Don't draft captions or post. After the owner approves the MP4, the next step is `/post-pack $id`.

## Output

```
out/$id/money-map.mp4
out/$id/cover-9x16.png, cover-4x5.png
out/$id/carousel/01.png … 08.png
out/$id/script.md        on-screen text + VO lines, each number with its data path
out/$id/qa.md            what visual QA checked
out/$id/sources.md       filing + music license + voice (Kokoro TTS, AI label on)
out/$id/build/           composition, layout, VO (gitignored)
```
