# -*- coding: utf-8 -*-
"""Builds every page of the site.   Run:  python _build/build.py   (from anywhere)
Shared header / footer / chat / trust / Google-reviews blocks live here, so one edit updates all pages."""
import os, re, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE) + os.sep
sys.path.insert(0, HERE)
import content as C
import hashlib
ASSET_V = {f: hashlib.md5(open(ROOT + f, 'rb').read()).hexdigest()[:8] for f in ('styles.css', 'script.js', 'chat.js')}

PAGES_DIR = os.path.join(HERE, 'pages'); os.makedirs(PAGES_DIR, exist_ok=True)
esc = lambda s: s.replace('&', '&amp;')
PHONE_TEL = '+919940662500'
PHONE_SVG = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79a15.05 15.05 0 006.59 6.59l2.2-2.2a1 1 0 011.01-.24c1.12.37 2.33.57 3.58.57a1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1c0 1.25.2 2.46.57 3.58a1 1 0 01-.25 1.01l-2.2 2.2z"/></svg>'

# ---------- first run: keep the hand-written main content of these pages as sources ----------
for name in ['index', 'about', 'contact']:
    src = os.path.join(PAGES_DIR, name + '.main.html')
    if not os.path.exists(src):
        h = open(ROOT + name + '.html', encoding='utf-8').read()
        a = h.index('<main id="main">') + len('<main id="main">')
        b = h.index('</main>')
        open(src, 'w', encoding='utf-8').write(h[a:b].strip('\n') + '\n')
main_of = lambda n: open(os.path.join(PAGES_DIR, n + '.main.html'), encoding='utf-8').read()

photo = lambda n: os.path.exists(ROOT + 'images/photos/' + n + '.webp')
TRUST_BLOCK = re.search(r'    <section class="trust".*?</section>\n', main_of('index'), re.S).group(0)

CTA = '''    <section class="cta-band">
      <div class="wrap cta-in">
        <div><h2>Ready to feel better?</h2><p>Book a session and let's build your recovery plan together.</p></div>
        <a class="btn btn-gold btn-lg" href="contact.html">Book a session</a>
      </div>
    </section>
'''

def nav_links(active, base=''):
    items = [('#top', 'Home'), ('#about', 'About'), ('#explore', 'Treatments'), ('#contact', 'Contact')]
    cur = '#top' if not base else ('#explore' if active.startswith('treatments/') else '')
    return ''.join(f'<a href="{base}{h}"' + (' class="active" aria-current="page"' if h == cur else '') + f'>{n}</a>' for h, n in items)

def header(active, base=''):
    return f'''  <header class="site" id="site-header">
    <div class="nav">
      <a class="brand" href="{base or '#top'}" aria-label="SHEroots Physiotherapy Clinic home">
        <img src="images/logo-left.webp" width="483" height="500" alt="SHEroots logo">
        <span class="brand-text"><strong>SHEroots</strong><small>Physiotherapy Clinic</small></span>
      </a>
      <nav class="links" id="menu" aria-label="Main">
        {nav_links(active, base)}
        <a class="btn btn-primary menu-cta" data-call href="tel:+919940662500">{PHONE_SVG}Call us <b class="call-num">99406 62500</b></a>
      </nav>
      <div class="nav-right">
        <a class="btn btn-primary nav-cta" data-call href="tel:+919940662500">{PHONE_SVG}Call us</a>
        <img class="badge" src="images/logo-right.webp" width="499" height="500" alt="SHEroots badge">
        <button class="burger" aria-label="Open menu" aria-expanded="false" aria-controls="menu"><span></span><span></span><span></span></button>
      </div>
    </div>
  </header>
'''

FOOT_SERVICES = ['pelvic-floor', 'pregnancy-care', 'postnatal-care', 'diastasis-recti', 'pcos-pcod',
                 'back-pain-sciatica', 'neck-pain', 'knee-pain']
IG_URL = 'https://www.instagram.com/sherootsphysiotherapy_clinic/'
MAP_URL = 'https://www.google.com/maps?cid=15464404039475393364'
_svg = lambda d, extra='': f'<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"{extra}><path d="{d}"/></svg>'
IC_IG = _svg('M7.5 2h9A5.5 5.5 0 0122 7.5v9a5.5 5.5 0 01-5.5 5.5h-9A5.5 5.5 0 012 16.5v-9A5.5 5.5 0 017.5 2zm0 2A3.5 3.5 0 004 7.5v9A3.5 3.5 0 007.5 20h9a3.5 3.5 0 003.5-3.5v-9A3.5 3.5 0 0016.5 4h-9zM12 7a5 5 0 110 10 5 5 0 010-10zm0 2a3 3 0 100 6 3 3 0 000-6zm5.25-3.25a1.25 1.25 0 110 2.5 1.25 1.25 0 010-2.5z')
IC_WA = _svg('M12 2a10 10 0 00-8.6 15.1L2 22l5-1.3A10 10 0 1012 2zm0 18a8 8 0 01-4.1-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8 8 0 1112 20zm4.4-6c-.2-.1-1.4-.7-1.7-.8s-.4-.1-.5.1-.6.8-.8 1-.3.2-.5.1a6.6 6.6 0 01-3.3-2.9c-.2-.4.2-.4.7-1.3a.4.4 0 000-.4l-.8-1.8c-.2-.5-.4-.4-.5-.4h-.5a.9.9 0 00-.6.3 2.7 2.7 0 00-.9 2 4.7 4.7 0 001 2.5 10.7 10.7 0 004.1 3.6c1.5.7 2.1.7 2.9.6a2.4 2.4 0 001.6-1.1 2 2 0 00.1-1.1c0-.1-.2-.2-.4-.3z')
IC_MAP = _svg('M15 4l-6-2-7 2.5v17.5l7-2.5 6 2 7-2.5V1.5zM10 4.2l4 1.4v14.2l-4-1.4zM4 5.9l4-1.4v14.2l-4 1.4zm16 12.2l-4 1.4V5.6l4-1.4z')

IC_MAIL = _svg('M4 5h16a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V7a2 2 0 012-2zm0 2v.4l8 5 8-5V7H4zm16 2.75l-7.47 4.67a1 1 0 01-1.06 0L4 9.75V17h16V9.75z')
IC_PIN = _svg('M12 2a7 7 0 00-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 00-7-7zm0 9.5A2.5 2.5 0 1112 6.5a2.5 2.5 0 010 5z')
IC_CLOCK = _svg('M12 2a10 10 0 110 20 10 10 0 010-20zm0 2a8 8 0 100 16 8 8 0 000-16zm1 3v4.6l3.2 3.2-1.4 1.4-3.8-3.8V7h2z')

def footer(base=''):
    home = base or '#top'
    svc = ''.join(f'<li><a href="treatments/{sv[0]}.html">{esc(sv[1])}</a></li>'
                  for slug in FOOT_SERVICES for sv in C.SERVICES if sv[0] == slug)
    quick = ''.join(f'<li><a href="{h}">{n}</a></li>' for h, n in (
        (home, 'Home'), (f'{base}#about', 'About us'), (f'{base}#doctor', 'Our doctor'),
        (f'{base}#explore', 'Treatments'), (f'{base}#faq', 'FAQs'), (f'{base}#visit', 'Visit us'),
        (f'{base}#contact', 'Book an appointment')))
    socials = ((IG_URL, '', 'Instagram', IC_IG), ('https://wa.me/', ' data-wa', 'WhatsApp', IC_WA),
               (MAP_URL, '', 'Google Maps', IC_MAP))
    row = ''.join(f'<li><a href="{h}"{extra} target="_blank" rel="noopener" data-tip="{lab}" aria-label="{lab} (opens in a new tab)">{ic}</a></li>'
                  for h, extra, lab, ic in socials)
    return f"""<footer class="sf">
    <div class="wrap">
      <section class="sf-cta" aria-labelledby="sf-cta-h">
        <div class="sf-cta-copy">
          <h2 id="sf-cta-h">Questions before you book?</h2>
          <div class="greviews sf-gr" hidden>
            <span class="gr-g" aria-hidden="true">G</span>
            <span class="gr-txt"><strong>Patient reviews on Google</strong><span class="gr-rating"></span></span>
            <span class="gr-actions"></span>
          </div>
        </div>
        <div class="sf-cta-acts">
          <a class="sf-btn sf-btn-light" data-call href="tel:{PHONE_TEL}">{PHONE_SVG}Call 99406 62500</a>
          <a class="sf-btn sf-btn-line" data-wa href="https://wa.me/" target="_blank" rel="noopener">{IC_WA}WhatsApp us</a>
        </div>
      </section>

      <div class="sf-main">
        <div class="sf-brand">
          <a class="sf-logo" href="{home}" aria-label="SHEroots Physiotherapy Clinic home">
            <img src="images/logo-left.webp" width="483" height="500" alt="" loading="lazy">
            <span><strong>SHEroots</strong><small>Physiotherapy Clinic</small></span>
          </a>
          <p class="sf-about">A women-first physiotherapy clinic in Madurai, led by Dr.&nbsp;Chitra Karthick. Gentle, hands-on care for everyday pain, pregnancy, life after birth and every stage in between.</p>
          <div class="sf-follow">
            <p class="sf-label" id="sf-follow-h">Follow us on</p>
            <ul class="sf-social" aria-labelledby="sf-follow-h">{row}</ul>
          </div>
        </div>
        <nav class="sf-col" aria-labelledby="sf-svc-h">
          <h3 id="sf-svc-h">Services</h3>
          <ul class="sf-links">{svc}</ul>
          <a class="sf-all" href="{base}#explore">View all treatments <i aria-hidden="true">&rarr;</i></a>
        </nav>
        <nav class="sf-col sf-qh" aria-labelledby="sf-quick-h">
          <h3 id="sf-quick-h">Quick links</h3>
          <ul class="sf-links">{quick}</ul>
        </nav>
        <div class="sf-col sf-reach">
          <h3>Contact &amp; hours</h3>
          <ul class="sf-info">
            <li><span class="sf-ic">{PHONE_SVG}</span><span><a data-call href="tel:{PHONE_TEL}">+91 99406 62500</a></span></li>
            <li><span class="sf-ic">{IC_MAIL}</span><span><a href="mailto:sherootsphysio@gmail.com">sherootsphysio@gmail.com</a></span></li>
            <li><span class="sf-ic">{IC_PIN}</span><span><a href="{MAP_URL}" target="_blank" rel="noopener">No.3, Kamarajar 3rd Cross St, Chinna Chokkikulam, Madurai 625002</a></span></li>
            <li class="sf-hrs"><span class="sf-ic">{IC_CLOCK}</span><span>Mon &ndash; Sun &middot; 9:00 AM &ndash; 1:00 PM<br>and 5:00 PM &ndash; 9:00 PM<em class="sf-status" data-open-status hidden></em></span></li>
          </ul>
        </div>
      </div>

      <div class="sf-bottom">
        <p>&copy; <span data-year>2026</span> SHEroots Physiotherapy Clinic. All rights reserved.</p>
        <p>Crafted by <a class="sf-zolv" href="https://www.zolvminds.com/" target="_blank" rel="noopener">Zolvminds</a></p>
      </div>
    </div>
  </footer>"""

def mobile_bar(base=''):
    return f'''<nav class="mobile-bar" aria-label="Quick actions">
    <a class="mb-call" data-call href="tel:+919940662500">{PHONE_SVG}<span>Call us</span></a>
    <a href="{base}#explore"><span>Treatments</span></a>
    <a href="{base}#contact"><span>Book</span></a>
  </nav>'''
MOBILE_BAR = mobile_bar()

def prefixize(html, depth):
    if not depth: return html
    pre = '../' * depth
    return re.sub(r'(href|src)="(?!https?:|#|tel:|mailto:|/|data:)([^"]+)"', lambda m: f'{m.group(1)}="{pre}{m.group(2)}"', html)

# ---- final HTML touches, applied to every page ----
from PIL import Image as _Img
_dims = {}
def _size(src):
    path = ROOT + re.sub(r'^(\.\./)+|^/', '', src.split('?')[0])
    if path not in _dims:
        try: _dims[path] = _Img.open(path).size
        except Exception: _dims[path] = None
    return _dims[path]
def _img_dims(m):
    tag = m.group(0)
    if re.search(r'\swidth=', tag) or re.search(r'\sheight=', tag): return tag
    src = re.search(r'\ssrc="([^"]+)"', tag)
    d = src and not src.group(1).startswith(('http', 'data:')) and _size(src.group(1))
    return tag.replace('<img ', f'<img width="{d[0]}" height="{d[1]}" ', 1) if d else tag
def finalize(html):
    html = re.sub(r'<img\s[^>]*>', _img_dims, html)                          # width/height on every image (no layout jump)
    html = re.sub(r'data-call href="[^"]*"', f'data-call href="tel:{PHONE_TEL}"', html)  # real phone link in the HTML
    return html

def page(fname, title, desc, main, active, depth=0, extra_head=''):
    main = main.rstrip() + '\n'
    root_attr = '../' * depth
    base = '/' if depth else ''
    html = f'''<!DOCTYPE html>
<html lang="en" data-root="{root_attr}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="theme-color" content="#e20c75">
  <link rel="icon" href="/favicon.ico" sizes="48x48">
  <link rel="icon" href="images/favicon-32.png" type="image/png" sizes="32x32">
  <link rel="icon" href="images/icon-192.png" type="image/png" sizes="192x192">
  <link rel="apple-touch-icon" href="images/apple-touch-icon.png">
  <script>document.documentElement.classList.add('js')</script>
  <link rel="stylesheet" href="styles.css?v={ASSET_V['styles.css']}">{extra_head}
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>

{header(active, base)}
  <main id="main">
{main}
  </main>

  {footer(base)}

  {mobile_bar(base)}

  <script src="script.js?v={ASSET_V['script.js']}"></script>
  <script src="chat.js?v={ASSET_V['chat.js']}" defer></script>
</body>
</html>
'''
    html = finalize(prefixize(html, depth))
    out = ROOT + fname
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(html)

def page_hero(kicker, h, lead, ta='', crumbs=''):
    ta_html = f'\n        <p class="ta" lang="ta">{ta}</p>' if ta else ''
    return f'''    <section class="page-hero">
      <div class="wrap">{crumbs}
        <p class="kicker"><i></i>{kicker}</p>
        <h1>{h}</h1>{ta_html}
        <p class="lead">{lead}</p>
      </div>
    </section>
'''

# ---------- HOME (swap hero art for a real photo if one exists; add clinic gallery) ----------
home = main_of('index').replace('class="hero-copy reveal"','class="hero-copy"').replace('class="hero-art reveal"','class="hero-art"')
def explorer():
    """Treatments: two tiles (Core / Women's), each a grid of separate photo cards. A card opens that treatment's details in a dialog."""
    BLURB = {
        'neck-pain': 'Relieves neck pain and stiffness.', 'shoulder-pain': 'Improves shoulder movement.',
        'tennis-elbow': 'Eases elbow pain and strain.', 'back-pain-sciatica': 'Alleviates back pain and nerve pain.',
        'knee-pain': 'Reduces joint pain and stiffness.', 'ankle-sprain': 'Promotes ankle healing and stability.',
        'joint-pain': 'Relieves joint pain and discomfort.', 'wrist-carpal-tunnel': 'Eases wrist pain and numbness.',
        'posture-correction': 'Improves alignment and body balance.', 'sports-injuries': 'Rehabilitates sports and activity injuries.',
        'weight-loss': 'Supports safe, sustainable weight management.', 'pelvic-floor': 'Strengthens pelvic floor and bladder control.',
        'postnatal-care': 'Aids safe and faster postnatal recovery.', 'pcos-pcod': 'Supports hormone balance and wellness.',
        'pregnancy-care': 'Keeps you active and prepared for delivery.', 'diastasis-recti': 'Helps close the abdominal muscle gap.',
        'urinary-incontinence': 'Improves bladder control and confidence.', 'cardiac-rehabilitation': 'Rebuilds heart health, stamina and strength.',
        'dry-needling': 'Relieves muscle tightness and trigger points.',
    }
    ICON = {
        'core': '<path d="M16 3v26M12 7h8M11 12h10M10 17h12M11 22h10"/>',
        'womens': '<path d="M16 5c3 4 3 9 0 14-3-5-3-10 0-14z"/><path d="M16 19c-5-1-9-4-10-9 5 1 9 4 10 9zM16 19c5-1 9-4 10-9-5 1-9 4-10 9z"/>',
    }
    FILE = {'core': 'core-physio.png', 'womens': 'womens-health.png'}
    SUB = {'core': 'Pain, joints, movement', 'womens': 'Pregnancy, postnatal, pelvic'}
    groups = [(C.CORE, 'core'), (C.WOMEN, 'womens')]
    tabs, sets, panels = [], [], []
    for gi, (gname, gid) in enumerate(groups):
        cards = []
        for s in C.SERVICES:
            if s[3] != gname: continue
            slug, en, ta, intro = s[0], s[1], s[2], s[4]
            cards.append(f'<li><button type="button" class="ex-item" data-slug="{slug}" aria-haspopup="dialog">'
                         f'<span class="ex-th"><img src="images/tx-{slug}.jpg" width="240" height="300" loading="lazy" decoding="async" alt="{esc(en)} physiotherapy in Madurai"></span>'
                         f'<span class="ex-it"><b>{esc(en)}</b><em lang="ta">{ta}</em></span>'
                         f'<span class="ex-ar" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></span>'
                         f'<span class="sr-only">View details</span></button></li>')
            signs = "".join(f"<li>{esc(x)}</li>" for x in s[6])
            helps = "".join(f"<li>{esc(x)}</li>" for x in s[7])
            panels.append(f'''<article class="ex-panel" hidden data-slug="{slug}">
              <img class="ex-p-img" src="images/tx-{slug}.jpg" loading="lazy" decoding="async" alt="{esc(en)} physiotherapy at SHEroots, Madurai">
              <div class="ex-p-main">
                <p class="ex-p-group">{esc(gname)}</p>
                <h3>{esc(en)}</h3>
                <p class="ex-p-ta" lang="ta">{ta}</p>
                <p class="ex-p-txt">{esc(intro)}</p>
                <div class="ex-p-more">
                  <div><h5>{esc(s[5])}</h5><ul>{signs}</ul></div>
                  <div><h5>How physiotherapy can help</h5><ul>{helps}</ul></div>
                </div>
                <div class="ex-p-acts"><a class="btn btn-primary" href="#contact" data-service="{esc(en)}">Book a session <span aria-hidden="true">→</span></a>
                <a class="ex-p-link" href="treatments/{slug}.html">Read the full guide <span aria-hidden="true">→</span></a></div>
              </div>
            </article>''')
        tabs.append(f'<button type="button" class="ex-tab ex-tab-{gid}{" on" if gi == 0 else ""}" role="tab" aria-selected="{"true" if gi == 0 else "false"}" data-g="{gi}">'
                    f'<span class="ex-tab-ic" aria-hidden="true"><img src="images/icons/{FILE[gid]}" width="30" height="30" loading="lazy" decoding="async" alt=""></span>'
                    f'<span class="ex-tab-t"><strong>{esc(gname)}</strong><small>{SUB[gid]}</small></span></button>')
        sets.append(f'<ul class="ex-set" data-g="{gi}" role="tabpanel"{"" if gi == 0 else " hidden"}>{"".join(cards)}</ul>')
    return f"""<div class="ex-tabs" role="tablist" aria-label="Treatment groups">{"".join(tabs)}</div>
        <div class="ex-sets">{"".join(sets)}</div>
        <div class="ex-panels" hidden>{"".join(panels)}</div>
        <dialog class="ex-dlg" id="exDialog" aria-label="Treatment details">
          <button type="button" class="ex-x" data-ex-close aria-label="Close">&times;</button>
          <div class="ex-dbody"></div>
          <div class="ex-dnav"><button type="button" data-ex-prev>&#8249; Previous</button><button type="button" data-ex-next>Next &#8250;</button></div>
        </dialog>"""
home = home.replace('<!--EXPLORER-->', explorer())
if photo('hero'):
    alt = C.PHOTO_ALT['hero']
    art = f'''<div class="hx-art hx-photo">
          <div class="photo-frame"><img src="images/photos/hero.webp" alt="{alt}" fetchpriority="high"></div>
          <div class="glass g-badge"><img src="images/logo-right.webp" width="499" height="500" alt=""></div>
          <span class="spark s1"></span><span class="spark s2"></span>
        </div>'''
    home = re.sub(r'<!--HERO-ART-->.*?<!--/HERO-ART-->', lambda m: art, home, count=1, flags=re.S)
clinic = sorted(glob.glob(ROOT + 'images/photos/clinic-*.webp'))
if clinic:
    figs = ''.join(f'<figure class="reveal"><img src="images/photos/{os.path.basename(p)}" alt="Inside SHEroots Physiotherapy Clinic" loading="lazy"></figure>' for p in clinic[:6])
    gal = f'''    <section class="section tinted">
      <div class="wrap">
        <div class="head reveal"><p class="kicker"><i></i>Inside the clinic</p><h2>A space made for you</h2></div>
        <div class="gallery">{figs}</div>
      </div>
    </section>

'''
    i = home.index('<div class="wrap why">'); j = home.rfind('<section', 0, i)
    home = home[:j] + gal + home[j:]
# ---------- SEO: canonical, social cards and structured data (JSON-LD) ----------
import json, html as _html
SITE_URL = 'https://sheroots.gentize.in/'
HOME_TITLE = 'SHEroots Physiotherapy Clinic Madurai | Women&#39;s Health'
HOME_DESC = ('Women-first physiotherapy clinic in Chinna Chokkikulam, Madurai. Back, neck and knee pain, '
             'pelvic floor, pregnancy and postnatal care. Call 99406 62500.')
OG_IMAGE = SITE_URL + 'images/hero-bg-poster.jpg'
CLINIC_ID = SITE_URL + '#clinic'
DOCTOR_ID = SITE_URL + '#dr-chitra-karthick'
ADDRESS = 'No.3, Kamarajar 3rd Cross Street, Chinna Chokkikulam, Madurai &ndash; 625002'
MAPS_URL = 'https://www.google.com/maps?cid=15464404039475393364'
TX_URL = lambda slug: f'{SITE_URL}treatments/{slug}.html'

def _txt(fragment):
    t = re.sub(r'<[^>]+>', ' ', fragment)
    t = _html.unescape(re.sub(r'\s+', ' ', t)).strip()
    return re.sub(r'^[^\w]+', '', t)          # drop leading emoji

def clinic_node():
    return {
        '@type': 'MedicalClinic', '@id': CLINIC_ID,
        'name': 'SHEroots Physiotherapy Clinic', 'alternateName': 'SHEroots',
        'slogan': 'Strong roots. Stronger you.',
        'description': _html.unescape(HOME_DESC),
        'url': SITE_URL, 'logo': SITE_URL + 'images/logo-right.webp',
        'image': [OG_IMAGE, SITE_URL + 'images/doctor-banner.webp'],
        'telephone': '+91-99406-62500', 'email': 'sherootsphysio@gmail.com',
        'address': {'@type': 'PostalAddress',
                    'streetAddress': 'No.3, Kamarajar 3rd Cross Street, Chinna Chokkikulam',
                    'addressLocality': 'Madurai', 'addressRegion': 'Tamil Nadu',
                    'postalCode': '625002', 'addressCountry': 'IN'},
        'hasMap': _html.unescape(MAPS_URL),
        'areaServed': {'@type': 'City', 'name': 'Madurai'},
        'openingHoursSpecification': [
            {'@type': 'OpeningHoursSpecification',
             'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
             'opens': o, 'closes': c} for o, c in (('09:00', '13:00'), ('17:00', '21:00'))],
        'medicalSpecialty': 'https://schema.org/Physiotherapy',
        'availableService': [{'@type': 'MedicalTherapy', 'name': sv[1], 'url': TX_URL(sv[0])} for sv in C.SERVICES],
        'knowsLanguage': ['en', 'ta'],
        'employee': {'@id': DOCTOR_ID},
        'sameAs': ['https://www.instagram.com/sherootsphysiotherapy_clinic/', 'https://www.google.com/maps?cid=15464404039475393364'],
    }

def doctor_node():
    return {
        '@type': 'Person', '@id': DOCTOR_ID,
        'name': 'Chitra Karthick', 'honorificPrefix': 'Dr.', 'honorificSuffix': 'BPT, MIAP, MD (Acu)',
        'jobTitle': 'Physiotherapist',
        'description': "Women's health and pelvic floor specialist, prenatal and postnatal trainer and yoga trainer.",
        'knowsAbout': ["Women's health physiotherapy", 'Pelvic floor rehabilitation',
                       'Prenatal and postnatal exercise', 'Yoga'],
        'image': SITE_URL + 'images/dr-portrait.webp', 'worksFor': {'@id': CLINIC_ID},
    }

def head_tags(url, title, desc, image, image_alt, graph, preload=''):
    ld = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, indent=1).replace('</', '<\\/')
    pre = f'\n  <link rel="preload" as="image" href="{preload}" fetchpriority="high">' if preload else ''
    return f"""
  <link rel="canonical" href="{url}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="geo.region" content="IN-TN">
  <meta name="geo.placename" content="Madurai">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="SHEroots Physiotherapy Clinic">
  <meta property="og:locale" content="en_IN">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="{image}">
  <meta property="og:image:alt" content="{image_alt}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{image}">{pre}
  <script type="application/ld+json">
{ld}
  </script>"""

def seo_head(main_html):
    website = {'@type': 'WebSite', '@id': SITE_URL + '#website', 'url': SITE_URL,
               'name': 'SHEroots Physiotherapy Clinic', 'inLanguage': 'en-IN', 'publisher': {'@id': CLINIC_ID}}
    graph = [clinic_node(), doctor_node(), website]
    faqs = []
    for m in re.finditer(r'<button type="button" class="fc-q".*?</button></h3>\s*<div[^>]*>(.*?)</div>\s*</div>', main_html, re.S):
        q = _txt(re.search(r'<button.*?</button>', m.group(0), re.S).group(0))
        a = _txt(m.group(1))
        if q and a:
            faqs.append({'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}})
    if faqs:
        graph.append({'@type': 'FAQPage', '@id': SITE_URL + '#faq', 'mainEntity': faqs})
    return head_tags(SITE_URL, HOME_TITLE, HOME_DESC, OG_IMAGE, 'SHEroots Physiotherapy Clinic in Madurai',
                     graph, preload='images/hero-bg-poster.jpg')

page('index.html', HOME_TITLE, HOME_DESC, home, 'index.html', extra_head=seo_head(home))

# ---------- ONE PAGE PER TREATMENT: treatments/<slug>.html ----------
SUFFIXES = ('Physiotherapy', 'Treatment', 'Therapy', 'Care', 'Rehabilitation', 'Correction')
by_slug = {sv[0]: sv for sv in C.SERVICES}
import tx_content as TX
TICK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.2 4.2L19 7"/></svg>'

def tx_page(sv):
    slug, en, ta, group, intro, ltitle, signs, helps, rel = sv
    name = esc(en)
    kw = '' if en.endswith(SUFFIXES) else ' Physiotherapy'
    # Keep titles <= 60 and descriptions <= 155 visible characters so search results don't cut them off
    vis = lambda x: len(_html.unescape(x))
    title = next(t for t in (f'{name}{kw} in Madurai | SHEroots', f'{name}{kw} in Madurai',
                             f'{name} in Madurai | SHEroots', f'{name} in Madurai') if vis(t) <= 60 or t.endswith('in Madurai') and ' | ' not in t and kw == '')
    desc = next(d for d in (
        f'{name} treatment in Madurai at SHEroots, Chinna Chokkikulam. Assessment, hands-on care and a home plan. Call 99406 62500.',
        f'{name} treatment in Madurai at SHEroots. Assessment, hands-on care and a home plan. Call 99406 62500.',
        f'{name} treatment in Madurai at SHEroots. Hands-on care and a home plan. Call 99406 62500.') if vis(d) <= 155 or d.startswith(name + ' treatment in Madurai at SHEroots. Hands'))
    desc = desc.replace('"', '&quot;')
    h1_tail = f'{kw.strip().lower() + " " if kw else ""}in Madurai'
    url = TX_URL(slug)
    img_alt = f'{name} physiotherapy at SHEroots, Madurai'
    li = lambda xs: ''.join(f'<li>{TICK}<span>{esc(x)}</span></li>' for x in xs)
    related = ''.join(
        f'<li><a href="treatments/{r}.html"><img src="images/tx-{r}.jpg" width="60" height="75" loading="lazy" alt="">'
        f'<span>{esc(by_slug[r][1])}</span></a></li>' for r in rel if r in by_slug)
    X = TX.EXTRA[slug]
    svc_name = name + kw
    is_condition = ltitle == 'Signs you may notice' and slug not in ('pregnancy-care', 'postnatal-care')
    causes_h = 'What can cause it?' if is_condition else 'Common reasons people come to us'
    general = [qa for qa in C.FAQ if qa[0] in ('Is this right for me?', 'What should I bring?')]
    faqs = list(X['faqs']) + general
    faq = ''.join(f'<details class="tp-faq"{" open" if i == 0 else ""}><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for i, (q, a) in enumerate(faqs))
    warn = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l9.5 17h-19L12 3z"/><path d="M12 10v4.5M12 17.2v.1"/></svg>' 
    crumbs = (f'<nav class="tp-crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span>'
              f'<a href="/#explore">Treatments</a><span aria-hidden="true">/</span><span aria-current="page">{name}</span></nav>')
    main = f'''    <section class="tp-hero">
      <div class="wrap tp-hero-in">
        <div class="tp-hero-copy">
          {crumbs}
          <p class="kicker"><i></i>{esc(group)}</p>
          <h1>{name} <span>{h1_tail}</span></h1>
          <p class="tp-ta" lang="ta">{ta}</p>
          <p class="tp-lead">{esc(intro)}</p>
          <div class="tp-cta">
            <a class="btn btn-primary btn-lg" data-call href="/#contact">{PHONE_SVG}Call us</a>
            <a class="btn btn-ghost btn-lg" href="/#contact">Book a session</a>
          </div>
        </div>
        <figure class="tp-hero-img"><img src="images/tx-{slug}.jpg" width="600" height="750" alt="{img_alt}" fetchpriority="high"></figure>
      </div>
    </section>

    <section class="tp-body">
      <div class="wrap tp-grid">
        <article class="tp-main">
          <div class="tp-two">
            <div class="tp-box"><h2>{esc(ltitle)}</h2><ul class="tp-ticks">{li(signs)}</ul></div>
            <div class="tp-box tp-box-pink"><h2>How physiotherapy helps</h2><ul class="tp-ticks">{li(helps)}</ul></div>
          </div>

          <h2>{causes_h}</h2>
          <ul class="tp-dots">{''.join(f'<li>{esc(x)}</li>' for x in X['causes'])}</ul>

          <h2>What {svc_name} sessions involve</h2>
          <p>{esc(X['sessions'])}</p>

          <h2>How long recovery can take</h2>
          <p>{esc(X['timeline'])}</p>

          <h2>What to expect at your first visit</h2>
          <ol class="tp-steps">
            <li><b>We listen</b><span>A relaxed conversation about your history, your goals and what worries you.</span></li>
            <li><b>We assess</b><span>A careful assessment to find the cause, with every step explained first.</span></li>
            <li><b>We plan together</b><span>Hands-on care, guided exercise and a home plan made for you.</span></li>
          </ol>

          <div class="tp-two tp-two-gap">
            <div class="tp-box"><h2>Simple things that help at home</h2><ul class="tp-ticks">{li(X['home'])}</ul></div>
            <div class="tp-box tp-warn"><h2>{warn}See a doctor first if you have</h2><ul class="tp-dots">{''.join(f'<li>{esc(x)}</li>' for x in X['urgent'])}</ul></div>
          </div>

          <h2>{name} care at SHEroots, Madurai</h2>
          <p>SHEroots is a women-first physiotherapy clinic in Chinna Chokkikulam, Madurai, led by
          <a href="/#doctor">Dr. Chitra Karthick</a> (BPT, MIAP, MD (Acu)). Every plan starts with a proper assessment,
          and we look for the reason behind your symptoms, not only the pain itself. Sessions take place in a calm,
          private room, and we explain each step in plain words, in English or Tamil.</p>

          <h2>{name}: common questions</h2>
          <div class="tp-faqs">{faq}</div>

          <p class="tp-note">This page is general information, not a diagnosis or medical advice. Results vary from person to person. If you have severe or sudden symptoms, please seek urgent medical care.</p>
        </article>

        <aside class="tp-side">
          <div class="tp-card tp-book">
            <h2>Book a session</h2>
            <p class="tp-hours">Open daily<br><b>9 AM &ndash; 1 PM &middot; 5 PM &ndash; 9 PM</b></p>
            <a class="btn btn-primary" data-call href="tel:+919940662500">{PHONE_SVG}Call 99406 62500</a>
            <a class="btn btn-ghost" href="/#contact">Request an appointment</a>
            <p class="tp-addr">{ADDRESS}</p>
            <a class="tp-dir" href="{MAPS_URL}" target="_blank" rel="noopener">Get directions <span aria-hidden="true">&rarr;</span></a>
          </div>
          <div class="tp-card">
            <h2>Related treatments</h2>
            <ul class="tp-rel">{related}</ul>
            <a class="tp-all" href="/#explore">All treatments <span aria-hidden="true">&rarr;</span></a>
          </div>
        </aside>
      </div>
    </section>
'''
    graph = [
        {'@type': 'MedicalWebPage', '@id': url + '#page', 'url': url,
         'name': _html.unescape(title), 'description': _html.unescape(desc),
         'inLanguage': 'en-IN', 'audience': {'@type': 'PeopleAudience', 'geographicArea': {'@type': 'City', 'name': 'Madurai'}},
         'about': {'@type': 'MedicalTherapy', 'name': en},
         'primaryImageOfPage': SITE_URL + f'images/tx-{slug}.jpg',
         'publisher': {'@id': CLINIC_ID},
         'breadcrumb': {'@id': url + '#breadcrumb'}},
        {'@type': 'BreadcrumbList', '@id': url + '#breadcrumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE_URL},
            {'@type': 'ListItem', 'position': 2, 'name': 'Treatments', 'item': SITE_URL + '#explore'},
            {'@type': 'ListItem', 'position': 3, 'name': en, 'item': url}]},
        {'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]},
        clinic_node(), doctor_node(),
    ]
    extra = head_tags(url, title, desc, SITE_URL + f'images/tx-{slug}.jpg', img_alt, graph)
    page(f'treatments/{slug}.html', title, desc, main, f'treatments/{slug}.html', depth=1, extra_head=extra)

for sv in C.SERVICES:
    tx_page(sv)

# ---------- 404 page (served by nginx for any missing URL, so every link is absolute) ----------
nf_links = ''.join(f'<li><a href="{TX_URL(sv[0]).replace(SITE_URL, "/")}">{esc(sv[1])}</a></li>' for sv in C.SERVICES[:8])
nf_main = f'''    <section class="section nf">
      <div class="container nf-wrap">
        <p class="kicker">Page not found</p>
        <h1>Sorry, we couldn&#39;t find that page</h1>
        <p class="lead">The link may be old or mistyped. Here is where you can go next:</p>
        <div class="nf-acts">
          <a class="btn btn-primary btn-lg" href="/">Go to the home page</a>
          <a class="btn btn-ghost btn-lg" href="/#contact">Book an appointment</a>
          <a class="btn btn-ghost btn-lg" data-call href="tel:{PHONE_TEL}">Call 99406 62500</a>
        </div>
        <h2 class="nf-h">Popular treatments</h2>
        <ul class="nf-list">{nf_links}<li><a href="/#explore">All treatments &rarr;</a></li></ul>
      </div>
    </section>'''
page('404.html', 'Page not found | SHEroots Physiotherapy Clinic', 'This page could not be found.', nf_main, '', extra_head='\n  <meta name="robots" content="noindex">')
_nf = open(ROOT + '404.html', encoding='utf-8').read().replace('data-root=""', 'data-root="/"')
_nf = re.sub(r'(href|src)="(?!https?:|#|tel:|mailto:|/|data:)([^"]+)"', r'\1="/\2"', _nf)
_nf = re.sub(r'href="#(?!main")', 'href="/#', _nf)
open(ROOT + '404.html', 'w', encoding='utf-8').write(_nf)

# ---------- sitemap.xml ----------
import datetime
today = datetime.date.today().isoformat()
urls = [(SITE_URL, ['images/hero-bg-poster.jpg', 'images/doctor-banner.webp', 'images/dr-portrait.webp'])] + \
       [(TX_URL(sv[0]), [f'images/tx-{sv[0]}.jpg']) for sv in C.SERVICES]
sm = ''.join(f'  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n' +
             ''.join(f'    <image:image><image:loc>{SITE_URL}{i}</image:loc></image:image>\n' for i in imgs) +
             '  </url>\n' for u, imgs in urls)
open(ROOT + 'sitemap.xml', 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
    'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + sm + '</urlset>\n')

print(f'built index.html + {len(C.SERVICES)} treatment pages + sitemap.xml')
sys.exit(0)

# ---------- ABOUT ----------
about = main_of('about')
if photo('team'):
    team = f'''    <section class="section">
      <div class="wrap about-team">
        <figure class="reveal"><img src="images/photos/team.webp" alt="{C.PHOTO_ALT['team']}" loading="lazy"></figure>
        <div class="reveal"><p class="kicker"><i></i>Our team</p><h2>People who listen first</h2>
          <p class="sub">Add a short, true introduction to your physiotherapist and team here.</p></div>
      </div>
    </section>

'''
    k = about.index('<section class="section tinted"')
    about = about[:k] + team + about[k:]
page('about.html', 'About | SHEroots Physiotherapy Clinic', 'Our approach to physiotherapy: listen, assess, treat, thrive.', about, 'about.html')

# ---------- CONTACT ----------
page('contact.html', 'Contact &amp; Book | SHEroots Physiotherapy Clinic', 'Book a physiotherapy session at SHEroots. Open 9 AM to 1 PM and 5 PM to 9 PM.', main_of('contact'), 'contact.html')

# ---------- TREATMENTS INDEX ----------
def card(i, s):
    slug, en, ta = s[0], s[1], s[2]
    return f'''          <a class="card reveal" href="treatments/{slug}.html">
            <h3>{esc(en)}</h3>
            <p lang="ta">{esc(ta)}</p>
            <span class="more">Learn more <span aria-hidden="true">→</span></span>
          </a>'''
core = [s for s in C.SERVICES if s[3] == C.CORE]
women = [s for s in C.SERVICES if s[3] == C.WOMEN]
tmain = page_hero('Our treatments', 'Expert physiotherapy care', 'Personalised treatment for pain, injury and women\'s health, in a comfortable and private setting.', 'எங்கள் சிகிச்சைகள்') + '\n' + TRUST_BLOCK + f'''
    <section class="section">
      <div class="wrap">
        <div class="group-head reveal" id="core"><h3>Core Physiotherapy Treatments</h3><span lang="ta">முக்கிய பிசியோதெரபி சிகிச்சைகள்</span></div>
        <div class="cards">
{chr(10).join(card(i, s) for i, s in enumerate(core, 1))}
        </div>
        <div class="group-head reveal" id="womens"><h3>Women's Health &amp; Rehabilitation</h3><span lang="ta">பெண்கள் நலம் &amp; மறுவாழ்வு</span></div>
        <div class="cards">
{chr(10).join(card(i, s) for i, s in enumerate(women, len(core) + 1))}
        </div>
      </div>
    </section>

''' + CTA
page('treatments.html', 'Treatments | SHEroots Physiotherapy Clinic', 'All our physiotherapy treatments: neck, back, knee, shoulder, sports injuries, pelvic floor, pregnancy, postnatal, PCOS and more.', tmain, 'treatments.html')

# ---------- ONE PAGE PER SERVICE ----------
by_slug = {s[0]: s for s in C.SERVICES}
faq_html = ''.join(f'<details class="faq"><summary>{q}</summary><p>{a}</p></details>' for q, a in C.FAQ)
for s in C.SERVICES:
    slug, en, ta, group, intro, ltitle, signs, help_, rel = s
    crumbs = f'<nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span>›</span><a href="treatments.html">Treatments</a><span>›</span><span aria-current="page">{esc(en)}</span></nav>'
    has_img = photo('service-' + slug)
    img = f'<figure class="svc-photo"><img src="images/photos/service-{slug}.webp" alt="{esc(en)} physiotherapy at SHEroots" loading="lazy"></figure>' if has_img else ''
    related = ''.join(f'<li><a href="treatments/{r}.html">{esc(by_slug[r][1])}</a></li>' for r in rel)
    main = page_hero(group, esc(en), intro, esc(ta), crumbs) + '\n' + TRUST_BLOCK + f'''
    <section class="section">
      <div class="wrap svc-grid">
        <div class="svc-main">
          {img}
          <h2>{ltitle}</h2>
          <ul class="ticks-list">{''.join(f'<li>{x}</li>' for x in signs)}</ul>
          <h2>How physiotherapy can help</h2>
          <ul class="ticks-list">{''.join(f'<li>{x}</li>' for x in help_)}</ul>
          <h2>What to expect</h2>
          <ol class="mini-steps">
            <li><b>We listen.</b> A relaxed conversation about your history, goals and concerns.</li>
            <li><b>We assess.</b> A careful assessment, with every step explained.</li>
            <li><b>We plan together.</b> Treatment and exercises tailored to you, with a home plan.</li>
          </ol>
          <h2>Common questions</h2>
          {faq_html}
          <p class="disclaimer">This page is general information, not a diagnosis or medical advice. Results vary from person to person. If you have severe or sudden symptoms, seek urgent medical care.</p>
        </div>
        <aside class="svc-side">
          <div class="side-card">
            <h3>Book a session</h3>
            <p>Open 9 AM – 1 PM and 5 PM – 9 PM.<br><span lang="ta">காலை 9 – 1 · மாலை 5 – 9</span></p>
            <a class="btn btn-primary" data-call href="tel:+919940662500">{PHONE_SVG}Call us <b class="call-num">99406 62500</b></a>
            <a class="btn btn-ghost" href="contact.html">Request an appointment</a>
          </div>
          <div class="side-card">
            <h3>Related treatments</h3>
            <ul class="rel">{related}</ul>
            <a class="link-arrow" href="treatments.html">All treatments <span aria-hidden="true">→</span></a>
          </div>
        </aside>
      </div>
    </section>

''' + CTA
    page(f'treatments/{slug}.html', f'{esc(en)} Physiotherapy | SHEroots Physiotherapy Clinic', intro.replace('"', '&quot;'), main, 'treatments.html', depth=1)

# ---------- ONE PAGE PER AREA (only for areas listed in content.py) ----------
if C.AREAS:
    cards = ''.join(f'<a class="card reveal" href="areas/{a["slug"]}.html"><h3>{esc(a["name"])}</h3><p>{esc(a["blurb"])}</p><span class="more">Physiotherapy in {esc(a["name"])} <span aria-hidden="true">→</span></span></a>' for a in C.AREAS)
    page('areas/index.html', 'Areas we serve | SHEroots Physiotherapy Clinic', 'Areas served by SHEroots Physiotherapy Clinic.',
         page_hero('Areas we serve', 'Physiotherapy near you', 'Find the details for your area.') + f'<section class="section"><div class="wrap"><div class="cards">{cards}</div></div></section>\n' + CTA, 'areas/index.html', depth=1)
    for a in C.AREAS:
        links = ''.join(f'<li><a href="treatments/{s[0]}.html">{esc(s[1])}</a></li>' for s in C.SERVICES)
        crumbs = f'<nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span>›</span><a href="areas/index.html">Areas</a><span>›</span><span aria-current="page">{esc(a["name"])}</span></nav>'
        m = page_hero('Local physiotherapy', f'Physiotherapy in {esc(a["name"])}', esc(a['blurb']), crumbs=crumbs) + '\n' + TRUST_BLOCK + f'''
    <section class="section"><div class="wrap svc-grid"><div class="svc-main">
      <h2>Getting here</h2><p>{esc(a.get("how_to_find", ""))}</p>
      <h2>Treatments available</h2><ul class="ticks-list cols">{links}</ul>
    </div>
    <aside class="svc-side"><div class="side-card"><h3>Book a session</h3><p>Open 9 AM – 1 PM and 5 PM – 9 PM.</p>
      <a class="btn btn-primary" data-call href="tel:+919940662500">{PHONE_SVG}Call us <b class="call-num">99406 62500</b></a></div></aside></div></section>
''' + CTA
        page(f'areas/{a["slug"]}.html', f'Physiotherapy in {esc(a["name"])} | SHEroots Physiotherapy Clinic', esc(a['blurb']).replace('"', '&quot;'), m, 'areas/index.html', depth=1)

print('built', 4 + len(C.SERVICES) + (1 + len(C.AREAS) if C.AREAS else 0), 'pages;',
      'hero photo' if photo('hero') else 'no hero photo yet', '|', len(clinic), 'clinic photos')
