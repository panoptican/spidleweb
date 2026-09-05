# Domain shift — Expert Insights & Campaign Sim

Both cases come from one Blueshift engagement (2025) whose client is
NDA-sensitive. The published versions move the work out of pharma medical
affairs and into sports representation. The design problem, the IA, and Jason's
role are described accurately; only the domain and the sample data are
substituted, and each case discloses that in its facts table
(`Note — Domain changed under NDA`).

Copy on both pages is rewritten. The screens are edited in Figma from the
client's existing frames — text substitutions, not a rebuild — using the
prompts below. `qa/precision-screens/` held the source captures of the
eleven screens; since 2026-09-04 it holds the edited exports, which are
copied into `assets/` under the site's names.

## Prompts

- `figma-prompt-expert-insights.md` — seven screens (`navigator-01` to `-07`):
  Dashboard, Search, Social Explorer, and four Dashboard states showing the AI
  ask panel and three answers.
- `figma-prompt-campaign-sim.md` — four screens (`campaign-sim-01` to `-04`):
  Select Channels, Select Content, Channel Insights, Review Campaign.

Each prompt is self-contained and pasteable with the matching frame selected.
The prompt files are the source of truth for every string; this file records
only the decisions behind them.

## Decisions

- **Sport is football (soccer).** The case copy says "transfer fee", so every
  invented detail follows: release clauses, academies, loan spells, first-team
  minutes, trial days. Nothing American-football ("combine") survives.
- **Product names in-screen are the case titles.** The Expert Insights wordmark
  replaces `Navigator365™ Matrix`; the Campaign Sim onboarding video replaces
  `Welcome to Omnitopia!`. Both client logo marks are replaced with neutral
  geometric glyphs — a blur would read as a redacted real client.
- **Text only.** Colors, icons, figures, bars, and layout stay. The client's
  magenta accent therefore stays too; recoloring it is a separate call.
  (Jason made that call in the export pass on 2026-09-04: the accent is
  recolored on every frame, and the campaign currency became euros.)
- **`Team Skywalker` → `Team Northline`.** No reason to carry a trademark
  through a redraw.
- **One inconsistency fixed in passing.** The original `navigator-07` insight
  text (67% vs 54%) disagreed with its own bars (58% vs 35%); the rewritten
  text follows the bars.
- **Channel Insights had lorem ipsum** in its subtitle; the prompt supplies
  real copy.

## Vocabulary

- key opinion leader / KOL / DOL / expert / HCP → scout
- brand / drug / product → player
- My Brands → My Players · Competitor Brands → Rival Players
- therapeutic area → league · conference / congress → showcase
- clinical trial → match record · patient potential → prospect potential
- medical affairs team / pharmaceutical company → representation agency
- rep → agent · detailing → film session · MCQ → exposure
- Owned Medical → Owned Scouting

## Naming rule

Invented names only, searched before publishing. The original
`expert-insights-02.png` put a fabricated social post under Maryam Lustberg, a
real practicing oncologist — that is the failure this rule exists to prevent.

Vetted 2026-09-03: Toma Vasquez, Elias Braun, Dembe Osei, Idris Falk, Mateus
Oyelaran, Dana Whitfield, Marcus Feld returned no notable athlete or scout.
Rejected in the same pass: Nico Ferreira (current Uruguayan pro footballer),
Rafael Lindqvist (living Uppsala professor), Meridian Athletic (real training
organization). Replacements — Ruben Achterberg, Rafael Eikeland, Kestrel Sports
Group — were vetted the same day: no notable athlete, scout, or agency.
"Ruben Achterberg" is a common Dutch name with no prominent bearer; "Toma
Vasquez" sits one letter from Tomas Vasquez, a Chilean MMA fighter, and is kept
on the grounds that the sport and spelling both differ.

Names carried over from the original demo data (Sophie Greenfield, Liam
Hargrove, Emma Sinclair, Ethan Kim, Oliver Chen, Mia Turner, Emma Zhang, Sarah
Chen, Michael Ross, Lisa Park; Sofia Clarino, Eric Robertson, Martin Johnson,
Frank Smith, Julie Abraham, Victor Gregorio) are generic and unchanged.

## Follow-ups on the site once screens are exported

Done 2026-09-04, once the exports landed:

- `work/campaign-sim.html`: Review Campaign figure repointed to
  `campaign-sim-04.png`; Channel Insights (`-03`) added to the opening section
  with a sentence on the reference table and the onboarding video; the second
  figure's alt text now reads "from player news to event information".
- `work/expert-insights.html`: new closing section, "The answer takes the
  shape of the question", with `-04` full frame and `-05` to `-07` cropped to
  the answer panel (crop geometry in `specs/portfolio.md`).
- Both OG images regenerated. The five new assets were added to the preview
  gate for the review period.
- Review Campaign's Resources card had been filled with youth-movement
  Scouting costs (trail permits, campsite fees) where the source had
  placeholders; fixed in Figma to Match Travel, Showcase Fees, and Video
  Analysis. The Campaign Sim set, first exported at 1x, was re-exported at
  2x in the same pass.

Closed 2026-09-04: Doug at the client approved both case studies without
changes for display without password protection. The middleware and the two
sitemap omissions are gone; `docs/deployment.md` notes that the two Pages
secrets are now unused and can be deleted.
