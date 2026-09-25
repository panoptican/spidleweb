/* spidleweb.net: site chrome behaviour.

   The phone menu, copying the email address, the docked Grid and List bar,
   and the footer year, plus the filters and pagination on the Craft pages.
   Every page with the site chrome loads this file with
   <script src="/site.js" defer>. Each part is progressive enhancement: without
   this file the menu is a row of links, the address is a mailto link, the
   dock never appears, and every card shows. The markup is in
   specs/redesign.md, "Chrome contract". */

(() => {
  const root = document.documentElement;
  // The inline line in <head> normally sets this first, so the no-JS layout
  // never flashes. Setting it again covers a page that left the line out.
  root.classList.add('js');

  const phone = matchMedia('(max-width: 799px)');

  // ---- Footer year, with the static year in the markup as the fallback ----

  const year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());

  // ---- Phone menu ----
  // A disclosure: the trigger names the current place and toggles the list.
  // Picking a row, tapping the trigger, tapping outside, or Esc closes it.
  // Esc and a tap outside send focus back to the trigger. A picked row leaves
  // focus to where it leads, since About opens in place and takes focus.

  function setupMenu() {
    const nav = document.querySelector('.masthead__nav');
    const trigger = nav?.querySelector('.masthead__trigger');
    const places = nav?.querySelector('.masthead__places');
    if (!trigger || !places) return;

    const isOpen = () => trigger.getAttribute('aria-expanded') === 'true';
    const setOpen = (open, returnFocus = false) => {
      nav.classList.toggle('is-open', open);
      trigger.setAttribute('aria-expanded', String(open));
      if (!open && returnFocus) trigger.focus();
    };

    trigger.addEventListener('click', () => setOpen(!isOpen()));

    places.addEventListener('click', (event) => {
      if (isOpen() && event.target.closest('a')) setOpen(false);
    });

    document.addEventListener('click', (event) => {
      if (isOpen() && !nav.contains(event.target)) setOpen(false, nav.contains(document.activeElement));
    });

    // Capture, so Esc closes the menu before anything else hears it.
    document.addEventListener('keydown', (event) => {
      if (event.key !== 'Escape' || !isOpen()) return;
      event.stopPropagation();
      setOpen(false, true);
    }, true);

    phone.addEventListener('change', () => setOpen(false));
  }

  // ---- Copying the email address ----
  // Any <a class="email" href="mailto:…"> copies instead of opening mail. If
  // the clipboard is unavailable it falls back to the mailto link.

  let status;
  function announce(message) {
    if (!status) {
      status = document.createElement('p');
      status.className = 'visually-hidden';
      status.setAttribute('role', 'status');
      document.body.append(status);
    }
    status.textContent = '';
    requestAnimationFrame(() => { status.textContent = message; });
  }

  async function copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      // Older browsers, or a page without clipboard permission.
    }
    try {
      const area = document.createElement('textarea');
      area.value = text;
      area.setAttribute('readonly', '');
      area.style.cssText = 'position:fixed;top:0;left:0;opacity:0';
      document.body.append(area);
      area.select();
      const copied = document.execCommand('copy');
      area.remove();
      return copied;
    } catch {
      return false;
    }
  }

  function part(className, text, hidden = false) {
    const span = document.createElement('span');
    span.className = className;
    if (text) span.textContent = text;
    if (hidden) span.setAttribute('aria-hidden', 'true');
    return span;
  }

  function setupEmail() {
    for (const link of document.querySelectorAll('a.email[href^="mailto:"]')) {
      const address = decodeURIComponent(link.getAttribute('href').slice('mailto:'.length));
      const tip = part('email__tip', 'Click to copy', true);
      link.replaceChildren(
        part('email__address', link.textContent.trim()),
        part('email__done', 'Copied to clipboard ✓'),
        part('email__glyph', '', true),
        tip,
      );
      let timer;
      link.addEventListener('click', async (event) => {
        if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        if (!(await copyText(address))) {
          location.href = link.href;
          return;
        }
        link.dataset.copied = '';
        tip.textContent = 'Copied to clipboard';
        announce('Copied to clipboard');
        clearTimeout(timer);
        timer = setTimeout(() => {
          delete link.dataset.copied;
          tip.textContent = 'Click to copy';
        }, 2000);
      });
    }
  }

  // ---- Docked Grid and List bar ----
  // A copy of the masthead switcher, fixed to the bottom of the screen once
  // the original scrolls away. It hides while scrolling down and returns on
  // the first scroll up, and it steps aside while the pagination or the
  // legend is in view, so Grid and List never show twice. The slide is CSS,
  // and reduced motion drops it there.

  function setupDock() {
    const source = document.querySelector('.view-switch');
    if (!source || !('IntersectionObserver' in window)) return;

    const dock = document.createElement('nav');
    dock.className = 'view-dock micro';
    dock.setAttribute('aria-label', 'View, docked');
    dock.dataset.hidden = '';
    for (const link of source.querySelectorAll('a')) {
      const copy = link.cloneNode(true);
      copy.className = 'view-dock__link';
      dock.append(copy);
    }
    document.body.append(dock);

    let sourceInView = true;
    let lastY = scrollY;
    let goingDown = false;
    const blockers = new Set();

    const update = () => {
      const holdsFocus = dock.contains(document.activeElement);
      const show = !sourceInView && !blockers.size && (!goingDown || holdsFocus);
      dock.toggleAttribute('data-hidden', !show);
    };

    new IntersectionObserver(([entry]) => {
      sourceInView = entry.isIntersecting;
      update();
    }).observe(source);

    const blockerObserver = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) blockers.add(entry.target);
        else blockers.delete(entry.target);
      }
      update();
    });
    for (const el of document.querySelectorAll('.legend, [data-pager]')) blockerObserver.observe(el);

    // A few pixels of travel settle the direction, so a trackpad's jitter
    // does not flicker the bar.
    addEventListener('scroll', () => {
      const y = scrollY;
      if (Math.abs(y - lastY) < 6) return;
      goingDown = y > lastY;
      lastY = y;
      update();
    }, { passive: true });

    dock.addEventListener('focusout', () => requestAnimationFrame(update));
  }

  // ---- Craft: filters and pagination ----
  // Every item is already in the page, so pagination only reveals cards, 30
  // at a time, and the filters narrow the same list. The count, the bar, and
  // "Show 30 more" always describe the filtered set. Hidden cards carry the
  // hidden attribute. A deep link reveals everything up to its card, whether
  // it arrives as the page's own #id or as a stream:reveal event from
  // stream.js, which opens items in place.

  const PAGE_SIZE = 30;
  const TYPE_LABELS = {
    'case-study': 'Case studies',
    screen: 'Screens',
    prototype: 'Prototypes',
    tool: 'Tools',
    video: 'Videos',
    reel: 'Reels',
    post: 'Writing',
  };

  // data-industry is kebab case, and its label is that with spaces.
  const industryLabel = (value) => {
    const words = value.replace(/-/g, ' ');
    return words.charAt(0).toUpperCase() + words.slice(1);
  };

  function hashId() {
    try {
      return decodeURIComponent(location.hash.slice(1));
    } catch {
      return '';
    }
  }

  function setupStream() {
    const stream = document.querySelector('[data-stream]');
    if (!stream) return;
    const cards = [...stream.children].filter((el) => el.matches('article[data-type]'));
    if (!cards.length) return;

    const pager = document.querySelector('[data-pager]');
    const empty = document.querySelector('[data-stream-empty]');
    const selects = [...document.querySelectorAll('[data-filters] select[data-filter]')];
    // Each select's data-filter names the card attribute it reads.
    const fields = selects.map((select) => select.dataset.filter);

    const filters = {};
    const params = new URLSearchParams(location.search);
    for (const field of fields) {
      const value = params.get(field) ?? '';
      filters[field] = cards.some((card) => card.dataset[field] === value) ? value : '';
    }
    let limit = Math.max(PAGE_SIZE, Number(history.state?.shown) || 0);

    const matches = (card, except) => fields.every((field) =>
      field === except || !filters[field] || card.dataset[field] === filters[field]);
    const matching = () => cards.filter((card) => matches(card));

    // Options come from the cards on the page, each with a count that
    // respects the other filter.
    function renderOptions() {
      for (const select of selects) {
        const field = select.dataset.filter;
        const counts = new Map();
        for (const card of cards) {
          if (!matches(card, field)) continue;
          const value = card.dataset[field];
          counts.set(value, (counts.get(value) ?? 0) + 1);
        }
        const values = field === 'type'
          ? Object.keys(TYPE_LABELS).filter((value) => cards.some((card) => card.dataset.type === value))
          : [...new Set(cards.map((card) => card.dataset.industry))].sort();
        const label = (value) => (field === 'type' ? TYPE_LABELS[value] : industryLabel(value));
        const total = [...counts.values()].reduce((sum, n) => sum + n, 0);
        const options = [new Option(`All (${total})`, '')];
        for (const value of values) {
          const n = counts.get(value) ?? 0;
          const option = new Option(`${label(value)} (${n})`, value);
          option.disabled = n === 0 && filters[field] !== value;
          options.push(option);
        }
        select.replaceChildren(...options);
        select.value = filters[field];
        const shown = document.querySelector(`[data-filter-label="${field}"]`);
        if (shown) shown.textContent = filters[field] ? label(filters[field]) : 'All';
      }
    }

    function render() {
      const list = matching();
      const visible = new Set(list.slice(0, limit));
      for (const card of cards) card.hidden = !visible.has(card);

      const shown = Math.min(limit, list.length);
      if (empty) empty.hidden = list.length > 0;
      if (pager) {
        pager.hidden = list.length === 0;
        pager.querySelector('[data-pager-shown]').textContent = shown;
        pager.querySelector('[data-pager-total]').textContent = list.length;
        pager.querySelector('[data-pager-fill]').style.width = `${list.length ? (shown / list.length) * 100 : 0}%`;
        const more = pager.querySelector('[data-pager-more]');
        const next = Math.min(PAGE_SIZE, list.length - shown);
        more.hidden = next <= 0;
        pager.querySelector('[data-pager-next]').textContent = next;
      }
    }

    function remember() {
      history.replaceState({ ...(history.state ?? {}), shown: limit }, '');
    }

    function writeQuery() {
      const url = new URL(location.href);
      for (const field of fields) {
        if (filters[field]) url.searchParams.set(field, filters[field]);
        else url.searchParams.delete(field);
      }
      history.replaceState({ ...(history.state ?? {}), shown: limit }, '', url);
    }

    function setFilters(next) {
      Object.assign(filters, next);
      limit = PAGE_SIZE;
      renderOptions();
      render();
      writeQuery();
    }

    // Reveals every card up to this one. Returns the card, or null.
    function reveal(id) {
      const card = id ? cards.find((el) => el.id === id) : null;
      if (!card) return null;
      if (!matches(card)) {
        for (const field of fields) filters[field] = '';
        renderOptions();
        writeQuery();
      }
      const index = matching().indexOf(card);
      if (index >= limit) limit = index + 1;
      render();
      remember();
      return card;
    }

    for (const select of selects) {
      select.addEventListener('change', () => setFilters({ [select.dataset.filter]: select.value }));
    }

    document.querySelector('[data-filters-clear]')?.addEventListener('click', () => {
      setFilters(Object.fromEntries(fields.map((field) => [field, ''])));
      selects[0]?.focus();
    });

    pager?.querySelector('[data-pager-more]').addEventListener('click', () => {
      const list = matching();
      const first = list[limit];
      limit += PAGE_SIZE;
      render();
      remember();
      // Carry keyboard focus to the first card just revealed.
      const link = first?.querySelector('a[data-open], a');
      if (link) {
        link.focus({ preventScroll: true });
        if (link.getBoundingClientRect().top > innerHeight) link.scrollIntoView({ block: 'nearest' });
      }
    });

    document.addEventListener('stream:reveal', (event) => reveal(event.detail?.id));

    // A same-page link to a hidden card: the browser's jump found nothing
    // to scroll to, so scroll once the card is shown.
    addEventListener('hashchange', () => {
      const id = hashId();
      const wasHidden = cards.find((el) => el.id === id)?.hidden;
      const card = reveal(id);
      if (card && wasHidden) card.scrollIntoView();
    });

    // On load only cards after the target are hidden, so the browser's own
    // jump to the fragment stays where it landed.
    renderOptions();
    if (!reveal(hashId())) render();
  }

  setupMenu();
  setupEmail();
  setupStream();
  setupDock();
})();
