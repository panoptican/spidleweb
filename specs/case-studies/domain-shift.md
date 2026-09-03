# Domain shift — Expert Insights & Campaign Sim

Both cases come from one Blueshift engagement (2025) whose client is
NDA-sensitive. The published versions move the work out of pharma medical
affairs and into sports representation. The design problem, the IA, and Jason's
role are described accurately; only the domain and the sample data are
substituted, and each case discloses that in its facts table
(`Note — Domain changed under NDA`).

Copy on both pages is already rewritten. **The six screenshots are not**, so the
pages currently describe screens that do not exist. This file is the build spec
for redrawing them.

## Where to build

Not in the client's Figma. Jason holds a **View** seat on the Precision Medicine
Group org and a Full seat on Blueshift, so the source file is not editable by him
anyway — and duplicating it would be the wrong move regardless. A duplicate
carries hidden layers, component names, and variable names that still read
`HCP`, `KOL`, `therapeutic area`; those survive an export and leak through a
shared Figma link. **Build fresh frames in a Blueshift file**, typed from this
spec.

Export the six case screens at 2880×2048 to `assets/`, keeping the existing
filenames. Regenerate `assets/og/expert-insights.png` and
`assets/og/campaign-sim.png` at 1200×630.

## Vocabulary

- key opinion leader / KOL / DOL → scout
- HCP → scout
- brand / drug → player
- My Brands → My Players · Competitor Brands → Rival Players
- therapeutic area → league
- congress → showcase
- clinical trial → match record
- medical affairs team → representation agency
- patient potential → prospect potential
- rep → agent
- detailing → film session

## Naming rule

Invented names only, checked before publishing. The current
`expert-insights-02.png` puts a fabricated social post under **Maryam Lustberg**,
a real practicing oncologist — that is the failure this rule exists to prevent.
Search each invented player and scout name before export; if a real athlete or
scout comes back, change it.

Scout names already in the screens (Sophie Greenfield, Liam Hargrove, Emma
Sinclair, Ethan Kim, Oliver Chen, Mia Turner) are fictional and carry over
unchanged. Campaign Sim's names carry over with the `Dr.` prefix dropped.

Player names to introduce — my roster: **Toma Vasquez**, **Elias Braun**. Rival
roster: **Nico Ferreira**, **Dembe Osei**, **Rafael Lindqvist**.

## The client mark

The current captures blur the client logo top-left. A blur reads as a redacted
real client and half-undoes the substitution. Draw a neutral fictional wordmark
instead.

---

## expert-insights-01.png — Dashboard

Nav: Dashboard · **Scouts** · **Showcases** · Analysis · Social Explorer ·
Search · **Leagues**

Metrics: `10,045 total discussions ↑20%` keeps; `847 active experts ↓7%` →
`847 active scouts ↓7%`.

What's Moving cards:

- Competitive Shift — "Meridian Athletic's #NextWave campaign gained 23% share
  of voice, primarily through amplification of combine data."
- Sentiment Driver — "Negative sentiment spike (-12%) linked to release-clause
  discussions around Toma Vasquez"
- Emerging Theme — "Load-management discussions up 340% following league
  guidance update on under-21 minutes"

Disclaimer — keep verbatim except: "do not constitute regulatory, clinical, or
strategic advice" → "do not constitute scouting, contractual, or strategic
advice".

Table `Brand Sentiment` → `Roster Sentiment`. Column `Top Expert` → `Top Scout`.
Group headers `My Brands` → `My Players`, `Competitor Brands` → `Rival Players`.
All figures carry over unchanged:

- Toma Vasquez · 3,120 · 58 / 7 / 35 · Sophie Greenfield
- Elias Braun · 4,300 · 63 / 11 / 26 · Liam Hargrove
- Nico Ferreira · 1,845 · 72 / 12 / 16 · Emma Sinclair
- Dembe Osei · 2,560 · 67 / 10 / 23 · Ethan Kim
- Rafael Lindqvist · 2,900 · 70 / 8 / 22 · Sophie Greenfield

## expert-insights-02.png — Search

Query `#BreastCancerResearch` → `#AcademyWatch`.

Insights paragraph → "Recent discussions reveal a dual landscape of rapid
analytical progress and persistent access challenges in academy scouting.
Tracking data is accelerating individualized development plans. While there is a
growing focus on player welfare and long-term progression, the most critical
hurdle is persistent disparity in scout coverage, particularly in rural
catchments."

Sentiment bar 58 / 7 / 35 keeps. Channel tabs keep their counts; `Blogs` →
`Scout Reports` so the nine channels match the case copy.

Posts:

- **Dana Whitfield** @danawhitfield · 4h · Positive — "Breaking down the movement
  patterns that separate elite academy wingers. Our latest report identifies
  markers that could change how clubs recruit." · 76 / 7 / 129
- **Marcus Feld** @marcusfeld · 2h · Neutral — "Scouts are digging deeper into
  academy data, uncovering insights that could change recruitment protocols.
  Stay tuned for updates." · 43 / 5 / 210
- **Emma Zhang** @emmazhang · 1h · Negative — "Leading scouts in youth football
  are emphasizing the need for individualized development plans. Accessibility
  and tailored coaching are…"

## expert-insights-03.png — Social Explorer

Keywords: `Toma Vasquez` · `Elias Braun` · `Dembe Osei`.

Combined Analysis → "Comparative Analysis: Elias Braun leads in overall
conversation volume with 332 active scouts, suggesting broader network reach.
However, Toma Vasquez shows the strongest positive sentiment (50%), driven
largely by regional academy coaches. While Elias Braun has visibility,
qualitative analysis suggests Toma Vasquez is winning on scout perception."

`DOLs` must not survive — it is pharma vocabulary ("digital opinion leaders").

`Top Experts` → `Top Scouts` in all three columns; the four names and post counts
carry over unchanged.

---

## campaign-sim-01.png — Select Channels

Top bar: `Team Skywalker` → `Team Northline` (the current name is a Star Wars
reference and there is no reason to keep it through a redraw). `2nd place`,
`Round 2`, `80% Capacity used`, `¢ 235,340 Remaining budget` all keep.

Subtitle: "Select the channels you'll use to reach **Julie Abraham**."

Left panel: `Dr. Sofia Clarino` → `Sofia Clarino`; role `Key Opinion Leader` →
`Talent Scout`.

- Segment Details — `Patient potential` → `Prospect potential`, value `SP 1` →
  `T1`. `Group Size 40` keeps. `Accessible per year: 2 per company` → `2 per club`.
- `Customer Preferences` → `Scout Preferences`; the three rows keep.
- Plan Totals — `Expected MCQ` → `Expected Exposure`, value keeps. Other rows keep.

Channel cards:

- International congress → **International Showcase** — "Paid offline channel,
  sponsorship of scouts. Maximum of 25 delegates per showcase."
- Local Scientific Meeting → **Regional Combine** — "owned event such as
  face-to-face for a group of scouts"
- Medical Scientific Liaison → **Player Liaison Officer** — "club-facing role
  performing face-to-face interactions with scouts"
- Rep visit → **Scout Visit** — "face-to-face conversation with (or without) a
  printed profile sheet or tablet dossier that contains player information"
- eMail Rep → **Agent Email** — "eMail with pre-approved content sent by agents.
  Also called agent triggered eMail (ATE)"
- Advertisement — keeps, "advertisement in offline media"
- Smartphone app — keeps; description → "application for professional purposes
  delivered by a representation agency (club service)"
- Teledetailing → **Remote Film Session** — "conducting an interactive, online,
  real-time meeting with a scout. Also referred to as 'remote review' or 'web
  calls'"
- eMSL → **Remote Liaison** — "online player liaison officer"

## campaign-sim-02.png — Select Content

Same top bar and left panel as 01. Subtitle: "Select the advertisement content
you'll use to reach **Julie Abraham**."

Content rows (icons and colors keep):

- Product news → **Player news** — "Promotional information about your player"
- Disease Awareness → **League Awareness** — "General league information, without
  linking to a player"
- Reimbursement → **Contract Terms** — "Specific contract information on your
  player or bracket"
- Clinical Trials → **Performance Data** — "Information about results of matches
  played by your player"
- Treatment Guidelines → **Development Guidelines** — "Information about
  guidelines issued by governing bodies"
- Event Information — keeps

## campaign-sim-03.png — Review Campaign

Table names drop `Dr.` and take the role `Talent Scout`: Sofia Clarino, Eric
Robertson, Martin Johnson, Frank Smith, Julie Abraham, Victor Gregorio. Column
`Expected MCQ` → `Expected Exposure`. All figures and deltas carry over.

`By Type` legend: `Owned Medical` → `Owned Scouting`; `Owned Promotional` and
`Paid` keep.

`By Content` legend takes the six renamed content types from screen 02.
