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
