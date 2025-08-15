/**
 * Service Worker - Omni Keywords Finder
 * Cache Strategy: Cache First with Network Fallback
 * Tracing ID: SW_OPTIMIZATION_20250127_001
 */

const CACHE_NAME = 'omni-keywords-finder-v1.0.0';
const STATIC_CACHE = 'omni-static-v1.0.0';
const API_CACHE = 'omni-api-v1.0.0';

// Assets críticos para cache imediato
const CRITICAL_ASSETS = [
  '/',
  '/index.html',
  '/static/css/main.css',
  '/static/js/main.js',
  '/manifest.json',
  '/favicon.ico'
];

// Rotas de API para cache inteligente
const API_ROUTES = [
  '/api/keywords',
  '/api/analytics',
  '/api/dashboard',
  '/api/user/profile'
];

// Estratégia de cache: Cache First para assets estáticos
const cacheFirstStrategy = async (request) => {
  const cache = await caches.open(STATIC_CACHE);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.status === 200) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.error('Cache First Strategy Error:', error);
    return new Response('Offline content not available', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
};

// Estratégia de cache: Network First para APIs
const networkFirstStrategy = async (request) => {
  const cache = await caches.open(API_CACHE);
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.status === 200) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('Network failed, trying cache:', error);
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    return new Response('API offline', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
};

// Estratégia de cache: Stale While Revalidate para dados dinâmicos
const staleWhileRevalidateStrategy = async (request) => {
  const cache = await caches.open(API_CACHE);
  const cachedResponse = await cache.match(request);
  
  const fetchPromise = fetch(request).then((networkResponse) => {
    if (networkResponse.status === 200) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  }).catch(() => cachedResponse);
  
  return cachedResponse || fetchPromise;
};

// Install event - Cache assets críticos
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('Caching critical assets');
        return cache.addAll(CRITICAL_ASSETS);
      })
      .then(() => {
        console.log('Service Worker installed successfully');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker install failed:', error);
      })
  );
});

// Activate event - Limpeza de caches antigos
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== STATIC_CACHE && cacheName !== API_CACHE) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker activated successfully');
      return self.clients.claim();
    })
  );
});

// Fetch event - Intercepta requisições
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip chrome-extension requests
  if (url.protocol === 'chrome-extension:') {
    return;
  }
  
  // Estratégia baseada no tipo de recurso
  if (url.pathname.startsWith('/api/')) {
    // APIs - Network First com cache fallback
    event.respondWith(networkFirstStrategy(request));
  } else if (
    url.pathname.includes('.js') ||
    url.pathname.includes('.css') ||
    url.pathname.includes('.png') ||
    url.pathname.includes('.jpg') ||
    url.pathname.includes('.svg') ||
    url.pathname.includes('.woff') ||
    url.pathname.includes('.woff2')
  ) {
    // Assets estáticos - Cache First
    event.respondWith(cacheFirstStrategy(request));
  } else if (url.pathname.startsWith('/dashboard/') || url.pathname.startsWith('/analytics/')) {
    // Páginas dinâmicas - Stale While Revalidate
    event.respondWith(staleWhileRevalidateStrategy(request));
  } else {
    // Outros recursos - Network First
    event.respondWith(networkFirstStrategy(request));
  }
});

// Background sync para dados offline
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    console.log('Background sync triggered');
    event.waitUntil(
      // Implementar sincronização de dados offline
      syncOfflineData()
    );
  }
});

// Push notifications
self.addEventListener('push', (event) => {
  console.log('Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'Nova atualização disponível',
    icon: '/favicon.ico',
    badge: '/favicon.ico',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Ver detalhes',
        icon: '/favicon.ico'
      },
      {
        action: 'close',
        title: 'Fechar',
        icon: '/favicon.ico'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('Omni Keywords Finder', options)
  );
});

// Função para sincronizar dados offline
async function syncOfflineData() {
  try {
    const cache = await caches.open(API_CACHE);
    const requests = await cache.keys();
    
    for (const request of requests) {
      if (request.url.includes('/api/')) {
        try {
          const response = await fetch(request);
          if (response.status === 200) {
            await cache.put(request, response);
          }
        } catch (error) {
          console.error('Sync failed for:', request.url, error);
        }
      }
    }
    
    console.log('Offline data sync completed');
  } catch (error) {
    console.error('Background sync failed:', error);
  }
}

// Função para limpar cache expirado
async function cleanupExpiredCache() {
  try {
    const cache = await caches.open(API_CACHE);
    const requests = await cache.keys();
    const now = Date.now();
    
    for (const request of requests) {
      const response = await cache.match(request);
      if (response) {
        const cacheTime = response.headers.get('sw-cache-time');
        if (cacheTime && (now - parseInt(cacheTime)) > 24 * 60 * 60 * 1000) { // 24 horas
          await cache.delete(request);
        }
      }
    }
  } catch (error) {
    console.error('Cache cleanup failed:', error);
  }
}

// Limpeza periódica de cache (a cada 6 horas)
setInterval(cleanupExpiredCache, 6 * 60 * 60 * 1000);

console.log('Service Worker loaded successfully'); 