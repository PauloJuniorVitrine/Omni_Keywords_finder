/**
 * session-store.ts
 * 
 * Store para gerenciamento de sessão do usuário
 * 
 * Tracing ID: STORE-SESSION-001
 * Data: 2025-01-27
 * Versão: 1.0
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 4.5
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Gerenciamento de sessão
 * - Sincronização com backend
 * - Persistência seletiva
 * - Timeout automático
 * - Multi-tab sync
 * - Activity tracking
 * - Session recovery
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { User } from '../shared/types/api';

// Tipos
interface SessionData {
  id: string;
  userId: string;
  user: User;
  token: string;
  refreshToken: string;
  createdAt: number;
  lastActivity: number;
  expiresAt: number;
  ipAddress?: string;
  userAgent: string;
  deviceId: string;
  isActive: boolean;
  permissions: string[];
  roles: string[];
  metadata: Record<string, any>;
}

interface SessionActivity {
  timestamp: number;
  action: string;
  component?: string;
  url?: string;
  metadata?: Record<string, any>;
}

interface SessionState {
  // Dados da sessão
  session: SessionData | null;
  
  // Atividades da sessão
  activities: SessionActivity[];
  
  // Configurações
  config: {
    sessionTimeout: number; // segundos
    activityTracking: boolean;
    maxActivities: number;
    autoRefresh: boolean;
    refreshThreshold: number; // segundos antes da expiração
    multiTabSync: boolean;
    persistSession: boolean;
  };
  
  // Estado
  isAuthenticated: boolean;
  isLoading: boolean;
  isRefreshing: boolean;
  lastSync: number | null;
  
  // Actions
  setSession: (session: SessionData) => void;
  clearSession: () => void;
  updateSession: (updates: Partial<SessionData>) => void;
  refreshSession: () => Promise<boolean>;
  extendSession: (duration?: number) => void;
  
  // Atividades
  trackActivity: (action: string, metadata?: Record<string, any>) => void;
  clearActivities: () => void;
  getActivities: (since?: number) => SessionActivity[];
  
  // Sincronização
  syncWithBackend: () => Promise<void>;
  loadFromStorage: () => void;
  saveToStorage: () => void;
  
  // Utilitários
  isSessionExpired: () => boolean;
  isSessionExpiringSoon: () => boolean;
  getSessionDuration: () => number;
  getRemainingTime: () => number;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: string) => boolean;
  getSessionInfo: () => SessionData | null;
}

// Configurações padrão
const SESSION_CONFIG = {
  sessionTimeout: 3600, // 1 hora
  activityTracking: true,
  maxActivities: 100,
  autoRefresh: true,
  refreshThreshold: 300, // 5 minutos
  multiTabSync: true,
  persistSession: true,
};

// Função para gerar device ID
const generateDeviceId = (): string => {
  const stored = localStorage.getItem('deviceId');
  if (stored) return stored;
  
  const deviceId = `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  localStorage.setItem('deviceId', deviceId);
  return deviceId;
};

// Função para obter IP address (mock)
const getIpAddress = (): string => {
  // Em produção, isso seria obtido do backend
  return '127.0.0.1';
};

// Função para verificar se sessão expirou
const isSessionExpired = (session: SessionData): boolean => {
  return Date.now() > session.expiresAt;
};

// Função para verificar se sessão está expirando em breve
const isSessionExpiringSoon = (session: SessionData, threshold: number): boolean => {
  return session.expiresAt - Date.now() < threshold * 1000;
};

export const useSessionStore = create<SessionState>()(
  devtools(
    subscribeWithSelector(
      persist(
        (set, get) => ({
          session: null,
          activities: [],
          config: SESSION_CONFIG,
          isAuthenticated: false,
          isLoading: false,
          isRefreshing: false,
          lastSync: null,

          // Actions
          setSession: (session: SessionData) => {
            set({
              session,
              isAuthenticated: true,
              lastSync: Date.now(),
            });

            // Configurar auto-refresh se habilitado
            if (SESSION_CONFIG.autoRefresh) {
              const checkExpiration = () => {
                const currentSession = get().session;
                if (currentSession && isSessionExpiringSoon(currentSession, SESSION_CONFIG.refreshThreshold)) {
                  get().refreshSession();
                }
              };

              // Verificar a cada minuto
              setInterval(checkExpiration, 60000);
            }

            // Configurar multi-tab sync
            if (SESSION_CONFIG.multiTabSync) {
              window.addEventListener('storage', (event) => {
                if (event.key === 'session-update' && event.newValue) {
                  const updatedSession = JSON.parse(event.newValue);
                  set({ session: updatedSession });
                }
              });
            }
          },

          clearSession: () => {
            set({
              session: null,
              activities: [],
              isAuthenticated: false,
              isLoading: false,
              isRefreshing: false,
              lastSync: null,
            });

            // Notificar outras abas
            if (SESSION_CONFIG.multiTabSync) {
              localStorage.setItem('session-clear', Date.now().toString());
            }
          },

          updateSession: (updates: Partial<SessionData>) => {
            set((state) => {
              if (!state.session) return state;

              const updatedSession = { ...state.session, ...updates };
              
              // Notificar outras abas
              if (SESSION_CONFIG.multiTabSync) {
                localStorage.setItem('session-update', JSON.stringify(updatedSession));
              }

              return { session: updatedSession };
            });
          },

          refreshSession: async (): Promise<boolean> => {
            const state = get();
            if (!state.session || state.isRefreshing) return false;

            set({ isRefreshing: true });

            try {
              // Aqui seria feita a chamada para o backend para refresh
              // Por enquanto, apenas estendemos a sessão localmente
              const newExpiresAt = Date.now() + (SESSION_CONFIG.sessionTimeout * 1000);
              
              set((state) => ({
                session: state.session ? {
                  ...state.session,
                  expiresAt: newExpiresAt,
                  lastActivity: Date.now(),
                } : null,
                isRefreshing: false,
                lastSync: Date.now(),
              }));

              return true;
            } catch (error) {
              console.error('Erro ao refresh da sessão:', error);
              set({ isRefreshing: false });
              return false;
            }
          },

          extendSession: (duration = SESSION_CONFIG.sessionTimeout) => {
            set((state) => {
              if (!state.session) return state;

              const newExpiresAt = Date.now() + (duration * 1000);
              
              return {
                session: {
                  ...state.session,
                  expiresAt: newExpiresAt,
                  lastActivity: Date.now(),
                },
              };
            });
          },

          // Atividades
          trackActivity: (action: string, metadata?: Record<string, any>) => {
            if (!SESSION_CONFIG.activityTracking) return;

            const activity: SessionActivity = {
              timestamp: Date.now(),
              action,
              component: metadata?.component,
              url: window.location.href,
              metadata,
            };

            set((state) => {
              const newActivities = [...state.activities, activity];
              
              // Limitar número de atividades
              if (newActivities.length > SESSION_CONFIG.maxActivities) {
                newActivities.splice(0, newActivities.length - SESSION_CONFIG.maxActivities);
              }

              return { activities: newActivities };
            });

            // Atualizar lastActivity da sessão
            get().updateSession({ lastActivity: Date.now() });
          },

          clearActivities: () => {
            set({ activities: [] });
          },

          getActivities: (since?: number): SessionActivity[] => {
            const state = get();
            if (!since) return state.activities;
            
            return state.activities.filter(activity => activity.timestamp >= since);
          },

          // Sincronização
          syncWithBackend: async () => {
            const state = get();
            if (state.isLoading) return;

            set({ isLoading: true });

            try {
              // Aqui seria feita a sincronização com o backend
              // Por enquanto, apenas carregamos do storage
              get().loadFromStorage();
              
              set({ lastSync: Date.now() });
            } catch (error) {
              console.error('Erro ao sincronizar sessão:', error);
            } finally {
              set({ isLoading: false });
            }
          },

          loadFromStorage: () => {
            try {
              const stored = localStorage.getItem('session-data');
              if (stored) {
                const sessionData = JSON.parse(stored);
                if (sessionData && !isSessionExpired(sessionData)) {
                  set({
                    session: sessionData,
                    isAuthenticated: true,
                  });
                } else {
                  // Sessão expirada, limpar
                  get().clearSession();
                }
              }
            } catch (error) {
              console.error('Erro ao carregar sessão do storage:', error);
            }
          },

          saveToStorage: () => {
            const state = get();
            if (!state.session || !SESSION_CONFIG.persistSession) return;

            try {
              localStorage.setItem('session-data', JSON.stringify(state.session));
            } catch (error) {
              console.error('Erro ao salvar sessão no storage:', error);
            }
          },

          // Utilitários
          isSessionExpired: (): boolean => {
            const state = get();
            return state.session ? isSessionExpired(state.session) : true;
          },

          isSessionExpiringSoon: (): boolean => {
            const state = get();
            return state.session ? isSessionExpiringSoon(state.session, SESSION_CONFIG.refreshThreshold) : false;
          },

          getSessionDuration: (): number => {
            const state = get();
            if (!state.session) return 0;
            
            return Date.now() - state.session.createdAt;
          },

          getRemainingTime: (): number => {
            const state = get();
            if (!state.session) return 0;
            
            return Math.max(0, state.session.expiresAt - Date.now());
          },

          hasPermission: (permission: string): boolean => {
            const state = get();
            return state.session?.permissions.includes(permission) || false;
          },

          hasRole: (role: string): boolean => {
            const state = get();
            return state.session?.roles.includes(role) || false;
          },

          getSessionInfo: (): SessionData | null => {
            const state = get();
            return state.session;
          },
        }),
        {
          name: 'session-store',
          storage: createJSONStorage(() => localStorage),
          partialize: (state) => ({
            session: state.session,
            activities: state.activities.slice(-50), // Manter apenas últimas 50 atividades
            config: state.config,
          }),
          onRehydrateStorage: () => (state) => {
            if (state) {
              // Verificar se a sessão ainda é válida
              if (state.session && isSessionExpired(state.session)) {
                state.clearSession();
              }
            }
          },
        }
      )
    ),
    {
      name: 'session-store',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);

// Hooks utilitários
export const useSession = () => {
  const store = useSessionStore();
  return {
    session: store.session,
    isAuthenticated: store.isAuthenticated,
    isLoading: store.isLoading,
    isRefreshing: store.isRefreshing,
    setSession: store.setSession,
    clearSession: store.clearSession,
    updateSession: store.updateSession,
    refreshSession: store.refreshSession,
    extendSession: store.extendSession,
  };
};

export const useSessionActivities = () => {
  const store = useSessionStore();
  return {
    activities: store.activities,
    trackActivity: store.trackActivity,
    clearActivities: store.clearActivities,
    getActivities: store.getActivities,
  };
};

export const useSessionUtils = () => {
  const store = useSessionStore();
  return {
    isSessionExpired: store.isSessionExpired,
    isSessionExpiringSoon: store.isSessionExpiringSoon,
    getSessionDuration: store.getSessionDuration,
    getRemainingTime: store.getRemainingTime,
    hasPermission: store.hasPermission,
    hasRole: store.hasRole,
    getSessionInfo: store.getSessionInfo,
  };
};

// Auto-save da sessão
if (typeof window !== 'undefined') {
  setInterval(() => {
    useSessionStore.getState().saveToStorage();
  }, 30000); // A cada 30 segundos
}

// Auto-refresh da sessão
if (typeof window !== 'undefined') {
  setInterval(() => {
    const state = useSessionStore.getState();
    if (state.session && state.isSessionExpiringSoon()) {
      state.refreshSession();
    }
  }, 60000); // A cada minuto
}

export default useSessionStore; 