/**
 * NotificationCenter - Centro de Notificações Avançado
 * 
 * Componente React para gerenciar e exibir notificações em tempo real,
 * com suporte a múltiplos canais, templates e preferências de usuário.
 * 
 * Funcionalidades:
 * - Notificações em tempo real via WebSocket
 * - Filtros por tipo, canal e status
 * - Preferências de usuário
 * - Templates personalizáveis
 * - Notificações push
 * - Integração com email/Slack/Discord
 * 
 * Autor: Sistema de Notificações Avançado
 * Data: 2024-12-19
 * Ruleset: enterprise_control_layer.yaml
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { createPortal } from 'react-dom';

// Tipos
interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success' | 'critical';
  channel: 'email' | 'slack' | 'discord' | 'push' | 'in_app' | 'webhook';
  priority: number;
  userId?: string;
  templateId?: string;
  variables?: Record<string, any>;
  createdAt: string;
  sentAt?: string;
  readAt?: string;
  metadata?: Record<string, any>;
}

interface UserPreferences {
  userId: string;
  emailEnabled: boolean;
  slackEnabled: boolean;
  discordEnabled: boolean;
  pushEnabled: boolean;
  inAppEnabled: boolean;
  webhookEnabled: boolean;
  webhookUrl?: string;
  emailAddress?: string;
  slackChannel?: string;
  discordWebhook?: string;
  notificationTypes: string[];
  quietHoursStart: string;
  quietHoursEnd: string;
  timezone: string;
}

interface NotificationTemplate {
  id: string;
  name: string;
  subject: string;
  body: string;
  variables: string[];
  channels: string[];
  createdAt: string;
  updatedAt: string;
}

interface NotificationCenterProps {
  userId: string;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  maxNotifications?: number;
  autoClose?: boolean;
  autoCloseDelay?: number;
  showPreferences?: boolean;
  showTemplates?: boolean;
  className?: string;
}

// Hooks personalizados
const useWebSocket = (url: string, userId: string) => {
  const [isConnected, setIsConnected] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const connect = () => {
      try {
        const ws = new WebSocket(`${url}?userId=${userId}`);
        
        ws.onopen = () => {
          setIsConnected(true);
          console.log('WebSocket conectado');
        };

        ws.onmessage = (event) => {
          const notification: Notification = JSON.parse(event.data);
          setNotifications(prev => [notification, ...prev]);
        };

        ws.onclose = () => {
          setIsConnected(false);
          console.log('WebSocket desconectado');
          // Reconectar após 5 segundos
          setTimeout(connect, 5000);
        };

        ws.onerror = (error) => {
          console.error('Erro WebSocket:', error);
        };

        wsRef.current = ws;
      } catch (error) {
        console.error('Erro ao conectar WebSocket:', error);
      }
    };

    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url, userId]);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  return { isConnected, notifications, sendMessage };
};

const useNotificationPreferences = (userId: string) => {
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPreferences = async () => {
      try {
        const response = await fetch(`/api/notifications/preferences/${userId}`);
        if (response.ok) {
          const data = await response.json();
          setPreferences(data);
        }
      } catch (error) {
        console.error('Erro ao carregar preferências:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPreferences();
  }, [userId]);

  const updatePreferences = async (newPreferences: Partial<UserPreferences>) => {
    try {
      const response = await fetch(`/api/notifications/preferences/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPreferences)
      });

      if (response.ok) {
        setPreferences(prev => prev ? { ...prev, ...newPreferences } : null);
        return true;
      }
    } catch (error) {
      console.error('Erro ao atualizar preferências:', error);
    }
    return false;
  };

  return { preferences, loading, updatePreferences };
};

const useNotificationTemplates = () => {
  const [templates, setTemplates] = useState<NotificationTemplate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const response = await fetch('/api/notifications/templates');
        if (response.ok) {
          const data = await response.json();
          setTemplates(data);
        }
      } catch (error) {
        console.error('Erro ao carregar templates:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTemplates();
  }, []);

  return { templates, loading };
};

// Componentes auxiliares
const NotificationItem: React.FC<{
  notification: Notification;
  onMarkAsRead: (id: string) => void;
  onDelete: (id: string) => void;
}> = ({ notification, onMarkAsRead, onDelete }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getTypeColor = (type: string) => {
    const colors = {
      info: '#4f8cff',
      warning: '#eab308',
      error: '#ef4444',
      success: '#10b981',
      critical: '#dc2626'
    };
    return colors[type as keyof typeof colors] || colors.info;
  };

  const getChannelIcon = (channel: string) => {
    const icons = {
      email: '📧',
      slack: '💬',
      discord: '🎮',
      push: '📱',
      in_app: '💻',
      webhook: '🔗'
    };
    return icons[channel as keyof typeof icons] || '📢';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  return (
    <div
      className={`notification-item ${notification.readAt ? 'read' : 'unread'}`}
      style={{
        background: notification.readAt ? '#f9f9f9' : '#ffffff',
        borderLeft: `4px solid ${getTypeColor(notification.type)}`,
        borderRadius: '8px',
        padding: '16px',
        marginBottom: '12px',
        boxShadow: notification.readAt ? 'none' : '0 2px 8px rgba(0,0,0,0.1)',
        cursor: 'pointer',
        transition: 'all 0.2s ease'
      }}
      onClick={() => setIsExpanded(!isExpanded)}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '16px' }}>{getChannelIcon(notification.channel)}</span>
          <div>
            <h4 style={{ margin: '0 0 4px 0', fontSize: '14px', fontWeight: '600' }}>
              {notification.title}
            </h4>
            <p style={{ margin: '0', fontSize: '12px', color: '#666' }}>
              {formatDate(notification.createdAt)}
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {!notification.readAt && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onMarkAsRead(notification.id);
              }}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                fontSize: '12px',
                color: '#4f8cff'
              }}
            >
              Marcar como lida
            </button>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(notification.id);
            }}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '12px',
              color: '#ef4444'
            }}
          >
            Excluir
          </button>
        </div>
      </div>
      
      {isExpanded && (
        <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #eee' }}>
          <p style={{ margin: '0 0 8px 0', fontSize: '13px', lineHeight: '1.4' }}>
            {notification.message}
          </p>
          {notification.metadata && (
            <div style={{ fontSize: '11px', color: '#888' }}>
              <strong>Metadados:</strong> {JSON.stringify(notification.metadata)}
            </div>
          )}
          <div style={{ fontSize: '11px', color: '#888', marginTop: '8px' }}>
            <span>Prioridade: {notification.priority}</span>
            {notification.templateId && (
              <span style={{ marginLeft: '12px' }}>Template: {notification.templateId}</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const PreferencesModal: React.FC<{
  preferences: UserPreferences;
  onUpdate: (preferences: Partial<UserPreferences>) => Promise<boolean>;
  onClose: () => void;
}> = ({ preferences, onUpdate, onClose }) => {
  const [formData, setFormData] = useState(preferences);
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    
    const success = await onUpdate(formData);
    if (success) {
      onClose();
    }
    
    setSaving(false);
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        background: 'white',
        padding: '24px',
        borderRadius: '8px',
        maxWidth: '500px',
        width: '90%',
        maxHeight: '80vh',
        overflow: 'auto'
      }}>
        <h3 style={{ margin: '0 0 20px 0' }}>Preferências de Notificação</h3>
        
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '16px' }}>
            <h4>Canais de Notificação</h4>
            <label style={{ display: 'block', marginBottom: '8px' }}>
              <input
                type="checkbox"
                checked={formData.emailEnabled}
                onChange={(e) => setFormData(prev => ({ ...prev, emailEnabled: e.target.checked }))}
              />
              Email
            </label>
            <label style={{ display: 'block', marginBottom: '8px' }}>
              <input
                type="checkbox"
                checked={formData.slackEnabled}
                onChange={(e) => setFormData(prev => ({ ...prev, slackEnabled: e.target.checked }))}
              />
              Slack
            </label>
            <label style={{ display: 'block', marginBottom: '8px' }}>
              <input
                type="checkbox"
                checked={formData.discordEnabled}
                onChange={(e) => setFormData(prev => ({ ...prev, discordEnabled: e.target.checked }))}
              />
              Discord
            </label>
            <label style={{ display: 'block', marginBottom: '8px' }}>
              <input
                type="checkbox"
                checked={formData.pushEnabled}
                onChange={(e) => setFormData(prev => ({ ...prev, pushEnabled: e.target.checked }))}
              />
              Push Notifications
            </label>
            <label style={{ display: 'block', marginBottom: '8px' }}>
              <input
                type="checkbox"
                checked={formData.inAppEnabled}
                onChange={(e) => setFormData(prev => ({ ...prev, inAppEnabled: e.target.checked }))}
              />
              Notificações In-App
            </label>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <h4>Configurações de Email</h4>
            <input
              type="email"
              placeholder="Email para notificações"
              value={formData.emailAddress || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, emailAddress: e.target.value }))}
              style={{ width: '100%', padding: '8px', marginBottom: '8px' }}
            />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <h4>Quiet Hours</h4>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <input
                type="time"
                value={formData.quietHoursStart}
                onChange={(e) => setFormData(prev => ({ ...prev, quietHoursStart: e.target.value }))}
                style={{ padding: '8px' }}
              />
              <span>até</span>
              <input
                type="time"
                value={formData.quietHoursEnd}
                onChange={(e) => setFormData(prev => ({ ...prev, quietHoursEnd: e.target.value }))}
                style={{ padding: '8px' }}
              />
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: '8px 16px',
                border: '1px solid #ddd',
                background: 'white',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saving}
              style={{
                padding: '8px 16px',
                border: 'none',
                background: '#4f8cff',
                color: 'white',
                borderRadius: '4px',
                cursor: saving ? 'not-allowed' : 'pointer',
                opacity: saving ? 0.6 : 1
              }}
            >
              {saving ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Componente principal
const NotificationCenter: React.FC<NotificationCenterProps> = ({
  userId,
  position = 'top-right',
  maxNotifications = 10,
  autoClose = true,
  autoCloseDelay = 5000,
  showPreferences = true,
  showTemplates = true,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [showPreferencesModal, setShowPreferencesModal] = useState(false);
  const [showTemplatesModal, setShowTemplatesModal] = useState(false);
  const [filter, setFilter] = useState({
    type: 'all',
    channel: 'all',
    read: 'all'
  });

  // Hooks personalizados
  const { isConnected, notifications, sendMessage } = useWebSocket('ws://localhost:8765', userId);
  const { preferences, loading: preferencesLoading, updatePreferences } = useNotificationPreferences(userId);
  const { templates, loading: templatesLoading } = useNotificationTemplates();

  // Auto-close para notificações
  useEffect(() => {
    if (autoClose && notifications.length > 0) {
      const timer = setTimeout(() => {
        // Auto-close notificações antigas
        const now = Date.now();
        const oldNotifications = notifications.filter(n => 
          now - new Date(n.createdAt).getTime() > autoCloseDelay
        );
        
        oldNotifications.forEach(n => {
          if (!n.readAt) {
            markAsRead(n.id);
          }
        });
      }, autoCloseDelay);

      return () => clearTimeout(timer);
    }
  }, [notifications, autoClose, autoCloseDelay]);

  // Funções
  const markAsRead = async (id: string) => {
    try {
      await fetch(`/api/notifications/${id}/read`, { method: 'PATCH' });
      sendMessage({ action: 'mark_read', notificationId: id });
    } catch (error) {
      console.error('Erro ao marcar como lida:', error);
    }
  };

  const deleteNotification = async (id: string) => {
    try {
      await fetch(`/api/notifications/${id}`, { method: 'DELETE' });
      sendMessage({ action: 'delete', notificationId: id });
    } catch (error) {
      console.error('Erro ao excluir notificação:', error);
    }
  };

  const filteredNotifications = notifications.filter(notification => {
    if (filter.type !== 'all' && notification.type !== filter.type) return false;
    if (filter.channel !== 'all' && notification.channel !== filter.channel) return false;
    if (filter.read === 'read' && !notification.readAt) return false;
    if (filter.read === 'unread' && notification.readAt) return false;
    return true;
  }).slice(0, maxNotifications);

  const unreadCount = notifications.filter(n => !n.readAt).length;

  // Posicionamento
  const getPositionStyles = () => {
    const baseStyles = {
      position: 'fixed' as const,
      zIndex: 1000,
      background: 'white',
      border: '1px solid #ddd',
      borderRadius: '8px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      maxWidth: '400px',
      width: '90vw',
      maxHeight: '80vh',
      overflow: 'hidden'
    };

    switch (position) {
      case 'top-right':
        return { ...baseStyles, top: '20px', right: '20px' };
      case 'top-left':
        return { ...baseStyles, top: '20px', left: '20px' };
      case 'bottom-right':
        return { ...baseStyles, bottom: '20px', right: '20px' };
      case 'bottom-left':
        return { ...baseStyles, bottom: '20px', left: '20px' };
      default:
        return { ...baseStyles, top: '20px', right: '20px' };
    }
  };

  return (
    <>
      {/* Botão de notificações */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'relative',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          fontSize: '20px',
          padding: '8px',
          borderRadius: '4px',
          transition: 'background-color 0.2s'
        }}
        className={className}
      >
        🔔
        {unreadCount > 0 && (
          <span style={{
            position: 'absolute',
            top: '0',
            right: '0',
            background: '#ef4444',
            color: 'white',
            fontSize: '10px',
            padding: '2px 6px',
            borderRadius: '10px',
            minWidth: '16px',
            textAlign: 'center'
          }}>
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Centro de notificações */}
      {isOpen && createPortal(
        <div style={getPositionStyles()}>
          {/* Header */}
          <div style={{
            padding: '16px',
            borderBottom: '1px solid #eee',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <h3 style={{ margin: 0, fontSize: '16px' }}>
              Notificações {unreadCount > 0 && `(${unreadCount})`}
            </h3>
            <div style={{ display: 'flex', gap: '8px' }}>
              {showPreferences && (
                <button
                  onClick={() => setShowPreferencesModal(true)}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '14px',
                    padding: '4px 8px',
                    borderRadius: '4px'
                  }}
                >
                  ⚙️
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '16px',
                  padding: '4px'
                }}
              >
                ✕
              </button>
            </div>
          </div>

          {/* Filtros */}
          <div style={{
            padding: '12px 16px',
            borderBottom: '1px solid #eee',
            display: 'flex',
            gap: '8px',
            flexWrap: 'wrap'
          }}>
            <select
              value={filter.type}
              onChange={(e) => setFilter(prev => ({ ...prev, type: e.target.value }))}
              style={{ padding: '4px 8px', fontSize: '12px' }}
            >
              <option value="all">Todos os tipos</option>
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
              <option value="success">Success</option>
              <option value="critical">Critical</option>
            </select>

            <select
              value={filter.channel}
              onChange={(e) => setFilter(prev => ({ ...prev, channel: e.target.value }))}
              style={{ padding: '4px 8px', fontSize: '12px' }}
            >
              <option value="all">Todos os canais</option>
              <option value="email">Email</option>
              <option value="slack">Slack</option>
              <option value="discord">Discord</option>
              <option value="push">Push</option>
              <option value="in_app">In-App</option>
            </select>

            <select
              value={filter.read}
              onChange={(e) => setFilter(prev => ({ ...prev, read: e.target.value }))}
              style={{ padding: '4px 8px', fontSize: '12px' }}
            >
              <option value="all">Todas</option>
              <option value="unread">Não lidas</option>
              <option value="read">Lidas</option>
            </select>
          </div>

          {/* Lista de notificações */}
          <div style={{
            maxHeight: '400px',
            overflow: 'auto',
            padding: '16px'
          }}>
            {filteredNotifications.length === 0 ? (
              <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
                Nenhuma notificação encontrada
              </div>
            ) : (
              filteredNotifications.map(notification => (
                <NotificationItem
                  key={notification.id}
                  notification={notification}
                  onMarkAsRead={markAsRead}
                  onDelete={deleteNotification}
                />
              ))
            )}
          </div>

          {/* Status de conexão */}
          <div style={{
            padding: '8px 16px',
            borderTop: '1px solid #eee',
            fontSize: '11px',
            color: '#666',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: isConnected ? '#10b981' : '#ef4444'
            }} />
            {isConnected ? 'Conectado' : 'Desconectado'}
          </div>
        </div>,
        document.body
      )}

      {/* Modal de preferências */}
      {showPreferencesModal && preferences && (
        <PreferencesModal
          preferences={preferences}
          onUpdate={updatePreferences}
          onClose={() => setShowPreferencesModal(false)}
        />
      )}
    </>
  );
};

export default NotificationCenter; 