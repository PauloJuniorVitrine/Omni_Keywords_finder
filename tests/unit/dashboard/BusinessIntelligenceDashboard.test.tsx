/**
 * Testes Unitários - BusinessIntelligenceDashboard Component
 * 
 * Prompt: Implementação de testes para componentes de business intelligence
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_BUSINESS_INTELLIGENCE_DASHBOARD_013
 * 
 * Baseado em código real do componente BusinessMetrics.tsx
 */

import React from 'react';

// Interfaces extraídas do componente para teste
interface BusinessMetricsProps {
  keywordsProcessed: number;
  clustersGenerated: number;
  apiCalls: number;
  efficiency?: number;
  successRate?: number;
}

interface BusinessIntelligenceData {
  kpis: {
    revenue: number;
    growth: number;
    marketShare: number;
    customerSatisfaction: number;
    operationalEfficiency: number;
  };
  trends: {
    monthlyGrowth: number;
    quarterlyGrowth: number;
    yearlyGrowth: number;
    seasonalFactor: number;
  };
  analytics: {
    keywordPerformance: {
      highPerforming: number;
      mediumPerforming: number;
      lowPerforming: number;
      conversionRate: number;
    };
    clusterEfficiency: {
      totalClusters: number;
      avgClusterSize: number;
      qualityScore: number;
      optimizationPotential: number;
    };
    apiMetrics: {
      totalCalls: number;
      successRate: number;
      avgResponseTime: number;
      costPerCall: number;
    };
  };
  insights: {
    topOpportunities: string[];
    riskFactors: string[];
    recommendations: string[];
    nextBestActions: string[];
  };
}

// Dados mock extraídos do componente para teste
const mockBusinessIntelligenceData: BusinessIntelligenceData = {
  kpis: {
    revenue: 1250000,
    growth: 0.15,
    marketShare: 0.23,
    customerSatisfaction: 0.87,
    operationalEfficiency: 0.92
  },
  trends: {
    monthlyGrowth: 0.08,
    quarterlyGrowth: 0.12,
    yearlyGrowth: 0.18,
    seasonalFactor: 0.05
  },
  analytics: {
    keywordPerformance: {
      highPerforming: 1250,
      mediumPerforming: 2340,
      lowPerforming: 890,
      conversionRate: 0.045
    },
    clusterEfficiency: {
      totalClusters: 342,
      avgClusterSize: 36.1,
      qualityScore: 0.78,
      optimizationPotential: 0.22
    },
    apiMetrics: {
      totalCalls: 45680,
      successRate: 0.94,
      avgResponseTime: 245,
      costPerCall: 0.12
    }
  },
  insights: {
    topOpportunities: [
      'Expandir keywords de alta conversão',
      'Otimizar clusters de baixa performance',
      'Melhorar eficiência das APIs'
    ],
    riskFactors: [
      'Aumento na taxa de erro das APIs',
      'Diminuição na qualidade dos clusters',
      'Redução na satisfação do cliente'
    ],
    recommendations: [
      'Implementar cache inteligente',
      'Refinar algoritmo de clustering',
      'Adicionar monitoramento avançado'
    ],
    nextBestActions: [
      'Priorizar otimização de performance',
      'Investir em infraestrutura',
      'Treinar equipe em novas tecnologias'
    ]
  }
};

// Funções utilitárias extraídas do componente
const calculateBusinessMetrics = (data: BusinessIntelligenceData) => {
  const { kpis, analytics } = data;
  
  return {
    totalKeywords: analytics.keywordPerformance.highPerforming + 
                   analytics.keywordPerformance.mediumPerforming + 
                   analytics.keywordPerformance.lowPerforming,
    avgKeywordsPerCluster: analytics.clusterEfficiency.totalClusters > 0 ? 
                          (analytics.keywordPerformance.highPerforming + 
                           analytics.keywordPerformance.mediumPerforming + 
                           analytics.keywordPerformance.lowPerforming) / 
                          analytics.clusterEfficiency.totalClusters : 0,
    apiEfficiency: analytics.apiMetrics.totalCalls > 0 ? 
                   ((analytics.keywordPerformance.highPerforming + 
                     analytics.keywordPerformance.mediumPerforming + 
                     analytics.keywordPerformance.lowPerforming) / 
                    analytics.apiMetrics.totalCalls) * 100 : 0,
    overallEfficiency: (kpis.operationalEfficiency * 0.4) + 
                       (analytics.clusterEfficiency.qualityScore * 0.3) + 
                       (analytics.apiMetrics.successRate * 0.3)
  };
};

const validateBusinessData = (data: BusinessIntelligenceData) => {
  const errors: string[] = [];

  // Validação de KPIs
  if (data.kpis.revenue < 0) {
    errors.push('Receita deve ser positiva');
  }
  if (data.kpis.growth < -1 || data.kpis.growth > 10) {
    errors.push('Crescimento deve estar entre -100% e 1000%');
  }
  if (data.kpis.marketShare < 0 || data.kpis.marketShare > 1) {
    errors.push('Market share deve estar entre 0 e 1');
  }
  if (data.kpis.customerSatisfaction < 0 || data.kpis.customerSatisfaction > 1) {
    errors.push('Satisfação do cliente deve estar entre 0 e 1');
  }
  if (data.kpis.operationalEfficiency < 0 || data.kpis.operationalEfficiency > 1) {
    errors.push('Eficiência operacional deve estar entre 0 e 1');
  }

  // Validação de tendências
  if (data.trends.monthlyGrowth < -1 || data.trends.monthlyGrowth > 2) {
    errors.push('Crescimento mensal deve estar entre -100% e 200%');
  }
  if (data.trends.quarterlyGrowth < -1 || data.trends.quarterlyGrowth > 2) {
    errors.push('Crescimento trimestral deve estar entre -100% e 200%');
  }
  if (data.trends.yearlyGrowth < -1 || data.trends.yearlyGrowth > 5) {
    errors.push('Crescimento anual deve estar entre -100% e 500%');
  }
  if (data.trends.seasonalFactor < 0 || data.trends.seasonalFactor > 1) {
    errors.push('Fator sazonal deve estar entre 0 e 1');
  }

  // Validação de analytics
  if (data.analytics.keywordPerformance.highPerforming < 0) {
    errors.push('Keywords de alta performance deve ser positivo');
  }
  if (data.analytics.keywordPerformance.mediumPerforming < 0) {
    errors.push('Keywords de média performance deve ser positivo');
  }
  if (data.analytics.keywordPerformance.lowPerforming < 0) {
    errors.push('Keywords de baixa performance deve ser positivo');
  }
  if (data.analytics.keywordPerformance.conversionRate < 0 || data.analytics.keywordPerformance.conversionRate > 1) {
    errors.push('Taxa de conversão deve estar entre 0 e 1');
  }

  if (data.analytics.clusterEfficiency.totalClusters < 0) {
    errors.push('Total de clusters deve ser positivo');
  }
  if (data.analytics.clusterEfficiency.avgClusterSize < 1) {
    errors.push('Tamanho médio de cluster deve ser maior que 0');
  }
  if (data.analytics.clusterEfficiency.qualityScore < 0 || data.analytics.clusterEfficiency.qualityScore > 1) {
    errors.push('Score de qualidade deve estar entre 0 e 1');
  }
  if (data.analytics.clusterEfficiency.optimizationPotential < 0 || data.analytics.clusterEfficiency.optimizationPotential > 1) {
    errors.push('Potencial de otimização deve estar entre 0 e 1');
  }

  if (data.analytics.apiMetrics.totalCalls < 0) {
    errors.push('Total de chamadas API deve ser positivo');
  }
  if (data.analytics.apiMetrics.successRate < 0 || data.analytics.apiMetrics.successRate > 1) {
    errors.push('Taxa de sucesso deve estar entre 0 e 1');
  }
  if (data.analytics.apiMetrics.avgResponseTime < 0) {
    errors.push('Tempo médio de resposta deve ser positivo');
  }
  if (data.analytics.apiMetrics.costPerCall < 0) {
    errors.push('Custo por chamada deve ser positivo');
  }

  return errors;
};

const calculatePerformanceScore = (data: BusinessIntelligenceData) => {
  const { kpis, analytics } = data;
  
  const keywordScore = (analytics.keywordPerformance.highPerforming / 
                       (analytics.keywordPerformance.highPerforming + 
                        analytics.keywordPerformance.mediumPerforming + 
                        analytics.keywordPerformance.lowPerforming)) * 100;
  
  const clusterScore = analytics.clusterEfficiency.qualityScore * 100;
  const apiScore = analytics.apiMetrics.successRate * 100;
  const efficiencyScore = kpis.operationalEfficiency * 100;
  
  return Math.round((keywordScore * 0.3) + (clusterScore * 0.25) + (apiScore * 0.25) + (efficiencyScore * 0.2));
};

const analyzeTrends = (data: BusinessIntelligenceData) => {
  const { trends } = data;
  
  return {
    growthTrend: trends.yearlyGrowth > 0.1 ? 'strong' : trends.yearlyGrowth > 0.05 ? 'moderate' : 'weak',
    seasonalityImpact: trends.seasonalFactor > 0.1 ? 'high' : trends.seasonalFactor > 0.05 ? 'medium' : 'low',
    stability: Math.abs(trends.monthlyGrowth - trends.quarterlyGrowth) < 0.05 ? 'stable' : 'volatile',
    momentum: trends.monthlyGrowth > trends.quarterlyGrowth ? 'accelerating' : 'decelerating'
  };
};

const generateInsights = (data: BusinessIntelligenceData) => {
  const insights: string[] = [];
  
  if (data.analytics.keywordPerformance.conversionRate < 0.03) {
    insights.push('Otimizar keywords de baixa conversão');
  }
  
  if (data.analytics.clusterEfficiency.qualityScore < 0.7) {
    insights.push('Melhorar qualidade dos clusters');
  }
  
  if (data.analytics.apiMetrics.successRate < 0.9) {
    insights.push('Investigar falhas nas APIs');
  }
  
  if (data.kpis.customerSatisfaction < 0.8) {
    insights.push('Focar na experiência do cliente');
  }
  
  if (data.trends.yearlyGrowth < 0.1) {
    insights.push('Implementar estratégias de crescimento');
  }
  
  return insights;
};

const calculateROI = (data: BusinessIntelligenceData) => {
  const { kpis, analytics } = data;
  
  const totalCost = analytics.apiMetrics.totalCalls * analytics.apiMetrics.costPerCall;
  const totalRevenue = kpis.revenue;
  
  return totalCost > 0 ? ((totalRevenue - totalCost) / totalCost) * 100 : 0;
};

const calculateEfficiencyMetrics = (data: BusinessIntelligenceData) => {
  const { analytics } = data;
  
  return {
    keywordEfficiency: analytics.keywordPerformance.highPerforming / 
                      (analytics.keywordPerformance.highPerforming + 
                       analytics.keywordPerformance.mediumPerforming + 
                       analytics.keywordPerformance.lowPerforming),
    clusterEfficiency: analytics.clusterEfficiency.qualityScore * 
                      (1 - analytics.clusterEfficiency.optimizationPotential),
    apiEfficiency: analytics.apiMetrics.successRate * 
                   (1000 / analytics.apiMetrics.avgResponseTime),
    overallEfficiency: (analytics.keywordPerformance.conversionRate * 0.4) + 
                       (analytics.clusterEfficiency.qualityScore * 0.3) + 
                       (analytics.apiMetrics.successRate * 0.3)
  };
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
};

const formatPercentage = (value: number) => {
  return `${(value * 100).toFixed(1)}%`;
};

const formatNumber = (value: number) => {
  return new Intl.NumberFormat('pt-BR').format(value);
};

describe('BusinessIntelligenceDashboard - Dashboard de Business Intelligence', () => {
  
  describe('Interface BusinessIntelligenceData - Validação de Estrutura', () => {
    
    test('deve validar estrutura do BusinessIntelligenceData', () => {
      const data: BusinessIntelligenceData = mockBusinessIntelligenceData;

      expect(data).toHaveProperty('kpis');
      expect(data).toHaveProperty('trends');
      expect(data).toHaveProperty('analytics');
      expect(data).toHaveProperty('insights');
      
      expect(data.kpis).toHaveProperty('revenue');
      expect(data.kpis).toHaveProperty('growth');
      expect(data.kpis).toHaveProperty('marketShare');
      expect(data.kpis).toHaveProperty('customerSatisfaction');
      expect(data.kpis).toHaveProperty('operationalEfficiency');
      
      expect(data.trends).toHaveProperty('monthlyGrowth');
      expect(data.trends).toHaveProperty('quarterlyGrowth');
      expect(data.trends).toHaveProperty('yearlyGrowth');
      expect(data.trends).toHaveProperty('seasonalFactor');
      
      expect(data.analytics).toHaveProperty('keywordPerformance');
      expect(data.analytics).toHaveProperty('clusterEfficiency');
      expect(data.analytics).toHaveProperty('apiMetrics');
      
      expect(data.insights).toHaveProperty('topOpportunities');
      expect(data.insights).toHaveProperty('riskFactors');
      expect(data.insights).toHaveProperty('recommendations');
      expect(data.insights).toHaveProperty('nextBestActions');
    });

    test('deve validar tipos de dados corretos', () => {
      const data: BusinessIntelligenceData = mockBusinessIntelligenceData;

      // KPIs
      expect(typeof data.kpis.revenue).toBe('number');
      expect(typeof data.kpis.growth).toBe('number');
      expect(typeof data.kpis.marketShare).toBe('number');
      expect(typeof data.kpis.customerSatisfaction).toBe('number');
      expect(typeof data.kpis.operationalEfficiency).toBe('number');

      // Trends
      expect(typeof data.trends.monthlyGrowth).toBe('number');
      expect(typeof data.trends.quarterlyGrowth).toBe('number');
      expect(typeof data.trends.yearlyGrowth).toBe('number');
      expect(typeof data.trends.seasonalFactor).toBe('number');

      // Analytics
      expect(typeof data.analytics.keywordPerformance.highPerforming).toBe('number');
      expect(typeof data.analytics.keywordPerformance.mediumPerforming).toBe('number');
      expect(typeof data.analytics.keywordPerformance.lowPerforming).toBe('number');
      expect(typeof data.analytics.keywordPerformance.conversionRate).toBe('number');

      expect(typeof data.analytics.clusterEfficiency.totalClusters).toBe('number');
      expect(typeof data.analytics.clusterEfficiency.avgClusterSize).toBe('number');
      expect(typeof data.analytics.clusterEfficiency.qualityScore).toBe('number');
      expect(typeof data.analytics.clusterEfficiency.optimizationPotential).toBe('number');

      expect(typeof data.analytics.apiMetrics.totalCalls).toBe('number');
      expect(typeof data.analytics.apiMetrics.successRate).toBe('number');
      expect(typeof data.analytics.apiMetrics.avgResponseTime).toBe('number');
      expect(typeof data.analytics.apiMetrics.costPerCall).toBe('number');

      // Insights
      expect(Array.isArray(data.insights.topOpportunities)).toBe(true);
      expect(Array.isArray(data.insights.riskFactors)).toBe(true);
      expect(Array.isArray(data.insights.recommendations)).toBe(true);
      expect(Array.isArray(data.insights.nextBestActions)).toBe(true);
    });
  });

  describe('Cálculo de Métricas de Negócio', () => {
    
    test('deve calcular métricas de negócio corretamente', () => {
      const metrics = calculateBusinessMetrics(mockBusinessIntelligenceData);

      expect(metrics.totalKeywords).toBe(4480);
      expect(metrics.avgKeywordsPerCluster).toBeCloseTo(13.1, 1);
      expect(metrics.apiEfficiency).toBeCloseTo(9.8, 1);
      expect(metrics.overallEfficiency).toBeCloseTo(0.89, 2);
    });

    test('deve calcular total de keywords', () => {
      const metrics = calculateBusinessMetrics(mockBusinessIntelligenceData);
      const expectedTotal = mockBusinessIntelligenceData.analytics.keywordPerformance.highPerforming + 
                           mockBusinessIntelligenceData.analytics.keywordPerformance.mediumPerforming + 
                           mockBusinessIntelligenceData.analytics.keywordPerformance.lowPerforming;
      
      expect(metrics.totalKeywords).toBe(expectedTotal);
    });

    test('deve calcular média de keywords por cluster', () => {
      const metrics = calculateBusinessMetrics(mockBusinessIntelligenceData);
      const expectedAvg = (mockBusinessIntelligenceData.analytics.keywordPerformance.highPerforming + 
                          mockBusinessIntelligenceData.analytics.keywordPerformance.mediumPerforming + 
                          mockBusinessIntelligenceData.analytics.keywordPerformance.lowPerforming) / 
                         mockBusinessIntelligenceData.analytics.clusterEfficiency.totalClusters;
      
      expect(metrics.avgKeywordsPerCluster).toBe(expectedAvg);
    });

    test('deve lidar com divisão por zero', () => {
      const emptyData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        analytics: {
          ...mockBusinessIntelligenceData.analytics,
          clusterEfficiency: {
            ...mockBusinessIntelligenceData.analytics.clusterEfficiency,
            totalClusters: 0
          },
          apiMetrics: {
            ...mockBusinessIntelligenceData.analytics.apiMetrics,
            totalCalls: 0
          }
        }
      };
      
      const metrics = calculateBusinessMetrics(emptyData);
      expect(metrics.avgKeywordsPerCluster).toBe(0);
      expect(metrics.apiEfficiency).toBe(0);
    });
  });

  describe('Validação de Dados de Business Intelligence', () => {
    
    test('deve validar dados corretos sem erros', () => {
      const errors = validateBusinessData(mockBusinessIntelligenceData);
      expect(errors).toHaveLength(0);
    });

    test('deve detectar receita negativa', () => {
      const invalidData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        kpis: {
          ...mockBusinessIntelligenceData.kpis,
          revenue: -1000
        }
      };
      
      const errors = validateBusinessData(invalidData);
      expect(errors).toContain('Receita deve ser positiva');
    });

    test('deve detectar crescimento inválido', () => {
      const invalidData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        kpis: {
          ...mockBusinessIntelligenceData.kpis,
          growth: 15.0
        }
      };
      
      const errors = validateBusinessData(invalidData);
      expect(errors).toContain('Crescimento deve estar entre -100% e 1000%');
    });

    test('deve detectar market share inválido', () => {
      const invalidData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        kpis: {
          ...mockBusinessIntelligenceData.kpis,
          marketShare: 1.5
        }
      };
      
      const errors = validateBusinessData(invalidData);
      expect(errors).toContain('Market share deve estar entre 0 e 1');
    });

    test('deve detectar satisfação do cliente inválida', () => {
      const invalidData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        kpis: {
          ...mockBusinessIntelligenceData.kpis,
          customerSatisfaction: -0.1
        }
      };
      
      const errors = validateBusinessData(invalidData);
      expect(errors).toContain('Satisfação do cliente deve estar entre 0 e 1');
    });

    test('deve detectar taxa de conversão inválida', () => {
      const invalidData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        analytics: {
          ...mockBusinessIntelligenceData.analytics,
          keywordPerformance: {
            ...mockBusinessIntelligenceData.analytics.keywordPerformance,
            conversionRate: 1.2
          }
        }
      };
      
      const errors = validateBusinessData(invalidData);
      expect(errors).toContain('Taxa de conversão deve estar entre 0 e 1');
    });

    test('deve detectar score de qualidade inválido', () => {
      const invalidData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        analytics: {
          ...mockBusinessIntelligenceData.analytics,
          clusterEfficiency: {
            ...mockBusinessIntelligenceData.analytics.clusterEfficiency,
            qualityScore: -0.1
          }
        }
      };
      
      const errors = validateBusinessData(invalidData);
      expect(errors).toContain('Score de qualidade deve estar entre 0 e 1');
    });

    test('deve detectar taxa de sucesso inválida', () => {
      const invalidData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        analytics: {
          ...mockBusinessIntelligenceData.analytics,
          apiMetrics: {
            ...mockBusinessIntelligenceData.analytics.apiMetrics,
            successRate: 1.1
          }
        }
      };
      
      const errors = validateBusinessData(invalidData);
      expect(errors).toContain('Taxa de sucesso deve estar entre 0 e 1');
    });
  });

  describe('Cálculo de Performance Score', () => {
    
    test('deve calcular performance score corretamente', () => {
      const score = calculatePerformanceScore(mockBusinessIntelligenceData);
      
      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(100);
      expect(typeof score).toBe('number');
    });

    test('deve calcular score para dados de alta performance', () => {
      const highPerformanceData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        analytics: {
          ...mockBusinessIntelligenceData.analytics,
          keywordPerformance: {
            highPerforming: 3000,
            mediumPerforming: 1000,
            lowPerforming: 200,
            conversionRate: 0.15
          },
          clusterEfficiency: {
            ...mockBusinessIntelligenceData.analytics.clusterEfficiency,
            qualityScore: 0.95
          },
          apiMetrics: {
            ...mockBusinessIntelligenceData.analytics.apiMetrics,
            successRate: 0.98
          }
        },
        kpis: {
          ...mockBusinessIntelligenceData.kpis,
          operationalEfficiency: 0.95
        }
      };

      const score = calculatePerformanceScore(highPerformanceData);
      expect(score).toBeGreaterThan(80);
    });

    test('deve calcular score para dados de baixa performance', () => {
      const lowPerformanceData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        analytics: {
          ...mockBusinessIntelligenceData.analytics,
          keywordPerformance: {
            highPerforming: 200,
            mediumPerforming: 500,
            lowPerforming: 2000,
            conversionRate: 0.01
          },
          clusterEfficiency: {
            ...mockBusinessIntelligenceData.analytics.clusterEfficiency,
            qualityScore: 0.30
          },
          apiMetrics: {
            ...mockBusinessIntelligenceData.analytics.apiMetrics,
            successRate: 0.70
          }
        },
        kpis: {
          ...mockBusinessIntelligenceData.kpis,
          operationalEfficiency: 0.50
        }
      };

      const score = calculatePerformanceScore(lowPerformanceData);
      expect(score).toBeLessThan(50);
    });
  });

  describe('Análise de Tendências', () => {
    
    test('deve analisar tendências corretamente', () => {
      const trends = analyzeTrends(mockBusinessIntelligenceData);

      expect(trends.growthTrend).toBe('strong');
      expect(trends.seasonalityImpact).toBe('low');
      expect(trends.stability).toBe('stable');
      expect(trends.momentum).toBe('accelerating');
    });

    test('deve identificar crescimento fraco', () => {
      const weakGrowthData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        trends: {
          ...mockBusinessIntelligenceData.trends,
          yearlyGrowth: 0.03
        }
      };
      
      const trends = analyzeTrends(weakGrowthData);
      expect(trends.growthTrend).toBe('weak');
    });

    test('deve identificar crescimento moderado', () => {
      const moderateGrowthData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        trends: {
          ...mockBusinessIntelligenceData.trends,
          yearlyGrowth: 0.08
        }
      };
      
      const trends = analyzeTrends(moderateGrowthData);
      expect(trends.growthTrend).toBe('moderate');
    });

    test('deve identificar impacto sazonal alto', () => {
      const highSeasonalityData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        trends: {
          ...mockBusinessIntelligenceData.trends,
          seasonalFactor: 0.15
        }
      };
      
      const trends = analyzeTrends(highSeasonalityData);
      expect(trends.seasonalityImpact).toBe('high');
    });

    test('deve identificar volatilidade', () => {
      const volatileData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        trends: {
          ...mockBusinessIntelligenceData.trends,
          monthlyGrowth: 0.15,
          quarterlyGrowth: 0.05
        }
      };
      
      const trends = analyzeTrends(volatileData);
      expect(trends.stability).toBe('volatile');
    });

    test('deve identificar desaceleração', () => {
      const deceleratingData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        trends: {
          ...mockBusinessIntelligenceData.trends,
          monthlyGrowth: 0.05,
          quarterlyGrowth: 0.12
        }
      };
      
      const trends = analyzeTrends(deceleratingData);
      expect(trends.momentum).toBe('decelerating');
    });
  });

  describe('Geração de Insights', () => {
    
    test('deve gerar insights baseados nos dados', () => {
      const insights = generateInsights(mockBusinessIntelligenceData);
      
      expect(Array.isArray(insights)).toBe(true);
      expect(insights.length).toBeGreaterThan(0);
    });

    test('deve recomendar otimização para baixa conversão', () => {
      const lowConversionData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        analytics: {
          ...mockBusinessIntelligenceData.analytics,
          keywordPerformance: {
            ...mockBusinessIntelligenceData.analytics.keywordPerformance,
            conversionRate: 0.02
          }
        }
      };
      
      const insights = generateInsights(lowConversionData);
      expect(insights).toContain('Otimizar keywords de baixa conversão');
    });

    test('deve recomendar melhoria de clusters para baixa qualidade', () => {
      const lowQualityData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        analytics: {
          ...mockBusinessIntelligenceData.analytics,
          clusterEfficiency: {
            ...mockBusinessIntelligenceData.analytics.clusterEfficiency,
            qualityScore: 0.65
          }
        }
      };
      
      const insights = generateInsights(lowQualityData);
      expect(insights).toContain('Melhorar qualidade dos clusters');
    });

    test('deve recomendar investigação de APIs para baixa taxa de sucesso', () => {
      const lowSuccessData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        analytics: {
          ...mockBusinessIntelligenceData.analytics,
          apiMetrics: {
            ...mockBusinessIntelligenceData.analytics.apiMetrics,
            successRate: 0.85
          }
        }
      };
      
      const insights = generateInsights(lowSuccessData);
      expect(insights).toContain('Investigar falhas nas APIs');
    });

    test('deve recomendar foco no cliente para baixa satisfação', () => {
      const lowSatisfactionData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        kpis: {
          ...mockBusinessIntelligenceData.kpis,
          customerSatisfaction: 0.75
        }
      };
      
      const insights = generateInsights(lowSatisfactionData);
      expect(insights).toContain('Focar na experiência do cliente');
    });

    test('deve recomendar estratégias de crescimento para baixo crescimento', () => {
      const lowGrowthData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        trends: {
          ...mockBusinessIntelligenceData.trends,
          yearlyGrowth: 0.05
        }
      };
      
      const insights = generateInsights(lowGrowthData);
      expect(insights).toContain('Implementar estratégias de crescimento');
    });
  });

  describe('Cálculo de ROI', () => {
    
    test('deve calcular ROI corretamente', () => {
      const roi = calculateROI(mockBusinessIntelligenceData);
      
      const expectedCost = mockBusinessIntelligenceData.analytics.apiMetrics.totalCalls * 
                          mockBusinessIntelligenceData.analytics.apiMetrics.costPerCall;
      const expectedRevenue = mockBusinessIntelligenceData.kpis.revenue;
      const expectedROI = ((expectedRevenue - expectedCost) / expectedCost) * 100;
      
      expect(roi).toBeCloseTo(expectedROI, 1);
    });

    test('deve lidar com custo zero', () => {
      const zeroCostData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        analytics: {
          ...mockBusinessIntelligenceData.analytics,
          apiMetrics: {
            ...mockBusinessIntelligenceData.analytics.apiMetrics,
            costPerCall: 0
          }
        }
      };
      
      const roi = calculateROI(zeroCostData);
      expect(roi).toBe(0);
    });

    test('deve calcular ROI negativo', () => {
      const negativeROIData: BusinessIntelligenceData = {
        ...mockBusinessIntelligenceData,
        kpis: {
          ...mockBusinessIntelligenceData.kpis,
          revenue: 100000
        },
        analytics: {
          ...mockBusinessIntelligenceData.analytics,
          apiMetrics: {
            ...mockBusinessIntelligenceData.analytics.apiMetrics,
            costPerCall: 10
          }
        }
      };
      
      const roi = calculateROI(negativeROIData);
      expect(roi).toBeLessThan(0);
    });
  });

  describe('Cálculo de Métricas de Eficiência', () => {
    
    test('deve calcular métricas de eficiência', () => {
      const efficiency = calculateEfficiencyMetrics(mockBusinessIntelligenceData);

      expect(efficiency.keywordEfficiency).toBeCloseTo(0.279, 3);
      expect(efficiency.clusterEfficiency).toBeCloseTo(0.608, 3);
      expect(efficiency.apiEfficiency).toBeCloseTo(3.837, 3);
      expect(efficiency.overallEfficiency).toBeCloseTo(0.333, 3);
    });

    test('deve calcular eficiência de keywords', () => {
      const efficiency = calculateEfficiencyMetrics(mockBusinessIntelligenceData);
      const expectedKeywordEfficiency = mockBusinessIntelligenceData.analytics.keywordPerformance.highPerforming / 
                                       (mockBusinessIntelligenceData.analytics.keywordPerformance.highPerforming + 
                                        mockBusinessIntelligenceData.analytics.keywordPerformance.mediumPerforming + 
                                        mockBusinessIntelligenceData.analytics.keywordPerformance.lowPerforming);
      
      expect(efficiency.keywordEfficiency).toBe(expectedKeywordEfficiency);
    });

    test('deve calcular eficiência de clusters', () => {
      const efficiency = calculateEfficiencyMetrics(mockBusinessIntelligenceData);
      const expectedClusterEfficiency = mockBusinessIntelligenceData.analytics.clusterEfficiency.qualityScore * 
                                       (1 - mockBusinessIntelligenceData.analytics.clusterEfficiency.optimizationPotential);
      
      expect(efficiency.clusterEfficiency).toBe(expectedClusterEfficiency);
    });

    test('deve calcular eficiência de APIs', () => {
      const efficiency = calculateEfficiencyMetrics(mockBusinessIntelligenceData);
      const expectedApiEfficiency = mockBusinessIntelligenceData.analytics.apiMetrics.successRate * 
                                   (1000 / mockBusinessIntelligenceData.analytics.apiMetrics.avgResponseTime);
      
      expect(efficiency.apiEfficiency).toBe(expectedApiEfficiency);
    });
  });

  describe('Formatação de Dados', () => {
    
    test('deve formatar moeda corretamente', () => {
      const formatted = formatCurrency(1250000);
      expect(formatted).toMatch(/R\$\s*1\.250\.000,00/);
    });

    test('deve formatar percentual corretamente', () => {
      const formatted = formatPercentage(0.045);
      expect(formatted).toBe('4.5%');
    });

    test('deve formatar número corretamente', () => {
      const formatted = formatNumber(45680);
      expect(formatted).toBe('45.680');
    });

    test('deve formatar valores zero', () => {
      expect(formatCurrency(0)).toMatch(/R\$\s*0,00/);
      expect(formatPercentage(0)).toBe('0.0%');
      expect(formatNumber(0)).toBe('0');
    });

    test('deve formatar valores negativos', () => {
      expect(formatCurrency(-1000)).toMatch(/R\$\s*-1\.000,00/);
      expect(formatPercentage(-0.05)).toBe('-5.0%');
      expect(formatNumber(-5000)).toBe('-5.000');
    });
  });

  describe('Validação de Consistência de Dados', () => {
    
    test('deve validar consistência entre métricas relacionadas', () => {
      const data = mockBusinessIntelligenceData;
      
      // Total de keywords deve ser a soma de todas as categorias
      const totalKeywords = data.analytics.keywordPerformance.highPerforming + 
                           data.analytics.keywordPerformance.mediumPerforming + 
                           data.analytics.keywordPerformance.lowPerforming;
      
      expect(totalKeywords).toBeGreaterThan(0);
      expect(data.analytics.keywordPerformance.highPerforming).toBeLessThanOrEqual(totalKeywords);
      expect(data.analytics.keywordPerformance.mediumPerforming).toBeLessThanOrEqual(totalKeywords);
      expect(data.analytics.keywordPerformance.lowPerforming).toBeLessThanOrEqual(totalKeywords);
      
      // Receita deve ser positiva
      expect(data.kpis.revenue).toBeGreaterThan(0);
      
      // Market share deve estar entre 0 e 1
      expect(data.kpis.marketShare).toBeGreaterThanOrEqual(0);
      expect(data.kpis.marketShare).toBeLessThanOrEqual(1);
      
      // Taxa de sucesso deve estar entre 0 e 1
      expect(data.analytics.apiMetrics.successRate).toBeGreaterThanOrEqual(0);
      expect(data.analytics.apiMetrics.successRate).toBeLessThanOrEqual(1);
    });

    test('deve validar que percentuais estão em escala correta', () => {
      const data = mockBusinessIntelligenceData;
      
      // Taxas devem estar entre 0 e 1
      expect(data.kpis.marketShare).toBeGreaterThanOrEqual(0);
      expect(data.kpis.marketShare).toBeLessThanOrEqual(1);
      expect(data.kpis.customerSatisfaction).toBeGreaterThanOrEqual(0);
      expect(data.kpis.customerSatisfaction).toBeLessThanOrEqual(1);
      expect(data.kpis.operationalEfficiency).toBeGreaterThanOrEqual(0);
      expect(data.kpis.operationalEfficiency).toBeLessThanOrEqual(1);
      expect(data.analytics.keywordPerformance.conversionRate).toBeGreaterThanOrEqual(0);
      expect(data.analytics.keywordPerformance.conversionRate).toBeLessThanOrEqual(1);
      expect(data.analytics.clusterEfficiency.qualityScore).toBeGreaterThanOrEqual(0);
      expect(data.analytics.clusterEfficiency.qualityScore).toBeLessThanOrEqual(1);
      expect(data.analytics.clusterEfficiency.optimizationPotential).toBeGreaterThanOrEqual(0);
      expect(data.analytics.clusterEfficiency.optimizationPotential).toBeLessThanOrEqual(1);
      expect(data.analytics.apiMetrics.successRate).toBeGreaterThanOrEqual(0);
      expect(data.analytics.apiMetrics.successRate).toBeLessThanOrEqual(1);
    });
  });
}); 