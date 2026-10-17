# Next

**Phase 5: the pilot.** Phase 4 is complete: three video formats, covers, carousel, script sheet and visual QA, all from one approved data file.

1. **Pick the pilot quarter.** Fresh releases today (Oct 17): PepsiCo FY2026Q3 (filed Oct 8), Nike FY2027Q1 (Oct 1), Costco FY2026Q4 (Sep 24). Coming next week: Netflix and Coca-Cola (around Oct 20–21), then Tesla (manual ingest). Refresh with `.venv/Scripts/python.exe scripts/find_releases.py <TICKER> --list`.
2. **Segments for the pick.** PepsiCo, Nike and Costco have no segment mapping yet, so their maps would start at revenue. Map the segments in `config/watchlist.yaml` first (labels exactly as printed), or run without them.
3. **The owner types `/earnings-ingest <TICKER>`** (Claude can't start it). It fetches, parses, validates, runs the blind audit and writes the numbers sheet, then stops at **Gate A**.
4. After Gate A: `/money-map <ID>` renders the money map (plus the two short formats if wanted), the covers and the carousel, runs `scripts/qa.mjs`, and stops at **Gate B** with a private review page.
5. After Gate B: `/post-pack <ID>` drafts captions, the pinned comment and the DM reply, checked by the compliance-reviewer. Nothing is posted by Claude.

Open owner items: beehiiv `/mcp` authentication (Phase 6); Visa revenue types (current quarter only in the release); segment mappings for Nvidia, Netflix, PepsiCo, McDonald's, Nike, Costco and Walmart; Tesla and Airbnb manual ingest.
