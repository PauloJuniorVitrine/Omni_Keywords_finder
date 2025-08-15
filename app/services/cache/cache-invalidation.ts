/**
 * Sistema de Invalidação Automática de Cache
 * 
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 7.2
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COMM_CHECKLIST_20250127_004
 */

import { globalCache } from './intelligent-cache';

export interface CacheInvalidationRule {
  pattern: string; // Regex pattern para matching de chaves
  dependencies: string[]; // Chaves que dependem desta
  eventTypes: string[]; // Tipos de eventos que disparam invalidação
  ttl?: number; // TTL específico para este tipo de cache
}

export interface CacheEvent {
  type: string;
  resource: string;
  action: 'create' | 'update' | 'delete' | 'refresh';
  timestamp: number;
  metadata?: Record<string, any>;
}

export class CacheInvalidationManager {
  private rules: Map<string, CacheInvalidationRule> = new Map();
  private eventListeners: Map<string, Set<Function>> = new Map();
  private dependencyGraph: Map<string, Set<string>> = new Map();

  constructor() {
    this.setupDefaultRules();
  }

  /**
   * Registra regra de invalidação
   */
  registerRule(name: string, rule: CacheInvalidationRule): void {
    this.rules.set(name, rule);
    
    // Construir grafo de dependências
    rule.dependencies.forEach(dep => {
      if (!this.dependencyGraph.has(dep)) {
        this.dependencyGraph.set(dep, new Set());
      }
      this.dependencyGraph.get(dep)!.add(name);
    });
  }

  /**
   * Processa evento e invalida cache conforme regras
   */
  processEvent(event: CacheEvent): void {
    console.log(`[CACHE] Processando evento: ${event.type} - ${event.resource}`);

    // Encontrar regras que se aplicam ao evento
    const applicableRules = this.findApplicableRules(event);
    
    // Invalidar cache baseado nas regras
    applicableRules.forEach(rule => {
      this.invalidateByRule(rule, event);
    });

    // Notificar listeners
    this.notifyEventListeners(event);
  }

  /**
   * Encontra regras aplicáveis ao evento
   */
  private findApplicableRules(event: CacheEvent): CacheInvalidationRule[] {
    const applicable: CacheInvalidationRule[] = [];

    for (const rule of this.rules.values()) {
      // Verificar se o tipo de evento está na lista
      if (rule.eventTypes.includes(event.type)) {
        // Verificar se o resource corresponde ao pattern
        if (new RegExp(rule.pattern).test(event.resource)) {
          applicable.push(rule);
        }
      }
    }

    return applicable;
  }

  /**
   * Invalida cache baseado na regra
   */
  private invalidateByRule(rule: CacheInvalidationRule, event: CacheEvent): void {
    const keysToInvalidate: string[] = [];

    // Buscar todas as chaves que correspondem ao pattern
    for (const [key] of globalCache['cache'].entries()) {
      if (new RegExp(rule.pattern).test(key)) {
        keysToInvalidate.push(key);
      }
    }

    // Invalidar chaves encontradas
    keysToInvalidate.forEach(key => {
      globalCache.delete(key);
      console.log(`[CACHE] Invalidado: ${key}`);
    });

    // Invalidar dependências
    this.invalidateDependencies(rule.dependencies);
  }

  /**
   * Invalida dependências recursivamente
   */
  private invalidateDependencies(dependencies: string[]): void {
    dependencies.forEach(dep => {
      // Invalidar cache que depende desta chave
      const dependentRules = this.dependencyGraph.get(dep);
      if (dependentRules) {
        dependentRules.forEach(ruleName => {
          const rule = this.rules.get(ruleName);
          if (rule) {
            this.invalidateByRule(rule, {
              type: 'dependency',
              resource: dep,
              action: 'refresh',
              timestamp: Date.now()
            });
          }
        });
      }
    });
  }

  /**
   * Registra listener para eventos de cache
   */
  on(eventType: string, callback: Function): void {
    if (!this.eventListeners.has(eventType)) {
      this.eventListeners.set(eventType, new Set());
    }
    this.eventListeners.get(eventType)!.add(callback);
  }

  /**
   * Remove listener
   */
  off(eventType: string, callback: Function): void {
    const listeners = this.eventListeners.get(eventType);
    if (listeners) {
      listeners.delete(callback);
    }
  }

  /**
   * Notifica listeners sobre evento
   */
  private notifyEventListeners(event: CacheEvent): void {
    const listeners = this.eventListeners.get(event.type);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(event);
        } catch (error) {
          console.error('[CACHE] Erro no listener:', error);
        }
      });
    }
  }

  /**
   * Configura regras padrão do sistema
   */
  private setupDefaultRules(): void {
    // Regra para dados de usuário
    this.registerRule('user-data', {
      pattern: '^user:',
      dependencies: ['user-profile', 'user-preferences'],
      eventTypes: ['user:update', 'user:delete', 'auth:logout']
    });

    // Regra para dados de análise
    this.registerRule('analytics-data', {
      pattern: '^analytics:',
      dependencies: ['dashboard:metrics'],
      eventTypes: ['analytics:new', 'analytics:update']
    });

    // Regra para dados de configuração
    this.registerRule('config-data', {
      pattern: '^config:',
      dependencies: ['app:settings'],
      eventTypes: ['config:update', 'config:reset']
    });

    // Regra para dados de API
    this.registerRule('api-data', {
      pattern: '^api:',
      dependencies: [],
      eventTypes: ['api:error', 'api:rate-limit']
    });
  }

  /**
   * Força invalidação de cache por pattern
   */
  forceInvalidate(pattern: string): void {
    const keysToInvalidate: string[] = [];

    for (const [key] of globalCache['cache'].entries()) {
      if (new RegExp(pattern).test(key)) {
        keysToInvalidate.push(key);
      }
    }

    keysToInvalidate.forEach(key => {
      globalCache.delete(key);
      console.log(`[CACHE] Força invalidação: ${key}`);
    });
  }

  /**
   * Retorna estatísticas de invalidação
   */
  getStats() {
    return {
      rulesCount: this.rules.size,
      listenersCount: Array.from(this.eventListeners.values()).reduce((acc, set) => acc + set.size, 0),
      dependenciesCount: this.dependencyGraph.size
    };
  }
}

// Instância global do gerenciador de invalidação
export const cacheInvalidationManager = new CacheInvalidationManager(); 