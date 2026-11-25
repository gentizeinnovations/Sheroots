// Pages in sub-folders (e.g. /treatments/) set data-root="../" so shared links still work.
const SITE_ROOT = document.documentElement.getAttribute('data-root') || '';

// ---- Clinic phone: set this ONE value and every "Call us" button updates ----
// Use international format, e.g. '+919876543210'. Leave empty until the number is known.
const CLINIC_PHONE = '+919940662500';

document.querySelectorAll('[data-call]').forEach(a => {
  if (!CLINIC_PHONE) return;
  a.setAttribute('href', 'tel:' + CLINIC_PHONE.replace(/[^+\d]/g, ''));
  // the number is already in the HTML (good for Google); only fill it if a button was left empty
  const n = a.querySelector('.call-num');
  if (n && !n.textContent.trim()) n.textContent = CLINIC_PHONE.replace(/^\+91(\d{5})(\d{5})$/, '$1 $2');
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

// Logo / "Home" links: the hero (#top) is position:sticky, so the browser thinks it is
// always in view and ignores a jump to #top. Scroll the window to the very top ourselves.
document.addEventListener('click', e => {
  const a = e.target.closest('a[href]');
  if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
  const href = a.getAttribute('href');
  const onHome = !!document.getElementById('top');
  const isTop = href === '#top' || href === '#' || (onHome && (href === '/' || href === '/#top' || href === 'index.html' || href === 'index.html#top'));
  if (!isTop || !onHome) return;
  e.preventDefault();
  setMenu(false);
  const smooth = !matchMedia('(prefers-reduced-motion: reduce)').matches;
  window.scrollTo({ top: 0, behavior: smooth ? 'smooth' : 'auto' });
  if (location.hash) history.replaceState(null, '', location.pathname + location.search);
});

// Scroll reveal: see the block at the end of this file

// Booking form: there is no server, so it opens a ready-to-send email to the clinic
const CLINIC_EMAIL = 'sherootsphysio@gmail.com';
// Clinic WhatsApp (country code + number, digits only). Used by the form and the chat bot.
window.SHE_WA = '919025603429';
window.waLink = text => 'https://wa.me/' + window.SHE_WA + '?text=' + encodeURIComponent(text);
const form = document.getElementById('bookForm');
const note = document.getElementById('formNote');
// Phone field: digits only, never more than 10 (also cleans pasted text such as "+91 98765-43210")
const phoneInput = form && form.querySelector('[name="phone"]');
if (phoneInput) phoneInput.addEventListener('input', () => {
  let d = phoneInput.value.replace(/\D/g, '');
  if (d.length > 10 && d.startsWith('91')) d = d.slice(2);
  phoneInput.value = d.slice(0, 10);
  phoneInput.classList.remove('invalid');
});
if (form) form.addEventListener('submit', e => {
  e.preventDefault();
  let ok = true;
  form.querySelectorAll('[required]').forEach(f => {
    const bad = !f.value.trim();
    f.classList.toggle('invalid', bad);
    if (bad) ok = false;
  });
  const ph = form.querySelector('[name="phone"]');
  if (ph && ph.value.length !== 10) { ph.classList.add('invalid'); ph.focus(); note.textContent = 'Please enter a 10-digit phone number.'; return; }
  if (!ok) { note.textContent = 'Please fill in your name, phone number, email, date and time.'; return; }
  const em = form.querySelector('[name="email"]');
  if (em && !/^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(em.value.trim())) { em.classList.add('invalid'); em.focus(); note.textContent = 'Please check your email address. Your confirmation is sent there.'; return; }
  const d = Object.fromEntries(new FormData(form));
  const fmtDate = v => { const x = new Date(v + 'T00:00'); return isNaN(x) ? v : x.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' }); };
  const fmtTime = v => { const [h, m] = v.split(':').map(Number); return (h % 12 || 12) + ':' + String(m).padStart(2, '0') + (h >= 12 ? ' PM' : ' AM'); };
  const lines = ['Name: ' + d.name, 'Phone: ' + d.phone, 'For: ' + d.service, 'Date: ' + fmtDate(d.date), 'Time: ' + fmtTime(d.time)].concat(d.message ? ['Message: ' + d.message] : []);
  const body = lines.map(encodeURIComponent).join('%0A');
  const subj = 'Appointment request: ' + d.service + ', ' + fmtDate(d.date) + ' ' + fmtTime(d.time);
  const gmail = 'https://mail.google.com/mail/?view=cm&fs=1&to=' + encodeURIComponent(CLINIC_EMAIL) + '&su=' + encodeURIComponent(subj) + '&body=' + body;
  const mailto = 'mailto:' + CLINIC_EMAIL + '?subject=' + encodeURIComponent(subj) + '&body=' + body;
  const btn = form.querySelector('[type="submit"]'), label = btn ? btn.textContent : '';
  if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
  note.classList.remove('ok'); note.textContent = '';
  const first = String(d.name).trim().split(' ')[0];
  fetch('/api/book', { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: d.name, phone: d.phone, email: d.email || '', concern: d.service, date: d.date, time: d.time, note: d.message || '', source: 'form', website: d.website || '' }) })
    .then(r => r.json().then(j => ({ code: r.status, j }))).catch(() => ({ code: 0, j: {} }))
    .then(({ code, j }) => {
      if (btn) { btn.disabled = false; btn.textContent = label; }
      if (code === 200 && j.ok) {
        note.classList.add('ok');
        // Clear "what happens next" card (all text set with textContent, never HTML from input)
        const mk = (tag, cls, txt) => { const x = document.createElement(tag); if (cls) x.className = cls; if (txt) x.textContent = txt; return x; };
        const card = mk('div', 'bk-done');
        const top = mk('div', 'bk-done-top'); top.append(mk('strong', '', 'Request sent, ' + first + '! ✅'));
        if (j.ref) top.append(mk('span', 'bk-done-ref', 'Ref: ' + j.ref));
        card.append(top, mk('p', 'bk-done-when', d.service + ' · ' + fmtDate(d.date) + ', ' + fmtTime(d.time)));
        const ol = mk('ol', 'bk-done-steps');
        [['Clinic reviews your request', 'Usually within a few hours during clinic time.'],
         ['You get the confirmation', 'By email to ' + d.email + ', on WhatsApp or a call on ' + d.phone + ', and here on the website under "Track my request".'],
         ['Come to your session', 'Arrive 10 minutes early, in comfortable clothes, with any scan reports.']]
          .forEach(([t, s]) => { const li = mk('li'); li.append(mk('b', '', t), mk('span', '', s)); ol.append(li); });
        card.append(ol);
        const acts = mk('div', 'bk-done-acts');
        // WhatsApp the clinic too: opens WhatsApp with the request typed out, so the clinic sees it at once
        const waMsg = ['Hi SHEroots, I just sent a booking request on your website' + (j.ref ? ' (Ref: ' + j.ref + ')' : '') + '.'].concat(lines).join('\n');
        const w = mk('a', 'wa-btn bk-done-wa', 'Also send on WhatsApp (faster reply)'); w.href = waLink(waMsg); w.target = '_blank'; w.rel = 'noopener'; acts.append(w);
        if (j.status_url) { const a = mk('a', 'bk-done-track', 'Track my request →'); a.href = j.status_url; a.setAttribute('data-track-open', ''); acts.append(a); }
        const cl = mk('a', '', 'Need it sooner? Call 99406 62500'); cl.href = 'tel:+919940662500'; acts.append(cl);
        card.append(acts, mk('p', 'bk-done-tip', 'Tip: save or screenshot this, so you have your reference.'));
        note.replaceChildren(card);
        if (window.sheRememberBooking) window.sheRememberBooking(j);
        form.reset(); refreshSlots();
        return;
      }
      if (code === 409) {
        refreshSlots();
        const alts = (j.alternatives || []).map(x => x.label).join(', ');
        note.textContent = 'Sorry, that time was just booked by someone else. Please pick another time.' + (alts ? ' Nearest free times: ' + alts + '.' : '');
        return;
      }
      if (code === 422) { note.textContent = j.error === 'email' ? 'Please enter a valid email address. Your confirmation is sent there.' : 'Please check your details and try again.'; return; }
      note.innerHTML = 'Sorry, we could not send this automatically. <a href="' + gmail + '" target="_blank" rel="noopener">Send it with Gmail</a>, <a href="' + mailto + '">use your mail app</a>, or call 99406 62500.';
      const wa = document.createElement('a'); wa.className = 'wa-btn'; wa.target = '_blank'; wa.rel = 'noopener'; wa.textContent = 'Send on WhatsApp';
      wa.href = waLink(['Hi SHEroots, I would like to book an appointment.'].concat(lines).join('\n'));
      note.appendChild(document.createTextNode(' ')); note.appendChild(wa);
    });
});

// Booking form: mark times that are already booked for the chosen day
function refreshSlots() {
  if (!form) return;
  const date = form.querySelector('[name="date"]'), sel = form.querySelector('select[name="time"]');
  if (!date || !sel) return;
  [...sel.options].forEach(o => { if (o.value) { o.disabled = false; o.textContent = o.textContent.replace(/ · .*$/, ''); } });
  if (!date.value) return;
  fetch('/api/slots?date=' + date.value).then(r => r.ok ? r.json() : null).then(j => {
    if (!j) return;
    const map = Object.fromEntries(j.slots.map(x => [x.time, x]));
    [...sel.options].forEach(o => {
      const x = map[o.value]; if (!x || x.free) return;
      o.disabled = true; o.textContent += x.past ? ' · not available' : ' · booked';
      if (sel.value === o.value) sel.value = '';
    });
  }).catch(() => {});
}
if (form) { const dt = form.querySelector('[name="date"]'); if (dt) dt.addEventListener('change', refreshSlots); }

// In-page links: picking a treatment opens it in the treatment picker; "Book" buttons pre-select the treatment
document.addEventListener('click', e => {
  const go = e.target.closest('[data-ex-go]');
  if (go) { e.preventDefault(); if (window.showTreatment) window.showTreatment(go.dataset.exGo); }
  const svc = e.target.closest('[data-service]');
  if (svc && form) { const sel = form.querySelector('select[name="service"]'); if (sel) [...sel.options].forEach(o => { if (o.textContent.trim() === svc.dataset.service) sel.value = o.value || o.textContent; }); }
});

// Nav: highlight the section you are in
(() => {
  const links = [...document.querySelectorAll('.links a[href^="#"]')]; if (!links.length) return;
  const order = [['top', 'top'], ['about', 'about'], ['explore', 'explore'], ['stages', 'explore'], ['pills', 'explore'], ['methods', 'explore'], ['first-visit', 'explore'], ['doctor', 'about'], ['trust', 'about'], ['instagram', 'about'], ['faq', 'contact'], ['visit', 'contact'], ['contact', 'contact']];
  const pos = () => order.map(([id, as]) => { const el = document.getElementById(id) || document.querySelector('.' + id); return el ? [el.getBoundingClientRect().top + scrollY, as] : null; }).filter(Boolean).sort((a, b) => a[0] - b[0]);
  const mark = () => {
    const y = scrollY + innerHeight * 0.35; let cur = 'top';
    pos().forEach(([top, as]) => { if (top <= y) cur = as; });
    links.forEach(a => { const on = a.getAttribute('href') === '#' + cur; a.classList.toggle('active', on); if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
  };
  addEventListener('scroll', mark, { passive: true }); addEventListener('resize', mark); mark();
})();

const yr = document.getElementById('yr'); if (yr) yr.textContent = new Date().getFullYear();


// ---- Trust strip: shown under the hero (Home) and on every other page ----
// Add ONLY real, verifiable items. Anything left empty stays hidden.

const TRUST = {
  credentials: [],  // degrees, certifications, years of experience
  clubs:       [],  // sporting clubs / teams / academies you work with
  others:      []   // awards, associations (e.g. Indian Association of Physiotherapists), partners
};
// Text: 'Bachelor of Physiotherapy'   Logo: { name: 'Club name', logo: 'images/trust/club.webp' }

const TRUST_SAMPLE = {   // shown only at ?preview
  credentials: ['Sample credential one', 'Sample credential two'],
  clubs:       ['Sample sports club'],
  others:      ['Sample association']
};
const TRUST_GROUPS = [
  { key: 'credentials', title: 'Credentials',                icon: 'M12 2l8 3v6c0 5-3.4 9.4-8 11-4.6-1.6-8-6-8-11V5l8-3zm-1.2 13.6l5.6-5.6-1.4-1.4-4.2 4.2-2-2-1.4 1.4 3.4 3.4z' },
  { key: 'clubs',       title: 'Sporting clubs',             icon: 'M7 3h10v2h3v3a4 4 0 01-4 4h-.3A5 5 0 0113 15.9V18h3v3H8v-3h3v-2.1A5 5 0 018.3 12H8a4 4 0 01-4-4V5h3V3zm-1 4v1a2 2 0 002 2V7H6zm12 0h-2v3a2 2 0 002-2V7z' },
  { key: 'others',      title: 'Also recognised by',         icon: 'M12 2l3 6.5 7 .9-5.1 4.9 1.3 7-6.2-3.4L5.8 21l1.3-7L2 9.4l7-.9L12 2z' }
];

(function renderTrust() {
  const sections = document.querySelectorAll('.trust');
  const preview = new URLSearchParams(location.search).has('preview');
  const data = preview ? TRUST_SAMPLE : TRUST;
  const ns = 'http://www.w3.org/2000/svg';
  const icon = d => {
    const s = document.createElementNS(ns, 'svg');
    s.setAttribute('viewBox', '0 0 24 24'); s.setAttribute('aria-hidden', 'true');
    const p = document.createElementNS(ns, 'path'); p.setAttribute('d', d); s.appendChild(p);
    return s;
  };

  sections.forEach(sec => {
    const grid = sec.querySelector('.trust-grid');
    const more = sec.querySelector('.trust-more');
    let shown = 0;

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
})();


// ---- Google reviews (shown above the footer call-to-action on every page) ----
// Fill in your Google Business Profile links. Leave empty and the block stays hidden.
//  GOOGLE_REVIEWS_URL      -> your profile / reviews page
//  GOOGLE_WRITE_REVIEW_URL -> the "write a review" link (Google Business Profile > Get more reviews)
//  GOOGLE_RATING / COUNT   -> optional, e.g. 4.9 and 120. Only enter REAL figures.
// This block links OUT to Google and never copies review text onto the site.
const GOOGLE_REVIEWS_URL = 'https://www.google.com/maps?cid=15464404039475393364';
const GOOGLE_WRITE_REVIEW_URL = 'https://search.google.com/local/writereview?placeid=ChIJJRxpkxTFADsRVPMLPIqZnNY';
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

// ===== Scroll-story motion (home page only) =====
(function motion() {
  if (!document.querySelector('.mq')) return;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;   // CSS shows static versions
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const ease = t => 1 - Math.pow(1 - t, 3);
  const vh = () => window.innerHeight;
  const prog = el => { const r = el.getBoundingClientRect(); return clamp(-r.top / (r.height - vh())); };

  const marquee = document.querySelector('[data-marquee]');
  const floats = [...document.querySelectorAll('[data-float]')];
  const pills = document.querySelector('[data-pills]');
  const pl = pills ? [...pills.querySelectorAll('.pl')] : [];
  const swap = pills && pills.querySelector('[data-swap]');
  const words = ['pain-free', 'pregnancy-ready', 'postnatal-strong', 'moving freely'];
  let wi = 0;
  const arc = document.querySelector('[data-arc]');
  const arcItems = arc ? [...arc.querySelectorAll('.arc-track li')] : [];
  const grow = document.querySelector('[data-grow]');
  let arcPos = 0, arcTarget = 0, lastY = scrollY, vel = 0, mqX = 0;

  pl.forEach((p, i) => {
    p.style.setProperty('--x', ((3 + ((i * 5) % 6) * 15 + (i % 2) * 4) * (innerWidth < 700 ? 0.62 : 1)) + '%');
    const rot = ((i * 37) % 28 - 14) + 'deg';
    p.style.setProperty('--r', rot); p._rot = rot;
    p._h = 0.03 + Math.floor(i / 6) * 0.1 + (i % 3) * 0.02;
  });

  if (arc) {
    const stage = arc.querySelector('.arc-stage'); let dragX = null;
    stage.addEventListener('pointerdown', e => { dragX = e.clientX; stage.setPointerCapture(e.pointerId); stage.style.cursor = 'grabbing'; });
    stage.addEventListener('pointermove', e => { if (dragX === null) return; arcTarget -= (e.clientX - dragX) / 180; dragX = e.clientX; });
    const end = () => { dragX = null; stage.style.cursor = ''; arcTarget = Math.round(arcTarget); };
    stage.addEventListener('pointerup', end); stage.addEventListener('pointercancel', end);
    arc.tabIndex = 0;
    arc.addEventListener('keydown', e => { if (e.key === 'ArrowRight') arcTarget++; if (e.key === 'ArrowLeft') arcTarget--; });
  }

  function frame() {
    const y = scrollY; vel += ((y - lastY) - vel) * 0.15; lastY = y;
    mqX -= 0.6 + Math.abs(vel) * 0.25;
    const w = marquee.scrollWidth / 3; marquee.style.transform = `translateX(${mqX % w}px)`;
    floats.forEach(f => {
      const r = f.closest('section').getBoundingClientRect();
      if (r.bottom < -200 || r.top > vh() + 200) return;
      f.style.transform = `translateY(${(r.top + r.height / 2 - vh() / 2) * parseFloat(f.dataset.float)}px)`;
    });

    if (pills) {
      const p = prog(pills), H = vh();
      pl.forEach((el, i) => {
        const t = ease(clamp((p - i * 0.055) / 0.3));
        const land = H * (1 - el._h) - 60 - (innerWidth <= 820 ? 84 : 0);
        el.style.transform = `translateY(${-120 + (land + 120) * t}px) rotate(${el._rot})`;
      });
      const n = Math.min(words.length - 1, Math.floor(p * words.length));
      if (n !== wi) { wi = n; swap.classList.add('out'); setTimeout(() => { swap.textContent = words[wi]; swap.classList.remove('out'); }, 200); }
    }

    if (arc) {
      const r = arc.getBoundingClientRect();
      if (r.top < vh() && r.bottom > 0) {
        const nudge = (1 - clamp((r.top + r.height) / (vh() + r.height))) * arcItems.length * 0.8;
        arcPos += ((arcTarget + nudge) - arcPos) * 0.08;
        const N = arcItems.length, spread = innerWidth < 700 ? innerWidth * 0.58 : Math.min(innerWidth / 5, 230);
        arcItems.forEach((li, i) => {
          let d = i - arcPos; d = ((d + N / 2) % N + N) % N - N / 2;
          li.style.transform = `translate(${d * spread}px,${Math.pow(Math.abs(d), 1.7) * 18 + 30}px) rotate(${d * 7}deg)`;
          li.style.zIndex = 100 - Math.round(Math.abs(d) * 10);
          li.style.opacity = clamp(1.25 - Math.abs(d) * 0.28);
        });
      }
    }

    if (grow) {
      const p = prog(grow), c = grow.querySelector('.grow-circle');
      c.style.transform = `scale(${1 + ease(clamp(p / 0.55)) * (Math.hypot(innerWidth, vh()) / c.offsetWidth)})`;
      grow.querySelector('.grow-logo').style.opacity = 1 - clamp(p / 0.3);
      grow.querySelector('.grow-words').style.transform = `translateX(${(0.5 - p) * 40}vw)`;
      grow.querySelector('.grow-line').style.opacity = clamp((p - 0.6) / 0.25);
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();

// ===== Treatments (home): two groups, one shown at a time; each card opens its details =====
(function treatments() {
  const tabs = [...document.querySelectorAll('.ex-tab')];
  const sets = [...document.querySelectorAll('.ex-set')];
  const dlg = document.getElementById('exDialog');
  if (!tabs.length || !dlg) return;
  const show = g => {
    tabs.forEach((t, k) => { t.classList.toggle('on', k === g); t.setAttribute('aria-selected', k === g); });
    sets.forEach((el, k) => { el.hidden = k !== g; });
  };
  tabs.forEach((t, g) => t.addEventListener('click', () => show(g)));
  const body = dlg.querySelector('.ex-dbody');
  const panels = [...document.querySelectorAll('.ex-panel')]; let cur = 0;
  const render = i => { cur = (i + panels.length) % panels.length; body.innerHTML = panels[cur].innerHTML; dlg.scrollTop = 0; };
  const open = i => { if (i < 0) return; render(i); if (!dlg.open) dlg.showModal(); };
  document.querySelector('.ex-sets').addEventListener('click', e => { const c = e.target.closest('.ex-item'); if (c) open(panels.findIndex(p => p.dataset.slug === c.dataset.slug)); });
  dlg.querySelector('[data-ex-close]').addEventListener('click', () => dlg.close());
  dlg.querySelector('[data-ex-prev]').addEventListener('click', () => render(cur - 1));
  dlg.querySelector('[data-ex-next]').addEventListener('click', () => render(cur + 1));
  dlg.addEventListener('click', e => { if (e.target === dlg || e.target.closest('a')) dlg.close(); });
  dlg.addEventListener('keydown', e => { if (e.key === 'ArrowRight') render(cur + 1); if (e.key === 'ArrowLeft') render(cur - 1); });
  window.showTreatment = slug => {
    const c = document.querySelector('.ex-item[data-slug="' + slug + '"]'); if (!c) return;
    show(sets.findIndex(el => el.contains(c)));
    document.getElementById('explore').scrollIntoView({ behavior: 'smooth' });
    setTimeout(() => open(panels.findIndex(p => p.dataset.slug === slug)), 450);
  };
})();

// ===== Home animation layer =====
(function homeAnimation() {
  if (!document.querySelector('.hv')) return;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const seen = (els, fn, th = 0.25) => {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { fn(e.target); io.unobserve(e.target); } }), { threshold: th });
    els.forEach(el => io.observe(el));
  };

  // hero: layers follow the cursor
  const hero = document.querySelector('.hv');
  hero.addEventListener('pointermove', e => {
    const r = hero.getBoundingClientRect();
    hero.style.setProperty('--mx', ((e.clientX - r.left) / r.width - 0.5) * 2);
    hero.style.setProperty('--my', ((e.clientY - r.top) / r.height - 0.5) * 2);
  });
  hero.addEventListener('pointerleave', () => { hero.style.setProperty('--mx', 0); hero.style.setProperty('--my', 0); });

  // hero scroll-out: text drifts up, artwork shrinks and fades as the next section arrives
  const setHero = () => hero.style.setProperty('--hp', clamp(scrollY / (hero.offsetHeight * 0.8)).toFixed(3));
  addEventListener('scroll', setHero, { passive: true }); setHero();

  // magnetic hero buttons
  document.querySelectorAll('.hv-cta .btn').forEach(b => {
    b.classList.add('mag');
    b.addEventListener('pointermove', e => {
      const r = b.getBoundingClientRect();
      b.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * 0.18}px,${(e.clientY - r.top - r.height / 2) * 0.3}px)`;
    });
    b.addEventListener('pointerleave', () => b.style.transform = '');
  });

  // counters count up when the facts row appears
  seen([...document.querySelectorAll('[data-count]')], el => {
    const to = +el.dataset.count, t0 = performance.now();
    (function tick(t) {
      const k = clamp((t - t0) / 1400); el.textContent = Math.round(to * (1 - Math.pow(1 - k, 3)));
      if (k < 1) requestAnimationFrame(tick);
    })(t0);
  }, 0.6);

  // section headings: words rise into place
  document.querySelectorAll('.ex-head h2,.stp .head h2,.arc h2').forEach(h => {
    const text = h.textContent.trim(); h.setAttribute('aria-label', text); h.textContent = '';
    text.split(/\s+/).forEach((w, i) => {
      const o = document.createElement('span'); o.className = 'sw'; o.setAttribute('aria-hidden', 'true');
      const s = document.createElement('span'); s.style.setProperty('--i', i); s.textContent = w;
      o.appendChild(s); h.append(o, ' ');
    });
    h.classList.add('split');
  });
  seen([...document.querySelectorAll('.split')], el => el.classList.add('in'), 0.6);

  // big band slides in
  const big = document.querySelector('.big'); if (big) seen([big], el => el.classList.add('in'), 0.4);
})();


/* Hero background video: starts reliably, fades in over the poster, and rests when it is off screen or the tab is hidden */
(() => {
  const v = document.querySelector('.hvi-vid'); if (!v) return;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) { v.pause(); return; }
  // The video file is large: attach it only after the page has loaded (poster shows until then),
  // and skip it entirely when the visitor has Data Saver on.
  const conn = navigator.connection;
  if (conn && conn.saveData) return;
  let loaded = !v.dataset.src;
  const start = () => { if (!loaded) return; const p = v.play(); if (p && p.catch) p.catch(() => {}); };
  const attach = () => {
    if (loaded) return; loaded = true;
    // Phones in portrait get a full-resolution 9:16 cut of the same video (smaller file, same sharpness)
    const phone = v.dataset.srcM && matchMedia('(max-width: 820px) and (orientation: portrait)').matches;
    if (phone) v.classList.add('is-m');
    v.src = phone ? v.dataset.srcM : v.dataset.src; v.preload = 'auto'; v.load(); start();
  };
  if (document.readyState === 'complete') setTimeout(attach, 300);
  else addEventListener('load', () => setTimeout(attach, 300), { once: true });
  v.addEventListener('playing', () => v.classList.add('is-playing'));
  v.addEventListener('canplay', start);
  v.addEventListener('error', () => v.classList.remove('is-playing'));   // poster stays visible
  start();
  // some phones block autoplay until the first touch
  ['touchstart', 'pointerdown', 'scroll'].forEach(ev => addEventListener(ev, () => { if (v.paused) start(); }, { once: true, passive: true }));
  let inView = true;
  const covered = () => { const h = document.querySelector('.hvi'); return !!h && h.classList.contains('is-covered'); };
  const sync = () => { if (document.hidden || !inView || covered()) v.pause(); else if (v.paused) start(); };
  addEventListener('scroll', () => requestAnimationFrame(sync), { passive: true });
  document.addEventListener('visibilitychange', sync);
  if ('IntersectionObserver' in window) new IntersectionObserver(es => { inView = es[0].isIntersecting; sync(); }, { threshold: 0.02 }).observe(v);
})();

/* Instagram: uniform post cards (they link to the real posts) + arrows */
(() => {
  const sec = document.getElementById('instagram'); if (!sec) return;
  const track = sec.querySelector('[data-ig-track]'), next = sec.querySelector('.igp-next'), prev = sec.querySelector('.igp-prev');
  const behavior = matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
  const step = () => Math.max(260, track.clientWidth * 0.8);
  next.addEventListener('click', () => track.scrollBy({ left: step(), behavior }));
  prev.addEventListener('click', () => track.scrollBy({ left: -step(), behavior }));
  const sync = () => { prev.hidden = track.scrollLeft < 8; next.hidden = track.scrollLeft + track.clientWidth >= track.scrollWidth - 8; };
  track.addEventListener('scroll', sync, { passive: true }); addEventListener('resize', sync); sync();

})();

/* "Join the movement": a normal-height section. When it scrolls into view the pills pop in one after
   another, and the highlighted word in the heading cycles while the section is on screen. */
(() => {
  const pills = document.querySelector('[data-pills]'); if (!pills) return;
  const pl = [...pills.querySelectorAll('.pl')], swap = pills.querySelector('[data-swap]');
  pl.forEach((p, i) => { p.style.setProperty('--r', ((i * 37) % 7 - 3) + 'deg'); p.style.setProperty('--k', i); });
  const words = ['pain-free', 'pregnancy-ready', 'postnatal-strong', 'moving freely'];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!('IntersectionObserver' in window)) { pills.classList.add('in'); return; }
  let wi = 0, timer = null;
  const cycle = () => { swap.classList.add('out'); setTimeout(() => { wi = (wi + 1) % words.length; swap.textContent = words[wi]; swap.classList.remove('out'); }, 220); };
  new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { pills.classList.add('in'); if (!reduce && swap && !timer) timer = setInterval(cycle, 2400); }
    else if (timer) { clearInterval(timer); timer = null; }
  }), { threshold: 0.2 }).observe(pills);
})();

/* Instagram cards: the share button shares (or copies) the link to that post */
document.addEventListener('click', e => {
  const sh = e.target.closest('[data-share]'); if (!sh) return;
  const url = sh.dataset.share;
  if (navigator.share) { navigator.share({ title: 'SHEroots Physiotherapy Clinic', url }).catch(() => {}); return; }
  const done = () => { sh.classList.add('copied'); setTimeout(() => sh.classList.remove('copied'), 1800); };
  if (navigator.clipboard) navigator.clipboard.writeText(url).then(done, done); else done();
});

/* How we treat: accordion of technique panels */
(() => {
  const acc = document.querySelector('.mt-acc'); if (!acc) return;
  const pans = [...acc.querySelectorAll('.mt-pan')];
  const set = p => pans.forEach(x => { const on = x === p; x.classList.toggle('on', on); x.querySelector('.mt-tab').setAttribute('aria-expanded', on); });
  pans.forEach(p => {
    const tab = p.querySelector('.mt-tab');
    tab.addEventListener('click', () => set(p));
    tab.addEventListener('focus', () => set(p));
    p.addEventListener('mouseenter', () => { if (matchMedia('(hover:hover) and (min-width:821px)').matches) set(p); });
  });
})();

/* First visit ticket: fill the progress line when it comes into view */
(() => {
  const el = document.querySelector('.ftk'); if (!el) return;
  if (!('IntersectionObserver' in window)) { el.classList.add('in'); return; }
  const io = new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { el.classList.add('in'); io.disconnect(); } }, { threshold: 0.35 });
  io.observe(el);
})();

/* Stage selector */
(() => {
  const tabs = [...document.querySelectorAll('.ls-tab')]; if (!tabs.length) return;
  const panels = [...document.querySelectorAll('.ls-panel')];
  const pick = i => { tabs.forEach((b, k) => { b.classList.toggle('on', k === i); b.setAttribute('aria-selected', k === i); });
    panels.forEach((p, k) => { p.hidden = k !== i; p.classList.toggle('on', k === i); }); };
  tabs.forEach((b, i) => {
    b.addEventListener('click', () => pick(i));
    b.addEventListener('mouseenter', () => { if (matchMedia('(hover:hover) and (min-width:901px)').matches) pick(i); });
    b.addEventListener('keydown', e => { const d = e.key === 'ArrowDown' || e.key === 'ArrowRight' ? 1 : e.key === 'ArrowUp' || e.key === 'ArrowLeft' ? -1 : 0;
      if (d) { e.preventDefault(); const n = (i + d + tabs.length) % tabs.length; tabs[n].focus(); pick(n); } });
  });
})();

// Phone quick-action bar: tuck it away while the booking form or the footer is on screen
// (both already have their own Call / WhatsApp actions, and the footer then needs no extra bottom space)
(() => {
  const bar = document.querySelector('.mobile-bar');
  const targets = [document.getElementById('contact'), document.querySelector('footer.sf')].filter(Boolean);
  if (!bar || !targets.length || !('IntersectionObserver' in window)) return;
  const on = new Set();
  const io = new IntersectionObserver(es => {
    es.forEach(e => (e.isIntersecting && e.intersectionRatio >= (e.target.id === 'contact' ? 0.25 : 0)) ? on.add(e.target) : on.delete(e.target));
    bar.classList.toggle('is-away', on.size > 0);
  }, { threshold: [0, 0.25] });
  targets.forEach(t => io.observe(t));
})();

// FAQ chat accordion: one answer open at a time, click the open one to close it
document.addEventListener('click', e => {
  const q = e.target.closest('.fc-q'); if (!q) return;
  const item = q.closest('.fc-item'), willOpen = !item.classList.contains('open');
  item.parentElement.querySelectorAll('.fc-item').forEach(it => {
    const on = it === item && willOpen;
    it.classList.toggle('open', on);
    it.querySelector('.fc-q').setAttribute('aria-expanded', on);
  });
});

// Patient stories: slide left / right with the arrows (swipe or scroll also works)
(() => {
  const wrap = document.querySelector('.rvs-wrap'); if (!wrap) return;
  const track = wrap.querySelector('.rvs-track'), prev = wrap.querySelector('.rvs-prev'), next = wrap.querySelector('.rvs-next');
  const step = () => { const c = track.querySelector('.rv'); return c ? c.getBoundingClientRect().width + 22 : 300; };
  const sync = () => { prev.disabled = track.scrollLeft < 8; next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 8; };
  prev.addEventListener('click', () => track.scrollBy({ left: -step(), behavior: 'smooth' }));
  next.addEventListener('click', () => track.scrollBy({ left: step(), behavior: 'smooth' }));
  track.addEventListener('scroll', sync, { passive: true }); addEventListener('resize', sync); sync();
})();

// Patient stories: staggered testimonial cards. Click a card (or use the arrows) to bring it to the centre.
(() => {
  const sec = document.querySelector('.rvs'), src = sec && sec.querySelector('.rvs-track'); if (!src) return;
  const data = [...src.querySelectorAll('.rv')].map((c, i) => ({
    id: i, name: c.querySelector('h3').textContent.trim(), role: c.querySelector('.rv-role').textContent.trim(),
    q: c.querySelector('.rv-q').textContent.trim()
  }));
  if (data.length < 3) return;
  const STAR = '<svg viewBox="0 0 16 15" aria-hidden="true"><path d="M7.524.464a.5.5 0 0 1 .952 0l1.432 4.41a.5.5 0 0 0 .476.345h4.637a.5.5 0 0 1 .294.904L11.563 8.85a.5.5 0 0 0-.181.559l1.433 4.41a.5.5 0 0 1-.77.559L8.294 11.65a.5.5 0 0 0-.588 0l-3.751 2.726a.5.5 0 0 1-.77-.56l1.433-4.41a.5.5 0 0 0-.181-.558L.685 6.123A.5.5 0 0 1 .98 5.22h4.637a.5.5 0 0 0 .476-.346z"/></svg>';
  const ARROW = d => '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="' + d + '"/></svg>';
  const stage = document.createElement('div'); stage.className = 'stg'; stage.setAttribute('role', 'region'); stage.setAttribute('aria-label', 'Patient stories');
  const cards = new Map(), prevPos = new Map();
  data.forEach(t => {
    const el = document.createElement('div'); el.className = 'stg-card'; el.tabIndex = 0; el.setAttribute('role', 'button'); el.setAttribute('aria-label', 'Show story from ' + t.name);
    el.innerHTML = '<div class="stg-top"><span class="stg-av" aria-hidden="true"></span><span class="stg-stars" role="img" aria-label="5 out of 5 stars">' + STAR.repeat(5) + '</span></div><h3 class="stg-q"></h3><p class="stg-by"></p>';
    el.querySelector('.stg-av').textContent = t.name[0]; el.querySelector('.stg-q').textContent = t.q; el.querySelector('.stg-by').textContent = '\u2014 ' + t.name + ', ' + t.role;
    cards.set(t.id, el); stage.appendChild(el);
  });
  const nav = document.createElement('div'); nav.className = 'stg-nav';
  nav.innerHTML = '<button type="button" aria-label="Previous story">' + ARROW('M15 5l-7 7 7 7') + '</button><span class="stg-count" aria-live="polite"></span><button type="button" aria-label="Next story">' + ARROW('M9 5l7 7-7 7') + '</button>';
  stage.appendChild(nav);
  sec.querySelector('.wrap').appendChild(stage); sec.classList.add('has-stage');

  const ci = data.length % 2 ? (data.length + 1) / 2 : data.length / 2;
  let list = [...data.slice(-ci), ...data.slice(0, data.length - ci)], size = 365;   // first story starts in the centre
  const render = () => {
    const n = list.length;
    list.forEach((t, idx) => {
      const pos = n % 2 ? idx - (n + 1) / 2 : idx - n / 2, el = cards.get(t.id), center = pos === 0;
      const wrapped = prevPos.has(t.id) && Math.abs(pos - prevPos.get(t.id)) > n / 2;
      if (wrapped) el.style.transition = 'none';
      el.style.width = el.style.height = size + 'px';
      el.style.transform = 'translate(-50%,-50%) translateX(' + (size / 1.34) * pos + 'px) translateY(' + (center ? -40 : pos % 2 ? 10 : -10) + 'px) rotate(' + (center ? 0 : pos % 2 ? 1.6 : -1.6) + 'deg)';
      el.style.opacity = 1; el.style.zIndex = center ? 10 : 6 - Math.abs(pos);   // nearer cards sit on top, so text never shows through
      el.classList.toggle('is-center', center); el.dataset.pos = pos;
      if (wrapped) { void el.offsetWidth; el.style.transition = ''; }
      prevPos.set(t.id, pos);
    });
    const cur = list[n % 2 ? (n + 1) / 2 : n / 2];
    nav.querySelector('.stg-count').textContent = String(cur.id + 1).padStart(2, '0') + ' / ' + String(n).padStart(2, '0');
  };
  const move = steps => {
    const l = list.slice();
    if (steps > 0) for (let i = 0; i < steps; i++) l.push(l.shift());
    else for (let i = 0; i < -steps; i++) l.unshift(l.pop());
    list = l; render();
  };
  // phones: a simple swipe row (one card at a time); the cards keep their order and the one in the middle is highlighted
  const rowMq = matchMedia('(max-width: 639px)'), rowMode = () => rowMq.matches;
  const dots = document.createElement('div'); dots.className = 'stg-dots'; dots.setAttribute('aria-hidden', 'true');
  data.forEach(() => dots.appendChild(document.createElement('i')));
  stage.parentNode.insertBefore(dots, stage.nextSibling);
  const cardList = [...cards.values()];
  const syncRow = () => {
    if (!rowMode()) return;
    const mid = stage.scrollLeft + stage.clientWidth / 2; let best = 0, bd = 1e9;
    cardList.forEach((c, i) => { const d = Math.abs(c.offsetLeft + c.offsetWidth / 2 - mid); if (d < bd) { bd = d; best = i; } });
    cardList.forEach((c, i) => { c.classList.toggle('is-center', i === best); dots.children[i].classList.toggle('on', i === best); });
  };
  stage.addEventListener('scroll', syncRow, { passive: true });
  rowMq.addEventListener('change', () => { stage.scrollLeft = 0; if (rowMode()) syncRow(); else render(); });
  stage.addEventListener('click', e => { if (rowMode()) return; const c = e.target.closest('.stg-card'); if (c) move(+c.dataset.pos); });
  stage.addEventListener('keydown', e => { if (rowMode()) return; const c = e.target.closest('.stg-card'); if (c && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); move(+c.dataset.pos); } });
  nav.children[0].addEventListener('click', () => move(-1)); nav.children[2].addEventListener('click', () => move(1));
  const mq = matchMedia('(min-width: 640px)'), size_ = () => { size = mq.matches ? 365 : Math.min(320, innerWidth - 44); render(); };
  addEventListener('resize', size_); size_(); syncRow();
})();

// Stacking cards (Every stage of life, Book a Session): each card scales back a little as the next one slides over it.
document.querySelectorAll('[data-stack]').forEach(wrap => {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const cards = [...wrap.querySelectorAll('.sk-card')], n = cards.length;
  const update = () => {
    const r = wrap.getBoundingClientRect(), span = r.height - innerHeight;
    const p = span > 0 ? Math.min(1, Math.max(0, -r.top / span)) : 0;
    cards.forEach((c, i) => {
      const from = i / n, t = Math.min(1, Math.max(0, (p - from) / (1 - from))), to = 1 - (n - i) * 0.03;
      c.style.transform = 'scale(' + (1 + (to - 1) * t).toFixed(4) + ')';
    });
  };
  addEventListener('scroll', update, { passive: true }); addEventListener('resize', update); update();
});

// Hero: the last word of the headline slides to a new one every few seconds
(() => {
  const w = document.querySelector('.hvi h1 .rw'); if (!w) return;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const words = w.dataset.words.split('|'); let i = 0;
  setInterval(() => {
    if (document.hidden) return;
    w.classList.add('out');
    setTimeout(() => {
      i = (i + 1) % words.length; w.textContent = words[i];
      w.classList.remove('out'); w.classList.add('in');
      void w.offsetWidth; w.classList.remove('in');
    }, 360);
  }, 2600);
})();

// Booking form: only allow today or later for the preferred date
(() => { const d = document.querySelector('#bookForm input[name="date"]'); if (!d) return; const t = new Date(); d.min = t.getFullYear() + '-' + String(t.getMonth() + 1).padStart(2, '0') + '-' + String(t.getDate()).padStart(2, '0'); })();

// Our promise: slide the six cards left / right
(() => {
  const rail = document.querySelector('.pp-rail'); if (!rail) return;
  const sec = rail.closest('section'), list = rail.querySelector('.pp-list'), prev = sec.querySelector('.pp-prev'), next = sec.querySelector('.pp-next'), cnt = sec.querySelector('.pp-count');
  const cards = [...list.querySelectorAll('.pp-card')];
  const step = () => cards[0].getBoundingClientRect().width + parseFloat(getComputedStyle(list).columnGap || 18);
  const sync = () => {
    prev.disabled = list.scrollLeft < 8; next.disabled = list.scrollLeft + list.clientWidth >= list.scrollWidth - 8;
    const i = Math.min(cards.length, Math.round(list.scrollLeft / step()) + 1); cnt.textContent = String(i).padStart(2, '0') + ' / ' + String(cards.length).padStart(2, '0');
  };
  prev.addEventListener('click', () => list.scrollBy({ left: -step(), behavior: 'smooth' }));
  next.addEventListener('click', () => list.scrollBy({ left: step(), behavior: 'smooth' }));
  list.addEventListener('scroll', sync, { passive: true }); addEventListener('resize', sync); sync();
})();

/* ===== Scroll reveal (whole page) =====
   One system for every section. Blocks fade up once as they come into view; blocks that arrive
   together are staggered. Scroll-based (not IntersectionObserver) so anything the visitor jumps
   past with a menu link / #anchor / fast scroll is also revealed and never stays invisible. */
(() => {
  const AUTO = ['.why-head', '.ex-tabs', '.ex-sets', '.pr-step', '.pr-cta', '.dr3-art', '.dr3-photo', '.dr3-panel',
    '.pp-rail', '.igp-head', '.igp-rail', '.igp-foot', '.visit-info', '.visit-map', '.rvs-wrap', '.faq-head',
    '.faq-help', '.cf-left', '.cf-right', 'footer.footer'];
  const GROUPS = ['.why-cards', '.ab3-cards', '.dr3-tiles', '.visit-list', '.cf-rows', '.faq-chat', '.sf-main'];   // children rise one after another
  const seen = new Set(document.querySelectorAll('.reveal'));
  document.querySelectorAll(AUTO.join(',')).forEach(el => { if (!seen.has(el) && !el.closest('.reveal')) { el.classList.add('reveal'); seen.add(el); } });
  document.querySelectorAll(GROUPS.join(',')).forEach(g => {
    g.classList.add('rv-kids'); seen.add(g);
    [...g.children].forEach((c, i) => c.style.setProperty('--d', Math.min(i, 7) * 90 + 'ms'));
  });
  let pending = [...seen];
  if (!pending.length) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let queued = false;
  const check = () => {
    queued = false;
    const H = innerHeight, line = H * 0.92;           // reveal a little before the block is fully on screen
    const atEnd = scrollY + H >= document.documentElement.scrollHeight - 4;      // bottom of the page: nothing can scroll further, so reveal what is left
    const due = pending.filter(el => atEnd || el.getBoundingClientRect().top < line);
    if (!due.length) return;
    pending = pending.filter(el => !due.includes(el));
    due.forEach((el, i) => {
      const r = el.getBoundingClientRect();
      const offscreen = r.bottom < 0;                  // jumped past it: show instantly, no animation
      el.style.transitionDelay = (offscreen || reduce) ? '0ms' : Math.min(i, 4) * 90 + 'ms';
      if (offscreen) { el.style.transition = 'none'; el.classList.add('rv-now'); }
      el.classList.add('in');
      const done = () => { el.style.transitionDelay = ''; el.style.transition = ''; };
      if (offscreen) requestAnimationFrame(() => requestAnimationFrame(done));
      else setTimeout(done, 1100);                     // free hover transitions from the stagger delay
    });
    if (!pending.length) { removeEventListener('scroll', req); removeEventListener('resize', req); }
  };
  const req = () => { if (!queued) { queued = true; requestAnimationFrame(check); } };
  addEventListener('scroll', req, { passive: true });
  addEventListener('resize', req);
  addEventListener('load', req);
  check();
  setTimeout(req, 400);                                // after fonts / late layout settle
})();

/* ===== One overlay: the top banner stays still while the next section slides up over it ===== */
(() => {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const hero = document.querySelector('main > section.hvi');
  const next = hero && hero.nextElementSibling;
  if (!hero || !next) return;
  hero.classList.add('stk');
  next.classList.add('stk-over');
  const shade = document.createElement('i'); shade.className = 'stk-shade'; shade.setAttribute('aria-hidden', 'true'); hero.appendChild(shade);
  const place = () => { hero.style.top = Math.min(0, innerHeight - hero.offsetHeight) + 'px'; };
  let queued = false;
  const depth = () => {
    queued = false;
    const h = Math.min(innerHeight, hero.offsetHeight);
    const p = Math.min(1, Math.max(0, 1 - next.getBoundingClientRect().top / h));
    hero.style.transformOrigin = hero.offsetHeight > innerHeight ? 'center bottom' : 'center top';
    hero.style.transform = p > 0 ? 'scale(' + (1 - 0.06 * p).toFixed(4) + ')' : '';
    shade.style.opacity = (0.42 * p).toFixed(3);
    // once the next section fully covers the banner, hide it so it can never show through the sections further down
    const covered = p >= 1;
    hero.style.visibility = covered ? 'hidden' : '';
    hero.classList.toggle('is-covered', covered);
  };
  const req = () => { if (!queued) { queued = true; requestAnimationFrame(depth); } };
  addEventListener('scroll', req, { passive: true });
  addEventListener('resize', () => { place(); req(); }); addEventListener('load', place);
  if ('ResizeObserver' in window) new ResizeObserver(place).observe(hero);
  place(); depth();
})();

/* ===== Scroll motion kit: a different kind of scroll animation for each part of the page =====
   words rise in headings · slide from left / right · zoom · blur-to-sharp · 3D flip · wipe (mask)
   cards that rise one by one · scroll-linked zoom of photos · parallax drift of icons · growing kicker lines
. Everything is switched off for people who prefer reduced motion. */
(() => {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const ease = t => 1 - Math.pow(1 - t, 3);
  const $$ = s => [...document.querySelectorAll(s)];

  /* 1 · reveal styles per block */
  const variant = (sel, cls) => $$(sel).forEach(e => e.classList.add(cls));
  variant('.why-head, .igp-head', 'rv-blur');
  variant('.ex-tabs, .pr-cta, .rvs-wrap, .pr-step:nth-child(2), .igp-foot', 'rv-zoom');
  variant('.ex-sets', 'rv-blur');
  variant('.pr-step:nth-child(1), .faq-help', 'rv-left');
  variant('.pr-step:nth-child(3)', 'rv-right');
  variant('.igp-rail', 'rv-flip');
  variant('.visit-map', 'rv-mask');
  $$('.why-cards').forEach(e => e.dataset.kv = 'flip');
  $$('.ab3-cards, .dr3-tiles').forEach(e => e.dataset.kv = 'left');
  $$('.visit-list, .faq-chat').forEach(e => e.dataset.kv = 'right');
  $$('.cf-rows').forEach(e => e.dataset.kv = 'zoom');

  /* 2 · section headings: the words rise into place (keeps the italic / coloured words) */
  const heads = $$('main section h2').filter(h => !h.closest('.pills, .dr3-panel, .hvi') && !h.matches('.cf-title') && !h.classList.contains('split'));
  heads.forEach(h => {
    h.setAttribute('aria-label', h.textContent.trim().replace(/\s+/g, ' '));
    let n = 0;
    const walk = node => {
      [...node.childNodes].forEach(c => {
        if (c.nodeType === 3) {
          const frag = document.createDocumentFragment();
          c.textContent.split(/(\s+)/).forEach(part => {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.append(' '); return; }
            const o = document.createElement('span'); o.className = 'sw'; o.setAttribute('aria-hidden', 'true');
            const s = document.createElement('span'); s.style.setProperty('--i', n++); s.textContent = part;
            o.appendChild(s); frag.append(o);
          });
          c.replaceWith(frag);
        } else if (c.nodeType === 1) walk(c);
      });
    };
    walk(h); h.classList.add('split');
  });

  /* 3 · scroll-linked motion (runs every frame while scrolling) */
  const zoomers = $$('.pr-img, .dr3-photo, .visit-map, .cf-card, .stg').map(el => ({ el, from: el.matches('.dr3-photo') ? 0.9 : 0.86 }));
  const drifters = $$('.why-cards img, .ab3-ic img, .pp-ph').map(el => ({ el, amp: el.matches('.pp-ph') ? 10 : 16 }));
  const lines = $$('.kicker i, .why-k i, .ab3-k i, .ab3-k::before').filter(Boolean);
  const pending = new Set(heads.concat($$('.split')));
  let queued = false;
  const frame = () => {
    queued = false;
    const H = innerHeight, max = document.documentElement.scrollHeight - H;
    const atEnd = scrollY + H >= document.documentElement.scrollHeight - 4;
    pending.forEach(h => { if (atEnd || h.getBoundingClientRect().top < H * 0.9) { h.classList.add('in'); pending.delete(h); } });
    zoomers.forEach(z => {
      const r = z.el.getBoundingClientRect(); if (r.bottom < -50 || r.top > H + 50) return;
      const q = ease(clamp((H - r.top) / (H * 0.65)));
      z.el.style.scale = (z.from + (1 - z.from) * q).toFixed(4);
    });
    drifters.forEach(d => {
      const r = d.el.getBoundingClientRect(); if (r.bottom < -50 || r.top > H + 50) return;
      const p = clamp((H - r.top) / (H + r.height));
      d.el.style.translate = '0 ' + ((0.5 - p) * 2 * d.amp).toFixed(1) + 'px';
    });
    lines.forEach(l => {
      const r = l.getBoundingClientRect(); if (r.bottom < -50 || r.top > H + 50) return;
      l.style.scale = clamp((H * 0.95 - r.top) / (H * 0.3)).toFixed(3) + ' 1';
    });
  };
  const req = () => { if (!queued) { queued = true; requestAnimationFrame(frame); } };
  addEventListener('scroll', req, { passive: true }); addEventListener('resize', req); addEventListener('load', req);
  frame(); setTimeout(req, 500);
})();

/* ===== "Track my request": the visitor's own browser remembers their booking requests. A tab on the
   left edge opens a panel with the live status of each one (checked again every 30 seconds while the
   page is open), and a note pops up as soon as the clinic confirms or declines. Patients on another
   phone/browser can find their booking with the reference + phone number. ===== */
(function myBooking() {
  const KEY = 'sheBookings', POLL = 30000;
  const read = () => { try { const l = JSON.parse(localStorage.getItem(KEY) || '[]'); return Array.isArray(l) ? l : []; } catch (e) { return []; } };
  const write = list => { try { localStorage.setItem(KEY, JSON.stringify(list.slice(-5))); } catch (e) {} };
  const mk = (tag, cls, txt) => { const x = document.createElement(tag); if (cls) x.className = cls; if (txt != null) x.textContent = txt; return x; };
  const today = () => { const t = new Date(); t.setHours(0, 0, 0, 0); return t; };
  const LABEL = { pending: 'Waiting for confirmation', confirmed: 'Confirmed', declined: 'Not available', cancelled: 'Cancelled' };
  const NEWS = {
    pending: s => 'Your booking request for ' + s.when + ' has reached the clinic. We will confirm it with you shortly.',
    confirmed: s => 'Your appointment on ' + s.when + ' is confirmed. We look forward to seeing you.',
    declined: s => 'We could not confirm ' + s.when + '. Please choose another time.',
    cancelled: s => 'Your booking for ' + s.when + ' was cancelled.'
  };
  const apiOf = b => b.url.replace('/api/b/', '/api/s/');

  // forget appointments whose day has passed
  write(read().filter(b => b && b.ref && b.url && (!b.date || new Date(b.date + 'T00:00') >= today())));

  /* ---- side tab + panel ---- */
  const tab = mk('button', 'trk-tab'); tab.type = 'button'; tab.setAttribute('aria-haspopup', 'dialog'); tab.setAttribute('aria-controls', 'trkPanel');
  tab.append(mk('span', 'trk-tab-txt', 'Track my request'), mk('span', 'trk-dot'));
  const panel = mk('div', 'trk-panel'); panel.id = 'trkPanel'; panel.hidden = true;
  panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-modal', 'false'); panel.setAttribute('aria-labelledby', 'trkTitle');
  const head = mk('div', 'trk-head'); const h = mk('h2', '', 'Track my request'); h.id = 'trkTitle';
  const close = mk('button', 'trk-x', '×'); close.type = 'button'; close.setAttribute('aria-label', 'Close');
  head.append(h, close);
  const listEl = mk('div', 'trk-list');
  const find = mk('form', 'trk-find'); find.noValidate = true;
  find.innerHTML = '<p class="trk-find-h">Booked on another phone or browser?</p>' +
    '<label>Booking reference<input name="ref" autocomplete="off" placeholder="e.g. SHE-261117-AB12CD" required></label>' +
    '<label>Phone number<input name="phone" inputmode="numeric" autocomplete="tel" maxlength="14" placeholder="10-digit mobile" required></label>' +
    '<button type="submit" class="btn">Find my booking</button><p class="trk-find-note" role="status"></p>';
  panel.append(head, listEl, find);
  document.body.append(tab, panel);

  const openPanel = () => { if (bar) bar.querySelector('.mybk-x').click(); const chatX = document.querySelector('.chat.open .chat-close'); if (chatX) chatX.click(); panel.hidden = false; tab.setAttribute('aria-expanded', 'true'); tab.classList.remove('has-news'); requestAnimationFrame(() => panel.classList.add('in')); render(); refresh(); close.focus(); };
  const closePanel = () => { panel.classList.remove('in'); tab.setAttribute('aria-expanded', 'false'); setTimeout(() => { if (!panel.classList.contains('in')) panel.hidden = true; }, 250); };
  tab.addEventListener('click', () => panel.hidden ? openPanel() : closePanel());
  close.addEventListener('click', () => { closePanel(); tab.focus(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !panel.hidden) { closePanel(); tab.focus(); } });
  document.addEventListener('click', e => { if (!panel.hidden && !panel.contains(e.target) && !tab.contains(e.target) && !e.target.closest('.mybk')) closePanel(); });
  document.addEventListener('click', e => { const a = e.target.closest('[data-track-open]'); if (a) { e.preventDefault(); openPanel(); } });
  window.sheOpenTracker = openPanel;

  function render() {
    const list = read().slice().reverse();
    listEl.replaceChildren();
    tab.classList.toggle('has-items', list.length > 0);
    tab.hidden = !list.length;      // the side tab appears only once this browser has a booking
    if (!list.length) { listEl.append(mk('p', 'trk-empty', 'When you send a booking request on this site, its status shows up here, so you can see the moment the clinic confirms it.')); return; }
    list.forEach(b => {
      const st = b.st || 'pending';
      const card = mk('div', 'trk-card trk-' + st);
      const top = mk('div', 'trk-card-top'); top.append(mk('span', 'trk-pill', LABEL[st] || st), mk('span', 'trk-ref', b.ref));
      card.append(top, mk('p', 'trk-when', (b.when || b.date || '') + (b.concern ? ' · ' + b.concern : '')));
      if (st === 'pending') card.append(mk('p', 'trk-sub', 'The clinic will confirm by WhatsApp or a call. This updates by itself.'));
      const acts = mk('div', 'trk-acts');
      if (st === 'declined' || st === 'cancelled') { const a = mk('a', '', 'Book another time'); a.href = SITE_ROOT + 'index.html#contact'; a.addEventListener('click', closePanel); acts.append(a); }
      const v = mk('a', '', st === 'pending' || st === 'confirmed' ? 'View or cancel' : 'View details'); v.href = b.url; v.target = '_blank'; v.rel = 'noopener'; acts.append(v);
      if (st === 'declined' || st === 'cancelled') { const rm = mk('button', 'trk-rm', 'Remove'); rm.type = 'button'; rm.addEventListener('click', () => { write(read().filter(y => y.ref !== b.ref)); render(); }); acts.append(rm); }
      card.append(acts);
      listEl.append(card);
    });
  }

  /* ---- pop-up note when the status changes ---- */
  let bar = null;
  function notify(b, s) {
    const text = NEWS[s.status]; if (!text) return;
    if (bar) bar.remove();
    bar = mk('div', 'mybk mybk-' + s.status); bar.setAttribute('role', 'status');
    const go = mk('button', 'mybk-go', s.status === 'declined' ? 'Choose another time' : 'View booking'); go.type = 'button';
    go.addEventListener('click', () => { dismiss(); if (s.status === 'declined') location.href = SITE_ROOT + 'index.html#contact'; else openPanel(); });
    const x = mk('button', 'mybk-x', '×'); x.type = 'button'; x.setAttribute('aria-label', 'Dismiss');
    const dismiss = () => { tab.classList.remove('has-news'); if (bar) { bar.remove(); bar = null; } write(read().map(y => y.ref === b.ref ? Object.assign(y, { seen: s.status }) : y)); };
    x.addEventListener('click', dismiss);
    bar.append(mk('span', 'mybk-pill', LABEL[s.status]), mk('span', 'mybk-msg', text(s)), go, x);
    document.body.appendChild(bar);
    requestAnimationFrame(() => bar && bar.classList.add('in'));
    if (panel.hidden) tab.classList.add('has-news');
  }

  /* ---- live status ---- */
  let busy = false;
  function refresh() {
    const list = read();
    if (busy || !list.length || !('fetch' in window)) return render();
    busy = true;
    Promise.all(list.map(b => fetch(apiOf(b), { cache: 'no-store' }).then(r => r.ok ? r.json() : null).catch(() => null).then(s => [b, s])))
      .then(res => {
        busy = false;
        let news = null;
        const cur = read();
        res.forEach(([b, s]) => {
          if (!s || !s.ok) return;
          const y = cur.find(z => z.ref === b.ref); if (!y) return;
          Object.assign(y, { st: s.status, when: s.when, concern: s.concern, date: s.date });
          if (y.seen !== s.status) news = [y, s];     // newest booking with unseen news wins
        });
        write(cur); render();
        if (news && !(bar && bar.classList.contains('mybk-' + news[1].status))) notify(news[0], news[1]);
      });
  }

  // called by the booking form and the chat assistant after a successful request
  window.sheRememberBooking = j => {
    if (!j || !j.ref || !j.status_url) return;
    write(read().filter(b => b.ref !== j.ref).concat([{ ref: j.ref, url: j.status_url, date: j.date || '', when: j.when || '', concern: j.concern || '', st: j.status || 'pending', seen: 'pending' }]));
    render(); tab.classList.add('pulse'); setTimeout(() => tab.classList.remove('pulse'), 2400);
  };

  /* ---- find a booking from another device ---- */
  const fPhone = find.querySelector('[name="phone"]'), fNote = find.querySelector('.trk-find-note');
  fPhone.addEventListener('input', () => { let d = fPhone.value.replace(/\D/g, ''); if (d.length > 10 && d.startsWith('91')) d = d.slice(2); fPhone.value = d.slice(0, 10); });
  find.addEventListener('submit', e => {
    e.preventDefault();
    const ref = find.ref.value.trim().toUpperCase().replace(/\s+/g, ''), phone = fPhone.value;
    if (!/^(SHE-)?\d{6}-[0-9A-F]{6}$/.test(ref) || phone.length !== 10) { fNote.textContent = 'Please enter your reference (like SHE-261117-AB12CD) and the 10-digit phone number you booked with.'; return; }
    const btn = find.querySelector('button'); btn.disabled = true; fNote.textContent = 'Checking…';
    fetch('/api/track', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ref, phone }) })
      .then(r => r.json().then(j => ({ code: r.status, j }))).catch(() => ({ code: 0, j: {} }))
      .then(({ code, j }) => {
        btn.disabled = false;
        if (code === 200 && j.ok) {
          write(read().filter(b => b.ref !== j.ref).concat([{ ref: j.ref, url: j.status_url, date: j.date, when: j.when, concern: j.concern, st: j.status, seen: j.status }]));
          find.reset(); fNote.textContent = 'Found it. Its status is shown above.'; render(); listEl.scrollTop = 0; return;
        }
        fNote.textContent = code === 404 ? 'We could not find a booking with that reference and phone number. Please check both, or call 99406 62500.'
          : code === 429 ? 'Too many tries. Please wait a few minutes, or call 99406 62500.' : 'Could not check right now. Please try again, or call 99406 62500.';
      });
  });

  render(); refresh();
  setInterval(() => { if (!document.hidden) refresh(); }, POLL);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) refresh(); });
  addEventListener('pageshow', e => { if (e.persisted) refresh(); });
  addEventListener('storage', e => { if (e.key === KEY) render(); });
})();

// Footer: current year, WhatsApp link, live "Open now / Closed" from clinic hours (India time)
(() => {
  document.querySelectorAll('[data-year]').forEach(el => { el.textContent = new Date().getFullYear(); });
  document.querySelectorAll('[data-wa]').forEach(a => { a.href = waLink('Hi SHEroots, I would like to know more.'); });
  const el = document.querySelector('[data-open-status]');
  if (!el) return;
  const SLOTS = [[9 * 60, 13 * 60], [17 * 60, 21 * 60]];          // open every day
  const fmt = m => { const h = Math.floor(m / 60), mm = m % 60; return ((h + 11) % 12 + 1) + (mm ? ':' + String(mm).padStart(2, '0') : '') + (h < 12 ? ' AM' : ' PM'); };
  const update = () => {
    const ist = new Date(Date.now() + (new Date().getTimezoneOffset() + 330) * 60000);
    const now = ist.getHours() * 60 + ist.getMinutes();
    const cur = SLOTS.find(([o, c]) => now >= o && now < c);
    const next = SLOTS.find(([o]) => now < o) || SLOTS[0];
    el.className = 'sf-status' + (cur ? ' is-open' : '');
    el.textContent = cur ? 'Open now, until ' + fmt(cur[1]) : 'Closed now, opens ' + (now < next[0] ? '' : 'tomorrow ') + 'at ' + fmt(next[0]);
    el.hidden = false;
  };
  update(); setInterval(update, 60000);
})();

/* gallery lightbox (photos + videos) */
(function(){
  const lb = document.querySelector('.gal-lb'); if (!lb) return;
  const btns = [...document.querySelectorAll('[data-gal]')];
  const img = lb.querySelector('img'), vid = lb.querySelector('video'), cap = lb.querySelector('figcaption');
  let i = 0, opener = null;
  const stop = () => { vid.pause(); vid.removeAttribute('src'); vid.load(); };
  const show = n => {
    i = (n + btns.length) % btns.length;
    const b = btns[i]; stop();
    if (b.dataset.video) {
      img.hidden = true; vid.hidden = false;
      vid.poster = b.querySelector('img').src; vid.src = b.dataset.video; vid.play().catch(() => {});
    } else {
      vid.hidden = true; img.hidden = false;
      img.src = b.querySelector('img').src; img.alt = b.querySelector('img').alt;
    }
    cap.textContent = b.querySelector('.gal-cap').textContent;
  };
  btns.forEach((b, n) => b.addEventListener('click', () => { opener = b; show(n); lb.showModal(); }));
  lb.querySelector('.gal-p').addEventListener('click', () => show(i - 1));
  lb.querySelector('.gal-n').addEventListener('click', () => show(i + 1));
  lb.querySelector('.gal-x').addEventListener('click', () => lb.close());
  lb.addEventListener('click', e => { if (e.target === lb) lb.close(); });
  lb.addEventListener('close', () => { stop(); if (opener) opener.focus(); });
  lb.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft') show(i - 1);
    if (e.key === 'ArrowRight') show(i + 1);
  });
})();
