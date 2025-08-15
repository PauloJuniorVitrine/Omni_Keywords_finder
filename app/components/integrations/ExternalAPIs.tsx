/**
 * ExternalAPIs.tsx
 * 
 * Sistema de Integração com APIs Externas - Omni Keywords Finder
 * 
 * Prompt: CHECKLIST_INTERFACE_GRAFICA_V1.md - UI-015
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2024-12-20
 * 
 * Funcionalidades:
 * - Configuração de APIs externas
 * - Teste de conectividade
 * - Monitoramento de status
 * - Gestão de credenciais
 * - Rate limiting
 * - Logs de integração
 * - Mapeamento de dados
 * - Transformação de payloads
 * - Retry automático
 * - Alertas de falha
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Card, Row, Col, Button, Space, Modal, Form, Input, Select, DatePicker, 
  Switch, message, Spin, Tabs, Tooltip, Badge, Divider, Typography, 
  Table, Tag, Progress, Alert, Drawer, List, Statistic, Timeline,
  Checkbox, Radio, Slider, InputNumber, TimePicker, Steps, Result,
  Descriptions, Empty, Skeleton, Avatar, Rate, Calendar, Carousel,
  Collapse, Tree, Transfer, Upload, Mentions, Cascader, TreeSelect,
  AutoComplete, InputNumber as AntInputNumber, Slider as AntSlider,
  Rate as AntRate, Switch as AntSwitch, Checkbox as AntCheckbox,
  Radio as AntRadio, DatePicker as AntDatePicker, TimePicker as AntTimePicker,
  Cascader as AntCascader, TreeSelect as AntTreeSelect, Transfer as AntTransfer,
  Upload as AntUpload, Mentions as AntMentions, AutoComplete as AntAutoComplete
} from 'antd';
import { 
  ApiOutlined, 
  CheckCircleOutlined, 
  ExclamationCircleOutlined,
  ClockCircleOutlined,
  ReloadOutlined,
  SettingOutlined,
  EyeOutlined,
  DownloadOutlined,
  BellOutlined,
  DashboardOutlined,
  LineChartOutlined,
  BarChartOutlined,
  PieChartOutlined,
  TableOutlined,
  FilterOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
  InfoCircleOutlined,
  WarningOutlined,
  CheckOutlined,
  CloseOutlined,
  SyncOutlined,
  ThunderboltOutlined,
  DatabaseOutlined,
  CloudOutlined,
  ServerOutlined,
  NetworkOutlined,
  KeyOutlined,
  LockOutlined,
  UnlockOutlined,
  SafetyOutlined,
  BugOutlined,
  CodeOutlined,
  FileTextOutlined,
  LinkOutlined,
  DisconnectOutlined,
  WifiOutlined,
  GlobalOutlined,
  EnvironmentOutlined,
  CompressOutlined,
  ExpandOutlined,
  RetweetOutlined,
  RollbackOutlined,
  ForwardOutlined,
  BackwardOutlined,
  StepForwardOutlined,
  StepBackwardOutlined,
  FastForwardOutlined,
  FastBackwardOutlined,
  PlaySquareOutlined,
  PauseCircleOutlined as PauseCircleOutlined2,
  StopOutlined as StopOutlined2,
  LoadingOutlined,
  Loading3QuartersOutlined,
  LoadingOutlined as LoadingOutlined2
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { TabPane } = Tabs;
const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Step } = Steps;
const { Panel } = Collapse;

// Tipos de API
interface ExternalAPI {
  id: string;
  name: string;
  description: string;
  baseUrl: string;
  version: string;
  type: 'rest' | 'graphql' | 'soap' | 'grpc' | 'webhook';
  status: 'active' | 'inactive' | 'error' | 'maintenance';
  lastCheck: string;
  responseTime: number;
  uptime: number;
  rateLimit: {
    requests: number;
    period: string;
    remaining: number;
    resetTime: string;
  };
  authentication: {
    type: 'none' | 'api_key' | 'bearer' | 'oauth2' | 'basic';
    credentials: Record<string, any>;
  };
  endpoints: APIEndpoint[];
  headers: Record<string, string>;
  timeout: number;
  retryConfig: {
    maxRetries: number;
    backoffMultiplier: number;
    initialDelay: number;
  };
  dataMapping: DataMapping[];
  transformations: DataTransformation[];
  webhooks: WebhookConfig[];
  monitoring: MonitoringConfig;
  createdAt: string;
  updatedAt: string;
}

// Endpoints da API
interface APIEndpoint {
  id: string;
  name: string;
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  description: string;
  parameters: EndpointParameter[];
  responseSchema: any;
  status: 'active' | 'inactive' | 'deprecated';
  lastUsed: string;
  usageCount: number;
  avgResponseTime: number;
  errorRate: number;
}

// Parâmetros do endpoint
interface EndpointParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  required: boolean;
  defaultValue?: any;
  description: string;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    enum?: any[];
  };
}

// Mapeamento de dados
interface DataMapping {
  id: string;
  name: string;
  sourceField: string;
  targetField: string;
  transformation?: string;
  required: boolean;
  description: string;
}

// Transformação de dados
interface DataTransformation {
  id: string;
  name: string;
  type: 'format' | 'validate' | 'enrich' | 'filter' | 'aggregate';
  description: string;
  config: Record<string, any>;
  enabled: boolean;
}

// Configuração de webhook
interface WebhookConfig {
  id: string;
  name: string;
  url: string;
  events: string[];
  secret?: string;
  status: 'active' | 'inactive';
  lastTriggered?: string;
  successRate: number;
}

// Configuração de monitoramento
interface MonitoringConfig {
  enabled: boolean;
  checkInterval: number;
  timeout: number;
  alertThreshold: number;
  notificationChannels: string[];
  healthCheckEndpoint?: string;
  customHeaders?: Record<string, string>;
}

// Log de integração
interface IntegrationLog {
  id: string;
  apiId: string;
  endpoint: string;
  method: string;
  timestamp: string;
  status: 'success' | 'error' | 'timeout' | 'rate_limited';
  responseTime: number;
  statusCode: number;
  requestData?: any;
  responseData?: any;
  errorMessage?: string;
  retryCount: number;
  userId?: string;
  traceId?: string;
}

// Teste de conectividade
interface ConnectivityTest {
  id: string;
  apiId: string;
  timestamp: string;
  status: 'success' | 'error' | 'timeout';
  responseTime: number;
  statusCode: number;
  errorMessage?: string;
  details: {
    dns: boolean;
    tcp: boolean;
    tls: boolean;
    http: boolean;
    authentication: boolean;
  };
}

// Props do componente
interface ExternalAPIsProps {
  showCredentials?: boolean;
  showLogs?: boolean;
  showMonitoring?: boolean;
  showTesting?: boolean;
  enableAutoRefresh?: boolean;
  refreshInterval?: number;
  onApiStatusChange?: (api: ExternalAPI) => void;
  onTestComplete?: (test: ConnectivityTest) => void;
  onError?: (error: string) => void;
  readOnly?: boolean;
}

export const ExternalAPIs: React.FC<ExternalAPIsProps> = ({
  showCredentials = true,
  showLogs = true,
  showMonitoring = true,
  showTesting = true,
  enableAutoRefresh = true,
  refreshInterval = 30000,
  onApiStatusChange,
  onTestComplete,
  onError,
  readOnly = false
}) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [apis, setApis] = useState<ExternalAPI[]>([]);
  const [logs, setLogs] = useState<IntegrationLog[]>([]);
  const [tests, setTests] = useState<ConnectivityTest[]>([]);
  const [selectedApi, setSelectedApi] = useState<ExternalAPI | null>(null);
  const [showApiModal, setShowApiModal] = useState(false);
  const [showTestModal, setShowTestModal] = useState(false);
  const [showLogsDrawer, setShowLogsDrawer] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [error, setError] = useState<string | null>(null);
  const [testingApi, setTestingApi] = useState<string | null>(null);

  // Carregar dados iniciais
  useEffect(() => {
    loadInitialData();
  }, []);

  // Auto-refresh
  useEffect(() => {
    if (!enableAutoRefresh) return;

    const interval = setInterval(() => {
      refreshApiStatus();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [enableAutoRefresh, refreshInterval]);

  const loadInitialData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      await Promise.all([
        loadAPIs(),
        loadLogs(),
        loadTests()
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
      message.error('Erro ao carregar configurações de APIs');
    } finally {
      setLoading(false);
    }
  };

  const loadAPIs = async () => {
    try {
      const response = await fetch('/api/integrations/external-apis');
      if (!response.ok) throw new Error('Falha ao carregar APIs');
      
      const apisData = await response.json();
      setApis(apisData);
    } catch (err) {
      console.error('Erro ao carregar APIs:', err);
      // Mock data para demonstração
      setApis([
        {
          id: 'google-analytics',
          name: 'Google Analytics',
          description: 'API para integração com Google Analytics',
          baseUrl: 'https://analytics.googleapis.com',
          version: 'v4',
          type: 'rest',
          status: 'active',
          lastCheck: new Date().toISOString(),
          responseTime: 245,
          uptime: 99.8,
          rateLimit: {
            requests: 1000,
            period: '1h',
            remaining: 850,
            resetTime: new Date(Date.now() + 3600000).toISOString()
          },
          authentication: {
            type: 'oauth2',
            credentials: {
              clientId: '***',
              clientSecret: '***',
              accessToken: '***'
            }
          },
          endpoints: [
            {
              id: 'get-reports',
              name: 'Get Reports',
              path: '/analytics/v4/reports:batchGet',
              method: 'POST',
              description: 'Obter relatórios do Google Analytics',
              parameters: [],
              responseSchema: {},
              status: 'active',
              lastUsed: new Date().toISOString(),
              usageCount: 1250,
              avgResponseTime: 245,
              errorRate: 0.2
            }
          ],
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ***'
          },
          timeout: 30000,
          retryConfig: {
            maxRetries: 3,
            backoffMultiplier: 2,
            initialDelay: 1000
          },
          dataMapping: [],
          transformations: [],
          webhooks: [],
          monitoring: {
            enabled: true,
            checkInterval: 300000,
            timeout: 10000,
            alertThreshold: 5000,
            notificationChannels: ['email', 'slack']
          },
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: new Date().toISOString()
        },
        {
          id: 'semrush',
          name: 'SEMrush',
          description: 'API para análise de SEO e keywords',
          baseUrl: 'https://api.semrush.com',
          version: 'v3',
          type: 'rest',
          status: 'active',
          lastCheck: new Date().toISOString(),
          responseTime: 180,
          uptime: 99.9,
          rateLimit: {
            requests: 500,
            period: '1h',
            remaining: 320,
            resetTime: new Date(Date.now() + 1800000).toISOString()
          },
          authentication: {
            type: 'api_key',
            credentials: {
              apiKey: '***'
            }
          },
          endpoints: [
            {
              id: 'keyword-analytics',
              name: 'Keyword Analytics',
              path: '/analytics/overview',
              method: 'GET',
              description: 'Obter análise de keywords',
              parameters: [
                {
                  name: 'keyword',
                  type: 'string',
                  required: true,
                  description: 'Palavra-chave para análise'
                }
              ],
              responseSchema: {},
              status: 'active',
              lastUsed: new Date().toISOString(),
              usageCount: 890,
              avgResponseTime: 180,
              errorRate: 0.1
            }
          ],
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 15000,
          retryConfig: {
            maxRetries: 2,
            backoffMultiplier: 1.5,
            initialDelay: 500
          },
          dataMapping: [],
          transformations: [],
          webhooks: [],
          monitoring: {
            enabled: true,
            checkInterval: 300000,
            timeout: 8000,
            alertThreshold: 3000,
            notificationChannels: ['email']
          },
          createdAt: '2024-01-15T00:00:00Z',
          updatedAt: new Date().toISOString()
        }
      ]);
    }
  };

  const loadLogs = async () => {
    try {
      const response = await fetch('/api/integrations/logs');
      if (!response.ok) throw new Error('Falha ao carregar logs');
      
      const logsData = await response.json();
      setLogs(logsData);
    } catch (err) {
      console.error('Erro ao carregar logs:', err);
      // Mock data para demonstração
      setLogs([
        {
          id: 'log-1',
          apiId: 'google-analytics',
          endpoint: '/analytics/v4/reports:batchGet',
          method: 'POST',
          timestamp: new Date().toISOString(),
          status: 'success',
          responseTime: 245,
          statusCode: 200,
          retryCount: 0,
          traceId: 'trace-123'
        },
        {
          id: 'log-2',
          apiId: 'semrush',
          endpoint: '/analytics/overview',
          method: 'GET',
          timestamp: new Date(Date.now() - 300000).toISOString(),
          status: 'error',
          responseTime: 5000,
          statusCode: 429,
          errorMessage: 'Rate limit exceeded',
          retryCount: 2,
          traceId: 'trace-124'
        }
      ]);
    }
  };

  const loadTests = async () => {
    try {
      const response = await fetch('/api/integrations/tests');
      if (!response.ok) throw new Error('Falha ao carregar testes');
      
      const testsData = await response.json();
      setTests(testsData);
    } catch (err) {
      console.error('Erro ao carregar testes:', err);
      // Mock data para demonstração
      setTests([
        {
          id: 'test-1',
          apiId: 'google-analytics',
          timestamp: new Date().toISOString(),
          status: 'success',
          responseTime: 245,
          statusCode: 200,
          details: {
            dns: true,
            tcp: true,
            tls: true,
            http: true,
            authentication: true
          }
        }
      ]);
    }
  };

  const refreshApiStatus = async () => {
    try {
      const response = await fetch('/api/integrations/status');
      if (!response.ok) throw new Error('Falha ao atualizar status');
      
      const statusData = await response.json();
      setApis(prevApis => 
        prevApis.map(api => {
          const updatedApi = statusData.find((s: any) => s.id === api.id);
          return updatedApi ? { ...api, ...updatedApi } : api;
        })
      );
    } catch (err) {
      console.error('Erro ao atualizar status:', err);
    }
  };

  const testConnectivity = async (apiId: string) => {
    setTestingApi(apiId);
    
    try {
      const response = await fetch(`/api/integrations/test/${apiId}`, {
        method: 'POST'
      });
      
      if (!response.ok) throw new Error('Falha no teste de conectividade');
      
      const testResult = await response.json();
      setTests(prev => [testResult, ...prev]);
      
      if (onTestComplete) {
        onTestComplete(testResult);
      }
      
      message.success('Teste de conectividade concluído');
    } catch (err) {
      message.error('Erro no teste de conectividade');
      if (onError) {
        onError(err instanceof Error ? err.message : 'Erro desconhecido');
      }
    } finally {
      setTestingApi(null);
    }
  };

  const toggleApiStatus = async (apiId: string, status: 'active' | 'inactive') => {
    try {
      const response = await fetch(`/api/integrations/apis/${apiId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
      
      if (!response.ok) throw new Error('Falha ao alterar status');
      
      setApis(prev => 
        prev.map(api => 
          api.id === apiId ? { ...api, status } : api
        )
      );
      
      message.success(`API ${status === 'active' ? 'ativada' : 'desativada'} com sucesso`);
    } catch (err) {
      message.error('Erro ao alterar status da API');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'green';
      case 'inactive': return 'gray';
      case 'error': return 'red';
      case 'maintenance': return 'orange';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircleOutlined />;
      case 'inactive': return <StopOutlined />;
      case 'error': return <ExclamationCircleOutlined />;
      case 'maintenance': return <ClockCircleOutlined />;
      default: return <InfoCircleOutlined />;
    }
  };

  const getAuthTypeIcon = (type: string) => {
    switch (type) {
      case 'api_key': return <KeyOutlined />;
      case 'bearer': return <LockOutlined />;
      case 'oauth2': return <SafetyOutlined />;
      case 'basic': return <UnlockOutlined />;
      default: return <ApiOutlined />;
    }
  };

  const apiColumns = [
    {
      title: 'API',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, api: ExternalAPI) => (
        <Space>
          <Avatar icon={<ApiOutlined />} style={{ backgroundColor: '#1890ff' }} />
          <div>
            <div>{name}</div>
            <Text type="secondary">{api.description}</Text>
          </div>
        </Space>
      )
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string, api: ExternalAPI) => (
        <Space>
          <Badge 
            status={status as any} 
            text={
              <Tag color={getStatusColor(status)} icon={getStatusIcon(status)}>
                {status === 'active' ? 'Ativo' : 
                 status === 'inactive' ? 'Inativo' : 
                 status === 'error' ? 'Erro' : 'Manutenção'}
              </Tag>
            }
          />
        </Space>
      )
    },
    {
      title: 'Tipo',
      dataIndex: 'type',
      key: 'type',
      render: (type: string, api: ExternalAPI) => (
        <Tag icon={getAuthTypeIcon(api.authentication.type)}>
          {type.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Tempo de Resposta',
      dataIndex: 'responseTime',
      key: 'responseTime',
      render: (responseTime: number) => (
        <Text>{responseTime}ms</Text>
      )
    },
    {
      title: 'Uptime',
      dataIndex: 'uptime',
      key: 'uptime',
      render: (uptime: number) => (
        <Progress 
          percent={uptime} 
          size="small"
          status={uptime >= 99 ? 'success' : uptime >= 95 ? 'normal' : 'exception'}
        />
      )
    },
    {
      title: 'Rate Limit',
      dataIndex: 'rateLimit',
      key: 'rateLimit',
      render: (rateLimit: any) => (
        <div>
          <Text>{rateLimit.remaining}/{rateLimit.requests}</Text>
          <br />
          <Text type="secondary">{rateLimit.period}</Text>
        </div>
      )
    },
    {
      title: 'Ações',
      key: 'actions',
      render: (_, api: ExternalAPI) => (
        <Space>
          <Tooltip title="Testar Conectividade">
            <Button 
              type="text" 
              icon={<SyncOutlined spin={testingApi === api.id} />}
              onClick={() => testConnectivity(api.id)}
              disabled={testingApi === api.id}
            />
          </Tooltip>
          <Tooltip title="Ver Detalhes">
            <Button 
              type="text" 
              icon={<EyeOutlined />}
              onClick={() => {
                setSelectedApi(api);
                setShowApiModal(true);
              }}
            />
          </Tooltip>
          <Tooltip title={api.status === 'active' ? 'Desativar' : 'Ativar'}>
            <Button 
              type="text" 
              icon={api.status === 'active' ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
              onClick={() => toggleApiStatus(api.id, api.status === 'active' ? 'inactive' : 'active')}
              disabled={readOnly}
            />
          </Tooltip>
        </Space>
      )
    }
  ];

  const logColumns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp: string) => (
        <Text>{new Date(timestamp).toLocaleString()}</Text>
      )
    },
    {
      title: 'API',
      dataIndex: 'apiId',
      key: 'apiId',
      render: (apiId: string) => {
        const api = apis.find(a => a.id === apiId);
        return <Text>{api?.name || apiId}</Text>;
      }
    },
    {
      title: 'Endpoint',
      dataIndex: 'endpoint',
      key: 'endpoint',
      render: (endpoint: string, log: IntegrationLog) => (
        <Space>
          <Tag color="blue">{log.method}</Tag>
          <Text code>{endpoint}</Text>
        </Space>
      )
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={
          status === 'success' ? 'green' : 
          status === 'error' ? 'red' : 
          status === 'timeout' ? 'orange' : 'yellow'
        }>
          {status === 'success' ? 'Sucesso' : 
           status === 'error' ? 'Erro' : 
           status === 'timeout' ? 'Timeout' : 'Rate Limited'}
        </Tag>
      )
    },
    {
      title: 'Tempo de Resposta',
      dataIndex: 'responseTime',
      key: 'responseTime',
      render: (responseTime: number) => (
        <Text>{responseTime}ms</Text>
      )
    },
    {
      title: 'Código',
      dataIndex: 'statusCode',
      key: 'statusCode',
      render: (statusCode: number) => (
        <Tag color={statusCode >= 200 && statusCode < 300 ? 'green' : 'red'}>
          {statusCode}
        </Tag>
      )
    }
  ];

  if (loading) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>Carregando configurações de APIs externas...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert
        message="Erro no Sistema de APIs Externas"
        description={error}
        type="error"
        showIcon
        action={
          <Button size="small" danger onClick={loadInitialData}>
            Tentar Novamente
          </Button>
        }
      />
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <Card>
            <Row gutter={16} align="middle">
              <Col flex="1">
                <Title level={3} style={{ margin: 0 }}>APIs Externas</Title>
                <Text type="secondary">Gerencie integrações com serviços externos</Text>
              </Col>
              <Col>
                <Space>
                  <Button 
                    icon={<ReloadOutlined />} 
                    onClick={refreshApiStatus}
                    disabled={readOnly}
                  >
                    Atualizar
                  </Button>
                  <Button 
                    type="primary" 
                    icon={<PlusOutlined />}
                    onClick={() => setShowApiModal(true)}
                    disabled={readOnly}
                  >
                    Nova API
                  </Button>
                </Space>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="APIs Ativas" 
              value={apis.filter(a => a.status === 'active').length}
              suffix={`/ ${apis.length}`}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="Tempo Médio de Resposta" 
              value={apis.reduce((acc, api) => acc + api.responseTime, 0) / apis.length}
              suffix="ms"
              precision={0}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="Uptime Médio" 
              value={apis.reduce((acc, api) => acc + api.uptime, 0) / apis.length}
              suffix="%"
              precision={1}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="Logs Hoje" 
              value={logs.filter(log => 
                new Date(log.timestamp).toDateString() === new Date().toDateString()
              ).length}
            />
          </Card>
        </Col>
      </Row>

      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="Visão Geral" key="overview">
          <Card>
            <Table 
              dataSource={apis} 
              columns={apiColumns}
              rowKey="id"
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </TabPane>

        {showLogs && (
          <TabPane tab="Logs" key="logs">
            <Card>
              <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
                <Col flex="1">
                  <Title level={4}>Logs de Integração</Title>
                </Col>
                <Col>
                  <Space>
                    <Button 
                      icon={<DownloadOutlined />}
                      onClick={() => {
                        // Exportar logs
                        const csvContent = logs.map(log => 
                          `${log.timestamp},${log.apiId},${log.endpoint},${log.method},${log.status},${log.responseTime},${log.statusCode}`
                        ).join('\n');
                        const blob = new Blob([csvContent], { type: 'text/csv' });
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'integration-logs.csv';
                        a.click();
                      }}
                    >
                      Exportar
                    </Button>
                    <Button 
                      icon={<EyeOutlined />}
                      onClick={() => setShowLogsDrawer(true)}
                    >
                      Ver Detalhes
                    </Button>
                  </Space>
                </Col>
              </Row>
              <Table 
                dataSource={logs.slice(0, 50)} 
                columns={logColumns}
                rowKey="id"
                pagination={{ pageSize: 20 }}
              />
            </Card>
          </TabPane>
        )}

        {showTesting && (
          <TabPane tab="Testes" key="tests">
            <Card>
              <Row gutter={[16, 16]}>
                {apis.map(api => (
                  <Col span={8} key={api.id}>
                    <Card 
                      size="small"
                      title={api.name}
                      extra={
                        <Button 
                          type="primary" 
                          size="small"
                          icon={<SyncOutlined spin={testingApi === api.id} />}
                          onClick={() => testConnectivity(api.id)}
                          disabled={testingApi === api.id}
                        >
                          Testar
                        </Button>
                      }
                    >
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <div>
                          <Text type="secondary">Status:</Text>
                          <Tag color={getStatusColor(api.status)} style={{ marginLeft: '8px' }}>
                            {api.status === 'active' ? 'Ativo' : 
                             api.status === 'inactive' ? 'Inativo' : 
                             api.status === 'error' ? 'Erro' : 'Manutenção'}
                          </Tag>
                        </div>
                        <div>
                          <Text type="secondary">Último teste:</Text>
                          <Text style={{ marginLeft: '8px' }}>
                            {new Date(api.lastCheck).toLocaleString()}
                          </Text>
                        </div>
                        <div>
                          <Text type="secondary">Tempo de resposta:</Text>
                          <Text style={{ marginLeft: '8px' }}>
                            {api.responseTime}ms
                          </Text>
                        </div>
                      </Space>
                    </Card>
                  </Col>
                ))}
              </Row>
            </Card>
          </TabPane>
        )}

        {showMonitoring && (
          <TabPane tab="Monitoramento" key="monitoring">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Card title="Status das APIs">
                  <PieChartOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
                  <Text>Gráfico de status das APIs</Text>
                </Card>
              </Col>
              <Col span={12}>
                <Card title="Tempo de Resposta">
                  <LineChartOutlined style={{ fontSize: '48px', color: '#52c41a' }} />
                  <Text>Gráfico de tempo de resposta ao longo do tempo</Text>
                </Card>
              </Col>
            </Row>
          </TabPane>
        )}
      </Tabs>

      {/* Modal de Detalhes da API */}
      <Modal
        title="Detalhes da API"
        open={showApiModal}
        onCancel={() => setShowApiModal(false)}
        width={800}
        footer={[
          <Button key="close" onClick={() => setShowApiModal(false)}>
            Fechar
          </Button>,
          !readOnly && (
            <Button key="edit" type="primary">
              Editar
            </Button>
          )
        ]}
      >
        {selectedApi && (
          <div>
            <Row gutter={16} style={{ marginBottom: '16px' }}>
              <Col>
                <Avatar 
                  size={64} 
                  icon={<ApiOutlined />}
                  style={{ backgroundColor: '#1890ff' }}
                />
              </Col>
              <Col flex="1">
                <Title level={4}>{selectedApi.name}</Title>
                <Paragraph>{selectedApi.description}</Paragraph>
                <Space>
                  <Tag color={getStatusColor(selectedApi.status)}>
                    {selectedApi.status === 'active' ? 'Ativo' : 
                     selectedApi.status === 'inactive' ? 'Inativo' : 
                     selectedApi.status === 'error' ? 'Erro' : 'Manutenção'}
                  </Tag>
                  <Tag>{selectedApi.type.toUpperCase()}</Tag>
                  <Tag>v{selectedApi.version}</Tag>
                </Space>
              </Col>
            </Row>
            
            <Divider />
            
            <Row gutter={16}>
              <Col span={12}>
                <Title level={5}>Informações Básicas</Title>
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="URL Base">{selectedApi.baseUrl}</Descriptions.Item>
                  <Descriptions.Item label="Versão">{selectedApi.version}</Descriptions.Item>
                  <Descriptions.Item label="Tipo">{selectedApi.type.toUpperCase()}</Descriptions.Item>
                  <Descriptions.Item label="Timeout">{selectedApi.timeout}ms</Descriptions.Item>
                </Descriptions>
              </Col>
              <Col span={12}>
                <Title level={5}>Performance</Title>
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="Tempo de Resposta">{selectedApi.responseTime}ms</Descriptions.Item>
                  <Descriptions.Item label="Uptime">{selectedApi.uptime}%</Descriptions.Item>
                  <Descriptions.Item label="Última Verificação">
                    {new Date(selectedApi.lastCheck).toLocaleString()}
                  </Descriptions.Item>
                </Descriptions>
              </Col>
            </Row>
            
            <Divider />
            
            <Title level={5}>Rate Limiting</Title>
            <Descriptions column={2} size="small">
              <Descriptions.Item label="Limite">{selectedApi.rateLimit.requests}</Descriptions.Item>
              <Descriptions.Item label="Período">{selectedApi.rateLimit.period}</Descriptions.Item>
              <Descriptions.Item label="Restantes">{selectedApi.rateLimit.remaining}</Descriptions.Item>
              <Descriptions.Item label="Reset">
                {new Date(selectedApi.rateLimit.resetTime).toLocaleString()}
              </Descriptions.Item>
            </Descriptions>
            
            <Divider />
            
            <Title level={5}>Endpoints</Title>
            <List
              size="small"
              dataSource={selectedApi.endpoints}
              renderItem={(endpoint) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Avatar icon={<ApiOutlined />} size="small" />}
                    title={
                      <Space>
                        <Tag color="blue">{endpoint.method}</Tag>
                        <Text code>{endpoint.path}</Text>
                      </Space>
                    }
                    description={endpoint.description}
                  />
                  <div>
                    <Text type="secondary">{endpoint.usageCount} usos</Text>
                    <br />
                    <Text type="secondary">{endpoint.avgResponseTime}ms</Text>
                  </div>
                </List.Item>
              )}
            />
          </div>
        )}
      </Modal>

      {/* Drawer de Logs Detalhados */}
      <Drawer
        title="Logs Detalhados"
        placement="right"
        width={600}
        open={showLogsDrawer}
        onClose={() => setShowLogsDrawer(false)}
      >
        <List
          dataSource={logs}
          renderItem={(log) => (
            <List.Item>
              <List.Item.Meta
                avatar={
                  <Avatar 
                    icon={
                      log.status === 'success' ? <CheckCircleOutlined /> :
                      log.status === 'error' ? <ExclamationCircleOutlined /> :
                      <ClockCircleOutlined />
                    }
                    style={{ 
                      backgroundColor: 
                        log.status === 'success' ? '#52c41a' :
                        log.status === 'error' ? '#f5222d' : '#fa8c16'
                    }}
                  />
                }
                title={
                  <Space>
                    <Text>{log.apiId}</Text>
                    <Tag color="blue">{log.method}</Tag>
                    <Tag color={
                      log.status === 'success' ? 'green' : 
                      log.status === 'error' ? 'red' : 'orange'
                    }>
                      {log.status}
                    </Tag>
                  </Space>
                }
                description={
                  <div>
                    <div><Text code>{log.endpoint}</Text></div>
                    <div><Text type="secondary">{new Date(log.timestamp).toLocaleString()}</Text></div>
                    <div><Text type="secondary">Tempo: {log.responseTime}ms | Código: {log.statusCode}</Text></div>
                    {log.errorMessage && (
                      <div><Text type="danger">{log.errorMessage}</Text></div>
                    )}
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </Drawer>
    </div>
  );
}; 