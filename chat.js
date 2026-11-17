/* SHEroots chat assistant: instant answers, plus a short guided booking (concern, date, time, name, phone). No server, no tracking:
   a booking only leaves this page when the visitor presses Send in their own email app. Nothing is stored.
   Edit the ANSWERS below to change what it says. Anything unknown points patients to a call/booking. */
(function () {
  const BASE = document.documentElement.getAttribute('data-root') || '';
  const waHref = text => 'https://wa.me/' + (window.SHE_WA || '919025603429') + '?text=' + encodeURIComponent(text);
  const HOURS = '9 AM – 1 PM and 5 PM – 9 PM';
  const callHref = () => (typeof CLINIC_PHONE !== 'undefined' && CLINIC_PHONE)
    ? 'tel:' + CLINIC_PHONE.replace(/[^+\d]/g, '') : '#contact';
  const callLabel = () => (typeof CLINIC_PHONE !== 'undefined' && CLINIC_PHONE) ? 'Call ' + CLINIC_PHONE : 'Call us';

  const ACTIONS = {
    call: () => ({ label: callLabel(), href: callHref(), primary: true }),
    book: () => ({ label: 'Book a session', href: '#contact' }),
    treatments: () => ({ label: 'See all treatments', href: '#explore' }),
    mail: () => ({ label: 'Open the email again', href: lastMailto || '#contact' })
  };
  let lastMailto = '';

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
      kw: ['treat', 'service', 'condition', 'offer', 'back pain', 'neck', 'knee', 'shoulder', 'elbow', 'sciatica', 'sports', 'injury', 'posture', 'ankle', 'wrist', 'carpal', 'weight', 'cardiac', 'heart', 'joint', 'help'],
      text: "We treat 12 core conditions (neck, shoulder, back & sciatica, knee, ankle, wrist, tennis elbow, joint pain, sports injuries, posture, cardiac rehab, weight loss) and 7 women's health concerns (pelvic floor, pregnancy & postnatal care, PCOS/PCOD, diastasis recti, incontinence, dry needling). Not sure yours is listed? Just ask us.",
      actions: ['treatments', 'call'], next: ['women', 'new']
    },
    women: {
      chip: "Women's health",
      kw: ['women', 'woman', 'pelvic', 'pregnancy', 'pregnant', 'postnatal', 'prenatal', 'pcos', 'pcod', 'diastasis', 'recti', 'incontinence', 'bladder', 'leak', 'leaking', 'antenatal', 'baby', 'delivery', 'birth', 'periods', 'menopause'],
      text: "We understand these topics can feel personal, and you never have to be embarrassed here. We support pelvic floor rehab, pregnancy and postnatal care, PCOS/PCOD, diastasis recti correction and urinary incontinence. Feel free to ask us anything before you book.",
      actions: ['call', 'book'], next: ['visit', 'hours']
    },
    hours: {
      chip: 'Opening hours',
      kw: ['hour', 'hours', 'open', 'timing', 'timings', 'time', 'what time', 'close', 'closed', 'sunday', 'holiday', 'working', 'available'],
      text: 'We\'re open ' + HOURS + '.\nநேரம்: காலை 9 – 1, மாலை 5 – 9.',
      actions: ['book', 'call'], next: ['new', 'treat']
    },
    visit: {
      chip: 'What to expect at my first visit',
      kw: ['expect', 'bring', 'wear', 'prepare', 'first visit', 'first session', 'what happens', 'involve', 'dress', 'carry', 'reports'],
      text: "Wear comfortable clothes you can move in, and bring any scan reports, referral letters or a list of medicines if you have them. Arrive a few minutes early. Your therapist will explain every step before starting, and you can ask questions at any time.",
      actions: ['book'], next: ['pain', 'hours']
    },
    pain: {
      chip: 'Will it hurt?',
      kw: ['hurt', 'hurts', 'painful', 'uncomfortable', 'safe', 'afraid', 'fear', 'does it pain', 'is it pain', 'side effect'],
      text: "Your therapist will tell you what they're doing and why, and adjust to your comfort. Please speak up whenever something doesn't feel right, and we'll change the approach. Your comfort matters to us.",
      actions: ['call'], next: ['visit', 'new']
    },
    cost: {
      chip: 'Fees & payment',
      kw: ['cost', 'price', 'fee', 'fees', 'how much', 'charge', 'charges', 'pay', 'payment', 'rate', 'insurance', 'claim', 'referral', 'prescription', 'gp'],
      text: "We want to give you the right answer, so please ask our team directly about session fees, payment options and whether you need a doctor's referral. A quick call is the fastest way.",
      actions: ['call', 'book'], next: ['hours', 'new']
    },
    where: {
      chip: null,
      kw: ['where', 'address', 'location', 'located', 'situated', 'place', 'map', 'direction', 'madurai', 'chokkikulam', 'branch'],
      text: "We're at Chinna Chokkikulam, Madurai (625002). You'll find the map in the Visit us section of this page, or call us and we'll guide you.",
      actions: ['call', 'book'], next: ['hours']
    },
    book: {
      chip: 'Book a session',
      kw: ['book', 'call', 'phone', 'number', 'contact', 'reserve', 'schedule', 'speak', 'talk'],
      text: "Easy! Call us, or send a booking request and we'll get back to you. We're open " + HOURS + '.',
      actions: ['call', 'book'], next: ['new', 'cost']
    },
    hello: {
      chip: null,
      kw: ['hi', 'hii', 'hiii', 'hello', 'hey', 'hlo', 'hai', 'vanakkam', 'welcome', 'good morning', 'good afternoon', 'good evening', 'namaste', 'how are you', 'anybody', 'anyone there'],
      text: "Hello and welcome to SHEroots! 🌸 I'm doing well, thank you for asking. I can tell you about our treatments, timings and what to expect, or book a session for you in about a minute. What would you like to know?",
      actions: ['book'], next: ['new', 'treat', 'hours', 'book']
    },
    who: {
      chip: null,
      kw: ['your name', 'who are you', 'are you a bot', 'are you human', 'are you real', 'what are you', 'who is this'],
      text: "I'm the SHEroots assistant, a helper on this website. I can answer common questions and book a session request. For anything medical or personal, our physiotherapists are always happy to talk with you directly.",
      actions: ['call', 'book'], next: ['treat', 'hours', 'book']
    },
    doctor: {
      chip: 'Meet the physiotherapist',
      kw: ['doctor', 'dr', 'chitra', 'karthick', 'physiotherapist', 'therapist', 'physio', 'qualification', 'qualified', 'experience', 'trainer', 'who treats', 'who will', 'female', 'lady', 'woman'],
      text: "Your physiotherapist is Dr. Chitra Karthick (BPT, MIAP, MD Acu). She is a women's health and pelvic floor specialist, a prenatal and postnatal trainer and a yoga trainer. Care is personal, respectful and built around you.",
      actions: ['book', 'call'], next: ['women', 'visit', 'hours']
    },
    men: {
      chip: null,
      kw: ['men', 'man', 'male', 'gents', 'husband', 'father', 'dad', 'boy', 'child', 'kid', 'son', 'daughter', 'everyone', 'senior', 'elderly', 'old age', 'age limit'],
      text: "Yes. Women's health is our special focus, and we also look after everyday pain and injuries for everyone, such as neck, back, knee and shoulder problems. Tell us what's bothering you and we'll guide you.",
      actions: ['book', 'call'], next: ['treat', 'visit', 'hours']
    },
    sessions: {
      chip: null,
      kw: ['how many sessions', 'how many visits', 'how many days', 'how long will', 'how long does treatment', 'how long to recover', 'recover', 'duration', 'how soon', 'results', 'cure', 'permanent'],
      text: "It depends on your condition, your goals and how your body responds. After your first assessment we'll talk through a likely plan with you. Results vary from person to person, and we only promise what we can deliver.",
      actions: ['book', 'call'], next: ['visit', 'pain', 'cost']
    },
    needling: {
      chip: null,
      kw: ['dry needling', 'needling', 'needle', 'acupuncture', 'trigger point', 'knots'],
      text: "Dry needling is a focused technique for tight, painful muscle knots. We always explain it first and use it only when it suits you. Dr. Chitra also holds an MD in Acupuncture.",
      actions: ['book', 'call'], next: ['pain', 'visit']
    },
    home: {
      chip: null,
      kw: ['home visit', 'home service', 'come to my house', 'at home', 'online', 'video call', 'tele', 'virtual', 'whatsapp'],
      text: "I don't have details on home visits or online sessions, and I don't want to guess. Please call us and the team will tell you what's possible.",
      actions: ['call', 'book'], next: ['hours', 'treat']
    },
    parking: {
      chip: null,
      kw: ['parking', 'park', 'bus', 'landmark', 'nearby', 'how to reach', 'how to come', 'route'],
      text: "We're in Chinna Chokkikulam, Madurai. I don't have parking or landmark details, so please call us and we'll gladly guide you to the clinic.",
      actions: ['call'], next: ['hours', 'book']
    },
    urgent: {
      chip: null,
      kw: ['emergency', 'urgent', 'chest pain', 'cannot breathe', "can't breathe", 'faint', 'stroke', 'numb', 'paralys', 'suicid', 'bleeding'],
      text: "⚠️ If this is an emergency or you have severe symptoms (such as chest pain, trouble breathing, sudden weakness or numbness, or heavy bleeding), please call 108 for an ambulance straight away or go to the nearest hospital emergency department. We can't assess emergencies by chat.",
      actions: [], next: []
    },
    thanks: {
      chip: null,
      kw: ['thank', 'thanks', 'thank you', 'great', 'bye', 'good bye', 'nice', 'super'],
      text: "You're very welcome! 💗 We look forward to helping you feel stronger.",
      actions: ['book'], next: []
    }
  };
  const FALLBACK = {
    text: "Thanks for asking! I'm not sure I can answer that one properly, and I don't want to guess. Our team will happily help directly, or try one of the options below.",
    actions: ['call', 'book'], next: ['treat', 'hours', 'cost']
  };
  const START = ['new', 'treat', 'hours', 'visit', 'cost', 'book'];
  Object.keys(ANSWERS).forEach(k => { ANSWERS[k].key = k; });   // lets a reply hide the chip that was just asked

  // ---------- UI ----------
  const el = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt) e.textContent = txt; return e; };
  const root = el('div', 'chat');
  root.innerHTML =
    '<button class="chat-launch" type="button" aria-label="Chat with SHEroots" aria-expanded="false" aria-controls="chatPanel">' +
      '<img src="' + BASE + 'images/chat-bot.webp" width="256" height="256" alt="">' +
      '</button>' +
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
        const a = typeof k === 'string' ? ACTIONS[k]() : k; const link = el('a', 'act' + (a.primary ? ' primary' : ''), a.label); link.href = a.href;
        if (a.newTab) { link.target = '_blank'; link.rel = 'noopener'; }
        if (a.track) link.setAttribute('data-track-open', '');     // opens the "Track my request" panel (script.js)
        row.appendChild(link);
      });
      m.appendChild(row);
    }
    log.appendChild(m); scroll();
  }
  function setChips(keys, skip) {
    chips.replaceChildren(); chips.classList.remove('wrap'); chips.scrollLeft = 0;
    // suggested follow-ups first, then the rest of the main menu, so every option is always one tap away
    const all = [...new Set(keys.concat(START))].filter(k => k !== skip);
    all.filter(k => ANSWERS[k] && ANSWERS[k].chip).forEach(k => {
      const b = el('button', null, ANSWERS[k].chip); b.type = 'button';
      b.addEventListener('click', () => ask(ANSWERS[k].chip, k));
      chips.appendChild(b);
    });
  }
  function reply(entry) {
    const typing = el('div', 'msg bot typing', '…'); log.appendChild(typing); scroll();
    setTimeout(() => { typing.remove(); say('bot', entry.text, entry.actions); setChips(entry.next || [], entry.key); }, 450);
  }
  const escRe = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  function match(q) {
    const s = ' ' + q.toLowerCase().replace(/[^a-z0-9\u0B80-\u0BFF' ]+/g, ' ').replace(/\s+/g, ' ').trim() + ' ';
    if (ANSWERS.urgent.kw.some(w => s.includes(w))) return ANSWERS.urgent;
    let best = null, score = 0;
    Object.keys(ANSWERS).forEach(k => {
      let n = 0;
      ANSWERS[k].kw.forEach(w => {
        const re = new RegExp('(^|[^a-z])' + escRe(w) + '(s|es|ing|ed)?([^a-z]|$)');   // whole words, simple endings
        if (re.test(s)) n += w.length > 5 ? 3 : w.length > 3 ? 2 : 1;
      });
      if (n > score) { score = n; best = ANSWERS[k]; }
    });
    return best || FALLBACK;
  }
  function ask(text, key) {
    say('me', text);
    if (flow) return flowInput(text);
    if (key === 'book' || (!key && wantsBooking(text))) return chooseBooking();
    reply(key ? ANSWERS[key] : match(text));
  }


  // ---------- Guided booking: concern -> date -> time -> name -> phone -> note -> confirm ----------
  const EMAIL = (typeof CLINIC_EMAIL !== 'undefined' && CLINIC_EMAIL) ? CLINIC_EMAIL : 'sherootsphysio@gmail.com';
  const WD = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'], MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const WDF = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
  const MONF = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];
  const CONCERNS = ['Pain relief', "Women's health", 'Pregnancy / postnatal', 'Sports injury', 'Not sure yet'];
  const SLOTS = [[9, 0], [10, 0], [11, 0], [12, 0], [17, 0], [18, 0], [19, 0], [20, 0]];
  const pad = n => String(n).padStart(2, '0');
  const today0 = () => { const n = new Date(); return new Date(n.getFullYear(), n.getMonth(), n.getDate()); };
  const addDays = (d, k) => new Date(d.getFullYear(), d.getMonth(), d.getDate() + k);
  const sameDay = (a, b) => a.toDateString() === b.toDateString();
  const dLabel = d => WD[d.getDay()] + ' ' + d.getDate() + ' ' + MON[d.getMonth()];
  const tLabel = (h, m) => (h % 12 || 12) + ':' + pad(m) + ' ' + (h >= 12 ? 'PM' : 'AM');
  const chipDay = d => sameDay(d, today0()) ? 'Today' : sameDay(d, addDays(today0(), 1)) ? 'Tomorrow' : dLabel(d);
  const minsOf = (h, m) => h * 60 + m;
  const okWindow = t => (t >= 540 && t <= 750) || (t >= 1020 && t <= 1230);   // 9:00-12:30 and 5:00-8:30 PM
  const isPast = (d, t) => { const n = new Date(); return sameDay(d, today0()) && t <= minsOf(n.getHours(), n.getMinutes()) + 30; };
  const isoDate = d => d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
  let flow = null;

  function parseDate(s) {
    s = s.toLowerCase().trim(); const t0 = today0();
    if (/\btoday\b/.test(s)) return t0;
    if (/\b(tomorrow|tmrw|tmr)\b/.test(s)) return addDays(t0, 1);
    for (let i = 0; i < 7; i++) if (s.includes(WDF[i]) || new RegExp('\\b' + WD[i].toLowerCase() + '\\b').test(s)) {
      const k = (i - t0.getDay() + 7) % 7; return addDays(t0, k);
    }
    let m = s.match(/(\d{1,2})[\/\-.](\d{1,2})(?:[\/\-.](\d{2,4}))?/);
    if (m) { const d = new Date(t0.getFullYear(), +m[2] - 1, +m[1]); if (d < t0) d.setFullYear(d.getFullYear() + 1); return isNaN(d) ? null : d; }
    m = s.match(/(\d{1,2})(?:st|nd|rd|th)?\s*(?:of\s*)?([a-z]{3})/) || s.match(/([a-z]{3})[a-z]*\s*(\d{1,2})/);
    if (m) {
      const day = +(/^\d/.test(m[1]) ? m[1] : m[2]), mon = MONF.indexOf(/^\d/.test(m[1]) ? m[2] : m[1]);
      if (mon > -1) { const d = new Date(t0.getFullYear(), mon, day); if (d < t0) d.setFullYear(d.getFullYear() + 1); return d; }
    }
    return null;
  }
  function parseTime(s) {
    s = s.toLowerCase().replace(/\./g, '');
    if (/\bmorning\b/.test(s)) return [10, 0];
    if (/\bevening\b/.test(s)) return [18, 0];
    const m = s.match(/(\d{1,2})(?::(\d{2}))?\s*(am|pm)?/); if (!m) return null;
    let h = +m[1]; const mi = +(m[2] || 0), ap = m[3];
    if (ap === 'pm' && h < 12) h += 12; if (ap === 'am' && h === 12) h = 0;
    if (!ap && h >= 1 && h <= 8) h += 12;
    return h < 24 && mi < 60 ? [h, mi] : null;
  }

  function flowChips(items) {
    chips.replaceChildren(); chips.classList.add('wrap');
    items.concat([{ label: 'Cancel booking', fn: cancelFlow, ghost: true }]).forEach(it => {
      const b = el('button', it.ghost ? 'ghost' : null, it.label); b.type = 'button';
      b.addEventListener('click', () => { say('me', it.label); it.fn(); });
      chips.appendChild(b);
    });
  }
  function botSays(text, then, actions) {
    const typing = el('div', 'msg bot typing', '…'); log.appendChild(typing); scroll();
    setTimeout(() => { typing.remove(); say('bot', text, actions); if (then) then(); }, 350);
  }
  function cancelFlow() {
    flow = null; chips.classList.remove('wrap'); input.placeholder = 'Type your question…';
    botSays('No problem, I\'ve cancelled that. Nothing was sent. Ask me anything else, or start again any time. 🌸', () => setChips(START));
  }
  function chooseBooking() {
    botSays('Happy to help you book! 🌸 How would you like to do it?', () => {
      chips.replaceChildren(); chips.classList.add('wrap');
      [['Book with the assistant', () => { say('me', 'Book with the assistant'); startBooking(); }],
       ['Fill the booking form myself', () => { say('me', 'Fill the booking form myself'); goForm(); }]].forEach(([t, fn]) => {
        const b = el('button', 'choice', t); b.type = 'button'; b.addEventListener('click', fn); chips.appendChild(b);
      });
    });
  }
  function goForm() {
    botSays('Great, I\'ve taken you to the booking form on this page. Just fill in your details and press "Send request". 🌸', () => setChips(START));
    const t = document.getElementById('contact');
    setTimeout(() => { close(); if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 700);
  }
  function startBooking() {
    flow = { step: 'concern', d: {} };
    botSays("Lovely, let's book you in. It takes about a minute. 🌸\nWhat would you like help with?", askConcern);
  }
  function askConcern() {
    flow.step = 'concern'; input.placeholder = 'Or type what is bothering you…';
    flowChips(CONCERNS.map(c => ({ label: c, fn: () => setConcern(c) })));
  }
  function setConcern(c) { flow.d.concern = c; botSays('Got it: ' + c + '.\nWhich day suits you?', askDate); }
  function askDate() {
    flow.step = 'date'; input.placeholder = 'Or type a date, e.g. 20 Nov or Monday';
    const now = new Date(), opts = [];
    for (let i = 0; i < 7 && opts.length < 5; i++) { if (i === 0 && now.getHours() >= 19) continue; opts.push(addDays(today0(), i)); }
    flowChips(opts.map(d => ({ label: chipDay(d), fn: () => setDate(d) })));
  }
  function setDate(d) { flow.d.date = d; botSays(dLabel(d) + ', noted.\nWhat time would you like? We\'re open 9 AM – 1 PM and 5 PM – 9 PM.', askTime); }
  // Free slots for a day come from the booking server (so two people can't take the same time); local list if offline
  function loadSlots(d) {
    const local = () => SLOTS.filter(([h, m]) => !isPast(d, minsOf(h, m))).map(([h, m]) => [h, m]);
    return fetch('/api/slots?date=' + isoDate(d)).then(r => r.ok ? r.json() : Promise.reject())
      .then(j => j.slots.filter(x => x.free).map(x => x.time.split(':').map(Number))).catch(local);
  }
  function askTime() {
    flow.step = 'time'; input.placeholder = 'Or type a time, e.g. 6 PM';
    const d = flow.d.date;
    loadSlots(d).then(free => {
      if (!flow || flow.d.date !== d) return;
      flow.free = free;
      if (!free.length) { botSays('Sorry, ' + dLabel(d) + ' is fully booked. 🌸 Please pick another day.', askDate); return; }
      flowChips(free.map(([h, m]) => ({ label: tLabel(h, m), fn: () => setTime(h, m) })));
    });
  }
  function setTime(h, m) { flow.d.hm = pad(h) + ':' + pad(m); flow.d.time = tLabel(h, m); botSays('Perfect, ' + flow.d.time + '.\nWhat is your name?', askName); }
  function askName() { flow.step = 'name'; input.placeholder = 'Your full name'; flowChips([]); input.focus(); }
  function setName(n) { flow.d.name = n; botSays('Nice to meet you, ' + n.split(' ')[0] + '! What is the best phone number to reach you on?', askPhone); }
  function askPhone() { flow.step = 'phone'; input.placeholder = 'Your phone number'; flowChips([]); input.focus(); }
  function setPhone(p) { flow.d.phone = p; botSays('What is your email? We will send your confirmation there as soon as the clinic accepts.', askEmail); }
  function askEmail() { flow.step = 'email'; input.placeholder = 'you@example.com'; flowChips([]); input.focus(); }
  function setEmail(e) { flow.d.email = e; botSays('Anything you would like us to know? For example where it hurts, or if you are pregnant. You can skip this.', askNote); }
  function askNote() { flow.step = 'note'; input.placeholder = 'A short note (optional)'; flowChips([{ label: 'Skip', fn: () => setNote('') }]); }
  function setNote(n) { flow.d.note = n; botSays(summary(), askConfirm); }
  function summary() {
    const d = flow.d;
    return 'Please check your details:\n• For: ' + d.concern + '\n• Day: ' + dLabel(d.date) + '\n• Time: ' + d.time + '\n• Name: ' + d.name + '\n• Phone: ' + d.phone + (d.email ? '\n• Email: ' + d.email : '') + (d.note ? '\n• Note: ' + d.note : '') +
      '\n\nShall I send this booking request to the clinic?';
  }
  function askConfirm() {
    flow.step = 'confirm'; input.placeholder = 'Type yes to send';
    flowChips([{ label: 'Yes, send it', fn: sendBooking }, { label: 'Change something', fn: () => { flow.d = {}; botSays("No problem, let's start again.\nWhat would you like help with?", askConcern); } }]);
  }
  function sendBooking() {
    const d = flow.d, first = d.name.split(' ')[0];
    const lines = ['Appointment request (via the website chat)', '', 'Name: ' + d.name, 'Phone: ' + d.phone, 'For: ' + d.concern, 'Day: ' + dLabel(d.date), 'Time: ' + d.time].concat(d.email ? ['Email: ' + d.email] : [], d.note ? ['Note: ' + d.note] : []).join('\n');
    const subj = 'Appointment request: ' + d.concern + ', ' + dLabel(d.date) + ' ' + d.time;
    lastMailto = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent(subj) + '&body=' + encodeURIComponent(lines);
    const gmail = 'https://mail.google.com/mail/?view=cm&fs=1&to=' + encodeURIComponent(EMAIL) + '&su=' + encodeURIComponent(subj) + '&body=' + encodeURIComponent(lines);
    const card = (title, ref, statusText, sent) => {
      const rows = [['For', d.concern], ['Day', dLabel(d.date)], ['Time', d.time], ['Name', d.name], ['Phone', d.phone]].concat(d.email ? [['Email', d.email]] : [], d.note ? [['Note', d.note]] : []);
      const c = el('div', 'msg bot book-card' + (sent ? ' sent' : ''));
      c.innerHTML = '<div class="bc-top"><strong></strong><em></em></div><div class="bc-rows">' + rows.map(() => '<div><span></span><b></b></div>').join('') + '</div><p class="bc-status"></p>';
      c.querySelector('.bc-top strong').textContent = title; c.querySelector('em').textContent = ref || 'Not sent';
      if (!ref) c.querySelector('em').remove();
      c.querySelectorAll('.bc-rows > div').forEach((r, i) => { r.firstChild.textContent = rows[i][0]; r.lastChild.textContent = rows[i][1]; });
      c.querySelector('.bc-status').textContent = statusText;
      return c;
    };
    const finish = () => { flow = null; chips.classList.remove('wrap'); input.placeholder = 'Type your question…'; setChips(START); scroll(); setTimeout(scroll, 60); };
    flow.step = 'sending'; chips.replaceChildren();
    const sending = el('div', 'msg bot typing', 'Sending your request to the clinic…'); log.appendChild(sending); scroll();
    const ctrl = 'AbortController' in window ? new AbortController() : null, timer = setTimeout(() => ctrl && ctrl.abort(), 15000);
    fetch('/api/book', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, signal: ctrl ? ctrl.signal : undefined,
      body: JSON.stringify({ name: d.name, phone: d.phone, email: d.email || '', concern: d.concern, date: isoDate(d.date), time: d.hm, note: d.note || '', source: 'chat' })
    }).then(r => r.json().then(j => ({ code: r.status, j }))).catch(() => ({ code: 0, j: {} }))
      .then(({ code, j }) => {
        clearTimeout(timer); sending.remove();
        if (code === 200 && j.ok) {
          if (window.sheRememberBooking) window.sheRememberBooking(j);
          log.appendChild(card('Booking request sent ✓', j.ref, 'Waiting for the clinic to confirm. We\'ll call you on ' + d.phone + '.', true));
          say('bot', 'Done, ' + first + '! ✅ Your booking request has reached the clinic.\n\nWhat happens next:\n1. The clinic reviews your request (usually within a few hours during clinic time).\n2. You get the confirmation by email to ' + d.email + ', on WhatsApp or a call on ' + d.phone + ', and on this website under "Track my request".\n3. Come 10 minutes early, in comfortable clothes, with any scan reports. 🌸\n\nKeep your reference ' + j.ref + '. Tap "Track my request" (also on the left edge of the page) to see when the clinic confirms.',
            [{ label: 'Also send on WhatsApp (faster reply)', href: waHref('Hi SHEroots, I just sent a booking request on your website (Ref: ' + j.ref + ').\n' + lines.split('\n').slice(2).join('\n')), newTab: true, primary: true }]
              .concat(j.status_url ? [{ label: 'Track my request', href: j.status_url, track: true }] : []));
          return finish();
        }
        if (code === 409 && j.alternatives) {      // someone else just took this slot
          const alts = j.alternatives;
          flow.step = 'time';
          botSays('Sorry, ' + first + ', ' + d.time + ' on ' + dLabel(d.date) + ' was just booked by someone else. 🙏\n' +
            (alts.length ? 'Here are the nearest free times. Tap one and I\'ll send your request straight away:' : 'Please pick another day.'), () => {
            if (!alts.length) return askDate();
            flowChips(alts.map(a => ({ label: a.label, fn: () => {
              const [y, mo, da] = a.date.split('-').map(Number), [h, mi] = a.time.split(':').map(Number);
              flow.d.date = new Date(y, mo - 1, da); flow.d.hm = a.time; flow.d.time = tLabel(h, mi); sendBooking();
            } })));
          });
          return;
        }
        const acts = el('div', 'msg-actions');
        [['Send on WhatsApp', waHref('Hi SHEroots, I would like to book an appointment.\n' + lines.split('\n').slice(2).join('\n')), true, true], ['Send with Gmail', gmail, false, true], ['Use my mail app (Outlook etc.)', lastMailto, false, false], ['Call ' + (typeof CLINIC_PHONE !== 'undefined' ? CLINIC_PHONE : ''), callHref(), false, false]].forEach(([t, h, pr, nw]) => { const l = el('a', 'act' + (pr ? ' primary' : ''), t); l.href = h; if (nw) { l.target = '_blank'; l.rel = 'noopener'; } acts.appendChild(l); });
        const c = card('Booking request not sent', '', 'We could not send this automatically. Please send it on WhatsApp, by email, or call us, and we\'ll confirm your time.', false);
        c.appendChild(acts);
        say('bot', 'Sorry, ' + first + ', something went wrong sending your request. 🙏 Your details are below, so you can send them in one tap or call us.');
        log.appendChild(c); finish();
      });
  }
  function flowInput(text) {
    const s = text.trim();
    if (/^(cancel|stop|quit|exit|never ?mind)\b/i.test(s)) return cancelFlow();
    const step = flow.step;
    if (step === 'concern') return setConcern(s.length > 60 ? s.slice(0, 60) : s);
    if (step === 'date') {
      const d = parseDate(s);
      if (!d) return botSays('Sorry, I could not read that date. Please tap a day below, or type it like "20 Nov" or "Monday".', askDate);
      if (d < today0() || d > addDays(today0(), 90)) return botSays('Please choose a day from today up to about three months ahead.', askDate);
      return setDate(d);
    }
    if (step === 'time') {
      const t = parseTime(s);
      if (!t) return botSays('Sorry, I could not read that time. Please tap a time below, or type it like "6:30 PM".', askTime);
      const mins = minsOf(t[0], t[1]);
      if (!okWindow(mins)) return botSays('We see patients from 9 AM to 1 PM and 5 PM to 9 PM. Please pick a time in those hours.', askTime);
      if (isPast(flow.d.date, mins)) return botSays('That time has already passed or is too soon today. Please pick a later time.', askTime);
      const free = flow.free || [], slot = free.find(([h]) => h === t[0]);
      if (!slot) return botSays('Sorry, ' + tLabel(t[0], 0) + ' is not available that day. Please tap one of the free times below.', askTime);
      if (t[1]) say('bot', 'We book in hourly slots, so I\'ve picked ' + tLabel(slot[0], slot[1]) + '.');
      return setTime(slot[0], slot[1]);
    }
    if (step === 'name') return /[a-z\u0B80-\u0BFF]{2,}/i.test(s) ? setName(s.slice(0, 60)) : botSays('Could I have your name, please?', askName);
    if (step === 'phone') {
      const digits = s.replace(/\D/g, '');
      return digits.length >= 10 ? setPhone(s.replace(/[^\d+\s-]/g, '').slice(0, 20)) : botSays('That number looks too short. Please type a 10-digit mobile number.', askPhone);
    }
    if (step === 'email') {
      if (/^(skip|no|none|nope)$/i.test(s)) return botSays('We need an email to send your confirmation. Please type your email address.', askEmail);
      return /^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(s) ? setEmail(s.slice(0, 120)) : botSays('That email does not look right. Please check it (for example name@gmail.com).', askEmail);
    }
    if (step === 'note') return setNote(/^(skip|no|none|nothing|nope)$/i.test(s) ? '' : s.slice(0, 200));
    if (step === 'confirm') {
      if (/^(y|yes|yeah|ok|okay|send|confirm|sure|correct)\b/i.test(s)) return sendBooking();
      if (/^(n|no|change|edit|wrong)\b/i.test(s)) { flow.d = {}; return botSays("No problem, let's start again.\nWhat would you like help with?", askConcern); }
      return botSays('Please say "yes" to send, or "change" to start again.', askConfirm);
    }
  }
  const wantsBooking = q => /\b(book|appointment|schedule|reserve|slot)\b/i.test(q);

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
  // It shows once, stays for a few seconds, then tucks itself away; it never sits over the booking form.
  if (!sessionStorage.getItem('chatTip')) setTimeout(() => {
    const form = document.getElementById('contact');
    const r = form && form.getBoundingClientRect();
    if (panel.hidden && !(r && r.top < innerHeight && r.bottom > 0)) {
      tip.hidden = false; sessionStorage.setItem('chatTip', '1');
      setTimeout(() => { tip.hidden = true; }, 8000);
    }
  }, 8000);
})();
