/**
 * AdvancedAnalytics.tsx
 * 
 * Dashboard de Analytics Avançado - Omni Keywords Finder
 * 
 * Prompt: CHECKLIST_PRIMEIRA_REVISAO.md - Item 15
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2024-12-19
 * 
 * Funcionalidades:
 * - Métricas de performance de keywords
 * - Análise de eficiência de clusters
 * - Análise de comportamento do usuário
 * - Insights preditivos
 * - Exportação de dados
 * - Personalização de dashboards
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Card, Row, Col, Statistic, Button, Dropdown, Space, Select, DatePicker, 
  Table, Tag, Progress, Alert, Modal, Form, Input, Switch, message, Spin,
  Tabs, Tooltip, Badge, Divider, Typography
} from 'antd';
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer,
  Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';
import { 
  DownloadOutlined, 
  ReloadOutlined, 
  SettingOutlined,
  EyeOutlined,
  BarChartOutlined,
  UserOutlined,
  SearchOutlined,
  ClusterOutlined,
  TrendingUpOutlined,
  BulbOutlined,
  ExportOutlined,
  CustomizeOutlined,
  FilterOutlined,
  InfoCircleOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  TrophyOutlined,
  FireOutlined,
  RocketOutlined
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { TabPane } = Tabs;
const { Title, Text } = Typography;

// Tipos de dados
interface KeywordPerformance {
  id: string;
  termo: string;
  volume_busca: number;
  cpc: number;
  concorrencia: number;
  score_qualidade: number;
  tempo_processamento: number;
  status: 'success' | 'error' | 'pending';
  categoria: string;
  nicho: string;
  data_processamento: string;
  roi_estimado: number;
  conversao_estimada: number;
}

interface ClusterEfficiency {
  id: string;
  nome: string;
  keywords_count: number;
  score_medio: number;
  diversidade_semantica: number;
  coesao_interna: number;
  tempo_geracao: number;
  qualidade_geral: number;
  categoria: string;
  nicho: string;
  data_criacao: string;
  keywords: KeywordPerformance[];
}

interface UserBehavior {
  user_id: string;
  session_id: string;
  timestamp: string;
  action_type: 'search' | 'export' | 'analyze' | 'cluster' | 'view';
  action_details: any;
  duration: number;
  success: boolean;
  device_type: 'desktop' | 'mobile' | 'tablet';
  browser: string;
  location: string;
}

interface PredictiveInsight {
  id: string;
  type: 'keyword_trend' | 'cluster_performance' | 'user_engagement' | 'revenue_forecast';
  title: string;
  description: string;
  confidence: number;
  predicted_value: number;
  current_value: number;
  trend: 'up' | 'down' | 'stable';
  timeframe: string;
  factors: string[];
  recommendations: string[];
}

interface AnalyticsData {
  keywords_performance: KeywordPerformance[];
  clusters_efficiency: ClusterEfficiency[];
  user_behavior: UserBehavior[];
  predictive_insights: PredictiveInsight[];
  summary_metrics: {
    total_keywords: number;
    total_clusters: number;
    avg_processing_time: number;
    success_rate: number;
    avg_roi: number;
    user_engagement_score: number;
    cluster_quality_score: number;
  };
}

interface AdvancedAnalyticsProps {
  refreshInterval?: number;
  enableRealTime?: boolean;
  showPredictions?: boolean;
  customFilters?: any;
}

export const AdvancedAnalytics: React.FC<AdvancedAnalyticsProps> = ({
  refreshInterval = 10000,
  enableRealTime = true,
  showPredictions = true,
  customFilters = {}
}) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [timeRange, setTimeRange] = useState<'1d' | '7d' | '30d' | '90d'>('7d');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedNicho, setSelectedNicho] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'overview' | 'detailed' | 'predictive'>('overview');
  const [customizationModal, setCustomizationModal] = useState(false);
  const [exportModal, setExportModal] = useState(false);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['performance', 'efficiency', 'behavior']);

  // Estados para personalização
  const [customWidgets, setCustomWidgets] = useState<string[]>(['keywords_performance', 'cluster_efficiency', 'user_behavior']);
  const [widgetSettings, setWidgetSettings] = useState<Record<string, any>>({});

  // Carregar dados
  useEffect(() => {
    fetchAnalyticsData();
    const interval = setInterval(fetchAnalyticsData, refreshInterval);
    return () => clearInterval(interval);
  }, [timeRange, selectedCategory, selectedNicho, refreshInterval]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/analytics/advanced?timeRange=${timeRange}&category=${selectedCategory}&nicho=${selectedNicho}`);
      const result = await response.json();
      
      if (result.success) {
        setData(result.data);
      } else {
        message.error('Erro ao carregar dados de analytics');
      }
    } catch (error) {
      console.error('Erro ao buscar dados de analytics:', error);
      message.error('Erro de conexão');
    } finally {
      setLoading(false);
    }
  };

  // Calcular métricas derivadas
  const calculatedMetrics = useMemo(() => {
    if (!data) return null;

    const keywords = data.keywords_performance;
    const clusters = data.clusters_efficiency;
    const users = data.user_behavior;

    // Métricas de performance de keywords
    const avgProcessingTime = keywords.reduce((sum, k) => sum + k.tempo_processamento, 0) / keywords.length;
    const successRate = (keywords.filter(k => k.status === 'success').length / keywords.length) * 100;
    const avgROI = keywords.reduce((sum, k) => sum + k.roi_estimado, 0) / keywords.length;

    // Métricas de eficiência de clusters
    const avgClusterQuality = clusters.reduce((sum, c) => sum + c.qualidade_geral, 0) / clusters.length;
    const avgGenerationTime = clusters.reduce((sum, c) => sum + c.tempo_geracao, 0) / clusters.length;
    const avgDiversity = clusters.reduce((sum, c) => sum + c.diversidade_semantica, 0) / clusters.length;

    // Métricas de comportamento do usuário
    const avgSessionDuration = users.reduce((sum, u) => sum + u.duration, 0) / users.length;
    const successActions = users.filter(u => u.success).length / users.length * 100;
    const mobileUsage = users.filter(u => u.device_type === 'mobile').length / users.length * 100;

    return {
      keywords: { avgProcessingTime, successRate, avgROI },
      clusters: { avgClusterQuality, avgGenerationTime, avgDiversity },
      users: { avgSessionDuration, successActions, mobileUsage }
    };
  }, [data]);

  // Dados para gráficos
  const chartData = useMemo(() => {
    if (!data) return {};

    // Performance de keywords ao longo do tempo
    const keywordPerformanceData = data.keywords_performance
      .sort((a, b) => new Date(a.data_processamento).getTime() - new Date(b.data_processamento).getTime())
      .map(k => ({
        date: new Date(k.data_processamento).toLocaleDateString('pt-BR'),
        processing_time: k.tempo_processamento,
        roi: k.roi_estimado,
        volume: k.volume_busca,
        score: k.score_qualidade
      }));

    // Eficiência de clusters
    const clusterEfficiencyData = data.clusters_efficiency.map(c => ({
      name: c.nome,
      quality: c.qualidade_geral,
      diversity: c.diversidade_semantica,
      cohesion: c.coesao_interna,
      keywords_count: c.keywords_count,
      generation_time: c.tempo_geracao
    }));

    // Comportamento do usuário
    const userBehaviorData = data.user_behavior.reduce((acc, u) => {
      const hour = new Date(u.timestamp).getHours();
      const existing = acc.find(d => d.hour === hour);
      if (existing) {
        existing.count++;
        existing.duration += u.duration;
      } else {
        acc.push({ hour, count: 1, duration: u.duration });
      }
      return acc;
    }, [] as any[]).sort((a, b) => a.hour - b.hour);

    return {
      keywordPerformance: keywordPerformanceData,
      clusterEfficiency: clusterEfficiencyData,
      userBehavior: userBehaviorData
    };
  }, [data]);

  // Configurações de cores
  const chartColors = {
    performance: '#1890ff',
    efficiency: '#52c41a',
    behavior: '#722ed1',
    success: '#52c41a',
    warning: '#faad14',
    error: '#ff4d4f',
    info: '#1890ff'
  };

  // Função de exportação
  const handleExport = useCallback(async (format: 'csv' | 'json' | 'pdf' | 'excel') => {
    try {
      const response = await fetch('/api/v1/analytics/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          format,
          timeRange,
          category: selectedCategory,
          nicho: selectedNicho,
          metrics: selectedMetrics
        })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analytics_${timeRange}_${new Date().toISOString().split('T')[0]}.${format}`;
        a.click();
        window.URL.revokeObjectURL(url);
        message.success(`Exportação em ${format.toUpperCase()} concluída`);
      } else {
        message.error('Erro na exportação');
      }
    } catch (error) {
      console.error('Erro na exportação:', error);
      message.error('Erro na exportação');
    }
  }, [timeRange, selectedCategory, selectedNicho, selectedMetrics]);

  // Renderizar métricas de performance de keywords
  const renderKeywordPerformance = () => (
    <Card title="Performance de Keywords" extra={
      <Space>
        <Button size="small" icon={<EyeOutlined />}>Detalhes</Button>
        <Button size="small" icon={<ExportOutlined />} onClick={() => handleExport('csv')}>Exportar</Button>
      </Space>
    }>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={8}>
          <Statistic
            title="Tempo Médio de Processamento"
            value={calculatedMetrics?.keywords.avgProcessingTime || 0}
            suffix="ms"
            valueStyle={{ color: chartColors.performance }}
            prefix={<ClockCircleOutlined />}
          />
        </Col>
        <Col xs={24} sm={8}>
          <Statistic
            title="Taxa de Sucesso"
            value={calculatedMetrics?.keywords.successRate || 0}
            suffix="%"
            valueStyle={{ color: chartColors.success }}
            prefix={<CheckCircleOutlined />}
          />
        </Col>
        <Col xs={24} sm={8}>
          <Statistic
            title="ROI Médio"
            value={calculatedMetrics?.keywords.avgROI || 0}
            suffix="%"
            valueStyle={{ color: chartColors.info }}
            prefix={<TrendingUpOutlined />}
          />
        </Col>
      </Row>

      <ResponsiveContainer width="100%" height={300} style={{ marginTop: 16 }}>
        <LineChart data={chartData.keywordPerformance}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <RechartsTooltip />
          <Legend />
          <Line type="monotone" dataKey="processing_time" stroke={chartColors.performance} name="Tempo (ms)" />
          <Line type="monotone" dataKey="roi" stroke={chartColors.success} name="ROI (%)" />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );

  // Renderizar eficiência de clusters
  const renderClusterEfficiency = () => (
    <Card title="Eficiência de Clusters" extra={
      <Space>
        <Button size="small" icon={<EyeOutlined />}>Detalhes</Button>
        <Button size="small" icon={<ExportOutlined />} onClick={() => handleExport('csv')}>Exportar</Button>
      </Space>
    }>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={8}>
          <Statistic
            title="Qualidade Média"
            value={calculatedMetrics?.clusters.avgClusterQuality || 0}
            suffix="/10"
            valueStyle={{ color: chartColors.efficiency }}
            prefix={<TrophyOutlined />}
          />
        </Col>
        <Col xs={24} sm={8}>
          <Statistic
            title="Tempo de Geração"
            value={calculatedMetrics?.clusters.avgGenerationTime || 0}
            suffix="s"
            valueStyle={{ color: chartColors.warning }}
            prefix={<ClockCircleOutlined />}
          />
        </Col>
        <Col xs={24} sm={8}>
          <Statistic
            title="Diversidade Semântica"
            value={calculatedMetrics?.clusters.avgDiversity || 0}
            suffix="/10"
            valueStyle={{ color: chartColors.behavior }}
            prefix={<ClusterOutlined />}
          />
        </Col>
      </Row>

      <ResponsiveContainer width="100%" height={300} style={{ marginTop: 16 }}>
        <RadarChart data={chartData.clusterEfficiency}>
          <PolarGrid />
          <PolarAngleAxis dataKey="name" />
          <PolarRadiusAxis />
          <Radar
            name="Qualidade"
            dataKey="quality"
            stroke={chartColors.efficiency}
            fill={chartColors.efficiency}
            fillOpacity={0.3}
          />
          <Radar
            name="Diversidade"
            dataKey="diversity"
            stroke={chartColors.behavior}
            fill={chartColors.behavior}
            fillOpacity={0.3}
          />
          <RechartsTooltip />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    </Card>
  );

  // Renderizar comportamento do usuário
  const renderUserBehavior = () => (
    <Card title="Comportamento do Usuário" extra={
      <Space>
        <Button size="small" icon={<EyeOutlined />}>Detalhes</Button>
        <Button size="small" icon={<ExportOutlined />} onClick={() => handleExport('csv')}>Exportar</Button>
      </Space>
    }>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={8}>
          <Statistic
            title="Duração Média da Sessão"
            value={calculatedMetrics?.users.avgSessionDuration || 0}
            suffix="min"
            valueStyle={{ color: chartColors.behavior }}
            prefix={<UserOutlined />}
          />
        </Col>
        <Col xs={24} sm={8}>
          <Statistic
            title="Taxa de Sucesso"
            value={calculatedMetrics?.users.successActions || 0}
            suffix="%"
            valueStyle={{ color: chartColors.success }}
            prefix={<CheckCircleOutlined />}
          />
        </Col>
        <Col xs={24} sm={8}>
          <Statistic
            title="Uso Mobile"
            value={calculatedMetrics?.users.mobileUsage || 0}
            suffix="%"
            valueStyle={{ color: chartColors.info }}
            prefix={<UserOutlined />}
          />
        </Col>
      </Row>

      <ResponsiveContainer width="100%" height={300} style={{ marginTop: 16 }}>
        <BarChart data={chartData.userBehavior}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="hour" />
          <YAxis />
          <RechartsTooltip />
          <Legend />
          <Bar dataKey="count" fill={chartColors.behavior} name="Ações" />
          <Bar dataKey="duration" fill={chartColors.info} name="Duração (min)" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );

  // Renderizar insights preditivos
  const renderPredictiveInsights = () => (
    <Card title="Insights Preditivos" extra={
      <Space>
        <Button size="small" icon={<BulbOutlined />}>Novos Insights</Button>
        <Button size="small" icon={<ExportOutlined />} onClick={() => handleExport('pdf')}>Relatório</Button>
      </Space>
    }>
      {data?.predictive_insights.map(insight => (
        <Alert
          key={insight.id}
          message={
            <div>
              <Title level={5}>{insight.title}</Title>
              <Text>{insight.description}</Text>
              <div style={{ marginTop: 8 }}>
                <Tag color={insight.trend === 'up' ? 'green' : insight.trend === 'down' ? 'red' : 'blue'}>
                  {insight.trend === 'up' ? '↗' : insight.trend === 'down' ? '↘' : '→'} {insight.predicted_value}
                </Tag>
                <Text type="secondary">Confiança: {insight.confidence}%</Text>
              </div>
            </div>
          }
          type={insight.trend === 'up' ? 'success' : insight.trend === 'down' ? 'warning' : 'info'}
          icon={<BulbOutlined />}
          style={{ marginBottom: 16 }}
        />
      ))}
    </Card>
  );

  // Renderizar tabela de dados detalhados
  const renderDetailedTable = () => {
    const columns = [
      {
        title: 'Keyword',
        dataKey: 'termo',
        key: 'termo',
        render: (text: string) => <Text strong>{text}</Text>
      },
      {
        title: 'Volume',
        dataKey: 'volume_busca',
        key: 'volume_busca',
        render: (value: number) => value.toLocaleString('pt-BR')
      },
      {
        title: 'CPC',
        dataKey: 'cpc',
        key: 'cpc',
        render: (value: number) => `R$ ${value.toFixed(2)}`
      },
      {
        title: 'Score',
        dataKey: 'score_qualidade',
        key: 'score_qualidade',
        render: (value: number) => (
          <Progress
            percent={value * 10}
            size="small"
            status={value >= 8 ? 'success' : value >= 6 ? 'normal' : 'exception'}
          />
        )
      },
      {
        title: 'ROI',
        dataKey: 'roi_estimado',
        key: 'roi_estimado',
        render: (value: number) => (
          <Tag color={value > 0 ? 'green' : 'red'}>
            {value > 0 ? '+' : ''}{value.toFixed(1)}%
          </Tag>
        )
      },
      {
        title: 'Status',
        dataKey: 'status',
        key: 'status',
        render: (status: string) => (
          <Tag color={status === 'success' ? 'green' : status === 'error' ? 'red' : 'orange'}>
            {status}
          </Tag>
        )
      }
    ];

    return (
      <Card title="Dados Detalhados" extra={
        <Space>
          <Select
            value={selectedCategory}
            onChange={setSelectedCategory}
            style={{ width: 150 }}
            placeholder="Filtrar por categoria"
          >
            <Option value="all">Todas as categorias</Option>
            <Option value="ecommerce">E-commerce</Option>
            <Option value="saas">SaaS</Option>
            <Option value="content">Content</Option>
          </Select>
          <Button icon={<ExportOutlined />} onClick={() => setExportModal(true)}>
            Exportar
          </Button>
        </Space>
      }>
        <Table
          dataSource={data?.keywords_performance || []}
          columns={columns}
          rowKey="id"
          pagination={{ pageSize: 10 }}
          scroll={{ x: 800 }}
        />
      </Card>
    );
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>Carregando analytics avançados...</div>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <BarChartOutlined style={{ marginRight: '12px' }} />
          Analytics Avançado
        </Title>
        <Text type="secondary">
          Análise profunda de performance, eficiência e comportamento do usuário
        </Text>
      </div>

      {/* Controles */}
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]} align="middle">
          <Col>
            <Space>
              <Text>Período:</Text>
              <Select value={timeRange} onChange={setTimeRange} style={{ width: 120 }}>
                <Option value="1d">Último dia</Option>
                <Option value="7d">Última semana</Option>
                <Option value="30d">Último mês</Option>
                <Option value="90d">Último trimestre</Option>
              </Select>
            </Space>
          </Col>
          <Col>
            <Space>
              <Text>Visualização:</Text>
              <Select value={viewMode} onChange={setViewMode} style={{ width: 120 }}>
                <Option value="overview">Visão Geral</Option>
                <Option value="detailed">Detalhado</Option>
                <Option value="predictive">Preditivo</Option>
              </Select>
            </Space>
          </Col>
          <Col>
            <Space>
              <Button icon={<ReloadOutlined />} onClick={fetchAnalyticsData}>
                Atualizar
              </Button>
              <Button icon={<CustomizeOutlined />} onClick={() => setCustomizationModal(true)}>
                Personalizar
              </Button>
              <Button icon={<ExportOutlined />} onClick={() => setExportModal(true)}>
                Exportar
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Conteúdo principal */}
      <Tabs activeKey={viewMode} onChange={setViewMode}>
        <TabPane tab="Visão Geral" key="overview">
          <Row gutter={[16, 16]}>
            {customWidgets.includes('keywords_performance') && (
              <Col xs={24} lg={12}>
                {renderKeywordPerformance()}
              </Col>
            )}
            {customWidgets.includes('cluster_efficiency') && (
              <Col xs={24} lg={12}>
                {renderClusterEfficiency()}
              </Col>
            )}
            {customWidgets.includes('user_behavior') && (
              <Col xs={24}>
                {renderUserBehavior()}
              </Col>
            )}
            {showPredictions && customWidgets.includes('predictive_insights') && (
              <Col xs={24}>
                {renderPredictiveInsights()}
              </Col>
            )}
          </Row>
        </TabPane>

        <TabPane tab="Detalhado" key="detailed">
          {renderDetailedTable()}
        </TabPane>

        <TabPane tab="Preditivo" key="predictive">
          {renderPredictiveInsights()}
        </TabPane>
      </Tabs>

      {/* Modal de personalização */}
      <Modal
        title="Personalizar Dashboard"
        open={customizationModal}
        onCancel={() => setCustomizationModal(false)}
        onOk={() => setCustomizationModal(false)}
        width={600}
      >
        <Form layout="vertical">
          <Form.Item label="Widgets Visíveis">
            <Select
              mode="multiple"
              value={customWidgets}
              onChange={setCustomWidgets}
              style={{ width: '100%' }}
            >
              <Option value="keywords_performance">Performance de Keywords</Option>
              <Option value="cluster_efficiency">Eficiência de Clusters</Option>
              <Option value="user_behavior">Comportamento do Usuário</Option>
              <Option value="predictive_insights">Insights Preditivos</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* Modal de exportação */}
      <Modal
        title="Exportar Dados"
        open={exportModal}
        onCancel={() => setExportModal(false)}
        onOk={() => setExportModal(false)}
        footer={null}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Button block icon={<DownloadOutlined />} onClick={() => handleExport('csv')}>
            Exportar CSV
          </Button>
          <Button block icon={<DownloadOutlined />} onClick={() => handleExport('json')}>
            Exportar JSON
          </Button>
          <Button block icon={<DownloadOutlined />} onClick={() => handleExport('pdf')}>
            Exportar PDF
          </Button>
          <Button block icon={<DownloadOutlined />} onClick={() => handleExport('excel')}>
            Exportar Excel
          </Button>
        </Space>
      </Modal>
    </div>
  );
};

export default AdvancedAnalytics; 