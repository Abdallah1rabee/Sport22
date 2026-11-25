#!/usr/bin/env python3
"""يسحب الأخبار المنشورة من لوحة الرفع (Firestore) ويكتبها في live_articles.json + صورها في images/live/
بعدها build_seo.py يعمل لكل خبر صفحة ثابتة news/<id>/ قابلة للفهرسة."""
import json, os, re, base64, time, urllib.request, urllib.error
PROJ = 'sport22-66fc3'
KEY = re.search(r'apiKey:\s*"([^"]+)"', open('firebase-config.js', encoding='utf-8').read()).group(1)
API = f'https://firestore.googleapis.com/v1/projects/{PROJ}/databases/(default)/documents'
def get(url):
    for i in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r: return json.load(r)
        except urllib.error.HTTPError as ex:
            if ex.code == 404: return None
            time.sleep(2)
        except Exception: time.sleep(2)
    raise SystemExit('تعذر الوصول إلى Firestore: ' + url.split('?')[0])
def val(v):
    if 'stringValue' in v: return v['stringValue']
    if 'integerValue' in v: return int(v['integerValue'])
    if 'doubleValue' in v: return v['doubleValue']
    if 'booleanValue' in v: return v['booleanValue']
    if 'arrayValue' in v: return [val(x) for x in v['arrayValue'].get('values', [])]
    if 'mapValue' in v: return {k: val(x) for k, x in v['mapValue'].get('fields', {}).items()}
    return None
def fields(doc): return {k: val(v) for k, v in doc.get('fields', {}).items()}
docs, tok = [], ''
while True:
    r = get(f'{API}/live_articles?pageSize=300&key={KEY}' + (f'&pageToken={tok}' if tok else ''))
    docs += (r or {}).get('documents', [])
    tok = (r or {}).get('nextPageToken')
    if not tok: break
old = {}
if os.path.exists('live_articles.json'):
    for a in json.load(open('live_articles.json', encoding='utf-8')): old[a['id']] = a
os.makedirs('images/live', exist_ok=True)
def save_img(name, data):
    m = re.match(r'data:image/(\w+);base64,(.+)$', data or '', re.S)
    if not m: return None
    ext = 'jpg' if m.group(1) in ('jpeg', 'jpg') else m.group(1)
    p = f'images/live/{name}.{ext}'
    open(p, 'wb').write(base64.b64decode(m.group(2)))
    return p
def fetch_img(name):
    r = get(f'{API}/live_imgs/{name}?key={KEY}')
    return save_img(name, fields(r).get('d')) if r else None
now = time.time() * 1000
out = []
for d in docs:
    x = fields(d); x['id'] = d['name'].rsplit('/', 1)[1]
    if not x.get('title') or not x.get('body'): continue
    fresh = now - (x.get('date') or 0) < 3 * 86400 * 1000
    o = old.get(x['id'], {})
    a = {'id': x['id'], 'cat': x.get('cat', 'news'), 'title': x['title'], 'author': x.get('author') or 'عبدالله ربيع',
         'body': x['body'], 'date': x.get('date') or now, 'links': x.get('links') or [], 'cap': x.get('cap', ''),
         'midAt': x.get('midAt', 0), 'midCap': x.get('midCap', ''), 'pre': x.get('pre', 0), 'preCap': x.get('preCap', '')}
    def pick(key, name, want, thumb=None):
        if not want: return ''
        if not fresh and o.get(key) and os.path.exists(o[key]): return o[key]
        return fetch_img(name) or (save_img(name, thumb) if thumb else '') or (o.get(key) or '')
    a['image'] = pick('image', x['id'], x.get('hasFull') or x.get('image'), x.get('image')) if (x.get('hasFull') or x.get('image')) else ''
    a['midImg'] = pick('midImg', x['id'] + '_mid', x.get('midAt', 0) > 0)
    a['preImg'] = pick('preImg', x['id'] + '_pre', x.get('pre'))
    a['gal'] = [pick('gal%d' % i, '%s_%d' % (x['id'], i), True) if False else (fetch_img('%s_%d' % (x['id'], i)) if fresh or not (o.get('gal') and len(o['gal']) >= i and os.path.exists(o['gal'][i-1])) else o['gal'][i-1]) for i in range(1, (x.get('extra') or 0) + 1)]
    a['gal'] = [g for g in a['gal'] if g]
    out.append(a)
out.sort(key=lambda a: a['date'])
keep = {p for a in out for p in [a['image'], a['midImg'], a['preImg']] + a['gal'] if p}
for f in os.listdir('images/live'):
    if 'images/live/' + f not in keep: os.remove('images/live/' + f)
json.dump(out, open('live_articles.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('live articles:', len(out))
