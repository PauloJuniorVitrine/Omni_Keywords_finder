/**
 * Hook para Progress Tracking - Omni Keywords Finder
 * =================================================
 * 
 * Este hook fornece integração com o sistema de tracking de progresso,
 * incluindo user journeys, milestones, analytics e notificações.
 * 
 * Autor: Paulo Júnior
 * Data: 2025-01-27
 * Tracing ID: USE_PROGRESS_001
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useAnalytics } from './useAnalytics';

// Tipos
export interface Milestone {
  milestone_id: string;
  name: string;
  description: string;
  progress_type: 'user_journey' | 'milestone' | 'achievement' | 'skill' | 'level' | 'custom';
  target_value: number;
  current_value: number;
  status: 'locked' | 'in_progress' | 'completed' | 'failed';
  rewards: Array<{
    type: string;
    value: number | string;
    description: string;
  }>;
  criteria: string[];
  created_at: string;
  completed_at?: string;
  metadata: Record<string, any>;
  progress_percentage: number;
}

export interface UserJourney {
  journey_id: string;
  user_id: string;
  journey_name: string;
  description: string;
  milestones: Milestone[];
  current_stage: number;
  total_stages: number;
  started_at: string;
  completed_at?: string;
  metadata: Record<string, any>;
  progress_percentage: number;
}

export interface ProgressAnalytics {
  user_id: string;
  total_milestones: number;
  completed_milestones: number;
  total_journeys: number;
  completed_journeys: number;
  average_completion_time: number;
  engagement_score: number;
  last_activity: string;
  progress_trend: 'excellent' | 'good' | 'fair' | 'needs_improvement' | 'stable';
  recommendations: string[];
  completion_rate: number;
}

export interface UserProgress {
  user_id: string;
  journeys: UserJourney[];
  milestones: Milestone[];
  analytics: ProgressAnalytics | null;
  last_updated: string;
}

export interface ProgressNotification {
  type: 'milestone_completed' | 'journey_completed' | 'level_up' | 'achievement_unlocked';
  title: string;
  message: string;
  data: any;
  timestamp: string;
}

// Configuração
const PROGRESS_API_BASE = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
const PROGRESS_ENDPOINTS = {
  progress: `${PROGRESS_API_BASE}/api/progress`,
  analytics: `${PROGRESS_API_BASE}/api/progress/analytics`,
  update: `${PROGRESS_API_BASE}/api/progress/update`,
  journey: `${PROGRESS_API_BASE}/api/progress/journey`,
  leaderboard: `${PROGRESS_API_BASE}/api/progress/leaderboard`,
  export: `${PROGRESS_API_BASE}/api/progress/export`,
} as const;

// Cache local
const progressCache = new Map<string, { data: UserProgress; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutos

export const useProgress = (userId?: string) => {
  const [progress, setProgress] = useState<UserProgress | null>(null);
  const [analytics, setAnalytics] = useState<ProgressAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notifications, setNotifications] = useState<ProgressNotification[]>([]);
  
  const { trackEvent } = useAnalytics();
  const abortControllerRef = useRef<AbortController | null>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Função para fazer requisições com retry
  const fetchWithRetry = useCallback(async (
    url: string, 
    options: RequestInit = {}, 
    retries = 3
  ): Promise<Response> => {
    try {
      const controller = new AbortController();
      abortControllerRef.current = controller;
      
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return response;
    } catch (error) {
      if (retries > 0 && error instanceof Error && error.name !== 'AbortError') {
        console.warn(`Tentativa falhou, tentando novamente... (${retries} restantes)`);
        await new Promise(resolve => setTimeout(resolve, 1000 * (4 - retries))); // Backoff exponencial
        return fetchWithRetry(url, options, retries - 1);
      }
      throw error;
    }
  }, []);

  // Carregar progresso do usuário
  const loadProgress = useCallback(async (forceRefresh = false) => {
    if (!userId) return;

    const cacheKey = `progress_${userId}`;
    const cached = progressCache.get(cacheKey);
    
    // Verificar cache
    if (!forceRefresh && cached && Date.now() - cached.timestamp < CACHE_TTL) {
      setProgress(cached.data);
      setAnalytics(cached.data.analytics);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetchWithRetry(`${PROGRESS_ENDPOINTS.progress}/${userId}`);
      const data: UserProgress = await response.json();

      // Atualizar cache
      progressCache.set(cacheKey, { data, timestamp: Date.now() });

      setProgress(data);
      setAnalytics(data.analytics);

      // Track analytics
      trackEvent('progress_loaded', {
        user_id: userId,
        total_journeys: data.journeys.length,
        total_milestones: data.milestones.length,
        engagement_score: data.analytics?.engagement_score || 0,
      });

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      setError(`Falha ao carregar progresso: ${errorMessage}`);
      console.error('Erro ao carregar progresso:', error);
    } finally {
      setLoading(false);
    }
  }, [userId, fetchWithRetry, trackEvent]);

  // Atualizar progresso de um milestone
  const updateMilestoneProgress = useCallback(async (
    milestoneId: string, 
    progressValue: number, 
    metadata?: Record<string, any>
  ) => {
    if (!userId) return false;

    try {
      const response = await fetchWithRetry(`${PROGRESS_ENDPOINTS.update}`, {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          milestone_id: milestoneId,
          progress_value: progressValue,
          metadata,
        }),
      });

      const result = await response.json();

      if (result.success) {
        // Recarregar progresso
        await loadProgress(true);
        
        // Track analytics
        trackEvent('milestone_progress_updated', {
          user_id: userId,
          milestone_id: milestoneId,
          progress_value: progressValue,
          new_total: progressValue,
        });

        return true;
      } else {
        throw new Error(result.error || 'Falha ao atualizar progresso');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      setError(`Falha ao atualizar progresso: ${errorMessage}`);
      console.error('Erro ao atualizar progresso:', error);
      return false;
    }
  }, [userId, fetchWithRetry, loadProgress, trackEvent]);

  // Criar nova journey
  const createJourney = useCallback(async (
    journeyName: string,
    description: string,
    milestones?: Milestone[]
  ) => {
    if (!userId) return null;

    try {
      const response = await fetchWithRetry(`${PROGRESS_ENDPOINTS.journey}`, {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          journey_name: journeyName,
          description,
          milestones,
        }),
      });

      const result = await response.json();

      if (result.success) {
        // Recarregar progresso
        await loadProgress(true);
        
        // Track analytics
        trackEvent('journey_created', {
          user_id: userId,
          journey_name: journeyName,
          milestones_count: milestones?.length || 0,
        });

        return result.journey_id;
      } else {
        throw new Error(result.error || 'Falha ao criar journey');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      setError(`Falha ao criar journey: ${errorMessage}`);
      console.error('Erro ao criar journey:', error);
      return null;
    }
  }, [userId, fetchWithRetry, loadProgress, trackEvent]);

  // Obter analytics detalhados
  const loadAnalytics = useCallback(async () => {
    if (!userId) return;

    try {
      const response = await fetchWithRetry(`${PROGRESS_ENDPOINTS.analytics}/${userId}`);
      const data: ProgressAnalytics = await response.json();
      setAnalytics(data);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      console.error('Erro ao carregar analytics:', error);
      // Não definir erro global, apenas log
    }
  }, [userId, fetchWithRetry]);

  // Obter leaderboard
  const getLeaderboard = useCallback(async (limit = 100) => {
    try {
      const response = await fetchWithRetry(`${PROGRESS_ENDPOINTS.leaderboard}?limit=${limit}`);
      const data = await response.json();
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      console.error('Erro ao carregar leaderboard:', error);
      return [];
    }
  }, [fetchWithRetry]);

  // Exportar relatório
  const exportProgressReport = useCallback(async (format: 'json' | 'csv' = 'json') => {
    if (!userId) return null;

    try {
      const response = await fetchWithRetry(`${PROGRESS_ENDPOINTS.export}/${userId}?format=${format}`);
      
      if (format === 'json') {
        const data = await response.json();
        return data;
      } else {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `progress_report_${userId}_${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        return 'download_iniciado';
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      setError(`Falha ao exportar relatório: ${errorMessage}`);
      console.error('Erro ao exportar relatório:', error);
      return null;
    }
  }, [userId, fetchWithRetry]);

  // Adicionar notificação
  const addNotification = useCallback((notification: ProgressNotification) => {
    setNotifications(prev => [notification, ...prev.slice(0, 9)]); // Manter apenas 10 mais recentes
    
    // Track analytics
    trackEvent('progress_notification_received', {
      user_id: userId,
      notification_type: notification.type,
      notification_title: notification.title,
    });
  }, [userId, trackEvent]);

  // Remover notificação
  const removeNotification = useCallback((index: number) => {
    setNotifications(prev => prev.filter((_, i) => i !== index));
  }, []);

  // Limpar todas as notificações
  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // Iniciar polling para atualizações em tempo real
  const startPolling = useCallback((intervalMs = 30000) => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    pollingIntervalRef.current = setInterval(() => {
      loadProgress(true);
    }, intervalMs);
  }, [loadProgress]);

  // Parar polling
  const stopPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  }, []);

  // Carregar progresso inicial
  useEffect(() => {
    if (userId) {
      loadProgress();
      startPolling();
    }

    return () => {
      stopPolling();
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [userId, loadProgress, startPolling, stopPolling]);

  // Computed values
  const totalJourneys = progress?.journeys.length || 0;
  const completedJourneys = progress?.journeys.filter(j => j.completed_at).length || 0;
  const totalMilestones = progress?.milestones.length || 0;
  const completedMilestones = progress?.milestones.filter(m => m.status === 'completed').length || 0;
  const inProgressMilestones = progress?.milestones.filter(m => m.status === 'in_progress').length || 0;
  const lockedMilestones = progress?.milestones.filter(m => m.status === 'locked').length || 0;

  const overallProgress = totalMilestones > 0 ? (completedMilestones / totalMilestones) * 100 : 0;
  const engagementScore = analytics?.engagement_score || 0;
  const progressTrend = analytics?.progress_trend || 'stable';
  const recommendations = analytics?.recommendations || [];

  return {
    // Estado
    progress,
    analytics,
    loading,
    error,
    notifications,
    
    // Computed values
    totalJourneys,
    completedJourneys,
    totalMilestones,
    completedMilestones,
    inProgressMilestones,
    lockedMilestones,
    overallProgress,
    engagementScore,
    progressTrend,
    recommendations,
    
    // Ações
    loadProgress,
    updateMilestoneProgress,
    createJourney,
    loadAnalytics,
    getLeaderboard,
    exportProgressReport,
    addNotification,
    removeNotification,
    clearNotifications,
    startPolling,
    stopPolling,
    
    // Utilitários
    refresh: () => loadProgress(true),
    clearError: () => setError(null),
  };
};

// Hook para notificações de progresso
export const useProgressNotifications = (userId?: string) => {
  const [notifications, setNotifications] = useState<ProgressNotification[]>([]);
  const { trackEvent } = useAnalytics();

  // Simular WebSocket para notificações em tempo real
  useEffect(() => {
    if (!userId) return;

    // Em produção, isso seria um WebSocket real
    const interval = setInterval(() => {
      // Simular notificações ocasionais
      if (Math.random() < 0.1) { // 10% de chance
        const mockNotification: ProgressNotification = {
          type: 'milestone_completed',
          title: 'Milestone Concluído!',
          message: 'Parabéns! Você completou um novo milestone.',
          data: { milestone_id: 'mock_milestone' },
          timestamp: new Date().toISOString(),
        };
        
        setNotifications(prev => [mockNotification, ...prev.slice(0, 9)]);
        
        trackEvent('mock_notification_received', {
          user_id: userId,
          notification_type: mockNotification.type,
        });
      }
    }, 60000); // Verificar a cada minuto

    return () => clearInterval(interval);
  }, [userId, trackEvent]);

  const removeNotification = useCallback((index: number) => {
    setNotifications(prev => prev.filter((_, i) => i !== index));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  return {
    notifications,
    removeNotification,
    clearAll,
  };
};

// Hook para analytics de progresso
export const useProgressAnalytics = (userId?: string) => {
  const [analytics, setAnalytics] = useState<ProgressAnalytics | null>(null);
  const [loading, setLoading] = useState(false);
  const { trackEvent } = useAnalytics();

  const loadAnalytics = useCallback(async () => {
    if (!userId) return;

    setLoading(true);
    try {
      const response = await fetch(`${PROGRESS_ENDPOINTS.analytics}/${userId}`);
      const data: ProgressAnalytics = await response.json();
      setAnalytics(data);
      
      trackEvent('progress_analytics_loaded', {
        user_id: userId,
        engagement_score: data.engagement_score,
        completion_rate: data.completion_rate,
      });
    } catch (error) {
      console.error('Erro ao carregar analytics:', error);
    } finally {
      setLoading(false);
    }
  }, [userId, trackEvent]);

  useEffect(() => {
    loadAnalytics();
  }, [loadAnalytics]);

  return {
    analytics,
    loading,
    refresh: loadAnalytics,
  };
}; 