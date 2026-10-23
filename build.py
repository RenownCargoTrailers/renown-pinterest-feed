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
print(len(rows),collections.Counter(r['product_type'] for r in rows),collections.Counter(r['brand'] for r in rows));print(len(skip));[print(s) for s in skip]
print(sum('\u2014' in r['description']+r['title'] for r in rows))
