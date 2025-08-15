/**
 * Sistema de Cache Inteligente com TTL
 * 
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 7.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COMM_CHECKLIST_20250127_004
 */

export interface CacheEntry<T = any> {
  data: T;
  timestamp: number;
  ttl: number;
  accessCount: number;
  lastAccessed: number;
}

export interface CacheConfig {
  defaultTTL: number; // em milissegundos
  maxSize: number;
  cleanupInterval: number;
  enableLRU: boolean;
}

export class IntelligentCache {
  private cache = new Map<string, CacheEntry>();
  private config: CacheConfig;
  private cleanupTimer?: NodeJS.Timeout;

  constructor(config: Partial<CacheConfig> = {}) {
    this.config = {
      defaultTTL: 5 * 60 * 1000, // 5 minutos
      maxSize: 1000,
      cleanupInterval: 60 * 1000, // 1 minuto
      enableLRU: true,
      ...config
    };

    this.startCleanupTimer();
  }

  /**
   * Armazena dados no cache com TTL
   */
  set<T>(key: string, data: T, ttl?: number): void {
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.config.defaultTTL,
      accessCount: 0,
      lastAccessed: Date.now()
    };

    // Implementar LRU se habilitado
    if (this.config.enableLRU && this.cache.size >= this.config.maxSize) {
      this.evictLRU();
    }

    this.cache.set(key, entry);
  }

  /**
   * Recupera dados do cache
   */
  get<T>(key: string): T | null {
    const entry = this.cache.get(key) as CacheEntry<T>;
    
    if (!entry) {
      return null;
    }

    // Verificar se expirou
    if (this.isExpired(entry)) {
      this.cache.delete(key);
      return null;
    }

    // Atualizar estatísticas de acesso
    entry.accessCount++;
    entry.lastAccessed = Date.now();

    return entry.data;
  }

  /**
   * Verifica se entrada expirou
   */
  private isExpired(entry: CacheEntry): boolean {
    return Date.now() - entry.timestamp > entry.ttl;
  }

  /**
   * Implementa evicção LRU (Least Recently Used)
   */
  private evictLRU(): void {
    let oldestKey: string | null = null;
    let oldestTime = Date.now();

    for (const [key, entry] of this.cache.entries()) {
      if (entry.lastAccessed < oldestTime) {
        oldestTime = entry.lastAccessed;
        oldestKey = key;
      }
    }

    if (oldestKey) {
      this.cache.delete(oldestKey);
    }
  }

  /**
   * Remove entrada específica
   */
  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  /**
   * Limpa todo o cache
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Retorna estatísticas do cache
   */
  getStats() {
    const now = Date.now();
    let expiredCount = 0;
    let totalAccessCount = 0;

    for (const entry of this.cache.values()) {
      if (this.isExpired(entry)) {
        expiredCount++;
      }
      totalAccessCount += entry.accessCount;
    }

    return {
      size: this.cache.size,
      expiredCount,
      totalAccessCount,
      hitRate: totalAccessCount > 0 ? totalAccessCount / this.cache.size : 0
    };
  }

  /**
   * Inicia timer de limpeza automática
   */
  private startCleanupTimer(): void {
    this.cleanupTimer = setInterval(() => {
      this.cleanup();
    }, this.config.cleanupInterval);
  }

  /**
   * Remove entradas expiradas
   */
  private cleanup(): void {
    const now = Date.now();
    const keysToDelete: string[] = [];

    for (const [key, entry] of this.cache.entries()) {
      if (this.isExpired(entry)) {
        keysToDelete.push(key);
      }
    }

    keysToDelete.forEach(key => this.cache.delete(key));
  }

  /**
   * Para o timer de limpeza
   */
  destroy(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
    }
  }
}

// Instância global do cache
export const globalCache = new IntelligentCache(); 