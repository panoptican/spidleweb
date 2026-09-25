#!/usr/bin/env node
/**
 * Stream generator for spidleweb.net.
 *
 * content/stream.json is the hand-ordered list of everything in the stream.
 * This script checks it, then writes card markup into marked regions of the
 * pages listed in PAGES. Pages keep serving plain files, and the output is
 * committed like any other edit.
 *
 *   node scripts/build-stream.mjs           rewrite every page in PAGES
 *   node scripts/build-stream.mjs --check   change nothing, and exit 1 when
 *                                           the content is invalid or a page
 *                                           is out of date
 *
 * Node 20 or later, no dependencies. The "Generator" and "Card contract"
 * sections of specs/redesign.md describe the schema and the markup.
 *
 * A page opts in with two kinds of marker. The generator replaces whatever
 * sits between each pair and leaves the rest of the page alone.
 *
 *   <!-- stream:start -->            cards or rows, in stream order
 *   <!-- stream:end -->
 *   <!-- stream-data:start -->       the JSON island the open panel reads
 *   <!-- stream-data:end -->
 *
 * A stream:start marker takes optional settings:
 *   view="grid|list"     Grid cards (the default) or List rows
 *   case-study="<slug>"  only what that case study shares, for "More from"
 *   heading="2..6"       heading level for titles, 2 by default
 *   eager="<n>"          load the first n images eagerly, 0 by default
 *
 * Two more markers serve the Work pages. Both follow the case studies
 * newest first, so the index and the bands always agree:
 *
 *   <!-- work-index:start -->        a row per case study, for /work/
 *   <!-- work-index:end -->
 *   <!-- next-story:start case-study="<slug>" -->
 *   <!-- next-story:end -->          the band that ends a case-study page,
 *                                    naming the next one in /work/ order
 */

import { existsSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { basename, dirname, extname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const STREAM_FILE = 'content/stream.json';

// Pages with generated regions. Add a page here when it gains one.
const PAGES = [
  'content/fixtures/grid.html',
  'content/fixtures/list.html',
  'content/fixtures/more-from.html',
  'work/index.html',
  'work/campaign-sim.html',
  'work/conservis.html',
  'work/everag.html',
  'work/expert-insights.html',
  'work/plinth.html',
  'work/vidscrip.html',
];

// ---- Vocabulary ----------------------------------------------------------

// Each type's label on cards, and the hint List rows show for opening it here.
const TYPES = {
  screen: { label: 'Screen', hint: 'Open' },
  'case-study': { label: 'Case study', hint: 'Preview here' },
  prototype: { label: 'Prototype', hint: 'Try it here' },
  tool: { label: 'Tool', hint: 'Open' },
  post: { label: 'Writing', hint: 'Read it here' },
  video: { label: 'Video', hint: 'Play here' },
  reel: { label: 'Reel', hint: 'Play here' },
};

// Filters are built from these, so a typo would quietly make a new filter.
const INDUSTRIES = [
  'Agriculture', 'Design systems', 'Finance', 'Healthcare', 'Home services',
  'Manufacturing', 'Productivity', 'Publishing', 'Sports', 'Writing',
];
const PLATFORMS = ['Web', 'Mobile', 'Tablet', 'Figma'];

// Every key an item may carry. Anything else is reported as a typo.
const ITEM_KEYS = [
  'id', 'type', 'title', 'note', 'alt', 'project', 'industry', 'platform', 'shared',
  'caseStudy', 'theme', 'media', 'links', 'related', 'facts', 'steps', 'placeholder',
];
const MEDIA_KEYS = ['src', 'width', 'height', 'video', 'duration', 'tile'];

// Image `sizes` hints. Keep them in step with the Grid columns in stream.css
// (Phase 2A) and the List image column (Phase 2D).
const SIZES = {
  grid: '(max-width: 599px) calc(100vw - 32px), (max-width: 1099px) calc((100vw - 120px) / 3), calc((100vw - 160px) / 5)',
  list: '(max-width: 767px) calc(100vw - 32px), min(560px, 40vw)',
};

// A /work/ cover is 306px wide beside its text, and runs the width of the
// screen, less the gutters and the stack's offset, on a phone (pages.css).
const COVER_SIZES = '(max-width: 599px) calc(100vw - 44px), 306px';

// Items in the first Grid row at 1440. The spec puts a case study among
// them, so the colour chip is explained early.
const FIRST_ROW = 5;

// ---- Small helpers -------------------------------------------------------

const read = (path) => readFileSync(join(ROOT, path), 'utf8');
const exists = (path) => existsSync(join(ROOT, path));
const isObject = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
const isText = (value) => typeof value === 'string' && value.trim() !== '';
const url = (path) => `/${path}`;
const year = (shared) => (shared ? shared.slice(0, 4) : '');

function slugify(text) {
  return text.toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function esc(text) {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

const ENTITIES = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: '\u00a0' };
function decode(text) {
  return text.replace(/&(#x[0-9a-f]+|#[0-9]+|[a-z]+);/gi, (match, entity) => {
    if (entity[0] !== '#') return ENTITIES[entity.toLowerCase()] ?? match;
    const hex = entity[1].toLowerCase() === 'x';
    return String.fromCodePoint(parseInt(entity.slice(hex ? 2 : 1), hex ? 16 : 10));
  });
}

const stripTags = (html) => decode(html.replace(/<[^>]+>/g, '')).replace(/\s+/g, ' ').trim();

function attributes(tag) {
  const found = {};
  for (const [, name, value] of tag.matchAll(/([a-z-]+)(?:="([^"]*)")?/g)) found[name] = value ?? '';
  return found;
}

/**
 * Width and height from an image file's header, for PNG, WebP, JPEG, and
 * AVIF. Returns null for anything else.
 */
function imageSize(path) {
  const buf = readFileSync(join(ROOT, path));
  if (buf.length > 24 && buf.readUInt32BE(0) === 0x89504e47) {
    return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
  }
  if (buf.toString('latin1', 0, 4) === 'RIFF' && buf.toString('latin1', 8, 12) === 'WEBP') {
    const chunk = buf.toString('latin1', 12, 16);
    if (chunk === 'VP8 ') return { width: buf.readUInt16LE(26) & 0x3fff, height: buf.readUInt16LE(28) & 0x3fff };
    if (chunk === 'VP8L') {
      const bits = buf.readUInt32LE(21);
      return { width: (bits & 0x3fff) + 1, height: ((bits >> 14) & 0x3fff) + 1 };
    }
    if (chunk === 'VP8X') return { width: buf.readUIntLE(24, 3) + 1, height: buf.readUIntLE(27, 3) + 1 };
  }
  if (buf[0] === 0xff && buf[1] === 0xd8) {
    // Walk the JPEG markers to the first start-of-frame.
    let at = 2;
    while (at + 9 < buf.length) {
      if (buf[at] !== 0xff) { at += 1; continue; }
      const marker = buf[at + 1];
      if (marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker)) {
        return { width: buf.readUInt16BE(at + 7), height: buf.readUInt16BE(at + 5) };
      }
      at += 2 + buf.readUInt16BE(at + 2);
    }
  }
  if (buf.toString('latin1', 4, 8) === 'ftyp') {
    // AVIF keeps the size in its "ispe" box: 4 bytes of flags, then width and height.
    const ispe = buf.indexOf('ispe');
    if (ispe > 0) return { width: buf.readUInt32BE(ispe + 8), height: buf.readUInt32BE(ispe + 12) };
  }
  return null;
}

/**
 * AVIF derivatives for an image, found by name. The feed keeps them in a
 * `responsive/` folder beside the fallback, and the case studies keep them
 * next to it, so both places are searched: `<stem>-<width>.avif`.
 */
function findAvifs(src) {
  const stem = basename(src, extname(src));
  const pattern = new RegExp(`^${stem.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}-(\\d+)\\.avif$`);
  const byWidth = new Map();
  for (const folder of [join(dirname(src), 'responsive'), dirname(src)]) {
    if (!exists(folder)) continue;
    for (const name of readdirSync(join(ROOT, folder)).sort()) {
      const match = name.match(pattern);
      if (match && !byWidth.has(Number(match[1]))) byWidth.set(Number(match[1]), `${folder}/${name}`);
    }
  }
  return [...byWidth].sort((a, b) => a[0] - b[0]).map(([width, path]) => ({ width, path }));
}

// Picks the shape the card uses to frame an image, from its aspect ratio.
function shapeOf(width, height) {
  const ratio = height / width;
  if (ratio <= 0.85) return 'wide';
  if (ratio <= 1.4) return 'square';
  return 'tall';
}

// ---- Case-study pages ----------------------------------------------------

/**
 * Reads what the stream needs from work/<slug>.html: the premise, the facts,
 * the intro note, and every figure in page order. A figure is known by its
 * image's file name without the extension, such as "conservis-03", and its
 * anchor on the page is "fig-" plus that name.
 */
function readCaseStudyPage(slug) {
  const file = `work/${slug}.html`;
  if (!exists(file)) return { error: `${file} does not exist` };
  const html = read(file);
  const base = `https://spidleweb.net/work/${slug}`;
  const resolve = (path) => new URL(path, base).pathname;

  const premise = html.match(/class="case-context__premise">([\s\S]*?)<\/p>/);
  const facts = html.match(/class="case-context__facts">([\s\S]*?)<\/dl>/);
  const note = html.match(/class="case-context__note">([\s\S]*?)<\/p>/);
  if (!premise || !facts || !note) return { error: `${file} has no case-context premise, facts, and note to read` };
  const factList = [...facts[1].matchAll(/<dd>([\s\S]*?)<\/dd>/g)].map((m) => stripTags(m[1]));
  if (factList.length < 2) return { error: `${file} lists fewer than two facts` };

  const figures = [];
  for (const match of html.matchAll(/<figure([^>]*)>([\s\S]*?)<\/figure>/g)) {
    const figureTag = attributes(match[1]);
    const body = match[2];
    const img = body.match(/<img ([^>]*)>/);
    if (!img) continue;
    const image = attributes(img[1]);
    const src = resolve(image.src);
    const stem = basename(src, extname(src));
    const source = body.match(/<source ([^>]*)>/);
    const avif = source
      ? attributes(source[1]).srcset.split(',').map((entry) => {
        const [path, width] = entry.trim().split(/\s+/);
        return `${resolve(path)} ${width}`;
      }).join(', ')
      : '';
    const caption = body.match(/<figcaption[^>]*>([\s\S]*?)<\/figcaption>/);
    // Phone figures share one sentence, written after their group.
    const group = /\bproof-phone\b/.test(figureTag.class ?? '')
      ? html.slice(match.index).match(/class="proof-caption">([\s\S]*?)<\/p>/)
      : null;
    figures.push({
      id: stem,
      anchor: figureTag.id ?? null,
      src,
      width: Number(image.width),
      height: Number(image.height),
      alt: decode(image.alt ?? ''),
      avif,
      caption: caption ? caption[1].trim() : '',
      group: group ? group[1].trim() : '',
    });
  }
  if (!figures.length) return { error: `${file} has no figures` };

  return {
    premise: stripTags(premise[1]),
    facts: factList,
    note: stripTags(note[1]),
    figures,
  };
}

/**
 * The start and end years in a dateline such as "Foundry · 2016–21" or
 * "Blueshift · 2025", or null when it ends with neither.
 */
function yearSpan(dates) {
  const match = dates.match(/(\d{4})(?:–(\d{2}|\d{4}))?$/);
  if (!match) return null;
  const start = Number(match[1]);
  if (!match[2]) return { start, end: start };
  // A two-digit end shares the start's century, unless that would run backwards.
  let end = match[2].length === 4 ? Number(match[2]) : Math.floor(start / 100) * 100 + Number(match[2]);
  if (end < start) end += 100;
  return { start, end };
}

/**
 * The case studies newest first: the order of the /work/ index, and of the
 * next-story band, which wraps from the last back to the first. Newest means
 * the latest end year, then the latest start year. A tie keeps stream order.
 */
function workOrder(items, pages) {
  return items
    .filter((item) => item.type === 'case-study')
    .map((item, i) => ({ item, i, ...yearSpan(pages.get(item.caseStudy.slug).facts[1]) }))
    .sort((a, b) => b.end - a.end || b.start - a.start || a.i - b.i)
    .map(({ item }) => item);
}

// ---- Checking the content ------------------------------------------------

/**
 * Checks every item and returns { errors, warnings }. Errors stop the build.
 * Warnings are gaps worth knowing about, such as a real item with no note.
 * `pages` collects the parsed case-study pages for the render step.
 */
function check(items, pages) {
  const errors = [];
  const warnings = [];
  if (!Array.isArray(items)) {
    errors.push(`${STREAM_FILE} must be an array of items`);
    return { errors, warnings };
  }

  const themes = read('style.css');
  const index = new Map();
  const stacks = new Map();

  items.forEach((item, i) => {
    const at = `${STREAM_FILE} item ${i + 1}${isObject(item) && item.id ? ` (${item.id})` : ''}`;
    const fail = (message) => errors.push(`${at}: ${message}`);
    const warn = (message) => warnings.push(`${at}: ${message}`);
    if (!isObject(item)) return fail('is not an object');
    const real = item.placeholder !== true;

    for (const key of Object.keys(item)) if (!ITEM_KEYS.includes(key)) fail(`unknown field "${key}"`);

    if (typeof item.id !== 'string' || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(item.id)) {
      fail('id must be lowercase words joined by hyphens');
    } else if (item.id.startsWith('fig-')) {
      fail('ids starting with "fig-" are kept for figure anchors');
    } else if (index.has(item.id)) {
      fail(`id is already used by item ${index.get(item.id) + 1}`);
    } else {
      index.set(item.id, i);
    }

    if (!TYPES[item.type]) fail(`type must be one of ${Object.keys(TYPES).join(', ')}`);
    if (!isText(item.title)) fail('needs a title');
    if (item.note !== undefined && typeof item.note !== 'string') fail('note must be text');
    if (real && !isText(item.note)) warn('has no note yet');
    if (!isText(item.project)) fail('needs a project');
    if (!INDUSTRIES.includes(item.industry)) fail(`industry must be one of ${INDUSTRIES.join(', ')}`);
    if (item.platform !== undefined && !PLATFORMS.includes(item.platform)) fail(`platform must be one of ${PLATFORMS.join(', ')}`);
    if (item.shared !== undefined && !/^\d{4}-(0[1-9]|1[0-2])$/.test(item.shared)) fail('shared must be a month, as YYYY-MM');
    if (real && item.shared === undefined) fail('needs a shared month');
    if (item.placeholder !== undefined && typeof item.placeholder !== 'boolean') fail('placeholder must be true or false');

    // Media: an image or poster, an ink tile for tools, or nothing yet.
    const media = item.media ?? {};
    if (item.media !== undefined && !isObject(item.media)) fail('media must be an object');
    for (const key of Object.keys(media)) if (!MEDIA_KEYS.includes(key)) fail(`unknown media field "${key}"`);
    if (media.src !== undefined) {
      if (!isText(item.alt)) fail('an image needs alt text');
      if (!Number.isInteger(media.width) || !Number.isInteger(media.height)) fail('media needs a whole-number width and height');
      if (!exists(media.src)) {
        if (real) fail(`media file ${media.src} does not exist`);
      } else {
        const size = imageSize(media.src);
        if (!size) fail(`cannot read the size of ${media.src}`);
        else if (size.width !== media.width || size.height !== media.height) {
          fail(`media is ${size.width} × ${size.height}, not ${media.width} × ${media.height}`);
        } else if (real && !findAvifs(media.src).length) {
          warn(`${media.src} has no AVIF derivatives`);
        }
        // srcset trusts the width in each file name, so check it.
        for (const avif of findAvifs(media.src)) {
          const actual = imageSize(avif.path);
          if (actual && actual.width !== avif.width) warn(`${avif.path} is ${actual.width}px wide, not ${avif.width}px as named`);
        }
      }
    }
    if (media.tile !== undefined && (item.type !== 'tool' || !isText(media.tile))) fail('only tools take a tile, and it needs its kicker text');
    if (media.duration !== undefined && !/^\d+:\d{2}$/.test(media.duration)) fail('duration must look like 2:02');
    if (media.video !== undefined && !exists(media.video) && real) fail(`video file ${media.video} does not exist`);
    if (real) {
      if (media.src === undefined && media.tile === undefined) fail('needs media, or placeholder: true');
      if (['video', 'reel'].includes(item.type) && (!media.video || !media.duration)) fail('a video needs its file and duration');
    }

    // Links: full is a page on this site, external leaves it.
    const links = item.links ?? {};
    if (item.links !== undefined && !isObject(item.links)) fail('links must be an object');
    for (const key of Object.keys(links)) if (!['full', 'external'].includes(key)) fail(`unknown links field "${key}"`);
    if (links.full !== undefined && !(typeof links.full === 'string' && links.full.startsWith('/'))) fail('links.full must be a path on this site, starting with /');
    if (links.external !== undefined) {
      if (!isObject(links.external) || !/^https:\/\//.test(links.external.href ?? '') || !isText(links.external.label)) {
        fail('links.external needs an https href and a label');
      }
    }
    if (item.type === 'post' && real && !links.full?.startsWith('/writing/')) fail('a post needs links.full under /writing/');

    if (item.facts !== undefined && !(Array.isArray(item.facts) && item.facts.every((f) => isObject(f) && isText(f.label) && isText(f.value)))) {
      fail('facts must be a list of { label, value }');
    }
    if (item.steps !== undefined && (item.type !== 'prototype' || !Array.isArray(item.steps) || !item.steps.every(isText))) {
      fail('steps are a list of text, for prototypes only');
    }
    if (item.related !== undefined && !(Array.isArray(item.related) && item.related.every((id) => typeof id === 'string'))) {
      fail('related must be a list of item ids');
    }

    // Case studies. A stack is the case study itself; anything else names the
    // case study it belongs to, and optionally the figure it is on the page.
    if (item.caseStudy !== undefined) {
      const cs = item.caseStudy;
      if (!isObject(cs) || !/^[a-z0-9-]+$/.test(cs.slug ?? '')) fail('caseStudy needs a slug');
      else if (Object.keys(cs).some((key) => !['slug', 'figure'].includes(key))) fail('caseStudy takes only slug and figure');
    }
    if (item.type === 'case-study') {
      if (!item.caseStudy) fail('a case study needs caseStudy.slug');
      else if (item.caseStudy.figure) fail('a case study has no figure of its own');
      else if (stacks.has(item.caseStudy.slug)) fail(`${item.caseStudy.slug} already has a case-study item`);
      else stacks.set(item.caseStudy.slug, item);
      if (typeof item.theme !== 'string' || !new RegExp(`\\.theme-${item.theme}\\s*\\{`).test(themes)) {
        fail('a case study needs a theme that style.css defines, such as "conservis"');
      }
    } else if (item.theme !== undefined) {
      fail('only case-study items take a theme');
    }
  });
  if (errors.length) return { errors, warnings };

  // Second pass: references between items, and the case-study pages.
  for (const [slug] of stacks) {
    const page = readCaseStudyPage(slug);
    if (page.error) errors.push(page.error);
    else pages.set(slug, page);
  }

  items.forEach((item, i) => {
    const at = `${STREAM_FILE} item ${i + 1} (${item.id})`;
    for (const id of item.related ?? []) {
      if (id === item.id) errors.push(`${at}: lists itself as related`);
      else if (!index.has(id)) errors.push(`${at}: related item "${id}" does not exist`);
    }
    if (new Set(item.related ?? []).size !== (item.related ?? []).length) errors.push(`${at}: repeats a related item`);

    if (!item.caseStudy) return;
    const { slug, figure } = item.caseStudy;
    const stack = stacks.get(slug);
    if (!stack) {
      errors.push(`${at}: no case-study item has the slug "${slug}"`);
      return;
    }
    if (item.project !== stack.project) errors.push(`${at}: project must match its case study, "${stack.project}"`);
    if (item.industry !== stack.industry) errors.push(`${at}: industry must match its case study, "${stack.industry}"`);
    const page = pages.get(slug);
    if (figure && page && !page.figures.some((f) => f.id === figure)) {
      errors.push(`${at}: work/${slug}.html has no figure with the image "${figure}"`);
    }

    // The order is set by hand, but a stack beside its own screens is a clump.
    const next = items[i + 1];
    if (next?.caseStudy?.slug === slug) {
      warnings.push(`${at}: sits beside ${next.id}, from the same case study`);
    }
  });

  // The Work pages order case studies by the years on each page.
  for (const [slug, page] of pages) {
    if (!yearSpan(page.facts[1])) {
      errors.push(`work/${slug}.html: its second fact, "${page.facts[1]}", needs to end with a year or a range such as 2016–21`);
    }
  }

  if (!items.slice(0, FIRST_ROW).some((item) => item.type === 'case-study')) {
    errors.push(`${STREAM_FILE}: the first ${FIRST_ROW} items must include a case study, so the colour chip is explained early`);
  }

  // Figure anchors arrive with Phase 2C. Until then, say so once, not per figure.
  const unanchored = [...pages].filter(([, page]) => page.figures.some((f) => f.anchor === null)).map(([slug]) => slug);
  if (unanchored.length) {
    warnings.push(`figure anchors (id="fig-<image>") are missing on work/${unanchored.join(', ')}; Phase 2C adds them`);
  }
  for (const [slug, page] of pages) {
    for (const f of page.figures) {
      if (f.anchor !== null && f.anchor !== `fig-${f.id}`) {
        errors.push(`work/${slug}.html: the figure for ${f.id} has id="${f.anchor}", expected "fig-${f.id}"`);
      }
    }
  }

  return { errors, warnings };
}

// ---- Resolving items for output ------------------------------------------

/**
 * Adds everything rendering needs: the canonical link, resolved media, and
 * the case study's colour and place. The item's own fields stay as written.
 */
function resolve(items, pages) {
  const stacks = new Map(items.filter((i) => i.type === 'case-study').map((i) => [i.caseStudy.slug, i]));

  return items.map((item) => {
    const media = item.media ?? {};
    const resolved = { ...item, note: item.note ?? '', typeLabel: TYPES[item.type].label };

    let caseStudy = null;
    if (item.caseStudy) {
      const { slug, figure } = item.caseStudy;
      const page = pages.get(slug);
      const position = figure ? page.figures.findIndex((f) => f.id === figure) + 1 : 0;
      caseStudy = {
        slug,
        figure: figure ?? null,
        position,
        total: page.figures.length,
        theme: stacks.get(slug).theme,
        dates: page.facts[1],
      };
    }
    resolved.caseStudy = caseStudy;
    resolved.projectKey = caseStudy ? caseStudy.slug : slugify(item.project);

    // The canonical URL: where the item lives without JavaScript.
    if (item.type === 'case-study') resolved.href = `/work/${caseStudy.slug}`;
    else if (caseStudy?.figure) resolved.href = `/work/${caseStudy.slug}#fig-${caseStudy.figure}`;
    else if (item.type === 'post' && item.links?.full) resolved.href = item.links.full;
    else resolved.href = `/#${item.id}`;

    // The page that shows the item in full, when there is one.
    resolved.full = caseStudy ? `/work/${caseStudy.slug}` : item.links?.full ?? null;
    resolved.external = item.links?.external ?? null;

    if (media.src && exists(media.src)) {
      const avifs = findAvifs(media.src);
      resolved.image = {
        src: url(media.src),
        width: media.width,
        height: media.height,
        shape: shapeOf(media.width, media.height),
        avif: avifs.map((a) => `${url(a.path)} ${a.width}w`).join(', '),
      };
    } else {
      resolved.image = null;
    }
    resolved.tile = media.tile ?? null;
    resolved.video = media.video ? url(media.video) : null;
    resolved.duration = media.duration ?? null;
    return resolved;
  });
}

// ---- Markup --------------------------------------------------------------

const indent = (lines, by) => lines.map((line) => (line ? `${' '.repeat(by)}${line}` : line));

/** The <article> attributes both views share. */
function articleOpen(item, block) {
  const classes = [block];
  // The theme class sets --case-dark, --case-hover, --paper, and --ink to the
  // project's colours, for the chip, the stack, and the List rule.
  if (item.caseStudy) classes.push(`theme-${item.caseStudy.theme}`);
  const attrs = [
    ['class', classes.join(' ')],
    ['id', item.id],
    ['data-type', item.type],
    ['data-project', item.projectKey],
    ['data-industry', slugify(item.industry)],
  ];
  if (item.caseStudy) attrs.push(['data-case-study', item.caseStudy.slug]);
  if (item.placeholder) attrs.push(['data-placeholder', null]);
  return `<article${attrs.map(([k, v]) => (v === null ? ` ${k}` : ` ${k}="${esc(v)}"`)).join('')}>`;
}

/** The image, tile, or empty frame, with any badge and running time. */
function mediaLines(item, block, sizes, eager) {
  const extras = [];
  if (item.type === 'prototype') extras.push(`<span class="${block}__badge" aria-hidden="true">Try it</span>`);
  if (item.type === 'reel') extras.push(`<span class="${block}__badge" aria-hidden="true">Reel</span>`);
  if (item.duration) {
    extras.push(`<span class="${block}__time" id="${item.id}-time"><span class="visually-hidden">Running time </span>${esc(item.duration)}</span>`);
  }

  if (item.tile) {
    // The tile repeats the title as artwork, so it stays out of the reading order.
    return [
      `<div class="${block}__media ${block}__media--tile" aria-hidden="true">`,
      `  <span class="${block}__kicker">${esc(item.tile)}</span>`,
      `  <span class="${block}__tile-title">${esc(item.title)}</span>`,
      '</div>',
    ];
  }
  if (!item.image) {
    // Nothing to show yet: an empty frame in the shape the media will take.
    const open = `<div class="${block}__media ${block}__media--empty" data-shape="${item.type === 'reel' ? 'tall' : 'wide'}">`;
    return extras.length ? [open, ...indent(extras, 2), '</div>'] : [`${open}</div>`];
  }

  const { image } = item;
  const img = `<img src="${esc(image.src)}" width="${image.width}" height="${image.height}" alt="${esc(item.alt)}" loading="${eager ? 'eager' : 'lazy'}" decoding="async">`;
  const picture = image.avif
    ? ['<picture>', `  <source type="image/avif" srcset="${esc(image.avif)}" sizes="${esc(sizes)}">`, `  ${img}`, '</picture>']
    : [img];
  return [`<div class="${block}__media" data-shape="${image.shape}">`, ...indent([...picture, ...extras], 2), '</div>'];
}

/**
 * The meta line. Case-study items show the colour chip and the project;
 * everything else shows its industry. Posts show the year they were shared,
 * and a stack shows how many screens its case study holds.
 */
function metaHtml(item, block) {
  const type = `<span class="${block}__type">${esc(item.typeLabel)}</span>`;
  const dot = '<span aria-hidden="true"> · </span>';
  const chip = `<span class="${block}__chip" aria-hidden="true"></span>`;
  if (item.type === 'case-study') {
    const count = `${item.caseStudy.total} screen${item.caseStudy.total === 1 ? '' : 's'}`;
    return `<span class="${block}__case">${chip}${type}${dot}${count}</span>`;
  }
  if (item.caseStudy) {
    // Read aloud as "Screen from the Conservis case study".
    return `${type} <span class="${block}__case">${chip}<span class="visually-hidden">from the </span>${esc(item.project)}<span class="visually-hidden"> case study</span></span>`;
  }
  if (item.type === 'post') {
    // A List row carries the year in its dateline, so it is not repeated here.
    return block === 'stream-row' || !item.shared ? type : `${type}${dot}${year(item.shared)}`;
  }
  return `${type}${dot}${esc(item.industry)}`;
}

/** A Grid card: one link wraps the media, the title, and the meta line. */
function renderCard(item, { heading, eager }) {
  const labelledBy = [`${item.id}-title`, `${item.id}-meta`];
  if (item.duration) labelledBy.push(`${item.id}-time`);
  return [
    articleOpen(item, 'stream-card'),
    `  <a class="stream-card__link" href="${esc(item.href)}" data-open="${item.id}" aria-labelledby="${labelledBy.join(' ')}">`,
    ...indent(mediaLines(item, 'stream-card', SIZES.grid, eager), 4),
    `    <h${heading} class="stream-card__title" id="${item.id}-title">${esc(item.title)}</h${heading}>`,
    `    <p class="stream-card__meta micro" id="${item.id}-meta">${metaHtml(item, 'stream-card')}</p>`,
    '  </a>',
    '</article>',
  ];
}

/** The right-hand label on a List row's meta line. */
function dateline(item) {
  if (item.type === 'case-study') return item.caseStudy.dates;
  if (item.caseStudy) return item.caseStudy.dates.split(' · ').pop();
  if (item.type === 'tool' || item.type === 'post') return year(item.shared);
  return item.platform ?? year(item.shared);
}

/**
 * A List row. The note and the extra links sit beside the image, so the row
 * cannot be one link. The title link stretches over the row instead, and the
 * extra links sit above it.
 */
function renderRow(item, { heading, eager }) {
  const hint = item.caseStudy && item.type === 'screen' ? 'Open the case study here' : TYPES[item.type].hint;
  const actions = [`<span class="stream-row__hint" aria-hidden="true">${hint} ↓</span>`];
  if (item.type === 'case-study') {
    actions.push(`<a class="stream-row__action" href="${esc(item.full)}">Full case study <span aria-hidden="true">→</span></a>`);
  }
  if (item.external) {
    actions.push(`<a class="stream-row__action" href="${esc(item.external.href)}">${esc(item.external.label)} <span aria-hidden="true">↗</span></a>`);
  }
  const when = dateline(item);
  return [
    articleOpen(item, 'stream-row'),
    ...indent(mediaLines(item, 'stream-row', SIZES.list, eager), 2),
    '  <div class="stream-row__body">',
    `    <p class="stream-row__meta micro"><span class="stream-row__kind">${metaHtml(item, 'stream-row')}</span>${when ? `<span class="stream-row__dateline">${esc(when)}</span>` : ''}</p>`,
    `    <h${heading} class="stream-row__title"><a class="stream-row__link" href="${esc(item.href)}" data-open="${item.id}">${esc(item.title)}</a></h${heading}>`,
    ...(item.note ? [`    <p class="stream-row__note">${esc(item.note)}</p>`] : []),
    `    <p class="stream-row__actions micro">${actions.join(' ')}</p>`,
    '  </div>',
    '</article>',
  ];
}

// ---- The JSON island -----------------------------------------------------

// Drops empty values so each record only says what it has.
function compact(record) {
  const empty = (v) => v === null || v === undefined || v === ''
    || (Array.isArray(v) && !v.length)
    || (isObject(v) && !Object.keys(v).length);
  return Object.fromEntries(Object.entries(record).filter(([, v]) => !empty(v)));
}

function islandItem(item) {
  return compact({
    type: item.type,
    title: item.title,
    note: item.note,
    href: item.href,
    project: item.project,
    industry: item.industry,
    platform: item.platform,
    shared: item.shared,
    caseStudy: item.caseStudy && compact({
      slug: item.caseStudy.slug,
      figure: item.caseStudy.figure,
      position: item.caseStudy.position || null,
      total: item.caseStudy.total,
    }),
    media: compact({
      src: item.image?.src,
      width: item.image?.width,
      height: item.image?.height,
      alt: item.image ? item.alt : null,
      avif: item.image?.avif,
      tile: item.tile,
      video: item.video,
      duration: item.duration,
    }),
    links: compact({ full: item.full, external: item.external }),
    related: item.related,
    facts: item.facts,
    steps: item.steps,
    placeholder: item.placeholder || null,
  });
}

function islandCaseStudy(slug, stack, page) {
  return {
    title: stack.title,
    theme: stack.theme,
    href: `/work/${slug}`,
    premise: page.premise,
    facts: page.facts,
    note: page.note,
    // Captions are HTML from the page, since some carry links.
    figures: page.figures.map((f) => compact({
      id: f.id,
      anchor: `fig-${f.id}`,
      src: f.src,
      width: f.width,
      height: f.height,
      alt: f.alt,
      avif: f.avif,
      caption: f.caption,
      group: f.group,
    })),
  };
}

/**
 * The island holds a record for every item on the page, plus anything those
 * items list as related, plus each case study they belong to. One line per
 * record keeps diffs readable. "<", ">", and "&" are escaped so the JSON can
 * never close its own script element.
 */
function renderIsland(shown, all, pages) {
  const byId = new Map(all.map((item) => [item.id, item]));
  const wanted = new Set(shown.map((item) => item.id));
  for (const item of shown) for (const id of item.related ?? []) wanted.add(id);
  const records = all.filter((item) => wanted.has(item.id));
  const slugs = [...new Set(records.filter((item) => item.caseStudy).map((item) => item.caseStudy.slug))];
  const stackOf = (slug) => all.find((item) => item.type === 'case-study' && item.caseStudy.slug === slug);

  const json = (value) => JSON.stringify(value).replace(/</g, '\\u003c').replace(/>/g, '\\u003e').replace(/&/g, '\\u0026');
  const entries = (pairs) => pairs.map(([key, value], i) => `${json(key)}:${json(value)}${i < pairs.length - 1 ? ',' : ''}`);
  return [
    '<script type="application/json" id="stream-data">',
    '{"items":{',
    ...entries(records.map((item) => [item.id, islandItem(byId.get(item.id))])),
    '},"caseStudies":{',
    ...entries(slugs.map((slug) => [slug, islandCaseStudy(slug, stackOf(slug), pages.get(slug))])),
    '}}',
    '</script>',
  ];
}

// ---- The Work pages ------------------------------------------------------

/**
 * The /work/ index: one row per case study, newest first. The whole row is
 * one link, named by its title and described by its premise. The cover is
 * the page's first figure, drawn as a stack in the project's colour, and it
 * stays out of the reading order since the title already names it.
 */
function renderWorkIndex(order, pages) {
  return order.flatMap((stack, i) => {
    const slug = stack.caseStudy.slug;
    const page = pages.get(slug);
    const cover = page.figures[0];
    const id = `work-${slug}`;
    const priority = i === 0 ? ' fetchpriority="high"' : '';
    const img = `<img src="${esc(cover.src)}" width="${cover.width}" height="${cover.height}" alt="" loading="${i < 2 ? 'eager' : 'lazy'}"${priority} decoding="async">`;
    const picture = cover.avif
      ? ['<picture>', `  <source type="image/avif" srcset="${esc(cover.avif)}" sizes="${COVER_SIZES}">`, `  ${img}`, '</picture>']
      : [img];
    const [role, dates] = page.facts;
    return [
      ...(i ? [''] : []),
      `<li class="entry entry--case theme-${stack.theme}">`,
      `  <a class="entry__link" href="/work/${slug}" aria-labelledby="${id}-title" aria-describedby="${id}-premise">`,
      '    <div class="entry__cover" aria-hidden="true">',
      ...indent(picture, 6),
      '    </div>',
      '    <div class="entry__body">',
      `      <h2 class="entry__title" id="${id}-title">${esc(stack.title)}</h2>`,
      `      <p class="entry__dek" id="${id}-premise">${esc(page.premise)}</p>`,
      `      <p class="entry__meta micro"><span class="entry__dateline">${esc(dates)}</span> <span class="entry__detail">${esc(role)}</span></p>`,
      '    </div>',
      '    <p class="entry__cta micro">Read the case study <span aria-hidden="true">→</span></p>',
      '  </a>',
      '</li>',
    ];
  });
}

/**
 * The band that ends a case-study page. It only moves forward: it names the
 * next case study in /work/ order, wrapping from the last to the first, and
 * carries no other link. The theme class gives it the destination's colours.
 */
function renderNextStory(slug, order, file) {
  const at = order.findIndex((stack) => stack.caseStudy.slug === slug);
  if (at < 0) throw new Error(`${file}: next-story case-study="${slug}" matches no case study in the stream`);
  const next = order[(at + 1) % order.length];
  return [
    `<nav class="next-story theme-${next.theme}" aria-label="Next case study">`,
    `  <a class="next-story__link" href="/work/${next.caseStudy.slug}">`,
    `    <span class="next-story__name">${esc(next.title)}</span>`,
    '    <span class="next-story__arrow" aria-hidden="true">→</span>',
    '  </a>',
    '</nav>',
  ];
}

// ---- Filling pages -------------------------------------------------------

const REGION = /^([ \t]*)<!-- stream:start((?:\s+[a-z-]+="[^"]*")*)\s*-->[\s\S]*?^[ \t]*<!-- stream:end -->/gm;
const ISLAND = /^([ \t]*)<!-- stream-data:start -->[\s\S]*?^[ \t]*<!-- stream-data:end -->/m;
const WORK_INDEX = /^([ \t]*)<!-- work-index:start -->[\s\S]*?^[ \t]*<!-- work-index:end -->/gm;
const NEXT_STORY = /^([ \t]*)<!-- next-story:start case-study="([a-z0-9-]+)" -->[\s\S]*?^[ \t]*<!-- next-story:end -->/gm;

function regionOptions(text, file) {
  const options = { view: 'grid', caseStudy: null, heading: 2, eager: 0 };
  for (const [, name, value] of text.matchAll(/([a-z-]+)="([^"]*)"/g)) {
    if (name === 'view' && ['grid', 'list'].includes(value)) options.view = value;
    else if (name === 'case-study' && value) options.caseStudy = value;
    else if (name === 'heading' && /^[2-6]$/.test(value)) options.heading = Number(value);
    else if (name === 'eager' && /^\d+$/.test(value)) options.eager = Number(value);
    else throw new Error(`${file}: stream:start has an unknown setting ${name}="${value}"`);
  }
  return options;
}

/**
 * Which items a region shows. A case-study region is "More from": what the
 * project shares, less its own stack and the screens already on its page.
 */
function regionItems(items, options, file) {
  if (!options.caseStudy) return items;
  if (!items.some((item) => item.type === 'case-study' && item.caseStudy.slug === options.caseStudy)) {
    throw new Error(`${file}: case-study="${options.caseStudy}" matches no case study in the stream`);
  }
  return items.filter((item) => item.caseStudy?.slug === options.caseStudy && item.type !== 'case-study' && !item.caseStudy.figure);
}

/** Returns the page with every region and the island regenerated. */
function buildPage(file, items, pages, order) {
  const html = read(file);
  const count = (marker) => (html.match(new RegExp(`<!-- ${marker}`, 'g')) ?? []).length;
  for (const kind of ['stream', 'work-index', 'next-story']) {
    if (count(`${kind}:start`) !== count(`${kind}:end -->`)) {
      throw new Error(`${file}: has ${count(`${kind}:start`)} ${kind}:start and ${count(`${kind}:end -->`)} ${kind}:end markers`);
    }
  }
  const starts = count('stream:start');
  if (!starts && !count('work-index:start') && !count('next-story:start')) {
    throw new Error(`${file}: has no generated regions; remove it from PAGES or add one`);
  }
  if (starts && !ISLAND.test(html)) throw new Error(`${file}: has stream regions but no stream-data markers for the island`);

  const shown = [];
  let regions = 0;
  let out = html.replace(REGION, (match, space, settings) => {
    regions += 1;
    const options = regionOptions(settings, file);
    const list = regionItems(items, options, file);
    const render = options.view === 'list' ? renderRow : renderCard;
    const lines = list.flatMap((item, i) => [
      ...(i ? [''] : []),
      ...render(item, { heading: options.heading, eager: i < options.eager }),
    ]);
    checkContract(lines.join('\n'), list, options.view, file);
    shown.push(...list);
    return [`${space}<!-- stream:start${settings} -->`, ...indent(lines, space.length), `${space}<!-- stream:end -->`].join('\n');
  });
  if (regions !== starts) throw new Error(`${file}: a stream:start marker could not be read`);

  const ids = shown.map((item) => item.id);
  const repeated = ids.find((id, i) => ids.indexOf(id) !== i);
  if (repeated) throw new Error(`${file}: ${repeated} appears in more than one region, which would repeat its id`);

  if (starts) {
    out = out.replace(ISLAND, (match, space) => [
      `${space}<!-- stream-data:start -->`,
      ...indent(renderIsland(shown, items, pages), space.length),
      `${space}<!-- stream-data:end -->`,
    ].join('\n'));
  }

  out = out.replace(WORK_INDEX, (match, space) => [
    `${space}<!-- work-index:start -->`,
    ...indent(renderWorkIndex(order, pages), space.length),
    `${space}<!-- work-index:end -->`,
  ].join('\n'));
  out = out.replace(NEXT_STORY, (match, space, slug) => [
    `${space}<!-- next-story:start case-study="${slug}" -->`,
    ...indent(renderNextStory(slug, order, file), space.length),
    `${space}<!-- next-story:end -->`,
  ].join('\n'));
  return out;
}

// ---- The card contract ---------------------------------------------------

/**
 * Re-reads the markup just rendered and checks it against the card contract
 * in specs/redesign.md. A failure here is a bug in this script, not in the
 * content, so it names the rule that broke.
 */
function checkContract(html, list, view, file) {
  const block = view === 'list' ? 'stream-row' : 'stream-card';
  const articles = [...html.matchAll(/<article ([^>]*)>([\s\S]*?)<\/article>/g)];
  const fail = (item, rule) => { throw new Error(`${file}: ${item.id} breaks the card contract: ${rule}`); };
  if (articles.length !== list.length) throw new Error(`${file}: rendered ${articles.length} ${block}s for ${list.length} items`);

  articles.forEach(([, open, body], i) => {
    const item = list[i];
    const a = attributes(open);
    if (a.class.split(' ')[0] !== block) fail(item, `the article's first class is ${block}`);
    if (a.id !== item.id) fail(item, 'the article id is the item id');
    for (const name of ['data-type', 'data-project', 'data-industry']) if (!a[name]) fail(item, `the article has ${name}`);
    if (('data-case-study' in a) !== Boolean(item.caseStudy)) fail(item, 'data-case-study is present only for case-study items');

    const links = [...body.matchAll(new RegExp(`<a class="${block}__link"([^>]*)>`, 'g'))];
    if (links.length !== 1) fail(item, `there is exactly one ${block}__link`);
    const link = attributes(links[0][1]);
    if (link.href !== esc(item.href) || link['data-open'] !== item.id) fail(item, 'the link has the canonical href and data-open set to the item id');

    if (view === 'grid') {
      // One link wraps everything, so there can be no second link inside.
      if ((body.match(/<a /g) ?? []).length !== 1) fail(item, 'the card holds no other link');
      const inside = body.slice(body.indexOf('<a '), body.lastIndexOf('</a>'));
      for (const part of ['__media', '__title', '__meta']) if (!inside.includes(`${block}${part}`)) fail(item, `the link wraps the ${part.slice(2)}`);
    }
    if (item.image && !/<img [^>]*alt="[^"]+"/.test(body)) fail(item, 'images carry alt text');
    if (item.caseStudy && !body.includes(`${block}__chip`)) fail(item, 'case-study items show the colour chip');
  });
}

// ---- Main ----------------------------------------------------------------

function main() {
  const checkOnly = process.argv.includes('--check');
  const unknown = process.argv.slice(2).filter((arg) => arg !== '--check');
  if (unknown.length) {
    console.error(`Unknown option ${unknown[0]}. Use no options to write, or --check.`);
    return 2;
  }

  let items;
  try {
    items = JSON.parse(read(STREAM_FILE));
  } catch (error) {
    console.error(`${STREAM_FILE}: ${error.message}`);
    return 1;
  }

  const pages = new Map();
  const { errors, warnings } = check(items, pages);
  for (const warning of warnings) console.warn(`warning: ${warning}`);
  if (errors.length) {
    for (const error of errors) console.error(`error: ${error}`);
    console.error(`${errors.length} error${errors.length === 1 ? '' : 's'}; nothing was written.`);
    return 1;
  }

  const resolved = resolve(items, pages);
  const order = workOrder(items, pages);
  const placeholders = resolved.filter((item) => item.placeholder).length;
  console.log(`${resolved.length} items: ${resolved.length - placeholders} ready, ${placeholders} placeholders.`);

  let stale = 0;
  for (const file of PAGES) {
    let next;
    try {
      next = buildPage(file, resolved, pages, order);
    } catch (error) {
      console.error(`error: ${error.message}`);
      return 1;
    }
    const current = read(file);
    if (next === current) {
      console.log(`up to date  ${file}`);
    } else if (checkOnly) {
      console.error(`stale       ${file}`);
      stale += 1;
    } else {
      writeFileSync(join(ROOT, file), next);
      console.log(`wrote       ${file}`);
    }
  }
  if (stale) {
    console.error(`${stale} page${stale === 1 ? ' is' : 's are'} out of date. Run: node scripts/build-stream.mjs`);
    return 1;
  }
  return 0;
}

process.exitCode = main();
