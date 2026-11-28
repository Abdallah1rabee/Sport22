/* SPORT 22 service worker: الشبكة أولًا عشان الأخبار دايمًا تبقى أحدث نسخة، والكاش بس لما النت يقطع */
var CACHE = 's22-v2';
var SHELL = ['offline.html', 'icons/icon-192.png'];
self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(SHELL); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (ks) {
    return Promise.all(ks.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  var r = e.request;
  if (r.method !== 'GET') return;
  var u = new URL(r.url);
  if (u.origin !== location.origin) return;
  e.respondWith(
    fetch(r.mode === 'navigate' ? new Request(r, { cache: 'no-cache' }) : r).then(function (res) {
      if (res && res.ok && res.type === 'basic') { var copy = res.clone(); caches.open(CACHE).then(function (c) { c.put(r, copy); }); }
      return res;
    }).catch(function () {
      return caches.match(r).then(function (hit) {
        if (hit) return hit;
        if (r.mode === 'navigate') return caches.match('offline.html');
        return new Response('', { status: 504, statusText: 'offline' });
      });
    })
  );
});
