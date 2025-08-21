// Simple Service Worker for College Football Predictor PWA
const CACHE_NAME = 'cfb-predictor-v2';
const urlsToCache = [
  '/',
  '/index.html',
  '/app.js',
  '/teams.json',
  '/week1/',
  '/week1/index.html'
];

// Install service worker and cache files
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

// Serve cached content when offline
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        return response || fetch(event.request);
      })
  );
});
