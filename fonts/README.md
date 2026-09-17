# Fonts

GT America web files are stored in the private `spidleweb-fonts` R2 bucket,
served by the `/fonts/*` Pages Function, referenced from `style.css`, and
preloaded on the pages that use them:

- `GT-America-Standard-Medium.woff2` / `.woff` — GT America Medium
  (homepage body, weight 500)
- `GT-America-Expanded-Regular.woff2` / `.woff` — GT America Expanded Regular
  (display, weight 400)

`woff2` is what every current browser takes; `woff` is the fallback in the
`src` list. Only the `woff2` files are preloaded, so a browser fetches one
file per face. Until they load the site falls back to Helvetica
(`font-display: block`, so display type does not flash in a substitute).
Mono micro-labels use the system mono stack (SF Mono / Menlo), no file needed.

These replaced unhinted `.ttf` copies of the same two faces in September 2026:
identical version 1.005 outlines, same 1000 upem, same 722 glyphs, same
advance widths — 312 KB of `.ttf` became 96 KB of `.woff2` with no visual
change.

## This directory is the origin for both sites

`tools.spidleweb.net` loads these same two faces from
`https://spidleweb.net/fonts/` rather than carrying its own copies, because
the Atomic Tools repo is public and these are licensed files. `_headers`
grants `/fonts/*` the CORS header cross-origin font loading needs, and caches
them for a year as `immutable`.

Two consequences. Moving or renaming a file here breaks type on that site too,
so grep the atomic-tools repo first. And because of that year-long cache,
replacing a face means giving the file a new name — overwriting one in place
leaves year-old copies in browsers that already have it.

Licensing note: these are licensed font files from Grilli Type. The `.woff`
and `.woff2` files must not be committed to this repository.

## Case-study serif (2026-09-16)

The B + F case studies use EB Garamond Regular (400, normal) for prose,
project facts, and captions. The public WOFF2 and its complete OFL notice are
tracked under `assets/fonts/eb-garamond/`, outside the `/fonts/*` private
Pages Function. That Function's allowlist and R2 binding are unchanged.
See the asset directory's README for the exact upstream URL and version.
Case studies preload this face and GT America Expanded Regular; the homepage
retains its existing GT America Medium preload and typography. No GT Alpina
or trial font is included. `font-synthesis: none` on case studies avoids
inventing weights or italics that have not been loaded.
