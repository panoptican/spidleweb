document.documentElement.classList.add('feed-enhanced');

const feedPage = document.querySelector('[data-feed-page]');
const cards = [...document.querySelectorAll('[data-feed-card]')];
const filters = document.querySelector('[data-feed-filters]');
const emptyState = document.querySelector('[data-feed-empty]');
const dialog = document.querySelector('[data-feed-dialog]');
const dialogMedia = dialog?.querySelector('[data-dialog-media]');
const dialogTitle = dialog?.querySelector('[data-dialog-title]');
const dialogKind = dialog?.querySelector('[data-dialog-kind]');
const dialogCount = dialog?.querySelector('[data-dialog-count]');
const previousButton = dialog?.querySelector('[data-dialog-previous]');
const nextButton = dialog?.querySelector('[data-dialog-next]');

function itemSlides(card) {
  const template = card.querySelector('template[data-feed-slides]');
  if (template) return [...template.content.querySelectorAll('[data-feed-slide] picture')];
  const picture = card.querySelector('.feed-card__media picture');
  return picture ? [picture] : [];
}

const items = cards.map((card) => {
  const link = card.querySelector('[data-feed-action]');
  const action = link?.dataset.feedAction;
  return {
    action,
    card,
    kind: card.dataset.kind,
    link,
    slug: card.id,
    slides: action === 'viewer' ? itemSlides(card) : [],
    title: card.querySelector('h2').textContent
  };
});
const viewerItems = items.filter((item) => item.action === 'viewer' && item.slides.length);
const itemBySlug = new Map(viewerItems.map((item) => [item.slug, item]));
const filterNames = {
  all: 'All',
  agriculture: 'Agriculture',
  finance: 'Finance',
  healthcare: 'Healthcare',
  'home-services': 'Home services',
  manufacturing: 'Manufacturing',
  posts: 'Writing',
  productivity: 'Productivity',
  prototypes: 'Prototypes',
  screens: 'Screens',
  sports: 'Sports',
  tools: 'Tools',
  websites: 'Websites'
};
let currentItem = null;
let currentSlide = 0;
let dialogOpener = null;

if ('scrollRestoration' in history) history.scrollRestoration = 'manual';

function filterStateFromUrl() {
  const params = new URLSearchParams(location.search);
  return {
    type: filterNames[params.get('type')] ? params.get('type') : 'all',
    industry: filterNames[params.get('industry')] ? params.get('industry') : 'all'
  };
}

function scrollKey() {
  return `spidleweb-feed-scroll:${location.pathname}${location.search}`;
}

function saveScroll() {
  sessionStorage.setItem(scrollKey(), String(window.scrollY));
}

function restoreScroll() {
  const saved = Number(sessionStorage.getItem(scrollKey()));
  if (!Number.isFinite(saved) || saved <= 0) return;
  const restore = () => window.scrollTo(0, saved);
  restore();
  requestAnimationFrame(() => requestAnimationFrame(restore));
}

function updateFilterControls(state) {
  filters.querySelectorAll('[data-filter]').forEach((group) => {
    const name = group.dataset.filter;
    const value = state[name];
    group.querySelector('[data-filter-label]').textContent = filterNames[value];
    group.querySelectorAll('[data-filter-value]').forEach((button) => {
      button.setAttribute('aria-pressed', String(button.dataset.filterValue === value));
    });
  });
}

function applyFilters(state = filterStateFromUrl()) {
  let visible = 0;
  cards.forEach((card) => {
    const matchesType = state.type === 'all' || card.dataset.type === state.type;
    const matchesIndustry = state.industry === 'all' || card.dataset.industry === state.industry;
    card.hidden = !(matchesType && matchesIndustry);
    if (!card.hidden) visible += 1;
  });
  emptyState.hidden = visible !== 0;
  updateFilterControls(state);
}

function updateFilter(name, value) {
  saveScroll();
  const params = new URLSearchParams(location.search);
  if (value === 'all') params.delete(name);
  else params.set(name, value);
  const query = params.toString();
  history.pushState({}, '', `${location.pathname}${query ? `?${query}` : ''}${location.hash}`);
  applyFilters();
  saveScroll();
}

function updateCounts() {
  filters.querySelectorAll('[data-filter]').forEach((group) => {
    const name = group.dataset.filter;
    group.querySelectorAll('[data-filter-value]').forEach((button) => {
      const value = button.dataset.filterValue;
      const count = value === 'all' ? cards.length :
        cards.filter((card) => card.dataset[name] === value).length;
      button.querySelector('[data-filter-count]').textContent = count;
    });
  });
}

function itemHash(item) {
  return `#${item.slug}`;
}

function viewerSizes(isLong) {
  if (isLong) return '(max-width: 639px) calc(100vw - 112px), min(780px, calc(100vw - 176px))';
  return '(max-width: 639px) calc(100vw - 112px), min(1080px, calc(100vw - 176px))';
}

function setSlide(nextIndex) {
  if (!currentItem) return;
  const total = currentItem.slides.length;
  currentSlide = (nextIndex + total) % total;
  const picture = currentItem.slides[currentSlide].cloneNode(true);
  const image = picture.querySelector('img');
  const isLong = Number(image.getAttribute('height')) / Number(image.getAttribute('width')) > 2;
  picture.querySelectorAll('source').forEach((source) => {
    source.sizes = viewerSizes(isLong);
  });
  image.loading = 'eager';
  image.removeAttribute('fetchpriority');
  dialog.dataset.orientation = isLong ? 'long' : 'standard';
  dialogMedia.replaceChildren(picture);
  dialogMedia.scrollTop = 0;
  dialogCount.textContent = `${String(currentSlide + 1).padStart(2, '0')} / ${String(total).padStart(2, '0')}`;
  const hasGallery = total > 1;
  previousButton.hidden = !hasGallery;
  previousButton.disabled = !hasGallery;
  nextButton.hidden = !hasGallery;
  nextButton.disabled = !hasGallery;
}

function showItem(item, updateUrl = true) {
  currentItem = item;
  currentSlide = 0;
  dialogTitle.textContent = item.title;
  dialogKind.textContent = `Feed / ${item.kind}`;
  setSlide(0);
  if (updateUrl) {
    history.replaceState({ feedItem: item.slug }, '', `${location.pathname}${location.search}${itemHash(item)}`);
  }
}

function removeDialogHash() {
  if (!itemBySlug.has(location.hash.slice(1))) return;
  history.replaceState({}, '', `${location.pathname}${location.search}`);
}

function closeDialog(returnFocus = true, updateUrl = true) {
  if (dialog.open) dialog.close();
  feedPage.inert = false;
  if (updateUrl) removeDialogHash();
  if (returnFocus && dialogOpener?.isConnected) dialogOpener.focus();
  dialogOpener = null;
  currentItem = null;
}

function openDialog(item, opener = null, updateUrl = true) {
  dialogOpener = opener;
  showItem(item, updateUrl);
  if (!dialog.open) dialog.showModal();
  feedPage.inert = true;
  queueMicrotask(() => dialog.querySelector('[data-dialog-close]').focus());
}

function syncDialogToHash() {
  const item = itemBySlug.get(location.hash.slice(1));
  if (item) {
    openDialog(item, null, false);
    return;
  }
  if (dialog.open) closeDialog(false, false);
}

if (filters && cards.length) {
  filters.hidden = false;
  updateCounts();
  applyFilters();
  filters.addEventListener('click', (event) => {
    const button = event.target.closest('[data-filter-value]');
    if (!button) return;
    const group = button.closest('[data-filter]');
    updateFilter(group.dataset.filter, button.dataset.filterValue);
    group.open = false;
    group.querySelector('summary').focus();
  });
  document.addEventListener('click', (event) => {
    filters.querySelectorAll('details[open]').forEach((details) => {
      if (!details.contains(event.target)) details.open = false;
    });
  });
}

viewerItems.forEach((item) => {
  item.link.addEventListener('click', (event) => {
    if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    saveScroll();
    history.pushState({ feedItem: item.slug }, '', `${location.pathname}${location.search}${itemHash(item)}`);
    openDialog(item, item.link, false);
  });
});

document.querySelectorAll('a[href]').forEach((link) => {
  link.addEventListener('click', () => {
    if (!link.matches('[data-feed-action="viewer"], [data-dialog-close]')) saveScroll();
  });
});

dialog.querySelector('[data-dialog-close]').addEventListener('click', (event) => {
  event.preventDefault();
  closeDialog();
});
dialog.addEventListener('cancel', (event) => {
  event.preventDefault();
  closeDialog();
});
dialog.addEventListener('click', (event) => {
  if (event.target === dialog) closeDialog();
});
dialog.addEventListener('keydown', (event) => {
  if (event.key === 'Tab') {
    const focusable = [...dialog.querySelectorAll('a[href], button:not([disabled])')]
      .filter((element) => !element.hidden && element.getClientRects().length);
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }
  if (event.key === 'ArrowLeft' && currentItem?.slides.length > 1) {
    event.preventDefault();
    setSlide(currentSlide - 1);
  }
  if (event.key === 'ArrowRight' && currentItem?.slides.length > 1) {
    event.preventDefault();
    setSlide(currentSlide + 1);
  }
});
previousButton.addEventListener('click', () => setSlide(currentSlide - 1));
nextButton.addEventListener('click', () => setSlide(currentSlide + 1));

window.addEventListener('pagehide', saveScroll);
window.addEventListener('pageshow', restoreScroll);
window.addEventListener('popstate', () => {
  applyFilters();
  syncDialogToHash();
  restoreScroll();
});

const year = document.getElementById('year');
if (year) year.textContent = new Date().getFullYear();

syncDialogToHash();
restoreScroll();
