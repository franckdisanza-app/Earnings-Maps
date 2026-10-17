# Next

**Waiting at Gate 2.** The owner picks one look (dark editorial, light editorial, bold) and one voice (bm_george, am_michael, af_heart) on https://claude.ai/artifact/VE8g5iapdg5FpKmAtkJ24C.

After the pick (rest of Phase 4):
1. `brand/tokens.json`: set `status: final`, `theme`, `voice.voice`; delete the other themes; log in DECISIONS.md.
2. Voiceover: one Kokoro line per beat (hook, each row, insight, end card), durations measured with ffprobe into `build/vo/timings.json`; the timeline follows them; add the audio track (AAC) and an optional licensed music bed.
3. Covers (9:16 and 4:5) and the 6–8 slide carousel (1080×1350) from the same layout.
4. Templates 2 and 3: "Where \$1 goes" (about 20 s) and "Earnings in 30 seconds" (four KPI cards).
5. Visual QA script: keyframes at 0/25/50/75/100% plus the layout tests; contrast and safe-zone report into `out/<ID>/qa.md`.
6. Known layout follow-ups: a footer slot for the call to action when the company name is long (Microsoft); the Microsoft "Tax and other" label warning; let the insight picker skip growth the auditor flags as not like-for-like (Uber's Freight acquisition).

Then Phase 5 (pilot): refresh candidates with `find_releases.py <T> --list`; today PepsiCo FY2026Q3, Nike FY2027Q1, Costco FY2026Q4.
