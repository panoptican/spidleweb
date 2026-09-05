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
  right column carries rewritten copy, figures with mono captions, and a
  next-project handoff row. (The per-case Results blocks were removed on
  2026-09-03; see the copy-pass note under Content sources.)
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
- Ever.Ag imagery: `assets/everag-01..07.png`. 01 is the design-system
  dashboard template from `qa/260819-screens/`. 02–07 (re-exported
  2026-09-04) are six of the twelve 2x Figma exports in `qa/everag/`
  (ignored): hauler routes, payroll home, swine marketing at full height in
  a scroll frame, ground corn overview cropped to 2880×2176 at the gap above
  its open-orders card, and two phones, the markets watchlist (12px black
  bezel trimmed to 780×1688) and the dry whey detail. Left out on review:
  the applications launcher (it prints the internal codenames the copy
  avoids), producer listings, and the brokerage, insurance, futures-chart,
  and watchlist-picker phones. The earlier 02/03/05 deck-slide crops and
  the 1x swine dashboard came off the page the same day. A Mobile Manifest
  phone crop was tried before that and cut on review (Jason: looked wrong
  in the layout); the field app stays in the copy only. OG captured from
  the live page at 1200×630 with Playwright's headless Chromium shell.
- Bio: jasonspidle.com + `application/resume-draft.md`.
- Site-wide copy pass (2026-09-03), reviewed against the `jason-voice` skill,
  the job-search project's writing-style guide, and the Evolve cover letter
  Jason holds up as the gold standard for his application prose. What that
  letter established as the target register: pairs rather than triplets, no
  colon-then-list sentences, complete sentences of even length, reasoning
  before evidence, judgment stated as practice. Changes made on that basis:
  - One positioning line reused verbatim in the panel, og:description, and
    (with a location prefix) the meta description. Bio rewritten to lead
    with how Jason works, borrowing the letter's logic on task-organized
    screens, depth for experienced users, and coded prototypes with realistic
    data. The "fifty-some homes" line stays at Jason's request.
  - Profile heading now reads "Open to contract and full-time roles" (was
    contract only; Jason is open to both). Roster: "Product designer, then
    director" for Foundry, and "Fractional chief design officer" spelled out.
  - Every Results block was cut. Jason's rule: cut it if it only restates
    the case. The one measurable claim, Conservis "100% adoption", has no
    source Jason can produce, so it is gone; every other bullet restated the
    body. The plinth.us and design.ever.ag links moved into the body copy.
  - Ever.Ag: "public style guide" dropped. The client asked for the
    zeroheight to be password-protected in January 2023, and today's fetch
    shows mixed page-level gating flags, so the copy says only that the guide
    is published at design.ever.ag. Added the verifiably-Jason parts of the
    engagement (pitched it, owned the system hands-on from September 2022,
    set up and administered the domain, proved out the cross-org Figma
    handoff and wrote the gaps handoff) and kept "we" for the audit and
    foundations, which colleagues built.
  - Conservis: "world leader" superlative cut (unverified, not ours to make).
  - Shipped sites: Ascensus stays. Jason built the design system for
    ascensus.com and Ascensus engineers shipped it.
  - Meta descriptions changed from the "Case study: ..." label to a plain
    sentence, "A case study on ...".
  - Untouched on purpose: the editorial section headings, figure captions,
    and alt text; the title tag ("Product Designer" rather than the decided
    LinkedIn headline "Principal Product Designer"), which Jason did not
    rule on.
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
- Case imagery: `assets/*.png` (supplied). The Vidscrip case uses four revised
  captures in scrollable frames, including the procedure survey and date editor.
  Site imagery:
  `assets/sites/*.png`, captured 2026-07-17 from the four live sites at
  1440×1024 @2x with Playwright's headless Chromium shell. Ascensus is
  top-cropped to 1240px to remove a cookie banner.

## Assumptions (flagged for Jason)

1. **Navigator365 and Omnitopia are published with their domain changed.**
   The engagement is real (Blueshift, 2025; screens dated Nov–Dec 2025) but the
   client is NDA-sensitive, so both cases are rewritten out of pharma medical
   affairs and into sports representation: key opinion leaders become scouts,
   brands become the agency's players, therapeutic areas become leagues, and
   congresses become showcases. The client line reads "Sports representation
   (NDA)", and each facts table carries a `Note — Domain changed under NDA` row
   so the substitution is disclosed rather than hidden. The design problem, the
   IA, and Jason's role are described accurately; only the domain and the data
   are substituted.

   The substitution does not settle the confidentiality question. The IA and
   the analytical model — three-way sentiment split, own-brand versus
   competitor benchmarking, top-expert-per-row, three-way side-by-side compare
   — survive the translation intact and stay recognizable to anyone in the
   original market. Jason's contact at the client (Doug) reviewed both pages
   and approved them without changes on 2026-09-04 for display without
   password protection. The preview gate (`functions/_middleware.js`) and
   the two sitemap omissions were removed the same day.

   **Screens redrawn 2026-09-04.** All eleven frames were edited in Figma
   from the prompts in `specs/case-studies/domain-shift.md` and exported to
   `qa/precision-screens/`; `assets/expert-insights-01..07.png` and
   `assets/campaign-sim-01..04.png` are those exports. The edit went past
   the text-only brief in two ways: the client's magenta accent is recolored
   on every frame, and the campaign currency reads as euros rather than the
   original cent glyph. `expert-insights-05..07` are 1788x1788 crops of the
   2880x2048 dashboard frames at offset x 1092, y 260 (the answer panel with
   the roster table behind it), which holds the panel close to 1:1 in the
   852px measure where the full frame showed it at 59%. Every frame is a 2x
   export (2880x2048); the Campaign Sim set first came out at 1x and was
   re-exported the same day. Both OG images were regenerated from the local
   pages. All eleven files have been public since the gate came out on
   2026-09-04.

   One content slip was caught on review and fixed in the re-export: the
   Review Campaign Resources card had been filled with youth-movement
   Scouting costs (trail permits, campsite fees) where the source frame had
   placeholder "Resource 1" rows. It now reads Match Travel, Showcase Fees,
   and Video Analysis.

2. **Years**: Conservis 2016–21 (Jason, 2026-09-03; the screens are 2019
   but the engagement ran from the first dashboard wireframes in January 2016
   through 2021), Vidscrip 2021 (procedure dates in screens),
   Navigator/Omnitopia 2025.
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
