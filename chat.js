/* SHEroots chat assistant: instant answers, no server, no tracking, nothing is stored or sent.
   Edit the ANSWERS below to change what it says. Anything unknown points patients to a call/booking. */
(function () {
  const BASE = document.documentElement.getAttribute('data-root') || '';
  const HOURS = '9 AM – 1 PM and 5 PM – 9 PM';
  const callHref = () => (typeof CLINIC_PHONE !== 'undefined' && CLINIC_PHONE)
    ? 'tel:' + CLINIC_PHONE.replace(/[^+\d]/g, '') : BASE + 'contact.html';
  const callLabel = () => (typeof CLINIC_PHONE !== 'undefined' && CLINIC_PHONE) ? 'Call ' + CLINIC_PHONE : 'Call us';

  const ACTIONS = {
    call: () => ({ label: callLabel(), href: callHref(), primary: true }),
    book: () => ({ label: 'Book a session', href: BASE + 'contact.html' }),
    treatments: () => ({ label: 'See all treatments', href: BASE + 'treatments.html' })
  };

  // key -> { chip label (null = not a chip), keywords, answer, actions }
  const ANSWERS = {
    new: {
      chip: "I'm a new patient",
      kw: ['new', 'first', 'start', 'begin', 'never', 'nervous', 'scared', 'worried', 'anxious'],
      text: "Welcome, and well done for reaching out! 🌸 It's completely normal to feel unsure before a first visit. We begin with a relaxed conversation about what's bothering you, carefully assess, then explain what we find and agree a plan together. You're always in control: ask questions or pause any time.",
      actions: ['call', 'book'], next: ['treat', 'visit', 'hours']
    },
    treat: {
      chip: 'What do you treat?',
      kw: ['treat', 'service', 'condition', 'offer', 'pain', 'back', 'neck', 'knee', 'shoulder', 'elbow', 'sciatica', 'sports', 'injury', 'posture', 'ankle', 'wrist', 'carpal', 'weight', 'cardiac', 'heart', 'joint', 'help'],
      text: "We treat 12 core conditions (neck, shoulder, back & sciatica, knee, ankle, wrist, tennis elbow, joint pain, sports injuries, posture, cardiac rehab, weight loss) and 7 women's health concerns (pelvic floor, pregnancy & postnatal care, PCOS/PCOD, diastasis recti, incontinence, dry needling). Not sure yours is listed? Just ask us.",
      actions: ['treatments', 'call'], next: ['women', 'new']
    },
    women: {
      chip: "Women's health",
      kw: ['women', 'pelvic', 'pregnan', 'postnatal', 'pcos', 'pcod', 'diastasis', 'incontinence', 'bladder', 'leak', 'antenatal', 'baby', 'birth', 'period'],
      text: "We understand these topics can feel personal, and you never have to be embarrassed here. We support pelvic floor rehab, pregnancy and postnatal care, PCOS/PCOD, diastasis recti correction and urinary incontinence. Feel free to ask us anything before you book.",
      actions: ['call', 'book'], next: ['visit', 'hours']
    },
    hours: {
      chip: 'Opening hours',
      kw: ['hour', 'open', 'time', 'when', 'close', 'today', 'morning', 'evening', 'timing'],
      text: 'We\'re open ' + HOURS + '.\nநேரம்: காலை 9 – 1, மாலை 5 – 9.',
      actions: ['book', 'call'], next: ['new', 'treat']
    },
    visit: {
      chip: 'What to expect at my first visit',
      kw: ['expect', 'bring', 'wear', 'prepare', 'session', 'appointment', 'visit', 'long', 'involve'],
      text: "Wear comfortable clothes you can move in, and bring any scan reports, referral letters or a list of medicines if you have them. Arrive a few minutes early. Your therapist will explain every step before starting, and you can ask questions at any time.",
      actions: ['book'], next: ['pain', 'hours']
    },
    pain: {
      chip: 'Will it hurt?',
      kw: ['hurt', 'painful', 'uncomfortable', 'safe', 'afraid', 'fear'],
      text: "Your therapist will tell you what they're doing and why, and adjust to your comfort. Please speak up whenever something doesn't feel right, and we'll change the approach. Your comfort matters to us.",
      actions: ['call'], next: ['visit', 'new']
    },
    cost: {
      chip: 'Fees & health funds',
      kw: ['cost', 'price', 'fee', 'much', 'charge', 'pay', 'insurance', 'fund', 'medicare', 'private health', 'rebate', 'claim', 'hicaps', 'referral', 'gp'],
      text: "We want to give you the right answer, so please ask our team directly about fees, health fund rebates and whether you need a referral. A quick call is the fastest way.",
      actions: ['call', 'book'], next: ['hours', 'new']
    },
    where: {
      chip: null,
      kw: ['where', 'address', 'location', 'find', 'map', 'parking', 'direction', 'near'],
      text: "For our address and directions, please call us or check the Contact page, and we'll gladly guide you.",
      actions: ['call', 'book'], next: ['hours']
    },
    book: {
      chip: 'Book / call us',
      kw: ['book', 'call', 'phone', 'number', 'contact', 'reserve', 'schedule', 'speak', 'talk'],
      text: "Easy! Call us, or send a booking request and we'll get back to you. We're open " + HOURS + '.',
      actions: ['call', 'book'], next: ['new', 'cost']
    },
    urgent: {
      chip: null,
      kw: ['emergency', 'urgent', 'chest pain', 'cannot breathe', "can't breathe", 'faint', 'stroke', 'numb', 'paralys', 'suicid', 'bleeding'],
      text: "⚠️ If this is an emergency or you have severe symptoms (such as chest pain, trouble breathing, sudden weakness or numbness, or heavy bleeding), please call your local emergency number straight away (000 in Australia) or go to the nearest emergency department. We can't assess emergencies by chat.",
      actions: [], next: []
    },
    thanks: {
      chip: null,
      kw: ['thank', 'thanks', 'ok', 'great', 'bye'],
      text: "You're very welcome! 💗 We look forward to helping you feel stronger.",
      actions: ['book'], next: []
    }
  };
  const FALLBACK = {
    text: "I'm not sure I have the right answer for that, and I don't want to guess. Our team will be happy to help directly.",
    actions: ['call', 'book'], next: ['treat', 'hours', 'cost']
  };
  const START = ['new', 'treat', 'hours', 'visit', 'cost', 'book'];

  // ---------- UI ----------
  const el = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt) e.textContent = txt; return e; };
  const root = el('div', 'chat');
  root.innerHTML =
    '<button class="chat-launch" type="button" aria-label="Chat with SHEroots" aria-expanded="false" aria-controls="chatPanel">' +
      '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4h16a2 2 0 012 2v10a2 2 0 01-2 2H9l-5 4v-4H4a2 2 0 01-2-2V6a2 2 0 012-2z"/></svg>' +
      '<span class="chat-ping" aria-hidden="true"></span></button>' +
    '<div class="chat-tip" role="status" hidden><span>New here? Ask us anything 🌸</span><button type="button" aria-label="Dismiss">×</button></div>' +
    '<section class="chat-panel" id="chatPanel" role="dialog" aria-label="Chat with SHEroots" hidden>' +
      '<header><img src="' + BASE + 'images/logo-right.webp" alt="" width="40" height="40"><div><strong>SHEroots Assistant</strong><small>Instant answers · We\'re here to help</small></div>' +
      '<button type="button" class="chat-close" aria-label="Close chat">×</button></header>' +
      '<div class="chat-log" aria-live="polite"></div>' +
      '<div class="chat-chips"></div>' +
      '<form class="chat-form" autocomplete="off"><input type="text" name="q" placeholder="Type your question…" aria-label="Your question" maxlength="200"><button type="submit" aria-label="Send"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 21l21-9L2 3v7l15 2-15 2z"/></svg></button></form>' +
      '<p class="chat-note">General information only, not medical advice. In an emergency call your local emergency number.</p>' +
    '</section>';
  document.body.appendChild(root);

  const launch = root.querySelector('.chat-launch');
  const panel = root.querySelector('.chat-panel');
  const log = root.querySelector('.chat-log');
  const chips = root.querySelector('.chat-chips');
  const form = root.querySelector('.chat-form');
  const input = form.q;
  const tip = root.querySelector('.chat-tip');
  let started = false;

  function scroll() { log.scrollTop = log.scrollHeight; }
  function say(who, text, actions) {
    const m = el('div', 'msg ' + who);
    text.split('\n').forEach((ln, i) => { if (i) m.appendChild(document.createElement('br')); m.appendChild(document.createTextNode(ln)); });
    if (actions && actions.length) {
      const row = el('div', 'msg-actions');
      actions.forEach(k => {
        const a = ACTIONS[k](); const link = el('a', 'act' + (a.primary ? ' primary' : ''), a.label); link.href = a.href;
        row.appendChild(link);
      });
      m.appendChild(row);
    }
    log.appendChild(m); scroll();
  }
  function setChips(keys) {
    chips.replaceChildren();
    keys.filter(k => ANSWERS[k] && ANSWERS[k].chip).forEach(k => {
      const b = el('button', null, ANSWERS[k].chip); b.type = 'button';
      b.addEventListener('click', () => ask(ANSWERS[k].chip, k));
      chips.appendChild(b);
    });
  }
  function reply(entry) {
    const typing = el('div', 'msg bot typing', '…'); log.appendChild(typing); scroll();
    setTimeout(() => { typing.remove(); say('bot', entry.text, entry.actions); setChips(entry.next && entry.next.length ? entry.next : START); }, 450);
  }
  function match(q) {
    const s = q.toLowerCase();
    if (ANSWERS.urgent.kw.some(w => s.includes(w))) return ANSWERS.urgent;
    let best = null, score = 0;
    Object.keys(ANSWERS).forEach(k => {
      const n = ANSWERS[k].kw.filter(w => s.includes(w)).length;
      if (n > score) { score = n; best = ANSWERS[k]; }
    });
    return best || FALLBACK;
  }
  function ask(text, key) { say('me', text); reply(key ? ANSWERS[key] : match(text)); }

  function open() {
    panel.hidden = false; root.classList.add('open');
    launch.setAttribute('aria-expanded', 'true'); tip.hidden = true;
    sessionStorage.setItem('chatTip', '1');
    if (!started) {
      started = true;
      say('bot', "Hi, I'm the SHEroots assistant 👋 Whether it's your first physio visit or you just have a quick question, I can help right away.", []);
      setChips(START);
    }
    setTimeout(() => input.focus(), 50);
  }
  function close() { panel.hidden = true; root.classList.remove('open'); launch.setAttribute('aria-expanded', 'false'); launch.focus(); }

  launch.addEventListener('click', () => (panel.hidden ? open() : close()));
  root.querySelector('.chat-close').addEventListener('click', close);
  tip.querySelector('button').addEventListener('click', () => { tip.hidden = true; sessionStorage.setItem('chatTip', '1'); });
  tip.querySelector('span').addEventListener('click', open);
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !panel.hidden) close(); });
  form.addEventListener('submit', e => {
    e.preventDefault();
    const q = input.value.trim(); if (!q) return;
    input.value = ''; ask(q);
  });

  // Friendly nudge after a few seconds (once per visit)
  if (!sessionStorage.getItem('chatTip')) setTimeout(() => { if (panel.hidden) tip.hidden = false; }, 6000);
})();
