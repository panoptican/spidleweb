# 001 — Smooth Case Index and Next Project Hover Inversions

- **Status**: DONE
- **Commit**: 11ca3ad
- **Severity**: MEDIUM
- **Category**: Preventing a jarring change
- **Estimated scope**: 1 file (style.css), ~20 lines of CSS

## Problem

In [style.css](file:///Users/jason/Projects/websites/spidleweb/style.css), case index rows (`.index__row`, lines 189-208) and the next project handoff link (`.next`, lines 453-472) swap text and background colors immediately, and expand layout margins/paddings on hover and focus:

```css
/* style.css:200 — current */
.index__row:hover,
.index__row:focus-visible {
  background: var(--ink);
  color: var(--paper);
  padding-left: 12px;
  padding-right: 12px;
  margin: 0 -12px;
  outline: none;
}

/* style.css:465 — current */
.next:hover, .next:focus-visible {
  background: var(--ink);
  color: var(--paper);
  padding-left: 12px;
  padding-right: 12px;
  margin-left: calc(var(--gap) - 12px);
  margin-right: calc(var(--gap) - 12px);
  outline: none;
}
```

These instant layout shifts and color inversions cause a jarring repaint jump when the user moves the mouse across the page list.

## Target

Introduce smooth transitions for layout properties (`padding`, `margin`) and colors (`background-color`, `color`) using the repository's custom expo curve `cubic-bezier(0.16, 1, 0.3, 1)` over `150ms`. These transitions must be gated by hover-capable media queries to prevent issues on mobile tap interactions. Under `prefers-reduced-motion: reduce`, layout transitions must be bypassed, only transitioning colors over a short `50ms` duration.

```css
/* target */
@media (hover: hover) and (pointer: fine) {
  .index__row {
    transition: background-color 0.15s cubic-bezier(0.16, 1, 0.3, 1),
                color 0.15s cubic-bezier(0.16, 1, 0.3, 1),
                padding-left 0.15s cubic-bezier(0.16, 1, 0.3, 1),
                padding-right 0.15s cubic-bezier(0.16, 1, 0.3, 1),
                margin-left 0.15s cubic-bezier(0.16, 1, 0.3, 1),
                margin-right 0.15s cubic-bezier(0.16, 1, 0.3, 1);
  }
  .next {
    transition: background-color 0.15s cubic-bezier(0.16, 1, 0.3, 1),
                color 0.15s cubic-bezier(0.16, 1, 0.3, 1),
                padding-left 0.15s cubic-bezier(0.16, 1, 0.3, 1),
                padding-right 0.15s cubic-bezier(0.16, 1, 0.3, 1),
                margin-left 0.15s cubic-bezier(0.16, 1, 0.3, 1),
                margin-right 0.15s cubic-bezier(0.16, 1, 0.3, 1);
  }
}

@media (prefers-reduced-motion: reduce) {
  .index__row, .next {
    transition: background-color 0.05s ease-out, color 0.05s ease-out;
  }
}
```

## Repo conventions to follow

- The custom expo curve `cubic-bezier(0.16, 1, 0.3, 1)` is already defined in [style.css:L267](file:///Users/jason/Projects/websites/spidleweb/style.css#L267) and [style.css:L496](file:///Users/jason/Projects/websites/spidleweb/style.css#L496).
- All transitions are written in [style.css](file:///Users/jason/Projects/websites/spidleweb/style.css).

## Steps

1. Open [style.css](file:///Users/jason/Projects/websites/spidleweb/style.css).
2. Locate `.index__row` (around line 189) and add the hover-gated transition definition.
3. Locate `.next` (around line 453) and add the hover-gated transition definition.
4. Locate the `@media (prefers-reduced-motion: reduce)` block (around line 499) and add overrides for `.index__row` and `.next` to only transition `background-color` and `color` over `0.05s` with `ease-out`.

## Boundaries

- Do NOT change structural HTML or Javascript.
- Do NOT introduce any new animation libraries.
- If the CSS structure has shifted, STOP and report.

## Verification

- **Mechanical**: Ensure the site renders correctly in the browser without any lint errors.
- **Feel check**:
  - Hover cursor over case study items in the index grid. Confirm that the background expansion and text color inversion glide cleanly and responsively (150ms), rather than instantly popping.
  - Hover over the next-project row at the bottom of case study pages and verify the same smooth transition behavior.
  - In DevTools Rendering panel, toggle `prefers-reduced-motion: reduce` and verify the background and text color inversion happens instantly (50ms) without any layout sliding transitions.
- **Done when**: `.index__row` and `.next` elements smoothly transition on hover under desktop environments, and safely fall back under reduced-motion settings.
