import json,html,re,csv,collections,os,urllib.request,urllib.error,time
API='https://renowncargotrailers.com/wp-json/wc/store/v1/products?per_page=100&page=%d'
UA={'User-Agent':'Mozilla/5.0 RenownFeedBot'}
def get(u):
  for t in range(4):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
    except Exception as e: err=e; time.sleep(5)
  raise err
a=[];p=1
while True:
  b=get(API%p)
  if not b: break
  a+=b; p+=1
class NR(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,*k): return None
op=urllib.request.build_opener(NR)
def redirects(u):
  try: r=op.open(urllib.request.Request(u,headers=UA,method='GET'),timeout=30); return r.geturl().rstrip('/')!=u.rstrip('/')
  except urllib.error.HTTPError as e: return e.code in (301,302,303,307,308) or e.code>=400
  except Exception: return False
def txt(s): s=html.unescape(re.sub(r'<[^>]+>',' ',s or '')); return re.sub(r'\s+',' ',s).strip()
def clean(s): return s.replace('\u2014',', ').replace('\u2013','-').replace('×','x').replace('″','"').replace('′',"'")
BR=['Spartan','J&C','J & C','Diamond','Rock Solid','Quality','Covered Wagon','Look','Cynergy','Continental','Elite','Lark','Pace','Cargo Craft','Arising','Big Tex','Down 2 Earth','Anvil','Bravo','Renown','Formula','Haulmark','Interstate','Sure-Trac','Load Trail','Lamar','Top Hat','BWise','Doolittle','Hawke','Cargo Express','Charmac','American Hauler','Titanium','Deep South','MidSouth','Mid South','Lane','Panther','Southern Utility','Kingsforge','South Georgia Cargo','SDG']
def ptype(n,url,cats):
  l=(n+' '+url).lower()
  for k,v in [('groom','Grooming'),('concession','Concession'),('vending','Concession'),('dump','Dump'),('race','Race'),('toy hauler','Race'),('car hauler','Car Hauler'),('car-hauler','Car Hauler'),('equipment','Equipment'),('utility','Utility'),('open','Utility'),('motorcycle','Motorcycle'),('contractor','Contractor')]:
    if k in l: return v
  return 'Cargo'
rows=[];skip=[];seen=set()
for x in a:
  n=clean(html.unescape(x['name'])); d=txt(x['description']); url=x['permalink']
  pr=int(x['prices']['price'] or 0)
  imgs=[i['src'] for i in x['images']]; imgs=list(dict.fromkeys(imgs))
  if not pr or not imgs: skip.append((n,url,'no price' if not pr else 'no photo')); continue
  if redirects(url): skip.append((n,url,'redirects')); continue
  m=re.search(r'STOCK\s*#?:?\s*([A-Z0-9-]+)',d,re.I)
  vin=[t['name'] for at in x['attributes'] if at['name'].upper() in('VIN','STOCK') for t in at['terms']]
  pid=(m.group(1) if m else (vin[0] if vin else x['slug']))
  if pid in seen: pid=f"{pid}-{x['id']}"
  seen.add(pid)
  brand=next((b for b in BR if b.lower() in (n+' '+d[:200]).lower()),'Renown Cargo Trailers'); brand={'J & C':'J&C Cargo','J&C':'J&C Cargo','Diamond':'Diamond Cargo','Spartan':'Spartan Cargo'}.get(brand,brand)
  desc=clean(d); desc=re.sub(r'\$[\d,]+(\.\d\d)?','',desc); desc=re.sub(r'STOCK\s*#?:?\s*\S+','',desc,flags=re.I); desc=re.sub(r'\s+',' ',desc).strip()
  if len(desc)<20: desc=n+'. Available at Renown Cargo Trailers in Douglas, GA. Call 888-287-3954.'
  if len(desc)>499: desc=desc[:496].rsplit(' ',1)[0]+'...'
  rows.append(dict(id=pid,title=n[:99],description=desc,link=url,image_link=imgs[0],additional_image_link=','.join(imgs[1:5]),price=f"{pr/100:.2f} USD",availability='in stock',condition='used' if 'used' in n.lower() else 'new',brand=brand,google_product_category='Vehicles & Parts > Vehicles > Motor Vehicles > Trailers',product_type=ptype(n,url,x['categories'])))
assert len(rows)>50,'too few rows'
with open('docs/renown_pinterest_feed.csv','w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
json.dump(skip,open('docs/skipped.json','w'),indent=1)

# --- Bing Shopping title optimizer (does not affect Pinterest or WooCommerce names) ---
import re, html, collections

PROMO_RE = re.compile(r'\b(sale|special|deal|free|price|clearance|discount|cheap|cheapest|best price)\b', re.I)

MAKERS = [
    ('coast 2 coast', 'Coast 2 Coast'),
    ('coast to coast', 'Coast 2 Coast'),
    ('south georgia cargo', 'South Georgia Cargo'),
    ('southern utility', 'Southern Utility'),
    ('diamond cargo', 'Diamond Cargo'),
    ('spartan cargo', 'Spartan Cargo'),
    ('quality cargo', 'Quality Cargo'),
    ('rock solid cargo', 'Rock Solid'),
    ('rock solid', 'Rock Solid'),
    ('deep south', 'Deep South'),
    ('j & c cargo', 'J&C Cargo'),
    ('j&c cargo', 'J&C Cargo'),
    ('j & c', 'J&C Cargo'),
    ('j&c', 'J&C Cargo'),
    ('t.m. cargo', 'T.M. Cargo'),
    ('t.m cargo', 'T.M. Cargo'),
    ('panther cargo', 'Panther'),
    ('titanium', 'Titanium'),
    ('midsouth', 'MidSouth'),
    ('mid-south', 'MidSouth'),
    ('mid south', 'MidSouth'),
    ('kingsforge', 'Kingsforge'),
    ('xtreme cargo', 'Xtreme Cargo'),
    ('xtreme', 'Xtreme Cargo'),
    ('covered wagon', 'Covered Wagon'),
    ('c&a', 'C&A'),
    ('sdg', 'SDG'),
    ('alpha', 'Alpha'),
]

# Longer color phrases first. Two-tone handled separately.
COLOR_PHRASES = [
    'polar silver', 'polar gray', 'polar grey', 'charcoal gray', 'charcoal grey',
    'silver frost', 'silverfrost', 'hot pink', 'tiffany blue', 'water blue',
    'true blue', 'indigo blue', 'lucky green', 'piedmont green', 'army green',
    'grey blue', 'gray blue', 'electric blue', 'orange', 'turquoise',
    'charcoal', 'indigo', 'purple', 'yellow', 'white', 'black', 'gray', 'grey',
    'pink', 'blue', 'red', 'green', 'silver',
]

SMALL = {'and', 'or', 'of', 'with', 'a', 'an', 'the', 'for', 'in', 'on'}
KEEP_CASE = {
    'renown': 'Renown', 'a/c': 'A/C', 'bbq': 'BBQ', 'rv': 'RV', 'sdg': 'SDG',
    'v-nose': 'V-Nose', 'harley': 'Harley', 'j&c': 'J&C', 't.m.': 'T.M.',
    't.m': 'T.M.', 'c&a': 'C&A', 'gps': 'GPS', 'atp': 'ATP', 'led': 'LED',
    'midsouth': 'MidSouth',
    "j&c cargo": 'J&C Cargo',
}

def norm_space(s):
    return re.sub(r'\s+', ' ', (s or '').replace('\u2014', ', ').replace('\u2013', '-').replace('×', 'x').replace('″', '"').replace('′', "'")).strip()


def title_case(s):
    s = norm_space(s)
    out = []
    tokens = re.split(r'(\s+)', s)
    for i, tok in enumerate(tokens):
        if tok.isspace() or tok == '':
            out.append(tok)
            continue
        # split trailing punctuation
        m = re.match(r'^(.*?)([,;:]+)?$', tok)
        core, punct = m.group(1), m.group(2) or ''
        low = core.lower()
        if low in KEEP_CASE:
            out.append(KEEP_CASE[low] + punct)
            continue
        # sizes 7x14, 8.5x24, 7x16x4
        if re.fullmatch(r'\d+(?:\.\d+)?x\d+(?:\.\d+)?(?:x\d+(?:\.\d+)?)?', core, re.I):
            out.append(core.lower() + punct)
            continue
        if re.fullmatch(r'\d+(?:\.\d+)?(?:ft|in)', core, re.I):
            out.append(core.lower() + punct)
            continue
        if re.fullmatch(r'\d+k', core, re.I):
            out.append(core.upper() + punct)
            continue
        if '-' in core and not core.startswith('-'):
            bits = []
            for b in core.split('-'):
                bl = b.lower()
                if bl in KEEP_CASE:
                    bits.append(KEEP_CASE[bl])
                elif b:
                    bits.append(b[0].upper() + b[1:].lower() if len(b) > 1 else b.upper())
                else:
                    bits.append(b)
            out.append('-'.join(bits) + punct)
            continue
        if i > 0 and low in SMALL:
            out.append(core.lower() + punct)
            continue
        if core:
            cased = core[0].upper() + core[1:].lower() if len(core) > 1 else core.upper()
            out.append(cased + punct)
        else:
            out.append(tok)
    return ''.join(out).strip(' ,')

def size_from(text):
    # Prefer WxLxH dump sizes, then WxL. Allow 8.5, spaces, X or x.
    t = text.replace('×', 'x')
    m = re.search(r'\b(\d+(?:\.\d+)?)\s*[xX]\s*(\d+(?:\.\d+)?)\s*[xX]\s*(\d+(?:\.\d+)?)', t)
    if m:
        return f"{m.group(1)}x{m.group(2)}x{m.group(3)}"
    m = re.search(r'\b(\d+(?:\.\d+)?)\s*[xX]\s*(\d+(?:\.\d+)?)', t)
    if m:
        return f"{m.group(1)}x{m.group(2)}"
    return ''


def axle_from(text):
    t = text or ''
    # Size-glued codes: 6x10SA, 8.5x32TA, 8.5x36TTA5, 7X14TA
    glued = re.findall(r'\d+(?:\.\d+)?[xX]\d+(?:\.\d+)?(TTA\d*|TA\d*|SA)\b', t)
    # Triple first
    if re.search(r'\bTTA\d*\b|\btriple\s+axle|\btriple\s+\d', t, re.I) or any(g.upper().startswith('TTA') for g in glued):
        return 'Triple Axle'
    if re.search(r'\bsingle\s+axle\b|\bSA\b', t, re.I) or any(g.upper() == 'SA' for g in glued):
        return 'Single Axle'
    # TA3/TA4 are tandem with a weight rating, not triple/quad
    if re.search(r'\btandem\b|\bTA\d*\b', t, re.I) or any(g.upper().startswith('TA') for g in glued):
        return 'Tandem Axle'
    if re.search(r'\bspread\s+axles\b|\bdrop\s+axles\b|\b\d[\d,]*\s*lb\s+(?:drop\s+)?axles\b', t, re.I):
        return 'Tandem Axle'
    return ''

def _is_blackout(text, start, end):
    after = text[end:end+8]
    return bool(re.match(r'\s*out\b', after, re.I))

def color_from(title, desc):
    blob = f"{title} {desc}"
    stop = {'this','the','a','an','with','and','or','two','tone','features','upgrades','include','including','new','our','in','of','exterior','polycore'}

    def clean_color_name(s):
        words = [w for w in re.split(r'\s+', s.strip()) if w and w.lower() not in stop and w.lower() not in ('exterior','polycore','siding','package','trim')]
        return title_case(' '.join(words)) if words else ''

    # Two-tone patterns
    tt = re.search(
        r'two[\s-]?tone\s+([A-Za-z][A-Za-z ]{0,20}?)\s*(?:/|&|and)\s*([A-Za-z][A-Za-z ]{0,16})',
        blob, re.I)
    if tt:
        a, b = clean_color_name(tt.group(1)), clean_color_name(tt.group(2))
        if a and b:
            return f"{a} and {b}"
    tt2 = re.search(
        r'([A-Za-z][A-Za-z ]{0,16}?)\s*(?:/|&|and)\s*([A-Za-z][A-Za-z ]{0,16}?)\s+two[\s-]?tone',
        blob, re.I)
    if tt2:
        a, b = clean_color_name(tt2.group(1)), clean_color_name(tt2.group(2))
        if a and b:
            return f"{a} and {b}"

    # Strong body-color patterns: "{color} exterior/polycore/.080/siding"
    strong = re.compile(
        r'\b(' + '|'.join(re.escape(c) for c in COLOR_PHRASES) + r')\b'
        r'(?:\s+\.080)?(?:\s+polycore)?(?:\s+(?:exterior|siding|finish)\b)',
        re.I)
    for m in strong.finditer(blob):
        c = m.group(1)
        if _is_blackout(blob, m.start(), m.start()+len(c)):
            continue
        return title_case(c)

    # "{color} .080" without the word exterior yet
    mid = re.compile(
        r'\b(' + '|'.join(re.escape(c) for c in COLOR_PHRASES) + r')\b\s+\.080\b',
        re.I)
    for m in mid.finditer(blob):
        c = m.group(1)
        if _is_blackout(blob, m.start(), m.start()+len(c)):
            continue
        return title_case(c)


    # Mask "available colors:" option lists so we don't pick a catalog color
    blob_masked = re.sub(r'available colors?:\s*[^.]*', ' ', blob, flags=re.I)

    # "{color} blackout" (body color followed by the blackout package)
    bo = re.compile(
        r'\b(' + '|'.join(re.escape(c) for c in COLOR_PHRASES) + r')\b\s+black\s*out\b',
        re.I)
    for m in bo.finditer(blob_masked):
        return title_case(m.group(1))

    # "{color} poly/aluminum exterior"
    poly = re.compile(
        r'\b(' + '|'.join(re.escape(c) for c in COLOR_PHRASES) + r')\b'
        r'\s+(?:poly|aluminum|aluminium)\s+(?:exterior|skin|siding)\b',
        re.I)
    for m in poly.finditer(blob_masked):
        return title_case(m.group(1))

    # Two-tone "White Front / Silver Frost Rear" or "Charcoal Gray (Front) / Black (Rear)"
    fr = re.search(
        r'\b(' + '|'.join(re.escape(c) for c in COLOR_PHRASES) + r')\b'
        r'\s*(?:\((?:front|rear)\)|(?:front|rear))?\s*/\s*'
        r'\b(' + '|'.join(re.escape(c) for c in COLOR_PHRASES) + r')\b',
        blob_masked, re.I)
    if fr:
        return f"{title_case(fr.group(1))} and {title_case(fr.group(2))}"

    # Hyphenated body color: Blue-Purple (.080) Polycore
    hy = re.search(
        r'\b(' + '|'.join(re.escape(c) for c in COLOR_PHRASES) + r')-(' +
        '|'.join(re.escape(c) for c in COLOR_PHRASES) + r')\b(?:\s*\(\.080\))?(?:\s+polycore)?',
        blob_masked, re.I)
    if hy:
        return f"{title_case(hy.group(1))} and {title_case(hy.group(2))}"

    # "{color} & {color} ... exterior siding"
    amp = re.search(
        r'\b(' + '|'.join(re.escape(c) for c in COLOR_PHRASES) + r')\s*(?:&|and)\s*(' +
        '|'.join(re.escape(c) for c in COLOR_PHRASES) + r')\b(?:\s+\w+){0,3}\s+(?:exterior|siding)\b',
        blob_masked, re.I)
    if amp:
        return f"{title_case(amp.group(1))} and {title_case(amp.group(2))}"

    # "{color} features/specifications" near the header
    head = re.compile(
        r'\b(' + '|'.join(re.escape(c) for c in COLOR_PHRASES) + r')\b\s+(?:features|specifications|upgrades)\b',
        re.I)
    for m in head.finditer(blob_masked[:280]):
        if _is_blackout(blob_masked, m.start(), m.start()+len(m.group(1))):
            continue
        return title_case(m.group(1))

    # standalone "{color} gray/grey" already in phrases; "Charcoal Gray Standard Features"
    std = re.compile(
        r'\b(' + '|'.join(re.escape(c) for c in COLOR_PHRASES) + r')\b\s+standard features\b',
        re.I)
    for m in std.finditer(blob_masked):
        return title_case(m.group(1))


    # Color in the product title (not blackout, not manufacturer context-only)
    title_only = title
    # strip blackout so "WHITE BLACKOUT" still yields White
    title_nb = re.sub(r'\bblack\s*outs?\b', ' ', title_only, flags=re.I)
    # title after pipe
    m = re.search(r'\|\s*([A-Za-z][A-Za-z ]{1,24})$', title_nb.strip())
    if m:
        cand = clean_color_name(m.group(1))
        if cand and any(re.search(rf'\b{re.escape(c)}\b', cand, re.I) for c in COLOR_PHRASES + ['chameleon']):
            return cand
    for c in COLOR_PHRASES + ['chameleon']:
        m = re.search(rf'\b{re.escape(c)}\b', title_nb, re.I)
        if not m:
            continue
        if _is_blackout(title_nb, m.start(), m.end()):
            continue
        return title_case(c)

    # "in Black" / "in White" in the title
    m = re.search(r'\bin\s+(' + '|'.join(re.escape(c) for c in COLOR_PHRASES) + r')\b', title, re.I)
    if m:
        return title_case(m.group(1))
    return ''

def maker_from(text, brand):
    t = (text or '').lower()
    for pat, name in MAKERS:
        if pat in t:
            return name
    b = (brand or '').strip()
    if b and b.lower() not in ('renown', 'renown cargo trailers'):
        # normalize a few
        return {'Quality': 'Quality Cargo', 'Panther': 'Panther', 'Rock Solid': 'Rock Solid'}.get(b, b)
    return ''

def product_kind(title, desc, ptype, url=''):
    blob = f"{title} {desc} {url} {ptype}".lower()
    # most specific first; never call dump/utility "cargo"
    if re.search(r'groom', blob):
        return 'Dog Grooming Trailer'
    if re.search(r'\bbbq\b', blob):
        return 'BBQ Concession Trailer'
    if re.search(r'concession|food trailer|food truck|\bvending\b|mobile kitchen', blob):
        return 'Concession Trailer'
    if re.search(r'\bdump\b', blob):
        return 'Dump Trailer'
    if re.search(r'fiber\s+splic', blob):
        return 'Fiber Splicing Trailer'
    if re.search(r'mobile command|command\s+&\s+response|command response', blob):
        return 'Mobile Command Trailer'
    if re.search(r'motorcycle\s+trailer|\bharley\b', blob) or (ptype or '').lower()=='motorcycle':
        return 'Enclosed Motorcycle Trailer'
    if re.search(r'contractor\s+trailer', blob) or (ptype or '').lower()=='contractor':
        return 'Enclosed Contractor Trailer'
    if re.search(r'toy hauler', blob):
        return 'Enclosed Toy Hauler'
    if re.search(r'\brace\b|motorsports|race car hauler', blob):
        return 'Race Car Trailer'
    if re.search(r'car hauler|car-hauler', blob) or (ptype or '').lower() == 'car hauler':
        return 'Enclosed Car Hauler'
    if re.search(r'deckover', blob):
        return 'Deckover Equipment Trailer'
    if re.search(r'equipment trailer', blob) or (ptype or '').lower() == 'equipment' and 'food' not in blob:
        return 'Equipment Trailer'
    if (ptype or '').lower() == 'utility' or (re.search(r'\butility\b', blob) and not re.search(r'enclosed|cargo|car hauler|groom|dump|concession', blob)):
        # "Southern Utility" brand on equipment should already have been caught
        if re.search(r'equipment', blob):
            return 'Equipment Trailer'
        if re.search(r'\btube\b', blob):
            return 'Tube Utility Trailer'
        return 'Utility Trailer'
    # generic enclosed / cargo
    return 'Enclosed Cargo Trailer'

def interior_height(text):
    # 7'6", 7’6”, 7ft 6in, 7' 6"
    m = re.search(r"\b(6|7|8)\s*['’]\s*(\d{1,2})\s*[\"”]?", text)
    if m:
        ft, inch = m.group(1), m.group(2)
        return f"{ft}ft {inch}in Interior"
    m = re.search(r'\b(6|7|8)\s*(?:ft|foot)\s+(\d{1,2})\s*(?:in|inch)', text, re.I)
    if m:
        return f"{m.group(1)}ft {m.group(2)}in Interior"
    m = re.search(r"\b(6|7|8)\s*['’]\s*interior", text, re.I)
    if m:
        return f"{m.group(1)}ft Interior"
    m = re.search(r'\b(6|7|8)\s*(?:ft|foot|\s)\s*interior', text, re.I)
    if m:
        return f"{m.group(1)}ft Interior"
    m = re.search(r'\b(7|6|8)\s*ft\s*(?:interior|height)', text, re.I)
    if m:
        return f"{m.group(1)}ft Interior"
    # 75" interior height ~ 6'3" — skip odd inch-only unless clearly 78"/75" as 7ft-ish? Don't invent 7ft from 75".
    return ''

def dump_sides(text):
    m = re.search(r"\b(\d+)\s*(?:'|\s*ft)\s*(?:sides|walls|steel walls)\b", text, re.I)
    if m:
        return f"{m.group(1)}ft Sides"
    m = re.search(r'\b(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)', text, re.I)
    if m:
        return f"{m.group(3).replace('.0','')}ft Sides"
    return ''

def gvwr_k(text):
    m = re.search(r'\b(\d{1,2})\s*k\b', text, re.I)
    if m:
        n = int(m.group(1))
        if 10 <= n <= 40:
            return f"{n}K"
    m = re.search(r'\b(\d{2})\s*,?\s*000\s*(?:lb|pound)?', text, re.I)
    if m:
        n = int(m.group(1))
        if 10 <= n <= 40:
            return f"{n}K"
    return ''

def has(pat, text):
    return bool(re.search(pat, text, re.I))

def features_for(kind, title, desc):
    blob = f"{title} {desc}"
    feats = []
    def add(label, pat):
        if pat is True or (isinstance(pat, str) and has(pat, blob)):
            if label not in feats:
                feats.append(label)

    if kind == 'Dump Trailer':
        sides = dump_sides(blob)
        if sides:
            feats.append(sides)
        g = gvwr_k(blob)
        if g:
            feats.append(g)
        add('Telescopic', r'telescopic')
    if kind == 'Utility Trailer':
        add('Expanded Metal Gate', r'expanded metal')
    if kind in ('Concession Trailer', 'BBQ Concession Trailer'):
        if has(r'sink', blob) and has(r"a/?c\b|air conditioner|mini[\s-]?split", blob):
            feats.append('Sinks & A/C')
        else:
            add('Sinks', r'\bsinks?\b')
            add('A/C', r"\ba/?c\b|air conditioner")
            add('Mini Split', r'mini[\s-]?split')
        add('Blackout', r'black\s*out')
    if kind == 'Dog Grooming Trailer':
        add('Battery Powered', r'battery\s*(powered|operated|power|case)|joule')
        add('Awning', r'\bawning\b')
        h = interior_height(blob)
        if h:
            feats.append(h)
        add('Blackout', r'black\s*out')
        if has(r'legacy', blob):
            feats.append('Legacy Series')
        elif has(r'genesis', blob):
            feats.append('Genesis Series')
    if kind == 'Enclosed Motorcycle Trailer':
        add('Harley Edition', r'harley')
        add('Blackout', r'black\s*out')
    if kind == 'Fiber Splicing Trailer':
        add('Generator', r'generator')
    if kind == 'Equipment Trailer' or kind == 'Deckover Equipment Trailer':
        g = gvwr_k(blob)
        if g:
            feats.append(g)
        add('Heavy Duty', r'heavy[\s-]?duty')
    if kind in ('Enclosed Car Hauler', 'Race Car Trailer', 'Enclosed Toy Hauler'):
        add('Gull Wing', r'gull[\s-]?wing')
        add('Awning', r'\bawning\b')
        add('Winch', r'\bwinch\b')
        h = interior_height(blob)
        if h:
            feats.append(h)
        add('Escape Door', r'escape door')
        add('Blackout', r'black\s*out')
        add('V-Nose', r'v[\s-]?nose')
        add('Ramp Door', r'ramp door|rear ramp')
    if kind in ('Enclosed Cargo Trailer', 'Enclosed Contractor Trailer'):
        add('V-Nose', r'v[\s-]?nose')
        add('Ramp Door', r'ramp door|rear ramp')
        h = interior_height(blob)
        if h:
            feats.append(h)
        add('Blackout', r'black\s*out')
        add('Spoiler', r'\bspoiler\b')
    if kind == 'Mobile Command Trailer':
        add('Aluminum', r'\baluminum\b')
    # used / scratch and dent
    if has(r'\bused\b', title) or has(r'\bused\b', blob[:80]):
        # handled as a modifier before type, not a feature
        pass
    if has(r'scratch\s*&\s*dent|scratch and dent', blob):
        feats.append('Scratch and Dent')
    # generic blackout if not added
    if kind not in ('Concession Trailer', 'BBQ Concession Trailer', 'Dog Grooming Trailer',
                    'Enclosed Car Hauler', 'Race Car Trailer', 'Enclosed Toy Hauler',
                    'Enclosed Cargo Trailer', 'Enclosed Contractor Trailer', 'Enclosed Motorcycle Trailer'):
        add('Blackout', r'black\s*out')
    return feats

def is_used(title, desc, condition):
    if (condition or '').lower() == 'used':
        return True
    return bool(re.search(r'\bused\b', title, re.I))

def strip_promo(s):
    # remove promo words but keep surrounding structure
    s = PROMO_RE.sub('', s)
    s = re.sub(r'\s{2,}', ' ', s)
    s = re.sub(r'\s+,', ',', s)
    return s.strip(' -,')

def assemble(size, axle, used, kind, feats, color, maker, max_len=150, force_extra=None):
    # Build with progressive dropping: features, then maker, never drop Renown, size, kind.
    feats = list(feats)
    if force_extra:
        for x in force_extra:
            if x and x not in feats:
                feats.append(x)

    def build(use_feats, use_maker, use_color):
        parts = []
        head = ' '.join(p for p in [size, axle, 'Used' if used else '', kind] if p)
        # features after type
        if use_feats:
            head = head + ', ' + ', '.join(use_feats)
        tail_bits = []
        if use_color:
            tail_bits.append(use_color)
        tail_bits.append('Renown')
        if use_maker and maker:
            tail_bits.append(maker)
        s = head
        if tail_bits:
            s = s + ' - ' + ' - '.join(tail_bits)
        s = title_case(strip_promo(s))
        # title_case may downcase "Used" mid-string — it's after size/axle so first words stay capped.
        return s

    # drop from the end of features first, then color stays, then maker
    for nfeats in range(len(feats), -1, -1):
        for use_maker in (True, False) if maker else (False,):
            # Prefer including maker only if it fits; try with maker first when nfeats is full, but
            # actually: prefer features+color+Renown, add maker if room. When uniqueness needs maker, caller passes it as force.
            s = build(feats[:nfeats], use_maker, color)
            if len(s) <= max_len and s:
                return s
    # last ditch: size axle kind - Renown
    s = build([], False, color)
    if len(s) <= max_len:
        return s
    s = build([], False, '')
    return s[:max_len].rstrip(' -,')

def bing_title_parts(row):
    title = row.get('title') or ''
    desc = row.get('description') or ''
    blob = f"{title} {desc}"
    size = size_from(blob) or size_from(title)
    axle = axle_from(blob)
    kind = product_kind(title, desc, row.get('product_type') or '', row.get('link') or '')
    color = color_from(title, desc)
    maker = maker_from(blob, row.get('brand') or '')
    feats = features_for(kind, title, desc)
    used = is_used(title, desc, row.get('condition') or '')
    # dump size: prefer WxL plus sides feature (avoid 7x14x2 as the only size if we have sides)
    if kind == 'Dump Trailer' and size.count('x') == 2:
        a,b,_ = size.split('x')
        size = f"{a}x{b}"
    return dict(size=size, axle=axle, used=used, kind=kind, feats=feats, color=color, maker=maker, raw_title=title, id=row.get('id') or '')

def make_title(parts, extra=None):
    return assemble(parts['size'], parts['axle'], parts['used'], parts['kind'],
                    parts['feats'], parts['color'], parts['maker'], 150, force_extra=extra)

def clean_desc_rest(desc, old_title=''):
    d = norm_space(desc)
    # strip sale / was now / sale price lead-ins
    d = re.sub(r'\bSALE PRICE\b[:.]?', ' ', d, flags=re.I)
    d = re.sub(r'\bWas:\s*Now:\b', ' ', d, flags=re.I)
    d = re.sub(r'\bWAS\s+NOW\b', ' ', d, flags=re.I)
    d = re.sub(r'\b(on sale|clearance)\b', ' ', d, flags=re.I)
    d = norm_space(d)
    return d

def bing_description(new_title, old_desc, old_title=''):
    rest = clean_desc_rest(old_desc, old_title)
    lead = new_title if new_title.endswith('.') else new_title + '.'
    # avoid exact duplicate if rest already starts with the new title
    if rest.lower().startswith(new_title.lower()):
        text = rest
        if not text.endswith('.'):
            pass
        return text[:5000]
    text = f"{lead} {rest}".strip()
    if len(text) > 5000:
        text = text[:4997].rsplit(' ', 1)[0] + '...'
    return text


def _norm_gray(s):
    if not s:
        return s
    return re.sub(r'\bGrey\b', 'Gray', s)

def optimize_rows(rows):
    parts_list = [bing_title_parts(r) for r in rows]
    for p in parts_list:
        p['color'] = _norm_gray(p['color'])
    titles = [make_title(p) for p in parts_list]

    def collisions(ts):
        c = collections.Counter(t.lower() for t in ts)
        return {k for k,v in c.items() if v > 1}

    dups = collisions(titles)
    for i, p in enumerate(parts_list):
        if titles[i].lower() not in dups:
            continue
        pid = p['id'] or f'U{i+1}'
        # keep stock ids compact; don't append huge slugs in full
        tag = pid if len(pid) <= 22 else pid[:22]
        base = titles[i]
        cand = f"{base} ({tag})"
        if len(cand) > 150:
            # drop maker then features until it fits
            for nfeats in range(len(p['feats']), -1, -1):
                shorter = assemble(p['size'], p['axle'], p['used'], p['kind'], p['feats'][:nfeats], p['color'], '', 150 - len(tag) - 3)
                cand = f"{shorter} ({tag})"
                if len(cand) <= 150:
                    break
            if len(cand) > 150:
                cand = base[:150-len(tag)-3].rstrip(' -,') + ' (' + tag + ')'
        titles[i] = cand
    # if any still collide (identical id shouldn't happen), last-index suffix
    dups = collisions(titles)
    if dups:
        seen = collections.defaultdict(int)
        for i, t in enumerate(titles):
            if t.lower() in dups:
                seen[t.lower()] += 1
                if seen[t.lower()] > 1:
                    tag = (p if False else parts_list[i]['id']) or str(i+1)
                    cand = f"{t} ({tag})"
                    titles[i] = cand if len(cand) <= 150 else t[:150-len(tag)-3].rstrip(' -,') + ' (' + tag + ')'
    return titles, parts_list


# Microsoft Merchant Center (Bing Shopping) feed. Pinterest CSV above is unchanged.
# Spec: tab-delimited TXT, UTF-8, header row. Required: id, title, link, price, description, image_link.
# google_product_category 4044 = Vehicles & Parts > Vehicle Parts & Accessories > Vehicle Storage & Cargo > Motor Vehicle Trailers > Utility & Cargo Trailers
# (https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt). Trailers have no GTIN.
BING_COLS = ['id','title','link','price','description','image_link','additional_image_link','availability','condition','brand','identifier_exists','product_type','google_product_category','seller_name']
OKIMG = re.compile(r'\.(jpe?g|png|gif|bmp|tiff?)(\?|$)', re.I)
def bing_cell(s):
  return re.sub(r'[\t\r\n]+', ' ', str(s or '')).strip()
bing_rows=[]; bing_skip=[]
for r in rows:
  imgs = [r['image_link']] + [u for u in (r.get('additional_image_link') or '').split(',') if u]
  good = [u for u in imgs if OKIMG.search(u)]
  if not good:
    bing_skip.append((r['id'], r['title'], r['link'], 'no valid image (Microsoft requires jpg/png/gif/bmp/tiff)'))
    continue
  price_val = r['price'].split()[0] if r.get('price') else '0'
  try:
    if float(price_val) <= 0:
      bing_skip.append((r['id'], r['title'], r['link'], 'no price'))
      continue
  except ValueError:
    bing_skip.append((r['id'], r['title'], r['link'], 'invalid price'))
    continue
  bing_rows.append({
    'id': r['id'],
    'title': r['title'],
    'link': r['link'],
    'price': r['price'],
    'description': r['description'],
    'image_link': good[0],
    'additional_image_link': ','.join(good[1:10]),
    'availability': r['availability'],
    'condition': r['condition'],
    'brand': r['brand'],
    'identifier_exists': 'FALSE',
    'product_type': r['product_type'],
    'google_product_category': '4044',
    'seller_name': 'Renown Cargo Trailers',
  })
# Rewrite Bing titles/descriptions only. WooCommerce names and the Pinterest CSV are unchanged.
# TA3/TA4 are tandem axle weight ratings, not triple/quad; TTA/TTA5 are triple axle.
_btitles, _ = optimize_rows(bing_rows)
for _row, _title in zip(bing_rows, _btitles):
    _src_title = _row['title']
    _src_desc = _row['description']
    _row['title'] = _title
    _row['description'] = bing_description(_title, _src_desc, _src_title)

assert len(bing_rows)>50,'too few bing rows'
with open('docs/renown_bing_feed.txt'
,'w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f, fieldnames=BING_COLS, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, escapechar='\\')
  w.writeheader()
  for r in bing_rows:
    w.writerow({k: bing_cell(r.get(k,'')) for k in BING_COLS})
json.dump(bing_skip, open('docs/bing_skipped.json','w'), indent=1)
print('bing', len(bing_rows), 'skipped', len(bing_skip)); [print(s) for s in bing_skip]
print(len(rows),collections.Counter(r['product_type'] for r in rows),collections.Counter(r['brand'] for r in rows));print(len(skip));[print(s) for s in skip]
print(sum('\u2014' in r['description']+r['title'] for r in rows))
