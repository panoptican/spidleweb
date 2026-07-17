// Reveal sections as they enter the viewport. Progressive enhancement:
// without JS, @media (scripting: none) shows content; reduced motion skips animation.
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const targets = document.querySelectorAll('.reveal');

if (reduced || !('IntersectionObserver' in window)) {
  targets.forEach((el) => el.classList.add('is-in'));
} else {
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 }
  );
  targets.forEach((el) => io.observe(el));
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

