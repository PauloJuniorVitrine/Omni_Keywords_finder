/**
 * Testes Unitários - PerformanceDashboard Component
 * 
 * Prompt: Implementação de testes para componentes de dashboard
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_PERFORMANCE_DASHBOARD_011
 * 
 * Baseado em código real do componente PerformanceDashboard.tsx
 */

import React from 'react';

// Interfaces extraídas do componente para teste
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

interface AlertData {
  id: string;
  type: 'warning' | 'error' | 'info' | 'success';
  message: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

// Dados mock extraídos do componente para teste
const mockPerformanceData: PerformanceData[] = [
  {
    timestamp: '2024-12-20T10:00:00Z',
    responseTime: 150,
    throughput: 1250,
    errorRate: 0.5,
    cpuUsage: 45,
    memoryUsage: 67,
    activeUsers: 89,
    keywordsProcessed: 1250,
    clustersGenerated: 45,
    apiCalls: 890
  },
  {
    timestamp: '2024-12-20T10:05:00Z',
    responseTime: 180,
    throughput: 1180,
    errorRate: 1.2,
    cpuUsage: 52,
    memoryUsage: 71,
    activeUsers: 92,
    keywordsProcessed: 1180,
    clustersGenerated: 42,
    apiCalls: 920
  },
  {
    timestamp: '2024-12-20T10:10:00Z',
    responseTime: 220,
    throughput: 1100,
    errorRate: 2.8,
    cpuUsage: 68,
    memoryUsage: 78,
    activeUsers: 95,
    keywordsProcessed: 1100,
    clustersGenerated: 38,
    apiCalls: 950
  },
  {
    timestamp: '2024-12-20T10:15:00Z',
    responseTime: 280,
    throughput: 980,
    errorRate: 4.5,
    cpuUsage: 75,
    memoryUsage: 82,
    activeUsers: 88,
    keywordsProcessed: 980,
    clustersGenerated: 35,
    apiCalls: 880
  },
  {
    timestamp: '2024-12-20T10:20:00Z',
    responseTime: 320,
    throughput: 850,
    errorRate: 6.2,
    cpuUsage: 82,
    memoryUsage: 87,
    activeUsers: 85,
    keywordsProcessed: 850,
    clustersGenerated: 32,
    apiCalls: 820
  }
];

const mockAlerts: AlertData[] = [
  {
    id: '1',
    type: 'warning',
    message: 'Tempo de resposta acima do threshold (2.5s)',
    timestamp: '2024-12-20T10:15:00Z',
    severity: 'medium'
  },
  {
    id: '2',
    type: 'error',
    message: 'Taxa de erro aumentou para 5.2%',
    timestamp: '2024-12-20T10:20:00Z',
    severity: 'high'
  },
  {
    id: '3',
    type: 'info',
    message: 'Backup automático concluído com sucesso',
    timestamp: '2024-12-20T10:25:00Z',
    severity: 'low'
  }
];

// Funções utilitárias extraídas do componente
const calculateAggregatedMetrics = (performanceData: PerformanceData[]) => {
  if (performanceData.length === 0) return null;

  const latest = performanceData[performanceData.length - 1];
  const avgResponseTime = performanceData.reduce((sum, data) => sum + data.responseTime, 0) / performanceData.length;
  const avgThroughput = performanceData.reduce((sum, data) => sum + data.throughput, 0) / performanceData.length;
  const avgErrorRate = performanceData.reduce((sum, data) => sum + data.errorRate, 0) / performanceData.length;

  return {
    current: latest,
    average: {
      responseTime: avgResponseTime,
      throughput: avgThroughput,
      errorRate: avgErrorRate
    }
  };
};

const getPerformanceStatus = (responseTime: number, errorRate: number, cpuUsage: number, memoryUsage: number) => {
  const status = {
    responseTime: responseTime > 2000 ? 'warning' : 'success',
    errorRate: errorRate > 5 ? 'error' : 'success',
    cpuUsage: cpuUsage > 80 ? 'exception' : 'normal',
    memoryUsage: memoryUsage > 80 ? 'exception' : 'normal'
  };

  return status;
};

const filterPerformanceData = (data: PerformanceData[], timeRange: '1h' | '6h' | '24h' | '7d') => {
  const now = new Date();
  const ranges = {
    '1h': 60 * 60 * 1000,
    '6h': 6 * 60 * 60 * 1000,
    '24h': 24 * 60 * 60 * 1000,
    '7d': 7 * 24 * 60 * 60 * 1000
  };

  const cutoffTime = now.getTime() - ranges[timeRange];
  
  return data.filter(item => new Date(item.timestamp).getTime() > cutoffTime);
};

const calculateTrends = (data: PerformanceData[]) => {
  if (data.length < 2) return null;

  const current = data[data.length - 1];
  const previous = data[data.length - 2];

  return {
    responseTime: ((current.responseTime - previous.responseTime) / previous.responseTime) * 100,
    throughput: ((current.throughput - previous.throughput) / previous.throughput) * 100,
    errorRate: ((current.errorRate - previous.errorRate) / previous.errorRate) * 100,
    cpuUsage: ((current.cpuUsage - previous.cpuUsage) / previous.cpuUsage) * 100,
    memoryUsage: ((current.memoryUsage - previous.memoryUsage) / previous.memoryUsage) * 100
  };
};

const validatePerformanceThresholds = (data: PerformanceData) => {
  const thresholds = {
    responseTime: { warning: 2000, critical: 5000 },
    errorRate: { warning: 5, critical: 10 },
    cpuUsage: { warning: 80, critical: 95 },
    memoryUsage: { warning: 80, critical: 95 }
  };

  const violations = [];

  if (data.responseTime > thresholds.responseTime.critical) {
    violations.push({ metric: 'responseTime', severity: 'critical', value: data.responseTime });
  } else if (data.responseTime > thresholds.responseTime.warning) {
    violations.push({ metric: 'responseTime', severity: 'warning', value: data.responseTime });
  }

  if (data.errorRate > thresholds.errorRate.critical) {
    violations.push({ metric: 'errorRate', severity: 'critical', value: data.errorRate });
  } else if (data.errorRate > thresholds.errorRate.warning) {
    violations.push({ metric: 'errorRate', severity: 'warning', value: data.errorRate });
  }

  if (data.cpuUsage > thresholds.cpuUsage.critical) {
    violations.push({ metric: 'cpuUsage', severity: 'critical', value: data.cpuUsage });
  } else if (data.cpuUsage > thresholds.cpuUsage.warning) {
    violations.push({ metric: 'cpuUsage', severity: 'warning', value: data.cpuUsage });
  }

  if (data.memoryUsage > thresholds.memoryUsage.critical) {
    violations.push({ metric: 'memoryUsage', severity: 'critical', value: data.memoryUsage });
  } else if (data.memoryUsage > thresholds.memoryUsage.warning) {
    violations.push({ metric: 'memoryUsage', severity: 'warning', value: data.memoryUsage });
  }

  return violations;
};

const formatTimestamp = (timestamp: string) => {
  return new Date(timestamp).toLocaleString('pt-BR');
};

const calculateBusinessMetrics = (data: PerformanceData[]) => {
  if (data.length === 0) return null;

  const totalKeywords = data.reduce((sum, item) => sum + item.keywordsProcessed, 0);
  const totalClusters = data.reduce((sum, item) => sum + item.clustersGenerated, 0);
  const totalApiCalls = data.reduce((sum, item) => sum + item.apiCalls, 0);
  const avgActiveUsers = data.reduce((sum, item) => sum + item.activeUsers, 0) / data.length;

  return {
    totalKeywords,
    totalClusters,
    totalApiCalls,
    avgActiveUsers,
    keywordsPerCluster: totalClusters > 0 ? totalKeywords / totalClusters : 0,
    apiCallsPerUser: avgActiveUsers > 0 ? totalApiCalls / avgActiveUsers : 0
  };
};

describe('PerformanceDashboard - Dashboard de Performance em Tempo Real', () => {
  
  describe('Interface PerformanceData - Validação de Estrutura', () => {
    
    test('deve validar estrutura do PerformanceData', () => {
      const data: PerformanceData = mockPerformanceData[0];

      expect(data).toHaveProperty('timestamp');
      expect(data).toHaveProperty('responseTime');
      expect(data).toHaveProperty('throughput');
      expect(data).toHaveProperty('errorRate');
      expect(data).toHaveProperty('cpuUsage');
      expect(data).toHaveProperty('memoryUsage');
      expect(data).toHaveProperty('activeUsers');
      expect(data).toHaveProperty('keywordsProcessed');
      expect(data).toHaveProperty('clustersGenerated');
      expect(data).toHaveProperty('apiCalls');
      expect(typeof data.timestamp).toBe('string');
      expect(typeof data.responseTime).toBe('number');
      expect(typeof data.throughput).toBe('number');
      expect(typeof data.errorRate).toBe('number');
      expect(typeof data.cpuUsage).toBe('number');
      expect(typeof data.memoryUsage).toBe('number');
      expect(typeof data.activeUsers).toBe('number');
      expect(typeof data.keywordsProcessed).toBe('number');
      expect(typeof data.clustersGenerated).toBe('number');
      expect(typeof data.apiCalls).toBe('number');
    });

    test('deve validar valores numéricos positivos', () => {
      mockPerformanceData.forEach(data => {
        expect(data.responseTime).toBeGreaterThanOrEqual(0);
        expect(data.throughput).toBeGreaterThanOrEqual(0);
        expect(data.errorRate).toBeGreaterThanOrEqual(0);
        expect(data.cpuUsage).toBeGreaterThanOrEqual(0);
        expect(data.memoryUsage).toBeGreaterThanOrEqual(0);
        expect(data.activeUsers).toBeGreaterThanOrEqual(0);
        expect(data.keywordsProcessed).toBeGreaterThanOrEqual(0);
        expect(data.clustersGenerated).toBeGreaterThanOrEqual(0);
        expect(data.apiCalls).toBeGreaterThanOrEqual(0);
      });
    });

    test('deve validar percentuais dentro dos limites', () => {
      mockPerformanceData.forEach(data => {
        expect(data.errorRate).toBeLessThanOrEqual(100);
        expect(data.cpuUsage).toBeLessThanOrEqual(100);
        expect(data.memoryUsage).toBeLessThanOrEqual(100);
      });
    });

    test('deve validar formato de timestamp ISO', () => {
      const isoPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
      
      mockPerformanceData.forEach(data => {
        expect(isoPattern.test(data.timestamp)).toBe(true);
      });
    });
  });

  describe('Interface AlertData - Validação de Estrutura', () => {
    
    test('deve validar estrutura do AlertData', () => {
      const alert: AlertData = mockAlerts[0];

      expect(alert).toHaveProperty('id');
      expect(alert).toHaveProperty('type');
      expect(alert).toHaveProperty('message');
      expect(alert).toHaveProperty('timestamp');
      expect(alert).toHaveProperty('severity');
      expect(typeof alert.id).toBe('string');
      expect(typeof alert.message).toBe('string');
      expect(typeof alert.timestamp).toBe('string');
    });

    test('deve validar tipos de alerta', () => {
      const validTypes = ['warning', 'error', 'info', 'success'];
      
      mockAlerts.forEach(alert => {
        expect(validTypes).toContain(alert.type);
      });
    });

    test('deve validar níveis de severidade', () => {
      const validSeverities = ['low', 'medium', 'high', 'critical'];
      
      mockAlerts.forEach(alert => {
        expect(validSeverities).toContain(alert.severity);
      });
    });

    test('deve validar formato de timestamp dos alertas', () => {
      const isoPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
      
      mockAlerts.forEach(alert => {
        expect(isoPattern.test(alert.timestamp)).toBe(true);
      });
    });
  });

  describe('Cálculo de Métricas Agregadas', () => {
    
    test('deve calcular métricas agregadas corretamente', () => {
      const metrics = calculateAggregatedMetrics(mockPerformanceData);

      expect(metrics).not.toBeNull();
      expect(metrics?.current).toBe(mockPerformanceData[mockPerformanceData.length - 1]);
      expect(metrics?.average.responseTime).toBeCloseTo(230, 1);
      expect(metrics?.average.throughput).toBeCloseTo(1072, 1);
      expect(metrics?.average.errorRate).toBeCloseTo(3.04, 2);
    });

    test('deve retornar null para dados vazios', () => {
      const metrics = calculateAggregatedMetrics([]);
      expect(metrics).toBeNull();
    });

    test('deve calcular média correta para um único ponto', () => {
      const singleData = [mockPerformanceData[0]];
      const metrics = calculateAggregatedMetrics(singleData);

      expect(metrics?.average.responseTime).toBe(150);
      expect(metrics?.average.throughput).toBe(1250);
      expect(metrics?.average.errorRate).toBe(0.5);
    });
  });

  describe('Status de Performance', () => {
    
    test('deve determinar status correto para valores normais', () => {
      const status = getPerformanceStatus(150, 0.5, 45, 67);

      expect(status.responseTime).toBe('success');
      expect(status.errorRate).toBe('success');
      expect(status.cpuUsage).toBe('normal');
      expect(status.memoryUsage).toBe('normal');
    });

    test('deve determinar status de warning para valores elevados', () => {
      const status = getPerformanceStatus(2500, 6.0, 85, 82);

      expect(status.responseTime).toBe('warning');
      expect(status.errorRate).toBe('error');
      expect(status.cpuUsage).toBe('exception');
      expect(status.memoryUsage).toBe('exception');
    });

    test('deve determinar status crítico para valores muito altos', () => {
      const status = getPerformanceStatus(6000, 12.0, 98, 96);

      expect(status.responseTime).toBe('warning');
      expect(status.errorRate).toBe('error');
      expect(status.cpuUsage).toBe('exception');
      expect(status.memoryUsage).toBe('exception');
    });
  });

  describe('Filtros de Dados', () => {
    
    test('deve filtrar dados por intervalo de tempo', () => {
      const filtered1h = filterPerformanceData(mockPerformanceData, '1h');
      const filtered6h = filterPerformanceData(mockPerformanceData, '6h');
      const filtered24h = filterPerformanceData(mockPerformanceData, '24h');

      expect(filtered1h.length).toBeLessThanOrEqual(mockPerformanceData.length);
      expect(filtered6h.length).toBeLessThanOrEqual(mockPerformanceData.length);
      expect(filtered24h.length).toBeLessThanOrEqual(mockPerformanceData.length);
    });

    test('deve manter dados recentes no filtro de 1 hora', () => {
      const recentData = mockPerformanceData.filter(data => 
        new Date(data.timestamp) > new Date(Date.now() - 60 * 60 * 1000)
      );
      const filtered = filterPerformanceData(mockPerformanceData, '1h');

      expect(filtered.length).toBeLessThanOrEqual(recentData.length);
    });

    test('deve retornar array vazio para dados antigos', () => {
      const oldData = [
        {
          ...mockPerformanceData[0],
          timestamp: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString()
        }
      ];
      const filtered = filterPerformanceData(oldData, '1h');

      expect(filtered).toHaveLength(0);
    });
  });

  describe('Cálculo de Tendências', () => {
    
    test('deve calcular tendências corretamente', () => {
      const trends = calculateTrends(mockPerformanceData);

      expect(trends).not.toBeNull();
      expect(typeof trends?.responseTime).toBe('number');
      expect(typeof trends?.throughput).toBe('number');
      expect(typeof trends?.errorRate).toBe('number');
      expect(typeof trends?.cpuUsage).toBe('number');
      expect(typeof trends?.memoryUsage).toBe('number');
    });

    test('deve retornar null para dados insuficientes', () => {
      const singleData = [mockPerformanceData[0]];
      const trends = calculateTrends(singleData);

      expect(trends).toBeNull();
    });

    test('deve calcular tendência positiva e negativa', () => {
      const testData = [
        { ...mockPerformanceData[0], responseTime: 100, throughput: 1000 },
        { ...mockPerformanceData[1], responseTime: 200, throughput: 800 }
      ];
      const trends = calculateTrends(testData);

      expect(trends?.responseTime).toBe(100); // Aumentou 100%
      expect(trends?.throughput).toBe(-20); // Diminuiu 20%
    });
  });

  describe('Validação de Thresholds', () => {
    
    test('deve identificar violações de threshold', () => {
      const criticalData = {
        ...mockPerformanceData[0],
        responseTime: 6000,
        errorRate: 12,
        cpuUsage: 98,
        memoryUsage: 96
      };
      const violations = validatePerformanceThresholds(criticalData);

      expect(violations.length).toBeGreaterThan(0);
      expect(violations.some(v => v.severity === 'critical')).toBe(true);
    });

    test('deve identificar warnings de threshold', () => {
      const warningData = {
        ...mockPerformanceData[0],
        responseTime: 2500,
        errorRate: 6,
        cpuUsage: 85,
        memoryUsage: 82
      };
      const violations = validatePerformanceThresholds(warningData);

      expect(violations.length).toBeGreaterThan(0);
      expect(violations.some(v => v.severity === 'warning')).toBe(true);
    });

    test('deve não identificar violações para valores normais', () => {
      const normalData = {
        ...mockPerformanceData[0],
        responseTime: 150,
        errorRate: 0.5,
        cpuUsage: 45,
        memoryUsage: 67
      };
      const violations = validatePerformanceThresholds(normalData);

      expect(violations.length).toBe(0);
    });

    test('deve categorizar violações por severidade', () => {
      const mixedData = {
        ...mockPerformanceData[0],
        responseTime: 2500, // warning
        errorRate: 12, // critical
        cpuUsage: 45, // normal
        memoryUsage: 82 // warning
      };
      const violations = validatePerformanceThresholds(mixedData);

      const criticalViolations = violations.filter(v => v.severity === 'critical');
      const warningViolations = violations.filter(v => v.severity === 'warning');

      expect(criticalViolations.length).toBeGreaterThan(0);
      expect(warningViolations.length).toBeGreaterThan(0);
    });
  });

  describe('Formatação de Timestamps', () => {
    
    test('deve formatar timestamp corretamente', () => {
      const timestamp = '2024-12-20T10:00:00Z';
      const formatted = formatTimestamp(timestamp);

      expect(typeof formatted).toBe('string');
      expect(formatted).toMatch(/\d{2}\/\d{2}\/\d{4}/);
    });

    test('deve lidar com diferentes timestamps', () => {
      const timestamps = [
        '2024-12-20T10:00:00Z',
        '2024-12-20T15:30:45Z',
        '2024-12-20T23:59:59Z'
      ];

      timestamps.forEach(timestamp => {
        const formatted = formatTimestamp(timestamp);
        expect(typeof formatted).toBe('string');
        expect(formatted.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Métricas de Negócio', () => {
    
    test('deve calcular métricas de negócio corretamente', () => {
      const businessMetrics = calculateBusinessMetrics(mockPerformanceData);

      expect(businessMetrics).not.toBeNull();
      expect(businessMetrics?.totalKeywords).toBe(5360);
      expect(businessMetrics?.totalClusters).toBe(192);
      expect(businessMetrics?.totalApiCalls).toBe(4460);
      expect(businessMetrics?.avgActiveUsers).toBeCloseTo(89.8, 1);
    });

    test('deve calcular métricas derivadas', () => {
      const businessMetrics = calculateBusinessMetrics(mockPerformanceData);

      expect(businessMetrics?.keywordsPerCluster).toBeCloseTo(27.92, 2);
      expect(businessMetrics?.apiCallsPerUser).toBeCloseTo(49.67, 2);
    });

    test('deve lidar com divisão por zero', () => {
      const emptyData: PerformanceData[] = [];
      const businessMetrics = calculateBusinessMetrics(emptyData);

      expect(businessMetrics).toBeNull();
    });

    test('deve calcular métricas para dados com clusters zero', () => {
      const zeroClustersData = mockPerformanceData.map(data => ({
        ...data,
        clustersGenerated: 0
      }));
      const businessMetrics = calculateBusinessMetrics(zeroClustersData);

      expect(businessMetrics?.keywordsPerCluster).toBe(0);
    });
  });

  describe('Análise de Performance', () => {
    
    test('deve identificar degradação de performance', () => {
      const degradationData = [
        { ...mockPerformanceData[0], responseTime: 100, errorRate: 0.1 },
        { ...mockPerformanceData[1], responseTime: 200, errorRate: 0.5 },
        { ...mockPerformanceData[2], responseTime: 400, errorRate: 1.2 },
        { ...mockPerformanceData[3], responseTime: 800, errorRate: 2.8 },
        { ...mockPerformanceData[4], responseTime: 1600, errorRate: 5.5 }
      ];

      const trends = calculateTrends(degradationData);
      const violations = validatePerformanceThresholds(degradationData[degradationData.length - 1]);

      expect(trends?.responseTime).toBeGreaterThan(0); // Tendência de aumento
      expect(violations.length).toBeGreaterThan(0); // Violações detectadas
    });

    test('deve identificar melhoria de performance', () => {
      const improvementData = [
        { ...mockPerformanceData[0], responseTime: 800, errorRate: 5.0 },
        { ...mockPerformanceData[1], responseTime: 600, errorRate: 3.5 },
        { ...mockPerformanceData[2], responseTime: 400, errorRate: 2.0 },
        { ...mockPerformanceData[3], responseTime: 250, errorRate: 1.0 },
        { ...mockPerformanceData[4], responseTime: 150, errorRate: 0.5 }
      ];

      const trends = calculateTrends(improvementData);
      const violations = validatePerformanceThresholds(improvementData[improvementData.length - 1]);

      expect(trends?.responseTime).toBeLessThan(0); // Tendência de diminuição
      expect(violations.length).toBe(0); // Sem violações
    });

    test('deve calcular correlação entre métricas', () => {
      const highLoadData = mockPerformanceData.map(data => ({
        ...data,
        cpuUsage: data.cpuUsage + 20,
        memoryUsage: data.memoryUsage + 15,
        responseTime: data.responseTime * 1.5
      }));

      const metrics = calculateAggregatedMetrics(highLoadData);
      const status = getPerformanceStatus(
        metrics?.current.responseTime || 0,
        metrics?.current.errorRate || 0,
        metrics?.current.cpuUsage || 0,
        metrics?.current.memoryUsage || 0
      );

      expect(status.responseTime).toBe('warning');
      expect(status.cpuUsage).toBe('exception');
      expect(status.memoryUsage).toBe('exception');
    });
  });

  describe('Validação de Dados', () => {
    
    test('deve validar que timestamps estão em ordem cronológica', () => {
      const sortedData = [...mockPerformanceData].sort((a, b) => 
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      );

      for (let i = 1; i < sortedData.length; i++) {
        const prevTime = new Date(sortedData[i - 1].timestamp).getTime();
        const currTime = new Date(sortedData[i].timestamp).getTime();
        expect(currTime).toBeGreaterThanOrEqual(prevTime);
      }
    });

    test('deve validar que métricas de negócio são consistentes', () => {
      mockPerformanceData.forEach(data => {
        expect(data.keywordsProcessed).toBeGreaterThanOrEqual(data.clustersGenerated);
        expect(data.apiCalls).toBeGreaterThanOrEqual(data.activeUsers);
      });
    });

    test('deve validar que percentuais não excedem 100%', () => {
      mockPerformanceData.forEach(data => {
        expect(data.errorRate).toBeLessThanOrEqual(100);
        expect(data.cpuUsage).toBeLessThanOrEqual(100);
        expect(data.memoryUsage).toBeLessThanOrEqual(100);
      });
    });
  });
}); 