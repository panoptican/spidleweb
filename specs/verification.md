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
