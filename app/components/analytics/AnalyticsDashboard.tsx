/**
 * AnalyticsDashboard.tsx
 * 
 * Componente principal do sistema de analytics avançado
 * Integra métricas de performance, análise de clusters e insights preditivos
 * 
 * Tracing ID: UI-001
 * Data/Hora: 2024-12-20 07:00:00 UTC
 * Versão: 1.0
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '../shared/Card';
import { Button } from '../shared/Button';
import { Badge } from '../shared/Badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../shared/Tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../shared/Select';
import { DatePicker } from '../shared/DatePicker';
import { Progress } from '../shared/Progress';
import { Alert, AlertDescription } from '../shared/Alert';
import { Skeleton } from '../shared/Skeleton';
import { useAnalytics } from '../../hooks/useAnalytics';
import { usePerformanceMetrics } from '../../hooks/usePerformanceMetrics';
import { formatCurrency, formatPercentage, formatNumber } from '../../utils/formatters';
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  Target, 
  BarChart3, 
  PieChart,
  Download,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap
} from 'lucide-react';

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

interface AnalyticsDashboardProps {
  className?: string;
  refreshInterval?: number;
  enableRealTime?: boolean;
  exportFormats?: ('csv' | 'json' | 'pdf')[];
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  className = '',
  refreshInterval = 30000,
  enableRealTime = true,
  exportFormats = ['csv', 'json']
}) => {
  const [selectedPeriod, setSelectedPeriod] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('performance');
  const [isExporting, setIsExporting] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const {
    data: analyticsData,
    isLoading,
    error,
    refetch
  } = useAnalytics({
    period: selectedPeriod,
    metric: selectedMetric
  });

  const {
    data: performanceMetrics,
    isLoading: metricsLoading
  } = usePerformanceMetrics();

  // Auto-refresh para dados em tempo real
  useEffect(() => {
    if (!enableRealTime) return;

    const interval = setInterval(() => {
      refetch();
      setLastRefresh(new Date());
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [enableRealTime, refreshInterval, refetch]);

  // Cálculos derivados
  const calculatedMetrics = useMemo(() => {
    if (!analyticsData) return null;

    const { keywordsPerformance, clusterEfficiency, userBehavior, predictiveInsights } = analyticsData;

    return {
      performanceScore: Math.round(
        (keywordsPerformance.conversionRate * 0.4) +
        (clusterEfficiency.clusterQuality * 0.3) +
        (userBehavior.userEngagement * 0.3)
      ),
      efficiencyTrend: clusterEfficiency.semanticCoherence > 0.8 ? 'up' : 'down',
      riskLevel: predictiveInsights.anomalyScore > 0.7 ? 'high' : 
                 predictiveInsights.anomalyScore > 0.4 ? 'medium' : 'low'
    };
  }, [analyticsData]);

  // Handlers
  const handleExport = async (format: string) => {
    setIsExporting(true);
    try {
      // Implementar lógica de exportação
      console.log(`Exporting analytics data in ${format} format`);
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulação
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const handleRefresh = () => {
    refetch();
    setLastRefresh(new Date());
  };

  // Renderização de loading
  if (isLoading) {
    return (
      <div className={`analytics-dashboard ${className}`}>
        <div className="grid gap-6">
          <Skeleton className="h-8 w-64" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
          <Skeleton className="h-96" />
        </div>
      </div>
    );
  }

  // Renderização de erro
  if (error) {
    return (
      <div className={`analytics-dashboard ${className}`}>
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Erro ao carregar dados de analytics: {error.message}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className={`analytics-dashboard ${className}`}>
      {/* Header com controles */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics Dashboard</h1>
          <p className="text-muted-foreground">
            Métricas avançadas e insights preditivos do sistema
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1d">Último dia</SelectItem>
              <SelectItem value="7d">Última semana</SelectItem>
              <SelectItem value="30d">Último mês</SelectItem>
              <SelectItem value="90d">Último trimestre</SelectItem>
            </SelectContent>
          </Select>

          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>

          <div className="flex gap-1">
            {exportFormats.map(format => (
              <Button
                key={format}
                variant="outline"
                size="sm"
                onClick={() => handleExport(format)}
                disabled={isExporting}
              >
                <Download className="h-4 w-4 mr-2" />
                {format.toUpperCase()}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Indicadores de status */}
      <div className="flex items-center gap-4 mb-6 text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4" />
          Última atualização: {lastRefresh.toLocaleTimeString()}
        </div>
        
        {enableRealTime && (
          <div className="flex items-center gap-2">
            <Zap className="h-4 w-4 text-green-500" />
            Tempo real ativo
          </div>
        )}

        {calculatedMetrics && (
          <div className="flex items-center gap-2">
            {calculatedMetrics.riskLevel === 'low' ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : calculatedMetrics.riskLevel === 'medium' ? (
              <AlertTriangle className="h-4 w-4 text-yellow-500" />
            ) : (
              <AlertTriangle className="h-4 w-4 text-red-500" />
            )}
            Risco: {calculatedMetrics.riskLevel}
          </div>
        )}
      </div>

      {/* Métricas principais */}
      {analyticsData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Performance Score</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {calculatedMetrics?.performanceScore || 0}/100
              </div>
              <div className="flex items-center text-xs text-muted-foreground">
                {calculatedMetrics?.efficiencyTrend === 'up' ? (
                  <TrendingUp className="h-3 w-3 mr-1 text-green-500" />
                ) : (
                  <TrendingDown className="h-3 w-3 mr-1 text-red-500" />
                )}
                {calculatedMetrics?.efficiencyTrend === 'up' ? '+12%' : '-5%'} vs período anterior
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Keywords Ativas</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {analyticsData.keywordsPerformance.activeKeywords.toLocaleString()}
              </div>
              <div className="text-xs text-muted-foreground">
                de {analyticsData.keywordsPerformance.totalKeywords.toLocaleString()} total
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Taxa de Conversão</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatPercentage(analyticsData.keywordsPerformance.conversionRate)}
              </div>
              <Progress 
                value={analyticsData.keywordsPerformance.conversionRate * 100} 
                className="mt-2" 
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Usuários Ativos</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {analyticsData.userBehavior.activeUsers.toLocaleString()}
              </div>
              <div className="text-xs text-muted-foreground">
                {formatNumber(analyticsData.userBehavior.sessionDuration)}min sessão média
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabs principais */}
      <Tabs defaultValue="performance" className="space-y-4">
        <TabsList>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="clusters">Clusters</TabsTrigger>
          <TabsTrigger value="behavior">Comportamento</TabsTrigger>
          <TabsTrigger value="predictions">Insights Preditivos</TabsTrigger>
        </TabsList>

        <TabsContent value="performance" className="space-y-4">
          {analyticsData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Métricas de Keywords</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium">Posição Média</p>
                      <p className="text-2xl font-bold">
                        #{analyticsData.keywordsPerformance.avgPosition.toFixed(1)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">CTR</p>
                      <p className="text-2xl font-bold">
                        {formatPercentage(analyticsData.keywordsPerformance.clickThroughRate)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">CPC</p>
                      <p className="text-2xl font-bold">
                        {formatCurrency(analyticsData.keywordsPerformance.costPerClick)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Total Clicks</p>
                      <p className="text-2xl font-bold">
                        {analyticsData.keywordsPerformance.totalClicks.toLocaleString()}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Distribuição de Performance</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Alta Performance</span>
                      <Badge variant="success">23%</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Média Performance</span>
                      <Badge variant="warning">45%</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Baixa Performance</span>
                      <Badge variant="destructive">32%</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        <TabsContent value="clusters" className="space-y-4">
          {analyticsData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Eficiência de Clusters</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium">Total Clusters</p>
                      <p className="text-2xl font-bold">
                        {analyticsData.clusterEfficiency.totalClusters}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Tamanho Médio</p>
                      <p className="text-2xl font-bold">
                        {analyticsData.clusterEfficiency.avgClusterSize.toFixed(1)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Qualidade</p>
                      <p className="text-2xl font-bold">
                        {formatPercentage(analyticsData.clusterEfficiency.clusterQuality)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Coerência Semântica</p>
                      <p className="text-2xl font-bold">
                        {formatPercentage(analyticsData.clusterEfficiency.semanticCoherence)}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Análise de Variação</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm font-medium mb-2">Variação de Performance</p>
                      <Progress 
                        value={analyticsData.clusterEfficiency.performanceVariance * 100} 
                        className="mb-2" 
                      />
                      <p className="text-xs text-muted-foreground">
                        {formatPercentage(analyticsData.clusterEfficiency.performanceVariance)} de variação
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        <TabsContent value="behavior" className="space-y-4">
          {analyticsData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Comportamento do Usuário</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium">Page Views</p>
                      <p className="text-2xl font-bold">
                        {analyticsData.userBehavior.pageViews.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Bounce Rate</p>
                      <p className="text-2xl font-bold">
                        {formatPercentage(analyticsData.userBehavior.bounceRate)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Engajamento</p>
                      <p className="text-2xl font-bold">
                        {formatPercentage(analyticsData.userBehavior.userEngagement)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Duração Sessão</p>
                      <p className="text-2xl font-bold">
                        {formatNumber(analyticsData.userBehavior.sessionDuration)}min
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Padrões de Uso</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Usuários Recorrentes</span>
                      <Badge variant="success">67%</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Novos Usuários</span>
                      <Badge variant="secondary">33%</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Sessões Longas</span>
                      <Badge variant="warning">28%</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        <TabsContent value="predictions" className="space-y-4">
          {analyticsData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Insights Preditivos</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium">Tendência Prevista</p>
                      <p className="text-2xl font-bold">
                        {formatPercentage(analyticsData.predictiveInsights.trendPrediction)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Fator Sazonal</p>
                      <p className="text-2xl font-bold">
                        {formatPercentage(analyticsData.predictiveInsights.seasonalityFactor)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Score de Anomalia</p>
                      <p className="text-2xl font-bold">
                        {formatPercentage(analyticsData.predictiveInsights.anomalyScore)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Confiança</p>
                      <p className="text-2xl font-bold">
                        {formatPercentage(analyticsData.predictiveInsights.recommendationConfidence)}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Próxima Melhor Ação</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="font-medium mb-2">Recomendação:</p>
                      <p className="text-sm text-muted-foreground">
                        {analyticsData.predictiveInsights.nextBestAction}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline">
                        Ver Detalhes
                      </Button>
                      <Button size="sm">
                        Aplicar Sugestão
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AnalyticsDashboard; 