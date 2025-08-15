/**
 * RealTimeAnalytics.tsx
 * 
 * Componente avançado de analytics em tempo real
 * Integra WebSocket, PWA features, data visualization e exportação
 * 
 * Tracing ID: UI-RTA-001
 * Data/Hora: 2025-01-27 15:30:00 UTC
 * Versão: 1.0
 * Ruleset: enterprise_control_layer.yaml
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
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
import { Progress } from '../shared/Progress';
import { Alert, AlertDescription } from '../shared/Alert';
import { Skeleton } from '../shared/Skeleton';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useBusinessMetrics } from '../../hooks/useBusinessMetrics';
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
  Zap,
  Wifi,
  WifiOff,
  Activity,
  Eye,
  EyeOff,
  Maximize2,
  Minimize2,
  Share2,
  Bell,
  BellOff
} from 'lucide-react';

// =============================================================================
// TIPOS E INTERFACES
// =============================================================================

interface RealTimeMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  category: 'performance' | 'users' | 'keywords' | 'revenue' | 'system';
  timestamp: string;
  trend: 'up' | 'down' | 'stable';
  changePercent: number;
  alertLevel: 'low' | 'medium' | 'high';
  metadata?: Record<string, any>;
}

interface RealTimeEvent {
  id: string;
  type: 'user_action' | 'system_event' | 'performance_alert' | 'revenue_event';
  title: string;
  description: string;
  severity: 'info' | 'warning' | 'error' | 'success';
  timestamp: string;
  userId?: string;
  metadata?: Record<string, any>;
}

interface RealTimeAnalyticsProps {
  className?: string;
  refreshInterval?: number;
  enablePWA?: boolean;
  enableNotifications?: boolean;
  exportFormats?: ('csv' | 'json' | 'pdf' | 'excel')[];
  maxDataPoints?: number;
}

// =============================================================================
// COMPONENTE PRINCIPAL
// =============================================================================

export const RealTimeAnalytics: React.FC<RealTimeAnalyticsProps> = ({
  className = '',
  refreshInterval = 5000,
  enablePWA = true,
  enableNotifications = true,
  exportFormats = ['csv', 'json', 'excel'],
  maxDataPoints = 100
}) => {
  const [selectedCategory, setSelectedCategory] = useState<RealTimeMetric['category']>('performance');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showNotifications, setShowNotifications] = useState(enableNotifications);
  const [isExporting, setIsExporting] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'reconnecting'>('connected');

  // WebSocket para dados em tempo real
  const {
    data: realTimeData,
    isConnected,
    error: wsError,
    sendMessage
  } = useWebSocket('ws://localhost:8000/ws/analytics', {
    onMessage: (data) => {
      setLastUpdate(new Date());
      setConnectionStatus('connected');
    },
    onError: () => {
      setConnectionStatus('disconnected');
    },
    onReconnect: () => {
      setConnectionStatus('reconnecting');
    }
  });

  // Hook de métricas de negócio
  const {
    data: businessMetrics,
    loading: metricsLoading,
    error: metricsError,
    refetch: refetchMetrics
  } = useBusinessMetrics(
    { category: selectedCategory },
    { enableRealTime: true, refreshInterval }
  );

  // Estado local para dados em tempo real
  const [realTimeMetrics, setRealTimeMetrics] = useState<RealTimeMetric[]>([]);
  const [realTimeEvents, setRealTimeEvents] = useState<RealTimeEvent[]>([]);

  // Processar dados do WebSocket
  useEffect(() => {
    if (realTimeData) {
      try {
        const parsedData = JSON.parse(realTimeData);
        
        if (parsedData.type === 'metrics') {
          setRealTimeMetrics(prev => {
            const newMetrics = [...prev, ...parsedData.metrics];
            return newMetrics.slice(-maxDataPoints); // Manter apenas os últimos pontos
          });
        } else if (parsedData.type === 'events') {
          setRealTimeEvents(prev => {
            const newEvents = [parsedData.event, ...prev];
            return newEvents.slice(0, 50); // Manter apenas os 50 eventos mais recentes
          });
        }
      } catch (error) {
        console.error('Erro ao processar dados WebSocket:', error);
      }
    }
  }, [realTimeData, maxDataPoints]);

  // PWA Features
  useEffect(() => {
    if (enablePWA && 'serviceWorker' in navigator) {
      // Registrar service worker para PWA
      navigator.serviceWorker.register('/sw.js')
        .then(registration => {
          console.log('Service Worker registrado:', registration);
        })
        .catch(error => {
          console.error('Erro ao registrar Service Worker:', error);
        });
    }
  }, [enablePWA]);

  // Notificações push
  useEffect(() => {
    if (enableNotifications && showNotifications && 'Notification' in window) {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          console.log('Notificações push habilitadas');
        }
      });
    }
  }, [enableNotifications, showNotifications]);

  // Cálculos derivados
  const calculatedStats = useMemo(() => {
    if (realTimeMetrics.length === 0) return null;

    const currentMetrics = realTimeMetrics[realTimeMetrics.length - 1];
    const previousMetrics = realTimeMetrics[realTimeMetrics.length - 2];

    return {
      totalMetrics: realTimeMetrics.length,
      activeAlerts: realTimeEvents.filter(e => e.severity === 'error' || e.severity === 'warning').length,
      avgResponseTime: realTimeMetrics.reduce((sum, m) => sum + m.value, 0) / realTimeMetrics.length,
      trend: currentMetrics && previousMetrics ? 
        currentMetrics.value > previousMetrics.value ? 'up' : 'down' : 'stable'
    };
  }, [realTimeMetrics, realTimeEvents]);

  // Handlers
  const handleExport = async (format: string) => {
    setIsExporting(true);
    try {
      const exportData = {
        metrics: realTimeMetrics,
        events: realTimeEvents,
        timestamp: new Date().toISOString(),
        format
      };

      // Simular exportação
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Criar blob e download
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `realtime-analytics-${new Date().toISOString()}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Erro na exportação:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const handleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Analytics em Tempo Real',
          text: 'Dados de analytics em tempo real do Omni Keywords Finder',
          url: window.location.href
        });
      } catch (error) {
        console.error('Erro ao compartilhar:', error);
      }
    }
  };

  const toggleNotifications = () => {
    setShowNotifications(!showNotifications);
  };

  // Renderização de loading
  if (metricsLoading && realTimeMetrics.length === 0) {
    return (
      <div className={`realtime-analytics ${className}`}>
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
  if (wsError && metricsError) {
    return (
      <div className={`realtime-analytics ${className}`}>
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Erro de conexão: {wsError.message || metricsError.message}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className={`realtime-analytics ${className}`}>
      {/* Header com controles */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics em Tempo Real</h1>
          <p className="text-muted-foreground">
            Dados e eventos em tempo real com PWA features
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Select value={selectedCategory} onValueChange={(value: RealTimeMetric['category']) => setSelectedCategory(value)}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="performance">Performance</SelectItem>
              <SelectItem value="users">Usuários</SelectItem>
              <SelectItem value="keywords">Keywords</SelectItem>
              <SelectItem value="revenue">Receita</SelectItem>
              <SelectItem value="system">Sistema</SelectItem>
            </SelectContent>
          </Select>

          <Button
            variant="outline"
            size="sm"
            onClick={refetchMetrics}
            disabled={metricsLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${metricsLoading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={toggleNotifications}
          >
            {showNotifications ? <Bell className="h-4 w-4 mr-2" /> : <BellOff className="h-4 w-4 mr-2" />}
            Notificações
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleShare}
          >
            <Share2 className="h-4 w-4 mr-2" />
            Compartilhar
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleFullscreen}
          >
            {isFullscreen ? <Minimize2 className="h-4 w-4 mr-2" /> : <Maximize2 className="h-4 w-4 mr-2" />}
            Tela Cheia
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
          Última atualização: {lastUpdate.toLocaleTimeString()}
        </div>
        
        <div className="flex items-center gap-2">
          {connectionStatus === 'connected' ? (
            <Wifi className="h-4 w-4 text-green-500" />
          ) : connectionStatus === 'reconnecting' ? (
            <Activity className="h-4 w-4 text-yellow-500 animate-pulse" />
          ) : (
            <WifiOff className="h-4 w-4 text-red-500" />
          )}
          {connectionStatus === 'connected' ? 'Conectado' : 
           connectionStatus === 'reconnecting' ? 'Reconectando...' : 'Desconectado'}
        </div>

        <div className="flex items-center gap-2">
          <Zap className="h-4 w-4 text-green-500" />
          Tempo real ativo
        </div>

        {calculatedStats && (
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
            {calculatedStats.activeAlerts} alertas ativos
          </div>
        )}
      </div>

      {/* Métricas principais em tempo real */}
      {realTimeMetrics.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {realTimeMetrics.slice(-4).map((metric, index) => (
            <Card key={metric.id} className="relative overflow-hidden">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{metric.name}</CardTitle>
                <div className="flex items-center gap-1">
                  {metric.trend === 'up' ? (
                    <TrendingUp className="h-4 w-4 text-green-500" />
                  ) : metric.trend === 'down' ? (
                    <TrendingDown className="h-4 w-4 text-red-500" />
                  ) : (
                    <BarChart3 className="h-4 w-4 text-muted-foreground" />
                  )}
                  <Badge 
                    variant={metric.alertLevel === 'high' ? 'destructive' : 
                            metric.alertLevel === 'medium' ? 'warning' : 'default'}
                    className="text-xs"
                  >
                    {metric.alertLevel}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatNumber(metric.value)} {metric.unit}
                </div>
                <div className="flex items-center text-xs text-muted-foreground">
                  {metric.changePercent > 0 ? '+' : ''}{metric.changePercent.toFixed(1)}% vs anterior
                </div>
                <Progress 
                  value={Math.min(metric.value / 100, 1) * 100} 
                  className="mt-2" 
                />
              </CardContent>
              {/* Indicador de atualização em tempo real */}
              <div className="absolute top-2 right-2 w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            </Card>
          ))}
        </div>
      )}

      {/* Tabs principais */}
      <Tabs defaultValue="live" className="space-y-4">
        <TabsList>
          <TabsTrigger value="live">Dados ao Vivo</TabsTrigger>
          <TabsTrigger value="events">Eventos</TabsTrigger>
          <TabsTrigger value="charts">Gráficos</TabsTrigger>
          <TabsTrigger value="alerts">Alertas</TabsTrigger>
        </TabsList>

        <TabsContent value="live" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Métricas em Tempo Real</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {realTimeMetrics.slice(-10).map(metric => (
                    <div key={metric.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-medium">{metric.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(metric.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold">
                          {formatNumber(metric.value)} {metric.unit}
                        </p>
                        <p className={`text-xs ${
                          metric.changePercent > 0 ? 'text-green-500' : 
                          metric.changePercent < 0 ? 'text-red-500' : 'text-muted-foreground'
                        }`}>
                          {metric.changePercent > 0 ? '+' : ''}{metric.changePercent.toFixed(1)}%
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Estatísticas do Sistema</CardTitle>
              </CardHeader>
              <CardContent>
                {calculatedStats ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span>Total de Métricas</span>
                      <Badge variant="default">{calculatedStats.totalMetrics}</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Alertas Ativos</span>
                      <Badge variant="warning">{calculatedStats.activeAlerts}</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Tempo Médio de Resposta</span>
                      <Badge variant="default">{calculatedStats.avgResponseTime.toFixed(2)}ms</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Tendência Geral</span>
                      <Badge variant={calculatedStats.trend === 'up' ? 'success' : 'destructive'}>
                        {calculatedStats.trend === 'up' ? 'Crescimento' : 'Declínio'}
                      </Badge>
                    </div>
                  </div>
                ) : (
                  <p className="text-muted-foreground">Aguardando dados...</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Eventos em Tempo Real</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {realTimeEvents.map(event => (
                  <div key={event.id} className={`flex items-start gap-3 p-3 border rounded-lg ${
                    event.severity === 'error' ? 'border-red-200 bg-red-50' :
                    event.severity === 'warning' ? 'border-yellow-200 bg-yellow-50' :
                    event.severity === 'success' ? 'border-green-200 bg-green-50' :
                    'border-gray-200 bg-gray-50'
                  }`}>
                    <div className={`w-2 h-2 rounded-full mt-2 ${
                      event.severity === 'error' ? 'bg-red-500' :
                      event.severity === 'warning' ? 'bg-yellow-500' :
                      event.severity === 'success' ? 'bg-green-500' :
                      'bg-blue-500'
                    }`} />
                    <div className="flex-1">
                      <p className="font-medium">{event.title}</p>
                      <p className="text-sm text-muted-foreground">{event.description}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {new Date(event.timestamp).toLocaleString()}
                      </p>
                    </div>
                    <Badge variant={
                      event.severity === 'error' ? 'destructive' :
                      event.severity === 'warning' ? 'warning' :
                      event.severity === 'success' ? 'success' : 'default'
                    }>
                      {event.type}
                    </Badge>
                  </div>
                ))}
                {realTimeEvents.length === 0 && (
                  <p className="text-muted-foreground text-center py-8">
                    Nenhum evento em tempo real
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="charts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Visualização de Dados</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center border rounded-lg">
                <p className="text-muted-foreground">
                  Gráficos interativos serão implementados aqui
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Alertas e Notificações</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {realTimeEvents.filter(e => e.severity === 'error' || e.severity === 'warning').map(event => (
                  <Alert key={event.id} variant={event.severity === 'error' ? 'destructive' : 'warning'}>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      <strong>{event.title}</strong>: {event.description}
                    </AlertDescription>
                  </Alert>
                ))}
                {realTimeEvents.filter(e => e.severity === 'error' || e.severity === 'warning').length === 0 && (
                  <Alert>
                    <CheckCircle className="h-4 w-4" />
                    <AlertDescription>
                      Nenhum alerta ativo no momento
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}; 