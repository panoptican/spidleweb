# Research: embedding many live pieces on a static site

Resolves [issue #8](https://github.com/panoptican/spidleweb/issues/8). Question: proven techniques for embedding 5–10 independent interactive pieces ("built with agents" demos) on a static, no-build, vanilla HTML/CSS/JS site.

Context that shaped the answer: each piece already lives as a standalone document at `agents/<name>/index.html`, authored by different agent sessions with their own full-page CSS/JS. Everything is first-party and same-origin.

## The two families of techniques

### 1. Iframe isolation

Each piece is a self-contained HTML document loaded via `<iframe src="agents/<name>/" …>`.

**Isolation.** Total by construction: separate document, separate `window`, separate stylesheet universe, separate JS globals. A piece can use `body { margin: 0 }`, global event listeners, `requestAnimationFrame` loops, or clashing class names with zero risk to the host page or sibling pieces. This is the only technique where pieces written independently (e.g., by different agent sessions) need no authoring conventions at all.

**Performance.** The cost model depends on origin:

- *Same-origin iframes* (this site's case) share the parent's renderer process and main thread. There is no per-iframe ~17 MB process tax; that tax applies to cross-origin/out-of-process iframes ([webperf.tips: Iframes and Process Allocation](https://webperf.tips/tip/iframe-multi-process/), [Dave Hunt: measuring iframe memory](https://dev.to/pete_gleeson/what-is-an-iframe-3bi2)). Each iframe still creates its own `Window`/`Document`/frame objects — real but modest overhead per frame.
- Because same-origin frames share the main thread, a long task or hot animation loop in one piece *does* compete with the host page and other pieces ([webperf.tips](https://webperf.tips/tip/iframe-multi-process/)). Isolation is for correctness, not for CPU.
- Historically, eager iframes delayed the host's `onload` and competed for connections ([Souders: Using Iframes Sparingly](https://www.stevesouders.com/blog/2009/06/03/using-iframes-sparingly/)); lazy loading (below) sidesteps this entirely for below-the-fold pieces.
- Anecdotal benchmarks find web components ~4× faster to first render than equivalent iframes for widget-scale content ([Lewis: iframes vs Web Components 2025](https://dp-lewis.medium.com/iframes-vs-web-components-which-one-actually-performs-better-in-2025-4db95784eb9f)); the BBC moved off iframes largely for load cost and height-resizing pain ([BBC: Goodbye iframes](https://medium.com/bbc-product-technology/goodbye-iframes-6c84a651e137)). Both are for the "many third-party embeds" case; at 5–10 first-party, lazy-loaded frames the difference is not user-visible.

**Sizing.** An iframe does not size to its content. Either give each piece a fixed size / `aspect-ratio` box (fine for demo tiles, also prevents layout shift), or use `postMessage`/`ResizeObserver` height reporting (the complexity that drove the BBC off iframes). Fixed aspect boxes are the simple answer here.

### 2. Inline mounting (custom elements / scoped scripts / shadow DOM)

Each piece is a `<script type="module">` that defines a custom element (or mounts into a `<div>`), with markup/styles inside a shadow root.

**Isolation.** Shadow DOM gives real two-way *selector* scoping: page styles don't select into the shadow tree, shadow styles don't leak out ([MDN: Using shadow DOM](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_shadow_DOM), [MDN: CSS scoping](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scoping)). Two documented leaks remain:

- *Inheritable properties* (`color`, `font-*`, `line-height`, …) and *CSS custom properties* cross the boundary by design ([Matuzovic: Pros and cons of Shadow DOM](https://www.matuzo.at/blog/2023/pros-and-cons-of-shadow-dom/), [web.dev: Shadow DOM 201](https://web.dev/articles/shadowdom-201)). Usually desirable for theming; a `:host { all: initial }` reset closes it when not.
- *JavaScript is not isolated at all.* All inline pieces share one `window`, one global scope, one event loop. ES modules scope top-level `const`/`let`, but anything touching `window`, `document`-level listeners, or shared singletons can collide. Every piece must be written to a convention (module scope, listeners attached inside its own root, no global CSS). Agent-authored full-page demos violate this by default — each `agents/*/index.html` currently assumes it owns the whole document.

**Performance.** Cheapest option: one document, no per-frame `Window`/`Document` objects, no frame-loading overhead, natural content-based sizing. Same main-thread sharing as same-origin iframes.

**Cost.** Converting each standalone demo into a well-behaved custom element is real per-piece work and an ongoing discipline every future agent session must follow. It also removes the nicest property of the current layout: each piece is independently openable at its own URL.

## Lazy loading

Two layers, both needed:

1. **Deferred load.** `loading="lazy"` on iframes is now supported in all major engines (Chrome 77+, Firefox 121+, Safari 16.4+) and defers fetching until near-viewport; Google measured ~2–3 % median data savings and FCP wins ([web.dev: iframe lazy-loading](https://web.dev/articles/iframe-lazy-loading)). Its threshold is browser-chosen and generous; if tighter control is wanted, the classic pattern is `data-src` + `IntersectionObserver` swap-in ([LogRocket: lazy loading with IntersectionObserver](https://blog.logrocket.com/lazy-loading-using-the-intersection-observer-api/)). For heavy pieces, a *facade* (static screenshot + "run" button that injects the iframe on click) is the strongest version — zero cost until the visitor opts in.
2. **Pause when offscreen.** Lazy load only helps before first view. Once loaded, a piece with a `requestAnimationFrame` loop burns main-thread time forever. Use one `IntersectionObserver` in the host to notify pieces when they leave/enter the viewport (same-origin iframes: call a function on `iframe.contentWindow`, or `postMessage`), and have each piece stop its rAF loop while hidden. Browsers throttle timers in offscreen iframes, but rAF-driven canvas work should be paused explicitly.

Applies identically to inline mounting (observe the host element, pause the loop).

## Accessibility

- **Iframes:** every `<iframe>` needs a descriptive `title` — without it screen readers announce "frame" or the URL ([WebAIM: frames](https://webaim.org/techniques/frames/), [Deque: iframe titles](https://dequeuniversity.com/tips/provide-iframe-titles)). Keyboard users tab into and out of same-origin iframes natively; don't set `tabindex="-1"` on frames with focusable content ([Yale usability: iframes](https://usability.yale.edu/digital-accessibility/accessibility-resources/accessibility-articles/internal-frames)). The frame boundary is otherwise a *benefit*: each demo is announced as its own document with its own heading structure.
- **Inline/shadow DOM:** focus order and AT traversal work naturally (it's one document), but ids, `aria-labelledby` references, and form associations cannot cross shadow boundaries — a known papercut ([Matuzovic](https://www.matuzo.at/blog/2023/pros-and-cons-of-shadow-dom/)).
- **Either way:** each interactive demo needs a text alternative or caption saying what it is and how to operate it, and canvas-based pieces need keyboard equivalents or an explicit "this is a pointer toy" framing.

## prefers-reduced-motion

The media query is evaluated per document against the same OS setting, so it works identically *inside* each iframe — each piece should self-police:

- CSS animation/transition: gate with `@media (prefers-reduced-motion: reduce)` ([MDN: prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion), [W3C technique C39](https://www.w3.org/WAI/WCAG21/Techniques/css/C39)).
- JS/canvas loops: check `matchMedia('(prefers-reduced-motion: reduce)')` and listen for changes; render a static first frame instead of animating ([Smashing: Respecting motion preferences](https://www.smashingmagazine.com/2021/10/respecting-users-motion-preferences/)).
- Independent of the media query, anything that auto-animates for more than 5 seconds needs a visible pause control per WCAG 2.2.2 Pause, Stop, Hide. A shared "each piece starts paused with a play affordance, or auto-plays only while in view and honors reduced motion" convention satisfies both.

## Mobile touch / scroll capture

Interactive canvases that listen to `touchmove` will trap page scrolling if they `preventDefault()` — and Chrome requires `{ passive: false }` for that to even work ([MDN: Touch events](https://developer.mozilla.org/en-US/docs/Web/API/Touch_events)). Rules for pieces:

- Declare intent with CSS `touch-action` on the interactive surface: `touch-action: none` only for surfaces that genuinely own the gesture (drawing, dragging); `touch-action: pan-y` to allow vertical scroll through a horizontally-interactive piece ([Kirk: prevent scrolling while drawing on canvas](https://kirkdev.blogspot.com/2020/10/prevent-browser-scrolling-while-drawing.html)).
- A full-width piece with `touch-action: none` creates a scroll trap on phones — the visitor can't scroll past it. Keep pointer-hungry pieces narrower than the viewport, or require a tap-to-activate step before capturing gestures (the facade pattern does this for free).
- Iframes add no special touch problem when same-origin; scrolling gestures pass through non-capturing content normally.

## Comparison summary

- CSS isolation: iframe total; shadow DOM strong but inheritable/custom properties pierce; plain scoped scripts weakest.
- JS isolation: iframe total; inline none (shared window) — convention-dependent.
- Per-piece authoring freedom: iframe total (any full-page HTML works as-is); inline requires every piece to follow a component convention.
- Overhead at 5–10 pieces: inline lowest; same-origin lazy iframes low and fine; cross-origin iframes would be the expensive case and doesn't apply here.
- Sizing: inline natural; iframe needs fixed `aspect-ratio` boxes (acceptable, prevents CLS) or postMessage resizing (avoid).
- Accessibility: both workable; iframe needs `title` per frame; shadow DOM has cross-boundary ARIA papercuts.
- Standalone URLs per piece: iframe keeps them for free; inline loses them unless each piece is double-packaged.

## Recommendation for this site

**Same-origin `<iframe>` per piece, lazily loaded, with a small shared behavior contract.** Concretely:

1. Keep each piece as a standalone `agents/<name>/index.html` (already the layout). Each stays independently linkable and agent sessions can build them with zero knowledge of the host page.
2. Embed with `<iframe src="agents/<name>/" loading="lazy" title="<what it is>">` inside a container with a fixed `aspect-ratio` (no CLS, no resize plumbing).
3. Host page runs one `IntersectionObserver`; on exit it calls a conventional `contentWindow.piecePause?.()` (or `postMessage`) so pieces stop rAF loops offscreen. For the heaviest pieces, use a screenshot facade with a "run" button instead of `loading="lazy"`.
4. Per-piece contract (a short checklist in `docs/agents/`): honor `prefers-reduced-motion` (static first frame when reduced), expose `piecePause`/`pieceResume`, set `touch-action` deliberately and never full-viewport-width `touch-action: none`, keep an accessible name/caption, provide a pause control for anything auto-animating >5 s.

Why not inline shadow-DOM mounting: it's cheaper per piece at runtime, but at 5–10 lazy same-origin frames the runtime difference is negligible, while inline mounting would cost a rewrite of every existing piece, impose a permanent authoring convention on future agent sessions, forfeit hard JS isolation between independently-authored demos, and lose the free standalone URL per piece. Revisit only if the count grows well past ~10 simultaneously-visible pieces or a piece must integrate tightly with host-page state.

## Sources

- https://web.dev/articles/iframe-lazy-loading
- https://webperf.tips/tip/iframe-multi-process/
- https://www.stevesouders.com/blog/2009/06/03/using-iframes-sparingly/
- https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_shadow_DOM
- https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scoping
- https://web.dev/articles/shadowdom-201
- https://www.matuzo.at/blog/2023/pros-and-cons-of-shadow-dom/
- https://medium.com/bbc-product-technology/goodbye-iframes-6c84a651e137
- https://dp-lewis.medium.com/iframes-vs-web-components-which-one-actually-performs-better-in-2025-4db95784eb9f
- https://webaim.org/techniques/frames/
- https://dequeuniversity.com/tips/provide-iframe-titles
- https://usability.yale.edu/digital-accessibility/accessibility-resources/accessibility-articles/internal-frames
- https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion
- https://www.w3.org/WAI/WCAG21/Techniques/css/C39
- https://www.smashingmagazine.com/2021/10/respecting-users-motion-preferences/
- https://developer.mozilla.org/en-US/docs/Web/API/Touch_events
- https://kirkdev.blogspot.com/2020/10/prevent-browser-scrolling-while-drawing.html
- https://blog.logrocket.com/lazy-loading-using-the-intersection-observer-api/
