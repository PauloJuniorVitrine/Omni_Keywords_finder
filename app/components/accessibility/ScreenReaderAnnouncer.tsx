/**
 * ScreenReaderAnnouncer - Componente para anunciar mudanças para screen readers
 * 
 * Prompt: Implementação de ARIA labels para Criticalidade 3.2.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { Box } from '@mui/material';

interface Announcement {
  id: string;
  message: string;
  priority: 'polite' | 'assertive';
  timestamp: number;
}

interface ScreenReaderContextType {
  announce: (message: string, priority?: 'polite' | 'assertive') => void;
  clearAnnouncements: () => void;
  announcements: Announcement[];
}

const ScreenReaderContext = createContext<ScreenReaderContextType | undefined>(undefined);

interface ScreenReaderProviderProps {
  children: React.ReactNode;
  maxAnnouncements?: number;
  autoClearDelay?: number;
}

export const ScreenReaderProvider: React.FC<ScreenReaderProviderProps> = ({
  children,
  maxAnnouncements = 5,
  autoClearDelay = 5000
}) => {
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const timeoutRefs = useRef<Map<string, NodeJS.Timeout>>(new Map());

  const announce = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const id = `announcement-${Date.now()}-${Math.random()}`;
    const newAnnouncement: Announcement = {
      id,
      message,
      priority,
      timestamp: Date.now()
    };

    setAnnouncements(prev => {
      const updated = [...prev, newAnnouncement];
      // Manter apenas os últimos maxAnnouncements
      if (updated.length > maxAnnouncements) {
        return updated.slice(-maxAnnouncements);
      }
      return updated;
    });

    // Auto-clear após delay
    const timeout = setTimeout(() => {
      clearAnnouncement(id);
    }, autoClearDelay);

    timeoutRefs.current.set(id, timeout);
  };

  const clearAnnouncement = (id: string) => {
    setAnnouncements(prev => prev.filter(announcement => announcement.id !== id));
    
    const timeout = timeoutRefs.current.get(id);
    if (timeout) {
      clearTimeout(timeout);
      timeoutRefs.current.delete(id);
    }
  };

  const clearAnnouncements = () => {
    setAnnouncements([]);
    
    // Limpar todos os timeouts
    timeoutRefs.current.forEach(timeout => clearTimeout(timeout));
    timeoutRefs.current.clear();
  };

  useEffect(() => {
    return () => {
      // Cleanup timeouts no unmount
      timeoutRefs.current.forEach(timeout => clearTimeout(timeout));
      timeoutRefs.current.clear();
    };
  }, []);

  return (
    <ScreenReaderContext.Provider value={{ announce, clearAnnouncements, announcements }}>
      {children}
      <ScreenReaderAnnouncer announcements={announcements} />
    </ScreenReaderContext.Provider>
  );
};

interface ScreenReaderAnnouncerProps {
  announcements: Announcement[];
}

const ScreenReaderAnnouncer: React.FC<ScreenReaderAnnouncerProps> = ({ announcements }) => {
  const politeAnnouncements = announcements.filter(a => a.priority === 'polite');
  const assertiveAnnouncements = announcements.filter(a => a.priority === 'assertive');

  return (
    <Box
      component="div"
      aria-live="polite"
      aria-atomic="true"
      sx={{
        position: 'absolute',
        left: '-10000px',
        width: '1px',
        height: '1px',
        overflow: 'hidden',
        pointerEvents: 'none',
        userSelect: 'none'
      }}
    >
      {politeAnnouncements.length > 0 && (
        <div key={`polite-${politeAnnouncements[politeAnnouncements.length - 1].id}`}>
          {politeAnnouncements[politeAnnouncements.length - 1].message}
        </div>
      )}
    </Box>
  );
};

// Hook para usar o anunciador
export const useScreenReader = () => {
  const context = useContext(ScreenReaderContext);
  if (!context) {
    throw new Error('useScreenReader must be used within a ScreenReaderProvider');
  }
  return context;
};

// Componente para anunciar mudanças de estado
interface StateAnnouncerProps {
  state: any;
  label: string;
  priority?: 'polite' | 'assertive';
  formatMessage?: (state: any, label: string) => string;
}

export const StateAnnouncer: React.FC<StateAnnouncerProps> = ({
  state,
  label,
  priority = 'polite',
  formatMessage
}) => {
  const { announce } = useScreenReader();
  const prevStateRef = useRef(state);

  useEffect(() => {
    if (prevStateRef.current !== state) {
      const message = formatMessage 
        ? formatMessage(state, label)
        : `${label}: ${state}`;
      
      announce(message, priority);
      prevStateRef.current = state;
    }
  }, [state, label, priority, announce, formatMessage]);

  return null;
};

// Componente para anunciar contadores
interface CounterAnnouncerProps {
  count: number;
  label: string;
  formatMessage?: (count: number, label: string) => string;
}

export const CounterAnnouncer: React.FC<CounterAnnouncerProps> = ({
  count,
  label,
  formatMessage
}) => {
  const { announce } = useScreenReader();
  const prevCountRef = useRef(count);

  useEffect(() => {
    if (prevCountRef.current !== count) {
      const message = formatMessage 
        ? formatMessage(count, label)
        : `${label}: ${count} itens`;
      
      announce(message, 'polite');
      prevCountRef.current = count;
    }
  }, [count, label, announce, formatMessage]);

  return null;
};

// Componente para anunciar erros
interface ErrorAnnouncerProps {
  error: Error | string | null;
  label?: string;
}

export const ErrorAnnouncer: React.FC<ErrorAnnouncerProps> = ({
  error,
  label = 'Erro'
}) => {
  const { announce } = useScreenReader();
  const prevErrorRef = useRef(error);

  useEffect(() => {
    if (prevErrorRef.current !== error && error) {
      const message = typeof error === 'string' ? error : error.message;
      announce(`${label}: ${message}`, 'assertive');
      prevErrorRef.current = error;
    }
  }, [error, label, announce]);

  return null;
};

// Componente para anunciar sucessos
interface SuccessAnnouncerProps {
  success: string | null;
  label?: string;
}

export const SuccessAnnouncer: React.FC<SuccessAnnouncerProps> = ({
  success,
  label = 'Sucesso'
}) => {
  const { announce } = useScreenReader();
  const prevSuccessRef = useRef(success);

  useEffect(() => {
    if (prevSuccessRef.current !== success && success) {
      announce(`${label}: ${success}`, 'polite');
      prevSuccessRef.current = success;
    }
  }, [success, label, announce]);

  return null;
};

// Componente para anunciar carregamento
interface LoadingAnnouncerProps {
  isLoading: boolean;
  label?: string;
}

export const LoadingAnnouncer: React.FC<LoadingAnnouncerProps> = ({
  isLoading,
  label = 'Carregando'
}) => {
  const { announce } = useScreenReader();
  const prevLoadingRef = useRef(isLoading);

  useEffect(() => {
    if (prevLoadingRef.current !== isLoading) {
      const message = isLoading ? `${label}...` : `${label} concluído`;
      announce(message, 'polite');
      prevLoadingRef.current = isLoading;
    }
  }, [isLoading, label, announce]);

  return null;
};

export default ScreenReaderAnnouncer; 