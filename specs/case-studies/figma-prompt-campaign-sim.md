Build three desktop screens in Figma for **Campaign Sim**, a team-based training
simulation used by sports representation agencies. Teams get a budget, a roster
of talent scouts to reach, and a set of outreach channels, then compete across
rounds to build the most effective campaign for their players. Standing,
capacity used, and remaining budget are the three numbers the game turns on, so
they stay pinned to the top of every screen.

Create each screen as its own frame at **1440 × 1024**, set up to export at 2x
(2880 × 2048 PNG). Name the frames `campaign-sim-01`, `-02`, `-03`.

## Visual system

Light enterprise SaaS, slightly denser and more utilitarian than a marketing UI.
Build the shell and the left panel as components — they repeat across all three
screens unchanged.

- Page background `#EEF0F4`; cards `#FFFFFF`, 1px border `#E4E7EC`, 8px radius.
  The header block behind each page title is white and sits flush against the
  top bar.
- Text `#101828` primary, `#667085` secondary.
- Primary action blue `#1D4ED8` for filled buttons, the team name, and the
  metric values in the top bar.
- Accent indigo `#4F46E5` for the one floating channel icon on frame 2. Do not
  use magenta or pink anywhere.
- Type: Inter or a similar neutral grotesque. Page title 28/600, card title
  20/600, row title 16/600, body 14/400, label 13/400.
- Currency is written with a `¢` prefix throughout — it is a fictional game
  currency, not cents. Keep it exactly as written.

**Top bar**, full width, white, 1px bottom border:

- Left: `Team Northline` in blue at 15/600, `2nd place` beneath it at 13px gray.
- Centre: a bordered pill reading `Round 2`.
- Right, two stacked pairs side by side: `80%` in blue over the gray label
  `Capacity used`; `¢ 235,340` in blue over the gray label `Remaining budget`.

**Icon rail**, ~110px, white, running the full height below the top bar, 1px
right border. Icon-only, no labels, stacked with generous spacing: home, gauge,
grid, edit/notebook, lightbulb, target, help. Pinned to the bottom: a
panel-collapse icon, a hairline divider, and a circular avatar containing `S`.

**Page header block** — white, sitting directly under the top bar and to the
right of the rail: page title, then a one-line subtitle in gray beneath it. The
gray content area starts below this block.

## Naming rule

Every person, club, agency, and competition named in these screens is invented
and must stay invented. Do not substitute a real athlete, scout, club, or
tournament for any name below, and do not add real ones as filler.

---

## Shared left panel — frames 1 and 2

A ~440px white card pinned to the left of the content area, running to the bottom
edge of the frame and clipping there.

Top block, on a faint gray tint: `Sofia Clarino` at 22/600, `Talent Scout`
beneath it at 13px gray.

Then, at 15px, the channel description text:

> Paid offline channel, sponsorship of scouts. Maximum of 25 delegates per
> showcase.

Then three labelled sections, each a 15/600 heading followed by label/value rows
— label left in gray, value right in bold — separated by hairline dividers:

**Segment Details**
- Prospect potential · `T1`
- Group Size · `40`
- Accessible per year · `2 per club`

**Scout Preferences**
- Digital affinity · `Mix`
- Interaction preference · `Neutral`
- Content attributes · `Neutral`

**Plan Totals**
- Access Restrictions · `Yes`
- Capacity · `80%`
- Investment Planned · `¢ 245,654`
- Expected Exposure · `32,778`

Below Plan Totals, a small `By type` label with a three-segment horizontal bar
beneath it, then a `By content` label with its bar beginning and clipping at the
frame's bottom edge.

---

## Frame 1 — `campaign-sim-01`, Select Channels

Header: `Planning Tool – Select Channels` / "Select the channels you'll use to
reach Julie Abraham."

To the right of the left panel, a **three-column grid of channel cards**. Each
card: a line icon and a 20/600 title on one row, a 15px gray description
beneath, and a footer row holding a bordered duplicate-icon button at the left
and a `⊕ Add Content` text button at the right. Cards are equal height per row.

Give each card a distinct icon and icon colour so the grid reads as a set of
different things.

Row 1:
- **International Showcase** — "Paid offline channel, sponsorship of scouts.
  Maximum of 25 delegates per showcase."
- **Regional Combine** — "owned event such as face-to-face for a group of scouts"
- **Player Liaison Officer** — "club-facing role performing face-to-face
  interactions with scouts"

Row 2:
- **Scout Visit** — "face-to-face conversation with (or without) a printed profile
  sheet or tablet dossier that contains player information"
- **Agent Email** — "eMail with pre-approved content sent by agents. Also called
  agent triggered eMail (ATE)"
- **Advertisement** — "advertisement in offline media"

Row 3, beginning near the bottom and clipping at the frame edge so the grid reads
as scrollable:
- **Smartphone app** — "application for professional purposes delivered by a
  representation agency (club service)"
- **Remote Film Session** — "conducting an interactive, online, real-time meeting
  with a scout. Also referred to as 'remote review' or 'web calls'"
- **Remote Liaison** — "online player liaison officer"

On the **Advertisement** card only, draw `⊕ Add Content` as a bordered button
rather than plain text — it is the one channel already selected, and frame 2 is
what opens from it.

Bottom bar, spanning the content area: a bordered `Copy segment from…` button
with a duplicate icon at the left, and a filled blue
`Continue to next segment →` button at the right.

---

## Frame 2 — `campaign-sim-02`, Select Content

Same shell and same left panel. Header: `Planning Tool – Select Content` /
"Select the advertisement content you'll use to reach Julie Abraham."

Filling the area right of the left panel, one large white card: title
`Advertisement` at 24/600 with the subtitle "Choose a mix of content types and
set the frequency of engagement to maximize effectiveness." beneath it, and a
circular indigo icon button floating at its top-right corner.

Inside, a bordered table. A header row reading `Content` on a faint gray tint,
then six rows separated by hairlines. Each row: a 40px rounded-square icon in
its own colour at the left, then a 17/600 title with a 15px gray description
beneath. A final `Total` row, bold, on the same faint tint as the header.

- **Player news** — "Promotional information about your player" — dark green icon
- **League Awareness** — "General league information, without linking to a
  player" — periwinkle icon
- **Contract Terms** — "Specific contract information on your player or bracket"
  — deep magenta-brown icon
- **Performance Data** — "Information about results of matches played by your
  player" — orange icon
- **Development Guidelines** — "Information about guidelines issued by governing
  bodies" — violet icon
- **Event Information** — "Information about logistics, agenda, services" —
  cyan icon

These six colours are a set: reuse them exactly as the `By Content` legend
swatches on frame 3.

Card footer, right-aligned: a bordered `Cancel` button and a filled blue `Apply`
button.

---

## Frame 3 — `campaign-sim-03`, Review Campaign

Same shell, no left panel — this screen is full width. Header:
`Review Campaign` / "Review your campaign plan, compare it with previous rounds,
and verify your selected resources before submitting."

**Main table card**, taking roughly two thirds of the width. Columns: a leading
expand chevron, `Name ↓`, an `✎ Edit` text button, `Channels`, `Planned
Investment`, `Expected Exposure`. The last three are right-aligned.

Each row: the scout name at 17/600 with `Talent Scout` beneath it in 13px gray;
the channel count; then the two figure cells, each carrying a small delta line
beneath the number — green `↗ 2.5% vs Round 1` under Planned Investment, red
`↘ 2.5% vs Round 1` under Expected Exposure.

Six rows, all sharing the same figures — `18`, `¢ 54,345`, `234,342`:

Sofia Clarino · Eric Robertson · Martin Johnson · Frank Smith · Julie Abraham ·
Victor Gregorio

Then a bold `Total` row: `18` · `¢ 56,654` · `28,684`.

**Right rail**, three stacked cards:

1. A small table with the column heads `Resources` and `Planned Investment` —
   let the second head clip at the card's right edge. Three rows each reading
   `Resource 1` · `¢ 34,6…`, then a bold `Total` row · `¢ 34,6…`.
2. `By Type` — a three-segment horizontal bar, then three legend rows, each a
   coloured dot, a label, and a right-aligned percentage:
   `Owned Scouting 33%`, `Owned Promotional 33%`, `Paid 33%`.
3. `By Content` — a six-segment bar using the six frame-2 content colours in the
   same order, then six legend rows at `17%` each: `Player news`,
   `League Awareness`, `Contract Terms`, `Performance Data`,
   `Development Guidelines`, `Event Information`. Let the last row clip at the
   frame's bottom edge.

Bottom bar, full width: a bordered `✎ Edit Plan` button at the left, a filled
blue `Submit Plan` button with a check icon at the right.
