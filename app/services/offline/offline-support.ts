/**
 * Sistema de Suporte Offline
 * 
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 7.5
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COMM_CHECKLIST_20250127_004
 */

import { globalCache } from '../cache/intelligent-cache';
import { backgroundSyncManager } from '../sync/background-sync';

export interface OfflineData {
  key: string;
  data: any;
  timestamp: number;
  version: number;
  isStale: boolean;
}

export interface OfflineConfig {
  enableServiceWorker: boolean;
  enableIndexedDB: boolean;
  enableLocalStorage: boolean;
  maxStorageSize: number; // em MB
  syncOnReconnect: boolean;
  cacheCriticalData: boolean;
}

export class OfflineSupportManager {
  private config: OfflineConfig;
  private isOnline: boolean = navigator.onLine;
  private db: IDBDatabase | null = null;
  private storageQuota: StorageEstimate | null = null;

  constructor(config: Partial<OfflineConfig> = {}) {
    this.config = {
      enableServiceWorker: true,
      enableIndexedDB: true,
      enableLocalStorage: true,
      maxStorageSize: 50, // 50MB
      syncOnReconnect: true,
      cacheCriticalData: true,
      ...config
    };

    this.initialize();
  }

  /**
   * Inicializa o sistema offline
   */
  private async initialize(): Promise<void> {
    try {
      // Verificar quota de storage
      await this.checkStorageQuota();

      // Inicializar IndexedDB
      if (this.config.enableIndexedDB) {
        await this.initIndexedDB();
      }

      // Configurar Service Worker
      if (this.config.enableServiceWorker) {
        await this.registerServiceWorker();
      }

      // Configurar listeners de conectividade
      this.setupConnectivityListeners();

      // Cache de dados críticos
      if (this.config.cacheCriticalData) {
        await this.cacheCriticalData();
      }

      console.log('[OFFLINE] Sistema offline inicializado com sucesso');

    } catch (error) {
      console.error('[OFFLINE] Erro na inicialização:', error);
    }
  }

  /**
   * Verifica quota de storage disponível
   */
  private async checkStorageQuota(): Promise<void> {
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      try {
        this.storageQuota = await navigator.storage.estimate();
        const usedMB = (this.storageQuota.usage || 0) / (1024 * 1024);
        const quotaMB = (this.storageQuota.quota || 0) / (1024 * 1024);
        
        console.log(`[OFFLINE] Storage: ${usedMB.toFixed(2)}MB / ${quotaMB.toFixed(2)}MB`);
        
        if (usedMB > this.config.maxStorageSize) {
          console.warn('[OFFLINE] Storage próximo do limite');
          await this.cleanupOldData();
        }
      } catch (error) {
        console.warn('[OFFLINE] Não foi possível verificar quota de storage:', error);
      }
    }
  }

  /**
   * Inicializa IndexedDB
   */
  private async initIndexedDB(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('OfflineData', 1);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        
        // Store para dados offline
        if (!db.objectStoreNames.contains('offlineData')) {
          const store = db.createObjectStore('offlineData', { keyPath: 'key' });
          store.createIndex('timestamp', 'timestamp', { unique: false });
          store.createIndex('version', 'version', { unique: false });
        }

        // Store para fila de operações
        if (!db.objectStoreNames.contains('operationQueue')) {
          const queueStore = db.createObjectStore('operationQueue', { keyPath: 'id', autoIncrement: true });
          queueStore.createIndex('priority', 'priority', { unique: false });
          queueStore.createIndex('timestamp', 'timestamp', { unique: false });
        }
      };
    });
  }

  /**
   * Registra Service Worker
   */
  private async registerServiceWorker(): Promise<void> {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/service-worker.js');
        console.log('[OFFLINE] Service Worker registrado:', registration);
      } catch (error) {
        console.error('[OFFLINE] Erro ao registrar Service Worker:', error);
      }
    }
  }

  /**
   * Configura listeners de conectividade
   */
  private setupConnectivityListeners(): void {
    window.addEventListener('online', () => {
      this.isOnline = true;
      console.log('[OFFLINE] Conexão restaurada');
      
      if (this.config.syncOnReconnect) {
        this.syncOfflineData();
      }
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      console.log('[OFFLINE] Conexão perdida');
    });
  }

  /**
   * Cache de dados críticos para uso offline
   */
  private async cacheCriticalData(): Promise<void> {
    const criticalEndpoints = [
      '/api/user/profile',
      '/api/app/config',
      '/api/navigation/menu',
      '/api/features/flags'
    ];

    for (const endpoint of criticalEndpoints) {
      try {
        const response = await fetch(endpoint);
        if (response.ok) {
          const data = await response.json();
          await this.storeOfflineData(endpoint, data);
        }
      } catch (error) {
        console.warn(`[OFFLINE] Erro ao cachear ${endpoint}:`, error);
      }
    }
  }

  /**
   * Armazena dados para uso offline
   */
  async storeOfflineData(key: string, data: any, version: number = 1): Promise<void> {
    const offlineData: OfflineData = {
      key,
      data,
      timestamp: Date.now(),
      version,
      isStale: false
    };

    // Armazenar no IndexedDB
    if (this.config.enableIndexedDB && this.db) {
      await this.storeInIndexedDB(offlineData);
    }

    // Armazenar no LocalStorage (dados pequenos)
    if (this.config.enableLocalStorage && JSON.stringify(data).length < 1024 * 1024) {
      this.storeInLocalStorage(offlineData);
    }

    // Armazenar no cache em memória
    globalCache.set(`offline:${key}`, offlineData);
  }

  /**
   * Armazena dados no IndexedDB
   */
  private async storeInIndexedDB(data: OfflineData): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('IndexedDB não inicializado'));
        return;
      }

      const transaction = this.db.transaction(['offlineData'], 'readwrite');
      const store = transaction.objectStore('offlineData');
      const request = store.put(data);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Armazena dados no LocalStorage
   */
  private storeInLocalStorage(data: OfflineData): void {
    try {
      localStorage.setItem(`offline_${data.key}`, JSON.stringify(data));
    } catch (error) {
      console.warn('[OFFLINE] Erro ao salvar no LocalStorage:', error);
    }
  }

  /**
   * Recupera dados offline
   */
  async getOfflineData(key: string): Promise<any | null> {
    // Tentar cache em memória primeiro
    const cached = globalCache.get<OfflineData>(`offline:${key}`);
    if (cached && !cached.isStale) {
      return cached.data;
    }

    // Tentar IndexedDB
    if (this.config.enableIndexedDB && this.db) {
      const indexedDBData = await this.getFromIndexedDB(key);
      if (indexedDBData) {
        return indexedDBData.data;
      }
    }

    // Tentar LocalStorage
    if (this.config.enableLocalStorage) {
      const localStorageData = this.getFromLocalStorage(key);
      if (localStorageData) {
        return localStorageData.data;
      }
    }

    return null;
  }

  /**
   * Recupera dados do IndexedDB
   */
  private async getFromIndexedDB(key: string): Promise<OfflineData | null> {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        resolve(null);
        return;
      }

      const transaction = this.db.transaction(['offlineData'], 'readonly');
      const store = transaction.objectStore('offlineData');
      const request = store.get(key);

      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Recupera dados do LocalStorage
   */
  private getFromLocalStorage(key: string): OfflineData | null {
    try {
      const data = localStorage.getItem(`offline_${key}`);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.warn('[OFFLINE] Erro ao ler do LocalStorage:', error);
      return null;
    }
  }

  /**
   * Adiciona operação à fila offline
   */
  async queueOperation(operation: {
    type: string;
    endpoint: string;
    data?: any;
    priority: 'low' | 'medium' | 'high' | 'critical';
  }): Promise<string> {
    const operationId = `op_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const queuedOperation = {
      id: operationId,
      ...operation,
      timestamp: Date.now(),
      retryCount: 0
    };

    // Adicionar à fila do IndexedDB
    if (this.config.enableIndexedDB && this.db) {
      await this.addToOperationQueue(queuedOperation);
    }

    // Adicionar à fila de sincronização
    backgroundSyncManager.addTask({
      type: operation.type as any,
      endpoint: operation.endpoint,
      data: operation.data,
      priority: operation.priority,
      maxRetries: 3
    });

    return operationId;
  }

  /**
   * Adiciona operação à fila do IndexedDB
   */
  private async addToOperationQueue(operation: any): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        resolve();
        return;
      }

      const transaction = this.db.transaction(['operationQueue'], 'readwrite');
      const store = transaction.objectStore('operationQueue');
      const request = store.add(operation);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Sincroniza dados offline quando reconecta
   */
  private async syncOfflineData(): Promise<void> {
    console.log('[OFFLINE] Iniciando sincronização de dados offline');

    // Processar fila de operações
    if (this.config.enableIndexedDB && this.db) {
      await this.processOperationQueue();
    }

    // Atualizar dados stale
    await this.updateStaleData();
  }

  /**
   * Processa fila de operações
   */
  private async processOperationQueue(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        resolve();
        return;
      }

      const transaction = this.db.transaction(['operationQueue'], 'readwrite');
      const store = transaction.objectStore('operationQueue');
      const request = store.getAll();

      request.onsuccess = async () => {
        const operations = request.result;
        
        for (const operation of operations) {
          try {
            // Executar operação
            await this.executeQueuedOperation(operation);
            
            // Remover da fila
            store.delete(operation.id);
          } catch (error) {
            console.error('[OFFLINE] Erro ao processar operação:', error);
            operation.retryCount++;
            
            if (operation.retryCount >= 3) {
              store.delete(operation.id);
            }
          }
        }
        
        resolve();
      };

      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Executa operação da fila
   */
  private async executeQueuedOperation(operation: any): Promise<void> {
    const response = await fetch(operation.endpoint, {
      method: operation.type === 'create' ? 'POST' : operation.type === 'update' ? 'PUT' : 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`
      },
      body: operation.data ? JSON.stringify(operation.data) : undefined
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
  }

  /**
   * Atualiza dados stale
   */
  private async updateStaleData(): Promise<void> {
    // Implementar lógica para atualizar dados marcados como stale
    console.log('[OFFLINE] Atualizando dados stale');
  }

  /**
   * Limpa dados antigos
   */
  private async cleanupOldData(): Promise<void> {
    const cutoffTime = Date.now() - (7 * 24 * 60 * 60 * 1000); // 7 dias

    if (this.config.enableIndexedDB && this.db) {
      const transaction = this.db.transaction(['offlineData'], 'readwrite');
      const store = transaction.objectStore('offlineData');
      const index = store.index('timestamp');
      const request = index.openCursor(IDBKeyRange.upperBound(cutoffTime));

      request.onsuccess = (event) => {
        const cursor = (event.target as IDBRequest).result;
        if (cursor) {
          cursor.delete();
          cursor.continue();
        }
      };
    }

    // Limpar LocalStorage antigo
    if (this.config.enableLocalStorage) {
      Object.keys(localStorage)
        .filter(key => key.startsWith('offline_'))
        .forEach(key => {
          try {
            const data = JSON.parse(localStorage.getItem(key) || '{}');
            if (data.timestamp && data.timestamp < cutoffTime) {
              localStorage.removeItem(key);
            }
          } catch (error) {
            localStorage.removeItem(key);
          }
        });
    }
  }

  /**
   * Verifica se está offline
   */
  isOffline(): boolean {
    return !this.isOnline;
  }

  /**
   * Retorna estatísticas offline
   */
  async getStats() {
    let offlineDataCount = 0;
    let operationQueueCount = 0;

    if (this.config.enableIndexedDB && this.db) {
      const transaction = this.db.transaction(['offlineData', 'operationQueue'], 'readonly');
      
      const dataStore = transaction.objectStore('offlineData');
      const dataRequest = dataStore.count();
      offlineDataCount = await new Promise(resolve => {
        dataRequest.onsuccess = () => resolve(dataRequest.result);
      });

      const queueStore = transaction.objectStore('operationQueue');
      const queueRequest = queueStore.count();
      operationQueueCount = await new Promise(resolve => {
        queueRequest.onsuccess = () => resolve(queueRequest.result);
      });
    }

    return {
      isOnline: this.isOnline,
      offlineDataCount,
      operationQueueCount,
      storageQuota: this.storageQuota
    };
  }
}

// Instância global do gerenciador offline
export const offlineSupportManager = new OfflineSupportManager(); 