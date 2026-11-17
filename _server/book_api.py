#!/usr/bin/env python3
"""SHEroots booking service.

Stores booking requests (SQLite), prevents double booking (slot capacity checked inside a locked
transaction), emails the doctor with Accept / Decline / Call / Confirmed-by-phone actions, and keeps
the patient updated (status page + optional email).

Runs on 127.0.0.1:8095 behind nginx (location /api/). Standard library only.

Routes
  GET  /api/health
  GET  /api/slots?date=YYYY-MM-DD          free / full slots for a day
  POST /api/book                           create a booking (409 + alternatives if the slot is taken)
  GET  /api/b/<ref>?t=<token>              patient status page      POST: patient cancels
  GET  /api/d/<ref>?t=<token>[&do=...]     doctor page for one booking   POST: accept/decline/called/cancel
  GET  /api/s/<ref>?t=<token>              patient status as JSON (used by the website's "Track my request")
  POST /api/track  {ref, phone}             find a booking from another device (reference + phone must match)
  GET  /api/admin?k=<ADMIN_KEY>            doctor dashboard (all bookings)

Settings (environment, see /etc/sheroots-book.env)
  BOOK_TO        doctor / clinic email(s), comma-separated
  SMTP_USER      Gmail address that sends the emails     SMTP_PASS  its 16-character App Password
  SMTP_HOST/PORT default smtp.gmail.com / 465 (SSL)
  BOOK_SECRET    random secret used to sign links        ADMIN_KEY  secret for the dashboard link
  PUBLIC_URL     https://sheroots.gentize.in
  SLOT_TIMES     09:00,10:00,11:00,12:00,17:00,18:00,19:00,20:00
  SLOT_CAPACITY  patients per slot (default 1)           MAX_DAYS_AHEAD (default 90)
  CLINIC_PHONE   +919940662500
  DATA_DIR       /var/lib/sheroots-book (database + outbox for emails when SMTP is not set)

WhatsApp alerts to the clinic (new request, reminder, patient cancelled). Optional; pick one provider:
  WA_PROVIDER    callmebot | meta          WA_ALERT_TO  clinic WhatsApp number(s), e.g. 919025603429 (comma-separated)
  callmebot:     WA_CALLMEBOT_KEY  the apikey CallMeBot sends after you allow it (one key per number:
                 use "919025603429:KEY,919940662500:KEY2" for several numbers)
  meta:          WA_TOKEN, WA_PHONE_ID (WhatsApp Cloud API). Free text only arrives inside a 24-hour window
                 after the clinic number last messaged the business number; set WA_TEMPLATE (+ WA_TEMPLATE_LANG,
                 default en) to an approved template with one body variable to send any time.

Automatic WhatsApp to the PATIENT (request received / confirmed / declined / cancelled). Needs Meta's
WhatsApp Cloud API (WA_TOKEN + WA_PHONE_ID) and approved "utility" templates. Each template has three body
variables: {{1}} first name, {{2}} date & time, {{3}} treatment. Set the template names you got approved:
  WA_TPL_RECEIVED, WA_TPL_CONFIRMED, WA_TPL_DECLINED, WA_TPL_CANCELLED   (+ WA_TEMPLATE_LANG, default en)
Any one left empty is simply not sent (the patient still gets the email and sees it on the website).
"""
import hashlib, hmac, html, json, os, re, smtplib, sqlite3, ssl, sys, threading, time
from datetime import datetime, date as Date, timedelta, timezone
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs, quote

E = os.environ.get
PORT = int(E('BOOK_PORT', '8095'))
TO = [a.strip() for a in E('BOOK_TO', '').split(',') if a.strip()]
SMTP_USER, SMTP_PASS = E('SMTP_USER', '').strip(), E('SMTP_PASS', '').replace(' ', '').strip()
SMTP_HOST, SMTP_PORT = E('SMTP_HOST', 'smtp.gmail.com'), int(E('SMTP_PORT', '465'))
SECRET = E('BOOK_SECRET', '').encode()
ADMIN_KEY = E('ADMIN_KEY', '')
PUBLIC = E('PUBLIC_URL', 'https://sheroots.gentize.in').rstrip('/')
SLOTS = [t.strip() for t in E('SLOT_TIMES', '09:00,10:00,11:00,12:00,17:00,18:00,19:00,20:00').split(',') if t.strip()]
CAPACITY = max(1, int(E('SLOT_CAPACITY', '1')))
MAX_DAYS = int(E('MAX_DAYS_AHEAD', '90'))
CLINIC_PHONE = E('CLINIC_PHONE', '+919940662500')
DATA = E('DATA_DIR', '/var/lib/sheroots-book')
DB = os.path.join(DATA, 'bookings.db')
OUTBOX = os.path.join(DATA, 'outbox')
ALLOWED_ORIGINS = {PUBLIC}
IST = timezone(timedelta(hours=5, minutes=30))
ACTIVE = ('pending', 'confirmed')            # statuses that hold a slot
ADDRESS = 'No.3, Kamarajar 3rd Cross Street, Chinna Chokkikulam, Madurai 625002'
MAPS = 'https://www.google.com/maps?cid=15464404039475393364'
if not SECRET or not ADMIN_KEY:
    sys.exit('BOOK_SECRET and ADMIN_KEY must be set')

_book_lock = threading.Lock()
_hits, _hits_lock = {}, threading.Lock()


# ---------------------------------------------------------------- helpers
def now(): return datetime.now(IST)
def today(): return now().date()
def esc(v): return html.escape(str(v or ''), quote=True)
def tok(ref, role): return hmac.new(SECRET, f'{ref}:{role}'.encode(), hashlib.sha256).hexdigest()[:32]
def tok_ok(ref, role, t): return bool(t) and hmac.compare_digest(tok(ref, role), t)
def patient_url(ref): return f'{PUBLIC}/api/b/{ref}?t={tok(ref, "pt")}'
def doctor_url(ref, do=''): return f'{PUBLIC}/api/d/{ref}?t={tok(ref, "dr")}' + (f'&do={do}' if do else '')
def admin_url(): return f'{PUBLIC}/api/admin?k={ADMIN_KEY}'
def tlabel(hm): h, m = map(int, hm.split(':')); return f'{h % 12 or 12}:{m:02d} {"PM" if h >= 12 else "AM"}'
def dlabel(iso): return Date.fromisoformat(iso).strftime('%a %d %b %Y')
def when(b): return f'{dlabel(b["date"])}, {tlabel(b["time"])}'
def phone_fmt(p): return f'+91 {p[:5]} {p[5:]}'
def tel(p): return f'tel:+91{p}'
def wa(p, text=''): return f'https://wa.me/91{p}' + (f'?text={quote(text)}' if text else '')
REMIND_AFTER = timedelta(hours=float(E('REMIND_AFTER_HOURS', '2')))   # nudge the clinic if a request is still unanswered


def wa_text(b, kind):
    """Ready-to-send WhatsApp message from the clinic to the patient (the doctor only taps Send)."""
    first = b['name'].split(' ')[0]
    if kind == 'confirmed':
        return (f"Hi {first}, this is SHEroots Physiotherapy Clinic. Your appointment is confirmed for {when(b)} "
                f"({b['concern']}).\n\nAddress: {ADDRESS}\nDirections: {MAPS}\n\nPlease come 10 minutes early with "
                f"comfortable clothes and any scan reports. Your booking: {patient_url(b['ref'])}")
    if kind == 'cancelled' and (b['reason'] or '').lower() == 'cancelled by patient':
        return (f"Hi {first}, this is SHEroots Physiotherapy Clinic. We have cancelled your booking for {when(b)} as you asked. "
                f"Whenever you are ready, reply here or book again: {PUBLIC}/#contact")
    if kind in ('declined', 'cancelled'):
        why = f" ({b['reason']})" if b['reason'] else ''
        return (f"Hi {first}, this is SHEroots Physiotherapy Clinic. Sorry, we are not able to see you at {when(b)}{why}. "
                f"Please reply with a day and time that suits you, or book again here: {PUBLIC}/#contact")
    return (f"Hi {first}, this is SHEroots Physiotherapy Clinic. We have your request for {when(b)} ({b['concern']}). "
            f"Is this time still good for you?")


def db():
    c = sqlite3.connect(DB, timeout=15, isolation_level=None)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA journal_mode=WAL'); c.execute('PRAGMA busy_timeout=15000')
    return c


def init_db():
    os.makedirs(OUTBOX, exist_ok=True)
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS bookings(
          id INTEGER PRIMARY KEY, ref TEXT UNIQUE NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
          name TEXT NOT NULL, phone TEXT NOT NULL, email TEXT, concern TEXT NOT NULL, note TEXT,
          date TEXT NOT NULL, time TEXT NOT NULL, source TEXT, status TEXT NOT NULL DEFAULT 'pending',
          confirm_method TEXT, reason TEXT, history TEXT NOT NULL DEFAULT '[]');
        CREATE INDEX IF NOT EXISTS ix_slot ON bookings(date, time, status);
        CREATE INDEX IF NOT EXISTS ix_status ON bookings(status, date);''')
        cols = {r['name'] for r in c.execute('PRAGMA table_info(bookings)')}
        if 'reminded_at' not in cols: c.execute('ALTER TABLE bookings ADD COLUMN reminded_at TEXT')


def remind_once():
    cutoff = (now() - REMIND_AFTER).isoformat(); sent = 0
    with db() as c:
        rows = c.execute("SELECT * FROM bookings WHERE status='pending' AND reminded_at IS NULL AND created_at < ?", (cutoff,)).fetchall()
        for b in rows:
            c.execute('UPDATE bookings SET reminded_at=? WHERE ref=?', (now().isoformat(), b['ref']))
            if slot_dt(b['date'], b['time']) > now(): email_doctor_new(b, reminder=True); wa_alert_new(b, reminder=True); sent += 1
    return sent


def remind_loop():
    """Every 5 minutes: email the clinic once about requests still waiting REMIND_AFTER after they arrived."""
    while True:
        try: remind_once()
        except Exception as e:
            print('reminder loop error:', type(e).__name__, e, file=sys.stderr, flush=True)
        time.sleep(300)


def slot_dt(iso, hm):
    h, m = map(int, hm.split(':'))
    return datetime.combine(Date.fromisoformat(iso), datetime.min.time(), IST).replace(hour=h, minute=m)


def slot_bookable(iso, hm):
    """Slot exists, is in the future (30 min notice) and within the booking window."""
    if hm not in SLOTS: return False
    d = Date.fromisoformat(iso)
    if d < today() or d > today() + timedelta(days=MAX_DAYS): return False
    return slot_dt(iso, hm) > now() + timedelta(minutes=30)


def taken_counts(c, iso):
    rows = c.execute(f'SELECT time, COUNT(*) n FROM bookings WHERE date=? AND status IN ({",".join("?" * len(ACTIVE))}) GROUP BY time',
                     (iso, *ACTIVE)).fetchall()
    return {r['time']: r['n'] for r in rows}


def day_slots(c, iso):
    taken = taken_counts(c, iso)
    return [{'time': t, 'label': tlabel(t), 'free': slot_bookable(iso, t) and taken.get(t, 0) < CAPACITY,
             'past': not slot_bookable(iso, t)} for t in SLOTS]


def alternatives(c, iso, hm, n=4):
    """Nearest free slots: same day first, then the following days."""
    out, d0 = [], Date.fromisoformat(iso)
    for k in range(0, 8):
        d = (d0 + timedelta(days=k)).isoformat()
        for s in day_slots(c, d):
            if s['free']: out.append({'date': d, 'time': s['time'], 'label': f'{Date.fromisoformat(d).strftime("%a %d %b")}, {s["label"]}'})
            if len(out) >= n: return out
    return out


def add_history(b, event, by, extra=''):
    h = json.loads(b['history'] or '[]')
    h.append({'at': now().strftime('%d %b %Y %I:%M %p'), 'event': event, 'by': by, 'extra': extra})
    return json.dumps(h, ensure_ascii=False)


def rate_ok(key, limit=6, window=600):
    t = time.time()
    with _hits_lock:
        q = [x for x in _hits.get(key, []) if t - x < window]
        ok = len(q) < limit
        if ok: q.append(t)
        _hits[key] = q
    return ok


# ---------------------------------------------------------------- email
# Design: one calm white card under a small clinic header, clear hierarchy (one primary action,
# one secondary, everything else as quiet text links), no emoji. Table-based buttons so Gmail,
# Outlook and phone mail apps all render them the same way.
INK, MUTED, LINE, BRAND = '#1d1a1c', '#6b6168', '#ece5e9', '#b3125e'
FONT = "-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
TONE = {'brand': BRAND, 'ok': '#137a4b', 'warn': '#b26a00', 'bad': '#b42318', 'neutral': '#6b6168'}


def button(href, label, kind='primary', color=None):
    """Bulletproof button. kind: primary (solid) | secondary (outlined)."""
    c = color or BRAND
    if kind == 'primary':
        cell, link = f'background:{c};border:1px solid {c};', 'color:#ffffff;'
    else:
        cell, link = 'background:#ffffff;border:1px solid #d6ccd2;', f'color:{c};'
    return ('<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="display:inline-table;margin:0 8px 8px 0">'
            f'<tr><td style="{cell}border-radius:8px">'
            f'<a href="{esc(href)}" target="_blank" style="display:inline-block;padding:12px 22px;font-family:{FONT};font-size:15px;'
            f'font-weight:600;line-height:20px;{link}text-decoration:none;border-radius:8px">{esc(label)}</a></td></tr></table>')


def text_links(items):
    """Quiet secondary actions, e.g. 'Call +91 ... · WhatsApp'."""
    sep = '<span style="color:#cfc4ca;padding:0 8px">&middot;</span>'
    return sep.join(f'<a href="{esc(h)}" target="_blank" style="color:{BRAND};font-weight:600;text-decoration:none;white-space:nowrap">{esc(t)}</a>'
                    for t, h in items)


def status_pill(text, tone):
    c = TONE[tone]
    return (f'<span style="display:inline-block;padding:4px 10px;border-radius:999px;border:1px solid {c};color:{c};'
            f'font-size:12px;line-height:16px;font-weight:600;letter-spacing:.02em">{esc(text)}</span>')


def para(text, muted=False, size=15, mt=0):
    return (f'<p style="margin:{mt}px 0 0;font-size:{size}px;line-height:{size + 8}px;'
            f'color:{MUTED if muted else "#3a3337"}">{text}</p>')


def mail_shell(title, inner, tone='brand', preheader='', pill=None):
    """title: plain text. pill: (text, tone) shown above the title."""
    accent = TONE[tone]
    top = (status_pill(*pill) + '<div style="height:12px;line-height:12px">&nbsp;</div>') if pill else ''
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light">'
        f'<title>{esc(title)}</title></head>'
        '<body style="margin:0;padding:0;background:#f5f2f4;-webkit-text-size-adjust:100%">'
        f'<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:transparent">{esc(preheader)}</div>'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f5f2f4">'
        '<tr><td align="center" style="padding:28px 12px">'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:580px">'
        f'<tr><td style="padding:0 4px 14px;font-family:{FONT}">'
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>'
        f'<td style="padding-right:10px"><img src="{PUBLIC}/images/icon-192.png" width="32" height="32" alt="" '
        'style="display:block;border:0;border-radius:8px"></td>'
        f'<td style="font-size:15px;font-weight:700;color:{INK}">SHEroots '
        f'<span style="font-weight:400;color:{MUTED}">Physiotherapy Clinic</span></td></tr></table></td></tr>'
        f'<tr><td style="background:#ffffff;border:1px solid {LINE};border-top:3px solid {accent};border-radius:10px;'
        f'padding:28px 28px 24px;font-family:{FONT};color:{INK}">'
        f'{top}<h1 style="margin:0 0 6px;font-size:21px;line-height:28px;font-weight:700;color:{INK}">{esc(title)}</h1>'
        f'<div style="font-size:15px;line-height:23px;color:#3a3337">{inner}</div></td></tr>'
        f'<tr><td style="padding:16px 6px 0;font-family:{FONT};font-size:12px;line-height:18px;color:{MUTED}">'
        f'SHEroots Physiotherapy Clinic<br>{esc(ADDRESS)}<br>{esc(phone_fmt(CLINIC_PHONE[-10:]))}</td></tr>'
        '</table></td></tr></table></body></html>')


def detail_table(b, show_contact=True, show_when=True):
    rows = (([('Patient', b['name'])] if show_contact else [])
            + (([('Phone', phone_fmt(b['phone']))] + ([('Email', b['email'])] if b['email'] else [])) if show_contact else [])
            + [('Treatment', b['concern'])] + ([('Date & time', when(b))] if show_when else [])
            + ([('Note', b['note'])] if b['note'] else []) + [('Reference', b['ref'])])
    tr = ''.join(
        f'<tr><td style="padding:10px 12px 10px 0;width:32%;font-size:13px;line-height:20px;color:{MUTED};'
        f'border-top:1px solid {LINE};vertical-align:top">{esc(k)}</td>'
        f'<td style="padding:10px 0;font-size:15px;line-height:22px;font-weight:600;color:{INK};'
        f'border-top:1px solid {LINE};vertical-align:top">{esc(v)}</td></tr>' for k, v in rows)
    return ('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="margin:18px 0 22px;border-bottom:1px solid {LINE}">{tr}</table>')


def link(text, href, strong=True):
    return (f'<a href="{esc(href)}" target="_blank" style="color:{BRAND};{"font-weight:600;" if strong else ""}'
            f'text-decoration:none">{esc(text)}</a>')


def send_email(to, subject, html_body, text_body):
    if not to: return
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = formataddr(('SHEroots Physiotherapy Clinic', SMTP_USER or 'no-reply@sheroots.gentize.in'))
    msg['To'] = ', '.join(to if isinstance(to, list) else [to])
    msg['Message-ID'] = make_msgid(domain='sheroots.gentize.in')
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype='html')

    def go():
        try:
            if SMTP_USER and SMTP_PASS:
                with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ssl.create_default_context(), timeout=25) as s:
                    s.login(SMTP_USER, SMTP_PASS); s.send_message(msg)
            else:   # no SMTP yet: keep the email in the outbox so nothing is lost
                fn = os.path.join(OUTBOX, now().strftime('%Y%m%d-%H%M%S-') + re.sub(r'\W+', '-', subject)[:60] + '.eml')
                with open(fn, 'wb') as f: f.write(bytes(msg))
                print('SMTP not set, email saved to', fn, flush=True)
        except Exception as e:
            print('email failed:', type(e).__name__, e, '|', subject, file=sys.stderr, flush=True)
    threading.Thread(target=go, daemon=True).start()


# ---------------------------------------------------------------- WhatsApp alerts to the clinic
WA_PROVIDER = E('WA_PROVIDER', '').strip().lower()
WA_ALERT_TO = [re.sub(r'\D', '', x) for x in E('WA_ALERT_TO', '').split(',') if re.sub(r'\D', '', x)]
WA_CMB_KEYS = E('WA_CALLMEBOT_KEY', '').strip()
WA_TOKEN, WA_PHONE_ID = E('WA_TOKEN', '').strip(), E('WA_PHONE_ID', '').strip()
WA_TEMPLATE, WA_TEMPLATE_LANG = E('WA_TEMPLATE', '').strip(), E('WA_TEMPLATE_LANG', 'en').strip()


def wa_enabled():
    if not WA_ALERT_TO: return False
    if WA_PROVIDER == 'callmebot': return bool(WA_CMB_KEYS)
    if WA_PROVIDER == 'meta': return bool(WA_TOKEN and WA_PHONE_ID)
    return False


def _cmb_key(num):
    if ':' not in WA_CMB_KEYS: return WA_CMB_KEYS
    for part in WA_CMB_KEYS.split(','):
        n, _, k = part.partition(':')
        if re.sub(r'\D', '', n) == num: return k.strip()
    return ''


def send_whatsapp(text):
    """Fire-and-forget WhatsApp alert to the clinic number(s). Never blocks or breaks a booking."""
    if not wa_enabled(): return
    import urllib.request

    def go():
        for num in WA_ALERT_TO:
            try:
                if WA_PROVIDER == 'callmebot':
                    url = ('https://api.callmebot.com/whatsapp.php?phone=%2B' + num + '&text=' + quote(text)
                           + '&apikey=' + quote(_cmb_key(num)))
                    req = urllib.request.Request(url, headers={'User-Agent': 'sheroots-book'})
                else:
                    msg = ({'type': 'template', 'template': {'name': WA_TEMPLATE, 'language': {'code': WA_TEMPLATE_LANG},
                            'components': [{'type': 'body', 'parameters': [{'type': 'text', 'text': text.replace('\n', ' · ')[:1000]}]}]}}
                           if WA_TEMPLATE else {'type': 'text', 'text': {'body': text[:4000], 'preview_url': False}})
                    body = json.dumps({'messaging_product': 'whatsapp', 'to': num, **msg}).encode()
                    req = urllib.request.Request(f'https://graph.facebook.com/v21.0/{WA_PHONE_ID}/messages', data=body,
                                                 headers={'Authorization': 'Bearer ' + WA_TOKEN, 'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=25) as r:
                    out = r.read(400).decode('utf-8', 'replace')
                    if WA_PROVIDER == 'callmebot' and 'queued' not in out.lower() and 'sent' not in out.lower():
                        print('whatsapp alert not accepted:', re.sub(r'<[^>]+>', ' ', out)[:200], file=sys.stderr, flush=True)
            except Exception as e:
                detail = ''
                if hasattr(e, 'read'):
                    try: detail = e.read(300).decode('utf-8', 'replace')
                    except Exception: pass
                print('whatsapp alert failed:', type(e).__name__, e, detail, file=sys.stderr, flush=True)
    threading.Thread(target=go, daemon=True).start()


WA_TPL = {k: E('WA_TPL_' + k.upper(), '').strip() for k in ('received', 'confirmed', 'declined', 'cancelled')}


def meta_ready(): return bool(WA_TOKEN and WA_PHONE_ID)
def wa_patient_on(kind): return meta_ready() and bool(WA_TPL.get(kind))


def wa_patient(b, kind):
    """Automatic WhatsApp to the patient's own number through Meta's Cloud API (approved template)."""
    if not wa_patient_on(kind): return
    import urllib.request
    params = [b['name'].split(' ')[0][:60], when(b), b['concern'][:80]]
    body = json.dumps({'messaging_product': 'whatsapp', 'to': '91' + b['phone'], 'type': 'template',
                       'template': {'name': WA_TPL[kind], 'language': {'code': WA_TEMPLATE_LANG},
                                    'components': [{'type': 'body', 'parameters': [{'type': 'text', 'text': x} for x in params]}]}}).encode()

    def go():
        try:
            req = urllib.request.Request(f'https://graph.facebook.com/v21.0/{WA_PHONE_ID}/messages', data=body,
                                         headers={'Authorization': 'Bearer ' + WA_TOKEN, 'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=25) as r: r.read(300)
            print('whatsapp to patient sent:', kind, b['ref'], flush=True)
        except Exception as e:
            detail = ''
            if hasattr(e, 'read'):
                try: detail = e.read(300).decode('utf-8', 'replace')
                except Exception: pass
            print('whatsapp to patient failed:', kind, b['ref'], type(e).__name__, e, detail, file=sys.stderr, flush=True)
    threading.Thread(target=go, daemon=True).start()


def notify_patient(b, kind):
    """Tell the patient every way we can: email + WhatsApp (the website tracker reads the status itself)."""
    email_patient(b, kind)
    wa_patient(b, kind)


def told_patient(b, kind):
    ways = (['emailed'] if b['email'] else []) + (['sent a WhatsApp message'] if wa_patient_on(kind) else [])
    return (' The patient has been ' + ' and '.join(ways) + '.') if ways else ''


def wa_alert_new(b, reminder=False):
    head = '⏰ Still waiting for your reply' if reminder else '🌸 New appointment request'
    send_whatsapp(f"{head} (SHEroots website)\n\n"
                  f"Patient: {b['name']}\nPhone: +91 {b['phone']}\nFor: {b['concern']}\nWhen: {when(b)}\n"
                  + (f"Note: {b['note'][:300]}\n" if b['note'] else '')
                  + f"Ref: {b['ref']}\n\nAccept or decline: {doctor_url(b['ref'])}\n"
                  f"WhatsApp the patient: {wa(b['phone'])}")


def wa_alert_cancelled(b):
    send_whatsapp(f"❌ Booking cancelled by the patient (SHEroots website)\n\n"
                  f"Patient: {b['name']}\nPhone: +91 {b['phone']}\nWas: {when(b)} ({b['concern']})\nRef: {b['ref']}\n\n"
                  f"The slot is free again.")


def email_doctor_new(b, reminder=False):
    first = b['name'].split(' ')[0]
    lead = (para(f'The request from <b>{esc(b["name"])}</b> is still waiting. The patient has not been confirmed yet.')
            if reminder else para(f'<b>{esc(b["name"])}</b> has requested an appointment through the website.'))
    actions = (button(doctor_url(b['ref'], 'accept'), 'Accept booking', 'primary', TONE['ok'])
               + button(doctor_url(b['ref'], 'decline'), 'Decline', 'secondary', TONE['bad']))
    contact = (para(f'<span style="color:{MUTED}">Want to talk to {esc(first)} first?</span>&nbsp; '
                    + text_links([(f'Call {phone_fmt(b["phone"])}', tel(b['phone'])),
                                  ('WhatsApp', wa(b['phone'], wa_text(b, 'pending')))]), size=14, mt=8)
               + para('WhatsApp opens a chat with the patient, with a short message already typed that you can edit before sending.',
                      muted=True, size=13, mt=4))
    foot = (f'<div style="margin-top:22px;padding-top:16px;border-top:1px solid {LINE};font-size:13px;line-height:21px;color:{MUTED}">'
            f'Already agreed the time on a call? {link("Mark as confirmed by phone", doctor_url(b["ref"], "called"))}<br>'
            f'{link("Open booking", doctor_url(b["ref"]), False)}<span style="color:#cfc4ca;padding:0 6px">&middot;</span>'
            f'{link("All bookings", admin_url(), False)}</div>')
    inner = lead + detail_table(b) + actions + contact + foot
    text = (("Still waiting for your reply\n\n" if reminder else "New appointment request\n\n")
            + f"Patient: {b['name']}\nPhone: {phone_fmt(b['phone'])}\nTreatment: {b['concern']}\nDate & time: {when(b)}\n"
            + (f"Note: {b['note']}\n" if b['note'] else '') + f"Reference: {b['ref']}\n\n"
            + f"Accept: {doctor_url(b['ref'], 'accept')}\nDecline: {doctor_url(b['ref'], 'decline')}\n"
            + f"Call: +91{b['phone']}\nWhatsApp: {wa(b['phone'])}\n"
            + f"Confirmed on a call: {doctor_url(b['ref'], 'called')}\nAll bookings: {admin_url()}\n")
    title = 'Booking still waiting for you' if reminder else 'New appointment request'
    subject = (f"Reminder: {b['name']} is waiting, {when(b)}" if reminder
               else f"New booking: {b['name']}, {when(b)} ({b['concern']})")
    pill = ('Waiting over 2 hours', 'warn') if reminder else ('Needs your reply', 'brand')
    send_email(TO, subject, mail_shell(title, inner, 'warn' if reminder else 'brand',
                                       f"{b['name']} · {b['concern']} · {when(b)}", pill), text)


def email_patient(b, kind):
    if not b['email']: return
    first = esc(b['name'].split(' ')[0])
    track = para(link('View or cancel your booking', patient_url(b['ref'])), size=14, mt=10)
    call = para(text_links([(f'Call {phone_fmt(CLINIC_PHONE[-10:])}', f'tel:{CLINIC_PHONE}')]), size=14, mt=4)
    if kind == 'received':
        title, tone, pill = 'We have your request', 'brand', ('Waiting for confirmation', 'warn')
        body = (para(f'Hi {first}, thank you for choosing SHEroots.')
                + para(f'We will contact you on <b>{esc(phone_fmt(b["phone"]))}</b>, usually within a few hours during '
                       'clinic time, to confirm your appointment.', mt=10))
        acts, pre = track, f'Request received for {when(b)}. We will confirm shortly.'
    elif kind == 'confirmed':
        title, tone, pill = 'Your appointment is confirmed', 'ok', ('Confirmed', 'ok')
        body = (para(f'Hi {first}, we look forward to seeing you.')
                + '<div style="margin:16px 0 0;padding:14px 16px;border-radius:8px;background:#f1f8f4;border:1px solid #cfe8da">'
                  f'<div style="font-size:12px;line-height:16px;color:{TONE["ok"]};font-weight:600;letter-spacing:.04em;'
                  'text-transform:uppercase">Your appointment</div>'
                  f'<div style="font-size:18px;line-height:26px;font-weight:700;color:{INK};margin-top:2px">{esc(when(b))}</div></div>'
                + para('Please arrive 10 minutes early, wear comfortable clothes and bring any scan or medical reports.', mt=14))
        acts = button(MAPS, 'Get directions', 'primary') + call + track
        pre = f'Confirmed: {when(b)} at SHEroots Physiotherapy Clinic.'
    elif kind == 'declined':
        title, tone, pill = 'We could not confirm this time', 'bad', ('Not available', 'bad')
        body = (para(f'Hi {first}, sorry, we are not able to see you at <b>{esc(when(b))}</b>.')
                + (para(f'Message from the clinic: {esc(b["reason"])}', muted=True, mt=8) if b['reason'] else '')
                + para('Please choose another time, or call us and we will find a slot that suits you.', mt=10))
        acts = button(f'{PUBLIC}/#contact', 'Choose another time', 'primary') + call
        pre = f'We could not confirm {when(b)}. Please choose another time.'
    else:
        title, tone, pill = 'Your appointment has been cancelled', 'bad', ('Cancelled', 'bad')
        body = (para(f'Hi {first}, your appointment on <b>{esc(when(b))}</b> has been cancelled by the clinic.')
                + (para(f'Message from the clinic: {esc(b["reason"])}', muted=True, mt=8) if b['reason'] else ''))
        acts = button(f'{PUBLIC}/#contact', 'Book another time', 'primary') + call
        pre = f'Your appointment on {when(b)} was cancelled.'
    inner = body + detail_table(b, show_contact=False, show_when=(kind != 'confirmed')) + acts
    text = (re.sub(r'<[^>]+>', '', body.replace('</p>', '\n').replace('</div>', '\n'))
            + f'\nReference: {b["ref"]}\nYour booking: {patient_url(b["ref"])}\nCall: {CLINIC_PHONE}\n')
    send_email(b['email'], f'SHEroots: {title} ({when(b)})', mail_shell(title, inner, tone, pre, pill), html.unescape(text))


def email_doctor_patient_cancelled(b):
    inner = (para(f'<b>{esc(b["name"])}</b> cancelled their booking. The time slot is free again.') + detail_table(b)
             + para(text_links([('Open booking', doctor_url(b['ref'])), ('All bookings', admin_url())]), size=14))
    send_email(TO, f"Cancelled by patient: {b['name']}, {when(b)}",
               mail_shell('Booking cancelled by patient', inner, 'neutral', f"{b['name']} cancelled {when(b)}", ('Cancelled', 'neutral')),
               f"{b['name']} cancelled their booking for {when(b)} ({b['ref']}).\nAll bookings: {admin_url()}\n")


# ---------------------------------------------------------------- web pages
# Same design language as the emails: calm white cards, one primary action per screen.
CSS = '''*{box-sizing:border-box}
body{margin:0;background:#f5f2f4;font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#1d1a1c;-webkit-font-smoothing:antialiased}
.wrap{max-width:680px;margin:0 auto;padding:24px 16px 64px}.wide{max-width:1080px}
.brand{display:flex;align-items:center;gap:10px;margin:0 4px 18px;text-decoration:none;color:#1d1a1c;font-weight:700;font-size:15px}
.brand img{width:32px;height:32px;border-radius:8px}.brand span{font-weight:400;color:#6b6168}
.card{background:#fff;border:1px solid #ece5e9;border-radius:12px;padding:26px 26px 22px;margin-bottom:14px}
.card.accent{border-top:3px solid #b3125e}.card.accent.confirmed{border-top-color:#137a4b}.card.accent.declined,.card.accent.cancelled{border-top-color:#b42318}.card.accent.pending{border-top-color:#b26a00}
h1{font-size:22px;line-height:1.3;margin:10px 0 4px;font-weight:700}h2{font-size:15px;margin:0 0 12px;font-weight:700}
p{line-height:1.6;margin:0 0 10px}
.badge{display:inline-block;padding:4px 10px;border-radius:999px;font-weight:600;font-size:12px;border:1px solid currentColor;background:#fff}
.badge.pending{color:#b26a00}.badge.confirmed{color:#137a4b}.badge.declined,.badge.cancelled{color:#b42318}
.kv{width:100%;border-collapse:collapse;margin:16px 0 4px}.kv td{padding:10px 0;border-top:1px solid #ece5e9;vertical-align:top;font-size:15px}
.kv tr:last-child td{border-bottom:1px solid #ece5e9}.kv td:first-child{color:#6b6168;width:34%;font-size:13px;padding-right:12px}.kv td:last-child{font-weight:600}
.kv a,.link{color:#b3125e;text-decoration:none;font-weight:600}.kv a:hover,.link:hover{text-decoration:underline}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:11px 20px;border-radius:8px;border:1px solid transparent;font-family:inherit;font-size:15px;font-weight:600;line-height:1.2;text-decoration:none;cursor:pointer;transition:filter .15s,background .15s}
.btn:hover{filter:brightness(.94)}.btn:focus-visible{outline:3px solid #f2b8d3;outline-offset:2px}
.btn.primary{background:#b3125e;color:#fff}.btn.ok{background:#137a4b;color:#fff}.btn.danger{background:#b42318;color:#fff}
.btn.secondary{background:#fff;color:#1d1a1c;border-color:#d6ccd2}.btn.secondary.danger-text{color:#b42318}
.acts{display:flex;flex-wrap:wrap;gap:10px;margin-top:6px}.acts form{margin:0}
.sub{margin-top:18px;padding-top:16px;border-top:1px solid #ece5e9;font-size:14px;color:#6b6168;line-height:1.9}
.sep{color:#cfc4ca;padding:0 8px}
select{width:100%;max-width:420px;padding:10px 12px;border:1px solid #d6ccd2;border-radius:8px;font:inherit;margin:6px 0 14px;background:#fff}
label.muted{display:block;margin-top:4px}
.muted{color:#6b6168;font-size:14px}
.ok-msg,.err-msg{padding:12px 14px;border-radius:10px;font-weight:600;font-size:14px;margin-bottom:14px}
.ok-msg{background:#eef7f2;color:#0f5c39;border:1px solid #cfe8da}.err-msg{background:#fdf0ef;color:#8f1d14;border:1px solid #f4cbc6}
.hint{font-size:13px;color:#6b6168;margin:8px 0 0}
.hist{list-style:none;padding:0;margin:0;font-size:13px;color:#6b6168}.hist li{padding:7px 0;border-top:1px solid #f1ecef}.hist b{color:#1d1a1c;font-weight:600}
table.list{width:100%;border-collapse:collapse;font-size:14px}table.list th{text-align:left;color:#6b6168;font-weight:600;font-size:12px;letter-spacing:.03em;text-transform:uppercase;padding:8px 8px;border-bottom:1px solid #ece5e9}
table.list td{padding:12px 8px;border-bottom:1px solid #f1ecef;vertical-align:top}table.list a{color:#b3125e;font-weight:600;text-decoration:none}
.stats{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 2px}.stat{flex:1 1 140px;background:#faf8f9;border:1px solid #ece5e9;border-radius:10px;padding:12px 14px;font-size:13px;color:#6b6168}
.stat b{display:block;font-size:24px;color:#1d1a1c;margin-bottom:2px}
@media(max-width:640px){.card{padding:20px 18px}.acts .btn,.acts form,.acts form .btn{width:100%}
table.list thead{display:none}table.list tr{display:block;border-bottom:1px solid #ece5e9;padding:10px 0}table.list td{display:block;border:0;padding:2px 0}}'''


def page(title, body, wide=False):
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="robots" content="noindex,nofollow"><title>{esc(title)} | SHEroots</title><style>{CSS}</style></head><body>'
            f'<div class="wrap{" wide" if wide else ""}"><a class="brand" href="{PUBLIC}/"><img src="{PUBLIC}/images/icon-192.png" alt="">'
            f'SHEroots <span>Physiotherapy Clinic</span></a>{body}</div>'
            # drop the one-time result message (?m=) from the address bar so a refresh does not repeat it
            '<script>if(/[?&]m=/.test(location.search))history.replaceState(null,"",location.pathname+location.search.replace(/&m=[^&]*/,"")+location.hash)</script>'
            '</body></html>')


STATUS_TEXT = {'pending': 'Waiting for confirmation', 'confirmed': 'Confirmed', 'declined': 'Not available', 'cancelled': 'Cancelled'}


def kv(b, contact=True):
    rows = (([('Phone', f'<a href="{tel(b["phone"])}">{esc(phone_fmt(b["phone"]))}</a>')] if contact else [])
            + ([('Email', esc(b['email']))] if contact and b['email'] else [])
            + [('Treatment', esc(b['concern']))]
            + ([('Note', esc(b['note']))] if b['note'] else [])
            + [('Reference', esc(b['ref']))] + ([('Booked via', esc({'chat': 'Website chat', 'form': 'Website form'}.get(b['source'], 'Website')))] if contact else []))
    return '<table class="kv">' + ''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in rows) + '</table>'


def history_html(b):
    h = json.loads(b['history'] or '[]')
    return '<div class="card"><h2>History</h2><ul class="hist">' + ''.join(
        f'<li>{esc(x["at"])} &middot; <b>{esc(x["event"])}</b> by {esc(x["by"])}{" (" + esc(x["extra"]) + ")" if x.get("extra") else ""}</li>'
        for x in reversed(h)) + '</ul></div>'


def _msg(msg):
    if not msg: return ''
    return f'<div class="{"err-msg" if msg.startswith("!") else "ok-msg"}" role="status">{esc(msg.lstrip("!"))}</div>'


def doctor_page(b, msg='', do=''):
    st, first = b['status'], esc(b['name'].split(' ')[0])
    form = lambda action, label, cls, extra='': (
        f'<form method="post"><input type="hidden" name="t" value="{tok(b["ref"], "dr")}">'
        f'<input type="hidden" name="action" value="{action}">{extra}<button class="btn {cls}">{label}</button></form>')
    reason = ('<label class="muted" for="reason">Reason shown to the patient (optional)</label>'
              '<select name="reason" id="reason"><option value="">No reason</option><option>The clinic is fully booked at that time</option>'
              '<option>The doctor is not available at that time</option><option>Please call us to choose another time</option>'
              '<option>This treatment needs a longer appointment; we will call you</option></select>')
    back = f'<a class="btn secondary" href="{doctor_url(b["ref"])}">Back</a>'
    call = ('Call ' + esc(phone_fmt(b['phone'])), tel(b['phone']))
    wa_link = lambda label, kind: f'<a class="link" href="{esc(wa(b["phone"], wa_text(b, kind)))}" target="_blank" rel="noopener">{label}</a>'
    sep = '<span class="sep">&middot;</span>'
    acts = ''
    if st == 'pending':
        if do == 'decline':
            acts = f'<div class="card"><h2>Decline this request?</h2>{form("decline", "Decline request", "danger", reason)}<div class="acts">{back}</div></div>'
        elif do in ('accept', 'called'):
            # One tap from the email: the page confirms by itself as soon as it opens in a real browser.
            # Email link scanners (Gmail, Outlook Safe Links) fetch the page but do not run scripts, so they
            # cannot accept a booking. The button is a fallback if scripts are off.
            lab = 'Accept and confirm' if do == 'accept' else 'Yes, confirmed on a call'
            acts = (f'<div class="card"><h2>Confirming the booking…</h2><p class="muted">{esc(when(b))} &middot; {esc(b["concern"])}</p>'
                    f'<div class="acts" id="autoacc">{form(do, lab, "ok")}{back}</div></div>'
                    '<script>(function(){var f=document.querySelector("#autoacc form");if(!f)return;'
                    'var b=f.querySelector("button");b.disabled=true;b.textContent="Confirming…";f.submit();})()</script>')
        else:
            acts = (f'<div class="card"><h2>Your reply</h2><div class="acts">{form("accept", "Accept booking", "ok")}'
                    f'<a class="btn secondary danger-text" href="{doctor_url(b["ref"], "decline")}">Decline</a></div>'
                    f'<div class="sub">Talk to {first} first: <a class="link" href="{call[1]}">{call[0]}</a>{sep}{wa_link("WhatsApp", "pending")}<br>'
                    f'Already agreed the time on a call? <a class="link" href="{doctor_url(b["ref"], "called")}">Mark as confirmed by phone</a></div></div>')
    elif st == 'confirmed':
        cancel = (f'<h2 style="margin-top:6px">Cancel this appointment?</h2>{form("cancel", "Cancel appointment", "danger", reason)}'
                  if do == 'cancel' else f'Need to change it? <a class="link" href="{doctor_url(b["ref"], "cancel")}">Cancel appointment</a>')
        acts = (f'<div class="card"><h2>Next: let {first} know</h2>'
                f'<p class="muted">WhatsApp opens with the confirmation, address and directions already written. Check it and press Send.</p>'
                f'<div class="acts"><a class="btn ok" href="{esc(wa(b["phone"], wa_text(b, "confirmed")))}" target="_blank" rel="noopener">Send confirmation on WhatsApp</a>'
                f'<a class="btn secondary" href="{call[1]}">{call[0]}</a></div>'
                + ('' if b['email'] else f'<p class="hint">{first} did not give an email, so WhatsApp or a call is how they will hear from you.</p>')
                + f'<div class="sub">{cancel}</div></div>')
    else:
        by_patient = 'by patient' in (b['reason'] or '').lower()
        acts = (f'<div class="card"><h2>{"Contact " + first if by_patient else "Next: let " + first + " know"}</h2><div class="acts">'
                f'<a class="btn {"secondary" if by_patient else "ok"}" href="{esc(wa(b["phone"], wa_text(b, st)))}" target="_blank" rel="noopener">Message on WhatsApp</a>'
                f'<a class="btn secondary" href="{call[1]}">{call[0]}</a></div></div>')
    head = (f'<div class="card accent {st}"><span class="badge {st}">{STATUS_TEXT[st]}</span><h1>{esc(b["name"])}</h1>'
            f'<p class="muted" style="margin:0">{esc(when(b))}'
            + (f' &middot; {esc(b["confirm_method"])}' if st == 'confirmed' and b['confirm_method'] else '') + f'</p>{kv(b)}</div>')
    return page('Booking ' + b['ref'], _msg(msg) + head + acts + history_html(b) +
                f'<p style="margin:16px 4px 0"><a class="link" href="{admin_url()}">&larr; All bookings</a></p>')


def patient_page(b, msg=''):
    st = b['status']
    lead = {'pending': 'Thank you. We have your request and will contact you to confirm your appointment.',
            'confirmed': 'Your appointment is confirmed. We look forward to seeing you.',
            'declined': 'Sorry, we could not confirm this time. Please choose another time or call us.',
            'cancelled': 'This booking has been cancelled.'}[st]
    body = f'<div class="card accent {st}"><span class="badge {st}">{STATUS_TEXT[st]}</span><h1>{esc(when(b))}</h1><p class="muted">{lead}</p>'
    if b['reason'] and st in ('declined', 'cancelled'): body += f'<p class="muted">Message from the clinic: {esc(b["reason"])}</p>'
    body += kv(b, contact=False) + '<div class="acts" style="margin-top:18px">'
    call = f'<a class="btn secondary" href="tel:{esc(CLINIC_PHONE)}">Call {esc(phone_fmt(CLINIC_PHONE[-10:]))}</a>'
    if st == 'confirmed': body += f'<a class="btn primary" href="{MAPS}" target="_blank" rel="noopener">Get directions</a>' + call
    elif st in ('declined', 'cancelled'): body += f'<a class="btn primary" href="{PUBLIC}/#contact">Choose another time</a>' + call
    else: body += call
    body += '</div>'
    if st in ACTIVE:
        body += (f'<div class="sub"><form method="post" onsubmit="return confirm(\'Cancel this booking?\')" style="display:inline">'
                 f'<input type="hidden" name="t" value="{tok(b["ref"], "pt")}">Can\'t make it? '
                 f'<button class="link" style="border:0;background:none;padding:0;font:inherit;cursor:pointer">Cancel my booking</button></form></div>')
    body += f'<p class="muted" style="margin:16px 0 0;font-size:13px">{esc(ADDRESS)}</p></div>'
    if st == 'pending':   # keep checking while the patient waits; the page flips to Confirmed by itself
        body += ('<p class="muted" style="text-align:center;font-size:13px">This page updates by itself, so you can keep it open.</p>'
                 '<script>setTimeout(function(){if(!document.hidden)location.reload()},45000);'
                 'document.addEventListener("visibilitychange",function(){if(!document.hidden)location.reload()})</script>')
    return page('Your booking', _msg(msg) + body)


def admin_page():
    with db() as c:
        t = today().isoformat()
        up = c.execute("SELECT * FROM bookings WHERE date>=? AND status IN ('pending','confirmed') ORDER BY date, time", (t,)).fetchall()
        recent = c.execute("SELECT * FROM bookings WHERE status IN ('declined','cancelled') OR date<? ORDER BY updated_at DESC LIMIT 30", (t,)).fetchall()
        n_today = c.execute("SELECT COUNT(*) FROM bookings WHERE date=? AND status='confirmed'", (t,)).fetchone()[0]
    pend = [b for b in up if b['status'] == 'pending']

    def rows(items):
        if not items: return '<p class="muted">Nothing here.</p>'
        return ('<table class="list"><thead><tr><th>When</th><th>Patient</th><th>For</th><th>Status</th><th></th></tr></thead><tbody>' +
                ''.join(f'<tr><td>{esc(when(b))}</td><td>{esc(b["name"])}<br><a href="{tel(b["phone"])}">{esc(phone_fmt(b["phone"]))}</a></td>'
                        f'<td>{esc(b["concern"])}</td><td><span class="badge {b["status"]}">{STATUS_TEXT[b["status"]]}</span></td>'
                        f'<td><a href="{doctor_url(b["ref"])}">Open &rarr;</a></td></tr>' for b in items) + '</tbody></table>')
    body = (f'<div class="card"><h1>Bookings</h1><p class="muted">Updated {esc(now().strftime("%d %b %Y, %I:%M %p"))}. '
            f'{CAPACITY} patient{"s" if CAPACITY > 1 else ""} per slot. Keep this link private.</p>'
            f'<div class="stats"><div class="stat"><b>{len(pend)}</b>Waiting for you</div><div class="stat"><b>{n_today}</b>Confirmed today</div>'
            f'<div class="stat"><b>{len(up) - len(pend)}</b>Upcoming confirmed</div></div></div>'
            f'<div class="card"><h2 style="margin-top:0">Waiting for your answer</h2>{rows(pend)}</div>'
            f'<div class="card"><h2 style="margin-top:0">Upcoming confirmed</h2>{rows([b for b in up if b["status"] == "confirmed"])}</div>'
            f'<div class="card"><h2 style="margin-top:0">Recent past, declined and cancelled</h2>{rows(recent)}</div>')
    return page('Bookings', body, wide=True)


# ---------------------------------------------------------------- actions
def get_booking(c, ref):
    return c.execute('SELECT * FROM bookings WHERE ref=?', (ref,)).fetchone()


def apply_doctor(ref, action, reason):
    with db() as c:
        c.execute('BEGIN IMMEDIATE')
        b = get_booking(c, ref)
        st = b['status']
        if action in ('accept', 'called') and st == 'pending':
            method = 'accepted from email' if action == 'accept' else 'confirmed by phone call'
            c.execute("UPDATE bookings SET status='confirmed', confirm_method=?, updated_at=?, history=? WHERE ref=?",
                      (method, now().isoformat(), add_history(b, 'Confirmed', 'doctor', method), ref))
            kind, msg = 'confirmed', 'Booking confirmed.' + told_patient(b, 'confirmed') + ('' if wa_patient_on('confirmed') else ' Now send the patient the WhatsApp confirmation below.')
        elif action == 'decline' and st == 'pending':
            c.execute("UPDATE bookings SET status='declined', reason=?, updated_at=?, history=? WHERE ref=?",
                      (reason, now().isoformat(), add_history(b, 'Declined', 'doctor', reason), ref))
            kind, msg = 'declined', 'Booking declined. The slot is free again.' + (told_patient(b, 'declined') or ' Please call the patient.')
        elif action == 'cancel' and st == 'confirmed':
            c.execute("UPDATE bookings SET status='cancelled', reason=?, updated_at=?, history=? WHERE ref=?",
                      (reason, now().isoformat(), add_history(b, 'Cancelled', 'doctor', reason), ref))
            kind, msg = 'cancelled', 'Appointment cancelled. The slot is free again.' + (told_patient(b, 'cancelled') or ' Please call the patient.')
        else:
            c.execute('ROLLBACK')
            return b, f'!This booking is already {STATUS_TEXT[st].lower()}, so nothing changed.'
        c.execute('COMMIT')
        b = get_booking(c, ref)
    notify_patient(b, kind)
    return b, msg


def result_msg(role, code, b):
    """Message shown after an action. Rebuilt on the GET that follows the redirect (Post/Redirect/Get)."""
    if role == 'pt':
        return {'cancelled': 'Your booking has been cancelled. Thank you for letting us know.',
                'same': '!This booking cannot be cancelled now.'}.get(code, '')
    return {'confirmed': 'Booking confirmed.' + told_patient(b, 'confirmed') + ('' if wa_patient_on('confirmed') else ' Now send the patient the WhatsApp confirmation below.'),
            'declined': 'Booking declined. The slot is free again.' + (told_patient(b, 'declined') or ' Please let the patient know.'),
            'cancelled': 'Appointment cancelled. The slot is free again.' + (told_patient(b, 'cancelled') or ' Please let the patient know.'),
            'same': f'!This booking is already {STATUS_TEXT[b["status"]].lower()}, so nothing changed.'}.get(code, '')


def apply_patient_cancel(ref):
    with db() as c:
        c.execute('BEGIN IMMEDIATE')
        b = get_booking(c, ref)
        if b['status'] not in ACTIVE:
            c.execute('ROLLBACK'); return b, '!This booking cannot be cancelled now.'
        c.execute("UPDATE bookings SET status='cancelled', reason=?, updated_at=?, history=? WHERE ref=?",
                  ('Cancelled by patient', now().isoformat(), add_history(b, 'Cancelled', 'patient'), ref))
        c.execute('COMMIT')
        b = get_booking(c, ref)
    email_doctor_patient_cancelled(b)
    wa_alert_cancelled(b)
    return b, 'Your booking has been cancelled. Thank you for letting us know.'


def create_booking(d):
    """Returns (status_code, payload). Capacity is checked and the row inserted inside one locked transaction."""
    with _book_lock, db() as c:
        c.execute('BEGIN IMMEDIATE')
        taken = taken_counts(c, d['date']).get(d['time'], 0)
        if not slot_bookable(d['date'], d['time']) or taken >= CAPACITY:
            c.execute('ROLLBACK')
            return 409, {'ok': False, 'error': 'slot_taken', 'message': 'Sorry, that time is no longer available. Please choose another time.',
                         'alternatives': alternatives(c, d['date'], d['time'])}
        dup = c.execute(f"SELECT ref FROM bookings WHERE phone=? AND date=? AND time=? AND status IN ('pending','confirmed')",
                        (d['phone'], d['date'], d['time'])).fetchone()
        if dup:
            c.execute('ROLLBACK')
            b = get_booking(c, dup['ref'])
            return 200, {'ok': True, 'ref': b['ref'], 'status_url': patient_url(b['ref']), 'duplicate': True,
                         'when': when(b), 'date': b['date'], 'concern': b['concern'], 'status': b['status']}
        ref = 'SHE-' + now().strftime('%y%m%d') + '-' + os.urandom(3).hex().upper()
        ts = now().isoformat()
        hist = json.dumps([{'at': now().strftime('%d %b %Y %I:%M %p'), 'event': 'Requested', 'by': 'patient', 'extra': d['source']}])
        c.execute('INSERT INTO bookings(ref,created_at,updated_at,name,phone,email,concern,note,date,time,source,status,history) '
                  "VALUES(?,?,?,?,?,?,?,?,?,?,?,'pending',?)",
                  (ref, ts, ts, d['name'], d['phone'], d['email'], d['concern'], d['note'], d['date'], d['time'], d['source'], hist))
        c.execute('COMMIT')
        b = get_booking(c, ref)
    email_doctor_new(b)
    wa_alert_new(b)
    notify_patient(b, 'received')
    return 200, {'ok': True, 'ref': ref, 'status_url': patient_url(ref), 'when': when(b), 'date': b['date'],
                 'concern': b['concern'], 'status': b['status']}


def clean(d):
    lim = {'name': 80, 'phone': 20, 'email': 120, 'concern': 80, 'date': 10, 'time': 5, 'note': 600, 'source': 10}
    o = {}
    for k, mx in lim.items():
        v = str(d.get(k, '') or '')
        v = re.sub(r'[\x00-\x08\x0b-\x1f\x7f]', '', v if k == 'note' else re.sub(r'\s+', ' ', v)).strip()[:mx]
        o[k] = v
    for k in ('name', 'concern'):
        if not o[k]: raise ValueError(k)
    p = re.sub(r'\D', '', o['phone'])
    if p.startswith('91') and len(p) == 12: p = p[2:]
    if not re.fullmatch(r'[6-9]\d{9}', p): raise ValueError('phone')
    o['phone'] = p
    if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}', o['email']): raise ValueError('email')     # required: the confirmation is emailed
    try: Date.fromisoformat(o['date'])
    except ValueError: raise ValueError('date')
    if o['time'] not in SLOTS: raise ValueError('time')
    o['source'] = o['source'] if o['source'] in ('chat', 'form') else 'website'
    return o


# ---------------------------------------------------------------- HTTP
class H(BaseHTTPRequestHandler):
    server_version = 'sheroots-book'

    def send(self, code, body, ctype='application/json'):
        data = (json.dumps(body) if ctype == 'application/json' else body).encode()
        self.send_response(code)
        self.send_header('Content-Type', ctype + '; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Robots-Tag', 'noindex, nofollow')
        self.send_header('Referrer-Policy', 'no-referrer')
        if ctype == 'text/html': self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def redirect(self, url):
        # 303 See Other: the browser loads the result page with a normal GET
        self.send_response(303)
        self.send_header('Location', url)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def ip(self): return self.headers.get('X-Real-IP') or self.client_address[0]

    def body(self, limit=6000):
        n = int(self.headers.get('Content-Length', '0') or 0)
        if n <= 0 or n > limit: raise ValueError('size')
        raw = self.rfile.read(n).decode('utf-8')
        if 'json' in (self.headers.get('Content-Type') or ''): return json.loads(raw)
        return {k: v[0] for k, v in parse_qs(raw).items()}

    def do_GET(self):
        u = urlsplit(self.path); q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            if u.path == '/api/health':
                return self.send(200, {'ok': True, 'email': bool(SMTP_USER and SMTP_PASS), 'whatsapp': wa_enabled(), 'whatsapp_patient': {k: wa_patient_on(k) for k in WA_TPL}, 'capacity': CAPACITY})
            if u.path == '/api/slots':
                iso = q.get('date', '')
                Date.fromisoformat(iso)
                with db() as c: return self.send(200, {'date': iso, 'capacity': CAPACITY, 'slots': day_slots(c, iso)})
            m = re.fullmatch(r'/api/s/(SHE-[0-9]{6}-[0-9A-F]{6})', u.path)
            if m:
                if not tok_ok(m.group(1), 'pt', q.get('t', '')): return self.send(404, {'ok': False})
                with db() as c: b = get_booking(c, m.group(1))
                if not b: return self.send(404, {'ok': False})
                return self.send(200, {'ok': True, 'status': b['status'], 'label': STATUS_TEXT[b['status']], 'when': when(b),
                                       'date': b['date'], 'time': b['time'], 'concern': b['concern'], 'url': patient_url(b['ref'])})
            m = re.fullmatch(r'/api/(b|d)/(SHE-[0-9]{6}-[0-9A-F]{6})', u.path)
            if m:
                role = 'pt' if m.group(1) == 'b' else 'dr'
                if not tok_ok(m.group(2), role, q.get('t', '')): return self.send(404, page('Not found', '<div class="card"><h1>Link not valid</h1></div>'), 'text/html')
                with db() as c: b = get_booking(c, m.group(2))
                if not b: return self.send(404, page('Not found', '<div class="card"><h1>Booking not found</h1></div>'), 'text/html')
                msg = result_msg(role, q.get('m', ''), b)
                return self.send(200, patient_page(b, msg) if role == 'pt' else doctor_page(b, msg, do=q.get('do', '')), 'text/html')
            if u.path == '/api/admin':
                if not hmac.compare_digest(q.get('k', ''), ADMIN_KEY): return self.send(404, page('Not found', '<div class="card"><h1>Not found</h1></div>'), 'text/html')
                return self.send(200, admin_page(), 'text/html')
        except ValueError:
            return self.send(400, {'ok': False, 'error': 'bad request'})
        self.send(404, {'ok': False})

    def do_HEAD(self):
        if urlsplit(self.path).path == '/api/health':
            self.send_response(200); self.send_header('Content-Length', '0'); self.end_headers(); return
        self.send_response(404); self.send_header('Content-Length', '0'); self.end_headers()

    def do_POST(self):
        u = urlsplit(self.path)
        origin = self.headers.get('Origin', '')
        # Our own pages send "Referrer-Policy: no-referrer", so browsers post their forms with Origin "null".
        # Allow that only on the doctor/patient pages, which are authorised by the signed token anyway.
        signed_form = origin == 'null' and re.fullmatch(r'/api/(b|d)/SHE-[0-9]{6}-[0-9A-F]{6}', u.path)
        if origin and origin not in ALLOWED_ORIGINS and not signed_form: return self.send(403, {'ok': False, 'error': 'origin'})
        try: data = self.body()
        except Exception: return self.send(400, {'ok': False, 'error': 'bad request'})
        if u.path == '/api/book':
            if data.get('website'): return self.send(200, {'ok': True, 'ref': 'SHE-000000-000000'})   # honeypot
            if not rate_ok(self.ip()): return self.send(429, {'ok': False, 'error': 'too_many', 'message': 'Too many requests. Please call us.'})
            try: d = clean(data)
            except ValueError as e: return self.send(422, {'ok': False, 'error': str(e)})
            code, payload = create_booking(d)
            return self.send(code, payload)
        if u.path == '/api/track':
            if not rate_ok('track:' + self.ip(), limit=10, window=600): return self.send(429, {'ok': False, 'error': 'too_many'})
            ref = str(data.get('ref', '')).strip().upper().replace(' ', '')
            if not ref.startswith('SHE-'): ref = 'SHE-' + ref
            p = re.sub(r'\D', '', str(data.get('phone', '')))
            if p.startswith('91') and len(p) == 12: p = p[2:]
            if not re.fullmatch(r'SHE-[0-9]{6}-[0-9A-F]{6}', ref) or not re.fullmatch(r'\d{10}', p):
                return self.send(422, {'ok': False, 'error': 'format'})
            with db() as c: b = get_booking(c, ref)
            if not b or not hmac.compare_digest(b['phone'], p): return self.send(404, {'ok': False, 'error': 'not_found'})
            return self.send(200, {'ok': True, 'ref': ref, 'status': b['status'], 'label': STATUS_TEXT[b['status']], 'when': when(b),
                                   'date': b['date'], 'time': b['time'], 'concern': b['concern'], 'status_url': patient_url(ref)})
        m = re.fullmatch(r'/api/(b|d)/(SHE-[0-9]{6}-[0-9A-F]{6})', u.path)
        if m:
            role, ref = ('pt' if m.group(1) == 'b' else 'dr'), m.group(2)
            if not tok_ok(ref, role, data.get('t', '')): return self.send(404, page('Not found', '<div class="card"><h1>Link not valid</h1></div>'), 'text/html')
            with db() as c:
                if not get_booking(c, ref): return self.send(404, page('Not found', '<div class="card"><h1>Booking not found</h1></div>'), 'text/html')
            if role == 'pt':
                b, msg = apply_patient_cancel(ref)
                return self.redirect(patient_url(ref) + '&m=' + ('same' if msg.startswith('!') else 'cancelled'))
            act = data.get('action', '')
            if act not in ('accept', 'decline', 'called', 'cancel'): return self.send(400, {'ok': False})
            b, msg = apply_doctor(ref, act, (data.get('reason') or '')[:200])
            code = 'same' if msg.startswith('!') else {'accept': 'confirmed', 'called': 'confirmed', 'decline': 'declined', 'cancel': 'cancelled'}[act]
            return self.redirect(doctor_url(ref) + '&m=' + code)
        self.send(404, {'ok': False})

    def log_message(self, fmt, *args):
        line = fmt % args
        line = re.sub(r'([?&](?:t|k)=)[^& "]+', r'\1***', line)     # never log secret tokens
        sys.stderr.write(f'{self.headers.get("X-Real-IP", "-") if getattr(self, "headers", None) else "-"} {line}\n')


if __name__ == '__main__':
    init_db()
    threading.Thread(target=remind_loop, daemon=True).start()
    print(f'booking API on 127.0.0.1:{PORT}; to={TO or "(unset)"}; smtp={"set" if SMTP_USER and SMTP_PASS else "NOT SET (emails go to outbox)"}; '
          f'capacity={CAPACITY}; slots={SLOTS}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
