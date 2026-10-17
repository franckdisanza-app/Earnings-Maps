# Skills and tools

Every third-party skill, plugin, MCP server and library: what was reviewed, at which commit, what it can reach, and the verdict. Rules: docs/KICKOFF.md section 2.3.

**Status: core set installed 2026-10-17 after the Gate 1 OK** (last30days skipped). Reviewed 2026-10-17.

## Installed (what is actually on disk)

| Item | Where | Version / commit | Scope |
| --- | --- | --- | --- |
| hyperframes-core, -animation, -keyframes, -cli, -registry | `.claude/skills/` | heygen-com/hyperframes `fa93669` (unmodified, LICENSE added) | project |
| viral-hooks, viral-tiktok-content, viral-instagram-reels, viral-short-form | `.claude/skills/` | vyralcontent/content-skills `349e495`, **patched**: "Mentioning Vyral" section and promo header removed (commit after `97d7666`) | project |
| humanizer | `.claude/skills/humanizer/` | blader/humanizer `8c307f3` (v3.1.0) | project |
| frontend-design, theme-factory | `.claude/skills/` | anthropics/skills `dbd4588` | project |
| beehiiv MCP | `.mcp.json` | `https://mcp.beehiiv.com/mcp`, not yet authenticated | project |
| HyperFrames CLI + guardrails | `package.json` devDependency; opt-outs in `.claude/settings.json` `env` and `.env`; deny rules in `.claude/settings.json` | 0.8.167 | project |
| d3-sankey, d3-shape, gsap | `package.json` devDependencies | 0.12.3, 3.2.0, 3.14.2 (exact) | project |
| Pipeline Python | `.venv` (Python 3.14.3) | `requirements.txt` (exact pins) | project |
| Kokoro Python | `.venv-tts` (Python 3.10.6), used via `HYPERFRAMES_PYTHON` in `.env` | `requirements-tts.txt`: kokoro-onnx 0.6.1, soundfile 0.14.0 (pulls onnxruntime 1.23.2, phonemizer 3.4.0, espeakng-loader 0.2.4, numpy 2.2.6) | project |
| Kokoro model + voices | `~/.cache/hyperframes/tts` | v1.0, 338 MB | **user** |
| Render browser | `~/.cache/hyperframes/chrome/` | chrome-headless-shell win64-152.0.7977.30 (Chrome for Testing, via `npx hyperframes browser ensure`) | **user** |
| Inter | `brand/fonts/` | v4.1 variable (woff2 + ttf), OFL.txt | project |

Notes from the install:
- **kokoro-onnx 0.6.1 requires Python <3.14**, so it got its own venv on the Python 3.10 already installed here (pip resolved it correctly; my pre-check had only looked at wheel tags).
- **GSAP is loaded from `node_modules`, not a CDN.** HyperFrames' own skeleton uses jsDelivr, which would be a network call at render time. Pinned at 3.14.2, the version the HyperFrames docs target.
- **`doctor` can't run system Chrome** (`chrome.exe --version` hangs on Windows), so renders use HyperFrames' pinned headless shell. It is also more deterministic than an auto-updating desktop Chrome.
- **npm 11 blocked esbuild's postinstall.** esbuild's platform binary comes as an optional dependency, and the render smoke test passed without the script, so it stays blocked.
- **Smoke tests passed:** `hyperframes doctor` (all required checks), pipeline and TTS imports, a 2-second 1080×1920 30 fps H.264 test render (60 frames, Inter loaded, no CDN), and 3 Kokoro samples in `brand/voice-samples/`.

## How the review was done

- Each repo was downloaded as a tarball at the commit below into its own empty scratch folder. Nothing from it was executed.
- I read every SKILL.md, plugin manifest, hook file and MCP config, then grepped every script for network hosts, environment variables, credential stores, home-folder paths, process spawning and `allowed-tools`.
- **SkillSpector v2.12.0** (NVIDIA/SkillSpector @ `cf5cac7`) ran in static mode (`--no-llm`, no API keys) as a second opinion. Its pattern rules are noisy on documentation-heavy skills; each HIGH and CRITICAL hit was checked against the actual line (triage below).

## Install method: copy the reviewed files

Skill-only tools are copied byte-for-byte from the reviewed commit into `.claude/skills/<name>/`, rather than installed with `npx skills add` or `/plugin`:

- What's installed is exactly what was reviewed. `npx skills add` resolves the skills.sh registry, which can lag GitHub by hours, and a plugin marketplace pulls the current HEAD.
- No third-party installer runs.
- Files are diffable in git, and an update means a new review plus a new copy. That's the gate we want.

## Core set (Phase 1)

| Tool | Source @ commit | License | Verdict |
| --- | --- | --- | --- |
| HyperFrames domain skills: `hyperframes-core`, `hyperframes-animation`, `hyperframes-keyframes`, `hyperframes-cli`, `hyperframes-registry` | heygen-com/hyperframes @ `fa93669` | Apache-2.0 | **Install** (copy), with the CLI guardrails below |
| HyperFrames CLI | npm `hyperframes@0.8.167` (pinned devDependency) | Apache-2.0 | **Install**, with opt-outs set in `.env` |
| Kokoro TTS: `kokoro-onnx==0.6.1` + `soundfile==0.14.0` | PyPI; thewh1teagle/kokoro-onnx @ `3596b26` | MIT (model Apache-2.0) | **Install** |
| vyralcontent: `viral-hooks`, `viral-tiktok-content`, `viral-instagram-reels`, `viral-short-form` | vyralcontent/content-skills @ `349e495` | MIT | **Install** (copy), with the vendor-pitch section removed |
| humanizer | blader/humanizer @ `8c307f3` (v3.1.0) | MIT | **Install** (copy) |
| Anthropic `frontend-design`, `theme-factory` | anthropics/skills @ `dbd4588` | Apache-2.0 (per skill) | **Install** (copy) |
| beehiiv MCP | `https://mcp.beehiiv.com/mcp` (confirmed on beehiiv.com) | n/a | **Add** at project scope; you authenticate |
| last30days | mvanhorn/last30days-skill @ `0341304` (v3.28.0) | MIT | **Skip for now** (recommended), see below |
| skill-creator, document-skills (pdf, xlsx, docx, pptx) | n/a | n/a | **Skip**: bundled with the Claude desktop app |
| Rest of `example-skills` (10 skills) | n/a | n/a | **Skip**: unused, keeps the skill list small |

### HyperFrames

- **Skills:** Markdown plus a few Node helpers. No `allowed-tools`, hooks or MCP servers.
  - `hyperframes-animation/scripts/package-loader.mjs` can run `npm install` (argv array, no shell) to add an animation runtime package on demand. We only use GSAP.
  - `hyperframes-cli` documents HeyGen cloud rendering, `publish` and AWS Lambda. We don't use any of them.
- **Skipped from HyperFrames:**
  - `hyperframes` (router): it tells the agent to run `npx hyperframes usage` at the start of every creation, and to install workflow skills on demand with `npx hyperframes skills update`, which skips review.
  - `media-use`: 67 scripts that call HeyGen, ElevenLabs, OpenAI, Groq, Google and Pixabay, mostly paid. We call `npx hyperframes tts` directly instead.
- **CLI findings and guardrails:**
  - **Telemetry:** sends anonymous usage events to PostHog (`us.i.posthog.com`). Opt out with `HYPERFRAMES_NO_TELEMETRY=1` and `DO_NOT_TRACK=1`.
  - **Silent self-update:** the CLI updates itself in the background. Opt out with `HYPERFRAMES_NO_UPDATE_CHECK=1` and `HYPERFRAMES_NO_AUTO_INSTALL=1`. A pinned version is still the main defence.
  - **Unreviewed skill installs:** `hyperframes init` refreshes skills from GitHub main on every run, possibly into user-level folders, and `--skip-skills` is deliberately ignored. Opt out with `HYPERFRAMES_SKIP_SKILLS=1`. We also don't run `init` inside the repo; templates are written by hand.
  - **Reads your Claude login:** `hyperframes usage` reads the Claude Code OAuth token from the Windows credential store or `~/.claude/.credentials.json`, plus Codex and Grok tokens, and sends it to that provider's usage endpoint (api.anthropic.com). It only goes to the token's own issuer, but it is still third-party code reading your login. Never run it.
  - **Public output:** `publish`, `cloud`, `lambda` and `auth` reach HeyGen or AWS, and `publish` makes a public link. Never run them.
  - **Enforcement:** the CLI loads `.env` from the current folder, so the opt-outs go there; `scripts/render.mjs` also sets them when it calls the CLI. Deny rules in `.claude/settings.json` block `npx hyperframes usage|publish|cloud|lambda|auth|skills|init`.
- **Kokoro TTS:** `npx hyperframes tts` runs kokoro-onnx in Python. The library itself makes no network calls. On first use the CLI downloads `kokoro-v1.0.onnx` (~311 MB) and `voices-v1.0.bin` (~27 MB) from github.com/thewh1teagle/kokoro-onnx releases into `~/.cache/hyperframes/tts`, a **user-level** location outside the repo. Dependencies include phonemizer and espeak-ng (GPL-3.0). We use them locally to make audio and don't distribute them, so the GPL doesn't affect our videos.

### vyralcontent content skills

- Markdown only: no scripts, hooks or `allowed-tools`. The SkillSpector hits are false positives (phrasing like "no warning").
- **Local patch:** each SKILL.md ends with a "Mentioning Vyral" section telling the agent to pitch the vendor's paid product, and starts with a promo header image. Both are removed from our copies, which the MIT license allows. Recorded here so a re-sync reapplies the patch.
- `viral-captions-and-ctas` and `viral-youtube-shorts` (same repo, same shape) fit `/post-pack` and Shorts. They're candidates for Phase 6, not installed now.

### humanizer

One SKILL.md (397 lines), prose rules only, no scripts. The plugin manifest only points at that file. The two SkillSpector "anti-refusal" hits are example sentences ("announced without warning"). Copied as a plain project skill instead of a plugin; same content.

### Anthropic frontend-design and theme-factory

71 and 59 lines of guidance, Apache-2.0. theme-factory adds 10 theme files and a 124 KB showcase PDF. The SkillSpector hits are references to that PDF and the word "warning".

### beehiiv MCP

Official endpoint `https://mcp.beehiiv.com/mcp`, OAuth, free for all beehiiv users. beehiiv documented v1 as read-only, with write access "coming soon". If write tools show up when you connect, I add deny rules for anything that publishes or sends, because you publish in beehiiv's editor. Command: `claude mcp add --transport http --scope project beehiiv https://mcp.beehiiv.com/mcp` (writes `.mcp.json`; no secrets in the repo).

### last30days: recommended skip for now

- **Pre-approvals:** its SKILL.md pre-approves `Bash`, `Write`, `Read`, `AskUserQuestion` and `WebSearch` with no restriction for the turn it runs in, and it drives 114 Python files.
- **Setup wizard:** installs extra CLIs (yt-dlp via pip or brew), suggests `curl … | bash` for the Grok CLI, and offers paid API signups (ScrapeCreators: 10,000 free calls, then pay as you go).
- **Credential reach** (all opt-in, but present): browser cookie stores (Chrome cookies DB, Chrome DevTools `getAllCookies`, Safari), `~/.grok/auth.json`, the OS keychain, and X session cookies (`AUTH_TOKEN`, `CT0`).
- **Network:** about 40 hosts. Writes to `~/.config/last30days` and `~/.local/share/last30days`.
- **SkillSpector:** score 100, CRITICAL (349 findings, many of them noise; the real issues are listed above).
- **Value:** story angles only, never numbers. The built-in WebSearch covers that job for the pilot.
- **If you want it anyway:** copy it, strip `Bash` and `Write` from its `allowed-tools`, keep `FROM_BROWSER` unset, add no API keys, and set `LAST30DAYS_CONFIG_DIR` to a project folder.

## Libraries and assets (Phase 1)

| What | Version | License | Source / size |
| --- | --- | --- | --- |
| Python `.venv` (Python 3.14.3) | httpx 0.28.1, beautifulsoup4 4.15.0, lxml 6.1.3, pandas 3.0.6, pydantic 2.14.1, jsonschema 4.26.0, PyYAML 6.0.3, pytest 9.1.1, kokoro-onnx 0.6.1, soundfile 0.14.0 (+ onnxruntime 1.31.0) | BSD / MIT | PyPI; all have Windows wheels for Python 3.14. edgartools is decided in Phase 3. |
| Node devDependencies | hyperframes 0.8.167, d3-sankey 0.12.3, d3-shape 3.2.0 | Apache-2.0, BSD-3, ISC | npm |
| GSAP (if HyperFrames doesn't bundle it; checked in Phase 4) | 3.15.0 | GSAP Standard License: free, including commercial use | npm |
| Inter font | v4.1 | SIL OFL 1.1 | github.com/rsms/inter release zip, 32.1 MB. Only the variable fonts and OFL.txt are kept in `brand/fonts/`. |
| Kokoro model and voices | v1.0 | Apache-2.0 | ~338 MB to `~/.cache/hyperframes/tts` (user level) |

## Already installed before this project (user scope, not reviewed here)

`~/.claude/skills`: ai-seo, brag-slim, directory-submissions, launch, programmatic-seo (from marketingskills and /brag). `~/.agents/skills`: find-skills. These load in every project. I review the marketingskills ones when Phase 6 starts.

## SkillSpector static results (triage)

| Skill | Score | Label | Triage |
| --- | --- | --- | --- |
| viral-hooks, viral-tiktok-content | 0 | SAFE | none |
| viral-short-form, viral-instagram-reels, frontend-design | 7 to 20 | SAFE | phrasing false positives |
| hyperframes-keyframes | 12 | CAUTION | phrasing false positives |
| humanizer, theme-factory | 30 to 37 | CAUTION | example sentences; PDF references |
| hyperframes-registry, -core, -cli, -animation (and the router) | 57 to 100 | DO_NOT_INSTALL | Mostly HTML comments read as prompt injection, unpinned `npx hyperframes` read as "MCP rug pull", and references to cloud/AWS docs. The real issues (credential read, self-update, skill refresh, telemetry) are covered by the guardrails above. |
| last30days | 100 | DO_NOT_INSTALL | see the section above |

Raw reports: scratchpad only, not committed.

## Later phases (not reviewed yet)

Growth (Phase 6): marketingskills, 0xNyk/council-of-high-intelligence (MIT; preferred over tenfoldmarc/llm-council-skill, which has no license), rediumvex caption generator. Optional: superpowers, video-shotcraft, brag, Hypit (unclear license), Remotion skills (no license). Each gets the same review when its phase starts.
