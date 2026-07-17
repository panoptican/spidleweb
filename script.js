// Fade in the fixed marker once the hero has scrolled past.
const marker = document.getElementById('marker');
const hero = document.querySelector('.hero');

const observer = new IntersectionObserver(
  (entries) => {
    const heroVisible = entries[0].isIntersecting;
    marker.classList.toggle('is-visible', !heroVisible);
    marker.setAttribute('aria-hidden', heroVisible ? 'true' : 'false');
  },
  { threshold: 0, rootMargin: '-80px 0px 0px 0px' }
);

if (hero) observer.observe(hero);
