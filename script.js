// Reveal sections as they enter the viewport. Progressive enhancement:
// without JS, content stays visible (js-active never set); reduced motion skips animation.
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const targets = document.querySelectorAll('.reveal');

function revealNow(el) {
  el.classList.add('is-in');
}

function isInViewport(el) {
  const rect = el.getBoundingClientRect();
  return rect.top < window.innerHeight && rect.bottom > 0;
}

if (reduced || !('IntersectionObserver' in window)) {
  targets.forEach(revealNow);
} else {
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          revealNow(entry.target);
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.05, rootMargin: '48px 0px' }
  );

  // Hash deep-links and above-the-fold items must not stay invisible.
  const hashTarget = location.hash ? document.querySelector(location.hash) : null;
  targets.forEach((el) => {
    if (
      isInViewport(el) ||
      (hashTarget && (el === hashTarget || hashTarget.contains(el)))
    ) {
      revealNow(el);
      return;
    }
    io.observe(el);
  });
}

// Keep the footer year current.
const year = document.getElementById('year');
if (year) year.textContent = new Date().getFullYear();

// Active navigation highlighting based on scroll position
const sections = document.querySelectorAll('main.archive section[id]');
const navLinks = document.querySelectorAll('.archive__nav a');

if (sections.length && navLinks.length && 'IntersectionObserver' in window) {
  const observerOptions = {
    root: null,
    rootMargin: '-20% 0px -60% 0px', // Trigger when section occupies the upper-middle of viewport
    threshold: 0
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        navLinks.forEach((link) => {
          if (link.getAttribute('href') === `#${id}`) {
            link.classList.add('is-active');
          } else {
            link.classList.remove('is-active');
          }
        });
      }
    });
  }, observerOptions);

  sections.forEach((section) => observer.observe(section));
}
