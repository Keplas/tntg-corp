#!/usr/bin/env python3
"""
T&TG Design Patch System
════════════════════════
RULE: Never edit home.html, base.html, style.css or translations.py directly.
Always run this script instead. It restores the locked originals and applies
only the approved patches below.

Usage:
  python apply_patches.py

After running, git add and push as normal.
"""

import shutil, re, os

BASE = os.path.dirname(os.path.abspath(__file__))
PROTECTED = os.path.join(BASE, '_protected')

# ── Step 1: Restore locked originals ──────────────────────────────────────────
FILES = {
    'home':    ('home.html',         'templates/core/home.html'),
    'base':    ('base.html',         'templates/base.html'),
    'css':     ('style.css',         'static/css/style.css'),
    'trans':   ('translations.py',   'core/translations.py'),
}

print("Restoring originals...")
for key, (src, dst) in FILES.items():
    shutil.copy(os.path.join(PROTECTED, src), os.path.join(BASE, dst))
    print(f"  ✓ {dst}")

# ── Step 2: Load all files ─────────────────────────────────────────────────────
def read(path):
    with open(os.path.join(BASE, path)) as f: return f.read()

def write(path, content):
    with open(os.path.join(BASE, path), 'w') as f: f.write(content)

home  = read('templates/core/home.html')
base  = read('templates/base.html')
css   = read('static/css/style.css')
trans = read('core/translations.py')

patches_applied = []

# ══════════════════════════════════════════════════════════════════════════════
# APPROVED PATCHES — Add new changes below this line only
# Each patch must have: description, old string, new string
# ══════════════════════════════════════════════════════════════════════════════

# ── PATCH 1: Coffee-only product filters ──────────────────────────────────────
OLD = re.search(
    r'<a href="[^"]*\?category=clothing[^"]*".*?btn-outline-gold[^>]*>.*?</a>.*?'
    r'<a href="[^"]*\?gender=women[^"]*".*?btn-outline-gold[^>]*>.*?</a>',
    home, re.DOTALL
)
if OLD:
    home = home.replace(OLD.group(0),
        '<a href="{% url \'product_list\' %}?category=coffee" class="btn btn-sm btn-outline-gold">☕ All Coffee</a>\n'
        '      <a href="{% url \'product_list\' %}?category=coffee&name=arabica" class="btn btn-sm btn-outline-gold">🌱 Arabica</a>\n'
        '      <a href="{% url \'product_list\' %}?category=coffee&name=robusta" class="btn btn-sm btn-outline-gold">🫘 Robusta</a>'
    )
    patches_applied.append("PATCH 1: Coffee-only filters")

# ── PATCH 2: Coffee Shop card (was Online Shopping) ───────────────────────────
home = home.replace(
    'photo-1567401893414-76b7b1e5a7a5?w=600&h=400&fit=crop&q=80',
    'photo-1447933601403-0c6688de566e?w=600&h=400&fit=crop&q=80'
)
home = home.replace('Online Shopping', 'T&TG Shopping Platform')
home = home.replace(
    'alt="Online shopping — clothing, shoes, watches and coffee"',
    'alt="T&TG Coffee — Arabica and Robusta green coffee"'
)
home = home.replace('<div class="tg-card-icon-overlay">🛒</div>',
                    '<div class="tg-card-icon-overlay">☕</div>')
home = home.replace('Online Shopping Platform', 'T&TG Coffee Platform')
home = home.replace(
    'Clothing, shoes, watches and coffee for men and women across Local &amp; International markets.',
    'Premium T&amp;TG Arabica and Robusta green coffee, sourced from Uganda and exported across our trade corridors.'
)
patches_applied.append("PATCH 2: Coffee Shop card")

# ── PATCH 3: USA / Ohio on world map ──────────────────────────────────────────
# 3a. Ohio city coordinates
home = home.replace(
    "    toronto: [-79.38, 43.65],\n    kampala: [ 32.58,  0.35],\n    nairobi: [ 36.82, -1.29]",
    "    toronto: [-79.38, 43.65],\n    ohio:    [-82.99, 39.96],\n    kampala: [ 32.58,  0.35],\n    nairobi: [ 36.82, -1.29]"
)
# 3b. Ohio trade routes
home = home.replace(
    "    [CITIES.toronto, CITIES.kampala],\n    [CITIES.toronto, CITIES.nairobi],\n    [CITIES.kampala, CITIES.nairobi]",
    "    [CITIES.toronto, CITIES.kampala],\n    [CITIES.toronto, CITIES.nairobi],\n    [CITIES.toronto, CITIES.ohio],\n    [CITIES.ohio,    CITIES.kampala],\n    [CITIES.ohio,    CITIES.nairobi],\n    [CITIES.kampala, CITIES.nairobi]"
)
# 3c. USA badge (appended after Kenya badge)
OLD_KE = '''          <div class="tg-cbadge tg-cb-ke">
            <div class="tg-cb-flag">🇰🇪</div>
            <div><div class="tg-cb-name">Kenya</div><div class="tg-cb-role">Trade Gateway · Nairobi</div></div>
          </div>'''
if OLD_KE in home and 'tg-cb-us' not in home:
    home = home.replace(OLD_KE, OLD_KE + '''
          <div class="tg-cbadge tg-cb-us">
            <div class="tg-cb-flag">🇺🇸</div>
            <div><div class="tg-cb-name">USA</div><div class="tg-cb-role">Midwest Hub · Ohio</div></div>
          </div>''')
patches_applied.append("PATCH 3: USA/Ohio on map")

# 3d. Countries stat: 3 → 4
home = home.replace(
    '<span class="tg-stat-val">3</span>\n            <span class="tg-stat-lbl">{% t "hero_stat_countries" %}</span>',
    '<span class="tg-stat-val">4</span>\n            <span class="tg-stat-lbl">{% t "hero_stat_countries" %}</span>'
)

# ── PATCH 4: Translations — coffee + 4 countries ──────────────────────────────
trans = trans.replace(
    "Shop textiles, shoes, watches and coffee.",
    "Shop T&TG Arabica and Robusta green coffee."
)
trans = trans.replace(
    "connects Canada, Uganda and Kenya",
    "connects Canada, Uganda, Kenya and USA (Ohio)"
)
trans = trans.replace("'hero_stat_countries': '3 Countries'", "'hero_stat_countries': '4 Countries'")
patches_applied.append("PATCH 4: Translations")

# ── PATCH 5: Search bar placeholder ───────────────────────────────────────────
base = base.replace(
    'placeholder="Search clothing, shoes, watches, coffee…"',
    'placeholder="Search T&TG coffee — Arabica, Robusta…"'
)
patches_applied.append("PATCH 5: Search placeholder")

# ── PATCH 6: USA badge CSS ────────────────────────────────────────────────────
if 'tg-cb-us' not in css:
    css += (
        '\n/* ── USA badge ─────────────────────────────────────────────── */\n'
        '.tg-cb-us { top: 36%; left: 4%; animation: cf4 4.8s ease infinite; }\n'
        '@keyframes cf4 { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-7px)} }\n'
        '@media (max-width:576px) { .tg-cb-us { top: 48%; left: 2%; } }\n'
    )
patches_applied.append("PATCH 6: USA badge CSS")

# ══════════════════════════════════════════════════════════════════════════════

# ── PATCH 7: Dynamic imagery backgrounds ──────────────────────────────────────
# Adds parallax coffee imagery, floating particle canvas, and section visuals
# WITHOUT touching any existing HTML structure or CSS classes.

DYNAMIC_BG_CSS = """
/* ════════════════════════════════════════════════════════════
   PATCH 7 — Dynamic imagery & visual depth
   ═══════════════════════════════════════════════════════════ */

/* ── Hero: cinematic coffee-field background image ─────────── */
.tg-hero::before {
  content: '';
  position: absolute; inset: 0; z-index: 0;
  background-image: url('https://images.unsplash.com/photo-1523712999610-f77fbcfc3843?w=1600&h=900&fit=crop&q=60');
  background-size: cover;
  background-position: center 30%;
  background-attachment: fixed;
  opacity: .08;
  filter: saturate(0.4);
  pointer-events: none;
}

/* ── Floating gold particles (JS canvas injected) ──────────── */
#tg-particles {
  position: fixed; top: 0; left: 0;
  width: 100%; height: 100%;
  pointer-events: none; z-index: 0;
  opacity: .45;
}

/* ── Section 2 (what we offer): subtle bean texture ────────── */
.tg-offer-section::before {
  content: '';
  position: absolute; inset: 0; z-index: 0;
  background-image: url('https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=1600&h=800&fit=crop&q=50');
  background-size: cover;
  background-position: center;
  opacity: .04;
  pointer-events: none;
}

/* ── Scrolling coffee image strip between hero and offer ────── */
.tg-img-strip {
  width: 100%; overflow: hidden;
  height: 220px; position: relative;
  background: #04090f;
}
.tg-img-strip-track {
  display: flex; gap: 0;
  animation: stripScroll 40s linear infinite;
  width: max-content; height: 100%;
}
.tg-img-strip-track:hover { animation-play-state: paused; }
.tg-img-strip img {
  height: 220px; width: 340px;
  object-fit: cover; flex-shrink: 0;
  opacity: .75; transition: opacity .3s;
  filter: saturate(.8);
}
.tg-img-strip img:hover { opacity: 1; filter: saturate(1.1); }
@keyframes stripScroll {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}

/* ── Section divider glow lines ─────────────────────────────── */
.tg-glow-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(201,168,76,.5) 30%, rgba(201,168,76,.8) 50%, rgba(201,168,76,.5) 70%, transparent);
  margin: 0;
}

/* ── Country cards section: coffee field background ─────────── */
.tg-countries-section {
  position: relative;
}
.tg-countries-section::before {
  content: '';
  position: absolute; inset: 0; z-index: 0;
  background-image: url('https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=1600&h=900&fit=crop&q=50');
  background-size: cover;
  background-position: center;
  opacity: .05;
  pointer-events: none;
}

/* ── Floating animated coffee beans in hero ─────────────────── */
@keyframes floatBean {
  0%   { transform: translateY(0px)   rotate(0deg);   opacity: 0; }
  10%  { opacity: .6; }
  90%  { opacity: .6; }
  100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
}
.tg-bean {
  position: fixed; pointer-events: none; z-index: 0;
  font-size: 1rem; animation: floatBean linear infinite;
  filter: opacity(.25);
}
"""

DYNAMIC_BG_JS = """
<script>
/* ── Floating gold particles ──────────────────────────────────────── */
(function(){
  var canvas = document.createElement('canvas');
  canvas.id = 'tg-particles';
  document.body.insertBefore(canvas, document.body.firstChild);
  var ctx = canvas.getContext('2d');
  var W, H, pts = [];

  function resize(){ W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }
  window.addEventListener('resize', resize); resize();

  // Create 55 particles
  for(var i = 0; i < 55; i++){
    pts.push({
      x: Math.random() * W, y: Math.random() * H,
      r: Math.random() * 1.4 + .3,
      dx: (Math.random() - .5) * .35,
      dy: (Math.random() - .5) * .35,
      a: Math.random()
    });
  }

  function draw(){
    ctx.clearRect(0,0,W,H);
    pts.forEach(function(p){
      p.x += p.dx; p.y += p.dy;
      if(p.x < 0) p.x = W; if(p.x > W) p.x = 0;
      if(p.y < 0) p.y = H; if(p.y > H) p.y = 0;
      p.a += .008;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
      ctx.fillStyle = 'rgba(201,168,76,' + (.2 + .3*Math.abs(Math.sin(p.a))) + ')';
      ctx.fill();
    });
    // Draw connecting lines between close particles
    for(var i = 0; i < pts.length; i++){
      for(var j = i+1; j < pts.length; j++){
        var dx = pts[i].x - pts[j].x, dy = pts[i].y - pts[j].y;
        var dist = Math.sqrt(dx*dx + dy*dy);
        if(dist < 120){
          ctx.beginPath();
          ctx.moveTo(pts[i].x, pts[i].y);
          ctx.lineTo(pts[j].x, pts[j].y);
          ctx.strokeStyle = 'rgba(201,168,76,' + (.06*(1-dist/120)) + ')';
          ctx.lineWidth = .5;
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(draw);
  }
  draw();
})();

/* ── Parallax: hero background shifts on scroll ───────────────────── */
window.addEventListener('scroll', function(){
  var hero = document.querySelector('.tg-hero');
  if(hero){ hero.style.backgroundPositionY = (window.scrollY * 0.25) + 'px'; }
}, {passive:true});
</script>
"""

STRIP_HTML = """
<!-- ── T&TG Coffee Image Strip ─────────────────────────────────────── -->
<div class="tg-img-strip">
  <div class="tg-img-strip-track">
    <img src="https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=340&h=220&fit=crop&q=70" alt="Coffee roasting">
    <img src="https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=340&h=220&fit=crop&q=70" alt="Coffee espresso">
    <img src="https://images.unsplash.com/photo-1494412574643-ff11b0a5c1c3?w=340&h=220&fit=crop&q=70" alt="Shipping containers">
    <img src="https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=340&h=220&fit=crop&q=70" alt="Coffee beans">
    <img src="https://images.unsplash.com/photo-1590496793907-4d66e2994b4d?w=340&h=220&fit=crop&q=70" alt="Cargo port">
    <img src="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=340&h=220&fit=crop&q=70" alt="Forex trading">
    <img src="https://images.unsplash.com/photo-1578575437130-527eed3abbec?w=340&h=220&fit=crop&q=70" alt="Cargo ship">
    <img src="https://images.unsplash.com/photo-1541167760496-1628856ab772?w=340&h=220&fit=crop&q=70" alt="Coffee pour">
    <!-- duplicate for seamless loop -->
    <img src="https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=340&h=220&fit=crop&q=70" alt="Coffee roasting">
    <img src="https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=340&h=220&fit=crop&q=70" alt="Coffee espresso">
    <img src="https://images.unsplash.com/photo-1494412574643-ff11b0a5c1c3?w=340&h=220&fit=crop&q=70" alt="Shipping containers">
    <img src="https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=340&h=220&fit=crop&q=70" alt="Coffee beans">
    <img src="https://images.unsplash.com/photo-1590496793907-4d66e2994b4d?w=340&h=220&fit=crop&q=70" alt="Cargo port">
    <img src="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=340&h=220&fit=crop&q=70" alt="Forex trading">
    <img src="https://images.unsplash.com/photo-1578575437130-527eed3abbec?w=340&h=220&fit=crop&q=70" alt="Cargo ship">
    <img src="https://images.unsplash.com/photo-1541167760496-1628856ab772?w=340&h=220&fit=crop&q=70" alt="Coffee pour">
  </div>
</div>
<div class="tg-glow-divider"></div>
"""

# Inject CSS into style.css
css += DYNAMIC_BG_CSS
write('static/css/style.css', css)

# Inject the scrolling image strip between hero and offer section
if '<section class="tg-offer-section">' in home and 'tg-img-strip' not in home:
    home = home.replace(
        '<section class="tg-offer-section">',
        STRIP_HTML + '<section class="tg-offer-section">'
    )

# Inject particle JS before closing </body>
if 'tg-particles' not in home and '</body>' in home:
    home = home.replace('</body>', DYNAMIC_BG_JS + '\n</body>')

write('templates/core/home.html', home)
patches_applied.append("PATCH 7: Dynamic imagery backgrounds")


# ── PATCH 8: Remove hero coffee plantation background image ───────────────────
css = css.replace(
    """.tg-hero::before {
  content: '';
  position: absolute; inset: 0; z-index: 0;
  background-image: url('https://images.unsplash.com/photo-1523712999610-f77fbcfc3843?w=1600&h=900&fit=crop&q=60');
  background-size: cover;
  background-position: center 30%;
  background-attachment: fixed;
  opacity: .08;
  filter: saturate(0.4);
  pointer-events: none;
}""", "")
patches_applied.append("PATCH 8: Remove hero plantation background")

# ── PATCH 9: Update hero subtitle text ────────────────────────────────────────
trans = trans.replace(
    "T&TG Trade Corp connects Canada, Uganda, Kenya and USA (Ohio) through premium coffee trade. Shop T&TG Arabica and Robusta green coffee. Earn T&TG Loyalty Points on every purchase.",
    "T&TG Trade Corporation based in Toronto, ON Canada connects Uganda, Kenya and USA through seamless e-commerce. Shop T&TG\'s Artisanal Coffee Based Goods, Premium Green Arabica Coffee and Robusta Green Coffee. Earn T&TG Loyalty Points on every purchase."
)
patches_applied.append("PATCH 9: Updated hero subtitle text")

# ── PATCH 10: Rename card from Coffee Shop to Artisanal Coffee Based Goods ────
home = home.replace("T&TG Coffee Shop", "T&TG Artisanal Coffee Based Goods")
patches_applied.append("PATCH 10: Rename card to Artisanal Coffee Based Goods")

# ── PATCH 11: Fix world map — Canada as HQ hub, directional routes only ───────
# Add USA (840) to highlighted countries
home = home.replace(
    "var HIGHLIGHTED = { \'124\': true, \'800\': true, \'404\': true }; // Canada, Uganda, Kenya",
    "var HIGHLIGHTED = { \'124\': true, \'800\': true, \'404\': true, \'840\': true }; // Canada, Uganda, Kenya, USA"
)
# Fix routes: Canada hub → USA → East Africa. Remove Uganda↔Kenya cross-link.
home = home.replace(
    """  var ROUTES = [
    [CITIES.toronto, CITIES.kampala],
    [CITIES.toronto, CITIES.nairobi],
    [CITIES.toronto, CITIES.ohio],
    [CITIES.ohio,    CITIES.kampala],
    [CITIES.ohio,    CITIES.nairobi],
    [CITIES.kampala, CITIES.nairobi]
  ];""",
    """  // Routes flow: Canada (HQ) → USA → East Africa
  var ROUTES = [
    { from: CITIES.toronto, to: CITIES.ohio    },  // Canada → USA
    { from: CITIES.toronto, to: CITIES.kampala },  // Canada → Uganda
    { from: CITIES.toronto, to: CITIES.nairobi },  // Canada → Kenya
    { from: CITIES.ohio,    to: CITIES.kampala },  // USA → Uganda
    { from: CITIES.ohio,    to: CITIES.nairobi },  // USA → Kenya
  ];"""
)
# Update route drawing loop to use new {from, to} object structure
home = home.replace(
    "ROUTES.forEach(function(r) {",
    "ROUTES.forEach(function(r) { var r = [r.from, r.to];"
)
patches_applied.append("PATCH 11: Canada HQ map routes (no Uganda↔Kenya cross-link)")

# ── PATCH 12: Update contact info everywhere ───────────────────────────────────
ADDRESS_OLD = "9 Summerbridge Road, Scarborough, M1G 1L8 Toronto, ON"
ADDRESS_NEW = "Toronto, ON M1G 1L8, Canada"
home = home.replace(ADDRESS_OLD, ADDRESS_NEW)

# Also update about.html and contact.html
import os, shutil

def patch_file(path, replacements):
    if not os.path.exists(path): return
    with open(path) as f: c = f.read()
    for old, new in replacements:
        c = c.replace(old, new)
    with open(path, 'w') as f: f.write(c)

contact_replacements = [
    ("9 Summerbridge Road, Scarborough, M1G 1L8 Toronto, ON", "Toronto, ON M1G 1L8, Canada"),
    ("9 Summerbridge Road, Scarborough, M1G 1L8, Toronto, ON", "Toronto, ON M1G 1L8, Canada"),
    ("416 832 3512", "+1 (416) 832 3512"),
    ("Canada, Uganda and Kenya", "Canada, Uganda, Kenya and USA (Ohio)"),
    ("Uganda, Kenya and USA", "Uganda, Kenya and USA (Ohio)"),
]
patch_file("templates/core/contact.html", contact_replacements)
patch_file("templates/core/about.html",   contact_replacements)
patch_file("templates/base.html",         contact_replacements)

patches_applied.append("PATCH 12: Updated contact info and address")

# ── PATCH 13: Loyalty rate defaults update (data migration) ───────────────────
# Write a small management command / migration to update LoyaltySettings
migration_code = '''from django.db import migrations

def update_rates(apps, schema_editor):
    LoyaltySettings = apps.get_model("core", "LoyaltySettings")
    ls = LoyaltySettings.objects.first()
    if ls:
        ls.consumer_rate = 0.005   # 0.5%
        ls.referral_rate = 0.010   # 1.0%
        ls.save(update_fields=["consumer_rate", "referral_rate"])
    else:
        LoyaltySettings.objects.create(
            consumer_rate=0.005, referral_rate=0.010, payment_days=45
        )

class Migration(migrations.Migration):
    dependencies = [("core", "0003_add_blogpost")]
    operations   = [migrations.RunPython(update_rates, migrations.RunPython.noop)]
'''
os.makedirs("core/migrations", exist_ok=True)
with open("core/migrations/0004_update_loyalty_rates.py", "w") as f:
    f.write(migration_code)
patches_applied.append("PATCH 13: Loyalty rates 0.5% consumer / 1% referral")


# ADD NEW PATCHES ABOVE THIS LINE
# ══════════════════════════════════════════════════════════════════════════════

# ── Step 3: Write patched files ────────────────────────────────────────────────
write('templates/core/home.html',  home)
write('templates/base.html',       base)
write('static/css/style.css',      css)
write('core/translations.py',      trans)

print(f"\n{len(patches_applied)} patches applied:")
for p in patches_applied:
    print(f"  ✓ {p}")

print("\nDone. Now run:")
print("  git add templates/core/home.html templates/base.html static/css/style.css core/translations.py")
print("  git commit -m 'Your message'")
print("  git push")
