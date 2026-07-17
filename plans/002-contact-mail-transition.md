# 002 — Add Transition to Contact Email Hover

- **Status**: DONE
- **Commit**: 11ca3ad
- **Severity**: LOW
- **Category**: Easing & duration
- **Estimated scope**: 1 file (style.css), ~8 lines of CSS

## Problem

In [style.css](file:///Users/jason/Projects/personal/spidleweb/style.css), `.contact__mail` (lines 334-348) snaps immediately to the accent red color and red bottom border on hover/focus:

```css
/* style.css:348 — current */
.contact__mail:hover { color: var(--accent); border-color: var(--accent); }
```

This sudden color swap lacks the subtle polish found on other content/image hover elements of the portfolio.

## Target

Introduce a quick `120ms` ease-out transition on `color` and `border-color` gated by `@media (hover: hover) and (pointer: fine)`.

```css
/* target */
@media (hover: hover) and (pointer: fine) {
  .contact__mail {
    transition: color 0.12s ease-out, border-color 0.12s ease-out;
  }
}
```

## Repo conventions to follow

- Hover transitions are placed on the base selector (not the `:hover` pseudo-class) to ensure smooth transitions in both directions.
- All styles live in [style.css](file:///Users/jason/Projects/personal/spidleweb/style.css).

## Steps

1. Open [style.css](file:///Users/jason/Projects/personal/spidleweb/style.css).
2. Locate the `.contact__mail` class definition (around line 334).
3. Wrap the transition property in a `@media (hover: hover) and (pointer: fine)` query block targeting `.contact__mail`.

## Boundaries

- Do NOT change structural HTML or Javascript.
- Do NOT change other font or text styling.

## Verification

- **Mechanical**: Ensure the site renders correctly in the browser without any lint errors.
- **Feel check**:
  - Hover cursor over the contact email link at the bottom of the page. Confirm the color transitions smoothly and Snaps back cleanly when the cursor leaves.
- **Done when**: `.contact__mail` transitions text and border colors smoothly on hover under hover-supported environments.
