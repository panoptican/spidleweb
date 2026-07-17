# Variant rating tool

A self-contained, shareable reviewer for the 25 Paper index-page design variants. No build step, no backend — a single `index.html` plus the `variants/` PNGs. Host the folder anywhere static (GitHub Pages, Netlify drop, `python3 -m http.server`) and send the link.

## How it works for a reviewer

1. Enter your name on the welcome screen (used to tell the two exports apart).
2. Each variant fills the browser width; scroll to see the whole design.
3. The slider stays collapsed into a small floating circle (FAB) at bottom center; it expands when the cursor nears the bottom-center of the viewport, when the circle is tapped, or when the bar gets keyboard focus. Drag the slider to rate — continuous, no numbers, cool blue = dislike, hot orange = like. The thumb is dimmed until you've rated the current variant.
4. `←` / `→` (or the on-screen arrows) move between variants. Progress persists in `localStorage`, so a reload resumes where you left off.
5. A **Finish** button appears on the last variant (or once everything is rated) and downloads a JSON file to send back.

## Export format

`paper-index-ratings-<reviewer>-<date>.json`:

```json
{
  "tool": "paper-index-variant-rating",
  "formatVersion": 1,
  "reviewer": "Alex",
  "sessionId": "k3j2…",
  "startedAt": "…", "exportedAt": "…",
  "ratingScale": { "min": 0, "max": 1, "description": "…" },
  "variantCount": 25,
  "ratings": [
    { "variantId": "01", "variantName": "Live shelf (demos on the index)",
      "file": "variants/01-….png", "rating": 0.82, "ratedAt": "…" }
  ]
}
```

Every variant always appears in `ratings`, in order; skipped variants have `rating: null`. Two reviewer files merge cleanly on `variantId`, with `reviewer` + `sessionId` distinguishing sources.

## Provenance

Images were exported at 2x from the Paper file "Portfolio", page "Index" (artboards 01–25) on 2026-07-16. `variantId` matches the artboard number prefix; note 11 and 16 are both named "Field Journal" in Paper — 16 is labeled "Field Journal II" here to disambiguate.
