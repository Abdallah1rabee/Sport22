#!/usr/bin/env python3
"""يبلّغ محركات البحث (Bing/Yandex عبر IndexNow) بالأخبار الجديدة. يستخدم الروابط الموجودة في sitemap.xml التي تغيّرت."""
import re, sys, json, urllib.request
BASE = 'https://abdallah1rabee.github.io/Sport22/'
KEY = '594b0616f98bd5b23a5ebd72125193bd'
urls = [BASE + 'news/' + i + '/' for i in sys.argv[1:]]
if not urls: raise SystemExit('no new urls')
body = json.dumps({'host': 'abdallah1rabee.github.io', 'key': KEY, 'keyLocation': BASE + KEY + '.txt', 'urlList': urls}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', body, {'Content-Type': 'application/json; charset=utf-8'})
try: print(urllib.request.urlopen(req, timeout=20).status)
except Exception as ex: print('indexnow:', ex)
