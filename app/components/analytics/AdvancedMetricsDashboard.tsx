/**
 * 📊 Advanced Metrics Dashboard Component
 * 🎯 Objetivo: Dashboard de métricas avançadas em tempo real
 * 📅 Data: 2025-01-27
 * 🔗 Tracing ID: ADVANCED_METRICS_DASHBOARD_001
 * 📋 Ruleset: enterprise_control_layer.yaml
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Download,
  RefreshCw,
  Settings,
  BarChart3,
  LineChart,
  PieChart,
  Gauge,
  Zap,
  Shield,
  Users,
  Database,
  Globe,
  Server
} from 'lucide-react';

// Tipos para métricas
interface MetricData {
  id: string;
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  change: number;
  status: 'healthy' | 'warning' | 'critical';
  timestamp: number;
  category: 'performance' | 'business' | 'infrastructure' | 'user';
}

interface AlertData {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  isAcknowledged: boolean;
}

interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
    fill?: boolean;
  }>;
}

interface DashboardConfig {
  refreshInterval: number;
  autoRefresh: boolean;
  showAlerts: boolean;
  showTrends: boolean;
  timeRange: '1h' | '6h' | '24h' | '7d' | '30d';
  metricsFilter: string[];
}

// Dados de exemplo
const SAMPLE_METRICS: MetricData[] = [
  {
    id: 'response_time',
    name: 'Tempo de Resposta',
    value: 245,
    unit: 'ms',
    trend: 'down',
    change: -12.5,
    status: 'healthy',
    timestamp: Date.now(),
    category: 'performance'
  },
  {
    id: 'error_rate',
    name: 'Taxa de Erro',
    value: 1.2,
    unit: '%',
    trend: 'up',
    change: 0.3,
    status: 'warning',
    timestamp: Date.now(),
    category: 'performance'
  },
  {
    id: 'active_users',
    name: 'Usuários Ativos',
    value: 1247,
    unit: '',
    trend: 'up',
    change: 8.7,
    status: 'healthy',
    timestamp: Date.now(),
    category: 'user'
  },
  {
    id: 'cpu_usage',
    name: 'Uso de CPU',
    value: 78.5,
    unit: '%',
    trend: 'up',
    change: 5.2,
    status: 'warning',
    timestamp: Date.now(),
    category: 'infrastructure'
  },
  {
    id: 'memory_usage',
    name: 'Uso de Memória',
    value: 65.3,
    unit: '%',
    trend: 'stable',
    change: 0.1,
    status: 'healthy',
    timestamp: Date.now(),
    category: 'infrastructure'
  },
  {
    id: 'database_connections',
    name: 'Conexões DB',
    value: 89,
    unit: '',
    trend: 'down',
    change: -3.2,
    status: 'healthy',
    timestamp: Date.now(),
    category: 'infrastructure'
  },
  {
    id: 'revenue',
    name: 'Receita',
    value: 15420,
    unit: 'R$',
    trend: 'up',
    change: 12.8,
    status: 'healthy',
    timestamp: Date.now(),
    category: 'business'
  },
  {
    id: 'conversion_rate',
    name: 'Taxa de Conversão',
    value: 3.8,
    unit: '%',
    trend: 'up',
    change: 0.5,
    status: 'healthy',
    timestamp: Date.now(),
    category: 'business'
  }
];

const SAMPLE_ALERTS: AlertData[] = [
  {
    id: 'alert_1',
    type: 'warning',
    title: 'Alto Uso de CPU',
    message: 'CPU atingiu 85% de utilização',
    timestamp: Date.now() - 300000,
    severity: 'medium',
    category: 'infrastructure',
    isAcknowledged: false
  },
  {
    id: 'alert_2',
    type: 'error',
    title: 'Erro de Conexão',
    message: 'Falha na conexão com banco de dados',
    timestamp: Date.now() - 600000,
    severity: 'high',
    category: 'infrastructure',
    isAcknowledged: true
  },
  {
    id: 'alert_3',
    type: 'info',
    title: 'Manutenção Programada',
    message: 'Manutenção agendada para 02:00',
    timestamp: Date.now() - 900000,
    severity: 'low',
    category: 'maintenance',
    isAcknowledged: false
  }
];

export const AdvancedMetricsDashboard: React.FC = () => {
  // Estados
  const [metrics, setMetrics] = useState<MetricData[]>(SAMPLE_METRICS);
  const [alerts, setAlerts] = useState<AlertData[]>(SAMPLE_ALERTS);
  const [config, setConfig] = useState<DashboardConfig>({
    refreshInterval: 30,
    autoRefresh: true,
    showAlerts: true,
    showTrends: true,
    timeRange: '24h',
    metricsFilter: []
  });
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Cálculos derivados
  const healthyMetrics = useMemo(() => 
    metrics.filter(m => m.status === 'healthy').length, [metrics]
  );
  
  const warningMetrics = useMemo(() => 
    metrics.filter(m => m.status === 'warning').length, [metrics]
  );
  
  const criticalMetrics = useMemo(() => 
    metrics.filter(m => m.status === 'critical').length, [metrics]
  );

  const unacknowledgedAlerts = useMemo(() => 
    alerts.filter(a => !a.isAcknowledged).length, [alerts]
  );

  const criticalAlerts = useMemo(() => 
    alerts.filter(a => a.severity === 'critical' && !a.isAcknowledged).length, [alerts]
  );

  // Funções
  const refreshMetrics = useCallback(async () => {
    setIsLoading(true);
    try {
      // Simular chamada de API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Atualizar métricas com dados simulados
      const updatedMetrics = metrics.map(metric => ({
        ...metric,
        value: metric.value + (Math.random() - 0.5) * 10,
        change: metric.change + (Math.random() - 0.5) * 2,
        timestamp: Date.now()
      }));
      
      setMetrics(updatedMetrics);
      setLastUpdate(new Date());
      
    } catch (error) {
      console.error('Erro ao atualizar métricas:', error);
    } finally {
      setIsLoading(false);
    }
  }, [metrics]);

  const acknowledgeAlert = useCallback((alertId: string) => {
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === alertId 
          ? { ...alert, isAcknowledged: true }
          : alert
      )
    );
  }, []);

  const exportReport = useCallback(() => {
    const report = {
      timestamp: new Date().toISOString(),
      metrics: metrics,
      alerts: alerts,
      summary: {
        totalMetrics: metrics.length,
        healthyMetrics,
        warningMetrics,
        criticalMetrics,
        totalAlerts: alerts.length,
        unacknowledgedAlerts,
        criticalAlerts
      }
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `metrics_report_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [metrics, alerts, healthyMetrics, warningMetrics, criticalMetrics, unacknowledgedAlerts, criticalAlerts]);

  const getMetricIcon = (category: string) => {
    switch (category) {
      case 'performance': return <Activity className="w-4 h-4" />;
      case 'business': return <TrendingUp className="w-4 h-4" />;
      case 'infrastructure': return <Server className="w-4 h-4" />;
      case 'user': return <Users className="w-4 h-4" />;
      default: return <BarChart3 className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-100 text-green-800';
      case 'warning': return 'bg-yellow-100 text-yellow-800';
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp className="w-4 h-4 text-green-600" />;
      case 'down': return <TrendingDown className="w-4 h-4 text-red-600" />;
      case 'stable': return <Clock className="w-4 h-4 text-gray-600" />;
      default: return <Clock className="w-4 h-4 text-gray-600" />;
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'error': return <AlertTriangle className="w-4 h-4 text-red-600" />;
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      case 'success': return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'info': return <Activity className="w-4 h-4 text-blue-600" />;
      default: return <Activity className="w-4 h-4 text-gray-600" />;
    }
  };

  // Auto-refresh
  useEffect(() => {
    if (!config.autoRefresh) return;

    const interval = setInterval(refreshMetrics, config.refreshInterval * 1000);
    return () => clearInterval(interval);
  }, [config.autoRefresh, config.refreshInterval, refreshMetrics]);

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">📊 Dashboard de Métricas Avançadas</h1>
          <p className="text-gray-600">
            Monitoramento em tempo real • Última atualização: {lastUpdate.toLocaleTimeString()}
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            onClick={refreshMetrics}
            disabled={isLoading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
          <Button onClick={exportReport}>
            <Download className="w-4 h-4 mr-2" />
            Exportar Relatório
          </Button>
        </div>
      </div>

      {/* Resumo Geral */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Métricas Saudáveis</p>
                <p className="text-2xl font-bold text-green-600">{healthyMetrics}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avisos</p>
                <p className="text-2xl font-bold text-yellow-600">{warningMetrics}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Críticos</p>
                <p className="text-2xl font-bold text-red-600">{criticalMetrics}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Alertas Pendentes</p>
                <p className="text-2xl font-bold text-orange-600">{unacknowledgedAlerts}</p>
              </div>
              <Zap className="w-8 h-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="metrics" className="space-y-4">
        <TabsList>
          <TabsTrigger value="metrics">Métricas</TabsTrigger>
          <TabsTrigger value="alerts">Alertas</TabsTrigger>
          <TabsTrigger value="charts">Gráficos</TabsTrigger>
          <TabsTrigger value="settings">Configurações</TabsTrigger>
        </TabsList>

        {/* Métricas */}
        <TabsContent value="metrics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {metrics.map((metric) => (
              <Card key={metric.id} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-2">
                      {getMetricIcon(metric.category)}
                      <span>{metric.name}</span>
                    </div>
                    <Badge className={getStatusColor(metric.status)}>
                      {metric.status}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-2xl font-bold">
                      {metric.value.toLocaleString()}
                      <span className="text-sm text-gray-600 ml-1">{metric.unit}</span>
                    </div>
                    {getTrendIcon(metric.trend)}
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">
                      {metric.trend === 'up' ? '+' : ''}{metric.change.toFixed(1)}%
                    </span>
                    <span className="text-gray-500">
                      {new Date(metric.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Alertas */}
        <TabsContent value="alerts" className="space-y-4">
          {alerts.length === 0 ? (
            <Alert>
              <CheckCircle className="w-4 h-4" />
              <AlertDescription>Nenhum alerta ativo no momento.</AlertDescription>
            </Alert>
          ) : (
            <div className="space-y-4">
              {alerts.map((alert) => (
                <Card key={alert.id} className={alert.isAcknowledged ? 'opacity-60' : ''}>
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3">
                        {getAlertIcon(alert.type)}
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <h3 className="font-semibold">{alert.title}</h3>
                            <Badge variant={alert.severity === 'critical' ? 'destructive' : 'secondary'}>
                              {alert.severity}
                            </Badge>
                            {alert.isAcknowledged && (
                              <Badge variant="outline">Reconhecido</Badge>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{alert.message}</p>
                          <p className="text-xs text-gray-500">
                            {new Date(alert.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      {!alert.isAcknowledged && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => acknowledgeAlert(alert.id)}
                        >
                          Reconhecer
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Gráficos */}
        <TabsContent value="charts" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <LineChart className="w-5 h-5 mr-2" />
                  Tendência de Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  Gráfico de Linha - Implementar com Chart.js ou Recharts
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <PieChart className="w-5 h-5 mr-2" />
                  Distribuição de Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  Gráfico de Pizza - Implementar com Chart.js ou Recharts
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Métricas por Categoria
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  Gráfico de Barras - Implementar com Chart.js ou Recharts
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Gauge className="w-5 h-5 mr-2" />
                  Saúde Geral do Sistema
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  Gauge Chart - Implementar com Chart.js ou Recharts
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Configurações */}
        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="w-5 h-5 mr-2" />
                Configurações do Dashboard
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="refresh-interval">Intervalo de Atualização (segundos)</Label>
                  <Input
                    id="refresh-interval"
                    type="number"
                    value={config.refreshInterval}
                    onChange={(e) => setConfig(prev => ({ 
                      ...prev, 
                      refreshInterval: parseInt(e.target.value) || 30 
                    }))}
                    min="10"
                    max="300"
                  />
                </div>

                <div>
                  <Label htmlFor="time-range">Intervalo de Tempo</Label>
                  <Select
                    value={config.timeRange}
                    onValueChange={(value) => setConfig(prev => ({ 
                      ...prev, 
                      timeRange: value as any 
                    }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1h">Última Hora</SelectItem>
                      <SelectItem value="6h">Últimas 6 Horas</SelectItem>
                      <SelectItem value="24h">Últimas 24 Horas</SelectItem>
                      <SelectItem value="7d">Últimos 7 Dias</SelectItem>
                      <SelectItem value="30d">Últimos 30 Dias</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="auto-refresh"
                    checked={config.autoRefresh}
                    onCheckedChange={(checked) => setConfig(prev => ({ 
                      ...prev, 
                      autoRefresh: checked 
                    }))}
                  />
                  <Label htmlFor="auto-refresh">Atualização Automática</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="show-alerts"
                    checked={config.showAlerts}
                    onCheckedChange={(checked) => setConfig(prev => ({ 
                      ...prev, 
                      showAlerts: checked 
                    }))}
                  />
                  <Label htmlFor="show-alerts">Mostrar Alertas</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="show-trends"
                    checked={config.showTrends}
                    onCheckedChange={(checked) => setConfig(prev => ({ 
                      ...prev, 
                      showTrends: checked 
                    }))}
                  />
                  <Label htmlFor="show-trends">Mostrar Tendências</Label>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdvancedMetricsDashboard; 