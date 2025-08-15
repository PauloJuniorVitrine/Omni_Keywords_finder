/**
 * AppStore.tsx
 * 
 * Store centralizado para gerenciamento de estado global
 * 
 * Tracing ID: APP_STORE_001_20250127
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 17.1
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Store centralizado
 * - Persistência de estado
 * - Sincronização entre componentes
 * - DevTools integration
 * - Middleware para logging e analytics
 */

import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import { persist, createJSONStorage } from 'zustand/middleware';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { shallow } from 'zustand/shallow';

// Tipos para o estado global
interface AppState {
  // Estado de autenticação
  auth: {
    isAuthenticated: boolean;
    user: User | null;
    token: string | null;
    permissions: string[];
    roles: string[];
  };

  // Estado de UI
  ui: {
    theme: 'light' | 'dark';
    sidebarCollapsed: boolean;
    notifications: Notification[];
    breadcrumbs: Breadcrumb[];
    loadingStates: Record<string, boolean>;
    errorStates: Record<string, string | null>;
  };

  // Estado de dados
  data: {
    nichos: Nicho[];
    categorias: Categoria[];
    execucoes: Execucao[];
    webhooks: Webhook[];
    templates: Template[];
    credentials: Credential[];
    analytics: AnalyticsData;
  };

  // Estado de cache
  cache: {
    queries: Record<string, any>;
    lastUpdated: Record<string, string>;
    ttl: Record<string, number>;
  };

  // Estado de configurações
  config: {
    apiBaseUrl: string;
    environment: string;
    version: string;
    features: Record<string, boolean>;
  };
}

// Interfaces para os tipos de dados
interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  avatar?: string;
  lastLogin?: string;
}

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actions?: NotificationAction[];
}

interface NotificationAction {
  label: string;
  action: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
}

interface Breadcrumb {
  label: string;
  path: string;
  active?: boolean;
}

interface Nicho {
  id: string;
  nome: string;
  descricao: string;
  status: 'ativo' | 'inativo';
  createdAt: string;
  updatedAt: string;
}

interface Categoria {
  id: string;
  nome: string;
  nichoId: string;
  parentId?: string;
  status: 'ativo' | 'inativo';
  createdAt: string;
  updatedAt: string;
}

interface Execucao {
  id: string;
  nome: string;
  categoriaId: string;
  status: 'pendente' | 'executando' | 'concluida' | 'erro';
  progress: number;
  createdAt: string;
  updatedAt: string;
}

interface Webhook {
  id: string;
  url: string;
  events: string[];
  status: 'ativo' | 'inativo';
  lastTriggered?: string;
  createdAt: string;
  updatedAt: string;
}

interface Template {
  id: string;
  nome: string;
  conteudo: string;
  tipo: string;
  version: number;
  createdAt: string;
  updatedAt: string;
}

interface Credential {
  id: string;
  nome: string;
  tipo: string;
  encrypted: boolean;
  lastUsed?: string;
  createdAt: string;
  updatedAt: string;
}

interface AnalyticsData {
  totalNichos: number;
  totalCategorias: number;
  totalExecucoes: number;
  execucoesHoje: number;
  taxaSucesso: number;
  tempoMedioExecucao: number;
}

// Ações para o reducer
type AppAction =
  | { type: 'SET_AUTH'; payload: Partial<AppState['auth']> }
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_TOKEN'; payload: string | null }
  | { type: 'SET_PERMISSIONS'; payload: string[] }
  | { type: 'SET_THEME'; payload: 'light' | 'dark' }
  | { type: 'TOGGLE_SIDEBAR' }
  | { type: 'ADD_NOTIFICATION'; payload: Omit<Notification, 'id' | 'timestamp' | 'read'> }
  | { type: 'REMOVE_NOTIFICATION'; payload: string }
  | { type: 'MARK_NOTIFICATION_READ'; payload: string }
  | { type: 'SET_BREADCRUMBS'; payload: Breadcrumb[] }
  | { type: 'SET_LOADING'; payload: { key: string; loading: boolean } }
  | { type: 'SET_ERROR'; payload: { key: string; error: string | null } }
  | { type: 'SET_NICHOS'; payload: Nicho[] }
  | { type: 'ADD_NICHO'; payload: Nicho }
  | { type: 'UPDATE_NICHO'; payload: Nicho }
  | { type: 'REMOVE_NICHO'; payload: string }
  | { type: 'SET_CATEGORIAS'; payload: Categoria[] }
  | { type: 'ADD_CATEGORIA'; payload: Categoria }
  | { type: 'UPDATE_CATEGORIA'; payload: Categoria }
  | { type: 'REMOVE_CATEGORIA'; payload: string }
  | { type: 'SET_EXECUCOES'; payload: Execucao[] }
  | { type: 'ADD_EXECUCAO'; payload: Execucao }
  | { type: 'UPDATE_EXECUCAO'; payload: Execucao }
  | { type: 'REMOVE_EXECUCAO'; payload: string }
  | { type: 'SET_WEBHOOKS'; payload: Webhook[] }
  | { type: 'ADD_WEBHOOK'; payload: Webhook }
  | { type: 'UPDATE_WEBHOOK'; payload: Webhook }
  | { type: 'REMOVE_WEBHOOK'; payload: string }
  | { type: 'SET_TEMPLATES'; payload: Template[] }
  | { type: 'ADD_TEMPLATE'; payload: Template }
  | { type: 'UPDATE_TEMPLATE'; payload: Template }
  | { type: 'REMOVE_TEMPLATE'; payload: string }
  | { type: 'SET_CREDENTIALS'; payload: Credential[] }
  | { type: 'ADD_CREDENTIAL'; payload: Credential }
  | { type: 'UPDATE_CREDENTIAL'; payload: Credential }
  | { type: 'REMOVE_CREDENTIAL'; payload: string }
  | { type: 'SET_ANALYTICS'; payload: AnalyticsData }
  | { type: 'SET_CACHE'; payload: { key: string; data: any; ttl?: number } }
  | { type: 'CLEAR_CACHE'; payload?: string }
  | { type: 'SET_CONFIG'; payload: Partial<AppState['config']> }
  | { type: 'RESET_STATE' };

// Estado inicial
const initialState: AppState = {
  auth: {
    isAuthenticated: false,
    user: null,
    token: null,
    permissions: [],
    roles: []
  },
  ui: {
    theme: 'light',
    sidebarCollapsed: false,
    notifications: [],
    breadcrumbs: [],
    loadingStates: {},
    errorStates: {}
  },
  data: {
    nichos: [],
    categorias: [],
    execucoes: [],
    webhooks: [],
    templates: [],
    credentials: [],
    analytics: {
      totalNichos: 0,
      totalCategorias: 0,
      totalExecucoes: 0,
      execucoesHoje: 0,
      taxaSucesso: 0,
      tempoMedioExecucao: 0
    }
  },
  cache: {
    queries: {},
    lastUpdated: {},
    ttl: {}
  },
  config: {
    apiBaseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    environment: process.env.NODE_ENV || 'development',
    version: process.env.REACT_APP_VERSION || '1.0.0',
    features: {}
  }
};

// Função reducer
const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'SET_AUTH':
      return {
        ...state,
        auth: { ...state.auth, ...action.payload }
      };

    case 'SET_USER':
      return {
        ...state,
        auth: { ...state.auth, user: action.payload }
      };

    case 'SET_TOKEN':
      return {
        ...state,
        auth: { ...state.auth, token: action.payload }
      };

    case 'SET_PERMISSIONS':
      return {
        ...state,
        auth: { ...state.auth, permissions: action.payload }
      };

    case 'SET_THEME':
      return {
        ...state,
        ui: { ...state.ui, theme: action.payload }
      };

    case 'TOGGLE_SIDEBAR':
      return {
        ...state,
        ui: { ...state.ui, sidebarCollapsed: !state.ui.sidebarCollapsed }
      };

    case 'ADD_NOTIFICATION':
      const newNotification: Notification = {
        ...action.payload,
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        read: false
      };
      return {
        ...state,
        ui: {
          ...state.ui,
          notifications: [...state.ui.notifications, newNotification]
        }
      };

    case 'REMOVE_NOTIFICATION':
      return {
        ...state,
        ui: {
          ...state.ui,
          notifications: state.ui.notifications.filter(n => n.id !== action.payload)
        }
      };

    case 'MARK_NOTIFICATION_READ':
      return {
        ...state,
        ui: {
          ...state.ui,
          notifications: state.ui.notifications.map(n =>
            n.id === action.payload ? { ...n, read: true } : n
          )
        }
      };

    case 'SET_BREADCRUMBS':
      return {
        ...state,
        ui: { ...state.ui, breadcrumbs: action.payload }
      };

    case 'SET_LOADING':
      return {
        ...state,
        ui: {
          ...state.ui,
          loadingStates: {
            ...state.ui.loadingStates,
            [action.payload.key]: action.payload.loading
          }
        }
      };

    case 'SET_ERROR':
      return {
        ...state,
        ui: {
          ...state.ui,
          errorStates: {
            ...state.ui.errorStates,
            [action.payload.key]: action.payload.error
          }
        }
      };

    case 'SET_NICHOS':
      return {
        ...state,
        data: { ...state.data, nichos: action.payload }
      };

    case 'ADD_NICHO':
      return {
        ...state,
        data: { ...state.data, nichos: [...state.data.nichos, action.payload] }
      };

    case 'UPDATE_NICHO':
      return {
        ...state,
        data: {
          ...state.data,
          nichos: state.data.nichos.map(n =>
            n.id === action.payload.id ? action.payload : n
          )
        }
      };

    case 'REMOVE_NICHO':
      return {
        ...state,
        data: {
          ...state.data,
          nichos: state.data.nichos.filter(n => n.id !== action.payload)
        }
      };

    case 'SET_CATEGORIAS':
      return {
        ...state,
        data: { ...state.data, categorias: action.payload }
      };

    case 'ADD_CATEGORIA':
      return {
        ...state,
        data: { ...state.data, categorias: [...state.data.categorias, action.payload] }
      };

    case 'UPDATE_CATEGORIA':
      return {
        ...state,
        data: {
          ...state.data,
          categorias: state.data.categorias.map(c =>
            c.id === action.payload.id ? action.payload : c
          )
        }
      };

    case 'REMOVE_CATEGORIA':
      return {
        ...state,
        data: {
          ...state.data,
          categorias: state.data.categorias.filter(c => c.id !== action.payload)
        }
      };

    case 'SET_EXECUCOES':
      return {
        ...state,
        data: { ...state.data, execucoes: action.payload }
      };

    case 'ADD_EXECUCAO':
      return {
        ...state,
        data: { ...state.data, execucoes: [...state.data.execucoes, action.payload] }
      };

    case 'UPDATE_EXECUCAO':
      return {
        ...state,
        data: {
          ...state.data,
          execucoes: state.data.execucoes.map(e =>
            e.id === action.payload.id ? action.payload : e
          )
        }
      };

    case 'REMOVE_EXECUCAO':
      return {
        ...state,
        data: {
          ...state.data,
          execucoes: state.data.execucoes.filter(e => e.id !== action.payload)
        }
      };

    case 'SET_WEBHOOKS':
      return {
        ...state,
        data: { ...state.data, webhooks: action.payload }
      };

    case 'ADD_WEBHOOK':
      return {
        ...state,
        data: { ...state.data, webhooks: [...state.data.webhooks, action.payload] }
      };

    case 'UPDATE_WEBHOOK':
      return {
        ...state,
        data: {
          ...state.data,
          webhooks: state.data.webhooks.map(w =>
            w.id === action.payload.id ? action.payload : w
          )
        }
      };

    case 'REMOVE_WEBHOOK':
      return {
        ...state,
        data: {
          ...state.data,
          webhooks: state.data.webhooks.filter(w => w.id !== action.payload)
        }
      };

    case 'SET_TEMPLATES':
      return {
        ...state,
        data: { ...state.data, templates: action.payload }
      };

    case 'ADD_TEMPLATE':
      return {
        ...state,
        data: { ...state.data, templates: [...state.data.templates, action.payload] }
      };

    case 'UPDATE_TEMPLATE':
      return {
        ...state,
        data: {
          ...state.data,
          templates: state.data.templates.map(t =>
            t.id === action.payload.id ? action.payload : t
          )
        }
      };

    case 'REMOVE_TEMPLATE':
      return {
        ...state,
        data: {
          ...state.data,
          templates: state.data.templates.filter(t => t.id !== action.payload)
        }
      };

    case 'SET_CREDENTIALS':
      return {
        ...state,
        data: { ...state.data, credentials: action.payload }
      };

    case 'ADD_CREDENTIAL':
      return {
        ...state,
        data: { ...state.data, credentials: [...state.data.credentials, action.payload] }
      };

    case 'UPDATE_CREDENTIAL':
      return {
        ...state,
        data: {
          ...state.data,
          credentials: state.data.credentials.map(c =>
            c.id === action.payload.id ? action.payload : c
          )
        }
      };

    case 'REMOVE_CREDENTIAL':
      return {
        ...state,
        data: {
          ...state.data,
          credentials: state.data.credentials.filter(c => c.id !== action.payload)
        }
      };

    case 'SET_ANALYTICS':
      return {
        ...state,
        data: { ...state.data, analytics: action.payload }
      };

    case 'SET_CACHE':
      const ttl = action.payload.ttl || 5 * 60 * 1000; // 5 minutos padrão
      return {
        ...state,
        cache: {
          ...state.cache,
          queries: { ...state.cache.queries, [action.payload.key]: action.payload.data },
          lastUpdated: { ...state.cache.lastUpdated, [action.payload.key]: new Date().toISOString() },
          ttl: { ...state.cache.ttl, [action.payload.key]: ttl }
        }
      };

    case 'CLEAR_CACHE':
      if (action.payload) {
        const { [action.payload]: removed, ...remainingQueries } = state.cache.queries;
        const { [action.payload]: removedUpdated, ...remainingUpdated } = state.cache.lastUpdated;
        const { [action.payload]: removedTtl, ...remainingTtl } = state.cache.ttl;
        
        return {
          ...state,
          cache: {
            queries: remainingQueries,
            lastUpdated: remainingUpdated,
            ttl: remainingTtl
          }
        };
      }
      return {
        ...state,
        cache: { queries: {}, lastUpdated: {}, ttl: {} }
      };

    case 'SET_CONFIG':
      return {
        ...state,
        config: { ...state.config, ...action.payload }
      };

    case 'RESET_STATE':
      return initialState;

    default:
      return state;
  }
};

// Context para o store
interface AppStoreContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
  actions: {
    setAuth: (auth: Partial<AppState['auth']>) => void;
    setUser: (user: User | null) => void;
    setToken: (token: string | null) => void;
    setPermissions: (permissions: string[]) => void;
    setTheme: (theme: 'light' | 'dark') => void;
    toggleSidebar: () => void;
    addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
    removeNotification: (id: string) => void;
    markNotificationRead: (id: string) => void;
    setBreadcrumbs: (breadcrumbs: Breadcrumb[]) => void;
    setLoading: (key: string, loading: boolean) => void;
    setError: (key: string, error: string | null) => void;
    setNichos: (nichos: Nicho[]) => void;
    addNicho: (nicho: Nicho) => void;
    updateNicho: (nicho: Nicho) => void;
    removeNicho: (id: string) => void;
    setCategorias: (categorias: Categoria[]) => void;
    addCategoria: (categoria: Categoria) => void;
    updateCategoria: (categoria: Categoria) => void;
    removeCategoria: (id: string) => void;
    setExecucoes: (execucoes: Execucao[]) => void;
    addExecucao: (execucao: Execucao) => void;
    updateExecucao: (execucao: Execucao) => void;
    removeExecucao: (id: string) => void;
    setWebhooks: (webhooks: Webhook[]) => void;
    addWebhook: (webhook: Webhook) => void;
    updateWebhook: (webhook: Webhook) => void;
    removeWebhook: (id: string) => void;
    setTemplates: (templates: Template[]) => void;
    addTemplate: (template: Template) => void;
    updateTemplate: (template: Template) => void;
    removeTemplate: (id: string) => void;
    setCredentials: (credentials: Credential[]) => void;
    addCredential: (credential: Credential) => void;
    updateCredential: (credential: Credential) => void;
    removeCredential: (id: string) => void;
    setAnalytics: (analytics: AnalyticsData) => void;
    setCache: (key: string, data: any, ttl?: number) => void;
    clearCache: (key?: string) => void;
    setConfig: (config: Partial<AppState['config']>) => void;
    resetState: () => void;
  };
}

const AppStoreContext = createContext<AppStoreContextType | undefined>(undefined);

// Provider do store
export const AppStoreProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Middleware para logging
  useEffect(() => {
    // console.log('[AppStore] State updated:', state); // Removido para produção
  }, [state]);

  // Middleware para persistência
  useEffect(() => {
    const persistState = () => {
      try {
        const stateToPersist = {
          auth: state.auth,
          ui: {
            theme: state.ui.theme,
            sidebarCollapsed: state.ui.sidebarCollapsed
          },
          config: state.config
        };
        localStorage.setItem('appState', JSON.stringify(stateToPersist));
      } catch (error) {
        console.error('[AppStore] Error persisting state:', error);
      }
    };

    persistState();
  }, [state.auth, state.ui.theme, state.ui.sidebarCollapsed, state.config]);

  // Carregar estado persistido
  useEffect(() => {
    try {
      const persistedState = localStorage.getItem('appState');
      if (persistedState) {
        const parsedState = JSON.parse(persistedState);
        dispatch({ type: 'SET_AUTH', payload: parsedState.auth });
        dispatch({ type: 'SET_THEME', payload: parsedState.ui.theme });
        // Não restaurar sidebarCollapsed para manter UX consistente
        dispatch({ type: 'SET_CONFIG', payload: parsedState.config });
      }
    } catch (error) {
      console.error('[AppStore] Error loading persisted state:', error);
    }
  }, []);

  // Actions helpers
  const actions = {
    setAuth: useCallback((auth: Partial<AppState['auth']>) => {
      dispatch({ type: 'SET_AUTH', payload: auth });
    }, []),

    setUser: useCallback((user: User | null) => {
      dispatch({ type: 'SET_USER', payload: user });
    }, []),

    setToken: useCallback((token: string | null) => {
      dispatch({ type: 'SET_TOKEN', payload: token });
    }, []),

    setPermissions: useCallback((permissions: string[]) => {
      dispatch({ type: 'SET_PERMISSIONS', payload: permissions });
    }, []),

    setTheme: useCallback((theme: 'light' | 'dark') => {
      dispatch({ type: 'SET_THEME', payload: theme });
    }, []),

    toggleSidebar: useCallback(() => {
      dispatch({ type: 'TOGGLE_SIDEBAR' });
    }, []),

    addNotification: useCallback((notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
      dispatch({ type: 'ADD_NOTIFICATION', payload: notification });
    }, []),

    removeNotification: useCallback((id: string) => {
      dispatch({ type: 'REMOVE_NOTIFICATION', payload: id });
    }, []),

    markNotificationRead: useCallback((id: string) => {
      dispatch({ type: 'MARK_NOTIFICATION_READ', payload: id });
    }, []),

    setBreadcrumbs: useCallback((breadcrumbs: Breadcrumb[]) => {
      dispatch({ type: 'SET_BREADCRUMBS', payload: breadcrumbs });
    }, []),

    setLoading: useCallback((key: string, loading: boolean) => {
      dispatch({ type: 'SET_LOADING', payload: { key, loading } });
    }, []),

    setError: useCallback((key: string, error: string | null) => {
      dispatch({ type: 'SET_ERROR', payload: { key, error } });
    }, []),

    setNichos: useCallback((nichos: Nicho[]) => {
      dispatch({ type: 'SET_NICHOS', payload: nichos });
    }, []),

    addNicho: useCallback((nicho: Nicho) => {
      dispatch({ type: 'ADD_NICHO', payload: nicho });
    }, []),

    updateNicho: useCallback((nicho: Nicho) => {
      dispatch({ type: 'UPDATE_NICHO', payload: nicho });
    }, []),

    removeNicho: useCallback((id: string) => {
      dispatch({ type: 'REMOVE_NICHO', payload: id });
    }, []),

    setCategorias: useCallback((categorias: Categoria[]) => {
      dispatch({ type: 'SET_CATEGORIAS', payload: categorias });
    }, []),

    addCategoria: useCallback((categoria: Categoria) => {
      dispatch({ type: 'ADD_CATEGORIA', payload: categoria });
    }, []),

    updateCategoria: useCallback((categoria: Categoria) => {
      dispatch({ type: 'UPDATE_CATEGORIA', payload: categoria });
    }, []),

    removeCategoria: useCallback((id: string) => {
      dispatch({ type: 'REMOVE_CATEGORIA', payload: id });
    }, []),

    setExecucoes: useCallback((execucoes: Execucao[]) => {
      dispatch({ type: 'SET_EXECUCOES', payload: execucoes });
    }, []),

    addExecucao: useCallback((execucao: Execucao) => {
      dispatch({ type: 'ADD_EXECUCAO', payload: execucao });
    }, []),

    updateExecucao: useCallback((execucao: Execucao) => {
      dispatch({ type: 'UPDATE_EXECUCAO', payload: execucao });
    }, []),

    removeExecucao: useCallback((id: string) => {
      dispatch({ type: 'REMOVE_EXECUCAO', payload: id });
    }, []),

    setWebhooks: useCallback((webhooks: Webhook[]) => {
      dispatch({ type: 'SET_WEBHOOKS', payload: webhooks });
    }, []),

    addWebhook: useCallback((webhook: Webhook) => {
      dispatch({ type: 'ADD_WEBHOOK', payload: webhook });
    }, []),

    updateWebhook: useCallback((webhook: Webhook) => {
      dispatch({ type: 'UPDATE_WEBHOOK', payload: webhook });
    }, []),

    removeWebhook: useCallback((id: string) => {
      dispatch({ type: 'REMOVE_WEBHOOK', payload: id });
    }, []),

    setTemplates: useCallback((templates: Template[]) => {
      dispatch({ type: 'SET_TEMPLATES', payload: templates });
    }, []),

    addTemplate: useCallback((template: Template) => {
      dispatch({ type: 'ADD_TEMPLATE', payload: template });
    }, []),

    updateTemplate: useCallback((template: Template) => {
      dispatch({ type: 'UPDATE_TEMPLATE', payload: template });
    }, []),

    removeTemplate: useCallback((id: string) => {
      dispatch({ type: 'REMOVE_TEMPLATE', payload: id });
    }, []),

    setCredentials: useCallback((credentials: Credential[]) => {
      dispatch({ type: 'SET_CREDENTIALS', payload: credentials });
    }, []),

    addCredential: useCallback((credential: Credential) => {
      dispatch({ type: 'ADD_CREDENTIAL', payload: credential });
    }, []),

    updateCredential: useCallback((credential: Credential) => {
      dispatch({ type: 'UPDATE_CREDENTIAL', payload: credential });
    }, []),

    removeCredential: useCallback((id: string) => {
      dispatch({ type: 'REMOVE_CREDENTIAL', payload: id });
    }, []),

    setAnalytics: useCallback((analytics: AnalyticsData) => {
      dispatch({ type: 'SET_ANALYTICS', payload: analytics });
    }, []),

    setCache: useCallback((key: string, data: any, ttl?: number) => {
      dispatch({ type: 'SET_CACHE', payload: { key, data, ttl } });
    }, []),

    clearCache: useCallback((key?: string) => {
      dispatch({ type: 'CLEAR_CACHE', payload: key });
    }, []),

    setConfig: useCallback((config: Partial<AppState['config']>) => {
      dispatch({ type: 'SET_CONFIG', payload: config });
    }, []),

    resetState: useCallback(() => {
      dispatch({ type: 'RESET_STATE' });
    }, [])
  };

  const value: AppStoreContextType = {
    state,
    dispatch,
    actions
  };

  return (
    <AppStoreContext.Provider value={value}>
      {children}
    </AppStoreContext.Provider>
  );
};

// Hook para usar o store
export const useAppStore = () => {
  const context = useContext(AppStoreContext);
  if (context === undefined) {
    throw new Error('useAppStore must be used within an AppStoreProvider');
  }
  return context;
};

// Hook para seletores otimizados
export const useAppSelector = <T>(selector: (state: AppState) => T, equalityFn?: (a: T, b: T) => boolean): T => {
  const { state } = useAppStore();
  return React.useMemo(() => selector(state), [state, selector]);
};

// Hook para dispatch
export const useAppDispatch = () => {
  const { dispatch } = useAppStore();
  return dispatch;
};

// Hook para actions
export const useAppActions = () => {
  const { actions } = useAppStore();
  return actions;
};

export default AppStoreProvider; 