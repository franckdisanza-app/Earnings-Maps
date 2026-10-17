# Status

## 2026-10-17 · Phase 0: repo and environment ✅

- Environment: git 2.52, Node 24.13.1, npm 11.19, Python 3.14.3, FFmpeg 9.0.2, gh 2.98, Claude Code 2.1.233, Chrome. Nothing missing; no admin installs needed. `uv` is absent and not needed.
- Repo initialized on `main` (separate from the home-folder repo). Added `docs/KICKOFF.md`, `.env.example`, `.gitignore`, `.gitattributes`, `DECISIONS.md`.
- Section 12 answered: name **Earnings Maps**, Kokoro TTS voice, FT/Economist references, all 20 companies, newsletter Sunday 15:00 Zurich, SEC identity in Phase 3. Details in `DECISIONS.md`.
- Next: Phase 1, skill review, then Gate 1.

## 2026-10-17 · Phase 1: skill review ⏸ waiting at Gate 1

- Reviewed the core set at pinned commits, with SkillSpector static scans as a second opinion. Full review and install list in `SKILLS.md`.
- Nothing installed yet. Waiting for the Gate 1 OK.

## 2026-10-17 · Phase 1: skills and tools ✅

- Gate 1 approved. Installed the reviewed core set (13 skills, beehiiv MCP, HyperFrames CLI with guardrails, pinned Python and Node deps, Inter). last30days skipped. Details in `SKILLS.md`.
- Smoke tests: `hyperframes doctor` OK, 2 s portrait test render OK, 3 Kokoro voice samples in `brand/voice-samples/` (af_heart, am_michael, bm_george) for the Gate 2 pick.
- To do for you: authenticate beehiiv with `/mcp` before Phase 6.

## 2026-10-17 · Phase 2: scaffold, memory, skills, subagents ✅

- Repo tree per brief §5; `CLAUDE.md` (89 lines), `README.md`, `CORRECTIONS.md`, `INBOX.md`, `NEXT.md`; docs (platform specs, posting checklist, sponsor-kit and 30-day outlines); `brand/tokens.json` draft with three themes; `config/watchlist.yaml` (20 companies, unverified); `analytics/posts.csv` header.
- Five project skills: `/earnings-ingest`, `/money-map`, `/earnings-calendar` (owner-invoked), `/post-pack`, `/newsletter-issue`, each with eval prompts.
- Two read-only subagents: `numbers-auditor` (guarded to raw filings, no CLAUDE.md) and `compliance-reviewer`.
- Tests: 32 passing (auditor guard, repo structure).
- Not yet done: the skills' first real runs (they need the Phase 3–7 scripts). Next: Phase 3, see `NEXT.md`.

## 2026-10-17 · Phase 3: data pipeline ✅

- Scripts: `sec_client`, `find_releases`, `tables`, `parse_release`, `validate`, `audit_diff`, `numbers_sheet`, `approve`, `reconcile_xbrl`, `verify_watchlist`, plus the pydantic model behind `schemas/earnings.schema.json`.
- Watchlist: all 20 CIKs and fiscal year ends confirmed with SEC; 18 mapped and validated against their latest release; Tesla and Airbnb need manual ingest.
- Ingest + validation + blind audit on four past releases (Apple, Microsoft, Visa, Uber): 77/77 values matched, zero unresolved; XBRL agrees where a 10-Q exists. Numbers sheets in `out/<ID>/`.
- Tests: 113 passing.
- Pilot candidates (fresh releases): PepsiCo FY2026Q3 (filed Oct 8), Nike FY2027Q1 (Oct 1), Costco FY2026Q4 (Sep 24). Coming up: Netflix, Tesla, Coca-Cola (late October), then Microsoft, Alphabet, Meta, Visa, Apple, Amazon.
- Not yet run: `/earnings-ingest` as a slash command. The owner types it; Claude can't start it.
