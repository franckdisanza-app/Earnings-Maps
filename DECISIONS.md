# Decisions

Routine calls made without asking, plus the answers to the kickoff questions (docs/KICKOFF.md section 12). Newest at the bottom.

## 2026-10-17 · Section 12 answers

| # | Question | Answer |
| --- | --- | --- |
| 1 | Name | **Earnings Maps**. earningsmaps.com was unregistered on 2026-10-17 (Verisign RDAP). Social handles not checked. The owner registers the domain and handles. |
| 2 | Voice | **Labeled TTS, Kokoro-82M** (hexgrad/kokoro, Apache 2.0), run locally through `npx hyperframes tts` (kokoro-onnx, MIT). AI label switched on for every post. No cloned voices. |
| 3 | Visual references | **FT and The Economist**: restraint, muted palette, strong type hierarchy. Avoid their signatures (FT salmon background, Economist red box). |
| 4 | Watchlist | **All 20** from the brief. |
| 5 | Newsletter | **Sunday 15:00 Zurich** (09:00 New York; 10:00 during Oct 25 to Nov 1). |
| 6 | SEC identity | **Ask in Phase 3**, before the first EDGAR request. |

## 2026-10-17 · Routine decisions

- **Own git repo.** `C:\Users\franc` (the home folder) is itself a git repo, so this folder got its own `git init -b main`. Commits never land in the home repo, and Claude Code stops treating the home folder as the project root.
- **Python 3.14** (`python`, installed at C:\Python314) in a project `.venv`. `python3` on this machine is the Microsoft Store stub, so scripts and docs call `python`.
- **LF line endings** via `.gitattributes`. Global `core.autocrlf=true` would otherwise rewrite JSON on checkout and break the Gate A SHA-256 approval hashes.
- **`data/raw/` is gitignored** as a cache. Every normalized JSON carries the source URL, so raw filings can be re-downloaded. Test fixtures in `tests/fixtures/` are committed.
- **`npx skills add … --copy`** instead of the default symlinks, which need Developer Mode on Windows. Copies also make skill files diffable in the repo.
- **Project scope for plugins too** (`claude plugin marketplace add --scope project`, `claude plugin install --scope project`), so the setup travels with the repo.
- **Skipped installs:** `skill-creator` and `document-skills` (pdf, xlsx, docx, pptx and skill-creator are bundled in the Claude desktop app). From `example-skills`, only `frontend-design` and `theme-factory` are installed, so the skill list stays small. Revisit if the repo runs somewhere without the desktop app's bundled skills.
- **HyperFrames core skills by explicit name**, not the plugin with all 21 skills. Any workflow skill its router wants to install later goes through the same review first.
- **Council skill:** prefer 0xNyk/council-of-high-intelligence (MIT) over tenfoldmarc/llm-council-skill (no license) when Phase 6 starts.

## 2026-10-17 · Phase 1 review

- **Install by copying reviewed files** into `.claude/skills/` from the pinned commits in SKILLS.md, instead of `npx skills add` or `/plugin`. What's installed is exactly what was reviewed, no third-party installer runs, and updates go through review again.
- **HyperFrames:** domain skills only. The router (`hyperframes`) and `media-use` are skipped, the CLI is pinned to 0.8.167, and telemetry, self-update and skill refresh are switched off in `.env`. `usage`, `publish`, `cloud`, `lambda`, `auth`, `skills` and `init` are denied in project settings.
- **vyralcontent:** the "Mentioning Vyral" upsell section and promo header are removed from our copies (MIT).
- **SkillSpector** ran in static mode only (no LLM keys). It needed a short-path temp venv because of Windows' 260-character path limit; long-path support (a system setting) was left alone.
- **last30days:** recommended skip at Gate 1 (broad pre-approvals, extra installers, optional credential and cookie access). WebSearch covers story angles. Your call at Gate 1.

## 2026-10-17 · Phase 1 install (Gate 1 approved: "Ok phase 2")

- **Second venv for Kokoro.** kokoro-onnx 0.6.1 doesn't support Python 3.14, so `.venv-tts` runs on the existing Python 3.10.6 and HyperFrames reaches it through `HYPERFRAMES_PYTHON` (absolute path in `.env`). The pipeline stays on 3.14.
- **GSAP from `node_modules`** (3.14.2, exact pin), copied next to each composition at build time. No CDN at render time.
- **Render browser:** HyperFrames' pinned chrome-headless-shell 152.0.7977.30 in `~/.cache/hyperframes/chrome`. System Chrome hangs on `--version` under Windows.
- **esbuild postinstall left blocked** by npm 11's allowScripts; the render works without it.
- **HyperFrames opt-outs are set twice:** in `.claude/settings.json` `env` (applies to every command Claude runs here) and in `.env` (applies when the CLI runs from the repo root).

## 2026-10-17 · Phase 2 scaffold

- **Gate A approval lives in a sidecar**, `data/normalized/<ID>.approval.json` (approved_by, approved_at, sha256). The brief puts `approval` in the data file, but a file can't contain its own hash, so the data file's `approval` stays null and the sidecar holds the record. It's written by `scripts/approve.py` only after the owner's explicit "approve <ID>" in chat. `--verify` is used by render and post-pack.
- **`out/` keeps its text records in git** (numbers sheets, audits, scripts, captions, sources, compliance reports); media and build folders are ignored. The paper trail for every published number stays versioned.
- **Who can invoke what:** `/earnings-ingest`, `/money-map` and `/earnings-calendar` have `disable-model-invocation: true` (network, renders), so only the owner starts them. `/post-pack` and `/newsletter-issue` write local drafts only, so Claude can run them too. No project skill pre-approves tools.
- **The auditor's blindness is enforced, not just instructed:** `numbers-auditor` runs with `omitClaudeMd: true` and a PreToolUse hook (`.claude/hooks/auditor_guard.py`) that allows reads only under `data/raw/` and `tests/fixtures/<case>/raw/`. Covered by `tests/test_auditor_guard.py`.
- **Skill evals deferred to first real use.** skill-creator's loop compares runs with and without the skill, which needs the pipeline scripts (Phases 3–7). Each skill has `evals/evals.json` with prompts; assertions and runs happen at its first real use.
- **Watchlist:** names, fiscal-year-end rules and IR URLs entered now and marked `verified: false`; CIKs, line mappings and segments stay empty until Phase 3 verifies them against SEC data (that needs `SEC_USER_AGENT`).
- **`tzdata` pinned** in `requirements.txt`: Windows has no system time-zone database, and Zurich/New York conversions (including the Oct 25–Nov 1 five-hour week) depend on it.
- **`$` in skill files is escaped** (`\$94.9B`) because skill argument substitution treats `$<digit>` as a positional placeholder.

## 2026-10-17 · Phase 3 data pipeline

- **SEC identity:** the owner chose their git name plus account email for `SEC_USER_AGENT` (in `.env` only). The SEC client refuses the placeholder and runs at 5 requests/s, half SEC's limit.
- **Fiscal periods from the company's own filings.** A results 8-K (Item 2.02) belongs to the latest 10-Q/10-K period that ended within 75 days before it; the newest quarter's end is estimated and then confirmed from the release's column header. Period ends map to a nominal month by stepping back 7 days, which handles 52/53-week years (Apple, Disney, Costco, PepsiCo).
- **Preliminary 2.02 filings are skipped** (filed less than 10 days after quarter end, such as Tesla's deliveries), and the original 8-K wins over an 8-K/A.
- **Our own HTML table parser** (lxml with colspan grids) instead of edgartools: EDGAR release tables split values across cells and stack period headers, and every layout we hit (Coca-Cola's date row missing its label cell, McDonald's period heading in the label column, PepsiCo's numeric dates, Starbucks' half-labeled columns) is covered by a test.
- **Per-company mappings with labels exactly as printed** in `config/watchlist.yaml`; 18 of 20 companies mapped against their latest release. Tesla and Airbnb are `ingest: manual` because their 8-K exhibits have no HTML financial tables. Segments are pending for Nvidia, Netflix, PepsiCo, McDonald's, Nike, Costco and Walmart.
- **Sign conventions:** values stay exactly as printed; `expense_printed_negative` tells validation to use the magnitude. A printed dash counts as 0.
- **Three independent checks so far:** our parser, the blind numbers-auditor (77/77 values matched on four quarters, first via a general-purpose agent and then via the real guarded subagent), and SEC XBRL from the 10-Q where one exists (Microsoft 8/8, Uber 5/5). Fiscal Q4s have no three-month XBRL facts.
- **Fixtures:** Apple FY2025Q4 (products/services cost split), Microsoft FY2026Q1 (clean segments), Visa FY2025Q4 (no cost of revenue), Uber FY2022Q3 (net loss). Raw exhibits are committed under `tests/fixtures/` (public SEC filings).
- **Visa revenue types** aren't used: the release prints them for the current quarter only, with a YoY %, and our rule recomputes YoY from a prior-year column. Open question for the owner.

## 2026-10-17 · Phase 4 visual system (before Gate 2)

- **The map reads top to bottom.** The brief says "flows build left to right", but five stages of 44 px labels don't fit side by side at 1080 px wide. Reading downward mirrors the income statement (revenue at the top, net income at the bottom). Shown to the owner at Gate 2 as a departure.
- **Colors validated with the dataviz skill's checker** (`validate_palette.js --pairs all` on each theme's background): revenue blue, costs orange, profit aqua-green pass every gate in all three looks (worst colour-blind ΔE 9.4–10.5). The brief's muted red-grey costs failed (they read as grey and collapse into green for red-green colour-blind viewers). **Losses** use the cost color with a 45° hatch plus the word "loss": no fourth hue stays distinct.
- **Segments wear one color** (the revenue blue) and are told apart by labels, because they are nominal categories.
- **Backgrounds avoid stock looks:** dark editorial on slate #12161D, light editorial on cool paper #F4F6F5 (not cream), bold on indigo #1B1446.
- **Profit lines show margin, not year-on-year growth.** Revenue and segments show growth. One-offs in the prior-year quarter (Apple's 2024 State Aid tax charge) make profit growth misleading.
- **Layout is computed at build time** (`scripts/layout.mjs`: d3-sankey, labels measured with fontkit at the heaviest weight any theme draws), baked into `layout.json`, and tested for determinism, safe-zone bounds and label/bar overlap. Costs sit directly under the flow that feeds them; profit bars grow to hold their own label; cost labels use the column a peeled-off cost leaves free.
- **One view model** (`scripts/money_map_model.py`) formats every on-screen string with `fmt.py`, so the video, the numbers sheet and the captions agree. Subtotals we compute are labelled "our calculation".
- **Render gate:** `scripts/render.mjs` refuses a non-preview render unless the data file's SHA-256 matches its Gate A approval. Preview renders carry a "Style preview" marker and are for private review only.
- **Segment display names** may be shortened in the watchlist (`short:`), e.g. "Wearables", "Personal Computing"; locators keep the label as printed.

## 2026-10-17 · Gate 2

- **The owner picked light editorial and the am_michael voice.** `brand/tokens.json` is now `status: final` with only that look; the other two looks stay on record as frames in `brand/style-frames/`.
