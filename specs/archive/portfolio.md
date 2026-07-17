# spidleweb.net — portfolio concept

## Goal
Personal portfolio at spidleweb.net. Structure and pacing modeled on kevn.co: brief intro, then a visual-first body of work. Split into two piles:
1. Traditional product design work.
2. Things I designed and built with the aid of coding agents — shown as live, in-page interactive pieces, not screenshots.

## Structure (single long-scroll page)
1. Hero — name, one-sentence positioning, one secondary line
2. Background — 3-5 sentences, inline
3. Selected work — product design (visual grid, captions only, no detail pages)
4. Built with agents — interactive pieces (designed and built with coding agents), one per row, iframed from `/agents/<slug>/`
5. Contact — single line

## Navigation
No top nav at rest. A small fixed marker (name + Work / Agents jump links) fades in after the hero scrolls out of view.

## Typography
- GT America Medium — body and labels
- GT America Expanded Regular — name, section markers, large display moments
- Helvetica fallback until font files are dropped into `/fonts`

If additional weights/widths are needed, flag and request purchase.

## Stack
- Vanilla HTML/CSS/JS, single `index.html`
- No framework, no build step
- 2-space indent
- Agent demos: standalone HTML files under `/agents/<slug>/index.html`, lazy-loaded via `<iframe>`
- Hosting: static (Cloudflare Pages or similar), domain spidleweb.net

## Open items
- Real agent demos (3-4) — stubbed for now
- Hosting target confirmation
- Product work assets — placeholders for now
