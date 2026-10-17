# Earnings, Animated: kickoff brief for Claude Code

**How to use this file:** put it in an empty folder, open Claude Code in that folder, and type:
`Read KICKOFF.md and follow it. Start with Phase 0 in plan mode.`

---

## 0. Your role and how we work

You are my technical cofounder and production studio for **Earnings, Animated** (working name): a faceless short-form video channel plus a weekly newsletter that explain big companies' quarterly results with animated "money maps".

- Work through the phases below in order. End each phase with a git commit and a short note in `STATUS.md`.
- Stop at every **Gate** and wait for my OK: Gate 1 (skill installs) and Gate 2 (style frames) once, then Gate A (numbers) and Gate B (final MP4) for every video.
- Start in plan mode. Read this whole file, show me a plan for Phases 0 to 2, and ask the questions in section 12 in one batch. Don't change files until I answer.
- Keep a task list. If the session runs long, stop at a phase boundary and write `NEXT.md` saying exactly where to resume.
- Decide routine things yourself (libraries, file names, structure) and log them in `DECISIONS.md`. Ask me only about section 12, money, or anything public.
- Never post publicly, send messages or email, or spend money; I do all of that. The one exception: private artifacts for my review (Phase 5).
- Tools in this space change weekly. Before relying on a command, flag or API from memory, check its current README or docs.
- Copy this file into the repo as `docs/KICKOFF.md`.

---

## 1. The business

US-listed companies report results every quarter. We turn each report into a 25 to 35 second vertical video showing where the revenue came from, where it went and what was left, posted within 24 hours of the release on TikTok, Instagram Reels and YouTube Shorts. A weekly newsletter carries the full breakdowns.

Money comes from finance sponsors in the newsletter first, then a paid tier (deeper breakdowns, model spreadsheets) and motion work for small companies' investor updates.

**Context for your judgment (not copy for posts):**

- **Demand is proven.** App Economy Insights' "How They Make Money" grew a Substack to 296K+ subscribers on static income-statement visuals. Our edge is motion: the money visibly flows, and the final frame works as a screenshot people send to friends.
- **Sponsors pay well in this niche.** Finance newsletters had a median sponsorship CPM of about $92 per thousand opens in Q1 2026 (Newsletrix sample of 312 deals).
- **Instagram rewards original, shareable work.** It ranks on watch time, sends per reach and likes per reach. Since Apr 30, 2026, accounts that mostly repost lose recommendations across Reels, photos and carousels. Everything we post is our own design built from primary data.
- **TikTok polices AI content.** It requires labels on realistic AI-generated content and lets viewers turn AI content down in their feed. We use code-built charts and type, never synthetic people.
- **Capture runs on Instagram.** TikTok accounts registered in Switzerland, the EEA or the UK can't use TikTok's DM API, so comment-to-DM automation (ManyChat) runs on Instagram only. On TikTok we use the bio link and a pinned comment.
- **Timing.** I'm in Zurich. US companies release before the US open (around midday or early afternoon in Zurich) or after the close: 4:00 pm New York is 22:00 in Zurich, except 21:00 between Oct 25 and Nov 1, 2026, when only Europe has changed its clocks.
- **Tooling.** Claude Motion (Anthropic's prompt-to-MP4 feature) is a Team/Enterprise beta. We render with HyperFrames from Claude Code instead, so the whole pipeline is scripted and repeatable.
- **Now.** Q3 2026 earnings season is under way and most of the watchlist reports over the coming weeks, so the pilot can use a fresh release.

---

## 2. Non-negotiable rules

### 2.1 Accuracy (this is the brand)

1. **Primary sources only:** the earnings release (US filers: 8-K Item 2.02, usually Exhibit 99.1; foreign private issuers: 6-K), the 10-Q or 10-K, or the company's investor-relations site. Never news articles, social posts, data aggregators or last30days output.
2. **Every number is traceable.** Each value in `data/normalized/*.json` carries unit and scale, fiscal period plus calendar months, GAAP or non-GAAP, source URL, and a locator (table title plus row label as printed).
3. **Validation passes before any render:** segments sum to total revenue within rounding; revenue minus cost of revenue equals gross profit; gross profit minus operating expenses equals operating income (each check applies where the company reports those lines); YoY is recomputed from the prior-year column of the same release. Explain every exception in the numbers sheet.
4. **Independent audit.** The `numbers-auditor` subagent re-extracts every figure from the raw source without seeing our draft. Any mismatch blocks the render until resolved.
5. **Gate A:** I approve `numbers-sheet.md`. The render refuses to run unless `approval.json` holds the SHA-256 hash of the exact data file being rendered.
6. **On screen in every video:** company name and ticker; period label with calendar months (fiscal years differ: Apple's fiscal Q4 and Microsoft's fiscal Q1 both cover Jul to Sep); "Source: [Company] earnings release, filed [date]"; GAAP or non-GAAP labels where they apply; "Not investment advice".
7. **Comparisons:** prior year and the company's own guidance only. No "beat/miss vs. consensus" unless I license a consensus data source.
8. **Corrections within 24 hours:** pinned comment, a newsletter note and an entry in `CORRECTIONS.md`.
9. **No copied text.** Never copy sentences from a release. Report the numbers and paraphrase management's guidance.
10. **Label our math.** A subtotal the company doesn't print appears on screen only when labeled "our calculation", for example gross profit for Amazon, which reports cost of sales but no gross profit line.

### 2.2 Content and compliance

- **Original work only:** our own charts, type and motion from primary data. Never re-upload or lightly edit someone else's video. Hypit-style cloning is for our own past formats only.
- **Names, not logos.** Company names and tickers in our own type. No logos by default, and nothing that implies endorsement.
- **Education, not advice:** no buy, sell or hold language, no price targets, no share-price predictions. Flag anything that might be regulated and let me decide.
- **No synthetic presenters or cloned voices.** Voice is one of: none (text plus music), my recorded voice, or a TTS voice with the platform's AI label switched on.
- **Music** only with a license that covers commercial social use; record it in `sources.md`.
- **Hashtags:** three to five specific ones per post, never a wall.

### 2.3 Security

- **Review before install.** For every third-party skill or plugin, read its SKILL.md and every script, list what it can reach (network, credentials, files outside the project, commands it pre-approves) and record the commit or release you reviewed in `SKILLS.md`. Show me the review; install after my OK (**Gate 1**). Optional scanner: NVIDIA SkillSpector (github.com/NVIDIA/SkillSpector).
- **Secrets** live in `.env` (gitignored). Never print them.
- **SEC fair access:** every request sends the `User-Agent` from `SEC_USER_AGENT`, stays under 10 requests per second, caches responses on disk, and backs off on 403, 429 and 5xx errors.

---

## 3. Phase 0: plan and environment check

- Check git, Node.js 22+, Python 3.11+ and FFmpeg on PATH. Report anything missing with the install command for my OS; don't run installers that need admin rights without asking.
- Create `.env.example` with `SEC_USER_AGENT="Firstname Lastname you@example.com"` and a `.gitignore` that covers `.env`, caches and `out/`.
- Ask me the section 12 questions in one batch.

---

## 4. Phase 1: skills and tools

Prefer project scope so the setup travels with the repo; where a tool installs per user or globally, note it in `SKILLS.md`. Install the **core** set in this phase, after Gate 1, and the rest when its phase starts, so the skill list stays small. Plugin installs use `/plugin` commands: give me the exact lines to paste, or use the `claude plugin` CLI from the shell once you've confirmed marketplace names with `claude plugin marketplace list`.

### Core (Phase 1)

| Tool | Install | What we use it for |
| --- | --- | --- |
| **HyperFrames** (HeyGen, Apache 2.0) | `npx skills add heygen-com/hyperframes` | Our render engine: HTML, CSS and GSAP to deterministic MP4. CLI: `npx hyperframes init`, `npx hyperframes preview`, `npx hyperframes render`; blocks such as `npx hyperframes add data-chart`. Needs Node and FFmpeg; check its README for current requirements. |
| **last30days** | `/plugin marketplace add mvanhorn/last30days-skill` then `/plugin install last30days` | What people are arguing about for a company this month, for story angles and hooks. Never a source of numbers. |
| **vyralcontent content skills** | `npx skills add vyralcontent/content-skills --skill viral-hooks` (also `viral-tiktok-content`, `viral-instagram-reels`, `viral-short-form`) | Hooks, scripts, Reels rules (Trial Reels, originality) and carousel outlines. |
| **humanizer** | `/plugin marketplace add blader/humanizer` then `/plugin install humanizer@humanizer` | Strip AI tone from captions and the newsletter. Use it instead of stop-slop, not alongside. |
| **Anthropic skills** | `/plugin marketplace add anthropics/skills` then `/plugin install document-skills@anthropic-agent-skills` and `/plugin install example-skills@anthropic-agent-skills` | `pdf` for the lead magnet, `xlsx` for paid-tier models later, `frontend-design` and `theme-factory` for the landing page and style frames. |
| **skill-creator** | `/plugin install skill-creator@claude-plugins-official` | Build and evaluate our own project skills in Phase 2. Skip it if `example-skills` already provides it. |

### Growth (Phase 6)

| Tool | Install | What we use it for |
| --- | --- | --- |
| **marketingskills** (MIT) | `npx skills add coreyhaines31/marketingskills` | Landing-page copy, launch plan, sponsor kit, conversion. |
| **llm-council-skill** (tenfoldmarc) or **council-of-high-intelligence** (0xNyk) | Follow the repo README | Argue the bull and bear framing of a release; pressure-test names and positioning. |
| **social-media-caption-generator-claude** (rediumvex) | Follow the repo README | Optional: per-platform caption drafts. |

### Optional or later

| Tool | Install | Note |
| --- | --- | --- |
| **superpowers** | `/plugin install superpowers@claude-plugins-official` | Plan-then-test discipline for the pipeline. Skip it if its workflow conflicts with this brief's phases. |
| **video-shotcraft** (Apache 2.0) | `npx skills add Vincentwei1021/video-shotcraft` | Cinematic intro sting or brand opener. Remotion-based with 16:9 presets, so adapt to 9:16. |
| **/brag** (MIT) | `npx skills add https://github.com/latent-spaces/brag --skill brag-slim` (or `--skill brag`) | A launch video for our own landing page and newsletter. |
| **Hypit** | `npx skills add hypit-ai/hypit` | Hook variants and German/French versions. It lists no clear license: personal testing only until that's resolved. |
| **Remotion skills** | `npx skills add remotion-dev/skills` | Only if HyperFrames falls short; check Remotion's license first. |

### Connections and libraries

- **beehiiv MCP** (I'll sign in): run `claude mcp add --transport http beehiiv https://mcp.beehiiv.com/mcp` in the terminal, then inside Claude Code run `/mcp`, pick beehiiv and choose Authenticate. We use it for analytics and segments; I publish in beehiiv's editor.
- **Python 3.11+:** `httpx` or `requests`, `beautifulsoup4` and `lxml`, `pandas`, `pydantic`, `jsonschema`, `pytest`. Optional: `edgartools` (check its docs and set its identity from `SEC_USER_AGENT`).
- **Node 22+:** the HyperFrames CLI, `d3-sankey` and `d3-shape` for layout, and an open-license font (Inter or IBM Plex Sans).

---

## 5. Phase 2: scaffold, memory, project skills and subagents

The current folder is the repo root; the tree shows it as `earnings-animated/`.

```
earnings-animated/
├── CLAUDE.md
├── STATUS.md  DECISIONS.md  SKILLS.md  CORRECTIONS.md  NEXT.md  INBOX.md
├── README.md  .env.example  .gitignore
├── docs/           KICKOFF.md, platform-specs.md, posting-checklist.md, sponsor-kit.md, plan-30-days.md
├── brand/          tokens.json, fonts/, style-frames/
├── config/         watchlist.yaml
├── schemas/        earnings.schema.json
├── data/raw/<TICKER>/<period>/          # filings as downloaded (cache)
├── data/normalized/<TICKER>-<period>.json
├── scripts/        sec_client.py, find_releases.py, parse_release.py, validate.py, layout.mjs, render.mjs, watch.py
├── templates/      money-map/, dollar-split/, kpi-cards/, carousel/
├── out/<TICKER>-<period>/
├── newsletter/issues/
├── analytics/      posts.csv
├── tests/          fixtures/ and pytest tests
└── .claude/
    ├── skills/     earnings-ingest/, money-map/, post-pack/, newsletter-issue/, earnings-calendar/
    └── agents/     numbers-auditor.md, compliance-reviewer.md
```

**CLAUDE.md** stays short (well under 150 lines): the mission in two lines, a summary of section 2 with a pointer to this file, the folder map, the list of skills and commands, a pointer to `brand/tokens.json`, and the per-video definition of done. Put procedures in skills, not in CLAUDE.md.

**Project skills** in `.claude/skills/`. Build them with skill-creator, keep each SKILL.md under 500 lines, put scripts beside them or in `scripts/`, take parameters with `argument-hint` and `$ARGUMENTS`, and set `disable-model-invocation: true` on skills with side effects:

- **`/earnings-ingest <TICKER> [period]`:** find the latest results filing, download and cache it, extract to normalized JSON, run `validate.py`, run `numbers-auditor` and diff its extraction against ours, write `numbers-sheet.md` and `audit.md`, then stop at Gate A.
- **`/money-map <TICKER-PERIOD>`:** verify the approval hash, compute the layout, render the MP4, covers and carousel with HyperFrames, run visual QA, write `out/<id>/`, then stop at Gate B.
- **`/post-pack <TICKER-PERIOD>`:** three hooks, on-screen script, captions per platform, pinned comment, ManyChat keyword and DM text, alt text and `sources.md`; then run `compliance-reviewer`.
- **`/newsletter-issue <YYYY-WW>`:** compile the week's approved breakdowns into a beehiiv-ready issue (Markdown and HTML) with a sponsor placeholder and the disclaimer.
- **`/earnings-calendar`:** rebuild the next four weeks of report dates for the watchlist from company announcements, each with a source link, in Zurich time; mark unconfirmed dates.

**Subagents** in `.claude/agents/`:

- **`numbers-auditor`** with `tools: Read, Grep, Glob` (it never edits). It receives only the path to the raw release and the list of line items to find, extracts every figure from the raw document, and returns its extraction as JSON. The main session diffs that against the normalized file and writes `audit.md`, so the auditor never sees our draft.
- **`compliance-reviewer`** with `tools: Read, Grep, Glob`. It checks scripts, captions and on-screen text for advice language, missing source, period or disclaimer lines, unlabeled non-GAAP figures, logos, and claims without a number behind them.

---

## 6. Phase 3: data pipeline

**Watchlist v1** (`config/watchlist.yaml`), 20 widely followed companies with clear segment reporting: Apple, Microsoft, Alphabet, Amazon, Meta, Nvidia, Tesla, Netflix, Coca-Cola, PepsiCo, McDonald's, Starbucks, Nike, Disney, Uber, Airbnb, Visa, Mastercard, Costco and Walmart. Banks and insurers are out of v1 because their income statements need a different template. For each company store: ticker, CIK, fiscal year end, IR URL, the segments to show and a display name.

**Endpoints** (verify against the SEC docs before coding):

- `https://www.sec.gov/files/company_tickers.json`: ticker to CIK.
- `https://data.sec.gov/submissions/CIK##########.json`: a company's filings, with the CIK zero-padded to 10 digits. 8-K entries list their item numbers; look for 2.02. Confirm the field names in the docs.
- `https://www.sec.gov/Archives/edgar/data/<CIK>/<accession-without-dashes>/`: the filing folder with its exhibits.
- `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`: XBRL facts, for reconciling against the 10-Q or 10-K once it's filed.
- Docs: https://www.sec.gov/edgar/sec-api-documentation and https://www.sec.gov/os/accessing-edgar-data

**What to watch for:**

- Earnings-release tables are usually plain HTML, not XBRL-tagged. Parse them with row labels kept exactly as printed.
- Income statements differ. Visa and McDonald's print no cost of revenue or gross profit line, and Amazon prints cost of sales but no gross profit. Store each company's own line mapping in `config/watchlist.yaml`.
- Segment tables often sit apart from the income statement, and some companies publish segment detail only in a supplemental file or the 10-Q. In that case mark segments "not in release" and ask me whether to show total revenue only or wait for the 10-Q.
- When the 10-Q arrives, reconcile against XBRL and log any differences in the data file's notes.

**Schema** (`schemas/earnings.schema.json`, mirrored in pydantic):

- `company`: ticker, name, cik
- `period`: fiscal_label, fiscal_year, fiscal_quarter, start_date, end_date, calendar_label
- `currency` and `scale` (for example "millions")
- `release`: form, filing_date, accession, url, exhibit
- `lines[]`: id, label_as_printed, value, prior_year_value, basis (GAAP or non-GAAP), locator
- `segments[]`: name, value, prior_year_value, locator
- `derived`: revenue YoY, gross, operating and net margin, and their prior-year values
- `guidance` (optional): our paraphrase plus its locator
- `notes[]` and `approval` (approved_by, approved_at, sha256)

**Tests:** fixtures from four past releases with different shapes (clean segments; cost of revenue split into products and services; no cost-of-revenue line; a net loss, from an older release if needed), plus unit tests for parsing and for every identity in `validate.py`.

---

## 7. Phase 4: visual system and templates

**Output specs:**

- Video: 1080×1920, 30 fps, H.264 with AAC, 25 to 35 seconds.
- Covers at 1080×1920 and 1080×1350; carousel at 1080×1350 with 6 to 8 slides.
- Safe zones (rule of thumb; confirm with a private test upload): critical text stays out of the bottom ~20%, the right ~12% and the top ~8%.
- Readability: labels at least 44 px at 1080 wide, key numbers at least 72 px, no more than about seven words on screen at once, every number held for at least 1.5 seconds.

**Brand tokens** in `brand/tokens.json`: one background, revenue blue, costs muted red-grey, profit green, losses red, one accent color, an open-license font, numbers as `$94.9B` (one decimal; millions below $1B) and changes as `+6%` or `−3%`.

**Gate 2:** render three style frames of the same money map (dark editorial, light editorial, bold color) and let me pick.

**Determinism:** compute the Sankey layout at build time with d3-sankey and bake the coordinates into the composition. Drive everything from one seekable GSAP timeline, with no random values or live data at render time.

**Templates** (all driven by the normalized JSON):

1. **Money Map** (hero, about 30 s):
   - 0 to 2 s: hook card.
   - 2 to 18 s: flows build left to right with count-ups: segments, revenue, cost of revenue and gross profit, operating expenses and operating income, tax and other, net income. Skip any step the company doesn't report.
   - 18 to 26 s: one insight, such as the fastest-growing segment or the margin change vs. last year.
   - 26 to 30 s: end card with call to action, source and disclaimer. The final frame holds about 2 seconds as a clean screenshot.
2. **Where $1 goes** (about 20 s): one dollar of revenue splitting into cents per cost bucket.
3. **Earnings in 30 seconds:** four KPI cards with count-ups.
4. **Carousel:** cover, money map, three insight slides, then sources and call to action.

**Hook patterns** (fill with real numbers only after Gate A):

- "[Company] made $[X]B in 3 months. Here's where every dollar went."
- "Every $1 [Company] earned last quarter, split."
- "[Company]'s [segment] grew [X]% while [other] shrank."

**Visual QA:** export keyframes at 0, 25, 50, 75 and 100% as PNGs, look at them yourself, and check overflow, overlaps, safe zones, minimum sizes and contrast before showing me anything.

---

## 8. Phase 5: the pilot video

1. Find the most recent results release among the watchlist, or show me three candidates.
2. Run `/earnings-ingest`, then **Gate A** (I approve the numbers).
3. Run `/money-map`, then **Gate B** (I watch the MP4).
4. Run `/post-pack`.

Deliverables in `out/<TICKER>-<period>/`: `money-map.mp4`, `cover-9x16.png`, `cover-4x5.png`, `carousel/01.png` to `08.png`, `script.md`, `captions.md`, `sources.md`, `numbers-sheet.md` and `audit.md`.

If this Claude Code session can publish artifacts, publish the numbers sheet and a preview page as a private artifact so I can approve from my phone. Otherwise give me the file paths.

---

## 9. Phase 6: distribution, funnel and newsletter

**Post pack per video:** three hook variants for the first 1.5 seconds; a caption per platform (TikTok, Reels, Shorts; LinkedIn optional); a pinned comment; three to five specific hashtags; the Instagram keyword "MAP" with its ManyChat DM text; alt text.

**Funnel:**

1. Instagram: viewer comments "MAP".
2. ManyChat DMs the signup link.
3. beehiiv signup page.
4. Welcome email with a lead magnet: a PDF of the season's money maps.
5. The weekly issue.

On TikTok, use the bio link and a pinned comment.

**Newsletter (beehiiv), in this order:**

1. The week in one chart.
2. Three to five company breakdowns: still money map, three bullets (what grew, what shrank, what management guided) and a source link.
3. One number to remember.
4. Sponsor slot (placeholder for now).
5. Next week's reporting calendar.
6. Disclaimer and corrections.

**Drafts for this session:** issue #0 built from the pilot, the welcome email, landing-page copy (use marketingskills) and a one-page sponsor kit template with numbers to fill later.

**Tracking:** `analytics/posts.csv` with views, average watch time, completion, shares and sends, saves, follows, link clicks and signups per post; a weekly summary in `STATUS.md`.

---

## 10. Phase 7: calendar, watcher and 30-day plan

- **Calendar:** run `/earnings-calendar` for the next four weeks, times in Zurich time.
- **Watcher:** `scripts/watch.py` polls the submissions endpoint for watchlist CIKs every 10 to 15 minutes on US market days. On a new results filing it downloads the release, runs ingest up to Gate A and notifies me with a desktop notification and a line in `INBOX.md`.
- **Scheduling:** don't schedule the watcher until I say so. Then propose the right scheduler for my machine (launchd on macOS, cron on Linux, or a Claude Code Desktop scheduled task). Don't use in-session `/loop` for this, because those tasks expire after seven days.
- **Plan:** write `docs/plan-30-days.md` with the companies we cover, posting slots in Zurich time, newsletter dates and the weekly KPI review.

**Later, not this session:** a Swiss edition (Nestlé, Novartis, Roche, UBS, ABB) built from their own investor-relations releases, since none of them files 8-Ks; German and French versions; a bank and insurer template; a paid tier with model spreadsheets.

---

## 11. Definition of done for this kickoff

- [ ] `SKILLS.md` lists every installed skill with its version or commit and review notes, plus anything skipped and why.
- [ ] Repo scaffold, `CLAUDE.md`, `DECISIONS.md`, `.env.example`, `.gitignore` and `README.md` exist.
- [ ] The five project skills and two subagents exist and have each run once successfully.
- [ ] Ingest, validation and audit work for at least three companies on past releases, and tests pass.
- [ ] One approved pilot: money-map MP4, covers, carousel and post pack.
- [ ] Newsletter issue #0, welcome email and landing-page copy are drafted.
- [ ] Four-week earnings calendar and 30-day plan are written.
- [ ] Watcher script is ready but not scheduled.

---

## 12. Decisions I'll make (ask in one batch)

1. **Name and handle:** propose five options with a one-line rationale each, and check domain availability if you can.
2. **Voice:** none, my recorded voice, or labeled TTS.
3. **Visual references:** two or three channels or brands whose look I like. I make the final pick from the style frames at Gate 2.
4. **Watchlist:** confirm or edit the 20 companies.
5. **Newsletter:** send day and time.
6. **SEC identity:** my name and email for `SEC_USER_AGENT` in `.env`.

---

## 13. References

- SEC EDGAR APIs and fair access: https://www.sec.gov/edgar/sec-api-documentation and https://www.sec.gov/os/accessing-edgar-data
- HyperFrames: https://github.com/heygen-com/hyperframes (docs at hyperframes.heygen.com)
- Claude Code docs: skills https://code.claude.com/docs/en/skills, subagents https://code.claude.com/docs/en/sub-agents, MCP https://code.claude.com/docs/en/mcp-quickstart
- Index of Claude video skills: https://claudevideo.org/skills
- Instagram ranking and originality rules: https://creatorflow.so/blog/instagram-algorithm/
- TikTok AI-content controls: https://techcrunch.com/2025/11/18/tiktok-now-lets-you-choose-how-much-ai-generated-content-you-want-to-see/
- TikTok DM API regional limits: https://instantdm.com/blog/tiktok-comment-to-dm
- Newsletter sponsorship benchmarks: https://newsletrix.com/blog/newsletter-sponsorship-rates-by-niche
- beehiiv MCP: https://www.usecarly.com/blog/chatgpt-beehiiv-integration/
- Skill safety and install commands: https://walma.ai/en/guides/skills/best-claude-skills
