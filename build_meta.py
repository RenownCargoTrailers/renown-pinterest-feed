# Builds docs/renown_meta_vehicle_feed.csv for a Meta Commerce Manager Vehicles (automotive inventory) catalog.
# Spec: https://developers.facebook.com/docs/marketing-api/auto-ads/reference/
import urllib.parse,json,html,re,csv,collections,urllib.request,urllib.error,time,datetime
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36'}
def get(u,tries=4):
  for t in range(tries):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60))
    except Exception as e: err=e; time.sleep(3)
  raise err
def allp(site):
  a=[];p=1
  while True:
    b=get(f'https://{site}/wp-json/wc/store/v1/products?per_page=100&page={p}')
    if not b: break
    a+=b;p+=1
  return a
def side(site):
  try: return allp(site)
  except Exception as e: print('WARN',site,e); return []
RN=allp('renowncargotrailers.com'); CS=side('concessiontrailer.com'); MG=side('mobilegroomingtrailers.com')
def txt(s): s=html.unescape(re.sub(r'<[^>]+>',' ',s or '')); return re.sub(r'\s+',' ',s).strip()
def clean(s): return re.sub(r'\s+',' ',s.replace('\u2014',', ').replace('\u2013','-').replace('\u00d7','x').replace('\u2033','"').replace('\u2032',"'").replace('\u2019',"'").replace('\u201c','"').replace('\u201d','"')).strip()
BR=['Spartan','J&C','J & C','Diamond','Rock Solid','Quality','Covered Wagon','Look','Cynergy','Continental','Elite','Lark','Pace','Cargo Craft','Arising','Big Tex','Down 2 Earth','Anvil','Bravo','Formula','Haulmark','Interstate','Sure-Trac','Load Trail','Lamar','Top Hat','BWise','Doolittle','Hawke','Cargo Express','Charmac','American Hauler','Titanium','Deep South','MidSouth','Mid South','Lane','Panther','Southern Utility','Kingsforge','South Georgia Cargo','SDG','Alpha','Renown']
MK={'J & C':'J&C Cargo','J&C':'J&C Cargo','Diamond':'Diamond Cargo','Spartan':'Spartan Cargo','Rock Solid':'Rock Solid Cargo','Quality':'Quality Cargo','Panther':'Panther Cargo','Mid South':'MidSouth','Renown':'Renown Cargo Trailers','Alpha':'Alpha Cargo'}
def ptype(l):
  for k,v in [('groom','Pet Grooming Trailer'),('concession','Concession Trailer'),('food','Concession Trailer'),('bbq','Concession Trailer'),('vending','Concession Trailer'),('coffee','Concession Trailer'),('dump','Dump Trailer'),('race','Race Car Trailer'),('toy hauler','Toy Hauler'),('car hauler','Car Hauler'),('car-hauler','Car Hauler'),('motorcycle','Motorcycle Trailer'),('equipment','Equipment Trailer'),('deckover','Equipment Trailer'),('utility','Utility Trailer'),('open','Utility Trailer')]:
    if k in l: return v
  return 'Enclosed Cargo Trailer'
COL=['hot pink','pink','purple','red','black','white','blue','green','yellow','orange','silver','gray','grey','charcoal','turquoise','aqua','teal','tan','gold','brown','indigo']
def color(t):
  t=t.lower(); c=[]
  for x in COL:
    if re.search(r'\b'+x+r'\b',t):
      x={'grey':'Gray','hot pink':'Pink','charcoal':'Gray','indigo':'Blue','aqua':'Turquoise','teal':'Turquoise'}.get(x,x.title())
      if x not in c: c.append(x)
  return c[0] if len(c)==1 else ('Multicolor' if c else 'Other')
def colr(n,d):
  c=color(n)
  if c not in ('Other','Multicolor'): return c
  m=re.search(r'([A-Za-z]+(?: [A-Za-z]+)?) (?:poly |metal |aluminum )?(?:exterior|finish)',d,re.I)
  if m and color(m.group(1)) not in ('Other','Multicolor'): return color(m.group(1))
  cnt=collections.Counter()
  for x in COL:
    k=len(re.findall(r'\b'+x+r'\b',d[:800],re.I))
    if k: cnt[color(x)]+=k
  return cnt.most_common(1)[0][0] if cnt else c
def stockno(d):
  m=re.search(r'STOCK\s*#?:?\s*([A-Z]{0,4}-?[0-9][0-9A-Z-]*)',d,re.I); return m.group(1).upper() if m else ''
def num(s): m=re.search(r'(\d{4,6})',s or ''); return m.group(1) if m else ''
class NR(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,*k): return None
op=urllib.request.build_opener(NR)
def redirects(u):
  try: r=op.open(urllib.request.Request(u,headers=UA),timeout=30); return r.geturl().rstrip('/')!=u.rstrip('/')
  except urllib.error.HTTPError as e: return e.code in (301,302,303,307,308,404,410)
  except Exception: return False
OKIMG=re.compile(r'\.(jpe?g|png)(\?|$)',re.I)
CTA='Rent to own available, no credit check. Call 888-287-3954 or text 912-325-3578.'
YEAR_DEFAULT=2027  # Laura: current stock is model year 2027
def year(s):
  m=re.search(r'\b(20(2[4-9]))\b\s*(model|my)?',s,re.I); return int(m.group(1)) if m and m.group(3) else YEAR_DEFAULT
def desc_of(name,d):
  d=clean(d); d=re.sub(r'(was|reg(ular)?|msrp|now|only|sale)?:?\s*\$[\d,]+(\.\d\d)?','',d,flags=re.I)
  d=re.sub(r'STOCK\s*#?:?\s*\S+','',d,flags=re.I); d=re.sub(r'[^.]*\b(paid for|sitting on (the|our) lot)\b[^.]*\.?','',d,flags=re.I)
  d=re.sub(r'https?://\S+|www\.\S+','',d); d=re.sub(r'\s+',' ',d).strip()
  if len(d)<20: d=name+'. In stock at Renown Cargo Trailers in Douglas, GA.'
  if len(d)>1500: d=d[:1500].rsplit(' ',1)[0]+'...'
  if d.isupper(): d=d.capitalize()
  return d+' '+CTA
def items(src,site):
  for x in src:
    if not x.get('is_in_stock',True): continue
    yield site,x
# side-site lookup by stock number
side_by={}
for site,lst in (('concessiontrailer.com',CS),('mobilegroomingtrailers.com',MG)):
  for x in lst:
    if not x.get('is_in_stock',True): continue
    d=txt(x['short_description']+' '+x['description'])
    for k in {stockno(d),num(stockno(d)),num(x.get('sku',''))}-{''}: side_by.setdefault(k,(site,x))
rows=[];skip=[];seen=set();used_side=set()
def add(site,x,url_override=None):
  n=clean(html.unescape(x['name'])); d=txt(x['short_description']+' '+x['description']); url=url_override or x['permalink']
  pr=int(x['prices']['price'] or 0)
  imgs=[i['src'] for i in x['images']]; imgs=list(dict.fromkeys(imgs)); good=[i for i in imgs if OKIMG.search(i)]
  if not pr: skip.append((n,url,'no price'));return
  if not good: skip.append((n,url,'no jpg/png photo' if imgs else 'no photo'));return
  if site=='renowncargotrailers.com' and redirects(x['permalink']): skip.append((n,url,'listing redirects/404'));return
  sn=stockno(d); vid=sn or x.get('sku') or x['slug']
  if vid in seen: vid=f"{vid}-{x['id']}"
  seen.add(vid)
  b=next((b for b in BR if b.lower() in (n+' '+d[:300]).lower()),'Renown')
  mk=MK.get(b,b); l=(n+' '+url).lower(); pt=ptype(l)
  m=re.search(r'(\d+(?:\.\d+)?)\s*[xX]\s*(\d+)(?:\s*[xX]\s*(\d+))?',n); sz=(m.group(0).replace(' ','').replace('X','x')) if m else ''
  ax=' TTA' if re.search(r'\bTTA\b|triple axle',n,re.I) else ' TA' if re.search(r'\bTA\d*\b|tandem',n,re.I) else ' SA' if re.search(r'\bSA\b|single axle',n,re.I) else ''
  model=(sz+ax+' '+pt).strip(); yr=year(n+' '+d)
  title=clean(f'{yr} {mk} {model}' + (f' ({sn})' if sn else ''))[:200]
  r={'vehicle_id':vid,'title':title,'description':desc_of(n,d),'url':url,'make':mk,'model':model,'year':yr,
     'mileage.value':0,'mileage.unit':'MI','price':f'{pr//100} USD','exterior_color':colr(n,d),
     'state_of_vehicle':'Used' if re.search(r'\bused\b|pre-owned',n,re.I) else 'New','availability':'available',
     'vehicle_type':'trailer','body_style':'OTHER','dealer_name':'Renown Cargo Trailers','dealer_phone':'+18882873954',
     'address.addr1':'1135 Bowens Mill Rd SW','address.city':'Douglas','address.region':'GA','address.postal_code':'31533','address.country':'US',
     'latitude':'31.489435','longitude':'-82.867398','stock_number':sn,'custom_label_0':pt}
  for i,u in enumerate(good[:20]): r[f'image[{i}].url']=u
  rows.append(r)
for site,x in items(RN,'renowncargotrailers.com'):
  n=html.unescape(x['name']).lower(); d=txt(x['description']); ov=None
  if re.search(r'groom|concession|food|bbq|vending|coffee',n+' '+x['permalink']):
    for k in (stockno(d),num(stockno(d)),num(x.get('sku',''))):
      if k and k in side_by: s,y=side_by[k]; ov=y['permalink']; used_side.add(y['id']); break
  add(site,x,ov)
# side-site units not listed on renowncargotrailers.com
for lst,site in ((CS,'concessiontrailer.com'),(MG,'mobilegroomingtrailers.com')):
  for x in lst:
    if x.get('is_in_stock',True) and x['id'] not in used_side and x['permalink'] not in {r['url'] for r in rows}: add(site,x)
assert len(rows)>50,'too few rows'
mi=max(int(k[6:-5]) for r in rows for k in r if k.startswith('image['))
cols=['vehicle_id','title','description','url','make','model','year','mileage.value','mileage.unit','price','exterior_color','state_of_vehicle','availability','vehicle_type','body_style']+[f'image[{i}].url' for i in range(mi+1)]+['dealer_name','dealer_phone','address.addr1','address.city','address.region','address.postal_code','address.country','latitude','longitude','stock_number','custom_label_0']
with open('docs/renown_meta_vehicle_feed.csv','w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=cols,restval='');w.writeheader();w.writerows(rows)
json.dump(skip,open('docs/meta_skipped.json','w'),indent=1)
print(len(rows),collections.Counter(r['custom_label_0'] for r in rows),collections.Counter(urllib.parse.urlparse(r['url']).netloc for r in rows));print('skipped',len(skip));[print(s) for s in skip]
