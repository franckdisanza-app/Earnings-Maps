# Posting checklist

The owner posts; Claude never does. Run this for every video, on every platform.

## Before posting

- [ ] Gate A: `data/normalized/<ID>.approval.json` exists and matches the data file
- [ ] Gate B: owner watched and approved `out/<ID>/money-map.mp4`
- [ ] `compliance-reviewer` passed on `script.md` and `captions.md`
- [ ] On-screen lines present: company + ticker, period with calendar months, source + filing date, GAAP/non-GAAP labels, "our calculation" where used, "Not investment advice"
- [ ] `sources.md` complete: filing URL, music track + license, voice = Kokoro TTS (AI-labeled)
- [ ] Within 24 hours of the release

## On each platform

- [ ] **AI label switched on** (the voice is TTS): TikTok AI-generated content label, Instagram AI label, YouTube altered/synthetic disclosure
- [ ] Upload the cover (9:16; 4:5 for the Instagram grid)
- [ ] Caption from `captions.md` for that platform, 3–5 hashtags
- [ ] Alt text (Instagram)
- [ ] Pinned comment posted
- [ ] Instagram: ManyChat keyword "MAP" live with the current DM text
- [ ] TikTok: bio link points at the signup page

## After posting

- [ ] Add a row to `analytics/posts.csv` (post URL, platform, hook variant)
- [ ] 24 h and 7 d later: fill in views, watch time, completion, shares/sends, saves, follows, link clicks, signups
- [ ] Any error found → correction within 24 h: pinned comment, newsletter note, `CORRECTIONS.md`
