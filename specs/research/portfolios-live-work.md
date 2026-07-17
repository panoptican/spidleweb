# Research: how portfolios present live/interactive work

Resolves [issue #7](https://github.com/panoptican/spidleweb/issues/7). Surveyed 2026-07-16 via live fetches of each site (what they actually do today, not reputation).

## Examples surveyed

### Emil Kowalski — https://emilkowal.ski/
- Landing is deliberately plain: short conversational intro ("thinking deeply about how the UI looks, feels, behaves"), then flat lists — Projects (Sonner, Vaul, animations.dev, index.how), Writing, Newsletter. **No demos on the index at all.**
- The interactivity lives in the writing. Articles like "Building a Toast Component" alternate prose with inline working components: a real "Add toast" button that fires the actual component, annotated overlays (dark bars showing where pseudo-elements fill hover gaps), short videos only where interaction can't be embedded (swipe momentum).
- The pattern: *explain a decision, then let the reader feel it immediately*. Demos validate the prose one concept at a time — never a wall of demos.

### Rauno Freiberg — https://rauno.me/ and /craft
- Landing leads with a values statement ("Make it fast. Make it beautiful… Make it.") before any work — philosophy-first framing.
- `/craft` is the influential piece: a reverse-chronological index of small interaction experiments. Each entry is just **title + date + a motion thumbnail**, with occasional "View prototype/production" links. Almost no explanatory text; density and consistency do the talking.
- His "Devouring Details" (https://devouringdetails.com/, with Vercel) goes further: content is organized as Principles / Prototypes / Resources, everything built around live React prototypes with downloadable source, in a two-column scrollable layout "that doesn't ask for too much at once."

### Paco Coursey — https://paco.me/
- Minimal text index: Building / Projects / Writing / Now. Projects (⌘K, next-themes) link out to GitHub rather than embedding demos. Has a separate "Craft" section framing implementation as its own practice.
- Takeaway: even in this circle, some let the shipped open-source *be* the demo and keep the site itself quiet. Works when your repos have millions of downloads; weaker when a visitor won't recognize the names.

### Josh W. Comeau — https://www.joshwcomeau.com/
- Landing is a curated content index with explicit "Interactive Guide" labeling in titles ("An Interactive Guide to Flexbox"). Interactivity is a **promise made in the title**, so the index itself stays static and skimmable.
- Inside articles: embedded playgrounds and manipulable visualizations are the pedagogy — show, then let the reader poke it. Enthusiastic, personable voice keeps heavy interactivity feeling friendly rather than showy.

### Nanda Syahrasyad — https://www.nan.fyi/
- Self-described "interactive blog." Index is a card grid (thumbnail, title, date, one-line description) where descriptions foreground interactivity ("An interactive look at a classic array algorithm"). The thumbnails hint at the animated content inside.

### Amelia Wattenberger — https://wattenberger.com/
- Essay-first, intellectual-positioning site; current version is openly WIP and links out (Twitter, GitHub Next) more than it embeds. Her famous scrollytelling essays live in individual pieces, not the index. Demonstrates that a scattered index undermines even excellent interactive work — visitors seeking specifics get lost.

### Bruno Simon — https://bruno-simon.com/ (counter-example)
- The 3D drive-a-car portfolio. Memorable, technically impressive, widely shared — and **poor for a two-minute skimmer**: you must learn controls and explore a world to find the work; no fallback resume/projects view; accessibility and server-dependency problems. The canonical "experience as portfolio" gimmick: great as a stunt, risky as a primary hiring artifact.

## Patterns (what makes it legible)

1. **Quiet index, loud interiors.** The strongest sites (Emil, Rauno, Josh) keep the landing page fast, text-first, and scannable, and put the live work one click deep. The index's job is routing and credibility, not spectacle.
2. **Demo as evidence, not decoration.** Inline demos appear immediately after the prose that explains the decision they demonstrate. One concept → one demo → next concept. The demo proves a claim ("notice how toasts jump into place").
3. **Label the interactivity.** "Interactive guide," "Prototype," "Try it" — the promise of interactivity is made in plain text before the reader arrives, so skimmers know clicking is rewarded.
4. **Craft-index pattern (title + date + motion thumbnail).** For a volume of small experiments, a dense chronological grid with minimal copy reads as prolific and confident. Thumbnails must show motion/result, not logos.
5. **Real components, not simulations.** Emil's "Add toast" fires the actual shipped component. The credibility comes from "this is the real thing running," which is exactly the live-clickable-code differentiator.
6. **Bounded demos with reset/replay.** Good demos are small, sandboxed, obviously interactive (a visible button/handle), and recoverable — you can't break the page with them.
7. **Video only where embedding fails** (device gestures, momentum) — and framed as a fallback, not the default.
8. **Annotated internals as a flex.** Overlays showing hit areas, pseudo-elements, or timing curves communicate engineering depth to expert reviewers without extra words.

## Anti-patterns (what reads as gimmicky)

- **Experience-as-navigation** (Bruno Simon): making the visitor play a game to find the work. High friction for the exact audience (hiring managers) with the least time.
- **Landing-page spectacle with no routing:** heavy WebGL/scroll-jacking heroes that delay the answer to "who is this and what have they done?"
- **Unlabeled interactivity:** demos that look like static images, so skimmers never discover them. Interactivity that isn't signposted doesn't exist for a two-minute visitor.
- **Demo walls:** many demos with no prose framing — impressive for 10 seconds, then illegible. The prose-demo alternation is what converts "neat" into "this person thinks clearly."
- **Everything external:** indexes that only link to GitHub/Twitter (Paco, current Wattenberger) push the proof off-site; works only with pre-existing fame.
- **WIP/scattered index:** stream-of-consciousness landing pages bury the work.
- **Fragile demos:** server-dependent or breakable embeds ("Server currently offline") actively damage the craft claim.

## Implications for spidleweb

Audience: hiring managers/clients skimming for two minutes; differentiator: designs shown as live clickable code.

1. Keep the index restrained and fast — plain typography, short claim of what Jason does, then a scannable list of pieces. Signal interactivity in the item copy/thumbnail ("live demo," motion thumbnails), don't perform it on the index.
2. Structure each case study as prose-demo alternation: state the design decision, then embed the real working component right below it, with a visible affordance (button, drag handle) and a reset. Two or three demos per piece beats ten.
3. Make "this is real code running" explicit — a small "view source" or "built with X, source here" affordance per demo turns the differentiator into a verifiable claim.
4. Adopt a light craft-index for small experiments (title + date + motion thumbnail) if there's volume; it conveys prolific range at a glance.
5. Reserve video for gesture/device-bound interactions only.
6. Hard rule from the counter-examples: nothing between the visitor and the work — no intro animations, no exploration mechanics, no scroll-jacking. The two-minute skimmer must reach a working demo in ≤2 clicks.

## Sources

- https://emilkowal.ski/ and https://emilkowal.ski/ui/building-a-toast-component
- https://rauno.me/ and https://rauno.me/craft
- https://devouringdetails.com/
- https://paco.me/
- https://www.joshwcomeau.com/
- https://www.nan.fyi/
- https://wattenberger.com/
- https://bruno-simon.com/
- https://ui.land/interviews/rauno-freiberg
