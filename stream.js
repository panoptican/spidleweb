/*
  Open in place: Phase 2B of specs/redesign.md.

  Every stream card is a plain link, so without this script a card goes to
  its canonical page (the card contract). With it, clicking a card opens the
  item in a panel under that card's row, and the masthead's About link opens
  the About section the same way.

  - What a panel shows comes from the #stream-data JSON island that
    scripts/build-stream.mjs writes into the page.
  - One thing is open at a time: an item's panel, or About.
  - The panel stays where it opened. Its thumbnails, arrows, and the Left and
    Right keys change what it shows, never where it sits.
  - The soft rise sits under the centre of the card that opened the panel.
  - Opening sets #<item-id> with history.replaceState, and closing clears it.
    Only a phone's full-screen prototype adds a history step, so that the
    back gesture closes it.
  - A page loaded with #<item-id> asks the stream to reveal that item with a
    `stream:reveal` event, then opens it.

  Values come from Paper, file "Portfolio v3", page "current · redesign",
  rows 01 and 03 to 10. panel.css holds the styles.
*/
(() => {
  'use strict';

  // ---- Settings ------------------------------------------------------------

  /** Phones get the single-column panel, 16px gutters, and full-screen prototypes. */
  const PHONE = '(max-width: 599px)';
  /** Paper's row 03 note: the band grows down from the rise over 240ms. */
  const OPEN_MS = 240;
  /** Closing is quicker than opening. An estimate; no board gives it. */
  const CLOSE_MS = 180;
  const EASE_OUT = 'cubic-bezier(0.16, 1, 0.3, 1)';
  const EASE_IN = 'cubic-bezier(0.4, 0, 1, 1)';
  /** A phone capture is narrower than this ratio of width to height. */
  const PHONE_RATIO = 0.7;
  /** How long to wait for a demo to answer before treating it as missing. */
  const DEMO_TIMEOUT_MS = 2500;

  const CARD = '.stream-card, .stream-row';
  const ABOUT_LINKS = 'a[href="#about"], [aria-controls="about"]';

  const media = (query) => window.matchMedia(query);
  const isPhone = () => media(PHONE).matches;
  const reducedMotion = () => media('(prefers-reduced-motion: reduce)').matches;

  // ---- The island ----------------------------------------------------------

  let island;
  /** The page's stream data, read once. Pages without it still get About. */
  function streamData() {
    if (island === undefined) {
      island = { items: {}, caseStudies: {} };
      const node = document.getElementById('stream-data');
      if (node) {
        try {
          const parsed = JSON.parse(node.textContent);
          island = { items: parsed.items || {}, caseStudies: parsed.caseStudies || {} };
          // Records are keyed by id. Views need the id on the record too.
          for (const [id, item] of Object.entries(island.items)) item.id = id;
        } catch {
          // A broken island leaves every card a plain link.
        }
      }
    }
    return island;
  }
  const itemById = (id) => (id && Object.hasOwn(streamData().items, id) ? streamData().items[id] : null);
  const studyFor = (item) => (item?.caseStudy ? streamData().caseStudies[item.caseStudy.slug] || null : null);

  // ---- Small helpers -------------------------------------------------------

  const ENTITIES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ENTITIES[c]);
  const pad = (n) => String(n).padStart(2, '0');
  const clamp = (n, low, high) => Math.min(high, Math.max(low, n));
  const round = (n) => Math.round(n * 10) / 10;

  /** "2026-09" reads "September 2026". */
  function monthYear(shared) {
    const [year, month] = String(shared || '').split('-').map(Number);
    if (!year || !month) return '';
    return new Date(Date.UTC(year, month - 1, 1)).toLocaleString('en-US', { month: 'long', year: 'numeric', timeZone: 'UTC' });
  }
  const yearOf = (shared) => String(shared || '').slice(0, 4);

  /** Hidden cards (a later page of the stream, or filtered out) have no box. */
  const isRendered = (el) => el.getClientRects().length > 0;

  function shapeOf(m) {
    if (!m || !m.width || !m.height) return 'wide';
    return m.width / m.height < PHONE_RATIO ? 'phone' : 'wide';
  }

  function rowGap(container) {
    const gap = parseFloat(getComputedStyle(container).rowGap);
    return Number.isFinite(gap) ? gap : 0;
  }

  function setHash(id) {
    history.replaceState(history.state, '', `${location.pathname}${location.search}#${encodeURIComponent(id)}`);
  }
  function clearHash() {
    if (location.hash) history.replaceState(history.state, '', `${location.pathname}${location.search}`);
  }

  function setExpanded(control, open, controls) {
    if (!control) return;
    control.setAttribute('aria-expanded', String(open));
    if (controls) control.setAttribute('aria-controls', controls);
  }

  // ---- The soft rise -------------------------------------------------------
  //
  // A panel's top edge is a straight diagonal across the full width, with an
  // 80px rise over the card that opened it. On a 1440 board the diagonal
  // climbs 32px from left to right in a 56px box. On a 390 board it climbs
  // 16px in a 48px box. The rise stands 18px above the line, and its curves
  // leave the line 22px either side of the centre and flatten 16px either
  // side of it, which is Paper's path:
  //   M0 48 L128 45.2 C146 44.9 152 26.3 168 26.3 C184 26.3 190 43.7 208 43.4 L1440 16
  // Near an edge, as under About, the rise runs off the screen rather than
  // leave its anchor.

  function riseMetrics(width) {
    const drop = clamp(width * (32 / 1440), 16, 32);
    const height = Math.max(48, Math.round(drop + 24));
    return { drop, height };
  }

  function risePath(width, x, filled) {
    const { drop, height } = riseMetrics(width);
    const base = height - 8;
    const lineAt = (at) => base - drop * (at / width);
    const parts = [];
    if (x == null) {
      parts.push(`M0 ${round(lineAt(0))} L${width} ${round(lineAt(width))}`);
    } else {
      const peak = Math.max(1, lineAt(x) - 18);
      const left = x - 40;
      const right = x + 40;
      const start = Math.min(0, left);
      const end = Math.max(width, right);
      const point = (at) => `${round(at)} ${round(lineAt(at))}`;
      parts.push(
        `M${point(start)}`,
        `L${point(left)}`,
        `C${point(x - 22)} ${round(x - 16)} ${round(peak)} ${round(x)} ${round(peak)}`,
        `C${round(x + 16)} ${round(peak)} ${point(x + 22)} ${point(right)}`,
        `L${point(end)}`,
      );
    }
    if (filled) {
      const start = x == null ? 0 : Math.min(0, x - 40);
      const end = x == null ? width : Math.max(width, x + 40);
      parts.push(`L${round(end)} ${height} L${round(start)} ${height} Z`);
    }
    return { d: parts.join(' '), height };
  }

  function drawRise(svg, x, filled) {
    const width = Math.round(svg.getBoundingClientRect().width) || document.documentElement.clientWidth;
    const { d, height } = risePath(width, x, filled);
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    svg.style.height = `${height}px`;
    svg.firstElementChild.setAttribute('d', d);
    svg.dataset.width = String(width);
  }

  /** The centre of an element, measured from the left edge of the viewport. */
  function centreOf(el) {
    if (!el || !isRendered(el)) return null;
    const rect = el.getBoundingClientRect();
    return rect.left + rect.width / 2;
  }

  /**
   * Stretches `el` from its parent's content box to both edges of the
   * viewport. The insets are custom properties, so the width still follows
   * the parent when a scrollbar comes or goes.
   */
  function bleed(el) {
    const parent = el.parentElement;
    if (!parent) return;
    const style = getComputedStyle(parent);
    const rect = parent.getBoundingClientRect();
    const left = rect.left + parseFloat(style.borderLeftWidth) + parseFloat(style.paddingLeft);
    const right = document.documentElement.clientWidth -
      (rect.right - parseFloat(style.borderRightWidth) - parseFloat(style.paddingRight));
    el.style.setProperty('--stream-bleed-start', `${Math.max(0, left)}px`);
    el.style.setProperty('--stream-bleed-end', `${Math.max(0, Math.floor(right))}px`);
  }

  // ---- Rows ----------------------------------------------------------------
  //
  // The column count differs between Grid, List, and phones, so a row is read
  // from layout: items in one row share a top edge. The panel goes after the
  // last item of the opener's row.

  function rowEnd(card, skip) {
    const top = card.getBoundingClientRect().top;
    let end = card;
    for (let next = card.nextElementSibling; next; next = next.nextElementSibling) {
      if (next === skip || next.classList.contains('stream-panel') || !isRendered(next)) continue;
      if (Math.abs(next.getBoundingClientRect().top - top) > 2) break;
      end = next;
    }
    return end;
  }

  /**
   * An open panel starts a row of its own, so after a reflow it can split the
   * row it sits in. Rows are measured with it set aside. The container keeps
   * its height meanwhile, so the page cannot shorten and clamp the scroll.
   * Setting the panel aside resets the scroll of anything inside it, such as
   * the strip, so those offsets are put back.
   */
  function measureRowEnd(card, panel) {
    const container = card.parentElement;
    if (!panel || panel.parentElement !== container) return rowEnd(card, panel);
    const scrolled = [...panel.querySelectorAll('*')]
      .filter((el) => el.scrollLeft || el.scrollTop)
      .map((el) => [el, el.scrollLeft, el.scrollTop]);
    const keep = container.style.minHeight;
    container.style.minHeight = `${container.getBoundingClientRect().height}px`;
    panel.style.display = 'none';
    const end = rowEnd(card, panel);
    panel.style.display = '';
    container.style.minHeight = keep;
    for (const [el, left, top] of scrolled) {
      el.scrollLeft = left;
      el.scrollTop = top;
    }
    return end;
  }

  // ---- Motion --------------------------------------------------------------

  /**
   * Grows an element from nothing to its height while the content below makes
   * room. `from` holds the margins that make the element take no space at the
   * start, so nothing below jumps.
   */
  /** The element's settled box, as keyframe values. */
  function box(el) {
    const style = getComputedStyle(el);
    return {
      height: style.height,
      paddingTop: style.paddingTop,
      paddingBottom: style.paddingBottom,
      marginTop: style.marginTop,
      marginBottom: style.marginBottom,
    };
  }

  function collapsed(settled, margins) {
    return {
      height: '0px',
      paddingTop: '0px',
      paddingBottom: '0px',
      marginTop: margins.marginTop ?? settled.marginTop,
      marginBottom: margins.marginBottom ?? settled.marginBottom,
    };
  }

  function grow(el, margins = {}) {
    if (reducedMotion()) return Promise.resolve();
    const settled = box(el);
    el.classList.add('is-moving');
    const animation = el.animate([collapsed(settled, margins), settled], { duration: OPEN_MS, easing: EASE_OUT });
    return animation.finished.catch(() => {}).then(() => el.classList.remove('is-moving'));
  }

  function shrink(el, margins = {}) {
    if (reducedMotion()) return Promise.resolve();
    const settled = box(el);
    el.classList.add('is-moving');
    return el.animate([settled, collapsed(settled, margins)], { duration: CLOSE_MS, easing: EASE_IN, fill: 'forwards' })
      .finished.catch(() => {});
  }

  function scrollByY(delta, smooth) {
    if (Math.abs(delta) < 1) return;
    window.scrollBy({ top: delta, behavior: smooth && !reducedMotion() ? 'smooth' : 'instant' });
  }

  // ---- Markup --------------------------------------------------------------

  function picture(m, { sizes, eager = false, alt } = {}) {
    if (!m || !m.src) return '';
    const source = m.avif ? `<source type="image/avif" srcset="${esc(m.avif)}" sizes="${esc(sizes)}">` : '';
    const size = m.width && m.height ? ` width="${m.width}" height="${m.height}"` : '';
    return `<picture>${source}<img src="${esc(m.src)}"${size} alt="${esc(alt ?? m.alt ?? '')}" loading="${eager ? 'eager' : 'lazy'}" decoding="async" draggable="false"></picture>`;
  }

  function head(kicker) {
    return `<div class="stream-panel__head">
      ${kicker ? `<p class="stream-panel__kicker micro">${esc(kicker)}</p>` : '<span></span>'}
      <button type="button" class="stream-panel__close stream-panel__close--head micro" data-panel-close aria-keyshortcuts="Escape">Close<span aria-hidden="true">✕</span></button>
    </div>`;
  }

  function title(level, label, extra = '') {
    return `<h${level} class="stream-panel__title${extra}" id="stream-panel-title" tabindex="-1" data-focus-key="title">${esc(label)}</h${level}>`;
  }

  function lede(textValue, kind = 'lede') {
    return textValue ? `<p class="stream-panel__${kind}">${esc(textValue)}</p>` : '';
  }

  /** Rows of [label, value] or [label, value, html], skipping empty values. */
  function facts(rows) {
    const kept = rows.filter((row) => row[1] || row[2]);
    if (!kept.length) return '';
    return `<dl class="stream-panel__facts">${kept.map(([label, value, html]) =>
      `<div><dt class="micro">${esc(label)}</dt><dd class="micro">${html || esc(value)}</dd></div>`).join('')}</dl>`;
  }

  /** The arrow follows the site rule: ↓ opens here, → goes to a page, ↗ leaves the site. */
  function cta(href, label, arrow) {
    if (!href) return '';
    return `<a class="stream-panel__cta micro" href="${esc(href)}"><span>${esc(label)}</span><span class="stream-panel__cta-arrow" aria-hidden="true">${arrow}</span></a>`;
  }

  function closer(links = '') {
    return `<div class="stream-panel__closer"${links ? ' data-links' : ''}>${links}
      <span class="stream-panel__close-group">
        <button type="button" class="stream-panel__close micro" data-panel-close aria-keyshortcuts="Escape" data-focus-key="close">Close<span aria-hidden="true"> ✕</span></button>
        <kbd class="stream-panel__key micro" aria-hidden="true">esc</kbd>
      </span>
    </div>`;
  }

  /** aria-disabled rather than disabled, so a focused arrow keeps focus at the end. */
  function arrows(noun, { first = false, last = false } = {}) {
    return `<span class="stream-panel__arrows">
      <button type="button" class="stream-panel__arrow" data-step="-1" data-focus-key="prev" aria-label="Previous ${noun}" aria-disabled="${first}"><span aria-hidden="true">←</span></button>
      <button type="button" class="stream-panel__arrow" data-step="1" data-focus-key="next" aria-label="Next ${noun}" aria-disabled="${last}"><span aria-hidden="true">→</span></button>
    </span>`;
  }

  /** A button that shows another item in this panel, labelled with ↓. */
  function jump(target, label) {
    if (!target) return '';
    return `<a class="stream-panel__jump" href="${esc(target.href)}" data-show="${esc(target.id)}" data-focus-key="jump-${esc(target.id)}">${esc(label)} <span aria-hidden="true">↓</span></a>`;
  }

  // ---- Related items -------------------------------------------------------

  /** The item followed by the related items this page's island knows about. */
  function relatedSet(item) {
    const ids = [item.id, ...(item.related || []).filter((id) => id !== item.id && itemById(id))];
    return ids.length > 1 ? { ids, index: 0, project: item.project } : null;
  }

  function relatedThumb(id, current) {
    const item = itemById(id);
    const m = item.media;
    const shape = shapeOf(m);
    const image = m?.src
      ? picture(m, { sizes: '120px', alt: '' })
      : m?.tile
        ? `<span class="stream-related__tile" aria-hidden="true">${esc(item.title)}</span>`
        : '<span class="stream-related__empty"></span>';
    // Phones drop Try it from a web prototype, which they do not run.
    const tryable = item.type === 'prototype' && (item.platform === 'Mobile' || !isPhone());
    const badge = tryable ? '<span class="stream-related__badge micro" aria-hidden="true"><span>▶</span> Try it</span>' : '';
    return `<li><button type="button" class="stream-related__item" data-show="${esc(id)}" data-focus-key="show-${esc(id)}"${current ? ' aria-current="true"' : ''}>
      <span class="stream-related__thumb" data-shape="${shape}">${image}${badge}</span>
      <span class="stream-related__name">${esc(item.title)}</span>
    </button></li>`;
  }

  function relatedBlock(related, level) {
    if (!related) return '';
    const n = related.ids.length;
    return `<section class="stream-related" aria-labelledby="stream-related-title">
      <div class="stream-related__head">
        <h${level + 1} class="stream-related__title micro" id="stream-related-title">Related · ${esc(related.project)}</h${level + 1}>
        <p class="stream-related__count micro">${related.index + 1} of ${n}</p>
      </div>
      <ul class="stream-related__list">${related.ids.map((id, i) => relatedThumb(id, i === related.index)).join('')}</ul>
      <div class="stream-related__keys">${arrows('item', { first: related.index === 0, last: related.index === n - 1 })}<span class="micro" aria-hidden="true">Step through</span></div>
    </section>`;
  }

  function steps(item, level) {
    if (!item.steps?.length) return '';
    return `<section class="stream-steps" aria-labelledby="stream-steps-title">
      <h${level + 1} class="stream-steps__title micro" id="stream-steps-title">Things to try</h${level + 1}>
      <ul class="stream-steps__list">${item.steps.map((step) => `<li>${esc(step)}</li>`).join('')}</ul>
    </section>`;
  }

  // ---- The case-study strip ------------------------------------------------

  /** One frame per figure on the case study's page, in page order. */
  function figureFrame(figure) {
    const label = figure.group ? `<span class="stream-strip__label micro">${figure.caption}</span> ` : '';
    return {
      media: figure,
      shape: shapeOf(figure),
      // Captions are HTML from the case-study page, since Plinth's carry links.
      caption: figure.group ? `${label}${figure.group}` : figure.caption,
    };
  }

  /** A case-study item that is not a figure on its page leads its own strip. */
  function leadFrame(item) {
    if (item.type === 'video') return { video: item, shape: 'wide', caption: esc(item.note || item.title) };
    return { media: item.media, shape: shapeOf(item.media), caption: esc(item.note || item.title) };
  }

  function frameMarkup(frame, index, start) {
    const eager = Math.abs(index - start) < 2;
    let inner;
    if (frame.video) inner = player(frame.video, { eager });
    else if (frame.media?.src) {
      inner = picture(frame.media, {
        eager,
        sizes: frame.shape === 'phone' ? '(max-width: 599px) 110px, 200px' : '(max-width: 599px) 320px, 640px',
      });
    } else inner = '<span class="stream-strip__empty"></span>';
    const ratio = frame.shape === 'wide' && frame.media?.width ? ` style="aspect-ratio: ${frame.media.width} / ${frame.media.height}"` : '';
    return `<div class="stream-strip__frame" data-shape="${frame.shape}" data-index="${index}"${ratio}>${inner}</div>`;
  }

  function strip(frames, start, label) {
    return `<div class="stream-panel__media stream-strip" data-strip>
      <div class="stream-strip__track" data-strip-track role="group" aria-label="${esc(label)}">${frames.map((f, i) => frameMarkup(f, i, start)).join('')}</div>
      <div class="stream-strip__caption">
        <span class="stream-strip__number micro" data-strip-number aria-hidden="true"></span>
        <p class="stream-strip__text" data-strip-caption></p>
      </div>
      <div class="stream-strip__controls">
        <p class="stream-strip__count micro" data-strip-count aria-live="polite"></p>
        <span class="stream-strip__ticks" aria-hidden="true">${frames.map(() => '<span></span>').join('')}</span>
        ${arrows('screen')}
      </div>
    </div>`;
  }

  /**
   * Keeps a strip's current frame, caption, count, and ticks in step. The
   * track is a native scroller with snap points, so a swipe or a trackpad
   * moves it too. The frame that settles at the left edge becomes current.
   */
  function stripController(root, frames, start) {
    const track = root.querySelector('[data-strip-track]');
    const frameEls = [...track.children];
    const number = root.querySelector('[data-strip-number]');
    const caption = root.querySelector('[data-strip-caption]');
    const count = root.querySelector('[data-strip-count]');
    const ticks = [...root.querySelectorAll('.stream-strip__ticks > span')];
    const [prev, next] = root.querySelectorAll('[data-step]');
    const total = frames.length;
    let index = -1;
    let settle = 0;

    const padStart = () => parseFloat(getComputedStyle(track).paddingInlineStart) || 0;
    const offsetFor = (i) => frameEls[i].offsetLeft - padStart();

    function show(i) {
      i = clamp(i, 0, total - 1);
      if (i === index) return;
      index = i;
      number.textContent = pad(i + 1);
      caption.innerHTML = frames[i].caption || '';
      count.innerHTML = `<span aria-hidden="true">${pad(i + 1)} / ${pad(total)}</span><span class="visually-hidden">Screen ${i + 1} of ${total}</span>`;
      ticks.forEach((tick, t) => tick.toggleAttribute('data-current', t === i));
      frameEls.forEach((frame, f) => frame.toggleAttribute('data-current', f === i));
      prev.setAttribute('aria-disabled', String(i === 0));
      next.setAttribute('aria-disabled', String(i === total - 1));
    }

    function go(i, smooth = true) {
      show(i);
      track.scrollTo({ left: offsetFor(index), behavior: smooth && !reducedMotion() ? 'smooth' : 'instant' });
    }

    function nearest() {
      const left = track.scrollLeft;
      let best = 0;
      frameEls.forEach((_, i) => {
        if (Math.abs(offsetFor(i) - left) < Math.abs(offsetFor(best) - left)) best = i;
      });
      return best;
    }

    const onScroll = () => {
      clearTimeout(settle);
      settle = setTimeout(() => show(nearest()), 120);
    };
    track.addEventListener('scroll', onScroll, { passive: true });

    /**
     * A spacer after the last frame lets every frame reach the left edge.
     * It only changes with the track's width, so other reflows leave a swipe
     * in progress alone.
     */
    let laidOutAt = -1;
    function layout() {
      if (track.clientWidth === laidOutAt) return;
      laidOutAt = track.clientWidth;
      const last = frameEls[total - 1];
      const gap = parseFloat(getComputedStyle(track).columnGap) || 0;
      const room = track.clientWidth - padStart() - last.offsetWidth - gap;
      track.style.setProperty('--stream-strip-end', `${Math.max(0, Math.floor(room))}px`);
      track.scrollTo({ left: offsetFor(Math.max(0, index)), behavior: 'instant' });
    }

    show(start);
    return {
      get index() { return index; },
      step(delta) { go(index + delta); },
      layout,
      destroy() { clearTimeout(settle); track.removeEventListener('scroll', onScroll); },
    };
  }

  // ---- Players -------------------------------------------------------------

  /**
   * A video or reel. Nothing autoplays, so nothing plays with sound until the
   * visitor presses play. Until the file exists, the poster or an empty frame
   * stands in, with a line that says so.
   */
  function player(item, { eager = false, vertical = false } = {}) {
    const m = item.media || {};
    const time = m.duration ? `<span class="stream-player__time micro"><span class="visually-hidden">Running time </span>${esc(m.duration)}</span>` : '';
    if (m.video) {
      const poster = m.src ? ` poster="${esc(m.src)}"` : '';
      return `<div class="stream-player"${vertical ? ' data-vertical' : ''}>
        <video class="stream-player__video" controls playsinline preload="metadata"${poster} aria-label="${esc(item.title)}"><source src="${esc(m.video)}"></video>
      </div>`;
    }
    const still = m.src ? picture(m, { eager, sizes: vertical ? '330px' : '(max-width: 599px) 100vw, 900px' }) : '<span class="stream-player__empty"></span>';
    return `<div class="stream-player" data-missing${vertical ? ' data-vertical' : ''}>
      ${still}${time}
      <p class="stream-player__note micro">The video is not published yet.</p>
    </div>`;
  }

  // ---- Demos ---------------------------------------------------------------

  const demoChecks = new Map();

  /** A prototype's live build lives at /demos/<name>/, its links.full or its id. */
  function demoURL(item) {
    const full = item.links?.full;
    return full && full.startsWith('/demos/') ? full : `/demos/${item.id}/`;
  }

  /** Demos ship later, so each is checked once before it is offered live. */
  function demoReady(item) {
    const url = demoURL(item);
    if (!demoChecks.has(url)) {
      const check = fetch(url, { method: 'HEAD', cache: 'no-store' })
        .then((response) => response.ok && /html/.test(response.headers.get('content-type') || ''))
        .catch(() => false);
      const timeout = new Promise((resolve) => setTimeout(() => resolve(false), DEMO_TIMEOUT_MS));
      demoChecks.set(url, Promise.race([check, timeout]));
    }
    return demoChecks.get(url);
  }

  // ---- Views, one per kind of item -----------------------------------------
  //
  // A view is { tone, theme, layout, html, strip? }. Tone is "band" for
  // anything that belongs to a case study and "neutral" otherwise. Layout
  // tells panel.css how to arrange the parts on a wide screen: "split" puts
  // the story beside a wide stage, "tall" puts a narrow stage and an aside
  // beside the story, and "solo" is the story alone. The markup order is the
  // phone's reading order.

  function bandFacts(study) {
    return facts([['Role', study.facts[0]], ['Scope', study.facts[2]]]);
  }

  /** A case-study stack, one of its screens, or its video, in the project's band. */
  function caseBandView(item, study, ctx) {
    const figures = study.figures || [];
    const frames = [];
    let start = 0;
    if (item.type !== 'case-study') {
      const at = item.caseStudy.figure ? figures.findIndex((f) => f.id === item.caseStudy.figure) : -1;
      if (at >= 0) start = at;
      else frames.push(leadFrame(item));
    }
    figures.forEach((figure) => frames.push(figureFrame(figure)));
    const stack = item.type === 'case-study';
    const kicker = ['Case study', study.facts[1], stack ? `${figures.length} screens` : ''].filter(Boolean).join(' · ');
    return {
      tone: 'band',
      theme: study.theme,
      layout: 'split',
      strip: { frames, start },
      html: [
        head(kicker),
        title(ctx.level, study.title, ' stream-panel__title--case'),
        lede(study.premise),
        strip(frames, start, `${study.title} screens`),
        lede(study.note, 'intro'),
        bandFacts(study),
        cta(study.href, 'Read the full case study', '→'),
        closer(),
      ].join(''),
    };
  }

  /** A screen with no case study: neutral, with its related screens. */
  function screenView(item, ctx) {
    const shape = shapeOf(item.media);
    const image = item.media?.src
      ? picture(item.media, { eager: true, sizes: shape === 'phone' ? '(max-width: 599px) 240px, 300px' : '(max-width: 599px) 100vw, 900px' })
      : '<span class="stream-shot__empty"></span>';
    return {
      tone: 'neutral',
      layout: shape === 'phone' ? 'tall' : 'split',
      html: [
        head(`Screen · ${item.industry}`),
        title(ctx.level, item.title),
        lede(item.note),
        `<div class="stream-panel__media stream-shot" data-shape="${shape}">${image}</div>`,
        facts([['Project', item.project], ['Industry', item.industry], ['Platform', item.platform], ['Shared', monthYear(item.shared)]]),
        `<div class="stream-panel__aside">${relatedBlock(ctx.related, ctx.level)}</div>`,
        closer(),
      ].join(''),
    };
  }

  /**
   * A prototype runs live on a wide screen, in a device frame when it is a
   * mobile build. Phones never run one inline: a mobile build goes full
   * screen before this view is asked for, and a web build shows its poster
   * with a line that it runs on a larger screen.
   */
  function prototypeView(item, study, ctx) {
    const mobile = item.platform === 'Mobile';
    const phone = isPhone();
    const live = ctx.demo && !phone;
    const band = Boolean(study);
    let stage;
    if (live) {
      const frame = `<iframe class="stream-proto__frame" src="${esc(demoURL(item))}" title="${esc(item.title)}, live prototype" loading="eager"></iframe>`;
      stage = `<div class="stream-proto" data-device="${mobile ? 'phone' : 'web'}" data-live>
        <p class="stream-proto__badge micro"><span class="stream-proto__dot" aria-hidden="true"></span>Live · tap to try</p>
        <div class="stream-proto__screen">${frame}</div>
      </div>`;
    } else {
      const poster = item.media?.src
        ? picture(item.media, { eager: true, sizes: '(max-width: 599px) 100vw, 640px' })
        : '<span class="stream-proto__empty"></span>';
      const note = phone && !mobile
        ? 'Runs on a larger screen. Open this page on a laptop to try it live.'
        : ctx.demo === false
          ? `The live prototype is not published yet${item.media?.src ? ', so its poster stands in for now' : ''}.`
          : '';
      stage = `<div class="stream-proto" data-device="${mobile && !phone ? 'phone' : 'web'}">
        <div class="stream-proto__screen">${poster}</div>
        ${note ? `<p class="stream-proto__note micro"><span aria-hidden="true">▭</span> ${esc(note)}</p>` : ''}
      </div>`;
    }
    const open = live ? `<a class="stream-panel__link micro" href="${esc(demoURL(item))}" target="_blank" rel="noopener">Open in a new tab <span aria-hidden="true">↗</span></a>` : '';
    return {
      tone: band ? 'band' : 'neutral',
      theme: study?.theme,
      layout: mobile && !phone ? 'tall' : 'split',
      html: [
        head(`Prototype · ${band ? item.project : item.industry}`),
        title(ctx.level, item.title),
        lede(item.note),
        `<div class="stream-panel__media">${stage}</div>`,
        facts([['Industry', item.industry], ['Platform', item.platform], ...(item.facts || []).map((f) => [f.label, f.value]), ['Shared', monthYear(item.shared)]]),
        band ? cta(study.href, 'Read the full case study', '→') : '',
        `<div class="stream-panel__aside">${steps(item, ctx.level)}${relatedBlock(ctx.related, ctx.level)}</div>`,
        closer(open),
      ].join(''),
    };
  }

  /** A tool previews and links out, marked ↗. A post about it opens here. */
  function toolView(item, study, ctx) {
    const post = (item.related || []).map(itemById).find((r) => r?.type === 'post');
    const m = item.media || {};
    const preview = m.src
      ? picture(m, { eager: true, sizes: '(max-width: 599px) 100vw, 900px' })
      : `<span class="stream-tool__tile" aria-hidden="true"><span class="micro">${esc(m.tile || 'Tool')}</span><span class="stream-tool__name">${esc(item.title)}</span></span>`;
    const external = item.links?.external;
    return {
      tone: study ? 'band' : 'neutral',
      theme: study?.theme,
      layout: 'split',
      html: [
        head(`Tool · ${m.tile || item.industry}`),
        title(ctx.level, item.title),
        lede(item.note),
        `<div class="stream-panel__media stream-tool">${preview}</div>`,
        facts([
          ['Runs in', item.platform],
          ...(item.facts || []).map((f) => [f.label, f.value]),
          ['Shared', monthYear(item.shared)],
          ['Writing', post?.title, post ? jump(post, post.title) : ''],
        ]),
        external ? cta(external.href, external.label, '↗') : '',
        closer(),
      ].join(''),
    };
  }

  /**
   * A post previews its dek and facts, then Continue reading →. The island
   * does not carry a post's opening paragraphs yet, so the stage shows the
   * cover when there is one and is left out when there is not.
   */
  function postView(item, study, ctx) {
    const tool = (item.related || []).map(itemById).find((r) => r && r.type !== 'post');
    const cover = item.media?.src;
    const shape = shapeOf(item.media);
    const full = item.links?.full || (item.href && !item.href.startsWith('/#') ? item.href : '');
    return {
      tone: study ? 'band' : 'neutral',
      theme: study?.theme,
      layout: cover ? (shape === 'phone' ? 'tall' : 'split') : 'solo',
      html: [
        head(`Writing · ${yearOf(item.shared)}`),
        title(ctx.level, item.title, ' stream-panel__title--post'),
        lede(item.note, 'dek'),
        cover ? `<div class="stream-panel__media stream-shot stream-shot--cover" data-shape="${shape}">${picture(item.media, { eager: true, sizes: '(max-width: 599px) 100vw, 640px' })}</div>` : '',
        facts([['About', tool?.title, tool ? jump(tool, tool.title) : ''], ...(item.facts || []).map((f) => [f.label, f.value])]),
        full ? cta(full, 'Continue reading', '→') : '',
        closer(),
      ].join(''),
    };
  }

  function videoView(item, ctx) {
    return {
      tone: 'neutral',
      layout: 'split',
      html: [
        head(`Video · ${item.industry}`),
        title(ctx.level, item.title),
        lede(item.note),
        `<div class="stream-panel__media">${player(item, { eager: true })}</div>`,
        facts([['Project', item.project], ['Running time', item.media?.duration], ['Shared', monthYear(item.shared)]]),
        `<div class="stream-panel__aside">${relatedBlock(ctx.related, ctx.level)}</div>`,
        closer(),
      ].join(''),
    };
  }

  /** A reel plays at phone size, with the next reel a swipe away in its related row. */
  function reelView(item, study, ctx) {
    return {
      tone: study ? 'band' : 'neutral',
      theme: study?.theme,
      layout: 'tall',
      html: [
        head(`Reel · ${item.industry}`),
        title(ctx.level, item.title),
        lede(item.note),
        `<div class="stream-panel__media">${player(item, { eager: true, vertical: true })}</div>`,
        facts([['Project', item.project], ['Running time', item.media?.duration], ['Shared', monthYear(item.shared)]]),
        study ? cta(study.href, 'Read the full case study', '→') : '',
        `<div class="stream-panel__aside">${relatedBlock(ctx.related, ctx.level)}</div>`,
        closer(),
      ].join(''),
    };
  }

  function viewFor(item, ctx) {
    const study = studyFor(item);
    switch (item.type) {
      case 'case-study':
      case 'screen':
        return study ? caseBandView(item, study, ctx) : screenView(item, ctx);
      case 'video':
        return study ? caseBandView(item, study, ctx) : videoView(item, ctx);
      case 'prototype': return prototypeView(item, study, ctx);
      case 'tool': return toolView(item, study, ctx);
      case 'post': return postView(item, study, ctx);
      case 'reel': return reelView(item, study, ctx);
      default: return screenView(item, ctx);
    }
  }

  // ---- The panel -----------------------------------------------------------

  /** What is open: kind is "item" or "about", or null when nothing is. */
  const open = { kind: null };
  let token = 0;

  function createPanel() {
    const panel = document.createElement('section');
    panel.className = 'stream-panel';
    panel.id = 'stream-panel';
    panel.setAttribute('aria-labelledby', 'stream-panel-title');
    panel.innerHTML = `<svg class="stream-panel__rise" aria-hidden="true" focusable="false" preserveAspectRatio="none"><path/></svg>
      <p class="visually-hidden" aria-live="polite" data-announce></p>
      <div class="stream-panel__body"></div>`;
    riseWatcher.observe(panel);
    return panel;
  }

  /** Redraws a rise when its width changes, as when a scrollbar appears. */
  const riseWatcher = new ResizeObserver((entries) => {
    for (const entry of entries) {
      const svg = entry.target.matches('svg') ? entry.target : entry.target.querySelector(':scope > .stream-panel__rise');
      if (!svg || Math.round(entry.contentRect.width) === Number(svg.dataset.width)) continue;
      if (open.kind === 'item' && entry.target === open.panel) fitRise();
      if (open.kind === 'about' && entry.target === open.rise) fitAboutRise();
    }
  });

  function headingLevel(card) {
    const heading = card.querySelector('.stream-card__title, .stream-row__title');
    const level = heading ? Number(heading.tagName.slice(1)) : 2;
    return clamp(level || 2, 2, 5);
  }

  /** Writes a view into the panel and wires up its strip. */
  function render(panel, item, view) {
    open.strip?.destroy();
    open.strip = null;
    panel.dataset.tone = view.tone;
    panel.dataset.layout = view.layout;
    panel.dataset.type = item.type;
    // The theme class carries the project's colours, as it does on the card.
    [...panel.classList].filter((name) => name.startsWith('theme-')).forEach((name) => panel.classList.remove(name));
    if (view.theme) panel.classList.add(`theme-${view.theme}`);
    panel.querySelector('.stream-panel__body').innerHTML = view.html;
    if (view.strip) {
      open.strip = stripController(panel.querySelector('[data-strip]'), view.strip.frames, view.strip.start);
    }
  }

  function fitRise() {
    const { panel, card } = open;
    drawRise(panel.querySelector('.stream-panel__rise'), centreOf(card), panel.dataset.tone === 'band');
  }

  /** Places the panel under the opener's row, full width, with the rise under the card. */
  function fit() {
    const { panel, card } = open;
    const end = measureRowEnd(card, panel);
    if (end.nextElementSibling !== panel) end.after(panel);
    panel.style.setProperty('--stream-row-gap', `${rowGap(panel.parentElement)}px`);
    bleed(panel);
    fitRise();
    open.strip?.layout();
  }

  /** Scrolls so the opened row and as much of its panel as fits are in view. */
  function bringIntoView(card, panel, smooth) {
    const top = card.getBoundingClientRect().top;
    const bottom = panel.getBoundingClientRect().top + panel.offsetHeight;
    if (isPhone()) {
      // Row 03's phone note: a tap scrolls the tapped row to the top.
      scrollByY(top - 16, smooth);
      return;
    }
    const need = Math.min(bottom + 24 - window.innerHeight, top - 24);
    if (need > 0) scrollByY(need, smooth);
  }

  function focusKeyIn(panel) {
    const active = document.activeElement;
    return active && panel.contains(active) ? active.closest('[data-focus-key]')?.dataset.focusKey : null;
  }

  function restoreFocus(panel, key) {
    const target = (key && panel.querySelector(`[data-focus-key="${CSS.escape(key)}"]`)) || panel.querySelector('#stream-panel-title');
    target?.focus({ preventScroll: true });
  }

  async function openItem(link, { animate = true, focus = true } = {}) {
    const id = link.dataset.open;
    const item = itemById(id);
    const card = link.closest(CARD) || link;
    if (!item || !isRendered(card)) return;

    // The open card closes its own panel.
    if (open.kind === 'item' && open.card === card) {
      closeItem();
      return;
    }
    const mine = ++token;
    const demo = item.type === 'prototype' ? await demoReady(item) : undefined;
    if (mine !== token) return;

    // A phone runs a mobile prototype full screen, not in the stream.
    if (item.type === 'prototype' && item.platform === 'Mobile' && isPhone() && demo) {
      closeAny({ animate: false, focus: false });
      openFullscreen(item, link);
      return;
    }
    if (open.kind === 'about') closeAbout({ animate: false, focus: false });

    const level = headingLevel(card);
    const related = relatedSet(item);
    const view = viewFor(item, { level, related, demo });
    const previous = open.kind === 'item' ? open : null;
    let panel = previous?.panel;
    const end = measureRowEnd(card, panel);
    const inPlace = Boolean(panel && end.nextElementSibling === panel);

    if (previous) {
      setExpanded(previous.link, false);
      stopMedia(previous.panel);
      if (!inPlace) {
        // Moving to another row: the old panel goes at once, and the page
        // shifts so the card that was clicked stays where it was.
        const before = card.getBoundingClientRect().top;
        retire(previous.panel);
        previous.panel.remove();
        scrollByY(card.getBoundingClientRect().top - before, false);
        panel = null;
      }
    }
    if (!panel) panel = createPanel();

    Object.assign(open, { kind: 'item', panel, card, link, id, level, related, demo });
    render(panel, item, view);
    fit();
    setExpanded(link, true, 'stream-panel');
    setHash(id);
    watchContainer(card.parentElement);

    const moving = animate && !inPlace && !reducedMotion();
    bringIntoView(card, panel, moving);
    if (moving) {
      // At the start the panel takes no room: its margins cancel the row gap
      // that its own grid row adds, so the rows below do not jump.
      grow(panel, { marginTop: `${-rowGap(panel.parentElement)}px`, marginBottom: '0px' }).then(() => {
        if (deferred) relayout();
        deferred = false;
      });
    }
    if (focus) panel.querySelector('#stream-panel-title')?.focus({ preventScroll: true });
  }

  /** Shows another item in the open panel, which stays where it is. */
  async function showInPanel(id) {
    const item = itemById(id);
    if (!item || open.kind !== 'item') return;
    const mine = ++token;
    const demo = item.type === 'prototype' ? await demoReady(item) : undefined;
    if (mine !== token || open.kind !== 'item') return;
    const { panel, level } = open;
    const key = focusKeyIn(panel);
    let related = open.related;
    const at = related ? related.ids.indexOf(id) : -1;
    related = at >= 0 ? { ...related, index: at } : relatedSet(item);
    stopMedia(panel);
    render(panel, item, viewFor(item, { level, related, demo }));
    Object.assign(open, { id, related, demo });
    fitRise();
    open.strip?.layout();
    setHash(id);
    const count = related ? `, ${related.index + 1} of ${related.ids.length}` : '';
    panel.querySelector('[data-announce]').textContent = `${item.title}${count}`;
    restoreFocus(panel, key);
  }

  function step(delta) {
    if (open.kind !== 'item') return;
    if (open.strip) {
      open.strip.step(delta);
      return;
    }
    const related = open.related;
    if (!related) return;
    const next = related.index + delta;
    if (next >= 0 && next < related.ids.length) showInPanel(related.ids[next]);
  }

  function stopMedia(root) {
    root.querySelectorAll('video').forEach((video) => video.pause());
  }

  /** A panel on its way out keeps no ids and takes no focus. */
  function retire(panel) {
    panel.inert = true;
    panel.querySelectorAll('[id]').forEach((el) => el.removeAttribute('id'));
    panel.removeAttribute('id');
    riseWatcher.unobserve(panel);
  }

  function closeItem({ animate = true, focus = true } = {}) {
    if (open.kind !== 'item') return;
    const { panel, link } = open;
    token++;
    open.strip?.destroy();
    unwatchContainer();
    for (const key of Object.keys(open)) delete open[key];
    open.kind = null;
    setExpanded(link, false);
    clearHash();
    stopMedia(panel);
    retire(panel);
    if (focus) link.focus();
    if (animate && !reducedMotion()) {
      shrink(panel, { marginTop: `${-rowGap(panel.parentElement)}px`, marginBottom: '0px' }).then(() => panel.remove());
    } else {
      panel.remove();
    }
  }

  function closeAny(options) {
    if (open.kind === 'item') closeItem(options);
    else if (open.kind === 'about') closeAbout(options);
  }

  // Reflow: a new column count, or cards shown or hidden by pagination and
  // filters, can move the opener to another row. The panel follows it.
  let frame = 0;
  let deferred = false;
  function relayout() {
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(() => {
      if (open.kind === 'item') {
        // Mid-animation sizes are not final. Try again when it ends.
        if (open.panel.classList.contains('is-moving')) {
          deferred = true;
          return;
        }
        if (!isRendered(open.card)) closeItem({ animate: false, focus: false });
        else fit();
      } else if (open.kind === 'about') {
        fitAboutRise();
      }
    });
  }

  let containerWatch = null;
  function watchContainer(container) {
    unwatchContainer();
    containerWatch = new MutationObserver((records) => {
      if (records.some((r) => r.target.parentElement === container && !r.target.classList.contains('stream-panel'))) relayout();
    });
    containerWatch.observe(container, { attributes: true, subtree: true, attributeFilter: ['hidden', 'class', 'style'] });
  }
  function unwatchContainer() {
    containerWatch?.disconnect();
    containerWatch = null;
  }

  // ---- A mobile prototype, full screen on a phone ---------------------------
  //
  // Opening it adds one history step, so the back gesture closes it, and so
  // does Close. It is a modal dialog, so the page behind is inert and Esc
  // works where there is a keyboard.

  let fullscreen = null;

  function openFullscreen(item, link) {
    const dialog = document.createElement('dialog');
    dialog.className = 'stream-fullscreen';
    dialog.setAttribute('aria-labelledby', 'stream-fullscreen-title');
    dialog.innerHTML = `<div class="stream-fullscreen__bar">
        <button type="button" class="stream-fullscreen__close micro" data-fullscreen-close><span aria-hidden="true">×</span> Close</button>
        <h2 class="stream-fullscreen__title micro" id="stream-fullscreen-title">${esc(item.title)}</h2>
        <p class="stream-fullscreen__live micro"><span class="stream-proto__dot" aria-hidden="true"></span>Live</p>
      </div>
      <iframe class="stream-fullscreen__frame" src="${esc(demoURL(item))}" title="${esc(item.title)}, live prototype"></iframe>`;
    dialog.addEventListener('cancel', (event) => {
      event.preventDefault();
      leaveFullscreen();
    });
    document.body.append(dialog);
    dialog.showModal();
    // The entry underneath keeps no hash, so going back leaves nothing open.
    clearHash();
    // Keep what else the entry holds, such as how many cards site.js shows.
    history.pushState({ ...history.state, streamFullscreen: item.id }, '', `${location.pathname}${location.search}#${encodeURIComponent(item.id)}`);
    fullscreen = { dialog, link, id: item.id };
    setExpanded(link, true);
    dialog.querySelector('[data-fullscreen-close]').focus();
  }

  /** Close goes back a step when the full-screen entry is the current one. */
  function leaveFullscreen() {
    if (!fullscreen) return;
    if (history.state?.streamFullscreen === fullscreen.id) history.back();
    else closeFullscreen();
  }

  function closeFullscreen() {
    if (!fullscreen) return;
    const { dialog, link } = fullscreen;
    fullscreen = null;
    dialog.close();
    dialog.remove();
    setExpanded(link, false);
    link.focus();
  }

  window.addEventListener('popstate', () => {
    if (fullscreen && history.state?.streamFullscreen !== fullscreen.id) closeFullscreen();
  });

  // ---- About ---------------------------------------------------------------
  //
  // 2A puts <section id="about" class="about" hidden> after the masthead on
  // every page, and the masthead's About link points to #about. About opens
  // and closes like a panel, with the same rise, drawn under the About link
  // or, when that link sits in the closed phone menu, under the menu trigger.

  const aboutSection = () => document.getElementById('about');

  function aboutRise(section) {
    let rise = section.previousElementSibling;
    if (!rise?.classList.contains('stream-about-rise')) {
      rise = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      rise.setAttribute('class', 'stream-panel__rise stream-about-rise');
      rise.setAttribute('aria-hidden', 'true');
      rise.setAttribute('focusable', 'false');
      rise.setAttribute('preserveAspectRatio', 'none');
      rise.append(document.createElementNS('http://www.w3.org/2000/svg', 'path'));
      section.before(rise);
    }
    return rise;
  }

  /** The visible control to draw the rise under. */
  function aboutAnchor(opener) {
    if (opener && isRendered(opener)) return opener;
    // A link inside a closed menu: use the control that opens that menu.
    for (let el = opener?.parentElement; el; el = el.parentElement) {
      if (!el.id) continue;
      const trigger = document.querySelector(`[aria-controls~="${CSS.escape(el.id)}"]`);
      if (trigger && isRendered(trigger)) return trigger;
    }
    return [...document.querySelectorAll(ABOUT_LINKS)].find(isRendered) || null;
  }

  function fitAboutRise() {
    const { rise, opener } = open;
    bleed(rise);
    drawRise(rise, centreOf(aboutAnchor(opener)), false);
  }

  function openAbout(opener, { animate = true, focus = true } = {}) {
    const section = aboutSection();
    if (!section) return;
    if (open.kind === 'about') {
      closeAbout();
      return;
    }
    token++;
    if (open.kind === 'item') closeItem({ animate: false, focus: false });
    if (fullscreen) closeFullscreen();
    const rise = aboutRise(section);
    rise.style.display = '';
    section.hidden = false;
    Object.assign(open, { kind: 'about', section, rise, opener });
    document.querySelectorAll(ABOUT_LINKS).forEach((link) => setExpanded(link, true, 'about'));
    riseWatcher.observe(rise);
    fitAboutRise();
    setHash('about');
    if (animate) {
      grow(rise);
      grow(section);
    }
    if (focus) {
      const heading = section.querySelector('h1, h2, h3') || section;
      if (!heading.hasAttribute('tabindex')) heading.setAttribute('tabindex', '-1');
      heading.focus({ preventScroll: true });
      if (section.getBoundingClientRect().top < 0) section.scrollIntoView({ block: 'start' });
    }
  }

  function closeAbout({ animate = true, focus = true } = {}) {
    if (open.kind !== 'about') return;
    const { section, rise, opener } = open;
    for (const key of Object.keys(open)) delete open[key];
    open.kind = null;
    riseWatcher.unobserve(rise);
    document.querySelectorAll(ABOUT_LINKS).forEach((link) => setExpanded(link, false));
    clearHash();
    stopMedia(section);
    const done = () => {
      section.hidden = true;
      rise.style.display = 'none';
      section.getAnimations().forEach((a) => a.cancel());
      rise.getAnimations().forEach((a) => a.cancel());
      section.classList.remove('is-moving');
      rise.classList.remove('is-moving');
    };
    if (animate && !reducedMotion()) Promise.all([shrink(section), shrink(rise)]).then(done);
    else done();
    if (focus) (aboutAnchor(opener) || opener)?.focus();
  }

  // ---- Events --------------------------------------------------------------

  const plainClick = (event) => !(event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey);

  document.addEventListener('click', (event) => {
    if (!plainClick(event) || !(event.target instanceof Element)) return;
    const target = event.target;

    if (target.closest('[data-fullscreen-close]')) {
      event.preventDefault();
      leaveFullscreen();
      return;
    }
    // About's Close is a link to #top, so it works without this script.
    const close = target.closest('[data-panel-close], #about .about__close');
    if (close) {
      event.preventDefault();
      if (close.closest('#about')) closeAbout();
      else closeItem();
      return;
    }
    const stepper = target.closest('.stream-panel [data-step]');
    if (stepper) {
      event.preventDefault();
      if (stepper.getAttribute('aria-disabled') !== 'true') {
        // A strip's own arrows step the strip. The related arrows step items.
        if (stepper.closest('.stream-related')) {
          const related = open.related;
          const next = related ? related.index + Number(stepper.dataset.step) : -1;
          if (related && next >= 0 && next < related.ids.length) showInPanel(related.ids[next]);
        } else {
          step(Number(stepper.dataset.step));
        }
      }
      return;
    }
    const show = target.closest('.stream-panel [data-show]');
    if (show) {
      event.preventDefault();
      showInPanel(show.dataset.show);
      return;
    }
    const opener = target.closest('[data-open]');
    if (opener && itemById(opener.dataset.open) && !opener.closest('.stream-panel')) {
      event.preventDefault();
      openItem(opener);
      return;
    }
    const about = target.closest(ABOUT_LINKS);
    if (about && aboutSection()) {
      event.preventDefault();
      openAbout(about);
    }
  });

  /** Keys that a focused control needs for itself. */
  function keepsArrows(el) {
    return el instanceof Element && Boolean(el.closest('input, textarea, select, video, audio, iframe, [contenteditable]:not([contenteditable="false"]), [role="slider"], [role="tablist"], [role="listbox"], [role="menu"]'));
  }

  document.addEventListener('keydown', (event) => {
    if (event.defaultPrevented || event.isComposing) return;
    if (event.key === 'Escape') {
      if (fullscreen) return; // The dialog's cancel event handles it.
      if (open.kind === 'item') closeItem();
      else if (open.kind === 'about') closeAbout();
      else return;
      event.preventDefault();
      return;
    }
    if ((event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') || open.kind !== 'item') return;
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || keepsArrows(event.target)) return;
    // Arrows belong to the panel while focus is in it, on the card that
    // opened it, or nowhere in particular.
    const active = document.activeElement;
    if (active && active !== document.body && !open.panel.contains(active) && active !== open.link) return;
    event.preventDefault();
    step(event.key === 'ArrowLeft' ? -1 : 1);
  });

  // Only a change of width can change the rows. A phone's address bar
  // changes the height as the page scrolls, and that must not disturb a swipe.
  let viewportWidth = document.documentElement.clientWidth;
  window.addEventListener('resize', () => {
    const width = document.documentElement.clientWidth;
    if (width === viewportWidth) return;
    viewportWidth = width;
    relayout();
  });
  document.addEventListener('stream:layout', relayout);
  // Crossing the phone breakpoint changes what a prototype offers.
  media(PHONE).addEventListener('change', () => {
    if (open.kind === 'item' && itemById(open.id)?.type === 'prototype') showInPanel(open.id);
  });

  window.addEventListener('hashchange', () => openFromHash({ animate: true }));

  // ---- Deep links ----------------------------------------------------------

  function cardLinkFor(id) {
    return [...document.querySelectorAll('[data-open]')].find((link) => link.dataset.open === id && !link.closest('.stream-panel'));
  }

  function openFromHash({ animate = false } = {}) {
    let id = '';
    try {
      id = decodeURIComponent(location.hash.slice(1));
    } catch {
      return;
    }
    if (!id) return;
    if (id === 'about') {
      if (aboutSection() && open.kind !== 'about') {
        openAbout(document.querySelector(ABOUT_LINKS), { animate });
      }
      return;
    }
    if (!itemById(id) || (open.kind === 'item' && open.id === id)) return;
    // Pagination reveals every card up to this one, then it opens.
    document.dispatchEvent(new CustomEvent('stream:reveal', { detail: { id } }));
    const link = cardLinkFor(id);
    const card = link?.closest(CARD);
    if (!link || !card) return;
    const run = () => {
      if (!isRendered(card)) return;
      openItem(link, { animate }).then(() => {
        if (open.kind === 'item' && open.id === id && !animate) {
          scrollByY(card.getBoundingClientRect().top - (isPhone() ? 16 : 24), false);
        }
      });
    };
    if (isRendered(card)) run();
    else requestAnimationFrame(run);
  }

  // ---- Start ---------------------------------------------------------------

  function start() {
    const links = document.querySelectorAll('[data-open]');
    if (links.length && Object.keys(streamData().items).length) {
      links.forEach((link) => {
        if (itemById(link.dataset.open)) setExpanded(link, false);
      });
    }
    if (aboutSection()) {
      // Taking over About switches off style.css's :target fallback.
      document.documentElement.classList.add('panels');
      document.querySelectorAll(ABOUT_LINKS).forEach((link) => setExpanded(link, false, 'about'));
    }
    openFromHash();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
})();
