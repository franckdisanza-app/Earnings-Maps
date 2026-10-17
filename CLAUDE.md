# Earnings Maps

Faceless short-form videos (TikTok, Reels, Shorts) and a weekly newsletter that turn US companies' quarterly results into animated money maps: where revenue came from, where it went, what was left. Built from primary filings only, posted within 24 hours of a release.

Full brief: `docs/KICKOFF.md` (the brief still says "Earnings, Animated"; the brand is **Earnings Maps**). Decisions: `DECISIONS.md`. Progress: `STATUS.md`. Resume point: `NEXT.md`.

## Rules (summary of KICKOFF §2; the brief wins on any conflict)

**Accuracy is the brand.**
- Numbers come only from the earnings release (8-K Item 2.02, usually Ex. 99.1; 6-K for foreign filers), the 10-Q/10-K, or the company's IR site. Never news, social posts, aggregators or web-search results.
- Every value in `data/normalized/*.json` carries unit, scale, fiscal period + calendar months, GAAP/non-GAAP, source URL and a locator (table title + row label as printed).
- `validate.py` identities must pass before any render. Every exception is explained in the numbers sheet.
- The `numbers-auditor` subagent re-extracts from the raw filing without seeing our draft. Any mismatch blocks the render.
- Compare only with the prior year and the company's own guidance. No beat/miss vs consensus.
- Never copy sentences from a release; paraphrase guidance. A subtotal the company doesn't print is labeled "our calculation" on screen.
- On screen in every video: company + ticker, period with calendar months, "Source: [Company] earnings release, filed [date]", GAAP/non-GAAP labels, "Not investment advice".
- Corrections within 24 hours: pinned comment, newsletter note, `CORRECTIONS.md`.

**Content.** Original work from primary data only. Names in our own type, no logos, nothing implying endorsement. Education, not advice: no buy/sell/hold, price targets or share-price predictions; flag anything that might be regulated. Voice is Kokoro TTS with each platform's AI label switched on; no synthetic presenters or cloned voices. Music only with a commercial-social license, recorded in `sources.md`. Three to five specific hashtags.

**Security.** Third-party skills are reviewed and pinned in `SKILLS.md` before install; they install by copying the reviewed files. Secrets live in `.env` (gitignored); never print them. SEC requests send `SEC_USER_AGENT`, stay under 10 req/s, cache to disk and back off on 403/429/5xx.

**Never** post, send messages or email, or spend money. The owner does all of that. The one exception: private artifacts for the owner's review.

## Gates

| Gate | When | What unlocks it |
| --- | --- | --- |
| A: numbers | every video, after `/earnings-ingest` | The owner explicitly approves `numbers-sheet.md` in chat. Then run `.venv/Scripts/python.exe scripts/approve.py <ID> --by "<name>"`, which writes `data/normalized/<ID>.approval.json` with the SHA-256 of the exact data file. Never write an approval without that explicit message. |
| B: final MP4 | every video, after `/money-map` | The owner watches the MP4 and approves. Then `/post-pack`. |
| 2: style | once (Phase 4) | The owner picks one of three style frames and a voice. |

The render refuses to run when the approval hash doesn't match the data file. Any edit to the data after approval needs a new Gate A.

## Folder map

```
config/watchlist.yaml        20 companies: CIK, fiscal year end, IR URL, line mapping, segments
schemas/                     earnings.schema.json (mirrored in pydantic)
data/raw/<TICKER>/<period>/  filings as downloaded (cache, gitignored)
data/normalized/<ID>.json    one quarter's numbers; <ID> = <TICKER>-<period>, e.g. AAPL-FY2026Q4
data/normalized/<ID>.approval.json   Gate A record
data/calendar/               /earnings-calendar output
scripts/                     data: sec_client, find_releases, tables, parse_release, validate, audit_diff,
                             numbers_sheet, approve, reconcile_xbrl, verify_watchlist
                             video: money_map_model, layout, render (--format), stills, qa, script_sheet
templates/                   money-map, formats (dollar-split, kpi-cards), carousel (HyperFrames HTML)
brand/                       tokens.json, fonts/ (Inter, OFL), style-frames/, voice-samples/
out/<ID>/                    deliverables; media gitignored, text records committed
newsletter/issues/<YYYY-WW>/ issue.md + issue.html
analytics/posts.csv          per-post metrics
tests/                       pytest; fixtures/<case>/raw + expected
docs/                        KICKOFF, platform-specs, posting-checklist, sponsor-kit, plan-30-days
```

## Skills and agents

Project skills (`.claude/skills/`; the owner types the ones marked ⌨, which have side effects):
- ⌨ `/earnings-ingest <TICKER> [period]`: filing → normalized JSON → validate → audit → numbers sheet → stop at Gate A
- ⌨ `/money-map <ID>`: approval check → layout → MP4, covers, carousel → visual QA → stop at Gate B
- `/post-pack <ID>`: hooks, script, captions, pinned comment, ManyChat DM, alt text, sources → compliance review
- `/newsletter-issue <YYYY-WW>`: the week's approved breakdowns → beehiiv-ready Markdown + HTML
- ⌨ `/earnings-calendar`: next four weeks of report dates from company announcements, in Zurich time

Subagents (`.claude/agents/`, read-only): `numbers-auditor` (blind re-extraction; a hook limits it to raw filings), `compliance-reviewer` (advice language, missing lines, unlabeled numbers).

Reviewed third-party skills: `hyperframes-core`, `-animation`, `-keyframes`, `-cli`, `-registry` (rendering); `viral-hooks`, `viral-tiktok-content`, `viral-instagram-reels`, `viral-short-form` (hooks, scripts); `humanizer` (tone pass on captions and newsletter); `frontend-design`, `theme-factory` (style frames, landing page). The bundled `pdf` and `xlsx` skills cover the lead magnet and models.

## Tooling

- Python pipeline: `.venv/Scripts/python.exe` (3.14). `python3` on this machine is a Store stub, so don't use it.
- Kokoro TTS: `npx hyperframes tts "<line>" -v <voice> -o <file>.wav`. It uses `.venv-tts` through `HYPERFRAMES_PYTHON` in `.env`. Local only; no HeyGen or ElevenLabs.
- HyperFrames: run `npx hyperframes` from the repo root (pinned 0.8.167). Allowed: `lint`, `check`, `snapshot`, `preview`, `render`, `tts`, `timeline`, `doctor`, `browser`. Denied in settings: `usage`, `publish`, `cloud`, `lambda`, `auth`, `skills`, `init`, `upgrade`, `@version`.
- GSAP and Inter are loaded from local files, never a CDN. Layout is computed at build time (d3-sankey) and baked in.
- beehiiv MCP (read-only analytics): the owner authenticates with `/mcp`. The owner publishes in beehiiv's editor.
- Tokens, palette, number format, safe zones, voice: `brand/tokens.json`. Platform specs: `docs/platform-specs.md`.

## Definition of done (per video)

1. `data/normalized/<ID>.json` validates; `out/<ID>/audit.md` shows zero unresolved mismatches; `<ID>.approval.json` matches the file (Gate A).
2. `out/<ID>/`: `money-map.mp4` (1080×1920, 30 fps, H.264 + AAC, 25–35 s), `cover-9x16.png`, `cover-4x5.png`, `carousel/01–08.png`, `numbers-sheet.md`, `audit.md`.
3. Visual QA keyframes checked at 0/25/50/75/100%: overflow, overlaps, safe zones, min sizes (44 px labels, 72 px key numbers), contrast, ≤7 words on screen, numbers held ≥1.5 s.
4. Owner approved the MP4 (Gate B).
5. `script.md`, `captions.md`, `sources.md` written; `compliance-reviewer` passes.
6. Row added to `analytics/posts.csv` once the owner posts.

## Working conventions

- Work phase by phase. End each phase with a commit and a `STATUS.md` note. At a phase boundary in a long session, write `NEXT.md`.
- Decide routine things and log them in `DECISIONS.md`. Ask the owner only about money, anything public, or brief §12-type choices.
- Check current docs before relying on a CLI flag or API from memory; this tooling changes weekly.
