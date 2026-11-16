# -*- coding: utf-8 -*-
"""Builds every page of the site.   Run:  python _build/build.py   (from anywhere)
Shared header / footer / chat / trust / Google-reviews blocks live here, so one edit updates all pages."""
import os, re, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE) + os.sep
sys.path.insert(0, HERE)
import content as C

PAGES_DIR = os.path.join(HERE, 'pages'); os.makedirs(PAGES_DIR, exist_ok=True)
esc = lambda s: s.replace('&', '&amp;')
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

GREVIEWS = '''    <section class="greviews" aria-label="Patient reviews on Google" hidden>
      <div class="wrap gr-in">
        <div class="gr-left">
          <span class="gr-g" aria-hidden="true">G</span>
          <div><strong>Patient reviews on Google</strong><span class="gr-rating"></span></div>
        </div>
        <div class="gr-actions"></div>
      </div>
    </section>
'''
CTA = '''    <section class="cta-band">
      <div class="wrap cta-in">
        <div><h2>Ready to feel better?</h2><p>Book a session and let's build your recovery plan together.</p></div>
        <a class="btn btn-gold btn-lg" href="contact.html">Book a session</a>
      </div>
    </section>
'''

def nav_links(active):
    items = [('#top', 'Home'), ('#about', 'About'), ('#explore', 'Treatments'), ('#contact', 'Contact')]
    return ''.join(f'<a href="{h}"' + (' class="active" aria-current="page"' if h == '#top' else '') + f'>{n}</a>' for h, n in items)

def header(active):
    return f'''  <header class="site" id="site-header">
    <div class="nav">
      <a class="brand" href="#top" aria-label="SHEroots Physiotherapy Clinic home">
        <img src="images/logo-left.webp" width="483" height="500" alt="SHEroots logo">
        <span class="brand-text"><strong>SHEroots</strong><small>Physiotherapy Clinic</small></span>
      </a>
      <nav class="links" id="menu" aria-label="Main">
        {nav_links(active)}
        <a class="btn btn-primary menu-cta" data-call href="#contact">{PHONE_SVG}Call us <b class="call-num"></b></a>
      </nav>
      <div class="nav-right">
        <a class="btn btn-primary nav-cta" data-call href="#contact">{PHONE_SVG}Call us</a>
        <img class="badge" src="images/logo-right.webp" width="499" height="500" alt="SHEroots badge">
        <button class="burger" aria-label="Open menu" aria-expanded="false" aria-controls="menu"><span></span><span></span><span></span></button>
      </div>
    </div>
  </header>
'''

def footer():
    return '''<footer class="footer foot-credit">
    <p>Crafted by <strong>Zolvminds</strong></p>
  </footer>'''

MOBILE_BAR = f'''<nav class="mobile-bar" aria-label="Quick actions">
    <a class="mb-call" data-call href="#contact">{PHONE_SVG}<span>Call us</span></a>
    <a href="#explore"><span>Treatments</span></a>
    <a href="#contact"><span>Book</span></a>
  </nav>'''

def prefixize(html, depth):
    if not depth: return html
    pre = '../' * depth
    return re.sub(r'(href|src)="(?!https?:|#|tel:|mailto:|/|data:)([^"]+)"', lambda m: f'{m.group(1)}="{pre}{m.group(2)}"', html)

def page(fname, title, desc, main, active, depth=0, extra_head=''):
    main = main.rstrip() + '\n'
    if '<section class="cta-band">' in main:
        main = main.replace('    <section class="cta-band">', GREVIEWS + '\n    <section class="cta-band">', 1)
    else:
        main += '\n' + GREVIEWS
    root_attr = '../' * depth
    html = f'''<!DOCTYPE html>
<html lang="en" data-root="{root_attr}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="theme-color" content="#e20c75">
  <link rel="icon" href="images/logo-right.webp" type="image/webp">
  <script>document.documentElement.classList.add('js')</script>
  <link rel="stylesheet" href="styles.css">{extra_head}
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>

{header(active)}
  <main id="main">
{main}
  </main>

  {footer()}

  {MOBILE_BAR}

  <script src="script.js"></script>
  <script src="chat.js" defer></script>
</body>
</html>
'''
    html = prefixize(html, depth)
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
    tabs, sets, panels, n = [], [], [], 0
    for gi, (gname, gid) in enumerate(groups):
        cards = []
        for s in C.SERVICES:
            if s[3] != gname: continue
            slug, en, ta, intro = s[0], s[1], s[2], s[4]
            n += 1
            cards.append(f'<li><button type="button" class="ex-item" data-slug="{slug}" aria-haspopup="dialog">'
                         f'<span class="ex-th"><img src="images/tx-{slug}.jpg" width="240" height="300" loading="lazy" alt=""></span>'
                         f'<span class="ex-it"><span class="ex-n">{n:02d}</span><b>{esc(en)}</b><em lang="ta">{ta}</em></span>'
                         f'<span class="ex-ar" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5l7 7-7 7"/></svg></span>'
                         f'<span class="sr-only">View details</span></button></li>')
            signs = "".join(f"<li>{esc(x)}</li>" for x in s[6])
            helps = "".join(f"<li>{esc(x)}</li>" for x in s[7])
            panels.append(f'''<article class="ex-panel" hidden data-slug="{slug}">
              <img class="ex-p-img" src="images/tx-{slug}.jpg" alt="{esc(en)}">
              <div class="ex-p-main">
                <p class="ex-p-group">{esc(gname)}</p>
                <h3>{esc(en)}</h3>
                <p class="ex-p-ta" lang="ta">{ta}</p>
                <p class="ex-p-txt">{esc(intro)}</p>
                <div class="ex-p-more">
                  <div><h5>{esc(s[5])}</h5><ul>{signs}</ul></div>
                  <div><h5>How physiotherapy can help</h5><ul>{helps}</ul></div>
                </div>
                <a class="btn btn-primary" href="#contact" data-service="{esc(en)}">Book a session <span aria-hidden="true">→</span></a>
              </div>
            </article>''')
        tabs.append(f'<button type="button" class="ex-tab ex-tab-{gid}{" on" if gi == 0 else ""}" role="tab" aria-selected="{"true" if gi == 0 else "false"}" data-g="{gi}">'
                    f'<span class="ex-tab-ic" aria-hidden="true"><img src="images/icons/{FILE[gid]}" width="30" height="30" alt=""></span>'
                    f'<span class="ex-tab-t"><strong>{esc(gname)}</strong><small>{SUB[gid]}</small></span>'
                    f'<b class="ex-tab-n">{len(cards)}</b></button>')
        sets.append(f'<ul class="ex-set" data-g="{gi}" role="tabpanel"{"" if gi == 0 else " hidden"}>{"".join(cards)}</ul>')
    return f"""<div class="ex-tabs" role="tablist" aria-label="Treatment groups">{"".join(tabs)}</div>
        <div class="ex-sets">{"".join(sets)}</div>
        <div class="ex-panels" hidden>{"".join(panels)}</div>
        <dialog class="ex-dlg" id="exDialog" aria-label="Treatment details">
          <button type="button" class="ex-x" data-ex-close aria-label="Close">&times;</button>
          <div class="ex-dbody"></div>
          <div class="ex-dnav"><button type="button" data-ex-prev>&#8249; Previous</button><span class="ex-dcount"></span><button type="button" data-ex-next>Next &#8250;</button></div>
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
page('index.html', 'SHEroots Physiotherapy Clinic | Expert Physiotherapy &amp; Women\'s Health',
     'Expert physiotherapy for neck, back, knee and shoulder pain, sports injuries, pelvic health, pregnancy and postnatal care. Open 9 AM to 1 PM and 5 PM to 9 PM.', home, 'index.html')

print('built 1 page (one-page landing)')
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
            <span class="no" aria-hidden="true">{i:02d}</span>
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
            <a class="btn btn-primary" data-call href="#contact">{PHONE_SVG}Call us <b class="call-num"></b></a>
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
      <a class="btn btn-primary" data-call href="#contact">{PHONE_SVG}Call us <b class="call-num"></b></a></div></aside></div></section>
''' + CTA
        page(f'areas/{a["slug"]}.html', f'Physiotherapy in {esc(a["name"])} | SHEroots Physiotherapy Clinic', esc(a['blurb']).replace('"', '&quot;'), m, 'areas/index.html', depth=1)

print('built', 4 + len(C.SERVICES) + (1 + len(C.AREAS) if C.AREAS else 0), 'pages;',
      'hero photo' if photo('hero') else 'no hero photo yet', '|', len(clinic), 'clinic photos')
