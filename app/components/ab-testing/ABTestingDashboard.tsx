/**
 * Dashboard de A/B Testing - Omni Keywords Finder
 * 
 * Componente principal para visualização e gerenciamento de experimentos A/B
 * Inclui métricas gerais, lista de experimentos, gráficos e ações rápidas
 * 
 * @author Sistema Omni Keywords Finder
 * @version 1.0.0
 * @date 2024-12-19
 */

import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Button, Tag, Space, Modal, message } from 'antd';
import { 
  ExperimentOutlined, 
  UserOutlined, 
  TrophyOutlined, 
  BarChartOutlined,
  PlusOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
  EyeOutlined,
  EditOutlined
} from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useTranslation } from 'react-i18next';

// Tipos
interface Experiment {
  id: string;
  name: string;
  description: string;
  type: 'feature' | 'ui' | 'algorithm' | 'content';
  area: string;
  status: 'draft' | 'running' | 'paused' | 'completed' | 'stopped';
  traffic_percentage: number;
  duration_days: number;
  primary_metrics: string[];
  secondary_metrics: string[];
  hypothesis: string;
  significance_level: number;
  statistical_power: number;
  min_sample_size: number;
  created_by: string;
  owner: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  statistics?: {
    total_participants: number;
    unique_users: number;
  };
}

interface DashboardData {
  overview: {
    total_experiments: number;
    active_experiments: number;
    total_participants: number;
    total_conversions: number;
  };
  recent_experiments: Array<{
    id: string;
    name: string;
    status: string;
    created_at: string;
  }>;
  experiments_by_type: Array<{
    type: string;
    count: number;
  }>;
}

const ABTestingDashboard: React.FC = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedExperiment, setSelectedExperiment] = useState<Experiment | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalType, setModalType] = useState<'details' | 'create' | 'edit'>('details');

  // Cores para gráficos
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  useEffect(() => {
    fetchDashboardData();
    fetchExperiments();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/v1/ab-testing/dashboard');
      const data = await response.json();
      
      if (data.success) {
        setDashboardData(data.data);
      } else {
        message.error('Erro ao carregar dados do dashboard');
      }
    } catch (error) {
      console.error('Erro ao buscar dados do dashboard:', error);
      message.error('Erro de conexão');
    } finally {
      setLoading(false);
    }
  };

  const fetchExperiments = async () => {
    try {
      const response = await fetch('/api/v1/ab-testing/experiments?limit=100');
      const data = await response.json();
      
      if (data.success) {
        setExperiments(data.data);
      } else {
        message.error('Erro ao carregar experimentos');
      }
    } catch (error) {
      console.error('Erro ao buscar experimentos:', error);
      message.error('Erro de conexão');
    }
  };

  const handleExperimentAction = async (experimentId: string, action: 'start' | 'stop' | 'pause') => {
    try {
      const endpoint = action === 'start' ? 'start' : 'stop';
      const response = await fetch(`/api/v1/ab-testing/experiments/${experimentId}/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (data.success) {
        message.success(`Experimento ${action === 'start' ? 'iniciado' : 'parado'} com sucesso`);
        fetchExperiments(); // Recarregar lista
      } else {
        message.error(data.error || 'Erro ao executar ação');
      }
    } catch (error) {
      console.error(`Erro ao ${action} experimento:`, error);
      message.error('Erro de conexão');
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      draft: 'default',
      running: 'processing',
      paused: 'warning',
      completed: 'success',
      stopped: 'error'
    };
    return colors[status as keyof typeof colors] || 'default';
  };

  const getTypeColor = (type: string) => {
    const colors = {
      feature: 'blue',
      ui: 'green',
      algorithm: 'purple',
      content: 'orange'
    };
    return colors[type as keyof typeof colors] || 'default';
  };

  // Colunas da tabela
  const columns = [
    {
      title: t('Nome'),
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Experiment) => (
        <a onClick={() => {
          setSelectedExperiment(record);
          setModalType('details');
          setModalVisible(true);
        }}>
          {text}
        </a>
      ),
    },
    {
      title: t('Tipo'),
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => (
        <Tag color={getTypeColor(type)}>
          {t(type.toUpperCase())}
        </Tag>
      ),
    },
    {
      title: t('Status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {t(status.toUpperCase())}
        </Tag>
      ),
    },
    {
      title: t('Tráfego'),
      dataIndex: 'traffic_percentage',
      key: 'traffic_percentage',
      render: (value: number) => `${value}%`,
    },
    {
      title: t('Participantes'),
      dataIndex: 'statistics',
      key: 'participants',
      render: (stats: any) => stats?.total_participants || 0,
    },
    {
      title: t('Duração'),
      dataIndex: 'duration_days',
      key: 'duration_days',
      render: (days: number) => `${days} ${t('dias')}`,
    },
    {
      title: t('Ações'),
      key: 'actions',
      render: (_, record: Experiment) => (
        <Space size="small">
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => {
              setSelectedExperiment(record);
              setModalType('details');
              setModalVisible(true);
            }}
            title={t('Ver detalhes')}
          />
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => {
              setSelectedExperiment(record);
              setModalType('edit');
              setModalVisible(true);
            }}
            title={t('Editar')}
          />
          {record.status === 'draft' && (
            <Button
              type="text"
              icon={<PlayCircleOutlined />}
              onClick={() => handleExperimentAction(record.id, 'start')}
              title={t('Iniciar')}
            />
          )}
          {record.status === 'running' && (
            <>
              <Button
                type="text"
                icon={<PauseCircleOutlined />}
                onClick={() => handleExperimentAction(record.id, 'pause')}
                title={t('Pausar')}
              />
              <Button
                type="text"
                icon={<StopOutlined />}
                onClick={() => handleExperimentAction(record.id, 'stop')}
                title={t('Parar')}
              />
            </>
          )}
        </Space>
      ),
    },
  ];

  if (loading) {
    return <div>Carregando...</div>;
  }

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '28px', marginBottom: '8px' }}>
          <ExperimentOutlined style={{ marginRight: '12px' }} />
          {t('Dashboard de A/B Testing')}
        </h1>
        <p style={{ color: '#666', fontSize: '16px' }}>
          {t('Gerencie e monitore seus experimentos A/B')}
        </p>
      </div>

      {/* Métricas Gerais */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('Total de Experimentos')}
              value={dashboardData?.overview.total_experiments || 0}
              prefix={<ExperimentOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('Experimentos Ativos')}
              value={dashboardData?.overview.active_experiments || 0}
              prefix={<PlayCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('Total de Participantes')}
              value={dashboardData?.overview.total_participants || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title={t('Total de Conversões')}
              value={dashboardData?.overview.total_conversions || 0}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Gráficos */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={12}>
          <Card title={t('Experimentos por Tipo')} extra={<BarChartOutlined />}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={dashboardData?.experiments_by_type || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ type, percent }) => `${type} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {(dashboardData?.experiments_by_type || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title={t('Participantes por Dia')} extra={<BarChartOutlined />}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart
                data={[
                  { day: 'Seg', participants: 120 },
                  { day: 'Ter', participants: 150 },
                  { day: 'Qua', participants: 180 },
                  { day: 'Qui', participants: 200 },
                  { day: 'Sex', participants: 220 },
                  { day: 'Sab', participants: 190 },
                  { day: 'Dom', participants: 160 },
                ]}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="participants" stroke="#8884d8" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Lista de Experimentos */}
      <Card
        title={t('Experimentos')}
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setSelectedExperiment(null);
              setModalType('create');
              setModalVisible(true);
            }}
          >
            {t('Novo Experimento')}
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={experiments}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `${t('Mostrando')} ${range[0]}-${range[1]} ${t('de')} ${total} ${t('experimentos')}`,
          }}
        />
      </Card>

      {/* Modal para detalhes/criação/edição */}
      <Modal
        title={
          modalType === 'create' ? t('Novo Experimento') :
          modalType === 'edit' ? t('Editar Experimento') :
          t('Detalhes do Experimento')
        }
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedExperiment && modalType === 'details' && (
          <div>
            <h3>{selectedExperiment.name}</h3>
            <p>{selectedExperiment.description}</p>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <strong>{t('Tipo')}:</strong> {t(selectedExperiment.type.toUpperCase())}
              </Col>
              <Col span={12}>
                <strong>{t('Status')}:</strong> {t(selectedExperiment.status.toUpperCase())}
              </Col>
              <Col span={12}>
                <strong>{t('Área')}:</strong> {selectedExperiment.area}
              </Col>
              <Col span={12}>
                <strong>{t('Tráfego')}:</strong> {selectedExperiment.traffic_percentage}%
              </Col>
              <Col span={12}>
                <strong>{t('Duração')}:</strong> {selectedExperiment.duration_days} {t('dias')}
              </Col>
              <Col span={12}>
                <strong>{t('Participantes')}:</strong> {selectedExperiment.statistics?.total_participants || 0}
              </Col>
            </Row>
            <div style={{ marginTop: '16px' }}>
              <strong>{t('Hipótese')}:</strong>
              <p>{selectedExperiment.hypothesis}</p>
            </div>
            <div style={{ marginTop: '16px' }}>
              <strong>{t('Métricas Primárias')}:</strong>
              <div>
                {selectedExperiment.primary_metrics.map((metric, index) => (
                  <Tag key={index} color="blue">{metric}</Tag>
                ))}
              </div>
            </div>
          </div>
        )}
        {modalType === 'create' && (
          <div>
            <p>{t('Formulário de criação de experimento será implementado aqui')}</p>
          </div>
        )}
        {modalType === 'edit' && (
          <div>
            <p>{t('Formulário de edição de experimento será implementado aqui')}</p>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ABTestingDashboard; 