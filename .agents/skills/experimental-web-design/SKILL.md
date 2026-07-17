---
name: experimental-web-design
description: Produce genuinely unconventional web design — layouts and interactions outside converged best practices. Use when the user asks for experimental, weird, avant-garde, controversial, or "alive" design work, or invokes this skill by name. Not for client work with usability mandates unless the user says otherwise.
---

# Experimental Web Design

## What this skill is for

The goal is design that could not have been produced by someone optimizing for "clean and professional." The output should feel authored, opinionated, and slightly uncomfortable — the kind of work where at least one decision is defensible but controversial. "Nice" is a failure state under this skill.

Two attractors will pull you off course, and both are banned:

1. **Converged tasteful web design.** The default distribution: hero sections, symmetric column grids, card components, centered max-width containers, uniform rounded corners, fade-in-on-scroll, generous-whitespace minimalism. If a competent designer would describe the result as clean, it failed.
2. **Brutalism pastiche.** The stock "experimental" costume: system-default styling worn as an aesthetic, harsh borders as decoration, deliberately-broken affect with nothing underneath. This is a genre with its own templates now. Imitating it is exactly as derivative as imitating a SaaS landing page.

Banning both matters because when pushed away from the first attractor, models reliably land on the second. Go somewhere else.

## Process: concept before code

**1. State the conceit.** Before any layout or code, write one sentence naming the organizing metaphor. Examples of the *form* (do not reuse these): "the page is a specimen drawer," "the index is a seismograph of the author's output," "navigation is an excavation — content is buried and the reader digs." Every significant design decision must be derivable from the conceit. If you cannot trace a decision back to it, the decision is arbitrary and should be cut or changed.

**2. Generate divergent conceits when exploring.** If the task calls for multiple directions, write the conceits first — one line each — and check them against each other. Two conceits that would produce similar pages are one conceit. Push apart at the level of idea, not skin.

**3. Choose the liveness moves.** Pick two or three techniques from the menu below (or invent equivalents), chosen because the conceit demands them — not because they demo well. More than three reads as a tech showcase; the conceit drowns.

**4. Build, then run the gate.** Before presenting, run the evaluation gate at the bottom. Revise until it passes. Do not present work that fails the gate with a caveat; fix it.

## The liveness menu

"Alive" means the page responds to the reader's presence, body, and time — it is not an animation checklist. Techniques, roughly grouped:

**Responds to the body.**
- Cursor-proximity behavior: elements lean toward, flee from, or deform near the pointer. Attraction and repulsion read as temperament.
- Variable font axes driven by input — scroll velocity, pointer position, dwell time. Type that breathes rather than sits.
- Scroll as a physical act: resistance, momentum, overshoot; scroll direction or speed changing what is revealed, not just when.

**Has physics.**
- Spring, inertia, gravity, and collision on layout elements. Things settle rather than snap.
- Draggable, throwable, stackable content. The reader can make a mess; the page remembers or repairs it.

**Distorts and dissolves.**
- Shader or displacement effects on imagery — refraction, melt, feedback — tied to interaction rather than looping ambiently.
- Text as texture: type that fills, wraps, floods, or erodes as material, while a readable channel remains available.

**Aware of time and history.**
- Elements that decay, accumulate, or migrate with time-on-page. A page you leave open should differ from one you just arrived at.
- Return-visit memory: the page changes because you have been here before.
- Layout derived from a live or seeded data source (date, weather, the author's actual output cadence) so no two renders are identical.

**Structural transgressions.**
- Spatial navigation instead of lists: a map, a field, a pile, a depth axis.
- Overlap and occlusion as a system — content that must be moved to be read.
- Orientation, edge, and viewport misuse: content that enters from the wrong edge, exceeds the frame deliberately, rotates the reading axis.

## Reference traditions

Sample from regions of design-space by name, without imitating any single one: net.art and JODI-era interface subversion, hypertext literature, the demoscene, digital gardens and HTML Energy handmade-web, Are.na practice, experimental typography in the Bauhaus and post-punk print lineages, generative and procedural layout. These are retrieval anchors, not skins. If the output would be recognized as "in the style of" one of them, push further.

## The floor: it must still work

One countervailing rule, non-negotiable unless the user waives it: the core content must remain reachable within a few intuitive actions, and a reduced-motion / assistive path must exist. Weirdness lives in how the reader gets there and what the journey feels like — not in whether they can arrive. `prefers-reduced-motion` gets a real fallback, not a blank page.

## Evaluation gate

Answer honestly before presenting:

1. Can every major decision be traced to the conceit? Untraceable decisions are noise — cut or justify.
2. Would a competent designer call this "nice" or "clean"? If yes, it failed. Revise toward the uncomfortable decision you talked yourself out of.
3. Is this recognizably brutalism pastiche or any other off-the-shelf "weird" genre? If yes, the conceit was too weak to generate its own form. Return to step 1.
4. Does at least one moment respond to the reader — body, time, or history — in a way a screenshot cannot capture?
5. Can the reader still reach the actual content? If no, restore the floor.

If the work passes 1–5 and you feel slightly unsure whether the user will like it, that is the correct feeling. Present it with a one-paragraph account of the conceit and the controversial decision, not an apology.

## Working notes

Update this skill as you learn. When a technique consistently lands or a new cliché emerges as an attractor, record it here — one line each — so future runs start smarter.