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

## Blueshift case study (2026-08-21)

Rendered from a local `python3 -m http.server` on 8011 with Playwright
driving the installed Chrome, since the bundled Chromium revisions in the
npx caches no longer match the installed Playwright.

### Checked

- `work/blueshift.html` at 1440x900, 1440x7073 (full page), and 390x8702.
  Cover grids are two-up with Surge, the Surge panel, and the packages frame
  spanning the full measure; all collapse to one column under 768px with
  captions stacked and left-aligned.
- Scripted audit at 1440x900 and 390x844 over `index.html` and the five
  case studies in the chain: HTTP 200, no broken or alt-less images, no
  duplicate ids, no horizontal overflow, no page errors, no 4xx sub-requests,
  and zero unrevealed `.reveal` sections after a full scroll.
- Panel facts fit the 320px column; the Partners value wraps to two lines
  right-aligned, which is the same behaviour as PLINTH's publisher value.
- Cover captions were shortened after the first render: several `.cover__note`
  values ran past their half-width cell and wrapped under the id. Anything
  over roughly 25 characters wraps in a two-up cell at 1440.
- Next-project chain re-verified as a complete cycle in the new index order:
  expert-insights → campaign-sim → blueshift → everag → vidscrip →
  conservis → plinth → expert-insights.
- All ten external links point at blueshift-consulting.com and returned 200
  during capture.
- `assets/og/blueshift.png` is 1200x630 and matches the framing of the other
  case OG captures.

### Changed while adding it

- Index row hover accents were keyed by `nth-child`, so inserting a row in
  the middle silently reassigned every colour below it. They now key off a
  `data-case` attribute on the `li` instead. The reveal stagger still keys
  off position, which is correct, and gained a seventh step.

### Not verified

- Hover states were reviewed in CSS, not interactively; headless capture
  cannot hover. The grayscale-to-colour branch is the same `.cover__link`
  rule PLINTH already exercises.
- Real-device Safari/iOS rendering.
