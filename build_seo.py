#!/usr/bin/env python3
"""يولّد صفحة ثابتة لكل خبر + sitemap.xml + robots.txt. شغّله بعد كل خبر جديد: python3 build_seo.py"""
import json, re, os, html, datetime, shutil
BASE = 'https://abdallah1rabee.github.io/Sport22/'
CATS = {'news': 'الأخبار'}
d = json.load(open('articles.json', encoding='utf-8'))
arts = d['articles']
e = html.escape
AR = '٠١٢٣٤٥٦٧٨٩'
def ar_date(ms):
    dt = datetime.datetime.utcfromtimestamp(ms/1000) + datetime.timedelta(hours=2)
    mon = ['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر'][dt.month-1]
    return f'{dt.day} {mon} {dt.year}'
def iso(ms):
    return (datetime.datetime.utcfromtimestamp(ms/1000)+datetime.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%S+02:00')
def inline(t):
    def link(m):
        u = m.group(2)
        m2 = re.match(re.escape(BASE)+r'#a-(.+)$', u)
        if m2: u = BASE + 'news/' + m2.group(1) + '/'
        return f'<a href="{e(u)}">{e(m.group(1))}</a>'
    out, last = '', 0
    for m in re.finditer(r'\[([^\]]+)\]\((https?://[^\s)]+)\)', t):
        out += e(t[last:m.start()]) + link(m); last = m.end()
    return out + e(t[last:])
def desc(a):
    p = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', a['body'].split('\n\n')[0]).strip()
    return p if len(p) <= 155 else p[:152].rsplit(' ', 1)[0] + '...'
CSS = """:root{--bg:#10151B;--surface:#18202A;--ink:#E9EDF2;--muted:#8B95A1;--line:#252D36;--accent:#7FD6B0}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:'IBM Plex Sans Arabic','Segoe UI',Tahoma,sans-serif;line-height:1.9}
header{border-bottom:1px solid var(--line)}.w{max-width:760px;margin:0 auto;padding:0 16px}
header .w{display:flex;justify-content:space-between;align-items:center;height:60px}
.logo{font-family:'Cairo',sans-serif;font-weight:800;font-size:22px;color:var(--ink);text-decoration:none;letter-spacing:.5px}
.logo b{color:var(--accent)}nav a{color:var(--muted);text-decoration:none;margin-inline-start:18px;font-size:15px}
article{padding:28px 0 40px}.tag{color:var(--accent);font-weight:600;font-size:14px;text-decoration:none}
h1{font-family:'Cairo',sans-serif;font-weight:800;font-size:32px;line-height:1.5;margin:6px 0 10px}
.by{color:var(--muted);font-size:15px;margin-bottom:18px}figure{margin:0 0 22px}
figure img{width:100%;height:auto;border-radius:14px;display:block}
p{font-size:19px;margin:0 0 18px}a{color:var(--accent)}
footer{border-top:1px solid var(--line);color:var(--muted);font-size:14px;padding:20px 0 40px}
@media(max-width:600px){h1{font-size:25px}p{font-size:17px}}"""
shutil.rmtree('news', ignore_errors=True)
for a in arts:
    url = f"{BASE}news/{a['id']}/"
    img = (BASE + a['image']) if a.get('image') else None
    ld = {"@context":"https://schema.org","@type":"NewsArticle","headline":a['title'],"datePublished":iso(a['date']),
          "dateModified":iso(a['date']),"author":{"@type":"Person","name":a['author']},
          "publisher":{"@type":"Organization","name":"SPORT 22"},"mainEntityOfPage":url,"inLanguage":"ar"}
    if img: ld["image"] = [img]
    paras = ''.join(f'<p>{inline(p)}</p>' for p in a['body'].split('\n\n') if p.strip())
    fig = f'<figure><img src="{e(img)}" alt="{e(a["title"])}" width="760" loading="eager"></figure>' if img else ''
    page = f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(a['title'])} | SPORT 22</title>
<meta name="description" content="{e(desc(a))}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{e(a['title'])}">
<meta property="og:description" content="{e(desc(a))}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="ar_AR">
<meta property="og:site_name" content="SPORT 22">
{f'<meta property="og:image" content="{e(img)}">' if img else ''}
<meta name="twitter:card" content="summary_large_image">
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@800&family=IBM+Plex+Sans+Arabic:wght@400;600&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{CSS}</style>
<script>window.goatcounter={{no_onload:false}}</script>
<script data-goatcounter="https://sport22.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</head>
<body>
<header><div class="w"><a class="logo" href="{BASE}">SPORT <b>22</b></a><nav><a href="{BASE}">الرئيسية</a><a href="{BASE}#c-{a.get('cat','news')}">{CATS.get(a.get('cat','news'),'الأخبار')}</a></nav></div></header>
<main class="w"><article>
<a class="tag" href="{BASE}#c-{a.get('cat','news')}">{CATS.get(a.get('cat','news'),'الأخبار')}</a>
<h1>{e(a['title'])}</h1>
<div class="by">{e(a['author'])} · <time datetime="{iso(a['date'])}">{ar_date(a['date'])}</time></div>
{fig}
{paras}
<p><a href="{BASE}">← كل أخبار SPORT 22</a></p>
</article></main>
<footer><div class="w">© SPORT 22 · أخبار وتقارير وتحليلات رياضية</div></footer>
</body>
</html>"""
    os.makedirs(f"news/{a['id']}", exist_ok=True)
    open(f"news/{a['id']}/index.html", 'w', encoding='utf-8').write(page)
urls = [(BASE, None)] + [(f"{BASE}news/{a['id']}/", iso(a['date'])[:10]) for a in arts]
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u, lm in urls:
    sm += f'  <url><loc>{u}</loc>' + (f'<lastmod>{lm}</lastmod>' if lm else '') + '</url>\n'
open('sitemap.xml', 'w', encoding='utf-8').write(sm + '</urlset>\n')
open('robots.txt', 'w').write(f"User-agent: *\nAllow: /\nDisallow: /Sport22/admin.html\n\nSitemap: {BASE}sitemap.xml\n")
print('pages:', len(arts))
