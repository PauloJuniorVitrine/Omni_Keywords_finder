/**
 * WebSocketService.ts
 * 
 * Serviço WebSocket para comunicação em tempo real
 * 
 * Tracing ID: WEBSOCKET_SERVICE_001_20250127
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 1.2.2
 * Ruleset: enterprise_control_layer.yaml
 * 
 * Funcionalidades:
 * - Conexão WebSocket em tempo real
 * - Reconexão automática
 * - Notificações push
 * - Status de processamento
 * - Heartbeat
 */

import { useAuth } from '../../hooks/useAuth';
import { useAppStore } from '../../store/AppStore';

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  id?: string;
}

export interface WebSocketConfig {
  url: string;
  reconnectAttempts?: number;
  reconnectDelay?: number;
  heartbeatInterval?: number;
  heartbeatTimeout?: number;
}

export interface WebSocketStatus {
  connected: boolean;
  connecting: boolean;
  error: string | null;
  reconnectAttempts: number;
  lastMessage?: WebSocketMessage;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private reconnectAttempts = 0;
  private maxReconnectAttempts: number;
  private reconnectDelay: number;
  private heartbeatInterval: number;
  private heartbeatTimeout: number;
  private heartbeatTimer?: NodeJS.Timeout;
  private reconnectTimer?: NodeJS.Timeout;
  private messageHandlers: Map<string, ((message: WebSocketMessage) => void)[]> = new Map();
  private statusHandlers: ((status: WebSocketStatus) => void)[] = [];
  private token: string | null = null;

  constructor(config: WebSocketConfig) {
    this.config = config;
    this.maxReconnectAttempts = config.reconnectAttempts || 5;
    this.reconnectDelay = config.reconnectDelay || 1000;
    this.heartbeatInterval = config.heartbeatInterval || 30000;
    this.heartbeatTimeout = config.heartbeatTimeout || 5000;
  }

  // Conectar ao WebSocket
  connect(token?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      this.token = token || this.token;
      if (!this.token) {
        reject(new Error('Token de autenticação necessário'));
        return;
      }

      try {
        const url = `${this.config.url}?token=${this.token}`;
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
          console.log('[WebSocket] Conectado');
          this.reconnectAttempts = 0;
          this.updateStatus({
            connected: true,
            connecting: false,
            error: null,
            reconnectAttempts: this.reconnectAttempts,
          });
          this.startHeartbeat();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('[WebSocket] Erro ao processar mensagem:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('[WebSocket] Desconectado:', event.code, event.reason);
          this.stopHeartbeat();
          this.updateStatus({
            connected: false,
            connecting: false,
            error: event.reason || 'Conexão fechada',
            reconnectAttempts: this.reconnectAttempts,
          });

          // Tentar reconectar se não foi fechamento intencional
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('[WebSocket] Erro:', error);
          this.updateStatus({
            connected: false,
            connecting: false,
            error: 'Erro de conexão',
            reconnectAttempts: this.reconnectAttempts,
          });
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  // Desconectar do WebSocket
  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = undefined;
    }

    this.stopHeartbeat();

    if (this.ws) {
      this.ws.close(1000, 'Desconexão intencional');
      this.ws = null;
    }

    this.updateStatus({
      connected: false,
      connecting: false,
      error: null,
      reconnectAttempts: 0,
    });
  }

  // Enviar mensagem
  send(type: string, data: any): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        reject(new Error('WebSocket não está conectado'));
        return;
      }

      const message: WebSocketMessage = {
        type,
        data,
        timestamp: new Date().toISOString(),
        id: Math.random().toString(36).substr(2, 9),
      };

      try {
        this.ws.send(JSON.stringify(message));
        resolve();
      } catch (error) {
        reject(error);
      }
    });
  }

  // Registrar handler para tipo de mensagem
  onMessage(type: string, handler: (message: WebSocketMessage) => void): void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, []);
    }
    this.messageHandlers.get(type)!.push(handler);
  }

  // Remover handler
  offMessage(type: string, handler: (message: WebSocketMessage) => void): void {
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  // Registrar handler para mudanças de status
  onStatusChange(handler: (status: WebSocketStatus) => void): void {
    this.statusHandlers.push(handler);
  }

  // Remover handler de status
  offStatusChange(handler: (status: WebSocketStatus) => void): void {
    const index = this.statusHandlers.indexOf(handler);
    if (index > -1) {
      this.statusHandlers.splice(index, 1);
    }
  }

  // Obter status atual
  getStatus(): WebSocketStatus {
    return {
      connected: this.ws?.readyState === WebSocket.OPEN,
      connecting: this.ws?.readyState === WebSocket.CONNECTING,
      error: null,
      reconnectAttempts: this.reconnectAttempts,
    };
  }

  // Iniciar heartbeat
  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      this.send('heartbeat', { timestamp: Date.now() });
    }, this.heartbeatInterval);
  }

  // Parar heartbeat
  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = undefined;
    }
  }

  // Agendar reconexão
  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    this.updateStatus({
      connected: false,
      connecting: true,
      error: `Tentativa de reconexão ${this.reconnectAttempts}/${this.maxReconnectAttempts}`,
      reconnectAttempts: this.reconnectAttempts,
    });

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  // Processar mensagem recebida
  private handleMessage(message: WebSocketMessage): void {
    // Atualizar última mensagem no status
    this.updateStatus({
      connected: true,
      connecting: false,
      error: null,
      reconnectAttempts: this.reconnectAttempts,
      lastMessage: message,
    });

    // Chamar handlers específicos do tipo
    const handlers = this.messageHandlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          console.error(`[WebSocket] Erro no handler para ${message.type}:`, error);
        }
      });
    }

    // Chamar handlers globais
    const globalHandlers = this.messageHandlers.get('*');
    if (globalHandlers) {
      globalHandlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          console.error('[WebSocket] Erro no handler global:', error);
        }
      });
    }
  }

  // Atualizar status
  private updateStatus(status: WebSocketStatus): void {
    this.statusHandlers.forEach(handler => {
      try {
        handler(status);
      } catch (error) {
        console.error('[WebSocket] Erro no handler de status:', error);
      }
    });
  }
}

// Instância global do WebSocket
const webSocketService = new WebSocketService({
  url: process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws',
  reconnectAttempts: 5,
  reconnectDelay: 1000,
  heartbeatInterval: 30000,
  heartbeatTimeout: 5000,
});

// Hook para usar WebSocket
export const useWebSocket = () => {
  const { token } = useAuth();
  const { actions } = useAppStore();
  const [status, setStatus] = React.useState<WebSocketStatus>(webSocketService.getStatus());

  React.useEffect(() => {
    // Handler para mudanças de status
    const handleStatusChange = (newStatus: WebSocketStatus) => {
      setStatus(newStatus);

      // Adicionar notificações baseadas no status
      if (newStatus.connected && !status.connected) {
        actions.addNotification({
          type: 'success',
          title: 'Conectado',
          message: 'Conexão em tempo real estabelecida',
        });
      } else if (!newStatus.connected && status.connected) {
        actions.addNotification({
          type: 'warning',
          title: 'Desconectado',
          message: 'Conexão em tempo real perdida',
        });
      } else if (newStatus.error && newStatus.error !== status.error) {
        actions.addNotification({
          type: 'error',
          title: 'Erro de Conexão',
          message: newStatus.error,
        });
      }
    };

    // Handler para notificações
    const handleNotification = (message: WebSocketMessage) => {
      if (message.type === 'notification') {
        actions.addNotification({
          type: message.data.type || 'info',
          title: message.data.title || 'Notificação',
          message: message.data.message || '',
        });
      }
    };

    // Handler para atualizações de execução
    const handleExecutionUpdate = (message: WebSocketMessage) => {
      if (message.type === 'execution_update') {
        // Atualizar estado da execução no store
        actions.updateExecucao(message.data);
      }
    };

    // Registrar handlers
    webSocketService.onStatusChange(handleStatusChange);
    webSocketService.onMessage('notification', handleNotification);
    webSocketService.onMessage('execution_update', handleExecutionUpdate);

    // Conectar se tiver token
    if (token) {
      webSocketService.connect(token);
    }

    return () => {
      webSocketService.offStatusChange(handleStatusChange);
      webSocketService.offMessage('notification', handleNotification);
      webSocketService.offMessage('execution_update', handleExecutionUpdate);
    };
  }, [token, actions]);

  // Reconectar quando token mudar
  React.useEffect(() => {
    if (token) {
      webSocketService.connect(token);
    } else {
      webSocketService.disconnect();
    }
  }, [token]);

  return {
    status,
    send: webSocketService.send.bind(webSocketService),
    onMessage: webSocketService.onMessage.bind(webSocketService),
    offMessage: webSocketService.offMessage.bind(webSocketService),
    connect: webSocketService.connect.bind(webSocketService),
    disconnect: webSocketService.disconnect.bind(webSocketService),
  };
};

export default webSocketService; 