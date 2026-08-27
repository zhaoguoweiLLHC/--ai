// 教资备考 PWA Service Worker
// 策略：网络优先，失败则用缓存（适合 git push 后自动更新场景）
const CACHE_NAME = 'jiaozi-v' + Date.now();
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './00_考试总览/学习计划表.html',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  // 只处理 GET
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then(res => {
        // 成功获取，更新缓存
        const clone = res.clone();
        caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
        return res;
      })
      .catch(() => {
        // 离线时用缓存
        return caches.match(e.request).then(cached => cached || caches.match('./index.html'));
      })
  );
});
