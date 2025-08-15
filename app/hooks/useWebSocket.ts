/**
 * useWebSocket.ts
 * 
 * Hook para comunicação WebSocket em tempo real
 * 
 * Prompt: CHECKLIST_PRIMEIRA_REVISAO.md - Item 5
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2024-12-19
 */

import { useState, useEffect, useRef, useCallback } from 'react';

interface UseWebSocketOptions {
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
}

export function useWebSocket<T>(
  url: string | null,
  refreshInterval?: number,
  options: UseWebSocketOptions = {}
) {
  const [data, setData] = useState<T | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const {
    reconnectInterval = 5000,
    maxReconnectAttempts = 5,
    onOpen,
    onClose,
    onError
  } = options;

  const connect = useCallback(() => {
    if (!url) return;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        setReconnectAttempts(0);
        onOpen?.();
      };

      ws.onmessage = (event) => {
        try {
          const parsedData = JSON.parse(event.data);
          setData(parsedData);
        } catch (parseError) {
          console.error('Erro ao fazer parse dos dados WebSocket:', parseError);
        }
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        onClose?.();

        // Tentar reconectar se não foi fechamento intencional
        if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
          setReconnectAttempts(prev => prev + 1);
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      ws.onerror = (event) => {
        setError('Erro na conexão WebSocket');
        onError?.(event);
      };

    } catch (err) {
      setError('Erro ao criar conexão WebSocket');
      console.error('Erro ao criar WebSocket:', err);
    }
  }, [url, reconnectInterval, maxReconnectAttempts, reconnectAttempts, onOpen, onClose, onError]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close(1000); // Código de fechamento normal
      wsRef.current = null;
    }
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    setIsConnected(false);
    setReconnectAttempts(0);
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, [isConnected]);

  // Conectar quando URL mudar
  useEffect(() => {
    if (url) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [url, connect, disconnect]);

  // Configurar intervalo de refresh se especificado
  useEffect(() => {
    if (refreshInterval && isConnected) {
      intervalRef.current = setInterval(() => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          // Enviar ping para manter conexão ativa
          wsRef.current.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
        }
      }, refreshInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [refreshInterval, isConnected]);

  // Cleanup no unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    data,
    isConnected,
    error,
    reconnectAttempts,
    sendMessage,
    connect,
    disconnect
  };
} 