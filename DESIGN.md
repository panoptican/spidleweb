---
name: Spidleweb Portfolio Design System
description: The Documentarian Ledger — Brutalist, editorial design system for Jason Spidle's personal portfolio.
colors:
  paper: "#f2f2ef"
  ink: "#0a0a0a"
  accent: "#fa1900"
  line: "rgba(10,10,10,0.18)"
  line-strong: "#0a0a0a"
  panel-paper: "rgba(242,242,239,0.7)"
typography:
  display:
    fontFamily: "GT America Expanded, Arial Black, Helvetica, sans-serif"
    fontWeight: 400
    lineHeight: 0.92
    letterSpacing: "-0.02em"
  body:
    fontFamily: "GT America, Helvetica, Arial, sans-serif"
    fontWeight: 500
    fontSize: "16px"
    lineHeight: 1.5
  label:
    fontFamily: "ui-monospace, SF Mono, JetBrains Mono, Menlo, Consolas, monospace"
    fontWeight: 400
    fontSize: "0.65rem"
    letterSpacing: "0.06em"
rounded:
  none: "0px"
spacing:
  gap: "24px"
components:
  panel:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    padding: "24px"
  index-row:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    padding: "28px 0px"
  index-row-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    padding: "28px 12px"
  site-card-frame:
    backgroundColor: "#d9d9d5"
    rounded: "{rounded.none}"
---

# Design System: Spidleweb Portfolio

## 1. Overview

**Creative North Star: "The Documentarian Ledger"**

The visual language is an archive-inspired, brutalist-editorial design system. It rejects modern SaaS clichés (smooth shadows, glass card overlays, bright gradients) in favor of a raw, physical document layout. The interface acts as a stark, content-centric container featuring coordinate indicators, volume markers, registration lines, and uppercase monospace identifiers.

It uses a split layout: a solid dark panel anchored on the left and a flowing content archive on the right. Information density is treated as a sign of expertise and clarity, rather than something to hide behind tabs or modals.

**Key Characteristics:**
- Paper-and-ink high contrast.
- Strict rectangular grids separated by clean hairline rules.
- Interactive hover states based on color inversions and transition grayscale filters to full color.

## 2. Colors

A strictly limited, high-contrast palette. Neutrals carry subtle tinting to avoid clinical coldness.

### Primary
- **Archive Red** (`#fa1900` / `oklch(60.85% 0.2455 24.89)`): Used sparingly for coordinate highlights, key volume details, item numbers, and subtle accents. Never covers more than 10% of any layout.

### Neutral
- **Warm Paper** (`#f2f2ef` / `oklch(96.11% 0.0028 85.34)`): The primary canvas background. Creates a tactile, document-like warmth.
- **Ink Black** (`#0a0a0a` / `oklch(12.72% 0.0016 85.34)`): Primary text color, split panel background, and solid hover inversion surfaces.
- **Hairline Rule** (`rgba(10, 10, 10, 0.18)`): Structural boundary lines that separate entries, sections, and items.
- **Strong Line** (`#0a0a0a`): Prominent separators and structural borders.

### Case-Specific Brutalist Themes (Committed Strategy)
To give each ledger entry a distinct visual identity, case study pages use specialized color palettes. The neutrals are dynamically tinted toward each case's signature hue:

- **Conservis (AgTech)**: Earth Crop Green accent (`oklch(55% 0.16 140)`), warm sage-tinted paper background (`oklch(96.5% 0.006 140)`), dark pine panel background (`oklch(22% 0.06 140)`), and dark forest-ink text (`oklch(13% 0.008 140)`).
- **Vidscrip (Health)**: Clinical Teal accent (`oklch(55% 0.15 195)`), pale teal-tinted paper background (`oklch(96.5% 0.006 195)`), spruce panel background (`oklch(22% 0.06 195)`), and deep-ocean-ink text (`oklch(13% 0.008 195)`).
- **Navigator365 (Enterprise)**: Cobalt Blue accent (`oklch(52% 0.17 260)`), slate-blue tinted paper background (`oklch(96.5% 0.006 260)`), deep indigo panel background (`oklch(20% 0.08 260)`), and midnight-blue ink text (`oklch(13% 0.008 260)`).
- **Omnitopia (Campaign Simulation)**: Terracotta/Orange accent (`oklch(60% 0.19 50)`), sand-tinted paper background (`oklch(96.5% 0.006 50)`), rust panel background (`oklch(25% 0.08 50)`), and warm-clay ink text (`oklch(13% 0.008 50)`).

All case themes support a responsive `var(--p-color-amount, 1)` range scaling parameter that allows adjustment of the chroma from completely monochrome (0) to fully saturated (1).

### Named Rules
**The One Voice Rule.** The primary accent is used on ≤10% of any given screen. Its rarity is the point.
**The Tinted Neutral Rule.** Never use pure black (`#000`) or pure white (`#fff`). All neutrals must be slightly tinted towards warm paper/ink hues.

## 3. Typography

The type scale balances expansive uppercase titles with precise, compact metadata labels.

**Display Font:** GT America Expanded (with fallbacks Arial Black, Helvetica, sans-serif)
**Body Font:** GT America (with fallbacks Helvetica, Arial, sans-serif)
**Label/Mono Font:** ui-monospace, SF Mono, JetBrains Mono, Menlo, Consolas, monospace

**Character:** A sharp editorial pairing. Bold, uppercase, horizontally-stretched display headings contrast with a highly structured monospace labeling system.

### Hierarchy
- **Display** (Weight: 400, Size: clamp(2.2rem, 6.6vw, 7.5rem), Line-height: 0.92): Used for primary names and main display headers. Highly compressed line-height.
- **Headline** (Weight: 400, Size: clamp(1.4rem, 3vw, 2.6rem), Line-height: 1.0): Used for case study titles and index row titles.
- **Title** (Weight: 400, Size: clamp(1.4rem, 2.5vw, 2.3rem), Line-height: 1.0): Used for section headers (e.g. Profile Title).
- **Body** (Weight: 500, Size: 16px, Line-height: 1.5): Standard prose copy. Line length capped at 65ch.
- **Label** (Weight: 400, Size: 0.65rem, Letter-spacing: 0.06em, Uppercase): Used for metadata, status values, coordinates, and navigation links.

### Named Rules
**The Uppercase display Rule.** All display and headline tags must be rendered in uppercase to match the archival editorial tone.

## 4. Elevation

The design system is entirely flat and paper-like. Depth is conveyed strictly via layout positioning, boundaries, and high-contrast color fills rather than simulated shadows.

### Named Rules
**The Absolute Flatness Rule.** No element uses `box-shadow` or `filter: drop-shadow`. Contrast and layering must be achieved solely via solid background changes or hairline borders.
**The Inversion Response Rule.** Interactive items do not lift off the page. Instead, they respond to cursor interaction by swapping text and background colors (`background: var(--ink)` and `color: var(--paper)`).

## 5. Components

### Navigation
- **Style:** Horizontal list of mono-spaced link items separated by gap spacing.
- **Hover/Active:** Text changes to Accent color. Text decoration is omitted.

### Case Index Rows
- **Layout:** 4-column baseline aligned grid (`3.5rem 1fr minmax(0, 11rem) 4rem`) with hairline separator border.
- **States:** Hover triggers full row inversion (background turns to Ink Black, text turns to Warm Paper). Margin expands slightly (`-12px`) and padding shifts (`12px`) to pad the inverted block. Number turns to Accent Red.

### Site Cards
- **Structure:** Aspect ratio `16/10` bordered image frame (`border: 1px solid var(--line-strong)`) with caption underneath.
- **Grayscale Transition:** Images are rendered in 100% grayscale with contrast enhanced. Hover transitions to full color and scales up (`scale(1.03)`).

### Split Panel
- **Layout:** Sticky column, full height (`100vh`). Ink background, paper text. Includes structural coordinate metrics at the top and bio/location metadata at the bottom.

## 6. Do's and Don'ts

### Do:
- **Do** use strict hairline rule dividers (`rgba(10, 10, 10, 0.18)`) to separate adjacent rows and columns.
- **Do** align metadata labels using the system monospace font family.
- **Do** use full-color images only as hover transitions on grayscale elements.

### Don't:
- **Don't** use side-stripe borders (e.g. left borders on alerts or cards) to highlight elements.
- **Don't** apply text gradients or background-clip text treatments.
- **Don't** add drop shadows or box-shadows to panels, site cards, or rows.
- **Don't** use rounded card corners or rounded borders (always use sharp `0px` corners).
- **Don't** implement bouncy or elastic transition curves (use clean, linear, or expo transitions).
