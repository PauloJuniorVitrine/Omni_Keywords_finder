/**
 * usePerformanceMetrics.ts
 * 
 * Hook para buscar métricas de performance do sistema
 * 
 * Prompt: CHECKLIST_PRIMEIRA_REVISAO.md - Item 5
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2024-12-19
 */

import { useState, useEffect, useCallback } from 'react';

interface PerformanceData {
  timestamp: string;
  responseTime: number;
  throughput: number;
  errorRate: number;
  cpuUsage: number;
  memoryUsage: number;
  activeUsers: number;
  keywordsProcessed: number;
  clustersGenerated: number;
  apiCalls: number;
}

interface PerformanceMetricsError {
  message: string;
  code?: string;
  details?: any;
}

interface UsePerformanceMetricsOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
  onError?: (error: PerformanceMetricsError) => void;
}

export function usePerformanceMetrics(
  timeRange: string,
  options: UsePerformanceMetricsOptions = {}
) {
  const [metrics, setMetrics] = useState<PerformanceData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<PerformanceMetricsError | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const {
    autoRefresh = true,
    refreshInterval = 30000, // 30 segundos
    onError
  } = options;

  // Função para buscar métricas da API
  const fetchMetrics = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Simular chamada à API (em produção seria uma chamada real)
      const response = await fetch(`/api/performance/metrics?timeRange=${timeRange}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setMetrics(data.metrics || []);
      setLastUpdated(new Date());

    } catch (err) {
      // Fallback para dados simulados em caso de erro
      console.warn('Erro ao buscar métricas, usando dados simulados:', err);
      
      const mockData = generateMockMetrics(timeRange);
      setMetrics(mockData);
      setLastUpdated(new Date());
      
      const errorObj: PerformanceMetricsError = {
        message: 'Erro ao carregar métricas em tempo real. Exibindo dados simulados.',
        code: 'MOCK_DATA_FALLBACK',
        details: err
      };
      
      setError(errorObj);
      onError?.(errorObj);
    } finally {
      setIsLoading(false);
    }
  }, [timeRange, onError]);

  // Função para gerar dados simulados
  const generateMockMetrics = (range: string): PerformanceData[] => {
    const now = new Date();
    const data: PerformanceData[] = [];
    
    let points: number;
    let interval: number;
    
    switch (range) {
      case '1h':
        points = 60;
        interval = 60000; // 1 minuto
        break;
      case '6h':
        points = 72;
        interval = 300000; // 5 minutos
        break;
      case '24h':
        points = 96;
        interval = 900000; // 15 minutos
        break;
      case '7d':
        points = 168;
        interval = 3600000; // 1 hora
        break;
      default:
        points = 60;
        interval = 60000;
    }

    for (let i = points - 1; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - (i * interval));
      
      // Gerar dados realistas com variação
      const baseResponseTime = 150 + Math.random() * 100;
      const baseThroughput = 50 + Math.random() * 30;
      const baseErrorRate = Math.random() * 3;
      const baseCpuUsage = 30 + Math.random() * 40;
      const baseMemoryUsage = 40 + Math.random() * 30;
      const baseActiveUsers = 10 + Math.random() * 20;
      const baseKeywordsProcessed = 100 + Math.random() * 200;
      const baseClustersGenerated = 10 + Math.random() * 15;
      const baseApiCalls = 30 + Math.random() * 40;

      data.push({
        timestamp: timestamp.toISOString(),
        responseTime: Math.round(baseResponseTime),
        throughput: Math.round(baseThroughput * 10) / 10,
        errorRate: Math.round(baseErrorRate * 100) / 100,
        cpuUsage: Math.round(baseCpuUsage),
        memoryUsage: Math.round(baseMemoryUsage),
        activeUsers: Math.round(baseActiveUsers),
        keywordsProcessed: Math.round(baseKeywordsProcessed),
        clustersGenerated: Math.round(baseClustersGenerated),
        apiCalls: Math.round(baseApiCalls)
      });
    }

    return data;
  };

  // Função para refresh manual
  const refreshMetrics = useCallback(async () => {
    await fetchMetrics();
  }, [fetchMetrics]);

  // Carregar métricas iniciais
  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  // Auto-refresh se habilitado
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchMetrics();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchMetrics]);

  // Buscar métricas quando timeRange mudar
  useEffect(() => {
    fetchMetrics();
  }, [timeRange, fetchMetrics]);

  return {
    metrics,
    isLoading,
    error,
    lastUpdated,
    refreshMetrics
  };
} 