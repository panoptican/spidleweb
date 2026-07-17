# Spec: Portfolio Colorization (2026-07-17)

## 1. Intent
Add purposeful, strategic color to the Spidleweb brutalist portfolio site. Previously, the portfolio used a strict paper-and-ink monochrome layout with a single Red accent (`#fa1900`). The goal of this task is to introduce a **Committed** color strategy that elevates each case study, providing a unique personality for each project sector while preserving the raw brutalist "Documentarian Ledger" aesthetic.

## 2. Design Strategy
Instead of applying colors arbitrarily, the color system is built around the following guidelines:
1. **Neutrals are Tinted**: The background paper (`--paper`) and primary ink text (`--ink`) are subtly tinted toward each case study's brand hue. This complies with the *Tinted Neutral Rule* and avoids the clinical coldness of pure black and white.
2. **Drenched/Committed Left Panel**: The sticky left panel (`42vw` width) transitions from standard `Ink Black` to a rich, saturated, dark variant of the case study's brand color.
3. **Hover Preview Waypoints**: On the homepage scroll index, hovering a row triggers an inversion that displays the specific signature color of the destination case study, providing an interactive hint of the color palette to come.
4. **Accessible OKLCH Contrasts**: Colors are defined using perceptually uniform `oklch()`. Text contrast remains high (well exceeding WCAG 4.5:1 requirements) by pairing light text with dark panel backgrounds, and keeping body ink text very dark (13% lightness) on light tinted paper backgrounds (96.5% lightness).
5. **Live Parameter Multiplier**: All themes support `var(--p-color-amount, 1)`, allowing live adjustments to scale down chroma to completely monochrome (0) or up to full saturation (1).

## 3. Themes Definition

```css
/* Conservis (AgTech - Green/Sage) */
.theme-conservis {
  --c-chroma: calc(0.14 * var(--p-color-amount, 1));
  --paper-chroma: calc(0.006 * var(--p-color-amount, 1));
  --panel-chroma: calc(0.06 * var(--p-color-amount, 1));
  --paper: oklch(96.5% var(--paper-chroma) 140);
  --ink: oklch(13% var(--paper-chroma) 140);
  --accent: oklch(55% var(--c-chroma) 140);
  --panel-bg: oklch(22% var(--panel-chroma) 140);
}

/* Vidscrip (Healthcare - Teal/Spruce) */
.theme-vidscrip {
  --c-chroma: calc(0.13 * var(--p-color-amount, 1));
  --paper-chroma: calc(0.006 * var(--p-color-amount, 1));
  --panel-chroma: calc(0.06 * var(--p-color-amount, 1));
  --paper: oklch(96.5% var(--paper-chroma) 195);
  --ink: oklch(13% var(--paper-chroma) 195);
  --accent: oklch(55% var(--c-chroma) 195);
  --panel-bg: oklch(22% var(--panel-chroma) 195);
}

/* Navigator365 (Enterprise Analytics - Cobalt/Indigo) */
.theme-navigator {
  --c-chroma: calc(0.17 * var(--p-color-amount, 1));
  --paper-chroma: calc(0.006 * var(--p-color-amount, 1));
  --panel-chroma: calc(0.08 * var(--p-color-amount, 1));
  --paper: oklch(96.5% var(--paper-chroma) 260);
  --ink: oklch(13% var(--paper-chroma) 260);
  --accent: oklch(52% var(--c-chroma) 260);
  --panel-bg: oklch(20% var(--panel-chroma) 260);
}

/* Omnitopia (Simulated Campaigns - Orange/Rust) */
.theme-omnitopia {
  --c-chroma: calc(0.19 * var(--p-color-amount, 1));
  --paper-chroma: calc(0.006 * var(--p-color-amount, 1));
  --panel-chroma: calc(0.08 * var(--p-color-amount, 1));
  --paper: oklch(96.5% var(--paper-chroma) 50);
  --ink: oklch(13% var(--paper-chroma) 50);
  --accent: oklch(60% var(--c-chroma) 50);
  --panel-bg: oklch(25% var(--panel-chroma) 50);
}
```

## 4. Verification Notes
- **Contrast Ratios**: Verified that all tinted neutrals maintain proper contrast values. Light backgrounds are strictly `96.5%` lightness while dark panels are `20%–25%` lightness.
- **Cascading Variables**: Verified that hairline rules, dividers, active states, layout borders, and select text links inherit these changes naturally due to dynamic CSS custom properties.
- **Reduced Motion Support**: Checked that color transition times and grayscale shifts adapt to prefers-reduced-motion media query restrictions.
