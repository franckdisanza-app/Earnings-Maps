---
name: post-pack
description: Write the full posting pack for an approved Earnings Maps video (three hook variants, the on-screen script, per-platform captions for TikTok, Reels and Shorts, a pinned comment, the Instagram "MAP" ManyChat DM, alt text, hashtags and sources.md), then run the compliance-reviewer. Use it whenever the owner wants captions, hooks, a pinned comment or any post copy for a ticker-period ID, even if they only ask for one piece.
argument-hint: "<TICKER-PERIOD, e.g. AAPL-FY2026Q4>"
arguments: [id]
---

# /post-pack $id

This writes the words that go around a finished video. Like the video, every number in them must trace to the approved data, and nothing may read as investment advice. The output is drafts for the owner; nothing here posts, schedules or sends.

## 0. Preconditions

- `data/normalized/$id.json` exists with a matching `data/normalized/$id.approval.json` (Gate A), checked with `scripts/approve.py --verify $id`. Without an approval there are no approved numbers to write about, so stop and say so.
- Prefer to run after Gate B, so the hook matches the video. If `out/$id/money-map.mp4` doesn't exist yet, write the pack anyway, but mark it "pre-render draft" at the top of `captions.md`.

Read `data/normalized/$id.json`, `out/$id/numbers-sheet.md` and `out/$id/script.md` (if present). Use only numbers from the data file, formatted per `brand/tokens.json` (`\$94.9B`, `+6%`, `−3%`). For each number in the copy, keep its JSON path in a comment, so the compliance reviewer can check it.

## 1. Hooks (first 1.5 s)

Write three variants that use different hook mechanics. The brief's patterns are a starting point:

- "[Company] made $[X]B in 3 months. Here's where every dollar went."
- "Every \$1 [Company] earned last quarter, split."
- "[Company]'s [segment] grew [X]% while [other] shrank."

Each one is ≤ 7 words on screen, works muted, and its promise is paid off in the video. For hook craft, read the `viral-hooks` skill (three-layer hook, anti-patterns). Avoid hype that implies a market move ("stock about to explode"); that's advice-adjacent and off-brand.

## 2. Script

If `out/$id/script.md` exists from `/money-map`, keep it as the source of truth and add only the chosen hook. If not, write it: the on-screen text by time window (hook, flow steps, one insight, end card) and the voice lines, each number with its data path.

## 3. Captions per platform → `out/$id/captions.md`

| Platform | Shape |
| --- | --- |
| TikTok | 1–2 short lines plus a question that invites comments. CTA: "link in bio" for the newsletter. 3–5 hashtags. |
| Instagram Reels | Hook line, 2–3 lines of context, then **"Comment MAP and I'll send you the full breakdown."** 3–5 hashtags. |
| YouTube Shorts | Title (≤ 60 chars, includes company + quarter) + 1–2 line description with the newsletter link placeholder `[NEWSLETTER_URL]`. |
| LinkedIn (optional) | 3–4 plain lines, no hashtag wall, one takeaway. |

For platform specifics, read `viral-tiktok-content` and `viral-instagram-reels`. Every caption carries the period ("fiscal Q4, Jul–Sep 2026") and ends with "Not investment advice. Source: [Company] earnings release." Hashtags: three to five **specific** ones (company, ticker, topic such as #earnings), never a wall.

Also in `captions.md`:
- **Pinned comment:** source link (the exhibit URL), the period, "Not investment advice", plus the newsletter pointer (TikTok: "link in bio").
- **ManyChat (Instagram only):** keyword `MAP`; DM text of 2–3 friendly lines with `[SIGNUP_URL]` and what they'll get (the full breakdown and the weekly issue). TikTok DM automation isn't available to Swiss/EEA/UK accounts, so TikTok uses the bio link and pinned comment.
- **Alt text** for the cover and each carousel slide: what the chart shows, with the key numbers, in plain words.
- **AI label reminder:** the voice is Kokoro TTS. Switch on each platform's AI label (TikTok AI-generated content, Instagram AI label, YouTube altered/synthetic disclosure).

## 4. Sources → `out/$id/sources.md`

- filing: company, form, filed date, accession, exhibit URL
- data file path and approval SHA-256
- derived values ("our calculation") with their formulas
- music: track, artist, license name and link, or "none"
- voice: Kokoro-82M (Apache 2.0), voice ID, AI label required
- fonts: Inter (OFL)

## 5. Tone pass

Run the `humanizer` skill over the captions, pinned comment and DM text. It must not change any number, ticker, period, link placeholder or required line. Diff the numbers before and after.

## 6. Compliance review

Delegate to the `compliance-reviewer` subagent (Agent tool, `subagent_type: compliance-reviewer`) with the ID and the paths: `out/$id/script.md`, `out/$id/captions.md`, `out/$id/sources.md`, `data/normalized/$id.json`, and the raw release folder `data/raw/<TICKER>/<period>/`. Save its report to `out/$id/compliance.md`.

Fix every blocker and every "fix", then run the reviewer again until it returns PASS. If a finding needs the owner's judgment (possibly regulated wording, anything ambiguous), leave it open and list it.

## 7. Hand-off

Tell the owner the pack is ready, which hook you recommend and why (in one line), any open compliance questions, and point to `docs/posting-checklist.md`. The owner posts. When they share post URLs, add rows to `analytics/posts.csv`.

## Output

```
out/$id/script.md      on-screen text + VO (with chosen hook)
out/$id/captions.md    hooks ×3, captions per platform, pinned comment, ManyChat DM, alt text, hashtags, AI-label reminder
out/$id/sources.md     filing, data hash, formulas, music license, voice, fonts
out/$id/compliance.md  reviewer report (PASS)
```
