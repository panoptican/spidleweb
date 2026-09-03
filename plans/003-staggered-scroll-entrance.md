# 003 — Stagger Case Index and Shipped Sites Scroll Reveal

- **Status**: DONE
- **Commit**: 11ca3ad
- **Severity**: LOW
- **Category**: Cohesion & tokens / Group entrances
- **Estimated scope**: 1 file (style.css), ~12 lines of CSS

## Problem

In [index.html](file:///Users/jason/Projects/websites/spidleweb/index.html), the case index rows and the shipped sites grid cards are revealed simultaneously using the `.reveal` and `.reveal.is-in` classes (driven by IntersectionObserver in [script.js](file:///Users/jason/Projects/websites/spidleweb/script.js) and styling in [style.css:L491-497](file:///Users/jason/Projects/websites/spidleweb/style.css#L491-L497)):

```css
/* style.css:491 — current */
.reveal { opacity: 0; transform: translateY(14px); }

.reveal.is-in {
  opacity: 1;
  transform: none;
  transition: opacity 0.55s ease, transform 0.55s cubic-bezier(0.16, 1, 0.3, 1);
}
```

When a user scrolls down the page, groups of items trigger simultaneously and pop in at the exact same instant, creating a blocky and rigid entrance effect.

## Target

Introduce a progressive `60ms` delay stagger per sibling item using CSS `:nth-child` child selectors for the items in the Case study index list and Shipped sites grid. Ensure this stagger delay is reset to `0ms` (or transition is disabled entirely) under `prefers-reduced-motion: reduce`.

```css
/* target */
.index li:nth-child(1) .reveal { transition-delay: 0ms; }
.index li:nth-child(2) .reveal { transition-delay: 60ms; }
.index li:nth-child(3) .reveal { transition-delay: 120ms; }
.index li:nth-child(4) .reveal { transition-delay: 180ms; }

.sites li:nth-child(1).reveal { transition-delay: 0ms; }
.sites li:nth-child(2).reveal { transition-delay: 60ms; }
.sites li:nth-child(3).reveal { transition-delay: 120ms; }
.sites li:nth-child(4).reveal { transition-delay: 180ms; }
```

## Repo conventions to follow

- Existing reveal rules are defined at the end of [style.css](file:///Users/jason/Projects/websites/spidleweb/style.css).
- Stagger delays are applied directly via CSS structure, keeping JS lightweight.

## Steps

1. Open [style.css](file:///Users/jason/Projects/websites/spidleweb/style.css).
2. Locate the `.reveal.is-in` rules (around line 493).
3. Append the staggered delay rules for `.index li:nth-child(n) .reveal` and `.sites li:nth-child(n).reveal` right below it.
4. Verify that `@media (prefers-reduced-motion: reduce)` (around line 499) completely resets or removes the transitions (which it already does by setting `transition: none;`).

## Boundaries

- Do NOT modify [script.js](file:///Users/jason/Projects/websites/spidleweb/script.js) or the HTML markup of case lists/grids.
- Stagger must never block interaction or delay usability.

## Verification

- **Mechanical**: Ensure the site renders correctly in the browser without any lint errors.
- **Feel check**:
  - Load the index page and scroll down to trigger the scroll reveals. Confirm the case list and the shipped sites grid items fade and slide up sequentially (cascading down), rather than all at once.
  - In DevTools Rendering panel, toggle `prefers-reduced-motion: reduce` and verify all elements appear instantly without any delays or animations.
- **Done when**: Reveal elements in lists/grids cascade in on scroll under standard settings, and display immediately with zero transition delay under reduced motion.
