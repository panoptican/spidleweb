# Verification — portfolio rebuild (2026-07-17)

No automated checks exist (static site, no build). Manual verification via
Playwright headless-shell renders of every page from `file://` URLs; captures
in `qa/screens/` (gitignored).

## Checked

- `index.html` at 1440×900, 1440×2900 (full page), 390×844: name fits the
  panel at all widths, index rows align, sites grid renders four equal
  16:10 frames, profile columns don't collide, contact email doesn't
  overflow, footer renders.
- `work/conservis.html` at 1440×900 and 390 wide: panel facts table, article
  sections, figures render; images load from `../assets/`.
- `work/vidscrip.html` at 1440×900 and 390×844: side-by-side scrollable
  phone frames render; all four revised captures load and remain scrollable;
  frames stack on mobile.
- `work/navigator.html`, `work/omnitopia.html` at 1440×900: hyphenated
  panel titles break correctly; figures load.
- Reveal script ran in all captures (content visible), and defaults to
  visible under reduced motion / no JS by construction.
- All internal links are relative (`work/*.html` ↔ `../index.html`), so the
  site works from `file://` and any static host.
- Final release audit: all five release pages returned HTTP 200 at 1440×900
  and 390×844; local images and both font families loaded; no page errors,
  missing local references, missing image alt text, duplicate IDs, clipping,
  or horizontal overflow were found. Normal-motion scroll testing left zero
  unrevealed sections on every page.

## Fixed during verification

- Name overflowed the panel (GT America Expanded width) — display sizes cut
  to 6.6vw desktop / 13.5vw mobile.
- Ascensus screenshot: `sips -c` crops from center, so the cookie banner
  survived the first crop; retaken and top-anchored via `--cropOffset 0 0`.
  Thumbnail also uses `object-position: left top` so the hero copy shows.
- `.site-card__frame` needed `display: block` for equal-aspect thumbnails.
- Contact email and profile heading sized down to prevent overflow.
- Stats columns now allow their contents to shrink, and the Navigator365 and
  Omnitopia count labels were tightened to prevent expanded display type from
  widening the desktop page.

## Not verified

- Real-device Safari/iOS rendering (headless Chromium only).
- Hover states were reviewed in CSS, not interactively.
- The abstract SVG favicon is linked from the index and all four case studies;
  its request returns HTTP 200.

## Release render notes

- Playwright CLI blocks `file://` navigation, so the final render used a
  temporary local Python static server on port 8001 and Playwright's bundled
  headless Chromium. The server was stopped after verification.
- Release screenshots are in `qa/screens/release-*.png` (gitignored).

## PLINTH case study (2026-08-20)

Same method as the rebuild: headless-shell renders from `file://`, no
automated checks exist.

### Checked

- `work/plinth.html` at 1440x900, 1440x4600 (full page), 1280, 1024, 900,
  800, and 390x6000. Cover grid is two-up with issue 07 spanning the full
  measure; collapses to one column under 768px. Panel facts fit on one line
  down to 1024 and wrap cleanly right-aligned at 900 and below — the
  "Unwin-Dunraven Literary Ecclesia" value is the widest thing in the panel
  and was the reason for checking those widths.
- Hover branch verified by rendering a scratch page that forces
  `filter: none` and the accent label, since headless shell cannot hover:
  covers reveal full colour and the issue label turns accent. The touch
  branch (no `hover: hover`) shows full colour by construction, as with the
  existing `.figure__frame` pattern.
- `index.html` at 1440x2000 with reduced motion forced: the sixth index row
  renders with the issue 06 thumbnail, which is the only cover legible at
  80x50. Note that reveal-on-scroll makes normal-motion captures of the
  lower rows unreliable — force reduced motion when capturing the index.
- Next-project chain re-verified as a complete cycle in index order:
  expert-insights → campaign-sim → everag → vidscrip → conservis → plinth →
  expert-insights.
- Every local reference in `work/plinth.html` resolves; all eight external
  links point at plinth.us and returned 200 during research.
- `assets/og/plinth.png` is 1200x630 and matches the framing of the other
  case OG captures.

### Fixed during verification

- Cover images rendered squashed to 1000px tall: the tags carry intrinsic
  `width`/`height` to reserve layout space, and `.cover__frame img` set
  `width: 100%` without `height: auto`. The older `.figure__frame img` rule
  has the same gap but no case hits it, because those tags omit dimensions.
- Index reveal stagger only defined delays for rows 1–4; rows 5 and 6 now
  continue the 60ms step, so Conservis picks up a 240ms delay it did not
  have before.

### Reading-page grid (added same day)

- `.covers` now carries two lists on the page, so `.cover__no`/`.cover__type`
  were renamed to `.cover__id`/`.cover__note`, and the full-measure span moved
  off `li:last-child` onto an explicit `.cover--wide` — otherwise the fourth
  reading page would have stretched across the grid. Re-checked that the
  seven-cover run still closes on the wide issue 07 frame.
- Reading grid rendered as a clean 2x2 at 1440 and stacked at 390. All four
  reading-page URLs returned 200.
- Caption lines wrapped raggedly at phone width, where two mono labels cannot
  share one line: `.cover__meta` now stacks and `.cover__note` left-aligns
  under 768px.
- Conn frame re-cropped after review; re-checked that it and Kreiden still
  render at equal height with their captions on a shared baseline.

## Text-balancing pass (2026-08-26)

Playwright/Chromium against a local `http-server`, all seven pages
(`index.html` plus the six case studies) at 1440×900, 769, 768, 390×844,
and 320 wide. Line boxes were read back per element with a `Range`, so the
numbers below are measured wrapping, not eyeballed.

### Checked

- Display headings (`.article__head`, `.panel__type`, `.index__title`,
  `.profile__title`, `.next__title`) now set `text-wrap: balance`. Mean
  raggedness across the 84 multi-line headings in the sweep fell from 41.2%
  to 21.8%. The Ever.Ag opener, the worst case, went from 492/690/272px to
  492/406/556px at 1440.
- No heading anywhere gained a line, at any of the five widths.
- Years and ranges no longer break at the en dash: seven wrapped instances
  in the index, panel facts, and sticky header (`2022–24`, `2014–19`) went
  to zero. `.index__year` carries `white-space: nowrap`; the values inside
  the panel `Year` row, the case header, and the profile roster are wrapped
  in `.nobreak`.
- Case prose and results tightened from 62ch to 58ch, matching the profile
  measure that was already 58ch. Computed max-width resolves to 580px on
  every case study.
- `text-wrap: pretty` verified as the computed value on body paragraphs,
  panel blurbs, figure captions, cover notes, profile copy, and result
  items — 158 elements asserted across the seven pages, zero misses.
- No horizontal overflow at any page/width combination.

### Fixed during verification

- Widening the mobile year column to a fixed `4rem` bought room for
  `2022–24` but pushed "Campaign Sim" onto two lines at 390. The column is
  `auto` under 768px instead, so it sizes to the range and leaves the title
  everything else. Years still right-align on a shared edge, because each
  row's grid ends at the same x.

## Precision screens (2026-09-04)

Python Playwright (Chromium, `reduced_motion='reduce'`) against the
`spidleweb-static` preview server on port 8765, both pages at 1440×900 and
390×844 with full-page captures in `qa/screens/precision-*.png` (gitignored).

### Checked

- `work/expert-insights.html`: seven figures, every image responds 200 and
  decodes (`complete && naturalWidth > 0`); `-01` to `-04` at 2880×2048
  render at 756×538, the three 1788×1788 answer-panel crops at 756×756. Four
  sections, all revealed; no horizontal overflow at either width; no console
  errors or failed requests other than the analytics script, which is
  external.
- `work/campaign-sim.html`: four figures in the new order (`-03`, `-01`,
  `-02`, `-04`), same checks, same result. First run was against 1×
  exports (1440×1024); re-run after the 2× re-export and the Resources-card
  fix, all four at 2880×2048, same 756×538 render, still clean.
- Captions and alt text read back from the DOM match the HTML.
- OG images recaptured with the Playwright CLI at 1200×630 after a 2s
  settle; both show the sports-domain panel facts and opening copy, with the
  first figure's top edge in frame as before.
- Preview gate: `GATED` gained `expert-insights-04..07` and
  `campaign-sim-04`; the `-01` thumbnails stay public. Not exercised locally
  (`wrangler pages dev` was not run); the set is a plain string list.

### Not verified

- Hover colorization on the new figures (CSS unchanged, same `.figure`
  pattern as every other case).
- The gate on a deployed preview.

## Gate removal (2026-09-04)

Client approved both Precision case studies without changes, so the
client-preview gate came out.

### Checked

- `functions/` is gone entirely (the middleware was its only file), so the
  project deploys as pure static again.
- `sitemap.xml` parses (`xmllint --noout`) and lists all seven pages,
  `/work/expert-insights` and `/work/campaign-sim` restored with a 2026-09-04
  `lastmod`.
- Neither case page carries a `noindex` meta; the only `noindex` was the
  header the middleware set, so nothing else keeps search engines out.
- `grep` for `middleware`, `PREVIEW_PASSWORD`, `PREVIEW_COOKIE_KEY`, and
  `noindex` across the site, docs, and specs turns up only the historical
  notes in `docs/deployment.md` and the specs.

### Not verified

- The live site: the gate is removed on push, and the two Pages secrets stay
  set on the project until deleted by hand (commands in
  `docs/deployment.md`).
