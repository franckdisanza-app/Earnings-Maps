# Earnings Maps

Animated money maps of big US companies' quarterly results, built from primary SEC filings: short vertical videos for TikTok, Reels and Shorts, plus a weekly newsletter.

- Brief: [docs/KICKOFF.md](docs/KICKOFF.md) · Working rules: [CLAUDE.md](CLAUDE.md) · Progress: [STATUS.md](STATUS.md)
- Reviewed third-party tools: [SKILLS.md](SKILLS.md) · Decisions log: [DECISIONS.md](DECISIONS.md)

## Setup (Windows)

Needs git, Node 22+, Python 3.14 (pipeline) and 3.10–3.13 (Kokoro TTS), FFmpeg.

```bash
cp .env.example .env            # then set SEC_USER_AGENT and HYPERFRAMES_PYTHON
python -m venv .venv && .venv/Scripts/python.exe -m pip install -r requirements.txt
py -3.10 -m venv .venv-tts && .venv-tts/Scripts/python.exe -m pip install -r requirements-tts.txt
npm install
npx hyperframes browser ensure  # pinned headless Chrome for rendering
npx hyperframes doctor
```

## Per video

`/earnings-ingest <TICKER>` → Gate A (approve numbers) → `/money-map <ID>` → Gate B (approve MP4) → `/post-pack <ID>` → the owner posts, following [docs/posting-checklist.md](docs/posting-checklist.md).

Not investment advice. All figures come from company filings; see each video's `sources.md`.
