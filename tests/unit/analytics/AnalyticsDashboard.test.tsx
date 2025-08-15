/**
 * Testes Unitários - AnalyticsDashboard Component
 * 
 * Prompt: Implementação de testes para componentes de analytics
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_ANALYTICS_DASHBOARD_012
 * 
 * Baseado em código real do componente AnalyticsDashboard.tsx
 */

import React from 'react';

// Interfaces extraídas do componente para teste
interface AnalyticsData {
  keywordsPerformance: {
    totalKeywords: number;
    activeKeywords: number;
    conversionRate: number;
    avgPosition: number;
    clickThroughRate: number;
    costPerClick: number;
    totalClicks: number;
    totalImpressions: number;
  };
  clusterEfficiency: {
    totalClusters: number;
    avgClusterSize: number;
    clusterQuality: number;
    semanticCoherence: number;
    performanceVariance: number;
  };
  userBehavior: {
    activeUsers: number;
    sessionDuration: number;
    pageViews: number;
    bounceRate: number;
    userEngagement: number;
  };
  predictiveInsights: {
    trendPrediction: number;
    seasonalityFactor: number;
    anomalyScore: number;
    recommendationConfidence: number;
    nextBestAction: string;
  };
}

// Dados mock extraídos do componente para teste
const mockAnalyticsData: AnalyticsData = {
  keywordsPerformance: {
    totalKeywords: 15420,
    activeKeywords: 12350,
    conversionRate: 0.045,
    avgPosition: 8.5,
    clickThroughRate: 0.032,
    costPerClick: 2.45,
    totalClicks: 45680,
    totalImpressions: 1425000
  },
  clusterEfficiency: {
    totalClusters: 342,
    avgClusterSize: 36.1,
    clusterQuality: 0.78,
    semanticCoherence: 0.82,
    performanceVariance: 0.15
  },
  userBehavior: {
    activeUsers: 2840,
    sessionDuration: 12.5,
    pageViews: 15680,
    bounceRate: 0.34,
    userEngagement: 0.67
  },
  predictiveInsights: {
    trendPrediction: 0.12,
    seasonalityFactor: 0.08,
    anomalyScore: 0.23,
    recommendationConfidence: 0.85,
    nextBestAction: 'Otimizar clusters de baixa performance e expandir keywords de alta conversão'
  }
};

// Funções utilitárias extraídas do componente
const calculatePerformanceScore = (data: AnalyticsData) => {
  return Math.round(
    (data.keywordsPerformance.conversionRate * 0.4) +
    (data.clusterEfficiency.clusterQuality * 0.3) +
    (data.userBehavior.userEngagement * 0.3)
  );
};

const calculateEfficiencyTrend = (semanticCoherence: number) => {
  return semanticCoherence > 0.8 ? 'up' : 'down';
};

const calculateRiskLevel = (anomalyScore: number) => {
  if (anomalyScore > 0.7) return 'high';
  if (anomalyScore > 0.4) return 'medium';
  return 'low';
};

const validateAnalyticsData = (data: AnalyticsData) => {
  const errors: string[] = [];

  // Validação de keywords
  if (data.keywordsPerformance.activeKeywords > data.keywordsPerformance.totalKeywords) {
    errors.push('Keywords ativas não podem ser maiores que total de keywords');
  }
  if (data.keywordsPerformance.conversionRate < 0 || data.keywordsPerformance.conversionRate > 1) {
    errors.push('Taxa de conversão deve estar entre 0 e 1');
  }
  if (data.keywordsPerformance.clickThroughRate < 0 || data.keywordsPerformance.clickThroughRate > 1) {
    errors.push('CTR deve estar entre 0 e 1');
  }
  if (data.keywordsPerformance.avgPosition < 1) {
    errors.push('Posição média deve ser maior que 0');
  }
  if (data.keywordsPerformance.costPerClick < 0) {
    errors.push('CPC deve ser positivo');
  }

  // Validação de clusters
  if (data.clusterEfficiency.totalClusters < 0) {
    errors.push('Total de clusters deve ser positivo');
  }
  if (data.clusterEfficiency.avgClusterSize < 1) {
    errors.push('Tamanho médio de cluster deve ser maior que 0');
  }
  if (data.clusterEfficiency.clusterQuality < 0 || data.clusterEfficiency.clusterQuality > 1) {
    errors.push('Qualidade de cluster deve estar entre 0 e 1');
  }
  if (data.clusterEfficiency.semanticCoherence < 0 || data.clusterEfficiency.semanticCoherence > 1) {
    errors.push('Coerência semântica deve estar entre 0 e 1');
  }
  if (data.clusterEfficiency.performanceVariance < 0 || data.clusterEfficiency.performanceVariance > 1) {
    errors.push('Variação de performance deve estar entre 0 e 1');
  }

  // Validação de comportamento do usuário
  if (data.userBehavior.activeUsers < 0) {
    errors.push('Usuários ativos deve ser positivo');
  }
  if (data.userBehavior.sessionDuration < 0) {
    errors.push('Duração da sessão deve ser positiva');
  }
  if (data.userBehavior.pageViews < 0) {
    errors.push('Page views deve ser positivo');
  }
  if (data.userBehavior.bounceRate < 0 || data.userBehavior.bounceRate > 1) {
    errors.push('Bounce rate deve estar entre 0 e 1');
  }
  if (data.userBehavior.userEngagement < 0 || data.userBehavior.userEngagement > 1) {
    errors.push('Engajamento do usuário deve estar entre 0 e 1');
  }

  // Validação de insights preditivos
  if (data.predictiveInsights.trendPrediction < -1 || data.predictiveInsights.trendPrediction > 1) {
    errors.push('Tendência predita deve estar entre -1 e 1');
  }
  if (data.predictiveInsights.seasonalityFactor < 0 || data.predictiveInsights.seasonalityFactor > 1) {
    errors.push('Fator sazonal deve estar entre 0 e 1');
  }
  if (data.predictiveInsights.anomalyScore < 0 || data.predictiveInsights.anomalyScore > 1) {
    errors.push('Score de anomalia deve estar entre 0 e 1');
  }
  if (data.predictiveInsights.recommendationConfidence < 0 || data.predictiveInsights.recommendationConfidence > 1) {
    errors.push('Confiança da recomendação deve estar entre 0 e 1');
  }
  if (!data.predictiveInsights.nextBestAction || data.predictiveInsights.nextBestAction.trim() === '') {
    errors.push('Próxima melhor ação não pode estar vazia');
  }

  return errors;
};

const calculateKeywordEfficiency = (data: AnalyticsData) => {
  const { keywordsPerformance } = data;
  
  return {
    activationRate: keywordsPerformance.activeKeywords / keywordsPerformance.totalKeywords,
    clickEfficiency: keywordsPerformance.totalClicks / keywordsPerformance.totalImpressions,
    costEfficiency: keywordsPerformance.totalClicks * keywordsPerformance.costPerClick,
    performanceRatio: keywordsPerformance.conversionRate / keywordsPerformance.clickThroughRate
  };
};

const calculateClusterMetrics = (data: AnalyticsData) => {
  const { clusterEfficiency } = data;
  
  return {
    totalKeywordsInClusters: clusterEfficiency.totalClusters * clusterEfficiency.avgClusterSize,
    efficiencyScore: clusterEfficiency.clusterQuality * clusterEfficiency.semanticCoherence,
    stabilityIndex: 1 - clusterEfficiency.performanceVariance,
    optimizationPotential: (1 - clusterEfficiency.clusterQuality) * 100
  };
};

const calculateUserMetrics = (data: AnalyticsData) => {
  const { userBehavior } = data;
  
  return {
    pagesPerSession: userBehavior.pageViews / userBehavior.activeUsers,
    engagementScore: userBehavior.userEngagement * (1 - userBehavior.bounceRate),
    retentionPotential: userBehavior.sessionDuration * userBehavior.userEngagement,
    conversionProbability: userBehavior.userEngagement * (1 - userBehavior.bounceRate)
  };
};

const analyzeTrends = (data: AnalyticsData) => {
  return {
    performanceTrend: data.predictiveInsights.trendPrediction > 0 ? 'positive' : 'negative',
    seasonalityImpact: data.predictiveInsights.seasonalityFactor > 0.1 ? 'high' : 'low',
    anomalyRisk: data.predictiveInsights.anomalyScore > 0.5 ? 'critical' : 'normal',
    confidenceLevel: data.predictiveInsights.recommendationConfidence > 0.8 ? 'high' : 'medium'
  };
};

const generateRecommendations = (data: AnalyticsData) => {
  const recommendations: string[] = [];
  
  if (data.keywordsPerformance.conversionRate < 0.03) {
    recommendations.push('Otimizar keywords de baixa conversão');
  }
  
  if (data.clusterEfficiency.clusterQuality < 0.7) {
    recommendations.push('Melhorar qualidade dos clusters');
  }
  
  if (data.userBehavior.bounceRate > 0.5) {
    recommendations.push('Reduzir taxa de rejeição');
  }
  
  if (data.predictiveInsights.anomalyScore > 0.3) {
    recommendations.push('Investigar anomalias detectadas');
  }
  
  return recommendations;
};

describe('AnalyticsDashboard - Dashboard de Analytics Avançado', () => {
  
  describe('Interface AnalyticsData - Validação de Estrutura', () => {
    
    test('deve validar estrutura do AnalyticsData', () => {
      const data: AnalyticsData = mockAnalyticsData;

      expect(data).toHaveProperty('keywordsPerformance');
      expect(data).toHaveProperty('clusterEfficiency');
      expect(data).toHaveProperty('userBehavior');
      expect(data).toHaveProperty('predictiveInsights');
      
      expect(data.keywordsPerformance).toHaveProperty('totalKeywords');
      expect(data.keywordsPerformance).toHaveProperty('activeKeywords');
      expect(data.keywordsPerformance).toHaveProperty('conversionRate');
      expect(data.keywordsPerformance).toHaveProperty('avgPosition');
      expect(data.keywordsPerformance).toHaveProperty('clickThroughRate');
      expect(data.keywordsPerformance).toHaveProperty('costPerClick');
      expect(data.keywordsPerformance).toHaveProperty('totalClicks');
      expect(data.keywordsPerformance).toHaveProperty('totalImpressions');
      
      expect(data.clusterEfficiency).toHaveProperty('totalClusters');
      expect(data.clusterEfficiency).toHaveProperty('avgClusterSize');
      expect(data.clusterEfficiency).toHaveProperty('clusterQuality');
      expect(data.clusterEfficiency).toHaveProperty('semanticCoherence');
      expect(data.clusterEfficiency).toHaveProperty('performanceVariance');
      
      expect(data.userBehavior).toHaveProperty('activeUsers');
      expect(data.userBehavior).toHaveProperty('sessionDuration');
      expect(data.userBehavior).toHaveProperty('pageViews');
      expect(data.userBehavior).toHaveProperty('bounceRate');
      expect(data.userBehavior).toHaveProperty('userEngagement');
      
      expect(data.predictiveInsights).toHaveProperty('trendPrediction');
      expect(data.predictiveInsights).toHaveProperty('seasonalityFactor');
      expect(data.predictiveInsights).toHaveProperty('anomalyScore');
      expect(data.predictiveInsights).toHaveProperty('recommendationConfidence');
      expect(data.predictiveInsights).toHaveProperty('nextBestAction');
    });

    test('deve validar tipos de dados corretos', () => {
      const data: AnalyticsData = mockAnalyticsData;

      // Keywords Performance
      expect(typeof data.keywordsPerformance.totalKeywords).toBe('number');
      expect(typeof data.keywordsPerformance.activeKeywords).toBe('number');
      expect(typeof data.keywordsPerformance.conversionRate).toBe('number');
      expect(typeof data.keywordsPerformance.avgPosition).toBe('number');
      expect(typeof data.keywordsPerformance.clickThroughRate).toBe('number');
      expect(typeof data.keywordsPerformance.costPerClick).toBe('number');
      expect(typeof data.keywordsPerformance.totalClicks).toBe('number');
      expect(typeof data.keywordsPerformance.totalImpressions).toBe('number');

      // Cluster Efficiency
      expect(typeof data.clusterEfficiency.totalClusters).toBe('number');
      expect(typeof data.clusterEfficiency.avgClusterSize).toBe('number');
      expect(typeof data.clusterEfficiency.clusterQuality).toBe('number');
      expect(typeof data.clusterEfficiency.semanticCoherence).toBe('number');
      expect(typeof data.clusterEfficiency.performanceVariance).toBe('number');

      // User Behavior
      expect(typeof data.userBehavior.activeUsers).toBe('number');
      expect(typeof data.userBehavior.sessionDuration).toBe('number');
      expect(typeof data.userBehavior.pageViews).toBe('number');
      expect(typeof data.userBehavior.bounceRate).toBe('number');
      expect(typeof data.userBehavior.userEngagement).toBe('number');

      // Predictive Insights
      expect(typeof data.predictiveInsights.trendPrediction).toBe('number');
      expect(typeof data.predictiveInsights.seasonalityFactor).toBe('number');
      expect(typeof data.predictiveInsights.anomalyScore).toBe('number');
      expect(typeof data.predictiveInsights.recommendationConfidence).toBe('number');
      expect(typeof data.predictiveInsights.nextBestAction).toBe('string');
    });
  });

  describe('Cálculo de Performance Score', () => {
    
    test('deve calcular performance score corretamente', () => {
      const score = calculatePerformanceScore(mockAnalyticsData);
      
      const expectedScore = Math.round(
        (mockAnalyticsData.keywordsPerformance.conversionRate * 0.4) +
        (mockAnalyticsData.clusterEfficiency.clusterQuality * 0.3) +
        (mockAnalyticsData.userBehavior.userEngagement * 0.3)
      );
      
      expect(score).toBe(expectedScore);
      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(100);
    });

    test('deve calcular score para dados de alta performance', () => {
      const highPerformanceData: AnalyticsData = {
        ...mockAnalyticsData,
        keywordsPerformance: {
          ...mockAnalyticsData.keywordsPerformance,
          conversionRate: 0.15
        },
        clusterEfficiency: {
          ...mockAnalyticsData.clusterEfficiency,
          clusterQuality: 0.95
        },
        userBehavior: {
          ...mockAnalyticsData.userBehavior,
          userEngagement: 0.90
        }
      };

      const score = calculatePerformanceScore(highPerformanceData);
      expect(score).toBeGreaterThan(80);
    });

    test('deve calcular score para dados de baixa performance', () => {
      const lowPerformanceData: AnalyticsData = {
        ...mockAnalyticsData,
        keywordsPerformance: {
          ...mockAnalyticsData.keywordsPerformance,
          conversionRate: 0.01
        },
        clusterEfficiency: {
          ...mockAnalyticsData.clusterEfficiency,
          clusterQuality: 0.30
        },
        userBehavior: {
          ...mockAnalyticsData.userBehavior,
          userEngagement: 0.20
        }
      };

      const score = calculatePerformanceScore(lowPerformanceData);
      expect(score).toBeLessThan(50);
    });
  });

  describe('Cálculo de Tendência de Eficiência', () => {
    
    test('deve determinar tendência positiva para coerência alta', () => {
      const trend = calculateEfficiencyTrend(0.85);
      expect(trend).toBe('up');
    });

    test('deve determinar tendência negativa para coerência baixa', () => {
      const trend = calculateEfficiencyTrend(0.75);
      expect(trend).toBe('down');
    });

    test('deve determinar tendência negativa para coerência no limite', () => {
      const trend = calculateEfficiencyTrend(0.80);
      expect(trend).toBe('down');
    });

    test('deve determinar tendência positiva para coerência acima do limite', () => {
      const trend = calculateEfficiencyTrend(0.81);
      expect(trend).toBe('up');
    });
  });

  describe('Cálculo de Nível de Risco', () => {
    
    test('deve determinar risco baixo para score baixo', () => {
      const risk = calculateRiskLevel(0.2);
      expect(risk).toBe('low');
    });

    test('deve determinar risco médio para score médio', () => {
      const risk = calculateRiskLevel(0.5);
      expect(risk).toBe('medium');
    });

    test('deve determinar risco alto para score alto', () => {
      const risk = calculateRiskLevel(0.8);
      expect(risk).toBe('high');
    });

    test('deve determinar risco médio para score no limite inferior', () => {
      const risk = calculateRiskLevel(0.4);
      expect(risk).toBe('medium');
    });

    test('deve determinar risco alto para score no limite superior', () => {
      const risk = calculateRiskLevel(0.7);
      expect(risk).toBe('high');
    });
  });

  describe('Validação de Dados de Analytics', () => {
    
    test('deve validar dados corretos sem erros', () => {
      const errors = validateAnalyticsData(mockAnalyticsData);
      expect(errors).toHaveLength(0);
    });

    test('deve detectar keywords ativas maiores que total', () => {
      const invalidData: AnalyticsData = {
        ...mockAnalyticsData,
        keywordsPerformance: {
          ...mockAnalyticsData.keywordsPerformance,
          activeKeywords: 20000,
          totalKeywords: 15000
        }
      };
      
      const errors = validateAnalyticsData(invalidData);
      expect(errors).toContain('Keywords ativas não podem ser maiores que total de keywords');
    });

    test('deve detectar taxa de conversão inválida', () => {
      const invalidData: AnalyticsData = {
        ...mockAnalyticsData,
        keywordsPerformance: {
          ...mockAnalyticsData.keywordsPerformance,
          conversionRate: 1.5
        }
      };
      
      const errors = validateAnalyticsData(invalidData);
      expect(errors).toContain('Taxa de conversão deve estar entre 0 e 1');
    });

    test('deve detectar CTR inválido', () => {
      const invalidData: AnalyticsData = {
        ...mockAnalyticsData,
        keywordsPerformance: {
          ...mockAnalyticsData.keywordsPerformance,
          clickThroughRate: -0.1
        }
      };
      
      const errors = validateAnalyticsData(invalidData);
      expect(errors).toContain('CTR deve estar entre 0 e 1');
    });

    test('deve detectar posição média inválida', () => {
      const invalidData: AnalyticsData = {
        ...mockAnalyticsData,
        keywordsPerformance: {
          ...mockAnalyticsData.keywordsPerformance,
          avgPosition: 0
        }
      };
      
      const errors = validateAnalyticsData(invalidData);
      expect(errors).toContain('Posição média deve ser maior que 0');
    });

    test('deve detectar CPC negativo', () => {
      const invalidData: AnalyticsData = {
        ...mockAnalyticsData,
        keywordsPerformance: {
          ...mockAnalyticsData.keywordsPerformance,
          costPerClick: -1.0
        }
      };
      
      const errors = validateAnalyticsData(invalidData);
      expect(errors).toContain('CPC deve ser positivo');
    });

    test('deve detectar qualidade de cluster inválida', () => {
      const invalidData: AnalyticsData = {
        ...mockAnalyticsData,
        clusterEfficiency: {
          ...mockAnalyticsData.clusterEfficiency,
          clusterQuality: 1.2
        }
      };
      
      const errors = validateAnalyticsData(invalidData);
      expect(errors).toContain('Qualidade de cluster deve estar entre 0 e 1');
    });

    test('deve detectar bounce rate inválido', () => {
      const invalidData: AnalyticsData = {
        ...mockAnalyticsData,
        userBehavior: {
          ...mockAnalyticsData.userBehavior,
          bounceRate: 1.5
        }
      };
      
      const errors = validateAnalyticsData(invalidData);
      expect(errors).toContain('Bounce rate deve estar entre 0 e 1');
    });

    test('deve detectar score de anomalia inválido', () => {
      const invalidData: AnalyticsData = {
        ...mockAnalyticsData,
        predictiveInsights: {
          ...mockAnalyticsData.predictiveInsights,
          anomalyScore: -0.1
        }
      };
      
      const errors = validateAnalyticsData(invalidData);
      expect(errors).toContain('Score de anomalia deve estar entre 0 e 1');
    });

    test('deve detectar próxima melhor ação vazia', () => {
      const invalidData: AnalyticsData = {
        ...mockAnalyticsData,
        predictiveInsights: {
          ...mockAnalyticsData.predictiveInsights,
          nextBestAction: ''
        }
      };
      
      const errors = validateAnalyticsData(invalidData);
      expect(errors).toContain('Próxima melhor ação não pode estar vazia');
    });
  });

  describe('Cálculo de Eficiência de Keywords', () => {
    
    test('deve calcular métricas de eficiência de keywords', () => {
      const efficiency = calculateKeywordEfficiency(mockAnalyticsData);

      expect(efficiency.activationRate).toBeCloseTo(0.801, 3);
      expect(efficiency.clickEfficiency).toBeCloseTo(0.032, 3);
      expect(efficiency.costEfficiency).toBeCloseTo(111916, 0);
      expect(efficiency.performanceRatio).toBeCloseTo(1.406, 3);
    });

    test('deve calcular taxa de ativação corretamente', () => {
      const efficiency = calculateKeywordEfficiency(mockAnalyticsData);
      const expectedActivationRate = mockAnalyticsData.keywordsPerformance.activeKeywords / 
                                    mockAnalyticsData.keywordsPerformance.totalKeywords;
      
      expect(efficiency.activationRate).toBe(expectedActivationRate);
    });

    test('deve calcular eficiência de clicks corretamente', () => {
      const efficiency = calculateKeywordEfficiency(mockAnalyticsData);
      const expectedClickEfficiency = mockAnalyticsData.keywordsPerformance.totalClicks / 
                                     mockAnalyticsData.keywordsPerformance.totalImpressions;
      
      expect(efficiency.clickEfficiency).toBe(expectedClickEfficiency);
    });
  });

  describe('Cálculo de Métricas de Clusters', () => {
    
    test('deve calcular métricas de clusters', () => {
      const metrics = calculateClusterMetrics(mockAnalyticsData);

      expect(metrics.totalKeywordsInClusters).toBeCloseTo(12346.2, 1);
      expect(metrics.efficiencyScore).toBeCloseTo(0.640, 3);
      expect(metrics.stabilityIndex).toBeCloseTo(0.850, 3);
      expect(metrics.optimizationPotential).toBeCloseTo(22.0, 1);
    });

    test('deve calcular total de keywords em clusters', () => {
      const metrics = calculateClusterMetrics(mockAnalyticsData);
      const expectedTotal = mockAnalyticsData.clusterEfficiency.totalClusters * 
                           mockAnalyticsData.clusterEfficiency.avgClusterSize;
      
      expect(metrics.totalKeywordsInClusters).toBe(expectedTotal);
    });

    test('deve calcular score de eficiência', () => {
      const metrics = calculateClusterMetrics(mockAnalyticsData);
      const expectedScore = mockAnalyticsData.clusterEfficiency.clusterQuality * 
                           mockAnalyticsData.clusterEfficiency.semanticCoherence;
      
      expect(metrics.efficiencyScore).toBe(expectedScore);
    });
  });

  describe('Cálculo de Métricas de Usuário', () => {
    
    test('deve calcular métricas de usuário', () => {
      const metrics = calculateUserMetrics(mockAnalyticsData);

      expect(metrics.pagesPerSession).toBeCloseTo(5.521, 3);
      expect(metrics.engagementScore).toBeCloseTo(0.442, 3);
      expect(metrics.retentionPotential).toBeCloseTo(8.375, 3);
      expect(metrics.conversionProbability).toBeCloseTo(0.442, 3);
    });

    test('deve calcular páginas por sessão', () => {
      const metrics = calculateUserMetrics(mockAnalyticsData);
      const expectedPagesPerSession = mockAnalyticsData.userBehavior.pageViews / 
                                     mockAnalyticsData.userBehavior.activeUsers;
      
      expect(metrics.pagesPerSession).toBe(expectedPagesPerSession);
    });

    test('deve calcular score de engajamento', () => {
      const metrics = calculateUserMetrics(mockAnalyticsData);
      const expectedEngagementScore = mockAnalyticsData.userBehavior.userEngagement * 
                                     (1 - mockAnalyticsData.userBehavior.bounceRate);
      
      expect(metrics.engagementScore).toBe(expectedEngagementScore);
    });
  });

  describe('Análise de Tendências', () => {
    
    test('deve analisar tendências corretamente', () => {
      const trends = analyzeTrends(mockAnalyticsData);

      expect(trends.performanceTrend).toBe('positive');
      expect(trends.seasonalityImpact).toBe('low');
      expect(trends.anomalyRisk).toBe('normal');
      expect(trends.confidenceLevel).toBe('high');
    });

    test('deve identificar tendência negativa', () => {
      const negativeData: AnalyticsData = {
        ...mockAnalyticsData,
        predictiveInsights: {
          ...mockAnalyticsData.predictiveInsights,
          trendPrediction: -0.15
        }
      };
      
      const trends = analyzeTrends(negativeData);
      expect(trends.performanceTrend).toBe('negative');
    });

    test('deve identificar impacto sazonal alto', () => {
      const seasonalData: AnalyticsData = {
        ...mockAnalyticsData,
        predictiveInsights: {
          ...mockAnalyticsData.predictiveInsights,
          seasonalityFactor: 0.15
        }
      };
      
      const trends = analyzeTrends(seasonalData);
      expect(trends.seasonalityImpact).toBe('high');
    });

    test('deve identificar risco crítico de anomalia', () => {
      const anomalyData: AnalyticsData = {
        ...mockAnalyticsData,
        predictiveInsights: {
          ...mockAnalyticsData.predictiveInsights,
          anomalyScore: 0.75
        }
      };
      
      const trends = analyzeTrends(anomalyData);
      expect(trends.anomalyRisk).toBe('critical');
    });
  });

  describe('Geração de Recomendações', () => {
    
    test('deve gerar recomendações baseadas nos dados', () => {
      const recommendations = generateRecommendations(mockAnalyticsData);
      
      expect(Array.isArray(recommendations)).toBe(true);
      expect(recommendations.length).toBeGreaterThan(0);
    });

    test('deve recomendar otimização para baixa conversão', () => {
      const lowConversionData: AnalyticsData = {
        ...mockAnalyticsData,
        keywordsPerformance: {
          ...mockAnalyticsData.keywordsPerformance,
          conversionRate: 0.02
        }
      };
      
      const recommendations = generateRecommendations(lowConversionData);
      expect(recommendations).toContain('Otimizar keywords de baixa conversão');
    });

    test('deve recomendar melhoria de clusters para baixa qualidade', () => {
      const lowQualityData: AnalyticsData = {
        ...mockAnalyticsData,
        clusterEfficiency: {
          ...mockAnalyticsData.clusterEfficiency,
          clusterQuality: 0.65
        }
      };
      
      const recommendations = generateRecommendations(lowQualityData);
      expect(recommendations).toContain('Melhorar qualidade dos clusters');
    });

    test('deve recomendar redução de bounce rate', () => {
      const highBounceData: AnalyticsData = {
        ...mockAnalyticsData,
        userBehavior: {
          ...mockAnalyticsData.userBehavior,
          bounceRate: 0.65
        }
      };
      
      const recommendations = generateRecommendations(highBounceData);
      expect(recommendations).toContain('Reduzir taxa de rejeição');
    });

    test('deve recomendar investigação de anomalias', () => {
      const anomalyData: AnalyticsData = {
        ...mockAnalyticsData,
        predictiveInsights: {
          ...mockAnalyticsData.predictiveInsights,
          anomalyScore: 0.45
        }
      };
      
      const recommendations = generateRecommendations(anomalyData);
      expect(recommendations).toContain('Investigar anomalias detectadas');
    });

    test('deve gerar múltiplas recomendações quando necessário', () => {
      const problematicData: AnalyticsData = {
        ...mockAnalyticsData,
        keywordsPerformance: {
          ...mockAnalyticsData.keywordsPerformance,
          conversionRate: 0.02
        },
        clusterEfficiency: {
          ...mockAnalyticsData.clusterEfficiency,
          clusterQuality: 0.65
        },
        userBehavior: {
          ...mockAnalyticsData.userBehavior,
          bounceRate: 0.65
        },
        predictiveInsights: {
          ...mockAnalyticsData.predictiveInsights,
          anomalyScore: 0.45
        }
      };
      
      const recommendations = generateRecommendations(problematicData);
      expect(recommendations.length).toBe(4);
    });
  });

  describe('Validação de Consistência de Dados', () => {
    
    test('deve validar consistência entre métricas relacionadas', () => {
      const data = mockAnalyticsData;
      
      // Keywords ativas devem ser menor ou igual ao total
      expect(data.keywordsPerformance.activeKeywords).toBeLessThanOrEqual(data.keywordsPerformance.totalKeywords);
      
      // Total de clicks deve ser menor ou igual ao total de impressões
      expect(data.keywordsPerformance.totalClicks).toBeLessThanOrEqual(data.keywordsPerformance.totalImpressions);
      
      // CTR deve ser igual a clicks/impressões
      const calculatedCTR = data.keywordsPerformance.totalClicks / data.keywordsPerformance.totalImpressions;
      expect(data.keywordsPerformance.clickThroughRate).toBeCloseTo(calculatedCTR, 3);
      
      // Duração da sessão deve ser positiva
      expect(data.userBehavior.sessionDuration).toBeGreaterThan(0);
      
      // Page views deve ser maior ou igual aos usuários ativos
      expect(data.userBehavior.pageViews).toBeGreaterThanOrEqual(data.userBehavior.activeUsers);
    });

    test('deve validar que percentuais estão em escala correta', () => {
      const data = mockAnalyticsData;
      
      // Taxas devem estar entre 0 e 1
      expect(data.keywordsPerformance.conversionRate).toBeGreaterThanOrEqual(0);
      expect(data.keywordsPerformance.conversionRate).toBeLessThanOrEqual(1);
      expect(data.keywordsPerformance.clickThroughRate).toBeGreaterThanOrEqual(0);
      expect(data.keywordsPerformance.clickThroughRate).toBeLessThanOrEqual(1);
      expect(data.userBehavior.bounceRate).toBeGreaterThanOrEqual(0);
      expect(data.userBehavior.bounceRate).toBeLessThanOrEqual(1);
      expect(data.userBehavior.userEngagement).toBeGreaterThanOrEqual(0);
      expect(data.userBehavior.userEngagement).toBeLessThanOrEqual(1);
      
      // Qualidades devem estar entre 0 e 1
      expect(data.clusterEfficiency.clusterQuality).toBeGreaterThanOrEqual(0);
      expect(data.clusterEfficiency.clusterQuality).toBeLessThanOrEqual(1);
      expect(data.clusterEfficiency.semanticCoherence).toBeGreaterThanOrEqual(0);
      expect(data.clusterEfficiency.semanticCoherence).toBeLessThanOrEqual(1);
      expect(data.clusterEfficiency.performanceVariance).toBeGreaterThanOrEqual(0);
      expect(data.clusterEfficiency.performanceVariance).toBeLessThanOrEqual(1);
    });
  });
}); 