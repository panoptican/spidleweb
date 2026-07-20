// Homepage script for the Japanese-web layout. Case pages keep script.js.

// Today's date in the dotted homepage format: 2026.07.18
const today = document.getElementById('today');
if (today) {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  today.dateTime = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
  today.textContent = `${now.getFullYear()}.${pad(now.getMonth() + 1)}.${pad(now.getDate())}`;
}

// Measure the chrome above the grid (bar + ticker + frame margin) so the
// sticky rail can size itself to fit the viewport and keep the seal in view.
const grid = document.querySelector('.grid');
if (grid) {
  const setRailOffset = () => {
    const top = grid.getBoundingClientRect().top + window.scrollY;
    document.documentElement.style.setProperty('--rail-offset', `${Math.round(top)}px`);
  };
  setRailOffset();
  window.addEventListener('resize', setRailOffset);
}

// Live clock with seconds in the top bar, 24-hour local time.
const clock = document.getElementById('clock');
if (clock) {
  const pad = (n) => String(n).padStart(2, '0');
  const tick = () => {
    const now = new Date();
    clock.textContent = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
  };
  tick();
  setInterval(tick, 1000);
}

// Keep the footer year current.
const year = document.getElementById('year');
if (year) year.textContent = new Date().getFullYear();

// Visitor counter: a loving fake. Increments once per browser, per day,
// so returning visitors see the number tick up like it's 2001.
const counter = document.getElementById('counter');
if (counter) {
  const BASE = 4721;
  let n = BASE;
  try {
    const stored = JSON.parse(localStorage.getItem('spidleweb-counter') || 'null');
    const stamp = new Date().toDateString();
    if (stored && stored.stamp === stamp) {
      n = stored.n;
    } else {
      n = (stored ? stored.n : BASE) + 1;
      localStorage.setItem('spidleweb-counter', JSON.stringify({ n, stamp }));
    }
  } catch (e) {
    // Private mode etc. — the counter just stays at base.
  }
  counter.textContent = String(n).padStart(6, '0');
}

// Active section highlighting in the directory strip.
const sections = document.querySelectorAll('.content section[id]');
const navLinks = document.querySelectorAll('.dirs a');

if (sections.length && navLinks.length && 'IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        navLinks.forEach((link) => {
          link.classList.toggle('is-active', link.getAttribute('href') === `#${id}`);
        });
      }
    });
  }, { rootMargin: '-20% 0px -60% 0px', threshold: 0 });

  sections.forEach((section) => observer.observe(section));
}
