Build three desktop screens in Figma for **Expert Insights**, a scout-intelligence
platform used by a sports representation agency. The agency tracks what talent
scouts are saying about its own players, rival agencies' players, and whole
leagues, across social platforms, showcases, and the press.

Create each screen as its own frame at **1440 × 1024**, set up to export at 2x
(2880 × 2048 PNG). Name the frames `expert-insights-01`, `-02`, `-03`.

## Visual system

Light enterprise SaaS. Build the shared pieces as components so the three
screens stay identical where they repeat.

- Page background `#F5F6F8`; cards `#FFFFFF`, 1px border `#E4E7EC`, 8px radius,
  very soft shadow.
- Text `#101828` primary, `#667085` secondary, `#475467` body.
- Primary action blue `#1D4ED8` for filled buttons and links.
- Accent indigo `#4F46E5` for big metric numbers, the active nav item, and the
  AI affordance. Do not use magenta or pink anywhere.
- Sentiment triad: positive green `#12805C` on tint `#E7F6F0`; neutral gray
  `#98A2B3` on tint `#F2F4F7`; negative red `#D92D20` on tint `#FEE4E2`. This
  triad must read identically on all three screens — same colors, same order,
  every time.
- Type: Inter or a similar neutral grotesque. Page title 28/600, card title
  18/600, body 14/400, table and label text 13/400, micro-labels 12/400.

**Left nav rail**, 260px, white, full height, 1px right border. Icon + label
rows, 15px: Dashboard · Scouts · Showcases · Analysis · Social Explorer ·
Search · Leagues. The active row gets a 3px indigo left bar, an indigo icon and
label, and a faint indigo row tint. Pinned to the bottom: a `Logout` row with an
exit icon. Top-left above the nav sits a small square wordmark — invent a
neutral one for the product, do not leave it blank or blurred.

**Auto-generated badge** — a small indigo pill with a sparkle icon and the label
`Auto-generated`, used wherever the product shows synthesized text.

**Disclaimer** — 12px `#667085`, used verbatim under every auto-generated block:

> This product leverages AI-powered capabilities to enhance your experience.
> Outputs are for informational purposes only and do not constitute scouting,
> contractual, or strategic advice. All outputs should be independently reviewed
> and validated before use.

**Date-range pill** — bordered white button with a calendar icon and the label
`Nov 3, 2025 - Dec 3, 2025`. Appears top-right on all three screens.

## Naming rule

Every person, club, agency, and competition named in these screens is invented
and must stay invented. Do not substitute a real athlete, scout, club, or
tournament for any name below, and do not add real ones as filler.

---

## Frame 1 — `expert-insights-01`, Dashboard

Page title `Dashboard` top-left, date-range pill top-right.

**Stat cards** — a narrow left column (~30% width) holding two stacked cards:

- `10,045` in indigo at ~48px, a green `↑ 20%` beside it, label `total
  discussions` beneath.
- `847` in indigo, a red `↓ 7%` beside it, label `active scouts` beneath.

**What's Moving** — a wide card filling the remaining ~70%, title plus the
Auto-generated badge. Three equal sub-cards in a row, each a bordered white box
with a 15/600 title and 13px body:

- **Competitive Shift** — "Meridian Athletic's #NextWave campaign gained 23%
  share of voice, primarily through amplification of combine data."
- **Sentiment Driver** — "Negative sentiment spike (-12%) linked to
  release-clause discussions around Toma Vasquez"
- **Emerging Theme** — "Load-management discussions up 340% following league
  guidance update on under-21 minutes"

The disclaimer runs full width beneath the three sub-cards.

**Roster Sentiment** — a full-width card below. Header: title left; right, a
segmented list/grid view toggle (list selected), a download icon, a settings
icon.

Table columns, left to right: player name, `Discussions`, `Positive`,
`Neutral`, `Negative`, `Top Scout`, and a trailing chevron. Under the column
headers, draw a 2px rule segmented in the sentiment triad — green beneath
Positive, gray beneath Neutral, red beneath Negative.

The three sentiment columns are tinted their full height: green tint, gray tint,
red tint. Numbers right-aligned in their columns. Each player name carries a
small leading dot — indigo for my players, gray for rivals. Each Top Scout cell
is an empty avatar circle plus a name.

Group header row `My Players`, 12px `#667085`:

- Toma Vasquez · 3,120 · 58% · 7% · 35% · Sophie Greenfield
- Elias Braun · 4,300 · 63% · 11% · 26% · Liam Hargrove

Group header row `Rival Players`:

- Nico Ferreira · 1,845 · 72% · 12% · 16% · Emma Sinclair
- Dembe Osei · 2,560 · 67% · 10% · 23% · Ethan Kim
- Rafael Lindqvist · 2,900 · 70% · 8% · 22% · Sophie Greenfield

A circular indigo AI button floats over the bottom-right corner of the screen.

---

## Frame 2 — `expert-insights-02`, Search

Page title `Search`. Beneath it a row: a wide bordered search input with a
magnifier icon, the value `#AcademyWatch`, and a filled blue `Search →` button
sitting inside its right edge; then a bordered `Filters` button with a filter
icon; then the date-range pill.

**Insights card** — title `Insights` plus the Auto-generated badge, then this
paragraph at 15px:

> Recent discussions reveal a dual landscape of rapid analytical progress and
> persistent access challenges in academy scouting. Tracking data is
> accelerating individualized development plans. While there is a growing focus
> on player welfare and long-term progression, the most critical hurdle is
> persistent disparity in scout coverage, particularly in rural catchments.

Below it a `Sentiment` heading and one full-width rounded bar split
58% green / 7% gray / 35% red, with `58% positive`, `7% neutral`, `35% negative`
sitting beneath the bar at its left, centre, and right. A hairline divider, then
the disclaimer.

**Feed card** — a tab row across the top, each tab a label with a count in
lighter gray. `X/Twitter 48` is active: darker label, blue underline. The rest:
`LinkedIn 12`, `Instagram 2`, `Facebook 4`, `YouTube 7`, `TikTok 1`, `Reddit 8`,
`Scout Reports 3`, `News 21`.

Beneath, stacked post cards. Each: an empty avatar circle, the author name at
15/600, `@handle · Nh ago` at 13px `#667085`, a sentiment chip at the far right,
the post body at 15px, and an engagement row of three icon+number pairs (heart,
comment, share).

- **Dana Whitfield** · @danawhitfield · 4h ago · chip `Positive` — "Breaking down
  the movement patterns that separate elite academy wingers. Our latest report
  identifies markers that could change how clubs recruit." · 76 · 7 · 129
- **Marcus Feld** · @marcusfeld · 2h ago · chip `Neutral` — "Scouts are digging
  deeper into academy data, uncovering insights that could change recruitment
  protocols. Stay tuned for updates." · 43 · 5 · 210
- **Emma Zhang** · @emmazhang · 1h ago · chip `Negative` — "Leading scouts in
  youth football are emphasizing the need for individualized development plans.
  Accessibility and tailored coaching are" — let this one run off the bottom edge
  of the frame mid-sentence, so the feed reads as scrollable.

The circular AI button floats bottom-right as on frame 1.

---

## Frame 3 — `expert-insights-03`, Social Explorer

Page title `Social Explorer` left. Right: a bordered `Saved Reports ⌄` button,
a `Filters` button, the date-range pill.

**Keyword row** — three equal bordered inputs, each with a 12px label above
(`Keyword 1`, `Keyword 2`, `Keyword 3`), a magnifier icon, a value, and a small
filled blue `Add` button inside its right edge. Values: `Toma Vasquez`,
`Elias Braun`, `Dembe Osei`.

**Combined Analysis** — full-width card, title plus the Auto-generated badge,
then:

> Comparative Analysis: Elias Braun leads in overall conversation volume with 332
> active scouts, suggesting broader network reach. However, Toma Vasquez shows
> the strongest positive sentiment (50%), driven largely by regional academy
> coaches. While Elias Braun has visibility, qualitative analysis suggests Toma
> Vasquez is winning on scout perception.

Then the disclaimer.

**Three comparison columns** — equal-width cards in a row, structurally
identical so differences read across a single line. Each contains, top to
bottom: the player name at 22/600; the label `Discussions` and the figure
`3,120` at 28/600; a `Sentiment` heading with a three-segment bar
(58 green / 7 gray / 35 red) and `58% positive`, `7% neutral`, `35% negative`
beneath it; a hairline divider; a `Top Scouts` heading with a blue
`View full list ›` link on the same line; then four bordered rows, each holding a
name, a green `Positive` chip, and a post count.

Column headings, left to right: `Toma Vasquez`, `Elias Braun`, `Dembe Osei`.

The four scout rows are the same in all three columns:

- Sophie Greenfield · Positive · 78 posts
- Liam Hargrove · Positive · 44 posts
- Oliver Chen · Positive · 31 posts
- Mia Turner · Positive · 29 posts

Let a fifth row begin and clip at the bottom frame edge so the lists read as
longer than the viewport. The circular AI button floats bottom-right.
