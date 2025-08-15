/**
 * config-store.ts
 * 
 * Store para gerenciamento de configurações da aplicação
 * 
 * Tracing ID: STORE-CONFIG-001
 * Data: 2025-01-27
 * Versão: 1.0
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 4.3
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Configurações de API
 * - Configurações de UI
 * - Configurações de performance
 * - Sincronização com backend
 * - Validação de configurações
 * - Fallbacks
 * - Hot reload
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { ApiClient } from '../services/api/ApiClient';

// Tipos
interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
  cacheEnabled: boolean;
  cacheTTL: number;
  requestQueue: boolean;
  requestQueueSize: number;
  rateLimit: {
    enabled: boolean;
    maxRequests: number;
    windowMs: number;
  };
  compression: boolean;
  keepAlive: boolean;
  keepAliveTimeout: number;
}

interface UIConfig {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  timezone: string;
  dateFormat: string;
  timeFormat: string;
  currency: string;
  locale: string;
  animations: boolean;
  soundEnabled: boolean;
  notifications: {
    enabled: boolean;
    position: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
    duration: number;
    maxVisible: number;
  };
  sidebar: {
    collapsed: boolean;
    width: number;
    autoCollapse: boolean;
  };
  table: {
    pageSize: number;
    showPagination: boolean;
    showSearch: boolean;
    showFilters: boolean;
    sortable: boolean;
  };
  form: {
    validateOnChange: boolean;
    validateOnBlur: boolean;
    showValidationMessages: boolean;
    autoSave: boolean;
    autoSaveDelay: number;
  };
}

interface PerformanceConfig {
  lazyLoading: boolean;
  virtualScrolling: boolean;
  imageOptimization: boolean;
  codeSplitting: boolean;
  preloading: boolean;
  caching: {
    enabled: boolean;
    strategy: 'memory' | 'localStorage' | 'sessionStorage' | 'indexedDB';
    maxSize: number;
  };
  monitoring: {
    enabled: boolean;
    sampleRate: number;
    trackErrors: boolean;
    trackPerformance: boolean;
    trackUserActions: boolean;
  };
  optimization: {
    debounceDelay: number;
    throttleDelay: number;
    batchUpdates: boolean;
    memoization: boolean;
  };
}

interface SecurityConfig {
  csrfProtection: boolean;
  xssProtection: boolean;
  contentSecurityPolicy: boolean;
  secureHeaders: boolean;
  sessionTimeout: number;
  maxLoginAttempts: number;
  passwordPolicy: {
    minLength: number;
    requireUppercase: boolean;
    requireLowercase: boolean;
    requireNumbers: boolean;
    requireSpecialChars: boolean;
  };
  twoFactorAuth: {
    enabled: boolean;
    method: 'sms' | 'email' | 'app';
  };
}

interface FeatureFlags {
  [key: string]: boolean;
}

interface ConfigState {
  // Configurações
  api: ApiConfig;
  ui: UIConfig;
  performance: PerformanceConfig;
  security: SecurityConfig;
  featureFlags: FeatureFlags;
  
  // Estado
  isLoaded: boolean;
  isSyncing: boolean;
  lastSync: number | null;
  version: string;
  
  // Actions
  updateApiConfig: (config: Partial<ApiConfig>) => void;
  updateUIConfig: (config: Partial<UIConfig>) => void;
  updatePerformanceConfig: (config: Partial<PerformanceConfig>) => void;
  updateSecurityConfig: (config: Partial<SecurityConfig>) => void;
  updateFeatureFlags: (flags: Partial<FeatureFlags>) => void;
  
  // Sincronização
  syncWithBackend: () => Promise<void>;
  loadFromBackend: () => Promise<void>;
  saveToBackend: () => Promise<void>;
  
  // Utilitários
  resetToDefaults: () => void;
  exportConfig: () => string;
  importConfig: (config: string) => boolean;
  validateConfig: () => boolean;
  getConfigValue: <T>(path: string) => T | undefined;
  setConfigValue: <T>(path: string, value: T) => void;
}

// Configurações padrão
const DEFAULT_API_CONFIG: ApiConfig = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api',
  timeout: 30000,
  retryAttempts: 3,
  retryDelay: 1000,
  cacheEnabled: true,
  cacheTTL: 5 * 60 * 1000, // 5 minutos
  requestQueue: true,
  requestQueueSize: 10,
  rateLimit: {
    enabled: true,
    maxRequests: 100,
    windowMs: 60 * 1000, // 1 minuto
  },
  compression: true,
  keepAlive: true,
  keepAliveTimeout: 30000,
};

const DEFAULT_UI_CONFIG: UIConfig = {
  theme: 'auto',
  language: 'pt-BR',
  timezone: 'America/Sao_Paulo',
  dateFormat: 'DD/MM/YYYY',
  timeFormat: 'HH:mm',
  currency: 'BRL',
  locale: 'pt-BR',
  animations: true,
  soundEnabled: false,
  notifications: {
    enabled: true,
    position: 'top-right',
    duration: 5000,
    maxVisible: 5,
  },
  sidebar: {
    collapsed: false,
    width: 250,
    autoCollapse: true,
  },
  table: {
    pageSize: 20,
    showPagination: true,
    showSearch: true,
    showFilters: true,
    sortable: true,
  },
  form: {
    validateOnChange: true,
    validateOnBlur: true,
    showValidationMessages: true,
    autoSave: false,
    autoSaveDelay: 2000,
  },
};

const DEFAULT_PERFORMANCE_CONFIG: PerformanceConfig = {
  lazyLoading: true,
  virtualScrolling: false,
  imageOptimization: true,
  codeSplitting: true,
  preloading: true,
  caching: {
    enabled: true,
    strategy: 'localStorage',
    maxSize: 50 * 1024 * 1024, // 50MB
  },
  monitoring: {
    enabled: true,
    sampleRate: 0.1, // 10%
    trackErrors: true,
    trackPerformance: true,
    trackUserActions: false,
  },
  optimization: {
    debounceDelay: 300,
    throttleDelay: 100,
    batchUpdates: true,
    memoization: true,
  },
};

const DEFAULT_SECURITY_CONFIG: SecurityConfig = {
  csrfProtection: true,
  xssProtection: true,
  contentSecurityPolicy: true,
  secureHeaders: true,
  sessionTimeout: 3600, // 1 hora
  maxLoginAttempts: 5,
  passwordPolicy: {
    minLength: 8,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecialChars: false,
  },
  twoFactorAuth: {
    enabled: false,
    method: 'app',
  },
};

// Função para validar configuração
const validateConfig = (config: any): boolean => {
  try {
    // Validações básicas
    if (!config.api?.baseUrl) return false;
    if (config.api.timeout < 1000) return false;
    if (config.ui.theme && !['light', 'dark', 'auto'].includes(config.ui.theme)) return false;
    if (config.performance.caching.maxSize < 1024 * 1024) return false; // Mínimo 1MB
    
    return true;
  } catch {
    return false;
  }
};

// Função para obter valor por path
const getValueByPath = (obj: any, path: string): any => {
  return path.split('.').reduce((current, key) => current?.[key], obj);
};

// Função para definir valor por path
const setValueByPath = (obj: any, path: string, value: any): void => {
  const keys = path.split('.');
  const lastKey = keys.pop()!;
  const target = keys.reduce((current, key) => {
    if (!current[key]) current[key] = {};
    return current[key];
  }, obj);
  target[lastKey] = value;
};

export const useConfigStore = create<ConfigState>()(
  devtools(
    subscribeWithSelector(
      persist(
        (set, get) => ({
          api: DEFAULT_API_CONFIG,
          ui: DEFAULT_UI_CONFIG,
          performance: DEFAULT_PERFORMANCE_CONFIG,
          security: DEFAULT_SECURITY_CONFIG,
          featureFlags: {},
          isLoaded: false,
          isSyncing: false,
          lastSync: null,
          version: '1.0.0',

          // Actions
          updateApiConfig: (config: Partial<ApiConfig>) => {
            set((state) => ({
              api: { ...state.api, ...config },
            }));
          },

          updateUIConfig: (config: Partial<UIConfig>) => {
            set((state) => ({
              ui: { ...state.ui, ...config },
            }));
          },

          updatePerformanceConfig: (config: Partial<PerformanceConfig>) => {
            set((state) => ({
              performance: { ...state.performance, ...config },
            }));
          },

          updateSecurityConfig: (config: Partial<SecurityConfig>) => {
            set((state) => ({
              security: { ...state.security, ...config },
            }));
          },

          updateFeatureFlags: (flags: Partial<FeatureFlags>) => {
            set((state) => ({
              featureFlags: { ...state.featureFlags, ...flags },
            }));
          },

          // Sincronização
          syncWithBackend: async () => {
            const state = get();
            if (state.isSyncing) return;

            set({ isSyncing: true });

            try {
              // Carregar configurações do backend
              const response = await ApiClient.get('/api/config');
              const backendConfig = response.data;

              // Mesclar com configurações locais
              set((state) => ({
                api: { ...state.api, ...backendConfig.api },
                ui: { ...state.ui, ...backendConfig.ui },
                performance: { ...state.performance, ...backendConfig.performance },
                security: { ...state.security, ...backendConfig.security },
                featureFlags: { ...state.featureFlags, ...backendConfig.featureFlags },
                lastSync: Date.now(),
                isLoaded: true,
              }));

              // Salvar configurações mescladas no backend
              await get().saveToBackend();

            } catch (error) {
              console.error('Erro ao sincronizar configurações:', error);
            } finally {
              set({ isSyncing: false });
            }
          },

          loadFromBackend: async () => {
            const state = get();
            if (state.isSyncing) return;

            set({ isSyncing: true });

            try {
              const response = await ApiClient.get('/api/config');
              const backendConfig = response.data;

              if (validateConfig(backendConfig)) {
                set((state) => ({
                  api: { ...state.api, ...backendConfig.api },
                  ui: { ...state.ui, ...backendConfig.ui },
                  performance: { ...state.performance, ...backendConfig.performance },
                  security: { ...state.security, ...backendConfig.security },
                  featureFlags: { ...state.featureFlags, ...backendConfig.featureFlags },
                  lastSync: Date.now(),
                  isLoaded: true,
                }));
              }
            } catch (error) {
              console.error('Erro ao carregar configurações do backend:', error);
              set({ isLoaded: true }); // Marcar como carregado mesmo com erro
            } finally {
              set({ isSyncing: false });
            }
          },

          saveToBackend: async () => {
            const state = get();
            if (state.isSyncing) return;

            set({ isSyncing: true });

            try {
              const config = {
                api: state.api,
                ui: state.ui,
                performance: state.performance,
                security: state.security,
                featureFlags: state.featureFlags,
                version: state.version,
              };

              await ApiClient.post('/api/config', config);
              set({ lastSync: Date.now() });
            } catch (error) {
              console.error('Erro ao salvar configurações no backend:', error);
            } finally {
              set({ isSyncing: false });
            }
          },

          // Utilitários
          resetToDefaults: () => {
            set({
              api: DEFAULT_API_CONFIG,
              ui: DEFAULT_UI_CONFIG,
              performance: DEFAULT_PERFORMANCE_CONFIG,
              security: DEFAULT_SECURITY_CONFIG,
              featureFlags: {},
              lastSync: null,
            });
          },

          exportConfig: () => {
            const state = get();
            return JSON.stringify({
              api: state.api,
              ui: state.ui,
              performance: state.performance,
              security: state.security,
              featureFlags: state.featureFlags,
              version: state.version,
            }, null, 2);
          },

          importConfig: (configStr: string): boolean => {
            try {
              const config = JSON.parse(configStr);
              
              if (!validateConfig(config)) {
                return false;
              }

              set((state) => ({
                api: { ...state.api, ...config.api },
                ui: { ...state.ui, ...config.ui },
                performance: { ...state.performance, ...config.performance },
                security: { ...state.security, ...config.security },
                featureFlags: { ...state.featureFlags, ...config.featureFlags },
                version: config.version || state.version,
              }));

              return true;
            } catch {
              return false;
            }
          },

          validateConfig: () => {
            const state = get();
            return validateConfig(state);
          },

          getConfigValue: <T>(path: string): T | undefined => {
            const state = get();
            return getValueByPath(state, path);
          },

          setConfigValue: <T>(path: string, value: T) => {
            set((state) => {
              const newState = { ...state };
              setValueByPath(newState, path, value);
              return newState;
            });
          },
        }),
        {
          name: 'config-store',
          storage: createJSONStorage(() => localStorage),
          partialize: (state) => ({
            api: state.api,
            ui: state.ui,
            performance: state.performance,
            security: state.security,
            featureFlags: state.featureFlags,
            version: state.version,
          }),
          onRehydrateStorage: () => (state) => {
            if (state) {
              state.isLoaded = true;
            }
          },
        }
      )
    ),
    {
      name: 'config-store',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);

// Hooks utilitários
export const useApiConfig = () => {
  const store = useConfigStore();
  return {
    config: store.api,
    updateConfig: store.updateApiConfig,
  };
};

export const useUIConfig = () => {
  const store = useConfigStore();
  return {
    config: store.ui,
    updateConfig: store.updateUIConfig,
  };
};

export const usePerformanceConfig = () => {
  const store = useConfigStore();
  return {
    config: store.performance,
    updateConfig: store.updatePerformanceConfig,
  };
};

export const useSecurityConfig = () => {
  const store = useConfigStore();
  return {
    config: store.security,
    updateConfig: store.updateSecurityConfig,
  };
};

export const useFeatureFlags = () => {
  const store = useConfigStore();
  return {
    flags: store.featureFlags,
    updateFlags: store.updateFeatureFlags,
    isEnabled: (flag: string) => store.featureFlags[flag] || false,
  };
};

export const useConfigSync = () => {
  const store = useConfigStore();
  return {
    isSyncing: store.isSyncing,
    lastSync: store.lastSync,
    syncWithBackend: store.syncWithBackend,
    loadFromBackend: store.loadFromBackend,
    saveToBackend: store.saveToBackend,
  };
};

// Auto-sync na inicialização
if (typeof window !== 'undefined') {
  // Carregar configurações do backend na inicialização
  setTimeout(() => {
    useConfigStore.getState().loadFromBackend();
  }, 1000);
}

export default useConfigStore; 