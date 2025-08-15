/**
 * PerformanceDashboard.tsx
 * 
 * Dashboard de Performance em Tempo Real - Omni Keywords Finder
 * 
 * Prompt: CHECKLIST_PRIMEIRA_REVISAO.md - Item 5
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2024-12-19
 * 
 * Funcionalidades:
 * - Métricas de performance em tempo real
 * - Gráficos interativos
 * - Alertas de performance
 * - Métricas de negócio
 * - Drill-down de dados
 * - Exportação de relatórios
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, Row, Col, Alert, Button, Dropdown, Space, Statistic, Progress } from 'antd';
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  Cell
} from 'recharts';
import { 
  DownloadOutlined, 
  ReloadOutlined, 
  SettingOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import { useWebSocket } from '../../hooks/useWebSocket';
import { usePerformanceMetrics } from '../../hooks/usePerformanceMetrics';
import { MetricsCard } from './MetricsCard';
import { AlertPanel } from './AlertPanel';
import { BusinessMetrics } from './BusinessMetrics';
import { ExportReports } from './ExportReports';

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

interface PerformanceDashboardProps {
  refreshInterval?: number;
  enableRealTime?: boolean;
  showAlerts?: boolean;
  showBusinessMetrics?: boolean;
}

export const PerformanceDashboard: React.FC<PerformanceDashboardProps> = ({
  refreshInterval = 5000,
  enableRealTime = true,
  showAlerts = true,
  showBusinessMetrics = true
}) => {
  const [performanceData, setPerformanceData] = useState<PerformanceData[]>([]);
  const [alerts, setAlerts] = useState<AlertData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('1h');
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['responseTime', 'throughput', 'errorRate']);

  // WebSocket para dados em tempo real
  const { data: realTimeData, isConnected } = useWebSocket<PerformanceData>(
    enableRealTime ? '/ws/performance' : null,
    refreshInterval
  );

  // Hook para métricas de performance
  const { 
    metrics: historicalMetrics, 
    isLoading: metricsLoading, 
    error: metricsError,
    refreshMetrics 
  } = usePerformanceMetrics(timeRange);

  // Atualizar dados quando receber dados em tempo real
  useEffect(() => {
    if (realTimeData) {
      setPerformanceData(prev => {
        const newData = [...prev, realTimeData];
        // Manter apenas os últimos 100 pontos para performance
        return newData.slice(-100);
      });
    }
  }, [realTimeData]);

  // Carregar dados históricos
  useEffect(() => {
    if (historicalMetrics && !metricsLoading) {
      setPerformanceData(historicalMetrics);
    }
  }, [historicalMetrics, metricsLoading]);

  // Simular alertas (em produção viria do backend)
  useEffect(() => {
    const mockAlerts: AlertData[] = [
      {
        id: '1',
        type: 'warning',
        message: 'Tempo de resposta acima do threshold (2.5s)',
        timestamp: new Date().toISOString(),
        severity: 'medium'
      },
      {
        id: '2',
        type: 'error',
        message: 'Taxa de erro aumentou para 5.2%',
        timestamp: new Date().toISOString(),
        severity: 'high'
      }
    ];
    setAlerts(mockAlerts);
  }, []);

  // Calcular métricas agregadas
  const aggregatedMetrics = useCallback(() => {
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
  }, [performanceData]);

  const calculatedMetrics = aggregatedMetrics();

  // Configurações de cores para gráficos
  const chartColors = {
    responseTime: '#1890ff',
    throughput: '#52c41a',
    errorRate: '#ff4d4f',
    cpuUsage: '#722ed1',
    memoryUsage: '#fa8c16',
    activeUsers: '#13c2c2'
  };

  // Função para exportar relatórios
  const handleExport = useCallback((format: 'pdf' | 'csv' | 'json') => {
    // console.log(`Exportando relatório em formato ${format}`); // Removido para produção
    // Implementar lógica de exportação
  }, []);

  // Função para refresh manual
  const handleRefresh = useCallback(() => {
    setIsLoading(true);
    refreshMetrics().finally(() => setIsLoading(false));
  }, [refreshMetrics]);

  if (metricsError) {
    return (
      <Alert
        message="Erro ao carregar métricas"
        description={metricsError.message}
        type="error"
        showIcon
        action={
          <Button size="small" onClick={handleRefresh}>
            Tentar Novamente
          </Button>
        }
      />
    );
  }

  return (
    <div className="performance-dashboard">
      {/* Header com controles */}
      <Card className="dashboard-header" style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <h2 style={{ margin: 0 }}>
              <ClockCircleOutlined style={{ marginRight: 8 }} />
              Dashboard de Performance em Tempo Real
            </h2>
            <p style={{ margin: 0, color: '#666' }}>
              Última atualização: {new Date().toLocaleString('pt-BR')}
              {isConnected && <CheckCircleOutlined style={{ marginLeft: 8, color: '#52c41a' }} />}
            </p>
          </Col>
          <Col>
            <Space>
              <Dropdown
                menu={{
                  items: [
                    { key: '1h', label: 'Última Hora' },
                    { key: '6h', label: 'Últimas 6 Horas' },
                    { key: '24h', label: 'Últimas 24 Horas' },
                    { key: '7d', label: 'Últimos 7 Dias' }
                  ],
                  onClick: ({ key }) => setTimeRange(key as any)
                }}
              >
                <Button>
                  {timeRange === '1h' ? '1H' : timeRange === '6h' ? '6H' : timeRange === '24h' ? '24H' : '7D'}
                </Button>
              </Dropdown>
              <Button 
                icon={<ReloadOutlined />} 
                loading={isLoading}
                onClick={handleRefresh}
              >
                Atualizar
              </Button>
              <Button icon={<SettingOutlined />}>
                Configurações
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Alertas */}
      {showAlerts && alerts.length > 0 && (
        <AlertPanel alerts={alerts} onDismiss={(id) => {
          setAlerts(prev => prev.filter(alert => alert.id !== id));
        }} />
      )}

      {/* Métricas Principais */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} sm={12} md={6}>
          <MetricsCard
            title="Tempo de Resposta"
            value={calculatedMetrics?.current.responseTime || 0}
            unit="ms"
            trend={calculatedMetrics?.average.responseTime || 0}
            status={calculatedMetrics?.current.responseTime > 2000 ? 'warning' : 'success'}
            icon={<ClockCircleOutlined />}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <MetricsCard
            title="Throughput"
            value={calculatedMetrics?.current.throughput || 0}
            unit="req/s"
            trend={calculatedMetrics?.average.throughput || 0}
            status="success"
            icon={<CheckCircleOutlined />}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <MetricsCard
            title="Taxa de Erro"
            value={calculatedMetrics?.current.errorRate || 0}
            unit="%"
            trend={calculatedMetrics?.average.errorRate || 0}
            status={calculatedMetrics?.current.errorRate > 5 ? 'error' : 'success'}
            icon={<WarningOutlined />}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <MetricsCard
            title="Usuários Ativos"
            value={calculatedMetrics?.current.activeUsers || 0}
            unit=""
            trend={0}
            status="success"
            icon={<CheckCircleOutlined />}
          />
        </Col>
      </Row>

      {/* Gráficos */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} lg={16}>
          <Card title="Performance em Tempo Real" extra={
            <Dropdown
              menu={{
                items: [
                  { key: 'responseTime', label: 'Tempo de Resposta' },
                  { key: 'throughput', label: 'Throughput' },
                  { key: 'errorRate', label: 'Taxa de Erro' },
                  { key: 'cpuUsage', label: 'Uso de CPU' },
                  { key: 'memoryUsage', label: 'Uso de Memória' }
                ],
                onClick: ({ key }) => {
                  setSelectedMetrics(prev => 
                    prev.includes(key) 
                      ? prev.filter(m => m !== key)
                      : [...prev, key]
                  );
                }
              }}
            >
              <Button size="small">Métricas</Button>
            </Dropdown>
          }>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(value) => new Date(value).toLocaleTimeString('pt-BR')}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleString('pt-BR')}
                  formatter={(value, name) => [
                    typeof value === 'number' ? value.toFixed(2) : value,
                    name === 'responseTime' ? 'Tempo (ms)' :
                    name === 'throughput' ? 'Throughput (req/s)' :
                    name === 'errorRate' ? 'Erro (%)' :
                    name === 'cpuUsage' ? 'CPU (%)' :
                    name === 'memoryUsage' ? 'Memória (%)' : name
                  ]}
                />
                <Legend />
                {selectedMetrics.includes('responseTime') && (
                  <Line 
                    type="monotone" 
                    dataKey="responseTime" 
                    stroke={chartColors.responseTime} 
                    name="Tempo de Resposta"
                  />
                )}
                {selectedMetrics.includes('throughput') && (
                  <Line 
                    type="monotone" 
                    dataKey="throughput" 
                    stroke={chartColors.throughput} 
                    name="Throughput"
                  />
                )}
                {selectedMetrics.includes('errorRate') && (
                  <Line 
                    type="monotone" 
                    dataKey="errorRate" 
                    stroke={chartColors.errorRate} 
                    name="Taxa de Erro"
                  />
                )}
                {selectedMetrics.includes('cpuUsage') && (
                  <Line 
                    type="monotone" 
                    dataKey="cpuUsage" 
                    stroke={chartColors.cpuUsage} 
                    name="Uso de CPU"
                  />
                )}
                {selectedMetrics.includes('memoryUsage') && (
                  <Line 
                    type="monotone" 
                    dataKey="memoryUsage" 
                    stroke={chartColors.memoryUsage} 
                    name="Uso de Memória"
                  />
                )}
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Uso de Recursos">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span>CPU</span>
                  <span>{calculatedMetrics?.current.cpuUsage || 0}%</span>
                </div>
                <Progress 
                  percent={calculatedMetrics?.current.cpuUsage || 0} 
                  status={calculatedMetrics?.current.cpuUsage > 80 ? 'exception' : 'normal'}
                  strokeColor={chartColors.cpuUsage}
                />
              </div>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span>Memória</span>
                  <span>{calculatedMetrics?.current.memoryUsage || 0}%</span>
                </div>
                <Progress 
                  percent={calculatedMetrics?.current.memoryUsage || 0} 
                  status={calculatedMetrics?.current.memoryUsage > 80 ? 'exception' : 'normal'}
                  strokeColor={chartColors.memoryUsage}
                />
              </div>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* Métricas de Negócio */}
      {showBusinessMetrics && (
        <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
          <Col xs={24}>
            <BusinessMetrics 
              keywordsProcessed={calculatedMetrics?.current.keywordsProcessed || 0}
              clustersGenerated={calculatedMetrics?.current.clustersGenerated || 0}
              apiCalls={calculatedMetrics?.current.apiCalls || 0}
            />
          </Col>
        </Row>
      )}

      {/* Exportação de Relatórios */}
      <Card title="Exportação de Relatórios">
        <ExportReports 
          onExport={handleExport}
          data={performanceData}
          timeRange={timeRange}
        />
      </Card>
    </div>
  );
};

export default PerformanceDashboard; 