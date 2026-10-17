# Platform specs

Source: brief §7, plus each platform's current rules to re-check before launch. Safe zones are a rule of thumb; confirm them with a private test upload on each platform before the first public post.

## Output

| Asset | Size | Notes |
| --- | --- | --- |
| Video | 1080×1920, 30 fps, H.264 + AAC | 25–35 s. Final frame holds ~2 s as a clean screenshot. |
| Cover (Reels, TikTok, Shorts) | 1080×1920 PNG | Same safe zones as the video. |
| Cover (Instagram grid / 4:5) | 1080×1350 PNG | The grid crops 9:16 covers, so this is designed separately. |
| Carousel | 1080×1350 PNG, 6–8 slides | Cover, money map, three insights, sources + call to action. |

## Safe zones (9:16, 1080×1920)

Critical text stays inside a box with these margins (also in `brand/tokens.json`):

| Edge | Margin | Why |
| --- | --- | --- |
| Top | 154 px (~8%) | status bar, "Following/For You" tabs |
| Bottom | 384 px (~20%) | caption, username, music line, progress bar |
| Right | 130 px (~12%) | like / comment / share / remix rail |
| Left | 64 px | breathing room |

Background, flows and decoration may run full-bleed; text and key numbers may not.

## Readability

- Labels ≥ 44 px, key numbers ≥ 72 px at 1080 wide.
- At most ~7 words on screen at once.
- Every number on screen for ≥ 1.5 s.
- Text contrast ≥ 4.5:1 (≥ 3:1 for large numbers).
- Works with sound off: everything the voice says is also on screen.

## Required on-screen lines (brief §2.1 rule 6)

Company name + ticker · period with calendar months · "Source: [Company] earnings release, filed [date]" · GAAP / non-GAAP labels where they apply · "Our calculation" on any subtotal the company doesn't print · "Not investment advice".

## Per platform (check current settings before each launch)

| | TikTok | Instagram Reels | YouTube Shorts |
| --- | --- | --- | --- |
| AI label (Kokoro voice) | Switch on the AI-generated content label | Switch on the AI label | Switch on the altered/synthetic content disclosure |
| Call to action | Bio link + pinned comment (no DM automation: Swiss/EEA/UK accounts can't use TikTok's DM API) | Comment "MAP" → ManyChat DM with signup link | Pinned comment + description link |
| Hashtags | 3–5 specific | 3–5 specific | 3–5 specific |
| Notes | Viewers can turn AI content down in their feed | Ranks on watch time, sends per reach, likes per reach; original content only | |
