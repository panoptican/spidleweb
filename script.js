// A fragment is an element ID, not a CSS selector. Malformed escapes are no match.
function getHashTarget() {
  try {
    return document.getElementById(decodeURIComponent(location.hash.slice(1)));
  } catch {
    return null;
  }
}

// Content stays visible until the reveal observer is ready.
const motionPreference = matchMedia('(prefers-reduced-motion: reduce)');
const targets = document.querySelectorAll('.reveal');
let revealObserver;

function revealNow(el) {
  el.classList.add('is-in');
}

function isInViewport(el) {
  const rect = el.getBoundingClientRect();
  return rect.top < window.innerHeight && rect.bottom > 0;
}

function revealAll() {
  if (revealObserver) revealObserver.disconnect();
  targets.forEach(revealNow);
  document.documentElement.classList.remove('js-active');
}

motionPreference.addEventListener('change', (event) => {
  if (event.matches) revealAll();
});

if (motionPreference.matches || !('IntersectionObserver' in window)) {
  revealAll();
} else {
  revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          revealNow(entry.target);
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.05, rootMargin: '48px 0px' }
  );

  const hashTarget = getHashTarget();
  targets.forEach((el) => {
    if (
      isInViewport(el) ||
      (hashTarget && (el === hashTarget || hashTarget.contains(el)))
    ) {
      revealNow(el);
    } else {
      revealObserver.observe(el);
    }
  });
  document.documentElement.classList.add('js-active');
}

// Keep the footer year current on every page, with a static HTML fallback.
const year = document.getElementById('year');
if (year) year.textContent = new Date().getFullYear();

// Use section starts and the page bottom for a deterministic reading position.
const sections = Array.from(document.querySelectorAll('main.archive > section[id]'));
const navLinks = document.querySelectorAll('.archive__nav a');

if (sections.length && navLinks.length) {
  const archive = document.querySelector('main.archive');
  const header = archive.querySelector('.archive__header');
  let updatePending = false;
  let anchoredSection = null;
  let anchoredScrollY = 0;

  function getHeaderHeight() {
    return getComputedStyle(header).position === 'sticky'
      ? header.getBoundingClientRect().height : 0;
  }

  function updateNavigation() {
    updatePending = false;
    const headerHeight = getHeaderHeight();
    archive.style.setProperty('--header-height', `${headerHeight}px`);

    // A bottom-clamped jump may not put its target against the header. Keep
    // that choice until the reader actually scrolls away from the landing.
    if (Math.abs(window.scrollY - anchoredScrollY) > 1) anchoredSection = null;
    let activeSection = anchoredSection || sections[0];
    if (!anchoredSection) {
      sections.forEach((section) => {
        if (section.getBoundingClientRect().top <= headerHeight + 1) {
          activeSection = section;
        }
      });
      if (window.scrollY > 0 &&
          Math.ceil(window.scrollY + window.innerHeight) >= document.documentElement.scrollHeight) {
        activeSection = sections[sections.length - 1];
      }
    }

    navLinks.forEach((link) => {
      link.classList.toggle('is-active', link.getAttribute('href') === `#${activeSection.id}`);
    });
  }

  function scheduleUpdate() {
    if (updatePending) return;
    updatePending = true;
    requestAnimationFrame(updateNavigation);
  }

  function rememberAnchor() {
    const target = getHashTarget();
    anchoredSection = null;
    if (sections.includes(target)) {
      const targetY = target.getBoundingClientRect().top + window.scrollY - getHeaderHeight();
      const maxScrollY = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
      const landingY = Math.max(0, Math.min(targetY, maxScrollY));
      // A scroll may have already followed the click before this callback runs.
      if (Math.abs(window.scrollY - landingY) <= 1) anchoredSection = target;
    }
    anchoredScrollY = window.scrollY;
    scheduleUpdate();
  }

  navLinks.forEach((link) => {
    link.addEventListener('click', (event) => {
      if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      // Wait for the browser's native jump, including repeat clicks on one hash.
      requestAnimationFrame(rememberAnchor);
    });
  });
  window.addEventListener('hashchange', rememberAnchor);
  window.addEventListener('load', rememberAnchor);
  window.addEventListener('scroll', scheduleUpdate, { passive: true });
  window.addEventListener('resize', scheduleUpdate);
  if ('ResizeObserver' in window) {
    const resizeObserver = new ResizeObserver(scheduleUpdate);
    resizeObserver.observe(header);
    resizeObserver.observe(archive);
  }
  updateNavigation();
}

// A complete context column sticks only when every item fits the viewport.
const caseContext = document.querySelector('.case-context');
if (caseContext) {
  const desktop = matchMedia('(min-width: 1000px) and (min-height: 600px)');
  function updateContextPosition() {
    caseContext.classList.toggle('is-sticky', desktop.matches &&
      caseContext.offsetHeight + 48 <= window.innerHeight);
  }
  window.addEventListener('resize', updateContextPosition);
  if ('ResizeObserver' in window) new ResizeObserver(updateContextPosition).observe(caseContext);
  document.fonts.ready.then(updateContextPosition);
  updateContextPosition();
}
