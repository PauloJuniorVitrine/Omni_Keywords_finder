/**
 * DataVisualization.tsx
 * 
 * Componente de data visualization com múltiplos tipos de gráficos
 * Suporta interatividade, animações e exportação
 * 
 * Tracing ID: UI-DV-001
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
import { useBusinessMetrics } from '../../hooks/useBusinessMetrics';
import { formatCurrency, formatPercentage, formatNumber } from '../../utils/formatters';
import { 
  BarChart3, 
  LineChart, 
  PieChart, 
  TrendingUp, 
  TrendingDown,
  Download,
  RefreshCw,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Filter,
  Eye,
  EyeOff,
  Maximize2,
  Minimize2,
  Share2,
  Settings,
  Info,
  Activity,
  Target,
  Users,
  DollarSign
} from 'lucide-react';

// =============================================================================
// TIPOS E INTERFACES
// =============================================================================

interface DataPoint {
  id: string;
  label: string;
  value: number;
  color?: string;
  category?: string;
  timestamp?: string;
  metadata?: Record<string, any>;
}

interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'area' | 'scatter' | 'heatmap' | 'radar' | 'doughnut';
  title: string;
  description?: string;
  data: DataPoint[];
  options?: {
    showLegend?: boolean;
    showGrid?: boolean;
    animate?: boolean;
    responsive?: boolean;
    interaction?: boolean;
    stacked?: boolean;
  };
}

interface DataVisualizationProps {
  className?: string;
  refreshInterval?: number;
  enableAnimations?: boolean;
  enableInteractions?: boolean;
  exportFormats?: ('png' | 'svg' | 'pdf' | 'csv' | 'json')[];
  maxDataPoints?: number;
}

// =============================================================================
// COMPONENTE PRINCIPAL
// =============================================================================

export const DataVisualization: React.FC<DataVisualizationProps> = ({
  className = '',
  refreshInterval = 30000,
  enableAnimations = true,
  enableInteractions = true,
  exportFormats = ['png', 'svg', 'csv'],
  maxDataPoints = 50
}) => {
  const [selectedChartType, setSelectedChartType] = useState<ChartConfig['type']>('line');
  const [selectedTimeframe, setSelectedTimeframe] = useState('7d');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showLegend, setShowLegend] = useState(true);
  const [showGrid, setShowGrid] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [zoomLevel, setZoomLevel] = useState(1);

  // Hook de métricas de negócio
  const {
    data: businessMetrics,
    loading: metricsLoading,
    error: metricsError,
    refetch: refetchMetrics
  } = useBusinessMetrics(
    {},
    { enableRealTime: true, refreshInterval }
  );

  // Gerar dados simulados
  const generateData = useCallback((type: ChartConfig['type'], count: number): DataPoint[] => {
    const data: DataPoint[] = [];
    const now = new Date();
    
    for (let i = 0; i < count; i++) {
      const timestamp = new Date(now.getTime() - (count - i) * 24 * 60 * 60 * 1000);
      data.push({
        id: `data-${i}`,
        label: timestamp.toLocaleDateString(),
        value: Math.random() * 1000 + 100,
        color: `hsl(${(i * 137.5) % 360}, 70%, 50%)`,
        category: ['Performance', 'Usuários', 'Receita', 'Keywords'][i % 4],
        timestamp: timestamp.toISOString(),
        metadata: {
          trend: Math.random() > 0.5 ? 'up' : 'down',
          changePercent: (Math.random() - 0.5) * 20,
          confidence: Math.random() * 0.3 + 0.7
        }
      });
    }
    
    return data;
  }, []);

  // Configurações de gráficos
  const chartConfigs = useMemo(() => {
    const baseData = generateData(selectedChartType, maxDataPoints);
    
    return {
      performance: {
        type: 'line' as const,
        title: 'Performance das Keywords',
        description: 'Evolução da performance ao longo do tempo',
        data: baseData.filter((_, i) => i % 3 === 0),
        options: {
          showLegend: showLegend,
          showGrid: showGrid,
          animate: enableAnimations,
          responsive: true,
          interaction: enableInteractions
        }
      },
      users: {
        type: 'bar' as const,
        title: 'Atividade de Usuários',
        description: 'Número de usuários ativos por período',
        data: baseData.filter((_, i) => i % 2 === 0),
        options: {
          showLegend: showLegend,
          showGrid: showGrid,
          animate: enableAnimations,
          responsive: true,
          interaction: enableInteractions,
          stacked: false
        }
      },
      revenue: {
        type: 'area' as const,
        title: 'Receita e Conversões',
        description: 'Receita gerada e taxa de conversão',
        data: baseData.filter((_, i) => i % 4 === 0),
        options: {
          showLegend: showLegend,
          showGrid: showGrid,
          animate: enableAnimations,
          responsive: true,
          interaction: enableInteractions
        }
      },
      distribution: {
        type: 'pie' as const,
        title: 'Distribuição por Categoria',
        description: 'Distribuição de métricas por categoria',
        data: baseData.slice(0, 6),
        options: {
          showLegend: showLegend,
          showGrid: false,
          animate: enableAnimations,
          responsive: true,
          interaction: enableInteractions
        }
      },
      trends: {
        type: 'scatter' as const,
        title: 'Análise de Tendências',
        description: 'Correlação entre diferentes métricas',
        data: baseData.slice(0, 20),
        options: {
          showLegend: showLegend,
          showGrid: showGrid,
          animate: enableAnimations,
          responsive: true,
          interaction: enableInteractions
        }
      }
    };
  }, [selectedChartType, maxDataPoints, showLegend, showGrid, enableAnimations, enableInteractions, generateData]);

  // Auto-refresh
  useEffect(() => {
    const interval = setInterval(() => {
      refetchMetrics();
      setLastUpdate(new Date());
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval, refetchMetrics]);

  // Handlers
  const handleExport = async (format: string) => {
    setIsExporting(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const exportData = {
        chartType: selectedChartType,
        data: chartConfigs[Object.keys(chartConfigs)[0] as keyof typeof chartConfigs].data,
        timestamp: new Date().toISOString(),
        format
      };

      if (format === 'json') {
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
          type: 'application/json'
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `data-visualization-${new Date().toISOString()}.json`;
        a.click();
        URL.revokeObjectURL(url);
      } else {
        console.log(`Exportando em formato ${format}`);
      }
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
          title: 'Data Visualization',
          text: 'Visualização de dados do Omni Keywords Finder',
          url: window.location.href
        });
      } catch (error) {
        console.error('Erro ao compartilhar:', error);
      }
    }
  };

  const handleZoom = (direction: 'in' | 'out') => {
    if (direction === 'in' && zoomLevel < 3) {
      setZoomLevel(zoomLevel + 0.5);
    } else if (direction === 'out' && zoomLevel > 0.5) {
      setZoomLevel(zoomLevel - 0.5);
    }
  };

  const handleReset = () => {
    setZoomLevel(1);
  };

  // Renderizar gráfico baseado no tipo
  const renderChart = (config: ChartConfig) => {
    const { type, data, options } = config;
    
    switch (type) {
      case 'line':
        return renderLineChart(data, options);
      case 'bar':
        return renderBarChart(data, options);
      case 'pie':
        return renderPieChart(data, options);
      case 'area':
        return renderAreaChart(data, options);
      case 'scatter':
        return renderScatterChart(data, options);
      default:
        return renderLineChart(data, options);
    }
  };

  const renderLineChart = (data: DataPoint[], options?: ChartConfig['options']) => (
    <div className="relative h-80 w-full overflow-hidden">
      <svg 
        className="w-full h-full" 
        viewBox="0 0 800 300"
        style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center' }}
      >
        {/* Grid */}
        {options?.showGrid && (
          <g className="grid-lines">
            {Array.from({ length: 5 }).map((_, i) => (
              <line
                key={i}
                x1="0"
                y1={60 * i}
                x2="800"
                y2={60 * i}
                stroke="#e5e7eb"
                strokeWidth="1"
              />
            ))}
          </g>
        )}
        
        {/* Data line */}
        <path
          d={data.map((point, i) => {
            const x = (i / (data.length - 1)) * 800;
            const y = 300 - (point.value / 1000) * 300;
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
          }).join(' ')}
          stroke="#3b82f6"
          strokeWidth="3"
          fill="none"
          className={options?.animate ? 'animate-draw' : ''}
        />
        
        {/* Data points */}
        {data.map((point, i) => {
          const x = (i / (data.length - 1)) * 800;
          const y = 300 - (point.value / 1000) * 300;
          return (
            <circle
              key={point.id}
              cx={x}
              cy={y}
              r="4"
              fill="#3b82f6"
              className={options?.interaction ? 'cursor-pointer hover:r-6 transition-all' : ''}
            />
          );
        })}
      </svg>
    </div>
  );

  const renderBarChart = (data: DataPoint[], options?: ChartConfig['options']) => (
    <div className="relative h-80 w-full overflow-hidden">
      <svg 
        className="w-full h-full" 
        viewBox="0 0 800 300"
        style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center' }}
      >
        {/* Grid */}
        {options?.showGrid && (
          <g className="grid-lines">
            {Array.from({ length: 5 }).map((_, i) => (
              <line
                key={i}
                x1="0"
                y1={60 * i}
                x2="800"
                y2={60 * i}
                stroke="#e5e7eb"
                strokeWidth="1"
              />
            ))}
          </g>
        )}
        
        {/* Bars */}
        {data.map((point, i) => {
          const x = (i / data.length) * 800 + 20;
          const width = (800 / data.length) - 40;
          const height = (point.value / 1000) * 300;
          const y = 300 - height;
          
          return (
            <rect
              key={point.id}
              x={x}
              y={y}
              width={width}
              height={height}
              fill={point.color || '#3b82f6'}
              className={options?.interaction ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}
            />
          );
        })}
      </svg>
    </div>
  );

  const renderPieChart = (data: DataPoint[], options?: ChartConfig['options']) => (
    <div className="relative h-80 w-full flex items-center justify-center">
      <svg 
        className="w-64 h-64" 
        viewBox="0 0 200 200"
        style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center' }}
      >
        <circle cx="100" cy="100" r="80" fill="none" stroke="#e5e7eb" strokeWidth="2" />
        
        {data.map((point, i) => {
          const total = data.reduce((sum, d) => sum + d.value, 0);
          const percentage = point.value / total;
          const startAngle = data.slice(0, i).reduce((sum, d) => sum + (d.value / total) * 360, 0);
          const endAngle = startAngle + percentage * 360;
          
          const x1 = 100 + 80 * Math.cos((startAngle - 90) * Math.PI / 180);
          const y1 = 100 + 80 * Math.sin((startAngle - 90) * Math.PI / 180);
          const x2 = 100 + 80 * Math.cos((endAngle - 90) * Math.PI / 180);
          const y2 = 100 + 80 * Math.sin((endAngle - 90) * Math.PI / 180);
          
          const largeArcFlag = percentage > 0.5 ? 1 : 0;
          
          return (
            <path
              key={point.id}
              d={`M 100 100 L ${x1} ${y1} A 80 80 0 ${largeArcFlag} 1 ${x2} ${y2} Z`}
              fill={point.color || '#3b82f6'}
              className={options?.interaction ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}
            />
          );
        })}
      </svg>
      
      {/* Center text */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <p className="text-2xl font-bold">{data.length}</p>
          <p className="text-sm text-muted-foreground">Categorias</p>
        </div>
      </div>
    </div>
  );

  const renderAreaChart = (data: DataPoint[], options?: ChartConfig['options']) => (
    <div className="relative h-80 w-full overflow-hidden">
      <svg 
        className="w-full h-full" 
        viewBox="0 0 800 300"
        style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center' }}
      >
        {/* Grid */}
        {options?.showGrid && (
          <g className="grid-lines">
            {Array.from({ length: 5 }).map((_, i) => (
              <line
                key={i}
                x1="0"
                y1={60 * i}
                x2="800"
                y2={60 * i}
                stroke="#e5e7eb"
                strokeWidth="1"
              />
            ))}
          </g>
        )}
        
        {/* Area fill */}
        <path
          d={`M 0 300 ${data.map((point, i) => {
            const x = (i / (data.length - 1)) * 800;
            const y = 300 - (point.value / 1000) * 300;
            return `L ${x} ${y}`;
          }).join(' ')} L 800 300 Z`}
          fill="url(#areaGradient)"
          opacity="0.3"
        />
        
        {/* Line */}
        <path
          d={data.map((point, i) => {
            const x = (i / (data.length - 1)) * 800;
            const y = 300 - (point.value / 1000) * 300;
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
          }).join(' ')}
          stroke="#3b82f6"
          strokeWidth="3"
          fill="none"
        />
        
        {/* Gradient definition */}
        <defs>
          <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.1" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );

  const renderScatterChart = (data: DataPoint[], options?: ChartConfig['options']) => (
    <div className="relative h-80 w-full overflow-hidden">
      <svg 
        className="w-full h-full" 
        viewBox="0 0 800 300"
        style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center' }}
      >
        {/* Grid */}
        {options?.showGrid && (
          <g className="grid-lines">
            {Array.from({ length: 5 }).map((_, i) => (
              <line
                key={i}
                x1="0"
                y1={60 * i}
                x2="800"
                y2={60 * i}
                stroke="#e5e7eb"
                strokeWidth="1"
              />
            ))}
          </g>
        )}
        
        {/* Scatter points */}
        {data.map((point, i) => {
          const x = (i / data.length) * 800;
          const y = 300 - (point.value / 1000) * 300;
          const size = (point.metadata?.confidence || 0.5) * 10 + 5;
          
          return (
            <circle
              key={point.id}
              cx={x}
              cy={y}
              r={size}
              fill={point.color || '#3b82f6'}
              opacity={0.7}
              className={options?.interaction ? 'cursor-pointer hover:opacity-100 transition-opacity' : ''}
            />
          );
        })}
      </svg>
    </div>
  );

  // Renderização de loading
  if (metricsLoading) {
    return (
      <div className={`data-visualization ${className}`}>
        <div className="grid gap-6">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-96" />
        </div>
      </div>
    );
  }

  // Renderização de erro
  if (metricsError) {
    return (
      <div className={`data-visualization ${className}`}>
        <Alert variant="destructive">
          <AlertDescription>
            Erro ao carregar dados: {metricsError.message}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className={`data-visualization ${className}`}>
      {/* Header com controles */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Data Visualization</h1>
          <p className="text-muted-foreground">
            Visualização avançada de dados com múltiplos tipos de gráficos
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Select value={selectedTimeframe} onValueChange={setSelectedTimeframe}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1d">1 dia</SelectItem>
              <SelectItem value="7d">7 dias</SelectItem>
              <SelectItem value="30d">30 dias</SelectItem>
              <SelectItem value="90d">90 dias</SelectItem>
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
            onClick={() => handleZoom('in')}
            disabled={zoomLevel >= 3}
          >
            <ZoomIn className="h-4 w-4 mr-2" />
            Zoom In
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => handleZoom('out')}
            disabled={zoomLevel <= 0.5}
          >
            <ZoomOut className="h-4 w-4 mr-2" />
            Zoom Out
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleReset}
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowLegend(!showLegend)}
          >
            {showLegend ? <Eye className="h-4 w-4 mr-2" /> : <EyeOff className="h-4 w-4 mr-2" />}
            Legenda
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowGrid(!showGrid)}
          >
            <Filter className="h-4 w-4 mr-2" />
            Grid
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
          <Activity className="h-4 w-4 text-blue-500" />
          Zoom: {Math.round(zoomLevel * 100)}%
        </div>

        <div className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-green-500" />
          {maxDataPoints} pontos de dados
        </div>

        <div className="flex items-center gap-2">
          <Settings className="h-4 w-4 text-purple-500" />
          Animações {enableAnimations ? 'ativas' : 'desativadas'}
        </div>
      </div>

      {/* Métricas rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Dados</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.values(chartConfigs).reduce((sum, config) => sum + config.data.length, 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Pontos de dados ativos
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tipos de Gráfico</CardTitle>
            <PieChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.keys(chartConfigs).length}
            </div>
            <p className="text-xs text-muted-foreground">
              Visualizações disponíveis
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Interatividade</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {enableInteractions ? 'Ativa' : 'Inativa'}
            </div>
            <p className="text-xs text-muted-foreground">
              Hover e zoom habilitados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Performance</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Math.round(performance.now() / 1000)}ms
            </div>
            <p className="text-xs text-muted-foreground">
              Tempo de renderização
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs de gráficos */}
      <Tabs defaultValue="performance" className="space-y-4">
        <TabsList>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="users">Usuários</TabsTrigger>
          <TabsTrigger value="revenue">Receita</TabsTrigger>
          <TabsTrigger value="distribution">Distribuição</TabsTrigger>
          <TabsTrigger value="trends">Tendências</TabsTrigger>
        </TabsList>

        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{chartConfigs.performance.title}</CardTitle>
              <p className="text-sm text-muted-foreground">
                {chartConfigs.performance.description}
              </p>
            </CardHeader>
            <CardContent>
              {renderChart(chartConfigs.performance)}
              
              {/* Legend */}
              {showLegend && (
                <div className="mt-4 flex flex-wrap gap-4">
                  {chartConfigs.performance.data.slice(0, 5).map(point => (
                    <div key={point.id} className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: point.color }}
                      />
                      <span className="text-sm">{point.label}</span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="users" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{chartConfigs.users.title}</CardTitle>
              <p className="text-sm text-muted-foreground">
                {chartConfigs.users.description}
              </p>
            </CardHeader>
            <CardContent>
              {renderChart(chartConfigs.users)}
              
              {/* Legend */}
              {showLegend && (
                <div className="mt-4 flex flex-wrap gap-4">
                  {chartConfigs.users.data.slice(0, 5).map(point => (
                    <div key={point.id} className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: point.color }}
                      />
                      <span className="text-sm">{point.label}</span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="revenue" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{chartConfigs.revenue.title}</CardTitle>
              <p className="text-sm text-muted-foreground">
                {chartConfigs.revenue.description}
              </p>
            </CardHeader>
            <CardContent>
              {renderChart(chartConfigs.revenue)}
              
              {/* Legend */}
              {showLegend && (
                <div className="mt-4 flex flex-wrap gap-4">
                  {chartConfigs.revenue.data.slice(0, 5).map(point => (
                    <div key={point.id} className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: point.color }}
                      />
                      <span className="text-sm">{point.label}</span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="distribution" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{chartConfigs.distribution.title}</CardTitle>
              <p className="text-sm text-muted-foreground">
                {chartConfigs.distribution.description}
              </p>
            </CardHeader>
            <CardContent>
              {renderChart(chartConfigs.distribution)}
              
              {/* Legend */}
              {showLegend && (
                <div className="mt-4 flex flex-wrap gap-4">
                  {chartConfigs.distribution.data.map(point => (
                    <div key={point.id} className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: point.color }}
                      />
                      <span className="text-sm">{point.label}</span>
                      <Badge variant="outline">{formatNumber(point.value)}</Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{chartConfigs.trends.title}</CardTitle>
              <p className="text-sm text-muted-foreground">
                {chartConfigs.trends.description}
              </p>
            </CardHeader>
            <CardContent>
              {renderChart(chartConfigs.trends)}
              
              {/* Legend */}
              {showLegend && (
                <div className="mt-4 flex flex-wrap gap-4">
                  {chartConfigs.trends.data.slice(0, 5).map(point => (
                    <div key={point.id} className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: point.color }}
                      />
                      <span className="text-sm">{point.label}</span>
                      <Badge variant="outline">
                        {(point.metadata?.confidence * 100).toFixed(0)}%
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}; 