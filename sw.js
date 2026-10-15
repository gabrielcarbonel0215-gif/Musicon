const CACHE_NAME = 'cinnamoroll-music-v10';
const PRECACHE_ASSETS = [
  '/manifest.json?v=10',
  '/assets/icon-192.png?v=10',
  '/assets/icon-512.png?v=10'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_ASSETS)).catch(() => {})
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  if (
    url.origin !== self.location.origin ||
    url.pathname.startsWith('/api/') ||
    url.pathname.startsWith('/canciones/') ||
    req.headers.has('range')
  ) {
    return;
  }

  // Network-First for main HTML page to ensure instant updates
  if (req.mode === 'navigate' || url.pathname === '/' || url.pathname === '/index.html') {
    event.respondWith(
      fetch(req, { cache: 'no-cache' })
        .then((networkResp) => {
          if (networkResp && networkResp.status === 200) {
            const copy = networkResp.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, copy)).catch(() => {});
          }
          return networkResp;
        })
        .catch(() => caches.match(req).then((cached) => cached || caches.match('/')))
    );
    return;
  }

  event.respondWith(
    fetch(req)
      .then((networkResp) => {
        if (networkResp && networkResp.status === 200 && networkResp.type === 'basic') {
          const copy = networkResp.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, copy)).catch(() => {});
        }
        return networkResp;
      })
      .catch(() => caches.match(req).then((cached) => cached || caches.match('/')))
  );
});
