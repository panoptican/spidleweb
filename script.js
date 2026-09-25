// spidleweb.net: case-study pages. The context column sticks while it fits,
// scrolling phone captures take a keyboard stop, and proofs fade to colour as
// they reach the middle of the window. The site chrome is site.js, and opening
// in place is stream.js.

const motionPreference = matchMedia('(prefers-reduced-motion: reduce)');

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

const proofFrames = [...document.querySelectorAll('.proof__frame')];
if (proofFrames.length) {
  // Only scrollable phone captures need a keyboard stop.
  const scrollers = document.querySelectorAll('.proof-phone .proof__frame');
  function updateScrollAccess() {
    scrollers.forEach((el) => {
      const scrollable = el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1;
      el.tabIndex = scrollable ? 0 : -1;
    });
  }
  window.addEventListener('resize', updateScrollAccess);
  if ('ResizeObserver' in window) {
    const sizeObserver = new ResizeObserver(updateScrollAccess);
    scrollers.forEach((el) => sizeObserver.observe(el));
  }
  proofFrames.forEach((frame) => frame.querySelector('img').addEventListener('load', updateScrollAccess));
  updateScrollAccess();

  // The trigger is the frame's midpoint, independent of the capture's scroll height.
  const pendingFrames = new Set(proofFrames);
  let colorUpdatePending = false;
  function stopColorReveal() {
    document.documentElement.classList.remove('color-reveal-active');
    pendingFrames.clear();
    window.removeEventListener('scroll', scheduleColorReveal);
    window.removeEventListener('resize', scheduleColorReveal);
  }
  function updateColorReveal() {
    colorUpdatePending = false;
    pendingFrames.forEach((frame) => {
      const rect = frame.getBoundingClientRect();
      if (rect.top + rect.height / 2 <= window.innerHeight) {
        frame.classList.add('is-color');
        pendingFrames.delete(frame);
      }
    });
    if (!pendingFrames.size) {
      window.removeEventListener('scroll', scheduleColorReveal);
      window.removeEventListener('resize', scheduleColorReveal);
    }
  }
  function scheduleColorReveal() {
    if (colorUpdatePending) return;
    colorUpdatePending = true;
    requestAnimationFrame(updateColorReveal);
  }
  if (!motionPreference.matches) {
    updateColorReveal();
    if (pendingFrames.size) {
      document.documentElement.classList.add('color-reveal-active');
      window.addEventListener('scroll', scheduleColorReveal, { passive: true });
      window.addEventListener('resize', scheduleColorReveal);
      document.fonts.ready.then(scheduleColorReveal);
    }
  }
  motionPreference.addEventListener('change', (event) => {
    if (event.matches) stopColorReveal();
  });
}
