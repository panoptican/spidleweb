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
