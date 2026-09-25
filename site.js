/* spidleweb.net: site chrome behaviour.

   The phone menu, copying the email address, the docked Grid and List bar,
   and the footer year. Every page with the site chrome loads this file with
   <script src="/site.js" defer>. Each part is progressive enhancement: without
   this file the menu is a row of links, the address is a mailto link, and the
   dock never appears. The markup is in specs/redesign.md, "Chrome contract". */

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
  // Picking a row, tapping the trigger, tapping outside, or Esc closes it,
  // and focus goes back to the trigger.

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
      if (isOpen() && event.target.closest('a')) setOpen(false, true);
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

  setupMenu();
  setupEmail();
  setupDock();
})();
