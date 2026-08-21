# spidleweb.net — portfolio (built 2026-07-17)

Living spec for the current site. Supersedes `specs/archive/portfolio.md`.

## Concept

Personal portfolio in the visual language of the `qa/experiments/formation`
design experiments: archive/brutalist editorial. Paper `#F2F2EF`, ink
`#0A0A0A`, one red accent `#FA1900`, hairline rules, mono uppercase
micro-labels, registration marks, large expanded display type, hover
inversions, grayscale imagery that colorizes on hover.

## Structure

- `index.html` — split layout. Sticky full-height dark panel on the left
  (name in GT America Expanded, coords/meta, positioning line). Scrolling
  archive on the right: case study index rows (01–04, full-row invert on
  hover), Sites grid (four live-site screenshots, external links), Profile
  (bio + roles roster), Contact.
- `work/conservis.html`, `work/vidscrip.html`, `work/navigator.html`,
  `work/omnitopia.html` — case studies in the same split layout. Left panel
  carries number, title, and a facts table (client/studio/role/scope/year);
  right column carries rewritten copy, figures with mono captions, a stats
  block, and a next-project handoff row.
- `style.css` — single shared stylesheet, all pages.
- `script.js` — reveal-on-scroll only (IntersectionObserver), fully
  progressive: reduced motion or no JS shows everything immediately.
- `assets/favicon.svg` — three-color abstract mark derived from the site's
  paper, ink, and red registration-mark visual language.

## Content sources

- Conservis copy: rewritten from `specs/case-studies/Conservis Snack-Sized
  Case Study.docx.pdf` (Foundry "snack-size" copy, first person, voice pass).
- Vidscrip copy: rewritten from `specs/case-studies/Vidscrip.pdf` (that PDF
  is the original product requirements doc, not case-study copy).
- Navigator365 / Omnitopia copy: written from the supplied screens in
  `assets/` — no write-ups existed. See assumptions.
- Ever.Ag copy (added 2026-08-19): written from `qa/everag-background/`
  (SOWs, the Foundry design collaboration guide, the design-system gaps doc,
  the 2023-05-05 retro transcript, and the Ever.Ag/supply-chain decks).
  Confidential material excluded: budgets/rates/FTE counts, competitor and
  PE-ownership details, named enterprise customers, internal retro
  criticism, individual names, and internal product codenames (Phoenix,
  Vault, CMS, MDD) — apps are described by domain instead. Links to the
  public style guide at design.ever.ag (verified live 2026-08-19).
- Ever.Ag imagery: `assets/everag-01..05.png` from `qa/260819-screens/`;
  02/03/05 are crops of two deck slides (Use of Color, Product Examples)
  trimmed to product imagery. A Mobile Manifest phone crop was tried and
  cut on review (Jason: looked wrong in the layout); the field app stays
  in the copy only. OG captured from the live page at 1200×630 with
  Playwright's headless Chromium shell.
- Bio: jasonspidle.com + `application/resume-draft.md`.
- PLINTH copy (added 2026-08-20): written from the live journal at
  plinth.us, not from any existing write-up. Facts verified against the
  running site: the manifesto and "attains each equinox" cadence from
  `issue02/about` and `issue06/about`; the contributor roster from
  `issue07/archive.html` (nine pieces an issue, sixty-three across seven
  issues); the per-issue type stacks read out of each issue's own CSS
  (`issue01/css/grid.css`, `issue02/css/grid.css`, `issue03/css/grid.css`,
  `issue04..07/css/styles.css`); issue 03's image-map contents page and
  issue 06's single-page structure from their markup. Collaborator credits
  (Garett Strickland editing, Tyann Prentice graphics) supplied by Jason.
  Copy passed through the `jason-voice` skill on 2026-08-20: em dashes and
  semicolons removed, "not X, it's Y" reversals unwound, and the writerly
  lines cut ("the differences are the argument", "a masthead built out of
  nothing but hairlines", "simple and unreasonable"). Agency moved to first
  person where Jason did the work ("I built the page to hold words where the
  poem put them"). Every specific was kept: that lint fails generic summary
  without backing detail, so the names, faces, and counts all stay.
- PLINTH imagery: `assets/plinth-01..07.jpg`, captured 2026-08-20 from the
  seven live issue indexes at 1440x1000 @2x with Playwright's headless
  Chromium shell, downsampled to 1440px wide and saved as JPEG q88 (~1.1 MB
  for all seven; PNG would have been ~3.3 MB, and these are photographic
  screen captures). Issue 03 is top-cropped by 50 CSS px to remove its
  unstyled "Skip to content" link, which is visible on that page because it
  has no external stylesheet. The home-page index thumbnail uses
  `plinth-06.jpg` because issue 06's black cover is the only one that reads
  at 80x50. OG captured from the local page at 1200x630 the same way.
- PLINTH reading pages (added 2026-08-20, Jason's picks):
  `assets/plinth-evenson.jpg`, `-attar.jpg`, `-kreiden.jpg`, `-conn.jpg`,
  captured the same way from `issue07/evenson`, `issue05/attar`,
  `issue04/kreiden`, and `issue03/conn`. They were chosen to each show a
  different thing the reading layout had to do: a justified prose measure,
  a poem scored across the full page width rather than reflowed into a
  column, a narrow ragged column on issue 04's mint grid, and issue 03's
  custom scrollbar. That last one is verifiable in the source rather than
  inferred from the render: `conn.html` calls `.scroll-pane').jScrollPane()`
  and `issue03/css/jquery.jscrollpane.css` sets `.jspTrack` to `#000000`
  with a white `.jspDrag`, so the black vertical rule beside the text
  really is the scrollbar with its usual colours inverted.
  The Conn capture is cropped to `2304x1600+192+0` of the raw 2880x2000
  before downscaling — Jason marked it up as too loose, and its content
  filled only 51% of the frame against 75% for Evenson and 100% for
  Kreiden. The crop is centred on the measured content bounds with even
  ~100px margins, and holds the 36:25 ratio the other frames use: an
  arbitrary aspect would leave that cell short of its neighbour and pull
  the row's caption baselines apart.
- Blueshift copy (added 2026-08-21): written from the live site and from
  `~/Projects/blueshift`, not from any existing write-up. Facts verified
  against the running pages at `/`, `/surge`, `/spark`, `/pulse`: headlines,
  subheads, stage names, deliverable names, package names, prices, and
  delivery windows are quoted or paraphrased from the SSR HTML as of
  2026-08-21. Founding year 2024 and the four founding partners (Nils
  Hansen, Heather Sowden, Kurt Schmidt, Jason) come from the site-wide
  schema in `archive/qa/seo/site-wide-schema.html` and `archive/qa/seo/
  llms.txt`. Project and retainer ranges ($30–80k, $8–15k monthly) are the
  homepage FAQ's own numbers. The Surge pricing story is verified against
  the two PDFs in `~/Projects/blueshift/specs/`: `Surge one-pager.pdf`
  ($2,500 / $5,000 / $10,000, hedged subhead) and `Blueshift_Surge.pdf`
  ($4,950 / $9,500 / $19,500, live subhead), which are otherwise identical
  stage for stage and deliverable for deliverable — `pdftotext -layout` on
  both confirms the only differences are the subhead and the three prices.
  The five-approach argument for the instrument panel is
  `archive/specs/design-approaches.md`, which names the direction and gives
  the reason quoted in the case ("showing what the AI does rather than
  describing it"). Client logos, the Precision AQ engagement document, and
  the internal SEO audit were deliberately left out; see assumptions.
  Copy passed through the `jason-voice` skill on 2026-08-21:
  pronoun-plus-copula openings rewritten to name their subject ("It is the
  cheapest door into the studio" to "Pulse is the cheapest way into the
  studio"), formal negations contracted, and two flourishes cut ("neither of
  which anyone will spend on a first date"; "The color rule does the arguing",
  which the sentence after it already said). An unsourced recommendation went
  too ("the one most people should walk through first"). Every price, name,
  and count was kept: the lint fails generic summary without backing detail.
- Blueshift imagery: `assets/blueshift-*.jpg`, captured 2026-08-21 from the
  live site at 1440×1000 @2x with Playwright driving the installed Chrome,
  downsampled to 1440px wide and saved as JPEG q88 (~2.0 MB for ten frames).
  Every capture scrolls the page to the bottom and back first, because the
  site reveals sections on scroll and a cold viewport screenshot catches
  them mid-transition. Full-page captures were tried and abandoned: the
  Surge teaser is scroll-pinned and repeats itself in a `fullPage` shot.
  Frames are viewport captures at fixed scroll offsets instead. The home
  index thumbnail uses `blueshift-01.jpg`, the homepage hero, because the
  magenta wordmark on the blue starfield is the only frame that reads at
  80×50. OG captured from the local page at 1200×630 the same way.
- Case imagery: `assets/*.png` (supplied). The Vidscrip case uses four revised
  captures in scrollable frames, including the procedure survey and date editor.
  Site imagery:
  `assets/sites/*.png`, captured 2026-07-17 from the four live sites at
  1440×1024 @2x with Playwright's headless Chromium shell. Ascensus is
  top-cropped to 1240px to remove a cookie banner.

## Assumptions (flagged for Jason)

1. **Navigator365 and Omnitopia clients are listed as "Life sciences (NDA)"**
   and attributed to Blueshift, 2025 (screens are dated Nov–Dec 2025; resume
   flags client names as needing NDA confirmation). Swap in real names if
   safe to list.
2. **Years**: Conservis 2019 (map data © 2019 in screens), Vidscrip 2021
   (procedure dates in screens), Navigator/Omnitopia 2025. Correct if wrong.
3. **Kardion** had no role/context info supplied; captioned "Site design"
   only.
4. **Roles**: "Product design lead" (Foundry-era cases) and "Design lead"
   (Blueshift-era cases) inferred from the resume draft.
5. The `agents/` demos and `variant-rating/` were left untouched and are not
   linked from the new site (out of the supplied scope for this build).
6. **Ever.Ag years listed as 2022–24**: the engagement started March 2022
   (collaboration guide); the sustainability-platform SOW ran from late
   October 2023 with a four-month initial term, which implies work into
   early 2024. Correct if the actual end date differs.
8. **PLINTH years listed as 2014–19, against Jason's recollection of
   2011–14.** Jason's initial brief said the journal ran 2011–2014; the site
   itself disagrees, and he chose to follow the site. Evidence: issue 04's
   masthead reads "Fall Equinox / MMXV" (2015) in `issue04/index.html`;
   Internet Archive first captures are issue 03 on 2015-03-25 (days after
   the March 2015 equinox), issue 04 on 2015-09-30, issue 05 mid-2016,
   issue 06 in 2018, issue 07 in 2019; and plinth.us was still a splash page
   linking only to unwin-dunraven.com as late as 2014-01-06, showing issue
   02's artwork by autumn 2014. Wayback first-capture is an upper bound on
   publication, so issue 01 and 07's exact dates remain approximate — hence
   the rounded "2014–19". 2011 is plausibly when the Ecclesia and the
   project began, which is not the same as when issue 01 shipped.
9. **PLINTH theme hue is 305 (violet)**, the first case hue outside the
   260–50 spread already in use, at chroma 0.16. No brand colour exists to
   match: the journal itself is mostly black and white, and its two colour
   issues (04 mint, 05 rust) disagree with each other.

10. **Jason's Blueshift title reads "Founding partner · Design lead".**
    Every source says "Founding Partner" and only that: the site-wide schema
    and `llms.txt` both list four Founding Partners. "Design lead" is
    Jason's own wording on the home-page roster and is carried through for
    consistency. Drop half of it if only one is right.
11. **The instrument panels are attributed to Jason.** What is documented is
    that `~/Projects/blueshift/archive/specs/design-approaches.md` argues
    for the direction, and that the Spark and Pulse components plus their
    handoff READMEs live in his repo. Who wrote the shipped React is not
    recorded anywhere. The case says he argued for the direction and that
    two of them shipped, which is what the files support. Correct the
    attribution if someone else built them.
12. **The shipped panels differ from the archived prototypes.** The Pulse
    component in `archive/framer/pulse/` is a beige scanner sweeping a
    wireframe with WCAG labels; what is live is a blue halftone field with
    a magenta core and `PROCESSING_NODES [ 56 ]` telemetry. The copy
    describes what is live, checked by capture on 2026-08-21.
13. **Blueshift theme hue is 265 (ultramarine)** at chroma 0.21, five
    degrees off the 260 already used by Expert Insights. Both rows go blue
    on hover. The collision is real and was accepted: 265 is the brand's
    dominant colour and its name, Expert Insights is Blueshift work anyway,
    and the panel is a much deeper, much more saturated ultramarine
    (`oklch(22% 0.14 265)`) than the insights panel. The alternative was
    Blueshift's magenta `#F81A75`, which clips out of sRGB above chroma
    0.20 at the lightness the accent needs and lands at 3.5:1 on paper,
    under the 4.5:1 the mono captions want.
14. **Blueshift appears both as a case study and in Shipped sites.** Left
    that way on purpose: the index row is the engagement, the sites row is
    the live site. Remove the sites row if the duplication reads badly.
15. **Left out of the Blueshift case on purpose.** The thirteen client
    logos on the homepage marquee are labelled "Clients and partners" and
    several are plausibly partner-team credentials, so no client is named.
    `~/Projects/blueshift/archive/qa/Precision_AQ_Kickoff_Agenda_styled.docx`
    is a live client engagement document naming client staff, a recruiter,
    and commercial terms; it is good evidence Jason leads engagements and
    unpublishable in any recognisable form. The hand-built vanilla rebuild
    of the homepage in `~/Projects/blueshift` was also cut: it is real craft
    but it is not shipped, and describing it means describing the live
    site's faults.

7. **Ever.Ag index-row hover accents**: the home-page `nth-child` accent
   hues were remapped so each row matches its case theme again (they had
   drifted when rows were reordered), with a new hue 165 for Ever.Ag.

## Conventions

- Vanilla HTML/CSS/JS, no build step, 2-space indent.
- Fonts: local GT America TTFs (see `fonts/README.md`); mono labels use the
  system mono stack.
- Adding a case study: copy any `work/*.html`, update panel facts, sections,
  figures, and the next-project links on its neighbors, and add an index row
  on `index.html`.
