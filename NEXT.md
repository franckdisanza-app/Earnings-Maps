# Next

**Resume at Phase 4: visual system and templates** (docs/KICKOFF.md §7), ending at **Gate 2**.

1. Owner check of the pipeline: type `/earnings-ingest AAPL FY2025Q4` once, so the skill itself has run (everything it calls is built and tested).
2. Brand tokens: finalize `brand/tokens.json` contrast with the dataviz checks; GSAP and Inter come from local files.
3. `scripts/layout.mjs`: d3-sankey layout baked to `out/<ID>/build/layout.json` from a data file. Steps: segments → revenue → cost of revenue / gross profit → opex / operating income → tax and other → net income; skip what the company doesn't report; "our calculation" labels.
4. `templates/money-map/`: HyperFrames composition (1080×1920, 30 fps, one paused GSAP timeline), on-screen required lines, safe zones.
5. Gate 2: three style frames (dark editorial, light editorial, bold) of the same money map from `AAPL-FY2025Q4`, plus the three Kokoro voices in `brand/voice-samples/`. The owner picks.
6. Then `render.mjs` (refuses without a matching approval), covers, carousel and visual QA.

Pilot (Phase 5): pick from the freshest releases at that time; today PepsiCo FY2026Q3, Nike FY2027Q1 or Costco FY2026Q4. Run `find_releases.py <T> --list` to refresh.

Open questions for the owner: Visa revenue types (current quarter only in the release); segment mappings pending for NVDA, NFLX, PEP, MCD, NKE, COST, WMT; manual ingest for TSLA and ABNB. beehiiv still needs `/mcp` authentication before Phase 6.
