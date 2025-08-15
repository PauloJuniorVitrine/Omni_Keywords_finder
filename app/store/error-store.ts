/**
 * error-store.ts
 * 
 * Store para gerenciamento de erros centralizado
 * 
 * Tracing ID: STORE-ERROR-001
 * Data: 2025-01-27
 * Versão: 1.0
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 4.2
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Categorização de erros
 * - Agrupamento por similaridade
 * - Histórico de erros
 * - Rate limiting
 * - Auto-dismiss
 * - Severidade levels
 * - Context tracking
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { ApiError } from '../shared/types/api';

// Tipos
export type ErrorSeverity = 'low' | 'medium' | 'high' | 'critical';
export type ErrorCategory = 'api' | 'network' | 'validation' | 'auth' | 'permission' | 'system' | 'user' | 'unknown';

interface ErrorContext {
  component?: string;
  action?: string;
  userId?: string;
  sessionId?: string;
  timestamp: number;
  userAgent?: string;
  url?: string;
  stack?: string;
}

interface ErrorEntry {
  id: string;
  message: string;
  code?: string;
  category: ErrorCategory;
  severity: ErrorSeverity;
  context: ErrorContext;
  count: number;
  firstOccurrence: number;
  lastOccurrence: number;
  dismissed: boolean;
  resolved: boolean;
  retryCount: number;
  maxRetries: number;
  autoDismissAt?: number;
}

interface ErrorGroup {
  pattern: string;
  errors: ErrorEntry[];
  totalCount: number;
  lastOccurrence: number;
}

interface ErrorState {
  // Erros ativos
  activeErrors: Map<string, ErrorEntry>;
  
  // Grupos de erros
  errorGroups: Map<string, ErrorGroup>;
  
  // Histórico
  errorHistory: ErrorEntry[];
  
  // Configurações
  config: {
    maxActiveErrors: number;
    maxHistorySize: number;
    autoDismissDelay: number;
    maxRetries: number;
    rateLimitWindow: number;
    rateLimitMax: number;
  };
  
  // Estatísticas
  stats: {
    totalErrors: number;
    errorsByCategory: Record<ErrorCategory, number>;
    errorsBySeverity: Record<ErrorSeverity, number>;
    resolvedErrors: number;
    dismissedErrors: number;
  };
  
  // Actions
  addError: (error: ApiError | Error, context?: Partial<ErrorContext>) => string;
  dismissError: (id: string) => void;
  resolveError: (id: string) => void;
  retryError: (id: string) => boolean;
  clearErrors: (category?: ErrorCategory) => void;
  clearHistory: () => void;
  
  // Getters
  getActiveErrors: () => ErrorEntry[];
  getErrorsByCategory: (category: ErrorCategory) => ErrorEntry[];
  getErrorsBySeverity: (severity: ErrorSeverity) => ErrorEntry[];
  getErrorGroups: () => ErrorGroup[];
  getErrorStats: () => typeof ErrorState.prototype.stats;
  
  // Utilitários
  isRateLimited: (pattern: string) => boolean;
  shouldAutoDismiss: (error: ErrorEntry) => boolean;
  cleanupExpiredErrors: () => void;
}

// Configurações padrão
const ERROR_CONFIG = {
  maxActiveErrors: 50,
  maxHistorySize: 1000,
  autoDismissDelay: 30 * 1000, // 30 segundos
  maxRetries: 3,
  rateLimitWindow: 60 * 1000, // 1 minuto
  rateLimitMax: 10,
};

// Função para gerar ID único
const generateErrorId = (): string => {
  return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

// Função para categorizar erro
const categorizeError = (error: ApiError | Error): ErrorCategory => {
  if ('status' in error) {
    const status = error.status;
    if (status >= 500) return 'system';
    if (status === 401) return 'auth';
    if (status === 403) return 'permission';
    if (status === 422) return 'validation';
    if (status >= 400) return 'api';
  }
  
  if (error.name === 'NetworkError' || error.message.includes('network')) return 'network';
  if (error.name === 'ValidationError') return 'validation';
  if (error.name === 'AuthError') return 'auth';
  if (error.name === 'PermissionError') return 'permission';
  
  return 'unknown';
};

// Função para determinar severidade
const determineSeverity = (error: ApiError | Error, category: ErrorCategory): ErrorSeverity => {
  if ('status' in error) {
    const status = error.status;
    if (status >= 500) return 'critical';
    if (status === 401 || status === 403) return 'high';
    if (status >= 400) return 'medium';
  }
  
  if (category === 'system') return 'critical';
  if (category === 'auth' || category === 'permission') return 'high';
  if (category === 'network') return 'medium';
  
  return 'low';
};

// Função para gerar padrão de agrupamento
const generateErrorPattern = (error: ApiError | Error, category: ErrorCategory): string => {
  if ('status' in error) {
    return `${category}_${error.status}_${error.message.split(' ').slice(0, 3).join('_')}`;
  }
  
  return `${category}_${error.name}_${error.message.split(' ').slice(0, 3).join('_')}`;
};

// Função para limpar erros expirados
const cleanupExpiredErrors = (errors: Map<string, ErrorEntry>): void => {
  const now = Date.now();
  for (const [id, error] of errors.entries()) {
    if (error.autoDismissAt && now > error.autoDismissAt) {
      errors.delete(id);
    }
  }
};

export const useErrorStore = create<ErrorState>()(
  devtools(
    subscribeWithSelector(
      persist(
        (set, get) => ({
          activeErrors: new Map<string, ErrorEntry>(),
          errorGroups: new Map<string, ErrorGroup>(),
          errorHistory: [],
          config: ERROR_CONFIG,
          stats: {
            totalErrors: 0,
            errorsByCategory: {
              api: 0,
              network: 0,
              validation: 0,
              auth: 0,
              permission: 0,
              system: 0,
              user: 0,
              unknown: 0,
            },
            errorsBySeverity: {
              low: 0,
              medium: 0,
              high: 0,
              critical: 0,
            },
            resolvedErrors: 0,
            dismissedErrors: 0,
          },

          // Actions
          addError: (error: ApiError | Error, context: Partial<ErrorContext> = {}) => {
            const id = generateErrorId();
            const category = categorizeError(error);
            const severity = determineSeverity(error, category);
            const pattern = generateErrorPattern(error, category);
            
            const errorEntry: ErrorEntry = {
              id,
              message: error.message,
              code: 'code' in error ? error.code : undefined,
              category,
              severity,
              context: {
                timestamp: Date.now(),
                userAgent: navigator.userAgent,
                url: window.location.href,
                stack: error.stack,
                ...context,
              },
              count: 1,
              firstOccurrence: Date.now(),
              lastOccurrence: Date.now(),
              dismissed: false,
              resolved: false,
              retryCount: 0,
              maxRetries: ERROR_CONFIG.maxRetries,
              autoDismissAt: severity === 'low' ? Date.now() + ERROR_CONFIG.autoDismissDelay : undefined,
            };

            set((state) => {
              const newActiveErrors = new Map(state.activeErrors);
              const newErrorGroups = new Map(state.errorGroups);
              const newErrorHistory = [...state.errorHistory];
              const newStats = { ...state.stats };

              // Verificar se já existe erro similar
              const existingGroup = newErrorGroups.get(pattern);
              if (existingGroup) {
                const existingError = existingGroup.errors.find(e => 
                  e.message === errorEntry.message && e.category === errorEntry.category
                );
                
                if (existingError) {
                  // Atualizar erro existente
                  existingError.count++;
                  existingError.lastOccurrence = Date.now();
                  existingError.retryCount = 0;
                  existingError.autoDismissAt = severity === 'low' ? Date.now() + ERROR_CONFIG.autoDismissDelay : undefined;
                  
                  // Atualizar grupo
                  existingGroup.totalCount++;
                  existingGroup.lastOccurrence = Date.now();
                  
                  return {
                    activeErrors: newActiveErrors,
                    errorGroups: newErrorGroups,
                    errorHistory: newErrorHistory,
                    stats: newStats,
                  };
                }
              }

              // Adicionar novo erro
              newActiveErrors.set(id, errorEntry);
              
              // Limitar número de erros ativos
              if (newActiveErrors.size > ERROR_CONFIG.maxActiveErrors) {
                const oldestError = Array.from(newActiveErrors.entries())
                  .sort((a, b) => a[1].firstOccurrence - b[1].firstOccurrence)[0];
                newActiveErrors.delete(oldestError[0]);
              }

              // Atualizar ou criar grupo
              const group = newErrorGroups.get(pattern) || {
                pattern,
                errors: [],
                totalCount: 0,
                lastOccurrence: 0,
              };
              group.errors.push(errorEntry);
              group.totalCount++;
              group.lastOccurrence = Date.now();
              newErrorGroups.set(pattern, group);

              // Adicionar ao histórico
              newErrorHistory.push(errorEntry);
              if (newErrorHistory.length > ERROR_CONFIG.maxHistorySize) {
                newErrorHistory.shift();
              }

              // Atualizar estatísticas
              newStats.totalErrors++;
              newStats.errorsByCategory[category]++;
              newStats.errorsBySeverity[severity]++;

              return {
                activeErrors: newActiveErrors,
                errorGroups: newErrorGroups,
                errorHistory: newErrorHistory,
                stats: newStats,
              };
            });

            return id;
          },

          dismissError: (id: string) => {
            set((state) => {
              const newActiveErrors = new Map(state.activeErrors);
              const error = newActiveErrors.get(id);
              
              if (error) {
                error.dismissed = true;
                newActiveErrors.delete(id);
                
                return {
                  activeErrors: newActiveErrors,
                  stats: {
                    ...state.stats,
                    dismissedErrors: state.stats.dismissedErrors + 1,
                  },
                };
              }
              
              return state;
            });
          },

          resolveError: (id: string) => {
            set((state) => {
              const newActiveErrors = new Map(state.activeErrors);
              const error = newActiveErrors.get(id);
              
              if (error) {
                error.resolved = true;
                newActiveErrors.delete(id);
                
                return {
                  activeErrors: newActiveErrors,
                  stats: {
                    ...state.stats,
                    resolvedErrors: state.stats.resolvedErrors + 1,
                  },
                };
              }
              
              return state;
            });
          },

          retryError: (id: string): boolean => {
            const state = get();
            const error = state.activeErrors.get(id);
            
            if (!error || error.retryCount >= error.maxRetries) {
              return false;
            }

            set((state) => {
              const newActiveErrors = new Map(state.activeErrors);
              const error = newActiveErrors.get(id);
              
              if (error) {
                error.retryCount++;
                error.lastOccurrence = Date.now();
              }
              
              return { activeErrors: newActiveErrors };
            });

            return true;
          },

          clearErrors: (category?: ErrorCategory) => {
            set((state) => {
              const newActiveErrors = new Map(state.activeErrors);
              
              if (category) {
                for (const [id, error] of newActiveErrors.entries()) {
                  if (error.category === category) {
                    newActiveErrors.delete(id);
                  }
                }
              } else {
                newActiveErrors.clear();
              }
              
              return { activeErrors: newActiveErrors };
            });
          },

          clearHistory: () => {
            set({ errorHistory: [] });
          },

          // Getters
          getActiveErrors: (): ErrorEntry[] => {
            const state = get();
            return Array.from(state.activeErrors.values());
          },

          getErrorsByCategory: (category: ErrorCategory): ErrorEntry[] => {
            const state = get();
            return Array.from(state.activeErrors.values())
              .filter(error => error.category === category);
          },

          getErrorsBySeverity: (severity: ErrorSeverity): ErrorEntry[] => {
            const state = get();
            return Array.from(state.activeErrors.values())
              .filter(error => error.severity === severity);
          },

          getErrorGroups: (): ErrorGroup[] => {
            const state = get();
            return Array.from(state.errorGroups.values());
          },

          getErrorStats: () => {
            const state = get();
            return state.stats;
          },

          // Utilitários
          isRateLimited: (pattern: string): boolean => {
            const state = get();
            const group = state.errorGroups.get(pattern);
            
            if (!group) return false;
            
            const now = Date.now();
            const recentErrors = group.errors.filter(error => 
              now - error.lastOccurrence < ERROR_CONFIG.rateLimitWindow
            );
            
            return recentErrors.length >= ERROR_CONFIG.rateLimitMax;
          },

          shouldAutoDismiss: (error: ErrorEntry): boolean => {
            return error.autoDismissAt ? Date.now() > error.autoDismissAt : false;
          },

          cleanupExpiredErrors: () => {
            set((state) => {
              const newActiveErrors = new Map(state.activeErrors);
              cleanupExpiredErrors(newActiveErrors);
              
              return { activeErrors: newActiveErrors };
            });
          },
        }),
        {
          name: 'error-store',
          storage: createJSONStorage(() => localStorage),
          partialize: (state) => ({
            errorHistory: state.errorHistory.slice(-100), // Manter apenas últimos 100
            stats: state.stats,
          }),
        }
      )
    ),
    {
      name: 'error-store',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);

// Hooks utilitários
export const useActiveErrors = () => {
  const store = useErrorStore();
  return store.getActiveErrors();
};

export const useErrorsByCategory = (category: ErrorCategory) => {
  const store = useErrorStore();
  return store.getErrorsByCategory(category);
};

export const useErrorsBySeverity = (severity: ErrorSeverity) => {
  const store = useErrorStore();
  return store.getErrorsBySeverity(severity);
};

export const useErrorGroups = () => {
  const store = useErrorStore();
  return store.getErrorGroups();
};

export const useErrorStats = () => {
  const store = useErrorStore();
  return store.getErrorStats();
};

// Auto-cleanup
if (typeof window !== 'undefined') {
  setInterval(() => {
    useErrorStore.getState().cleanupExpiredErrors();
  }, 60000); // A cada minuto
}

export default useErrorStore; 