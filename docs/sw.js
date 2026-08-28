// 教资备考 PWA Service Worker v2
// 策略：网络优先，缓存只用于离线兜底
const CACHE_VERSION = 'jiaozi-v2-20260828';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './通勤库/通勤.html',
];

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE_VERSION).then(c => c.addAll(ASSETS)));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_VERSION).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  // 导航请求和页面请求：网络优先
  e.respondWith(
    fetch(e.request).then(res => {
      const clone = res.clone();
      caches.open(CACHE_VERSION).then(c => c.put(e.request, clone));
      return res;
    }).catch(() => {
      return caches.match(e.request).then(cached => cached || caches.match('./index.html'));
    })
  );
});
