// Pages in sub-folders (e.g. /treatments/) set data-root="../" so shared links still work.
const SITE_ROOT = document.documentElement.getAttribute('data-root') || '';

// ---- Clinic phone: set this ONE value and every "Call us" button updates ----
// Use international format, e.g. '+919876543210'. Leave empty until the number is known.
const CLINIC_PHONE = '';

document.querySelectorAll('[data-call]').forEach(a => {
  if (!CLINIC_PHONE) return;
  a.setAttribute('href', 'tel:' + CLINIC_PHONE.replace(/[^+\d]/g, ''));
  const n = a.querySelector('.call-num');
  if (n) n.textContent = CLINIC_PHONE;
});

// Header: compact + shadow after the visitor starts scrolling
const siteHeader = document.getElementById('site-header');
const onScroll = () => siteHeader.classList.toggle('scrolled', window.scrollY > 16);
window.addEventListener('scroll', onScroll, { passive: true });
onScroll();

// Mobile menu
const burger = document.querySelector('.burger');
const menu = document.getElementById('menu');
const setMenu = open => {
  menu.classList.toggle('open', open);
  burger.setAttribute('aria-expanded', open);
  burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
};
burger.addEventListener('click', () => setMenu(!menu.classList.contains('open')));
menu.addEventListener('click', e => { if (e.target.closest('a')) setMenu(false); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') setMenu(false); });

// Scroll reveal
const items = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver((entries, obs) => {
    entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add('in'); obs.unobserve(en.target); } });
  }, { threshold: 0.12 });
  items.forEach((el, i) => { el.style.transitionDelay = (i % 3) * 80 + 'ms'; io.observe(el); });
} else {
  items.forEach(el => el.classList.add('in'));
}

// Booking form (front-end only: no backend is connected yet)
const form = document.getElementById('bookForm');
const note = document.getElementById('formNote');
if (form) form.addEventListener('submit', e => {
  e.preventDefault();
  let ok = true;
  form.querySelectorAll('[required]').forEach(f => {
    const bad = !f.value.trim();
    f.classList.toggle('invalid', bad);
    if (bad) ok = false;
  });
  if (!ok) { note.textContent = 'Please fill in your name and phone number.'; return; }
  note.textContent = 'Thank you! We will contact you soon.';
  form.reset();
});

const yr = document.getElementById('yr'); if (yr) yr.textContent = new Date().getFullYear();


// ---- Trust strip: shown under the hero (Home) and on every other page ----
// Add ONLY real, verifiable items. Anything left empty stays hidden.
//
// AHPRA: Australian physiotherapists must be registered. Put the registration number
// (format PHY0000000000) so patients can verify it on the public AHPRA register.
const AHPRA_NUMBER = '';           // e.g. 'PHY0001234567'
const AHPRA_NAME   = '';           // optional: practitioner name as on the register

const TRUST = {
  credentials: [],  // degrees, certifications, years of experience
  clubs:       [],  // sporting clubs / teams / academies you work with
  health:      [],  // private health funds / memberships accepted (HICAPS, etc.)
  others:      []   // awards, associations (e.g. Australian Physiotherapy Association), partners
};
// Text: 'Bachelor of Physiotherapy'   Logo: { name: 'Club name', logo: 'images/trust/club.webp' }

const TRUST_SAMPLE = {   // shown only at ?preview
  credentials: ['Sample credential one', 'Sample credential two'],
  clubs:       ['Sample sports club'],
  health:      ['Sample health fund'],
  others:      ['Sample association']
};
const TRUST_GROUPS = [
  { key: 'credentials', title: 'Credentials',                icon: 'M12 2l8 3v6c0 5-3.4 9.4-8 11-4.6-1.6-8-6-8-11V5l8-3zm-1.2 13.6l5.6-5.6-1.4-1.4-4.2 4.2-2-2-1.4 1.4 3.4 3.4z' },
  { key: 'clubs',       title: 'Sporting clubs',             icon: 'M7 3h10v2h3v3a4 4 0 01-4 4h-.3A5 5 0 0113 15.9V18h3v3H8v-3h3v-2.1A5 5 0 018.3 12H8a4 4 0 01-4-4V5h3V3zm-1 4v1a2 2 0 002 2V7H6zm12 0h-2v3a2 2 0 002-2V7z' },
  { key: 'health',      title: 'Private health memberships', icon: 'M12 21s-7-4.4-9.3-9A5.4 5.4 0 0112 6a5.4 5.4 0 019.3 6c-2.3 4.6-9.3 9-9.3 9zm-1-11v2H9v2h2v2h2v-2h2v-2h-2v-2h-2z' },
  { key: 'others',      title: 'Also recognised by',         icon: 'M12 2l3 6.5 7 .9-5.1 4.9 1.3 7-6.2-3.4L5.8 21l1.3-7L2 9.4l7-.9L12 2z' }
];
const AHPRA_REGISTER = 'https://www.ahpra.gov.au/Registration/Registers-of-Practitioners.aspx';
const SHIELD = 'M12 2l8 3v6c0 5-3.4 9.4-8 11-4.6-1.6-8-6-8-11V5l8-3zm-1.2 13.6l5.6-5.6-1.4-1.4-4.2 4.2-2-2-1.4 1.4 3.4 3.4z';

(function renderTrust() {
  const sections = document.querySelectorAll('.trust');
  const preview = new URLSearchParams(location.search).has('preview');
  const data = preview ? TRUST_SAMPLE : TRUST;
  const ahpraNo = preview ? 'PHY0000000000' : AHPRA_NUMBER;
  const ns = 'http://www.w3.org/2000/svg';
  const icon = d => {
    const s = document.createElementNS(ns, 'svg');
    s.setAttribute('viewBox', '0 0 24 24'); s.setAttribute('aria-hidden', 'true');
    const p = document.createElementNS(ns, 'path'); p.setAttribute('d', d); s.appendChild(p);
    return s;
  };

  sections.forEach(sec => {
    const grid = sec.querySelector('.trust-grid');
    const box = sec.querySelector('.ahpra');
    const more = sec.querySelector('.trust-more');
    let shown = 0;

    if (ahpraNo) {
      shown++;
      const txt = document.createElement('div');
      const t = document.createElement('strong'); t.textContent = 'Registered with AHPRA';
      const sub = document.createElement('span');
      sub.textContent = (AHPRA_NAME && !preview ? AHPRA_NAME + ' · ' : '') + 'Physiotherapist · Registration no. ' + ahpraNo;
      txt.append(t, sub);
      const a = document.createElement('a');
      a.href = AHPRA_REGISTER; a.target = '_blank'; a.rel = 'noopener noreferrer';
      a.textContent = 'Verify on the public register ↗';
      box.append(icon(SHIELD), txt, a);
      box.hidden = false;
    }

    TRUST_GROUPS.forEach(g => {
      const items = data[g.key] || [];
      if (!items.length) return;
      shown++;
      const col = document.createElement('div');
      col.className = 'trust-col';
      const head = document.createElement('div'); head.className = 'trust-head';
      const h = document.createElement('h3'); h.textContent = g.title;
      head.append(icon(g.icon), h);
      const ul = document.createElement('ul');
      items.forEach(it => {
        const li = document.createElement('li');
        if (typeof it === 'object' && it.logo) {
          const img = document.createElement('img');
          img.src = SITE_ROOT + it.logo; img.alt = it.name; img.loading = 'lazy'; img.height = 40;
          li.className = 'logo'; li.appendChild(img);
        } else li.textContent = typeof it === 'object' ? it.name : it;
        ul.appendChild(li);
      });
      col.append(head, ul); grid.appendChild(col);
    });
    grid.style.setProperty('--cols', grid.children.length || 1);

    if (!shown) return;
    sec.hidden = false;
    if (preview) sec.querySelector('.trust-preview').hidden = false;
  });

  // Footer registration line
  if (ahpraNo && !preview) {
    const f = document.querySelector('.footer .foot');
    if (f) { const p = document.createElement('p'); p.className = 'foot-reg'; p.textContent = 'AHPRA registration no. ' + ahpraNo; f.appendChild(p); }
  }
})();


// ---- Google reviews (shown above the footer call-to-action on every page) ----
// Fill in your Google Business Profile links. Leave empty and the block stays hidden.
//  GOOGLE_REVIEWS_URL      -> your profile / reviews page
//  GOOGLE_WRITE_REVIEW_URL -> the "write a review" link (Google Business Profile > Get more reviews)
//  GOOGLE_RATING / COUNT   -> optional, e.g. 4.9 and 120. Only enter REAL figures.
// AHPRA: its advertising rules restrict patient testimonials by registered practitioners, so this block
// links OUT to Google and never copies or quotes review text onto the site. Confirm the rating line is
// acceptable with AHPRA / your professional association before filling GOOGLE_RATING.
const GOOGLE_REVIEWS_URL = '';
const GOOGLE_WRITE_REVIEW_URL = '';
const GOOGLE_RATING = '';
const GOOGLE_COUNT = '';

(function renderGoogleReviews() {
  if (!GOOGLE_REVIEWS_URL) return;
  document.querySelectorAll('.greviews').forEach(sec => {
    const rating = sec.querySelector('.gr-rating');
    if (GOOGLE_RATING) {
      rating.textContent = '★★★★★  ' + GOOGLE_RATING + (GOOGLE_COUNT ? ' from ' + GOOGLE_COUNT + ' reviews' : '');
    } else rating.textContent = 'See what our patients say';
    const box = sec.querySelector('.gr-actions');
    const read = document.createElement('a');
    read.className = 'btn btn-ghost'; read.href = GOOGLE_REVIEWS_URL; read.target = '_blank'; read.rel = 'noopener noreferrer';
    read.textContent = 'Read reviews on Google ↗';
    box.appendChild(read);
    if (GOOGLE_WRITE_REVIEW_URL) {
      const w = document.createElement('a');
      w.className = 'btn btn-primary'; w.href = GOOGLE_WRITE_REVIEW_URL; w.target = '_blank'; w.rel = 'noopener noreferrer';
      w.textContent = 'Leave a review';
      box.appendChild(w);
    }
    sec.hidden = false;
  });
})();
