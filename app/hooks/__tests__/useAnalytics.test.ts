/**
 * useAnalytics.test.ts
 * 
 * Testes unitários para o hook useAnalytics
 * 
 * Tracing ID: TEST-HOOK-AN-001
 * Data/Hora: 2025-01-27 15:30:00 UTC
 * Versão: 1.0
 * Ruleset: enterprise_control_layer.yaml
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useAnalytics, useKeywordsAnalytics, useUserAnalytics, usePerformanceAnalytics, useRevenueAnalytics } from '../useAnalytics';
import { useGraphQL } from '../useGraphQL';

// Mock dos hooks
jest.mock('../useGraphQL');

const mockUseGraphQL = useGraphQL as jest.MockedFunction<typeof useGraphQL>;

describe('useAnalytics', () => {
  const defaultGraphQLResponse = {
    data: null,
    loading: false,
    error: null,
    refetch: jest.fn()
  };

  const mockAnalyticsData = {
    analytics: {
      keywordsPerformance: {
        totalKeywords: 1000,
        activeKeywords: 850,
        conversionRate: 0.15,
        avgPosition: 3.2,
        clickThroughRate: 0.08,
        costPerClick: 2.50,
        totalClicks: 5000,
        totalImpressions: 62500
      },
      clusterEfficiency: {
        totalClusters: 25,
        avgClusterSize: 34,
        clusterQuality: 0.85,
        semanticCoherence: 0.92,
        performanceVariance: 0.12
      },
      userBehavior: {
        activeUsers: 1200,
        sessionDuration: 8.5,
        pageViews: 15000,
        bounceRate: 0.35,
        userEngagement: 0.78
      },
      predictiveInsights: {
        trendPrediction: 0.75,
        seasonalityFactor: 0.3,
        anomalyScore: 0.1,
        recommendationConfidence: 0.85,
        nextBestAction: 'Increase budget for high-performing keywords'
      }
    }
  };

  const mockEventsData = {
    analyticsEvents: [
      {
        id: 'event-1',
        type: 'user_action',
        timestamp: new Date().toISOString(),
        data: { action: 'login', userId: 'user-123' },
        userId: 'user-123',
        sessionId: 'session-456'
      }
    ]
  };

  beforeEach(() => {
    mockUseGraphQL.mockReturnValue(defaultGraphQLResponse);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Hook principal', () => {
    it('deve retornar estado inicial correto', () => {
      const { result } = renderHook(() => useAnalytics());

      expect(result.current.data).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.status).toBe('idle');
      expect(result.current.lastRefresh).toBeInstanceOf(Date);
      expect(result.current.retryCount).toBe(0);
      expect(result.current.isExporting).toBe(false);
    });

    it('deve fazer chamadas GraphQL corretas', () => {
      renderHook(() => useAnalytics());

      expect(mockUseGraphQL).toHaveBeenCalledTimes(2); // analytics + events
      
      // Verificar se as queries estão corretas
      const calls = mockUseGraphQL.mock.calls;
      expect(calls[0][0]).toContain('GetAnalyticsData');
      expect(calls[1][0]).toContain('GetAnalyticsEvents');
    });

    it('deve processar dados de analytics corretamente', () => {
      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        data: mockAnalyticsData
      });

      const { result } = renderHook(() => useAnalytics());

      expect(result.current.data).toBeDefined();
      expect(result.current.data?.keywordsPerformance).toBeDefined();
      expect(result.current.data?.clusterEfficiency).toBeDefined();
      expect(result.current.data?.userBehavior).toBeDefined();
      expect(result.current.data?.predictiveInsights).toBeDefined();
    });

    it('deve calcular métricas derivadas corretamente', () => {
      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        data: mockAnalyticsData
      });

      const { result } = renderHook(() => useAnalytics());

      const calculatedMetrics = result.current.data?.calculatedMetrics;
      expect(calculatedMetrics).toBeDefined();
      expect(calculatedMetrics?.performanceScore).toBeGreaterThan(0);
      expect(calculatedMetrics?.efficiencyTrend).toBe('up');
      expect(calculatedMetrics?.riskLevel).toBe('low');
    });

    it('deve processar eventos corretamente', () => {
      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        data: mockEventsData
      });

      const { result } = renderHook(() => useAnalytics());

      expect(result.current.events).toHaveLength(1);
      expect(result.current.events[0].id).toBe('event-1');
      expect(result.current.events[0].type).toBe('user_action');
    });

    it('deve atualizar status baseado no estado dos dados', () => {
      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        loading: true
      });

      const { result } = renderHook(() => useAnalytics());

      expect(result.current.status).toBe('loading');
    });

    it('deve atualizar status para error quando há erro', () => {
      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        error: new Error('GraphQL error')
      });

      const { result } = renderHook(() => useAnalytics());

      expect(result.current.status).toBe('error');
    });

    it('deve atualizar status para success quando há dados', () => {
      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        data: mockAnalyticsData
      });

      const { result } = renderHook(() => useAnalytics());

      expect(result.current.status).toBe('success');
    });
  });

  describe('Cache', () => {
    it('deve gerenciar cache local corretamente', () => {
      const { result } = renderHook(() => useAnalytics());

      // Testar setCachedData
      act(() => {
        result.current.setCachedData('test-key', { test: 'data' });
      });

      expect(result.current.cacheSize).toBe(1);

      // Testar getCachedData
      const cachedData = result.current.getCachedData('test-key');
      expect(cachedData).toEqual({ test: 'data' });

      // Testar cleanupCache
      act(() => {
        result.current.cleanupCache();
      });

      expect(result.current.cacheSize).toBe(1); // Dados ainda válidos
    });

    it('deve limpar cache expirado', () => {
      const { result } = renderHook(() => useAnalytics({}, { cacheTime: 100 }));

      // Adicionar dados ao cache
      act(() => {
        result.current.setCachedData('test-key', { test: 'data' });
      });

      expect(result.current.cacheSize).toBe(1);

      // Simular passagem do tempo
      act(() => {
        jest.advanceTimersByTime(200);
        result.current.cleanupCache();
      });

      expect(result.current.cacheSize).toBe(0);
    });
  });

  describe('Retry logic', () => {
    it('deve implementar retry logic corretamente', () => {
      const mockRefetch = jest.fn();
      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        refetch: mockRefetch
      });

      const { result } = renderHook(() => useAnalytics({}, { maxRetries: 3 }));

      // Simular retry
      act(() => {
        result.current.retry();
      });

      expect(result.current.retryCount).toBe(1);
      expect(mockRefetch).toHaveBeenCalled();

      // Simular múltiplos retries
      act(() => {
        result.current.retry();
        result.current.retry();
        result.current.retry();
      });

      expect(result.current.retryCount).toBe(3);
    });

    it('deve resetar retry count quando dados são carregados com sucesso', () => {
      const mockRefetch = jest.fn();
      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        refetch: mockRefetch
      });

      const { result } = renderHook(() => useAnalytics());

      // Simular retry
      act(() => {
        result.current.retry();
      });

      expect(result.current.retryCount).toBe(1);

      // Simular sucesso
      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        data: mockAnalyticsData,
        loading: false
      });

      // Re-renderizar hook
      const { result: newResult } = renderHook(() => useAnalytics());

      expect(newResult.current.retryCount).toBe(0);
    });
  });

  describe('Exportação', () => {
    it('deve exportar dados em formato JSON', async () => {
      const mockCreateElement = jest.fn();
      const mockClick = jest.fn();
      const mockBlob = jest.fn();
      
      Object.assign(document, { createElement: mockCreateElement });
      Object.assign(global, { Blob: mockBlob });
      Object.assign(URL, { createObjectURL: jest.fn(), revokeObjectURL: jest.fn() });

      mockCreateElement.mockReturnValue({
        href: '',
        download: '',
        click: mockClick
      });

      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        data: mockAnalyticsData
      });

      const { result } = renderHook(() => useAnalytics());

      await act(async () => {
        await result.current.exportData('json');
      });

      expect(mockCreateElement).toHaveBeenCalledWith('a');
      expect(mockClick).toHaveBeenCalled();
    });

    it('deve gerenciar estado de exportação', async () => {
      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        data: mockAnalyticsData
      });

      const { result } = renderHook(() => useAnalytics());

      expect(result.current.isExporting).toBe(false);

      const exportPromise = act(async () => {
        await result.current.exportData('csv');
      });

      expect(result.current.isExporting).toBe(true);

      await exportPromise;

      expect(result.current.isExporting).toBe(false);
    });
  });

  describe('Tracking de eventos', () => {
    it('deve rastrear eventos corretamente', async () => {
      const { result } = renderHook(() => useAnalytics());

      const event = {
        type: 'user_action',
        data: { action: 'click', element: 'button' },
        userId: 'user-123',
        sessionId: 'session-456'
      };

      const response = await act(async () => {
        return await result.current.trackEvent(event);
      });

      expect(response.success).toBe(true);
      expect(response.id).toContain('event-');
    });
  });

  describe('Insights preditivos', () => {
    it('deve buscar insights preditivos', async () => {
      const { result } = renderHook(() => useAnalytics());

      const insights = await act(async () => {
        return await result.current.getPredictiveInsights();
      });

      expect(insights).toBeDefined();
      expect(insights?.trendPrediction).toBe(0.75);
      expect(insights?.nextBestAction).toBe('Increase budget for high-performing keywords');
    });
  });

  describe('Métricas em tempo real', () => {
    it('deve buscar métricas em tempo real', async () => {
      const { result } = renderHook(() => useAnalytics());

      const metrics = await act(async () => {
        return await result.current.getRealTimeMetrics();
      });

      expect(metrics).toBeDefined();
      expect(metrics?.activeUsers).toBeGreaterThan(0);
      expect(metrics?.requestsPerMinute).toBeGreaterThan(0);
    });
  });

  describe('Refresh de dados', () => {
    it('deve atualizar dados corretamente', () => {
      const mockRefetch = jest.fn();
      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        refetch: mockRefetch
      });

      const { result } = renderHook(() => useAnalytics());

      const initialRefresh = result.current.lastRefresh;

      act(() => {
        result.current.refetch();
      });

      expect(mockRefetch).toHaveBeenCalled();
      expect(result.current.lastRefresh.getTime()).toBeGreaterThan(initialRefresh.getTime());
    });
  });

  describe('Hooks especializados', () => {
    it('deve filtrar dados por keywords', () => {
      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        data: mockAnalyticsData
      });

      const { result } = renderHook(() => useKeywordsAnalytics());

      expect(result.current.keywordsData).toBeDefined();
      expect(result.current.clusterData).toBeDefined();
      expect(result.current.keywordsData?.totalKeywords).toBe(1000);
    });

    it('deve filtrar dados por usuários', () => {
      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        data: mockAnalyticsData
      });

      const { result } = renderHook(() => useUserAnalytics());

      expect(result.current.userData).toBeDefined();
      expect(result.current.userData?.activeUsers).toBe(1200);
    });

    it('deve filtrar dados por performance', () => {
      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        data: mockAnalyticsData
      });

      const { result } = renderHook(() => usePerformanceAnalytics());

      expect(result.current.performanceData).toBeDefined();
      expect(result.current.insights).toBeDefined();
      expect(result.current.performanceData?.conversionRate).toBe(0.15);
    });

    it('deve filtrar dados por receita', () => {
      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        data: mockAnalyticsData
      });

      const { result } = renderHook(() => useRevenueAnalytics());

      expect(result.current.revenueData).toBeDefined();
      expect(result.current.insights).toBeDefined();
      expect(result.current.revenueData?.costPerClick).toBe(2.50);
    });
  });

  describe('Utilitários', () => {
    it('deve formatar dados de analytics corretamente', () => {
      const formatted = useAnalytics.formatAnalyticsData(mockAnalyticsData.analytics);

      expect(formatted.performance).toBeDefined();
      expect(formatted.efficiency).toBeDefined();
      expect(formatted.users).toBeDefined();
      expect(formatted.insights).toBeDefined();
    });

    it('deve calcular tendência corretamente', () => {
      expect(useAnalytics.getAnalyticsTrend(110, 100)).toBe('up');
      expect(useAnalytics.getAnalyticsTrend(90, 100)).toBe('down');
      expect(useAnalytics.getAnalyticsTrend(102, 100)).toBe('stable');
    });

    it('deve calcular score de performance corretamente', () => {
      const score = useAnalytics.calculatePerformanceScore(mockAnalyticsData.analytics);
      expect(score).toBeGreaterThan(0);
      expect(score).toBeLessThanOrEqual(100);
    });
  });

  describe('Configurações', () => {
    it('deve aplicar configurações personalizadas', () => {
      const options = {
        enableRealTime: false,
        refreshInterval: 60000,
        enableCaching: false,
        cacheTime: 600000,
        maxRetries: 5
      };

      renderHook(() => useAnalytics({}, options));

      // Verificar se as configurações foram aplicadas
      expect(mockUseGraphQL).toHaveBeenCalledWith(
        expect.any(String),
        expect.any(Object),
        expect.objectContaining({
          pollInterval: undefined, // enableRealTime: false
          fetchPolicy: 'network-only' // enableCaching: false
        })
      );
    });

    it('deve aplicar filtros corretamente', () => {
      const filters = {
        period: '7d' as const,
        metric: 'performance' as const,
        category: 'keywords',
        userId: 'user-123'
      };

      renderHook(() => useAnalytics(filters));

      expect(mockUseGraphQL).toHaveBeenCalledWith(
        expect.any(String),
        { filters },
        expect.any(Object)
      );
    });
  });

  describe('Error handling', () => {
    it('deve lidar com erros de GraphQL', () => {
      const error = new Error('GraphQL error');
      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        error
      });

      const { result } = renderHook(() => useAnalytics());

      expect(result.current.error).toBe(error);
      expect(result.current.status).toBe('error');
    });

    it('deve lidar com erros de exportação', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      mockUseGraphQL.mockReturnValue({
        ...defaultGraphQLResponse,
        data: mockAnalyticsData
      });

      const { result } = renderHook(() => useAnalytics());

      // Simular erro na exportação
      jest.spyOn(global, 'Blob').mockImplementation(() => {
        throw new Error('Export error');
      });

      await act(async () => {
        await result.current.exportData('json');
      });

      expect(consoleSpy).toHaveBeenCalledWith('Erro na exportação:', expect.any(Error));
      expect(result.current.isExporting).toBe(false);

      consoleSpy.mockRestore();
    });
  });
}); 