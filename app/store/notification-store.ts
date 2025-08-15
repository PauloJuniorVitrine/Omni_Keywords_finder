/**
 * notification-store.ts
 * 
 * Store para gerenciamento de notificações
 * 
 * Tracing ID: STORE-NOTIFICATION-001
 * Data: 2025-01-27
 * Versão: 1.0
 * Prompt: COMMUNICATION_BACKEND_FRONTEND_CHECKLIST.md - Item 4.4
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Diferentes tipos de notificação
 * - Prioridades e severidade
 * - Auto-dismiss configurável
 * - Agrupamento de notificações
 * - Ações personalizadas
 * - Persistência seletiva
 * - Som e vibração
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { devtools, subscribeWithSelector } from 'zustand/middleware';

// Tipos
export type NotificationType = 'success' | 'info' | 'warning' | 'error' | 'loading';
export type NotificationPriority = 'low' | 'normal' | 'high' | 'urgent';
export type NotificationPosition = 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';

interface NotificationAction {
  label: string;
  action: () => void;
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  disabled?: boolean;
}

interface NotificationData {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  priority: NotificationPriority;
  position: NotificationPosition;
  timestamp: number;
  duration?: number; // Auto-dismiss em ms, undefined = não auto-dismiss
  dismissed: boolean;
  read: boolean;
  persistent: boolean; // Não é removida automaticamente
  actions?: NotificationAction[];
  metadata?: Record<string, any>;
  groupId?: string; // Para agrupar notificações similares
  progress?: number; // Para notificações de loading
  icon?: string;
  sound?: boolean;
  vibration?: boolean;
}

interface NotificationGroup {
  id: string;
  type: NotificationType;
  title: string;
  count: number;
  notifications: NotificationData[];
  lastNotification: NotificationData;
  collapsed: boolean;
}

interface NotificationState {
  // Notificações ativas
  notifications: Map<string, NotificationData>;
  
  // Grupos de notificações
  groups: Map<string, NotificationGroup>;
  
  // Configurações
  config: {
    maxNotifications: number;
    maxGroups: number;
    defaultDuration: number;
    soundEnabled: boolean;
    vibrationEnabled: boolean;
    position: NotificationPosition;
    groupSimilar: boolean;
    showProgress: boolean;
  };
  
  // Estatísticas
  stats: {
    totalNotifications: number;
    notificationsByType: Record<NotificationType, number>;
    notificationsByPriority: Record<NotificationPriority, number>;
    dismissedNotifications: number;
    readNotifications: number;
  };
  
  // Actions
  addNotification: (notification: Omit<NotificationData, 'id' | 'timestamp' | 'dismissed' | 'read'>) => string;
  dismissNotification: (id: string) => void;
  dismissAll: (type?: NotificationType) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  updateNotification: (id: string, updates: Partial<NotificationData>) => void;
  clearNotifications: (type?: NotificationType) => void;
  clearGroups: () => void;
  
  // Grupos
  toggleGroup: (groupId: string) => void;
  dismissGroup: (groupId: string) => void;
  markGroupAsRead: (groupId: string) => void;
  
  // Utilitários
  getNotificationsByType: (type: NotificationType) => NotificationData[];
  getNotificationsByPriority: (priority: NotificationPriority) => NotificationData[];
  getUnreadCount: () => number;
  getNotificationStats: () => typeof NotificationState.prototype.stats;
  cleanupExpiredNotifications: () => void;
}

// Configurações padrão
const NOTIFICATION_CONFIG = {
  maxNotifications: 50,
  maxGroups: 10,
  defaultDuration: 5000, // 5 segundos
  soundEnabled: true,
  vibrationEnabled: true,
  position: 'top-right' as NotificationPosition,
  groupSimilar: true,
  showProgress: true,
};

// Função para gerar ID único
const generateNotificationId = (): string => {
  return `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

// Função para gerar grupo ID
const generateGroupId = (type: NotificationType, title: string): string => {
  return `group_${type}_${title.toLowerCase().replace(/\s+/g, '_')}`;
};

// Função para determinar duração padrão
const getDefaultDuration = (type: NotificationType, priority: NotificationPriority): number | undefined => {
  if (type === 'loading') return undefined; // Loading não auto-dismiss
  if (priority === 'urgent') return undefined; // Urgente não auto-dismiss
  
  switch (type) {
    case 'success': return 3000; // 3 segundos
    case 'info': return 4000; // 4 segundos
    case 'warning': return 6000; // 6 segundos
    case 'error': return 8000; // 8 segundos
    default: return NOTIFICATION_CONFIG.defaultDuration;
  }
};

// Função para tocar som
const playNotificationSound = (type: NotificationType): void => {
  if (!NOTIFICATION_CONFIG.soundEnabled) return;
  
  try {
    const audio = new Audio();
    switch (type) {
      case 'success':
        audio.src = '/sounds/notification-success.mp3';
        break;
      case 'error':
        audio.src = '/sounds/notification-error.mp3';
        break;
      case 'warning':
        audio.src = '/sounds/notification-warning.mp3';
        break;
      default:
        audio.src = '/sounds/notification-info.mp3';
    }
    audio.play().catch(() => {
      // Ignorar erros de áudio
    });
  } catch {
    // Ignorar erros de áudio
  }
};

// Função para vibrar
const vibrate = (type: NotificationType): void => {
  if (!NOTIFICATION_CONFIG.vibrationEnabled || !navigator.vibrate) return;
  
  try {
    switch (type) {
      case 'error':
        navigator.vibrate([200, 100, 200]); // Padrão de erro
        break;
      case 'warning':
        navigator.vibrate([100, 50, 100]); // Padrão de aviso
        break;
      default:
        navigator.vibrate(100); // Vibração simples
    }
  } catch {
    // Ignorar erros de vibração
  }
};

export const useNotificationStore = create<NotificationState>()(
  devtools(
    subscribeWithSelector(
      persist(
        (set, get) => ({
          notifications: new Map<string, NotificationData>(),
          groups: new Map<string, NotificationGroup>(),
          config: NOTIFICATION_CONFIG,
          stats: {
            totalNotifications: 0,
            notificationsByType: {
              success: 0,
              info: 0,
              warning: 0,
              error: 0,
              loading: 0,
            },
            notificationsByPriority: {
              low: 0,
              normal: 0,
              high: 0,
              urgent: 0,
            },
            dismissedNotifications: 0,
            readNotifications: 0,
          },

          // Actions
          addNotification: (notification) => {
            const id = generateNotificationId();
            const duration = notification.duration ?? getDefaultDuration(notification.type, notification.priority);
            
            const notificationData: NotificationData = {
              ...notification,
              id,
              timestamp: Date.now(),
              dismissed: false,
              read: false,
              duration,
            };

            set((state) => {
              const newNotifications = new Map(state.notifications);
              const newGroups = new Map(state.groups);
              const newStats = { ...state.stats };

              // Adicionar notificação
              newNotifications.set(id, notificationData);
              
              // Limitar número de notificações
              if (newNotifications.size > NOTIFICATION_CONFIG.maxNotifications) {
                const oldestNotification = Array.from(newNotifications.entries())
                  .sort((a, b) => a[1].timestamp - b[1].timestamp)[0];
                newNotifications.delete(oldestNotification[0]);
              }

              // Agrupar notificações similares
              if (NOTIFICATION_CONFIG.groupSimilar && notification.groupId) {
                const group = newGroups.get(notification.groupId) || {
                  id: notification.groupId,
                  type: notification.type,
                  title: notification.title,
                  count: 0,
                  notifications: [],
                  lastNotification: notificationData,
                  collapsed: false,
                };
                
                group.notifications.push(notificationData);
                group.count = group.notifications.length;
                group.lastNotification = notificationData;
                newGroups.set(notification.groupId, group);
                
                // Limitar número de grupos
                if (newGroups.size > NOTIFICATION_CONFIG.maxGroups) {
                  const oldestGroup = Array.from(newGroups.entries())
                    .sort((a, b) => a[1].lastNotification.timestamp - b[1].lastNotification.timestamp)[0];
                  newGroups.delete(oldestGroup[0]);
                }
              }

              // Atualizar estatísticas
              newStats.totalNotifications++;
              newStats.notificationsByType[notification.type]++;
              newStats.notificationsByPriority[notification.priority]++;

              return {
                notifications: newNotifications,
                groups: newGroups,
                stats: newStats,
              };
            });

            // Tocar som e vibrar
            if (notification.sound !== false) {
              playNotificationSound(notification.type);
            }
            if (notification.vibration !== false) {
              vibrate(notification.type);
            }

            // Auto-dismiss
            if (duration && !notification.persistent) {
              setTimeout(() => {
                get().dismissNotification(id);
              }, duration);
            }

            return id;
          },

          dismissNotification: (id: string) => {
            set((state) => {
              const newNotifications = new Map(state.notifications);
              const notification = newNotifications.get(id);
              
              if (notification) {
                notification.dismissed = true;
                newNotifications.delete(id);
                
                return {
                  notifications: newNotifications,
                  stats: {
                    ...state.stats,
                    dismissedNotifications: state.stats.dismissedNotifications + 1,
                  },
                };
              }
              
              return state;
            });
          },

          dismissAll: (type?: NotificationType) => {
            set((state) => {
              const newNotifications = new Map(state.notifications);
              let dismissedCount = 0;
              
              for (const [id, notification] of newNotifications.entries()) {
                if (!type || notification.type === type) {
                  notification.dismissed = true;
                  newNotifications.delete(id);
                  dismissedCount++;
                }
              }
              
              return {
                notifications: newNotifications,
                stats: {
                  ...state.stats,
                  dismissedNotifications: state.stats.dismissedNotifications + dismissedCount,
                },
              };
            });
          },

          markAsRead: (id: string) => {
            set((state) => {
              const newNotifications = new Map(state.notifications);
              const notification = newNotifications.get(id);
              
              if (notification && !notification.read) {
                notification.read = true;
                
                return {
                  notifications: newNotifications,
                  stats: {
                    ...state.stats,
                    readNotifications: state.stats.readNotifications + 1,
                  },
                };
              }
              
              return state;
            });
          },

          markAllAsRead: () => {
            set((state) => {
              const newNotifications = new Map(state.notifications);
              let readCount = 0;
              
              for (const notification of newNotifications.values()) {
                if (!notification.read) {
                  notification.read = true;
                  readCount++;
                }
              }
              
              return {
                notifications: newNotifications,
                stats: {
                  ...state.stats,
                  readNotifications: state.stats.readNotifications + readCount,
                },
              };
            });
          },

          updateNotification: (id: string, updates: Partial<NotificationData>) => {
            set((state) => {
              const newNotifications = new Map(state.notifications);
              const notification = newNotifications.get(id);
              
              if (notification) {
                Object.assign(notification, updates);
                newNotifications.set(id, notification);
              }
              
              return { notifications: newNotifications };
            });
          },

          clearNotifications: (type?: NotificationType) => {
            set((state) => {
              const newNotifications = new Map(state.notifications);
              
              for (const [id, notification] of newNotifications.entries()) {
                if (!type || notification.type === type) {
                  newNotifications.delete(id);
                }
              }
              
              return { notifications: newNotifications };
            });
          },

          clearGroups: () => {
            set({ groups: new Map() });
          },

          // Grupos
          toggleGroup: (groupId: string) => {
            set((state) => {
              const newGroups = new Map(state.groups);
              const group = newGroups.get(groupId);
              
              if (group) {
                group.collapsed = !group.collapsed;
                newGroups.set(groupId, group);
              }
              
              return { groups: newGroups };
            });
          },

          dismissGroup: (groupId: string) => {
            set((state) => {
              const newNotifications = new Map(state.notifications);
              const newGroups = new Map(state.groups);
              const group = newGroups.get(groupId);
              
              if (group) {
                // Dismiss todas as notificações do grupo
                for (const notification of group.notifications) {
                  newNotifications.delete(notification.id);
                }
                newGroups.delete(groupId);
              }
              
              return {
                notifications: newNotifications,
                groups: newGroups,
              };
            });
          },

          markGroupAsRead: (groupId: string) => {
            set((state) => {
              const newNotifications = new Map(state.notifications);
              const newGroups = new Map(state.groups);
              const group = newGroups.get(groupId);
              
              if (group) {
                let readCount = 0;
                for (const notification of group.notifications) {
                  const storedNotification = newNotifications.get(notification.id);
                  if (storedNotification && !storedNotification.read) {
                    storedNotification.read = true;
                    readCount++;
                  }
                }
                
                return {
                  notifications: newNotifications,
                  groups: newGroups,
                  stats: {
                    ...state.stats,
                    readNotifications: state.stats.readNotifications + readCount,
                  },
                };
              }
              
              return state;
            });
          },

          // Getters
          getNotificationsByType: (type: NotificationType): NotificationData[] => {
            const state = get();
            return Array.from(state.notifications.values())
              .filter(notification => notification.type === type);
          },

          getNotificationsByPriority: (priority: NotificationPriority): NotificationData[] => {
            const state = get();
            return Array.from(state.notifications.values())
              .filter(notification => notification.priority === priority);
          },

          getUnreadCount: (): number => {
            const state = get();
            return Array.from(state.notifications.values())
              .filter(notification => !notification.read).length;
          },

          getNotificationStats: () => {
            const state = get();
            return state.stats;
          },

          cleanupExpiredNotifications: () => {
            set((state) => {
              const newNotifications = new Map(state.notifications);
              const now = Date.now();
              
              for (const [id, notification] of newNotifications.entries()) {
                if (notification.duration && now - notification.timestamp > notification.duration) {
                  newNotifications.delete(id);
                }
              }
              
              return { notifications: newNotifications };
            });
          },
        }),
        {
          name: 'notification-store',
          storage: createJSONStorage(() => localStorage),
          partialize: (state) => ({
            notifications: Array.from(state.notifications.entries()),
            groups: Array.from(state.groups.entries()),
            stats: state.stats,
          }),
          onRehydrateStorage: () => (state) => {
            if (state) {
              // Converter arrays de volta para Maps
              state.notifications = new Map(state.notifications as any);
              state.groups = new Map(state.groups as any);
            }
          },
        }
      )
    ),
    {
      name: 'notification-store',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);

// Hooks utilitários
export const useNotifications = () => {
  const store = useNotificationStore();
  return {
    notifications: Array.from(store.notifications.values()),
    addNotification: store.addNotification,
    dismissNotification: store.dismissNotification,
    dismissAll: store.dismissAll,
    markAsRead: store.markAsRead,
    markAllAsRead: store.markAllAsRead,
    updateNotification: store.updateNotification,
    clearNotifications: store.clearNotifications,
  };
};

export const useNotificationGroups = () => {
  const store = useNotificationStore();
  return {
    groups: Array.from(store.groups.values()),
    toggleGroup: store.toggleGroup,
    dismissGroup: store.dismissGroup,
    markGroupAsRead: store.markGroupAsRead,
    clearGroups: store.clearGroups,
  };
};

export const useNotificationStats = () => {
  const store = useNotificationStore();
  return {
    stats: store.getNotificationStats(),
    unreadCount: store.getUnreadCount(),
  };
};

// Auto-cleanup
if (typeof window !== 'undefined') {
  setInterval(() => {
    useNotificationStore.getState().cleanupExpiredNotifications();
  }, 30000); // A cada 30 segundos
}

export default useNotificationStore; 