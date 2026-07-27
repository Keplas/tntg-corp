// T&TG Service Worker — PWA offline support
const CACHE = 'tntg-v1';
const OFFLINE_URL = '/';
const ASSETS = ['/', '/static/css/style.css', '/static/images/logo.jpg'];

self.addEventListener('install', function(e){
  e.waitUntil(caches.open(CACHE).then(function(c){ return c.addAll(ASSETS); }));
  self.skipWaiting();
});

self.addEventListener('activate', function(e){
  e.waitUntil(caches.keys().then(function(keys){
    return Promise.all(keys.filter(function(k){ return k!==CACHE; }).map(function(k){ return caches.delete(k); }));
  }));
  self.clients.claim();
});

self.addEventListener('fetch', function(e){
  if(e.request.mode==='navigate'){
    e.respondWith(
      fetch(e.request).catch(function(){
        return caches.match(OFFLINE_URL);
      })
    );
  }
});
