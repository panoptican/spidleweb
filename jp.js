// Homepage script for the Japanese-web layout. Case pages keep script.js.

// Today's date in the dotted homepage format: 2026.07.18
const today = document.getElementById('today');
if (today) {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  today.dateTime = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
  today.textContent = `${now.getFullYear()}.${pad(now.getMonth() + 1)}.${pad(now.getDate())}`;
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

// Visitor counter: a real shared tally, served by the /api/hits Pages Function
// (Workers KV). To keep the count honest and the writes sane, each browser
// bumps it at most once per day and otherwise just reads the current total.
const counter = document.getElementById('counter');
if (counter) {
  const show = (n) => { counter.textContent = String(n).padStart(6, '0'); };

  // Decide whether this load should increment the count.
  let bump = true;
  try {
    const stamp = new Date().toDateString();
    if (localStorage.getItem('spidleweb-counter-stamp') === stamp) {
      bump = false; // already counted today
    } else {
      localStorage.setItem('spidleweb-counter-stamp', stamp);
    }
  } catch (e) {
    // Private mode etc. — treat every load as a fresh visit.
  }

  fetch(`/api/hits${bump ? '?bump=1' : ''}`, { cache: 'no-store' })
    .then((res) => (res.ok ? res.json() : Promise.reject(res.status)))
    .then((data) => {
      if (typeof data.count === 'number') show(data.count);
    })
    .catch(() => {
      // Offline, function not deployed yet, etc. — keep the static markup.
    });
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
