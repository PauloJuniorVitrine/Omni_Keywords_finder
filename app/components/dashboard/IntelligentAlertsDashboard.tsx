/**
 * IntelligentAlertsDashboard.tsx
 * 
 * Dashboard de Alertas Inteligentes - Omni Keywords Finder
 * Sistema completo de alertas com otimização, agrupamento e insights
 * 
 * Prompt: Implementação de sistema de alertas inteligentes
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * Tracing ID: INTELLIGENT_ALERTS_DASHBOARD_20250127_001
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Card,
  Table,
  Tag,
  Button,
  Space,
  Row,
  Col,
  Statistic,
  Progress,
  Alert,
  Modal,
  Form,
  Select,
  Input,
  Switch,
  Badge,
  Tooltip,
  Typography,
  Divider,
  Timeline,
  Collapse,
  Empty,
  Spin
} from 'antd';
import {
  BellOutlined,
  ExclamationCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  SettingOutlined,
  FilterOutlined,
  ReloadOutlined,
  EyeOutlined,
  EyeInvisibleOutlined,
  GroupOutlined,
  OptimizeOutlined,
  BarChartOutlined,
  ClockCircleOutlined,
  UserOutlined,
  DatabaseOutlined,
  ApiOutlined,
  SecurityScanOutlined
} from '@ant-design/icons';
import { Line, Pie, Column } from '@ant-design/plots';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;
const { Option } = Select;

// Tipos baseados no sistema real Omni Keywords Finder
interface AlertData {
  id: string;
  type: 'system_metric' | 'database_query' | 'error_event' | 'security_event' | 'health_check' | 'performance_degradation';
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: 'omni_keywords_finder_app' | 'database_service' | 'redis_cache' | 'firewall' | 'health_check_service' | 'api_gateway';
  message: string;
  timestamp: string;
  user_impact: boolean;
  impact_type: 'performance_degradation' | 'service_outage' | 'security_breach' | 'data_loss' | 'unknown';
  affected_users: number;
  duration_minutes: number;
  status: 'active' | 'acknowledged' | 'resolved' | 'suppressed' | 'grouped';
  suppression_reason?: 'false_positive' | 'duplicate' | 'low_severity' | 'frequent_pattern' | 'maintenance_window' | 'known_issue';
  group_id?: string;
  priority_score: number;
  impact_score: number;
  metadata?: Record<string, any>;
}

interface AlertGroup {
  id: string;
  strategy: 'by_source' | 'by_type' | 'by_severity' | 'by_time_window' | 'by_pattern' | 'by_impact';
  alerts: string[];
  summary: {
    total_alerts: number;
    highest_severity: string;
    average_priority: number;
    average_impact: number;
    affected_users_total: number;
  };
  created_at: string;
  is_active: boolean;
}

interface AlertStatistics {
  total_alerts: number;
  active_alerts: number;
  suppressed_alerts: number;
  grouped_alerts: number;
  resolved_alerts: number;
  reduction_percentage: number;
  average_response_time: number;
  top_sources: Array<{ source: string; count: number }>;
  severity_distribution: Array<{ severity: string; count: number }>;
}

interface AlertOptimizationConfig {
  enabled: boolean;
  grouping_window_minutes: number;
  suppression_threshold: number;
  max_alerts_per_group: number;
  pattern_detection_window: number;
}

// Dados reais baseados no sistema Omni Keywords Finder
const MOCK_ALERTS: AlertData[] = [
  {
    id: 'cpu_high_001',
    type: 'system_metric',
    severity: 'high',
    source: 'omni_keywords_finder_app',
    message: 'CPU usage exceeded 90% threshold',
    timestamp: '2025-01-27T15:30:00Z',
    user_impact: true,
    impact_type: 'performance_degradation',
    affected_users: 150,
    duration_minutes: 15,
    status: 'active',
    priority_score: 0.85,
    impact_score: 0.72
  },
  {
    id: 'slow_query_001',
    type: 'database_query',
    severity: 'medium',
    source: 'database_service',
    message: 'Query execution time exceeded 5 seconds',
    timestamp: '2025-01-27T15:25:00Z',
    user_impact: false,
    impact_type: 'performance_degradation',
    affected_users: 0,
    duration_minutes: 5,
    status: 'grouped',
    group_id: 'group_001',
    priority_score: 0.45,
    impact_score: 0.30
  },
  {
    id: 'connection_error_001',
    type: 'error_event',
    severity: 'high',
    source: 'database_service',
    message: 'Database connection timeout',
    timestamp: '2025-01-27T15:20:00Z',
    user_impact: true,
    impact_type: 'service_outage',
    affected_users: 500,
    duration_minutes: 30,
    status: 'acknowledged',
    priority_score: 0.95,
    impact_score: 0.88
  },
  {
    id: 'cache_full_001',
    type: 'system_metric',
    severity: 'medium',
    source: 'redis_cache',
    message: 'Cache usage exceeded 95%',
    timestamp: '2025-01-27T15:15:00Z',
    user_impact: false,
    impact_type: 'performance_degradation',
    affected_users: 0,
    duration_minutes: 10,
    status: 'suppressed',
    suppression_reason: 'frequent_pattern',
    priority_score: 0.35,
    impact_score: 0.25
  },
  {
    id: 'security_attack_001',
    type: 'security_event',
    severity: 'critical',
    source: 'firewall',
    message: 'SQL injection attempt detected',
    timestamp: '2025-01-27T15:10:00Z',
    user_impact: true,
    impact_type: 'security_breach',
    affected_users: 1000,
    duration_minutes: 5,
    status: 'active',
    priority_score: 1.0,
    impact_score: 0.95
  },
  {
    id: 'low_severity_001',
    type: 'health_check',
    severity: 'low',
    source: 'health_check_service',
    message: 'Health check failed',
    timestamp: '2025-01-27T15:05:00Z',
    user_impact: false,
    impact_type: 'unknown',
    affected_users: 0,
    duration_minutes: 1,
    status: 'suppressed',
    suppression_reason: 'low_severity',
    priority_score: 0.15,
    impact_score: 0.10
  }
];

const MOCK_GROUPS: AlertGroup[] = [
  {
    id: 'group_001',
    strategy: 'by_source',
    alerts: ['slow_query_001', 'connection_error_001'],
    summary: {
      total_alerts: 2,
      highest_severity: 'high',
      average_priority: 0.70,
      average_impact: 0.59,
      affected_users_total: 500
    },
    created_at: '2025-01-27T15:25:00Z',
    is_active: true
  }
];

const MOCK_STATISTICS: AlertStatistics = {
  total_alerts: 6,
  active_alerts: 2,
  suppressed_alerts: 2,
  grouped_alerts: 1,
  resolved_alerts: 0,
  reduction_percentage: 66.7,
  average_response_time: 2.5,
  top_sources: [
    { source: 'database_service', count: 2 },
    { source: 'omni_keywords_finder_app', count: 1 },
    { source: 'redis_cache', count: 1 },
    { source: 'firewall', count: 1 },
    { source: 'health_check_service', count: 1 }
  ],
  severity_distribution: [
    { severity: 'critical', count: 1 },
    { severity: 'high', count: 2 },
    { severity: 'medium', count: 2 },
    { severity: 'low', count: 1 }
  ]
};

interface IntelligentAlertsDashboardProps {
  refreshInterval?: number;
  showOptimization?: boolean;
  showGrouping?: boolean;
  maxAlerts?: number;
}

export const IntelligentAlertsDashboard: React.FC<IntelligentAlertsDashboardProps> = ({
  refreshInterval = 30000,
  showOptimization = true,
  showGrouping = true,
  maxAlerts = 50
}) => {
  const [alerts, setAlerts] = useState<AlertData[]>(MOCK_ALERTS);
  const [groups, setGroups] = useState<AlertGroup[]>(MOCK_GROUPS);
  const [statistics, setStatistics] = useState<AlertStatistics>(MOCK_STATISTICS);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    severity: [] as string[],
    source: [] as string[],
    type: [] as string[],
    status: [] as string[],
    user_impact: null as boolean | null
  });
  const [optimizationConfig, setOptimizationConfig] = useState<AlertOptimizationConfig>({
    enabled: true,
    grouping_window_minutes: 5,
    suppression_threshold: 0.8,
    max_alerts_per_group: 10,
    pattern_detection_window: 60
  });
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<AlertData | null>(null);
  const [showAlertDetails, setShowAlertDetails] = useState(false);

  // Simular carregamento de dados
  const loadData = async () => {
    setLoading(true);
    try {
      // Simular chamada API
      await new Promise(resolve => setTimeout(resolve, 1000));
      // Em produção, aqui viriam as chamadas reais para a API
      setAlerts(MOCK_ALERTS);
      setGroups(MOCK_GROUPS);
      setStatistics(MOCK_STATISTICS);
    } catch (error) {
      console.error('Erro ao carregar alertas:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  // Filtrar alertas
  const filteredAlerts = useMemo(() => {
    return alerts.filter(alert => {
      if (filters.severity.length > 0 && !filters.severity.includes(alert.severity)) return false;
      if (filters.source.length > 0 && !filters.source.includes(alert.source)) return false;
      if (filters.type.length > 0 && !filters.type.includes(alert.type)) return false;
      if (filters.status.length > 0 && !filters.status.includes(alert.status)) return false;
      if (filters.user_impact !== null && alert.user_impact !== filters.user_impact) return false;
      return true;
    });
  }, [alerts, filters]);

  // Configurações de colunas da tabela
  const columns = [
    {
      title: 'Severidade',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      render: (severity: string) => {
        const colors = {
          critical: '#ff4d4f',
          high: '#ff7875',
          medium: '#faad14',
          low: '#52c41a'
        };
        return <Tag color={colors[severity as keyof typeof colors]}>{severity.toUpperCase()}</Tag>;
      },
      sorter: (a: AlertData, b: AlertData) => {
        const order = { critical: 4, high: 3, medium: 2, low: 1 };
        return order[b.severity as keyof typeof order] - order[a.severity as keyof typeof order];
      }
    },
    {
      title: 'Fonte',
      dataIndex: 'source',
      key: 'source',
      width: 150,
      render: (source: string) => {
        const icons = {
          omni_keywords_finder_app: <ApiOutlined />,
          database_service: <DatabaseOutlined />,
          redis_cache: <DatabaseOutlined />,
          firewall: <SecurityScanOutlined />,
          health_check_service: <CheckCircleOutlined />
        };
        return (
          <Space>
            {icons[source as keyof typeof icons]}
            <Text>{source.replace(/_/g, ' ')}</Text>
          </Space>
        );
      }
    },
    {
      title: 'Mensagem',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
      render: (message: string, record: AlertData) => (
        <Tooltip title={message}>
          <Text style={{ cursor: 'pointer' }} onClick={() => {
            setSelectedAlert(record);
            setShowAlertDetails(true);
          }}>
            {message}
          </Text>
        </Tooltip>
      )
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string, record: AlertData) => {
        const statusConfig = {
          active: { color: '#ff4d4f', text: 'Ativo' },
          acknowledged: { color: '#faad14', text: 'Reconhecido' },
          resolved: { color: '#52c41a', text: 'Resolvido' },
          suppressed: { color: '#666', text: 'Suprimido' },
          grouped: { color: '#1890ff', text: 'Agrupado' }
        };
        const config = statusConfig[status as keyof typeof statusConfig];
        return (
          <Space>
            <Tag color={config.color}>{config.text}</Tag>
            {record.suppression_reason && (
              <Tooltip title={`Razão: ${record.suppression_reason}`}>
                <InfoCircleOutlined style={{ color: '#666' }} />
              </Tooltip>
            )}
          </Space>
        );
      }
    },
    {
      title: 'Impacto',
      dataIndex: 'user_impact',
      key: 'user_impact',
      width: 100,
      render: (user_impact: boolean, record: AlertData) => (
        <Space direction="vertical" size="small">
          <Badge 
            status={user_impact ? 'error' : 'default'} 
            text={user_impact ? 'Sim' : 'Não'} 
          />
          {user_impact && (
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {record.affected_users} usuários
            </Text>
          )}
        </Space>
      )
    },
    {
      title: 'Prioridade',
      dataIndex: 'priority_score',
      key: 'priority_score',
      width: 100,
      render: (score: number) => (
        <Progress 
          percent={Math.round(score * 100)} 
          size="small" 
          status={score > 0.8 ? 'exception' : score > 0.5 ? 'active' : 'normal'}
        />
      ),
      sorter: (a: AlertData, b: AlertData) => b.priority_score - a.priority_score
    },
    {
      title: 'Tempo',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 120,
      render: (timestamp: string) => (
        <Text type="secondary" style={{ fontSize: '12px' }}>
          {new Date(timestamp).toLocaleTimeString('pt-BR')}
        </Text>
      ),
      sorter: (a: AlertData, b: AlertData) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    },
    {
      title: 'Ações',
      key: 'actions',
      width: 120,
      render: (_, record: AlertData) => (
        <Space>
          <Button 
            type="link" 
            size="small" 
            icon={<EyeOutlined />}
            onClick={() => {
              setSelectedAlert(record);
              setShowAlertDetails(true);
            }}
          >
            Detalhes
          </Button>
          {record.status === 'active' && (
            <Button 
              type="link" 
              size="small" 
              icon={<CheckCircleOutlined />}
              onClick={() => handleAcknowledgeAlert(record.id)}
            >
              Reconhecer
            </Button>
          )}
        </Space>
      )
    }
  ];

  // Handlers
  const handleAcknowledgeAlert = (alertId: string) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId 
        ? { ...alert, status: 'acknowledged' as const }
        : alert
    ));
  };

  const handleUpdateOptimizationConfig = (config: AlertOptimizationConfig) => {
    setOptimizationConfig(config);
    setShowConfigModal(false);
    // Em produção, aqui seria feita a chamada para atualizar a configuração
  };

  const handleRefresh = () => {
    loadData();
  };

  // Configurações dos gráficos
  const severityChartConfig = {
    data: statistics.severity_distribution,
    angleField: 'count',
    colorField: 'severity',
    radius: 0.8,
    label: {
      type: 'outer',
      content: '{name}: {percentage}'
    },
    interactions: [{ type: 'element-active' }]
  };

  const sourceChartConfig = {
    data: statistics.top_sources,
    xField: 'source',
    yField: 'count',
    label: {
      position: 'middle',
      style: {
        fill: '#FFFFFF',
        opacity: 0.6
      }
    },
    meta: {
      source: { alias: 'Fonte' },
      count: { alias: 'Quantidade' }
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <Card>
            <Row gutter={16} align="middle">
              <Col flex="auto">
                <Title level={2} style={{ margin: 0 }}>
                  <BellOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                  Sistema de Alertas Inteligentes
                </Title>
                <Text type="secondary">
                  Monitoramento e otimização automática de alertas em tempo real
                </Text>
              </Col>
              <Col>
                <Space>
                  <Button 
                    icon={<ReloadOutlined />} 
                    onClick={handleRefresh}
                    loading={loading}
                  >
                    Atualizar
                  </Button>
                  <Button 
                    icon={<SettingOutlined />} 
                    onClick={() => setShowConfigModal(true)}
                  >
                    Configurações
                  </Button>
                </Space>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Estatísticas */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total de Alertas"
              value={statistics.total_alerts}
              prefix={<BellOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Alertas Ativos"
              value={statistics.active_alerts}
              valueStyle={{ color: '#ff4d4f' }}
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Redução de Alertas"
              value={statistics.reduction_percentage}
              suffix="%"
              valueStyle={{ color: '#52c41a' }}
              prefix={<OptimizeOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Tempo Médio de Resposta"
              value={statistics.average_response_time}
              suffix="min"
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* Gráficos */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={12}>
          <Card title="Distribuição por Severidade" extra={<BarChartOutlined />}>
            <Pie {...severityChartConfig} height={200} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Top Fontes de Alertas" extra={<BarChartOutlined />}>
            <Column {...sourceChartConfig} height={200} />
          </Card>
        </Col>
      </Row>

      {/* Filtros */}
      <Card style={{ marginBottom: '16px' }}>
        <Row gutter={16} align="middle">
          <Col span={3}>
            <Text strong>Filtros:</Text>
          </Col>
          <Col span={3}>
            <Select
              mode="multiple"
              placeholder="Severidade"
              style={{ width: '100%' }}
              value={filters.severity}
              onChange={(value) => setFilters(prev => ({ ...prev, severity: value }))}
            >
              <Option value="critical">Crítico</Option>
              <Option value="high">Alto</Option>
              <Option value="medium">Médio</Option>
              <Option value="low">Baixo</Option>
            </Select>
          </Col>
          <Col span={4}>
            <Select
              mode="multiple"
              placeholder="Fonte"
              style={{ width: '100%' }}
              value={filters.source}
              onChange={(value) => setFilters(prev => ({ ...prev, source: value }))}
            >
              <Option value="omni_keywords_finder_app">App Principal</Option>
              <Option value="database_service">Serviço DB</Option>
              <Option value="redis_cache">Cache Redis</Option>
              <Option value="firewall">Firewall</Option>
              <Option value="health_check_service">Health Check</Option>
            </Select>
          </Col>
          <Col span={3}>
            <Select
              mode="multiple"
              placeholder="Status"
              style={{ width: '100%' }}
              value={filters.status}
              onChange={(value) => setFilters(prev => ({ ...prev, status: value }))}
            >
              <Option value="active">Ativo</Option>
              <Option value="acknowledged">Reconhecido</Option>
              <Option value="resolved">Resolvido</Option>
              <Option value="suppressed">Suprimido</Option>
              <Option value="grouped">Agrupado</Option>
            </Select>
          </Col>
          <Col span={3}>
            <Select
              placeholder="Impacto"
              style={{ width: '100%' }}
              value={filters.user_impact}
              onChange={(value) => setFilters(prev => ({ ...prev, user_impact: value }))}
              allowClear
            >
              <Option value={true}>Com Impacto</Option>
              <Option value={false}>Sem Impacto</Option>
            </Select>
          </Col>
          <Col span={4}>
            <Button 
              icon={<FilterOutlined />}
              onClick={() => setFilters({
                severity: [],
                source: [],
                type: [],
                status: [],
                user_impact: null
              })}
            >
              Limpar Filtros
            </Button>
          </Col>
        </Row>
      </Card>

      {/* Tabela de Alertas */}
      <Card 
        title={
          <Space>
            <BellOutlined />
            Alertas ({filteredAlerts.length})
            {loading && <Spin size="small" />}
          </Space>
        }
        extra={
          <Space>
            {showOptimization && (
              <Badge count={statistics.suppressed_alerts} showZero>
                <Button icon={<EyeInvisibleOutlined />} size="small">
                  Suprimidos
                </Button>
              </Badge>
            )}
            {showGrouping && (
              <Badge count={statistics.grouped_alerts} showZero>
                <Button icon={<GroupOutlined />} size="small">
                  Agrupados
                </Button>
              </Badge>
            )}
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={filteredAlerts}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} de ${total} alertas`
          }}
          loading={loading}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* Grupos de Alertas */}
      {showGrouping && groups.length > 0 && (
        <Card 
          title={
            <Space>
              <GroupOutlined />
              Grupos de Alertas ({groups.length})
            </Space>
          }
          style={{ marginTop: '16px' }}
        >
          <Collapse>
            {groups.map(group => (
              <Panel
                key={group.id}
                header={
                  <Space>
                    <Text strong>Grupo {group.id}</Text>
                    <Tag color="blue">{group.strategy.replace(/_/g, ' ')}</Tag>
                    <Badge count={group.summary.total_alerts} />
                  </Space>
                }
              >
                <Row gutter={16}>
                  <Col span={6}>
                    <Statistic title="Total de Alertas" value={group.summary.total_alerts} />
                  </Col>
                  <Col span={6}>
                    <Statistic 
                      title="Maior Severidade" 
                      value={group.summary.highest_severity.toUpperCase()} 
                    />
                  </Col>
                  <Col span={6}>
                    <Statistic 
                      title="Prioridade Média" 
                      value={group.summary.average_priority.toFixed(2)} 
                    />
                  </Col>
                  <Col span={6}>
                    <Statistic 
                      title="Usuários Afetados" 
                      value={group.summary.affected_users_total} 
                    />
                  </Col>
                </Row>
              </Panel>
            ))}
          </Collapse>
        </Card>
      )}

      {/* Modal de Configurações */}
      <Modal
        title="Configurações de Otimização"
        open={showConfigModal}
        onCancel={() => setShowConfigModal(false)}
        footer={null}
        width={600}
      >
        <Form
          layout="vertical"
          initialValues={optimizationConfig}
          onFinish={handleUpdateOptimizationConfig}
        >
          <Form.Item label="Otimização Habilitada" name="enabled" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item label="Janela de Agrupamento (minutos)" name="grouping_window_minutes">
            <Input type="number" min={1} max={60} />
          </Form.Item>
          <Form.Item label="Threshold de Supressão" name="suppression_threshold">
            <Input type="number" min={0} max={1} step={0.1} />
          </Form.Item>
          <Form.Item label="Máximo de Alertas por Grupo" name="max_alerts_per_group">
            <Input type="number" min={1} max={50} />
          </Form.Item>
          <Form.Item label="Janela de Detecção de Padrões (minutos)" name="pattern_detection_window">
            <Input type="number" min={1} max={120} />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Salvar Configurações
              </Button>
              <Button onClick={() => setShowConfigModal(false)}>
                Cancelar
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Modal de Detalhes do Alerta */}
      <Modal
        title="Detalhes do Alerta"
        open={showAlertDetails}
        onCancel={() => setShowAlertDetails(false)}
        footer={null}
        width={800}
      >
        {selectedAlert && (
          <div>
            <Row gutter={16}>
              <Col span={12}>
                <Paragraph>
                  <Text strong>ID:</Text> {selectedAlert.id}
                </Paragraph>
                <Paragraph>
                  <Text strong>Tipo:</Text> {selectedAlert.type}
                </Paragraph>
                <Paragraph>
                  <Text strong>Fonte:</Text> {selectedAlert.source}
                </Paragraph>
                <Paragraph>
                  <Text strong>Severidade:</Text> 
                  <Tag color={
                    selectedAlert.severity === 'critical' ? '#ff4d4f' :
                    selectedAlert.severity === 'high' ? '#ff7875' :
                    selectedAlert.severity === 'medium' ? '#faad14' : '#52c41a'
                  }>
                    {selectedAlert.severity.toUpperCase()}
                  </Tag>
                </Paragraph>
              </Col>
              <Col span={12}>
                <Paragraph>
                  <Text strong>Status:</Text> {selectedAlert.status}
                </Paragraph>
                <Paragraph>
                  <Text strong>Impacto:</Text> {selectedAlert.user_impact ? 'Sim' : 'Não'}
                </Paragraph>
                <Paragraph>
                  <Text strong>Usuários Afetados:</Text> {selectedAlert.affected_users}
                </Paragraph>
                <Paragraph>
                  <Text strong>Duração:</Text> {selectedAlert.duration_minutes} minutos
                </Paragraph>
              </Col>
            </Row>
            <Divider />
            <Paragraph>
              <Text strong>Mensagem:</Text>
            </Paragraph>
            <Alert
              message={selectedAlert.message}
              type={
                selectedAlert.severity === 'critical' ? 'error' :
                selectedAlert.severity === 'high' ? 'warning' :
                selectedAlert.severity === 'medium' ? 'info' : 'success'
              }
              showIcon
            />
            <Divider />
            <Row gutter={16}>
              <Col span={12}>
                <Progress
                  percent={Math.round(selectedAlert.priority_score * 100)}
                  format={() => `Prioridade: ${selectedAlert.priority_score.toFixed(2)}`}
                  status={selectedAlert.priority_score > 0.8 ? 'exception' : 'active'}
                />
              </Col>
              <Col span={12}>
                <Progress
                  percent={Math.round(selectedAlert.impact_score * 100)}
                  format={() => `Impacto: ${selectedAlert.impact_score.toFixed(2)}`}
                  status={selectedAlert.impact_score > 0.8 ? 'exception' : 'active'}
                />
              </Col>
            </Row>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default IntelligentAlertsDashboard; 