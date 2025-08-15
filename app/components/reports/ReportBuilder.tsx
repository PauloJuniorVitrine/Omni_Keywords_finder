/**
 * ReportBuilder.tsx
 * 
 * Construtor Visual de Relatórios Personalizados - Omni Keywords Finder
 * 
 * Prompt: CHECKLIST_INTERFACE_GRAFICA_V1.md - UI-010
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2024-12-20
 * 
 * Funcionalidades:
 * - Construtor visual de relatórios
 * - Drag-and-drop de componentes
 * - Múltiplos tipos de gráficos
 * - Filtros customizáveis
 * - Agendamento de relatórios
 * - Exportação em múltiplos formatos
 * - Templates pré-definidos
 * - Compartilhamento de relatórios
 * - Versionamento de relatórios
 * - Permissões de acesso
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Card, Row, Col, Button, Space, Modal, Form, Input, Select, DatePicker, 
  Switch, message, Spin, Tabs, Tooltip, Badge, Divider, Typography, 
  Dropdown, Menu, Upload, Table, Tag, Progress, Alert, Drawer, List,
  Checkbox, Radio, Slider, ColorPicker, InputNumber, TimePicker
} from 'antd';
import { 
  PlusOutlined, 
  SaveOutlined, 
  EyeOutlined, 
  ShareAltOutlined,
  DownloadOutlined,
  SettingOutlined,
  DeleteOutlined,
  CopyOutlined,
  ClockCircleOutlined,
  BarChartOutlined,
  LineChartOutlined,
  PieChartOutlined,
  TableOutlined,
  FilterOutlined,
  LayoutOutlined,
  TemplateOutlined,
  UserOutlined,
  LockOutlined,
  UnlockOutlined,
  HistoryOutlined,
  StarOutlined,
  StarFilled,
  DragOutlined,
  ResizeOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { TabPane } = Tabs;
const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

// Tipos de componentes disponíveis
interface ComponentType {
  id: string;
  name: string;
  icon: React.ReactNode;
  category: 'chart' | 'table' | 'metric' | 'filter' | 'text';
  defaultConfig: any;
  preview: React.ReactNode;
}

// Configuração de um componente no relatório
interface ReportComponent {
  id: string;
  type: string;
  title: string;
  config: any;
  position: { x: number; y: number };
  size: { width: number; height: number };
  filters: FilterConfig[];
  dataSource: string;
  refreshInterval?: number;
}

// Configuração de filtros
interface FilterConfig {
  id: string;
  field: string;
  operator: 'equals' | 'contains' | 'greater' | 'less' | 'between' | 'in';
  value: any;
  label: string;
}

// Template de relatório
interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  thumbnail: string;
  components: ReportComponent[];
  isDefault: boolean;
  createdBy: string;
  createdAt: string;
  tags: string[];
}

// Relatório
interface Report {
  id: string;
  name: string;
  description: string;
  components: ReportComponent[];
  filters: FilterConfig[];
  schedule?: {
    enabled: boolean;
    frequency: 'daily' | 'weekly' | 'monthly';
    time: string;
    recipients: string[];
    format: 'pdf' | 'csv' | 'json' | 'excel';
  };
  permissions: {
    owner: string;
    shared: boolean;
    users: string[];
    roles: string[];
  };
  version: number;
  isPublic: boolean;
  isFavorite: boolean;
  createdAt: string;
  updatedAt: string;
  lastRun?: string;
  nextRun?: string;
}

// Props do componente
interface ReportBuilderProps {
  reportId?: string;
  onSave?: (report: Report) => void;
  onExport?: (report: Report, format: string) => void;
  onShare?: (report: Report) => void;
  onSchedule?: (report: Report) => void;
  readOnly?: boolean;
}

// Componente arrastável
const DraggableComponent: React.FC<{
  component: ComponentType;
  onAdd: (component: ComponentType) => void;
}> = ({ component, onAdd }) => {
  const [{ isDragging }, drag] = useDrag({
    type: 'COMPONENT',
    item: component,
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  return (
    <div
      ref={drag}
      style={{
        opacity: isDragging ? 0.5 : 1,
        cursor: 'move',
        padding: '8px',
        border: '1px solid #d9d9d9',
        borderRadius: '6px',
        backgroundColor: '#fafafa',
        marginBottom: '8px',
      }}
      onClick={() => onAdd(component)}
    >
      <Space>
        {component.icon}
        <Text>{component.name}</Text>
      </Space>
    </div>
  );
};

// Área de drop para o canvas
const CanvasDropZone: React.FC<{
  onDrop: (component: ComponentType, position: { x: number; y: number }) => void;
  children: React.ReactNode;
}> = ({ onDrop, children }) => {
  const [{ isOver }, drop] = useDrop({
    accept: 'COMPONENT',
    drop: (item: ComponentType, monitor) => {
      const offset = monitor.getClientOffset();
      if (offset) {
        onDrop(item, { x: offset.x, y: offset.y });
      }
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  });

  return (
    <div
      ref={drop}
      style={{
        minHeight: '600px',
        border: isOver ? '2px dashed #1890ff' : '1px solid #d9d9d9',
        borderRadius: '8px',
        padding: '16px',
        backgroundColor: isOver ? '#f0f8ff' : '#ffffff',
        position: 'relative',
      }}
    >
      {children}
    </div>
  );
};

// Componente de relatório renderizado
const ReportComponentRenderer: React.FC<{
  component: ReportComponent;
  onEdit: (component: ReportComponent) => void;
  onDelete: (componentId: string) => void;
  onResize: (componentId: string, size: { width: number; height: number }) => void;
}> = ({ component, onEdit, onDelete, onResize }) => {
  const renderComponent = () => {
    switch (component.type) {
      case 'line-chart':
        return (
          <div style={{ padding: '16px', textAlign: 'center' }}>
            <LineChartOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
            <div>Gráfico de Linha</div>
            <div style={{ fontSize: '12px', color: '#666' }}>{component.title}</div>
          </div>
        );
      case 'bar-chart':
        return (
          <div style={{ padding: '16px', textAlign: 'center' }}>
            <BarChartOutlined style={{ fontSize: '24px', color: '#52c41a' }} />
            <div>Gráfico de Barras</div>
            <div style={{ fontSize: '12px', color: '#666' }}>{component.title}</div>
          </div>
        );
      case 'pie-chart':
        return (
          <div style={{ padding: '16px', textAlign: 'center' }}>
            <PieChartOutlined style={{ fontSize: '24px', color: '#722ed1' }} />
            <div>Gráfico de Pizza</div>
            <div style={{ fontSize: '12px', color: '#666' }}>{component.title}</div>
          </div>
        );
      case 'table':
        return (
          <div style={{ padding: '16px', textAlign: 'center' }}>
            <TableOutlined style={{ fontSize: '24px', color: '#fa8c16' }} />
            <div>Tabela de Dados</div>
            <div style={{ fontSize: '12px', color: '#666' }}>{component.title}</div>
          </div>
        );
      case 'metric':
        return (
          <div style={{ padding: '16px', textAlign: 'center' }}>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#1890ff' }}>
              {component.config.value || '0'}
            </div>
            <div style={{ fontSize: '14px', color: '#666' }}>{component.title}</div>
          </div>
        );
      default:
        return <div>Componente não suportado</div>;
    }
  };

  return (
    <div
      style={{
        position: 'absolute',
        left: component.position.x,
        top: component.position.y,
        width: component.size.width,
        height: component.size.height,
        border: '1px solid #d9d9d9',
        borderRadius: '6px',
        backgroundColor: '#ffffff',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        cursor: 'move',
      }}
    >
      <div style={{ 
        padding: '8px', 
        borderBottom: '1px solid #f0f0f0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: '#fafafa'
      }}>
        <Text strong style={{ fontSize: '12px' }}>{component.title}</Text>
        <Space size="small">
          <Tooltip title="Editar">
            <Button 
              type="text" 
              size="small" 
              icon={<SettingOutlined />} 
              onClick={() => onEdit(component)}
            />
          </Tooltip>
          <Tooltip title="Excluir">
            <Button 
              type="text" 
              size="small" 
              icon={<DeleteOutlined />} 
              onClick={() => onDelete(component.id)}
              danger
            />
          </Tooltip>
        </Space>
      </div>
      <div style={{ height: 'calc(100% - 40px)', overflow: 'hidden' }}>
        {renderComponent()}
      </div>
    </div>
  );
};

export const ReportBuilder: React.FC<ReportBuilderProps> = ({
  reportId,
  onSave,
  onExport,
  onShare,
  onSchedule,
  readOnly = false
}) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<Report | null>(null);
  const [components, setComponents] = useState<ReportComponent[]>([]);
  const [selectedComponent, setSelectedComponent] = useState<ReportComponent | null>(null);
  const [showComponentModal, setShowComponentModal] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [activeTab, setActiveTab] = useState('components');
  const [canvasSize, setCanvasSize] = useState({ width: 1200, height: 800 });

  // Componentes disponíveis
  const availableComponents: ComponentType[] = useMemo(() => [
    {
      id: 'line-chart',
      name: 'Gráfico de Linha',
      icon: <LineChartOutlined />,
      category: 'chart',
      defaultConfig: {
        title: 'Gráfico de Linha',
        dataSource: 'keywords_performance',
        xField: 'date',
        yField: 'value',
        color: '#1890ff'
      },
      preview: <LineChartOutlined style={{ fontSize: '24px' }} />
    },
    {
      id: 'bar-chart',
      name: 'Gráfico de Barras',
      icon: <BarChartOutlined />,
      category: 'chart',
      defaultConfig: {
        title: 'Gráfico de Barras',
        dataSource: 'clusters_distribution',
        xField: 'category',
        yField: 'count',
        color: '#52c41a'
      },
      preview: <BarChartOutlined style={{ fontSize: '24px' }} />
    },
    {
      id: 'pie-chart',
      name: 'Gráfico de Pizza',
      icon: <PieChartOutlined />,
      category: 'chart',
      defaultConfig: {
        title: 'Gráfico de Pizza',
        dataSource: 'keywords_categories',
        valueField: 'value',
        nameField: 'category',
        colors: ['#1890ff', '#52c41a', '#722ed1', '#fa8c16']
      },
      preview: <PieChartOutlined style={{ fontSize: '24px' }} />
    },
    {
      id: 'table',
      name: 'Tabela de Dados',
      icon: <TableOutlined />,
      category: 'table',
      defaultConfig: {
        title: 'Tabela de Dados',
        dataSource: 'keywords_list',
        columns: ['keyword', 'volume', 'difficulty', 'cpc'],
        pagination: true,
        pageSize: 10
      },
      preview: <TableOutlined style={{ fontSize: '24px' }} />
    },
    {
      id: 'metric',
      name: 'Métrica',
      icon: <BarChartOutlined />,
      category: 'metric',
      defaultConfig: {
        title: 'Métrica',
        dataSource: 'total_keywords',
        value: 0,
        format: 'number',
        prefix: '',
        suffix: ''
      },
      preview: <BarChartOutlined style={{ fontSize: '24px' }} />
    }
  ], []);

  // Templates pré-definidos
  const defaultTemplates: ReportTemplate[] = useMemo(() => [
    {
      id: 'performance-overview',
      name: 'Visão Geral de Performance',
      description: 'Dashboard completo com métricas de performance do sistema',
      category: 'Performance',
      thumbnail: '/templates/performance.png',
      components: [
        {
          id: 'metric-1',
          type: 'metric',
          title: 'Total de Keywords',
          config: { dataSource: 'total_keywords', value: 0 },
          position: { x: 50, y: 50 },
          size: { width: 200, height: 100 },
          filters: [],
          dataSource: 'total_keywords'
        },
        {
          id: 'chart-1',
          type: 'line-chart',
          title: 'Performance ao Longo do Tempo',
          config: { dataSource: 'performance_trend' },
          position: { x: 300, y: 50 },
          size: { width: 400, height: 300 },
          filters: [],
          dataSource: 'performance_trend'
        }
      ],
      isDefault: true,
      createdBy: 'system',
      createdAt: new Date().toISOString(),
      tags: ['performance', 'overview', 'default']
    },
    {
      id: 'keywords-analysis',
      name: 'Análise de Keywords',
      description: 'Relatório detalhado de análise de keywords e clusters',
      category: 'Keywords',
      thumbnail: '/templates/keywords.png',
      components: [
        {
          id: 'chart-1',
          type: 'pie-chart',
          title: 'Distribuição de Clusters',
          config: { dataSource: 'clusters_distribution' },
          position: { x: 50, y: 50 },
          size: { width: 300, height: 300 },
          filters: [],
          dataSource: 'clusters_distribution'
        },
        {
          id: 'table-1',
          type: 'table',
          title: 'Top Keywords',
          config: { dataSource: 'top_keywords' },
          position: { x: 400, y: 50 },
          size: { width: 400, height: 300 },
          filters: [],
          dataSource: 'top_keywords'
        }
      ],
      isDefault: true,
      createdBy: 'system',
      createdAt: new Date().toISOString(),
      tags: ['keywords', 'analysis', 'clusters']
    }
  ], []);

  // Carregar relatório existente
  useEffect(() => {
    if (reportId) {
      loadReport(reportId);
    } else {
      // Criar novo relatório
      setReport({
        id: `report_${Date.now()}`,
        name: 'Novo Relatório',
        description: '',
        components: [],
        filters: [],
        permissions: {
          owner: 'current_user',
          shared: false,
          users: [],
          roles: []
        },
        version: 1,
        isPublic: false,
        isFavorite: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      });
    }
  }, [reportId]);

  const loadReport = async (id: string) => {
    setLoading(true);
    try {
      // Simular carregamento de relatório
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data - em produção viria da API
      const mockReport: Report = {
        id,
        name: 'Relatório de Performance',
        description: 'Análise completa de performance do sistema',
        components: [
          {
            id: 'metric-1',
            type: 'metric',
            title: 'Total de Keywords',
            config: { dataSource: 'total_keywords', value: 1250 },
            position: { x: 50, y: 50 },
            size: { width: 200, height: 100 },
            filters: [],
            dataSource: 'total_keywords'
          }
        ],
        filters: [],
        permissions: {
          owner: 'current_user',
          shared: false,
          users: [],
          roles: []
        },
        version: 1,
        isPublic: false,
        isFavorite: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      setReport(mockReport);
      setComponents(mockReport.components);
    } catch (error) {
      message.error('Erro ao carregar relatório');
    } finally {
      setLoading(false);
    }
  };

  // Adicionar componente ao canvas
  const handleAddComponent = useCallback((componentType: ComponentType) => {
    const newComponent: ReportComponent = {
      id: `component_${Date.now()}`,
      type: componentType.id,
      title: componentType.defaultConfig.title,
      config: { ...componentType.defaultConfig },
      position: { x: 100, y: 100 },
      size: { width: 300, height: 200 },
      filters: [],
      dataSource: componentType.defaultConfig.dataSource
    };

    setComponents(prev => [...prev, newComponent]);
    setSelectedComponent(newComponent);
    setShowComponentModal(true);
  }, []);

  // Editar componente
  const handleEditComponent = useCallback((component: ReportComponent) => {
    setSelectedComponent(component);
    setShowComponentModal(true);
  }, []);

  // Excluir componente
  const handleDeleteComponent = useCallback((componentId: string) => {
    setComponents(prev => prev.filter(c => c.id !== componentId));
    if (selectedComponent?.id === componentId) {
      setSelectedComponent(null);
      setShowComponentModal(false);
    }
  }, [selectedComponent]);

  // Salvar relatório
  const handleSave = useCallback(async () => {
    if (!report) return;

    setLoading(true);
    try {
      const updatedReport: Report = {
        ...report,
        components,
        updatedAt: new Date().toISOString(),
        version: report.version + 1
      };

      // Simular salvamento
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setReport(updatedReport);
      onSave?.(updatedReport);
      message.success('Relatório salvo com sucesso');
    } catch (error) {
      message.error('Erro ao salvar relatório');
    } finally {
      setLoading(false);
    }
  }, [report, components, onSave]);

  // Aplicar template
  const handleApplyTemplate = useCallback((template: ReportTemplate) => {
    setComponents(template.components.map(c => ({
      ...c,
      id: `component_${Date.now()}_${Math.random()}`
    })));
    setShowTemplateModal(false);
    message.success(`Template "${template.name}" aplicado com sucesso`);
  }, []);

  // Exportar relatório
  const handleExport = useCallback((format: string) => {
    if (!report) return;
    
    const updatedReport = { ...report, components };
    onExport?.(updatedReport, format);
    message.success(`Relatório exportado em formato ${format.toUpperCase()}`);
  }, [report, components, onExport]);

  // Agendar relatório
  const handleSchedule = useCallback(() => {
    if (!report) return;
    
    const updatedReport = { ...report, components };
    onSchedule?.(updatedReport);
    setShowScheduleModal(false);
  }, [report, components, onSchedule]);

  // Compartilhar relatório
  const handleShare = useCallback(() => {
    if (!report) return;
    
    const updatedReport = { ...report, components };
    onShare?.(updatedReport);
    setShowShareModal(false);
  }, [report, components, onShare]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>Carregando relatório...</div>
      </div>
    );
  }

  return (
    <DndProvider backend={HTML5Backend}>
      <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Card style={{ marginBottom: '16px' }}>
          <Row justify="space-between" align="middle">
            <Col>
              <Space>
                <Title level={4} style={{ margin: 0 }}>
                  {report?.name || 'Novo Relatório'}
                </Title>
                {report?.isFavorite && <StarFilled style={{ color: '#faad14' }} />}
                <Badge count={report?.version || 1} style={{ backgroundColor: '#52c41a' }} />
              </Space>
            </Col>
            <Col>
              <Space>
                <Button 
                  icon={<TemplateOutlined />} 
                  onClick={() => setShowTemplateModal(true)}
                >
                  Templates
                </Button>
                <Button 
                  icon={<ClockCircleOutlined />} 
                  onClick={() => setShowScheduleModal(true)}
                >
                  Agendar
                </Button>
                <Button 
                  icon={<ShareAltOutlined />} 
                  onClick={() => setShowShareModal(true)}
                >
                  Compartilhar
                </Button>
                <Dropdown
                  menu={{
                    items: [
                      { key: 'pdf', label: 'Exportar PDF', icon: <DownloadOutlined /> },
                      { key: 'csv', label: 'Exportar CSV', icon: <DownloadOutlined /> },
                      { key: 'json', label: 'Exportar JSON', icon: <DownloadOutlined /> },
                      { key: 'excel', label: 'Exportar Excel', icon: <DownloadOutlined /> }
                    ],
                    onClick: ({ key }) => handleExport(key)
                  }}
                >
                  <Button icon={<DownloadOutlined />}>
                    Exportar
                  </Button>
                </Dropdown>
                <Button 
                  type="primary" 
                  icon={<SaveOutlined />} 
                  onClick={handleSave}
                  loading={loading}
                >
                  Salvar
                </Button>
              </Space>
            </Col>
          </Row>
        </Card>

        {/* Main Content */}
        <div style={{ flex: 1, display: 'flex', gap: '16px' }}>
          {/* Sidebar */}
          <Card style={{ width: '300px', height: 'fit-content' }}>
            <Tabs activeKey={activeTab} onChange={setActiveTab}>
              <TabPane tab="Componentes" key="components">
                <div style={{ marginBottom: '16px' }}>
                  <Text strong>Arraste para o canvas:</Text>
                </div>
                {availableComponents.map(component => (
                  <DraggableComponent
                    key={component.id}
                    component={component}
                    onAdd={handleAddComponent}
                  />
                ))}
              </TabPane>
              <TabPane tab="Filtros" key="filters">
                <div style={{ marginBottom: '16px' }}>
                  <Text strong>Filtros Globais:</Text>
                </div>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Select placeholder="Selecionar campo" style={{ width: '100%' }}>
                    <Option value="date">Data</Option>
                    <Option value="category">Categoria</Option>
                    <Option value="status">Status</Option>
                  </Select>
                  <Select placeholder="Operador" style={{ width: '100%' }}>
                    <Option value="equals">Igual a</Option>
                    <Option value="contains">Contém</Option>
                    <Option value="greater">Maior que</Option>
                    <Option value="less">Menor que</Option>
                  </Select>
                  <Input placeholder="Valor" />
                  <Button size="small" block>Adicionar Filtro</Button>
                </Space>
              </TabPane>
              <TabPane tab="Configurações" key="settings">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text strong>Tamanho do Canvas:</Text>
                    <Row gutter={8} style={{ marginTop: '8px' }}>
                      <Col span={12}>
                        <InputNumber
                          placeholder="Largura"
                          value={canvasSize.width}
                          onChange={(value) => setCanvasSize(prev => ({ ...prev, width: value || 1200 }))}
                          style={{ width: '100%' }}
                        />
                      </Col>
                      <Col span={12}>
                        <InputNumber
                          placeholder="Altura"
                          value={canvasSize.height}
                          onChange={(value) => setCanvasSize(prev => ({ ...prev, height: value || 800 }))}
                          style={{ width: '100%' }}
                        />
                      </Col>
                    </Row>
                  </div>
                  <div>
                    <Text strong>Atualização Automática:</Text>
                    <Switch defaultChecked style={{ marginLeft: '8px' }} />
                  </div>
                  <div>
                    <Text strong>Modo de Visualização:</Text>
                    <Radio.Group defaultValue="edit" style={{ marginTop: '8px' }}>
                      <Radio.Button value="edit">Edição</Radio.Button>
                      <Radio.Button value="preview">Visualização</Radio.Button>
                    </Radio.Group>
                  </div>
                </Space>
              </TabPane>
            </Tabs>
          </Card>

          {/* Canvas */}
          <div style={{ flex: 1 }}>
            <Card>
              <div style={{ 
                width: canvasSize.width, 
                height: canvasSize.height,
                margin: '0 auto',
                position: 'relative',
                border: '1px solid #d9d9d9',
                borderRadius: '8px',
                backgroundColor: '#fafafa'
              }}>
                <CanvasDropZone onDrop={handleAddComponent}>
                  {components.map(component => (
                    <ReportComponentRenderer
                      key={component.id}
                      component={component}
                      onEdit={handleEditComponent}
                      onDelete={handleDeleteComponent}
                      onResize={(id, size) => {
                        setComponents(prev => 
                          prev.map(c => c.id === id ? { ...c, size } : c)
                        );
                      }}
                    />
                  ))}
                  {components.length === 0 && (
                    <div style={{ 
                      textAlign: 'center', 
                      padding: '50px',
                      color: '#666'
                    }}>
                      <LayoutOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                      <div>Arraste componentes aqui para começar</div>
                      <div style={{ fontSize: '12px', marginTop: '8px' }}>
                        Ou use um template para começar rapidamente
                      </div>
                    </div>
                  )}
                </CanvasDropZone>
              </div>
            </Card>
          </div>
        </div>

        {/* Modal de Configuração de Componente */}
        <Modal
          title={`Configurar ${selectedComponent?.title || 'Componente'}`}
          open={showComponentModal}
          onCancel={() => setShowComponentModal(false)}
          onOk={() => setShowComponentModal(false)}
          width={600}
        >
          {selectedComponent && (
            <Form layout="vertical">
              <Form.Item label="Título">
                <Input 
                  value={selectedComponent.title}
                  onChange={(e) => {
                    setSelectedComponent(prev => prev ? { ...prev, title: e.target.value } : null);
                    setComponents(prev => 
                      prev.map(c => c.id === selectedComponent.id ? { ...c, title: e.target.value } : c)
                    );
                  }}
                />
              </Form.Item>
              <Form.Item label="Fonte de Dados">
                <Select 
                  value={selectedComponent.dataSource}
                  onChange={(value) => {
                    setSelectedComponent(prev => prev ? { ...prev, dataSource: value } : null);
                    setComponents(prev => 
                      prev.map(c => c.id === selectedComponent.id ? { ...c, dataSource: value } : c)
                    );
                  }}
                >
                  <Option value="keywords_performance">Performance de Keywords</Option>
                  <Option value="clusters_distribution">Distribuição de Clusters</Option>
                  <Option value="user_behavior">Comportamento do Usuário</Option>
                  <Option value="system_metrics">Métricas do Sistema</Option>
                </Select>
              </Form.Item>
              <Form.Item label="Intervalo de Atualização (segundos)">
                <InputNumber 
                  value={selectedComponent.refreshInterval}
                  onChange={(value) => {
                    setSelectedComponent(prev => prev ? { ...prev, refreshInterval: value || undefined } : null);
                    setComponents(prev => 
                      prev.map(c => c.id === selectedComponent.id ? { ...c, refreshInterval: value || undefined } : c)
                    );
                  }}
                  min={0}
                  max={3600}
                />
              </Form.Item>
            </Form>
          )}
        </Modal>

        {/* Modal de Templates */}
        <Modal
          title="Templates de Relatório"
          open={showTemplateModal}
          onCancel={() => setShowTemplateModal(false)}
          footer={null}
          width={800}
        >
          <Row gutter={[16, 16]}>
            {defaultTemplates.map(template => (
              <Col span={12} key={template.id}>
                <Card
                  hoverable
                  cover={
                    <div style={{ 
                      height: '120px', 
                      backgroundColor: '#f0f0f0',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <TemplateOutlined style={{ fontSize: '48px', color: '#666' }} />
                    </div>
                  }
                  actions={[
                    <Button 
                      key="apply" 
                      type="primary" 
                      onClick={() => handleApplyTemplate(template)}
                    >
                      Aplicar
                    </Button>
                  ]}
                >
                  <Card.Meta
                    title={template.name}
                    description={template.description}
                  />
                  <div style={{ marginTop: '8px' }}>
                    {template.tags.map(tag => (
                      <Tag key={tag} size="small">{tag}</Tag>
                    ))}
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        </Modal>

        {/* Modal de Agendamento */}
        <Modal
          title="Agendar Relatório"
          open={showScheduleModal}
          onCancel={() => setShowScheduleModal(false)}
          onOk={handleSchedule}
          width={500}
        >
          <Form layout="vertical">
            <Form.Item label="Habilitar Agendamento">
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
              <TimePicker format="HH:mm" />
            </Form.Item>
            <Form.Item label="Destinatários">
              <Select mode="tags" placeholder="Adicionar emails">
                <Option value="admin@example.com">admin@example.com</Option>
                <Option value="user@example.com">user@example.com</Option>
              </Select>
            </Form.Item>
            <Form.Item label="Formato">
              <Select defaultValue="pdf">
                <Option value="pdf">PDF</Option>
                <Option value="csv">CSV</Option>
                <Option value="excel">Excel</Option>
              </Select>
            </Form.Item>
          </Form>
        </Modal>

        {/* Modal de Compartilhamento */}
        <Modal
          title="Compartilhar Relatório"
          open={showShareModal}
          onCancel={() => setShowShareModal(false)}
          onOk={handleShare}
          width={500}
        >
          <Form layout="vertical">
            <Form.Item label="Tornar Público">
              <Switch />
            </Form.Item>
            <Form.Item label="Usuários">
              <Select mode="multiple" placeholder="Selecionar usuários">
                <Option value="user1">Usuário 1</Option>
                <Option value="user2">Usuário 2</Option>
              </Select>
            </Form.Item>
            <Form.Item label="Roles">
              <Select mode="multiple" placeholder="Selecionar roles">
                <Option value="admin">Administrador</Option>
                <Option value="user">Usuário</Option>
                <Option value="viewer">Visualizador</Option>
              </Select>
            </Form.Item>
            <Form.Item label="Permissões">
              <Checkbox.Group options={[
                { label: 'Visualizar', value: 'view' },
                { label: 'Editar', value: 'edit' },
                { label: 'Compartilhar', value: 'share' },
                { label: 'Excluir', value: 'delete' }
              ]} />
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </DndProvider>
  );
}; 