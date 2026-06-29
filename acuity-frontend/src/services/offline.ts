const DB_NAME = 'acuity-offline';
const DB_VERSION = 1;

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains('requests')) {
        db.createObjectStore('requests', { keyPath: 'id', autoIncrement: true });
      }
      if (!db.objectStoreNames.contains('cache')) {
        db.createObjectStore('cache', { keyPath: 'key' });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

export const offlineDB = {
  async saveRequest(method: string, url: string, body?: unknown) {
    const db = await openDB();
    const tx = db.transaction('requests', 'readwrite');
    tx.objectStore('requests').add({ method, url, body, timestamp: Date.now() });
    return new Promise<void>((resolve, reject) => {
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  },

  async getPendingRequests() {
    const db = await openDB();
    const tx = db.transaction('requests', 'readonly');
    return new Promise<Array<{ id: number; method: string; url: string; body?: unknown }>>((resolve, reject) => {
      const req = tx.objectStore('requests').getAll();
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  },

  async removeRequest(id: number) {
    const db = await openDB();
    const tx = db.transaction('requests', 'readwrite');
    tx.objectStore('requests').delete(id);
    return new Promise<void>((resolve, reject) => {
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  },

  async setCache(key: string, data: unknown) {
    const db = await openDB();
    const tx = db.transaction('cache', 'readwrite');
    tx.objectStore('cache').put({ key, data, timestamp: Date.now() });
    return new Promise<void>((resolve, reject) => {
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  },

  async getCache(key: string) {
    const db = await openDB();
    const tx = db.transaction('cache', 'readonly');
    return new Promise<unknown>((resolve, reject) => {
      const req = tx.objectStore('cache').get(key);
      req.onsuccess = () => resolve(req.result?.data);
      req.onerror = () => reject(req.error);
    });
  },
};

export function isOnline(): boolean {
  return navigator.onLine;
}

export function registerSW() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js').catch(() => {});
    });
  }
}
