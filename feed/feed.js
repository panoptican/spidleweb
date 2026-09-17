const feedPage = document.querySelector('[data-feed-page]');
const cards = [...document.querySelectorAll('[data-feed-card]')];
const filters = document.querySelector('[data-feed-filters]');
const emptyState = document.querySelector('[data-feed-empty]');
const dialogs = new Map(
  [...document.querySelectorAll('[data-feed-dialog]')].map((dialog) => [dialog.id, dialog])
);
const filterNames = {
  all: 'All',
  agriculture: 'Agriculture',
  healthcare: 'Healthcare',
  productivity: 'Productivity',
  publishing: 'Publishing',
  screens: 'Screens',
  sports: 'Sports',
  tools: 'Tools',
  websites: 'Websites'
};
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
  if (Number.isFinite(saved) && saved > 0) {
    const restore = () => window.scrollTo(0, saved);
    restore();
    requestAnimationFrame(() => requestAnimationFrame(restore));
  }
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

function setSlide(dialog, nextIndex) {
  const slides = [...dialog.querySelectorAll('[data-dialog-slide]')];
  const index = (nextIndex + slides.length) % slides.length;
  slides.forEach((slide, slideIndex) => { slide.hidden = slideIndex !== index; });
  dialog.dataset.slide = String(index);
  dialog.querySelector('[data-dialog-count]').textContent =
    `${String(index + 1).padStart(2, '0')} / ${String(slides.length).padStart(2, '0')}`;
}

function removeDialogHash() {
  if (!dialogs.has(location.hash.slice(1))) return;
  history.replaceState({}, '', `${location.pathname}${location.search}`);
}

function closeDialog(dialog, returnFocus = true, updateUrl = true) {
  if (dialog.open) dialog.close();
  feedPage.inert = false;
  if (updateUrl) removeDialogHash();
  if (returnFocus && dialogOpener?.isConnected) dialogOpener.focus();
  dialogOpener = null;
}

function openDialog(dialog, opener = null) {
  document.querySelectorAll('[data-feed-dialog][open]').forEach((open) => {
    if (open !== dialog) closeDialog(open, false, false);
  });
  dialogOpener = opener;
  setSlide(dialog, 0);
  if (!dialog.open) dialog.showModal();
  feedPage.inert = true;
  queueMicrotask(() => dialog.querySelector('[data-dialog-close]').focus());
}

function syncDialogToHash() {
  const dialog = dialogs.get(location.hash.slice(1));
  if (dialog) {
    openDialog(dialog);
    return;
  }
  document.querySelectorAll('[data-feed-dialog][open]').forEach((open) => closeDialog(open, false, false));
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

document.querySelectorAll('[data-dialog-link]').forEach((link) => {
  link.addEventListener('click', (event) => {
    if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const dialog = dialogs.get(link.dataset.dialogLink);
    if (!dialog) return;
    event.preventDefault();
    saveScroll();
    history.pushState({ feedDialog: dialog.id }, '', `${location.pathname}${location.search}#${dialog.id}`);
    openDialog(dialog, link);
  });
});

document.querySelectorAll('a[href]').forEach((link) => {
  link.addEventListener('click', () => {
    if (!link.matches('[data-dialog-link], .feed-dialog__close')) saveScroll();
  });
});

dialogs.forEach((dialog) => {
  dialog.querySelector('[data-dialog-close]').addEventListener('click', (event) => {
    event.preventDefault();
    closeDialog(dialog);
  });
  dialog.addEventListener('cancel', (event) => {
    event.preventDefault();
    closeDialog(dialog);
  });
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog) closeDialog(dialog);
  });
  dialog.addEventListener('keydown', (event) => {
    const current = Number(dialog.dataset.slide || 0);
    if (event.key === 'Tab') {
      const focusable = [...dialog.querySelectorAll('a[href], button:not([disabled])')]
        .filter((element) => !element.closest('[hidden]'));
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
    if (event.key === 'ArrowLeft') {
      event.preventDefault();
      setSlide(dialog, current - 1);
    }
    if (event.key === 'ArrowRight') {
      event.preventDefault();
      setSlide(dialog, current + 1);
    }
  });
  dialog.querySelector('[data-dialog-previous]')?.addEventListener('click', () => {
    setSlide(dialog, Number(dialog.dataset.slide || 0) - 1);
  });
  dialog.querySelector('[data-dialog-next]')?.addEventListener('click', () => {
    setSlide(dialog, Number(dialog.dataset.slide || 0) + 1);
  });
});

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
