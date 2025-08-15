/**
 * Sistema de Background Sync
 * 
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 7.4
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: COMM_CHECKLIST_20250127_004
 */

import { globalCache } from '../cache/intelligent-cache';

export interface SyncTask {
  id: string;
  type: 'create' | 'update' | 'delete' | 'sync';
  endpoint: string;
  data?: any;
  priority: 'low' | 'medium' | 'high' | 'critical';
  retryCount: number;
  maxRetries: number;
  createdAt: number;
  lastAttempt?: number;
  error?: string;
}

export interface SyncConfig {
  syncInterval: number; // Intervalo entre sincronizações (ms)
  maxConcurrentTasks: number;
  retryDelay: number; // Delay entre tentativas (ms)
  enableOfflineQueue: boolean;
  syncOnOnline: boolean;
  syncOnVisibilityChange: boolean;
}

export class BackgroundSyncManager {
  private tasks: Map<string, SyncTask> = new Map();
  private config: SyncConfig;
  private isOnline: boolean = navigator.onLine;
  private isVisible: boolean = !document.hidden;
  private syncTimer?: NodeJS.Timeout;
  private isProcessing: boolean = false;

  constructor(config: Partial<SyncConfig> = {}) {
    this.config = {
      syncInterval: 30 * 1000, // 30 segundos
      maxConcurrentTasks: 3,
      retryDelay: 5000, // 5 segundos
      enableOfflineQueue: true,
      syncOnOnline: true,
      syncOnVisibilityChange: true,
      ...config
    };

    this.setupEventListeners();
    this.startSyncTimer();
  }

  /**
   * Adiciona tarefa de sincronização
   */
  addTask(task: Omit<SyncTask, 'id' | 'retryCount' | 'createdAt'>): string {
    const id = `sync_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const syncTask: SyncTask = {
      ...task,
      id,
      retryCount: 0,
      createdAt: Date.now()
    };

    this.tasks.set(id, syncTask);
    console.log(`[SYNC] Tarefa adicionada: ${id} - ${task.type} ${task.endpoint}`);

    // Processar imediatamente se online
    if (this.isOnline && !this.isProcessing) {
      this.processTasks();
    }

    return id;
  }

  /**
   * Remove tarefa da fila
   */
  removeTask(taskId: string): boolean {
    return this.tasks.delete(taskId);
  }

  /**
   * Processa todas as tarefas pendentes
   */
  async processTasks(): Promise<void> {
    if (this.isProcessing || !this.isOnline) {
      return;
    }

    this.isProcessing = true;

    try {
      // Ordenar tarefas por prioridade e data de criação
      const sortedTasks = Array.from(this.tasks.values())
        .sort((a, b) => {
          const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
          const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
          
          if (priorityDiff !== 0) return priorityDiff;
          return a.createdAt - b.createdAt;
        })
        .slice(0, this.config.maxConcurrentTasks);

      // Processar tarefas em paralelo
      const promises = sortedTasks.map(task => this.processTask(task));
      await Promise.allSettled(promises);

    } finally {
      this.isProcessing = false;
    }
  }

  /**
   * Processa uma tarefa específica
   */
  private async processTask(task: SyncTask): Promise<void> {
    try {
      console.log(`[SYNC] Processando: ${task.id} - ${task.type} ${task.endpoint}`);

      // Atualizar timestamp da última tentativa
      task.lastAttempt = Date.now();

      // Executar a operação
      const response = await this.executeTask(task);

      // Remover tarefa se bem-sucedida
      this.tasks.delete(task.id);
      console.log(`[SYNC] Sucesso: ${task.id}`);

      // Atualizar cache se necessário
      this.updateCache(task, response);

    } catch (error) {
      console.error(`[SYNC] Erro: ${task.id}`, error);

      // Incrementar contador de tentativas
      task.retryCount++;
      task.error = error instanceof Error ? error.message : 'Erro desconhecido';

      // Remover tarefa se excedeu tentativas máximas
      if (task.retryCount >= task.maxRetries) {
        this.tasks.delete(task.id);
        console.error(`[SYNC] Tarefa falhou definitivamente: ${task.id}`);
        this.handleTaskFailure(task, error);
      } else {
        // Reagendar para retry
        setTimeout(() => {
          if (this.tasks.has(task.id)) {
            this.processTasks();
          }
        }, this.config.retryDelay * task.retryCount);
      }
    }
  }

  /**
   * Executa a operação da tarefa
   */
  private async executeTask(task: SyncTask): Promise<any> {
    const { type, endpoint, data } = task;

    const options: RequestInit = {
      method: type === 'create' ? 'POST' : type === 'update' ? 'PUT' : type === 'delete' ? 'DELETE' : 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getAuthToken()}`
      }
    };

    if (data && type !== 'delete') {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(endpoint, options);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Atualiza cache com dados da sincronização
   */
  private updateCache(task: SyncTask, response: any): void {
    const cacheKey = this.generateCacheKey(task.endpoint);
    
    switch (task.type) {
      case 'create':
        // Adicionar novo item ao cache
        const existingData = globalCache.get<any[]>(cacheKey);
        if (existingData && Array.isArray(existingData)) {
          globalCache.set(cacheKey, [response, ...existingData]);
        }
        break;

      case 'update':
        // Atualizar item no cache
        const updateData = globalCache.get<any[]>(cacheKey);
        if (updateData && Array.isArray(updateData)) {
          const updatedList = updateData.map(item => 
            (item as any).id === (response as any).id ? response : item
          );
          globalCache.set(cacheKey, updatedList);
        }
        break;

      case 'delete':
        // Remover item do cache
        const deleteData = globalCache.get<any[]>(cacheKey);
        if (deleteData && Array.isArray(deleteData)) {
          const filteredList = deleteData.filter(item => 
            (item as any).id !== (task.data as any).id
          );
          globalCache.set(cacheKey, filteredList);
        }
        break;

      case 'sync':
        // Sincronizar dados completos
        globalCache.set(cacheKey, response);
        break;
    }
  }

  /**
   * Gera chave de cache baseada no endpoint
   */
  private generateCacheKey(endpoint: string): string {
    return `sync:${endpoint.replace(/[^a-zA-Z0-9]/g, '_')}`;
  }

  /**
   * Obtém token de autenticação
   */
  private getAuthToken(): string {
    // Implementar lógica para obter token do storage
    return localStorage.getItem('auth_token') || '';
  }

  /**
   * Trata falha definitiva de tarefa
   */
  private handleTaskFailure(task: SyncTask, error: any): void {
    // Notificar usuário sobre falha
    this.notifyTaskFailure(task, error);
    
    // Salvar em log de falhas
    this.logTaskFailure(task, error);
  }

  /**
   * Notifica usuário sobre falha
   */
  private notifyTaskFailure(task: SyncTask, error: any): void {
    // Implementar notificação ao usuário
    console.warn(`[SYNC] Falha na sincronização: ${task.type} ${task.endpoint}`);
  }

  /**
   * Registra falha em log
   */
  private logTaskFailure(task: SyncTask, error: any): void {
    const failureLog = {
      taskId: task.id,
      type: task.type,
      endpoint: task.endpoint,
      error: error instanceof Error ? error.message : 'Erro desconhecido',
      timestamp: new Date().toISOString(),
      retryCount: task.retryCount
    };

    // Salvar em localStorage para análise posterior
    const failures = JSON.parse(localStorage.getItem('sync_failures') || '[]');
    failures.push(failureLog);
    localStorage.setItem('sync_failures', JSON.stringify(failures));
  }

  /**
   * Configura listeners de eventos
   */
  private setupEventListeners(): void {
    // Listener para mudança de conectividade
    window.addEventListener('online', () => {
      this.isOnline = true;
      console.log('[SYNC] Conexão restaurada');
      if (this.config.syncOnOnline) {
        this.processTasks();
      }
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      console.log('[SYNC] Conexão perdida');
    });

    // Listener para mudança de visibilidade
    if (this.config.syncOnVisibilityChange) {
      document.addEventListener('visibilitychange', () => {
        this.isVisible = !document.hidden;
        if (this.isVisible && this.isOnline) {
          this.processTasks();
        }
      });
    }
  }

  /**
   * Inicia timer de sincronização
   */
  private startSyncTimer(): void {
    this.syncTimer = setInterval(() => {
      if (this.isOnline && this.isVisible) {
        this.processTasks();
      }
    }, this.config.syncInterval);
  }

  /**
   * Para o timer de sincronização
   */
  stopSyncTimer(): void {
    if (this.syncTimer) {
      clearInterval(this.syncTimer);
    }
  }

  /**
   * Retorna estatísticas de sincronização
   */
  getStats() {
    return {
      pendingTasks: this.tasks.size,
      isOnline: this.isOnline,
      isVisible: this.isVisible,
      isProcessing: this.isProcessing,
      tasksByPriority: {
        critical: Array.from(this.tasks.values()).filter(t => t.priority === 'critical').length,
        high: Array.from(this.tasks.values()).filter(t => t.priority === 'high').length,
        medium: Array.from(this.tasks.values()).filter(t => t.priority === 'medium').length,
        low: Array.from(this.tasks.values()).filter(t => t.priority === 'low').length
      }
    };
  }

  /**
   * Limpa todas as tarefas
   */
  clearTasks(): void {
    this.tasks.clear();
  }
}

// Instância global do gerenciador de sincronização
export const backgroundSyncManager = new BackgroundSyncManager(); 