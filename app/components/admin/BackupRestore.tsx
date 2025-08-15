/**
 * BackupRestore.tsx
 * 
 * Sistema de Backup e Restauração - Omni Keywords Finder
 * 
 * Prompt: CHECKLIST_INTERFACE_GRAFICA_V1.md - UI-011
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2024-12-20
 * 
 * Funcionalidades:
 * - Backup manual e automático
 * - Restauração de dados
 * - Histórico de backups
 * - Configuração de agendamento
 * - Compressão e criptografia
 * - Backup incremental
 * - Validação de integridade
 * - Backup em nuvem
 * - Notificações de backup
 * - Limpeza automática
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Card, Row, Col, Button, Space, Modal, Form, Input, Select, DatePicker, 
  Switch, message, Spin, Tabs, Tooltip, Badge, Divider, Typography, 
  Table, Tag, Progress, Alert, Drawer, List, Upload, Statistic, Timeline,
  Checkbox, Radio, Slider, InputNumber, TimePicker, Steps, Result
} from 'antd';
import { 
  CloudUploadOutlined, 
  CloudDownloadOutlined, 
  HistoryOutlined,
  SettingOutlined,
  DeleteOutlined,
  DownloadOutlined,
  UploadOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
  SafetyOutlined,
  DatabaseOutlined,
  FileZipOutlined,
  LockOutlined,
  UnlockOutlined,
  SyncOutlined,
  ReloadOutlined,
  EyeOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
  InfoCircleOutlined,
  WarningOutlined,
  CheckOutlined,
  CloseOutlined
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { TabPane } = Tabs;
const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Step } = Steps;

// Tipos de backup
interface BackupType {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  size: number;
  duration: number;
  compression: boolean;
  encryption: boolean;
}

// Configuração de backup
interface BackupConfig {
  id: string;
  name: string;
  type: 'full' | 'incremental' | 'differential';
  schedule: {
    enabled: boolean;
    frequency: 'daily' | 'weekly' | 'monthly';
    time: string;
    days?: string[];
    retention: number;
  };
  storage: {
    local: boolean;
    cloud: boolean;
    cloudProvider?: 'aws' | 'gcp' | 'azure';
    path: string;
  };
  compression: {
    enabled: boolean;
    level: number;
  };
  encryption: {
    enabled: boolean;
    algorithm: string;
    key: string;
  };
  validation: {
    enabled: boolean;
    checksum: boolean;
    integrity: boolean;
  };
  notifications: {
    enabled: boolean;
    email: string[];
    webhook?: string;
  };
}

// Backup realizado
interface BackupRecord {
  id: string;
  name: string;
  type: 'full' | 'incremental' | 'differential';
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  size: number;
  compressedSize: number;
  duration: number;
  startTime: string;
  endTime?: string;
  path: string;
  checksum: string;
  integrity: boolean;
  error?: string;
  metadata: {
    tables: number;
    records: number;
    version: string;
    database: string;
  };
}

// Restauração
interface RestoreRecord {
  id: string;
  backupId: string;
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  startTime: string;
  endTime?: string;
  progress: number;
  error?: string;
  validation: {
    checksum: boolean;
    integrity: boolean;
    data: boolean;
  };
}

// Props do componente
interface BackupRestoreProps {
  onBackup?: (config: BackupConfig) => void;
  onRestore?: (backupId: string, options: any) => void;
  onDelete?: (backupId: string) => void;
  onValidate?: (backupId: string) => void;
  readOnly?: boolean;
}

export const BackupRestore: React.FC<BackupRestoreProps> = ({
  onBackup,
  onRestore,
  onDelete,
  onValidate,
  readOnly = false
}) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [backups, setBackups] = useState<BackupRecord[]>([]);
  const [restores, setRestores] = useState<RestoreRecord[]>([]);
  const [configs, setConfigs] = useState<BackupConfig[]>([]);
  const [selectedBackup, setSelectedBackup] = useState<BackupRecord | null>(null);
  const [selectedConfig, setSelectedConfig] = useState<BackupConfig | null>(null);
  const [showBackupModal, setShowBackupModal] = useState(false);
  const [showRestoreModal, setShowRestoreModal] = useState(false);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [activeTab, setActiveTab] = useState('backups');
  const [currentStep, setCurrentStep] = useState(0);
  const [backupProgress, setBackupProgress] = useState(0);
  const [restoreProgress, setRestoreProgress] = useState(0);

  // Tipos de backup disponíveis
  const backupTypes: BackupType[] = useMemo(() => [
    {
      id: 'full',
      name: 'Backup Completo',
      description: 'Backup de todos os dados do sistema',
      icon: <DatabaseOutlined />,
      size: 1024, // MB
      duration: 30, // minutos
      compression: true,
      encryption: true
    },
    {
      id: 'incremental',
      name: 'Backup Incremental',
      description: 'Backup apenas das mudanças desde o último backup',
      icon: <SyncOutlined />,
      size: 256, // MB
      duration: 10, // minutos
      compression: true,
      encryption: true
    },
    {
      id: 'differential',
      name: 'Backup Diferencial',
      description: 'Backup das mudanças desde o último backup completo',
      icon: <HistoryOutlined />,
      size: 512, // MB
      duration: 15, // minutos
      compression: true,
      encryption: true
    }
  ], []);

  // Carregar dados iniciais
  useEffect(() => {
    loadBackups();
    loadRestores();
    loadConfigs();
  }, []);

  const loadBackups = async () => {
    setLoading(true);
    try {
      // Simular carregamento de backups
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockBackups: BackupRecord[] = [
        {
          id: 'backup_1',
          name: 'Backup Completo - 2024-12-20',
          type: 'full',
          status: 'completed',
          size: 1024,
          compressedSize: 512,
          duration: 1800,
          startTime: '2024-12-20T10:00:00Z',
          endTime: '2024-12-20T10:30:00Z',
          path: '/backups/backup_20241220_100000.zip',
          checksum: 'sha256:abc123...',
          integrity: true,
          metadata: {
            tables: 25,
            records: 15000,
            version: '1.0.0',
            database: 'omni_keywords_finder'
          }
        },
        {
          id: 'backup_2',
          name: 'Backup Incremental - 2024-12-19',
          type: 'incremental',
          status: 'completed',
          size: 256,
          compressedSize: 128,
          duration: 600,
          startTime: '2024-12-19T22:00:00Z',
          endTime: '2024-12-19T22:10:00Z',
          path: '/backups/backup_20241219_220000.zip',
          checksum: 'sha256:def456...',
          integrity: true,
          metadata: {
            tables: 25,
            records: 15000,
            version: '1.0.0',
            database: 'omni_keywords_finder'
          }
        }
      ];
      
      setBackups(mockBackups);
    } catch (error) {
      message.error('Erro ao carregar backups');
    } finally {
      setLoading(false);
    }
  };

  const loadRestores = async () => {
    try {
      const mockRestores: RestoreRecord[] = [
        {
          id: 'restore_1',
          backupId: 'backup_1',
          status: 'completed',
          startTime: '2024-12-20T11:00:00Z',
          endTime: '2024-12-20T11:15:00Z',
          progress: 100,
          validation: {
            checksum: true,
            integrity: true,
            data: true
          }
        }
      ];
      
      setRestores(mockRestores);
    } catch (error) {
      message.error('Erro ao carregar restaurações');
    }
  };

  const loadConfigs = async () => {
    try {
      const mockConfigs: BackupConfig[] = [
        {
          id: 'config_1',
          name: 'Backup Diário Automático',
          type: 'incremental',
          schedule: {
            enabled: true,
            frequency: 'daily',
            time: '22:00',
            retention: 30
          },
          storage: {
            local: true,
            cloud: true,
            cloudProvider: 'aws',
            path: '/backups/'
          },
          compression: {
            enabled: true,
            level: 6
          },
          encryption: {
            enabled: true,
            algorithm: 'AES-256',
            key: 'encrypted_key'
          },
          validation: {
            enabled: true,
            checksum: true,
            integrity: true
          },
          notifications: {
            enabled: true,
            email: ['admin@example.com']
          }
        }
      ];
      
      setConfigs(mockConfigs);
    } catch (error) {
      message.error('Erro ao carregar configurações');
    }
  };

  // Iniciar backup
  const handleStartBackup = useCallback(async (config: BackupConfig) => {
    setLoading(true);
    setBackupProgress(0);
    
    try {
      // Simular progresso do backup
      const progressInterval = setInterval(() => {
        setBackupProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      // Simular tempo de backup
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      clearInterval(progressInterval);
      setBackupProgress(100);

      const newBackup: BackupRecord = {
        id: `backup_${Date.now()}`,
        name: `${config.name} - ${new Date().toLocaleDateString()}`,
        type: config.type,
        status: 'completed',
        size: 1024,
        compressedSize: 512,
        duration: 300,
        startTime: new Date().toISOString(),
        endTime: new Date().toISOString(),
        path: `/backups/backup_${Date.now()}.zip`,
        checksum: `sha256:${Math.random().toString(36).substring(7)}`,
        integrity: true,
        metadata: {
          tables: 25,
          records: 15000,
          version: '1.0.0',
          database: 'omni_keywords_finder'
        }
      };

      setBackups(prev => [newBackup, ...prev]);
      onBackup?.(config);
      message.success('Backup concluído com sucesso');
    } catch (error) {
      message.error('Erro ao realizar backup');
    } finally {
      setLoading(false);
      setBackupProgress(0);
    }
  }, [onBackup]);

  // Iniciar restauração
  const handleStartRestore = useCallback(async (backupId: string, options: any) => {
    setLoading(true);
    setRestoreProgress(0);
    
    try {
      // Simular progresso da restauração
      const progressInterval = setInterval(() => {
        setRestoreProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 15;
        });
      }, 300);

      // Simular tempo de restauração
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      clearInterval(progressInterval);
      setRestoreProgress(100);

      const newRestore: RestoreRecord = {
        id: `restore_${Date.now()}`,
        backupId,
        status: 'completed',
        startTime: new Date().toISOString(),
        endTime: new Date().toISOString(),
        progress: 100,
        validation: {
          checksum: true,
          integrity: true,
          data: true
        }
      };

      setRestores(prev => [newRestore, ...prev]);
      onRestore?.(backupId, options);
      message.success('Restauração concluída com sucesso');
    } catch (error) {
      message.error('Erro ao realizar restauração');
    } finally {
      setLoading(false);
      setRestoreProgress(0);
    }
  }, [onRestore]);

  // Excluir backup
  const handleDeleteBackup = useCallback(async (backupId: string) => {
    try {
      setBackups(prev => prev.filter(b => b.id !== backupId));
      onDelete?.(backupId);
      message.success('Backup excluído com sucesso');
    } catch (error) {
      message.error('Erro ao excluir backup');
    }
  }, [onDelete]);

  // Validar backup
  const handleValidateBackup = useCallback(async (backupId: string) => {
    try {
      onValidate?.(backupId);
      message.success('Validação iniciada');
    } catch (error) {
      message.error('Erro ao validar backup');
    }
  }, [onValidate]);

  // Colunas da tabela de backups
  const backupColumns = [
    {
      title: 'Nome',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: BackupRecord) => (
        <Space direction="vertical" size="small">
          <Text strong>{text}</Text>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {new Date(record.startTime).toLocaleString()}
          </Text>
        </Space>
      )
    },
    {
      title: 'Tipo',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => {
        const typeConfig = backupTypes.find(t => t.id === type);
        return (
          <Tag color={type === 'full' ? 'blue' : type === 'incremental' ? 'green' : 'orange'}>
            {typeConfig?.name || type}
          </Tag>
        );
      }
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusConfig = {
          running: { color: 'processing', icon: <SyncOutlined spin /> },
          completed: { color: 'success', icon: <CheckCircleOutlined /> },
          failed: { color: 'error', icon: <ExclamationCircleOutlined /> },
          cancelled: { color: 'default', icon: <CloseOutlined /> }
        };
        
        const config = statusConfig[status as keyof typeof statusConfig];
        return (
          <Tag color={config?.color} icon={config?.icon}>
            {status.toUpperCase()}
          </Tag>
        );
      }
    },
    {
      title: 'Tamanho',
      dataIndex: 'compressedSize',
      key: 'compressedSize',
      render: (size: number) => `${(size / 1024).toFixed(2)} MB`
    },
    {
      title: 'Duração',
      dataIndex: 'duration',
      key: 'duration',
      render: (duration: number) => `${Math.floor(duration / 60)}m ${duration % 60}s`
    },
    {
      title: 'Integridade',
      dataIndex: 'integrity',
      key: 'integrity',
      render: (integrity: boolean) => (
        <Tag color={integrity ? 'success' : 'error'} icon={integrity ? <CheckOutlined /> : <CloseOutlined />}>
          {integrity ? 'Válido' : 'Inválido'}
        </Tag>
      )
    },
    {
      title: 'Ações',
      key: 'actions',
      render: (_, record: BackupRecord) => (
        <Space>
          <Tooltip title="Ver detalhes">
            <Button 
              type="text" 
              size="small" 
              icon={<EyeOutlined />} 
              onClick={() => {
                setSelectedBackup(record);
                setShowDetailsModal(true);
              }}
            />
          </Tooltip>
          <Tooltip title="Restaurar">
            <Button 
              type="text" 
              size="small" 
              icon={<CloudDownloadOutlined />} 
              onClick={() => {
                setSelectedBackup(record);
                setShowRestoreModal(true);
              }}
            />
          </Tooltip>
          <Tooltip title="Validar">
            <Button 
              type="text" 
              size="small" 
              icon={<SafetyOutlined />} 
              onClick={() => handleValidateBackup(record.id)}
            />
          </Tooltip>
          <Tooltip title="Excluir">
            <Button 
              type="text" 
              size="small" 
              icon={<DeleteOutlined />} 
              danger
              onClick={() => handleDeleteBackup(record.id)}
            />
          </Tooltip>
        </Space>
      )
    }
  ];

  // Colunas da tabela de restaurações
  const restoreColumns = [
    {
      title: 'Backup',
      dataIndex: 'backupId',
      key: 'backupId',
      render: (backupId: string) => {
        const backup = backups.find(b => b.id === backupId);
        return backup?.name || backupId;
      }
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusConfig = {
          running: { color: 'processing', icon: <SyncOutlined spin /> },
          completed: { color: 'success', icon: <CheckCircleOutlined /> },
          failed: { color: 'error', icon: <ExclamationCircleOutlined /> },
          cancelled: { color: 'default', icon: <CloseOutlined /> }
        };
        
        const config = statusConfig[status as keyof typeof statusConfig];
        return (
          <Tag color={config?.color} icon={config?.icon}>
            {status.toUpperCase()}
          </Tag>
        );
      }
    },
    {
      title: 'Progresso',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress: number) => (
        <Progress percent={progress} size="small" />
      )
    },
    {
      title: 'Início',
      dataIndex: 'startTime',
      key: 'startTime',
      render: (time: string) => new Date(time).toLocaleString()
    },
    {
      title: 'Validação',
      key: 'validation',
      render: (_, record: RestoreRecord) => (
        <Space>
          <Tag color={record.validation.checksum ? 'success' : 'error'}>Checksum</Tag>
          <Tag color={record.validation.integrity ? 'success' : 'error'}>Integridade</Tag>
          <Tag color={record.validation.data ? 'success' : 'error'}>Dados</Tag>
        </Space>
      )
    }
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>
          {backupProgress > 0 ? `Realizando backup... ${backupProgress}%` : 
           restoreProgress > 0 ? `Restaurando dados... ${restoreProgress}%` : 
           'Carregando...'}
        </div>
        {(backupProgress > 0 || restoreProgress > 0) && (
          <Progress 
            percent={backupProgress || restoreProgress} 
            status="active"
            style={{ marginTop: '16px', maxWidth: '300px' }}
          />
        )}
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <Card style={{ marginBottom: '16px' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={4} style={{ margin: 0 }}>
              Sistema de Backup e Restauração
            </Title>
            <Text type="secondary">
              Gerencie backups automáticos e restaurações do sistema
            </Text>
          </Col>
          <Col>
            <Space>
              <Button 
                icon={<CloudUploadOutlined />} 
                type="primary"
                onClick={() => setShowBackupModal(true)}
                disabled={readOnly}
              >
                Novo Backup
              </Button>
              <Button 
                icon={<SettingOutlined />} 
                onClick={() => setShowConfigModal(true)}
                disabled={readOnly}
              >
                Configurações
              </Button>
              <Button 
                icon={<ReloadOutlined />} 
                onClick={loadBackups}
              >
                Atualizar
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Estatísticas */}
      <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total de Backups"
              value={backups.length}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Último Backup"
              value={backups.length > 0 ? new Date(backups[0].startTime).toLocaleDateString() : 'N/A'}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Espaço Utilizado"
              value={backups.reduce((sum, b) => sum + b.compressedSize, 0) / 1024}
              suffix="GB"
              prefix={<FileZipOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Backups Válidos"
              value={backups.filter(b => b.integrity).length}
              suffix={`/ ${backups.length}`}
              prefix={<SafetyOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* Conteúdo Principal */}
      <Card>
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="Backups" key="backups">
            <Table
              dataSource={backups}
              columns={backupColumns}
              rowKey="id"
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) => `${range[0]}-${range[1]} de ${total} backups`
              }}
            />
          </TabPane>
          
          <TabPane tab="Restaurações" key="restores">
            <Table
              dataSource={restores}
              columns={restoreColumns}
              rowKey="id"
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) => `${range[0]}-${range[1]} de ${total} restaurações`
              }}
            />
          </TabPane>
          
          <TabPane tab="Configurações" key="configs">
            <List
              dataSource={configs}
              renderItem={(config) => (
                <List.Item
                  actions={[
                    <Button 
                      key="edit" 
                      type="text" 
                      icon={<SettingOutlined />}
                      onClick={() => {
                        setSelectedConfig(config);
                        setShowConfigModal(true);
                      }}
                    >
                      Editar
                    </Button>,
                    <Button 
                      key="run" 
                      type="text" 
                      icon={<PlayCircleOutlined />}
                      onClick={() => handleStartBackup(config)}
                    >
                      Executar
                    </Button>
                  ]}
                >
                  <List.Item.Meta
                    title={config.name}
                    description={
                      <Space direction="vertical" size="small">
                        <Text>Tipo: {config.type}</Text>
                        <Text>Agendamento: {config.schedule.enabled ? 'Ativo' : 'Inativo'}</Text>
                        <Text>Armazenamento: {config.storage.local ? 'Local' : ''} {config.storage.cloud ? 'Nuvem' : ''}</Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </TabPane>
        </Tabs>
      </Card>

      {/* Modal de Novo Backup */}
      <Modal
        title="Novo Backup"
        open={showBackupModal}
        onCancel={() => setShowBackupModal(false)}
        onOk={() => setShowBackupModal(false)}
        width={600}
        footer={null}
      >
        <Steps current={currentStep} style={{ marginBottom: '24px' }}>
          <Step title="Tipo" description="Selecionar tipo de backup" />
          <Step title="Configuração" description="Configurar opções" />
          <Step title="Execução" description="Realizar backup" />
        </Steps>

        {currentStep === 0 && (
          <div>
            <Title level={5}>Selecione o tipo de backup:</Title>
            <Row gutter={[16, 16]}>
              {backupTypes.map(type => (
                <Col span={8} key={type.id}>
                  <Card
                    hoverable
                    style={{ textAlign: 'center' }}
                    onClick={() => {
                      setSelectedConfig({
                        id: `config_${Date.now()}`,
                        name: `Backup ${type.name}`,
                        type: type.id as any,
                        schedule: {
                          enabled: false,
                          frequency: 'daily',
                          time: '22:00',
                          retention: 30
                        },
                        storage: {
                          local: true,
                          cloud: false,
                          path: '/backups/'
                        },
                        compression: {
                          enabled: true,
                          level: 6
                        },
                        encryption: {
                          enabled: true,
                          algorithm: 'AES-256',
                          key: 'encrypted_key'
                        },
                        validation: {
                          enabled: true,
                          checksum: true,
                          integrity: true
                        },
                        notifications: {
                          enabled: false,
                          email: []
                        }
                      });
                      setCurrentStep(1);
                    }}
                  >
                    <div style={{ fontSize: '32px', marginBottom: '8px' }}>
                      {type.icon}
                    </div>
                    <Title level={5}>{type.name}</Title>
                    <Text type="secondary">{type.description}</Text>
                    <div style={{ marginTop: '8px' }}>
                      <Tag>Tamanho: {(type.size / 1024).toFixed(1)} GB</Tag>
                      <Tag>Duração: {type.duration} min</Tag>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </div>
        )}

        {currentStep === 1 && selectedConfig && (
          <div>
            <Title level={5}>Configurar backup:</Title>
            <Form layout="vertical">
              <Form.Item label="Nome do Backup">
                <Input 
                  value={selectedConfig.name}
                  onChange={(e) => setSelectedConfig(prev => prev ? { ...prev, name: e.target.value } : null)}
                />
              </Form.Item>
              
              <Form.Item label="Agendamento">
                <Switch 
                  checked={selectedConfig.schedule.enabled}
                  onChange={(checked) => setSelectedConfig(prev => prev ? {
                    ...prev,
                    schedule: { ...prev.schedule, enabled: checked }
                  } : null)}
                />
                {selectedConfig.schedule.enabled && (
                  <div style={{ marginTop: '8px' }}>
                    <Select
                      value={selectedConfig.schedule.frequency}
                      onChange={(value) => setSelectedConfig(prev => prev ? {
                        ...prev,
                        schedule: { ...prev.schedule, frequency: value }
                      } : null)}
                      style={{ width: '100%', marginBottom: '8px' }}
                    >
                      <Option value="daily">Diário</Option>
                      <Option value="weekly">Semanal</Option>
                      <Option value="monthly">Mensal</Option>
                    </Select>
                    <TimePicker
                      value={selectedConfig.schedule.time}
                      onChange={(time) => setSelectedConfig(prev => prev ? {
                        ...prev,
                        schedule: { ...prev.schedule, time: time?.format('HH:mm') || '22:00' }
                      } : null)}
                      format="HH:mm"
                    />
                  </div>
                )}
              </Form.Item>

              <Form.Item label="Armazenamento">
                <Checkbox
                  checked={selectedConfig.storage.local}
                  onChange={(e) => setSelectedConfig(prev => prev ? {
                    ...prev,
                    storage: { ...prev.storage, local: e.target.checked }
                  } : null)}
                >
                  Local
                </Checkbox>
                <Checkbox
                  checked={selectedConfig.storage.cloud}
                  onChange={(e) => setSelectedConfig(prev => prev ? {
                    ...prev,
                    storage: { ...prev.storage, cloud: e.target.checked }
                  } : null)}
                >
                  Nuvem
                </Checkbox>
              </Form.Item>

              <Form.Item label="Compressão">
                <Switch 
                  checked={selectedConfig.compression.enabled}
                  onChange={(checked) => setSelectedConfig(prev => prev ? {
                    ...prev,
                    compression: { ...prev.compression, enabled: checked }
                  } : null)}
                />
                {selectedConfig.compression.enabled && (
                  <Slider
                    min={1}
                    max={9}
                    value={selectedConfig.compression.level}
                    onChange={(value) => setSelectedConfig(prev => prev ? {
                      ...prev,
                      compression: { ...prev.compression, level: value }
                    } : null)}
                    marks={{
                      1: 'Rápido',
                      5: 'Equilibrado',
                      9: 'Máximo'
                    }}
                  />
                )}
              </Form.Item>

              <Form.Item label="Criptografia">
                <Switch 
                  checked={selectedConfig.encryption.enabled}
                  onChange={(checked) => setSelectedConfig(prev => prev ? {
                    ...prev,
                    encryption: { ...prev.encryption, enabled: checked }
                  } : null)}
                />
              </Form.Item>
            </Form>
            
            <div style={{ textAlign: 'right', marginTop: '16px' }}>
              <Button onClick={() => setCurrentStep(0)}>Anterior</Button>
              <Button 
                type="primary" 
                onClick={() => setCurrentStep(2)}
                style={{ marginLeft: '8px' }}
              >
                Próximo
              </Button>
            </div>
          </div>
        )}

        {currentStep === 2 && selectedConfig && (
          <div>
            <Title level={5}>Executar backup:</Title>
            <Alert
              message="Configuração do Backup"
              description={
                <div>
                  <p><strong>Tipo:</strong> {selectedConfig.type}</p>
                  <p><strong>Nome:</strong> {selectedConfig.name}</p>
                  <p><strong>Agendamento:</strong> {selectedConfig.schedule.enabled ? 'Ativo' : 'Inativo'}</p>
                  <p><strong>Armazenamento:</strong> {selectedConfig.storage.local ? 'Local' : ''} {selectedConfig.storage.cloud ? 'Nuvem' : ''}</p>
                  <p><strong>Compressão:</strong> {selectedConfig.compression.enabled ? 'Ativa' : 'Inativa'}</p>
                  <p><strong>Criptografia:</strong> {selectedConfig.encryption.enabled ? 'Ativa' : 'Inativa'}</p>
                </div>
              }
              type="info"
              style={{ marginBottom: '16px' }}
            />
            
            <div style={{ textAlign: 'center' }}>
              <Button 
                type="primary" 
                size="large"
                icon={<CloudUploadOutlined />}
                onClick={() => {
                  handleStartBackup(selectedConfig);
                  setShowBackupModal(false);
                  setCurrentStep(0);
                }}
              >
                Iniciar Backup
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Modal de Restauração */}
      <Modal
        title="Restaurar Backup"
        open={showRestoreModal}
        onCancel={() => setShowRestoreModal(false)}
        onOk={() => setShowRestoreModal(false)}
        width={500}
      >
        {selectedBackup && (
          <div>
            <Alert
              message="Atenção"
              description="A restauração irá sobrescrever os dados atuais. Certifique-se de que tem um backup recente."
              type="warning"
              style={{ marginBottom: '16px' }}
            />
            
            <div style={{ marginBottom: '16px' }}>
              <Text strong>Backup selecionado:</Text>
              <div style={{ marginTop: '8px', padding: '8px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
                <p><strong>Nome:</strong> {selectedBackup.name}</p>
                <p><strong>Tipo:</strong> {selectedBackup.type}</p>
                <p><strong>Tamanho:</strong> {(selectedBackup.compressedSize / 1024).toFixed(2)} MB</p>
                <p><strong>Data:</strong> {new Date(selectedBackup.startTime).toLocaleString()}</p>
                <p><strong>Integridade:</strong> {selectedBackup.integrity ? 'Válida' : 'Inválida'}</p>
              </div>
            </div>

            <Form layout="vertical">
              <Form.Item label="Opções de Restauração">
                <Checkbox defaultChecked>Validar integridade antes da restauração</Checkbox>
                <Checkbox defaultChecked>Fazer backup dos dados atuais</Checkbox>
                <Checkbox>Restaurar apenas dados específicos</Checkbox>
              </Form.Item>
            </Form>

            <div style={{ textAlign: 'center', marginTop: '16px' }}>
              <Button 
                type="primary" 
                danger
                icon={<CloudDownloadOutlined />}
                onClick={() => {
                  handleStartRestore(selectedBackup.id, {});
                  setShowRestoreModal(false);
                }}
              >
                Confirmar Restauração
              </Button>
            </div>
          </div>
        )}
      </Modal>

      {/* Modal de Detalhes */}
      <Modal
        title="Detalhes do Backup"
        open={showDetailsModal}
        onCancel={() => setShowDetailsModal(false)}
        footer={null}
        width={700}
      >
        {selectedBackup && (
          <div>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Card size="small" title="Informações Gerais">
                  <p><strong>ID:</strong> {selectedBackup.id}</p>
                  <p><strong>Nome:</strong> {selectedBackup.name}</p>
                  <p><strong>Tipo:</strong> {selectedBackup.type}</p>
                  <p><strong>Status:</strong> {selectedBackup.status}</p>
                  <p><strong>Duração:</strong> {Math.floor(selectedBackup.duration / 60)}m {selectedBackup.duration % 60}s</p>
                </Card>
              </Col>
              <Col span={12}>
                <Card size="small" title="Armazenamento">
                  <p><strong>Tamanho Original:</strong> {(selectedBackup.size / 1024).toFixed(2)} MB</p>
                  <p><strong>Tamanho Comprimido:</strong> {(selectedBackup.compressedSize / 1024).toFixed(2)} MB</p>
                  <p><strong>Taxa de Compressão:</strong> {((1 - selectedBackup.compressedSize / selectedBackup.size) * 100).toFixed(1)}%</p>
                  <p><strong>Caminho:</strong> {selectedBackup.path}</p>
                  <p><strong>Checksum:</strong> {selectedBackup.checksum}</p>
                </Card>
              </Col>
            </Row>

            <Card size="small" title="Metadados" style={{ marginTop: '16px' }}>
              <Row gutter={[16, 16]}>
                <Col span={6}>
                  <Statistic title="Tabelas" value={selectedBackup.metadata.tables} />
                </Col>
                <Col span={6}>
                  <Statistic title="Registros" value={selectedBackup.metadata.records} />
                </Col>
                <Col span={6}>
                  <Statistic title="Versão" value={selectedBackup.metadata.version} />
                </Col>
                <Col span={6}>
                  <Statistic title="Database" value={selectedBackup.metadata.database} />
                </Col>
              </Row>
            </Card>

            <Card size="small" title="Timeline" style={{ marginTop: '16px' }}>
              <Timeline>
                <Timeline.Item>
                  <p><strong>Início:</strong> {new Date(selectedBackup.startTime).toLocaleString()}</p>
                </Timeline.Item>
                {selectedBackup.endTime && (
                  <Timeline.Item>
                    <p><strong>Fim:</strong> {new Date(selectedBackup.endTime).toLocaleString()}</p>
                  </Timeline.Item>
                )}
              </Timeline>
            </Card>
          </div>
        )}
      </Modal>

      {/* Modal de Configurações */}
      <Modal
        title="Configurações de Backup"
        open={showConfigModal}
        onCancel={() => setShowConfigModal(false)}
        onOk={() => setShowConfigModal(false)}
        width={600}
      >
        <Tabs>
          <TabPane tab="Agendamento" key="schedule">
            <Form layout="vertical">
              <Form.Item label="Backup Automático">
                <Switch defaultChecked />
              </Form.Item>
              <Form.Item label="Frequência">
                <Select defaultValue="daily">
                  <Option value="daily">Diário</Option>
                  <Option value="weekly">Semanal</Option>
                  <Option value="monthly">Mensal</Option>
                </Select>
              </Form.Item>
              <Form.Item label="Horário">
                <TimePicker defaultValue="22:00" format="HH:mm" />
              </Form.Item>
              <Form.Item label="Retenção (dias)">
                <InputNumber min={1} max={365} defaultValue={30} />
              </Form.Item>
            </Form>
          </TabPane>
          
          <TabPane tab="Armazenamento" key="storage">
            <Form layout="vertical">
              <Form.Item label="Backup Local">
                <Switch defaultChecked />
              </Form.Item>
              <Form.Item label="Backup em Nuvem">
                <Switch />
              </Form.Item>
              <Form.Item label="Provedor de Nuvem">
                <Select placeholder="Selecionar provedor">
                  <Option value="aws">Amazon S3</Option>
                  <Option value="gcp">Google Cloud Storage</Option>
                  <Option value="azure">Azure Blob Storage</Option>
                </Select>
              </Form.Item>
              <Form.Item label="Caminho Local">
                <Input defaultValue="/backups/" />
              </Form.Item>
            </Form>
          </TabPane>
          
          <TabPane tab="Segurança" key="security">
            <Form layout="vertical">
              <Form.Item label="Criptografia">
                <Switch defaultChecked />
              </Form.Item>
              <Form.Item label="Algoritmo">
                <Select defaultValue="AES-256">
                  <Option value="AES-256">AES-256</Option>
                  <Option value="AES-128">AES-128</Option>
                </Select>
              </Form.Item>
              <Form.Item label="Validação de Integridade">
                <Switch defaultChecked />
              </Form.Item>
              <Form.Item label="Checksum">
                <Switch defaultChecked />
              </Form.Item>
            </Form>
          </TabPane>
          
          <TabPane tab="Notificações" key="notifications">
            <Form layout="vertical">
              <Form.Item label="Notificações por Email">
                <Switch defaultChecked />
              </Form.Item>
              <Form.Item label="Emails">
                <Select mode="tags" placeholder="Adicionar emails">
                  <Option value="admin@example.com">admin@example.com</Option>
                </Select>
              </Form.Item>
              <Form.Item label="Webhook">
                <Input placeholder="URL do webhook" />
              </Form.Item>
            </Form>
          </TabPane>
        </Tabs>
      </Modal>
    </div>
  );
}; 