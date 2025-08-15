/**
 * WorkflowBuilder.tsx
 * 
 * Sistema completo de construtor de workflows
 * 
 * Tracing ID: UI-023
 * Data: 2024-12-20
 * Versão: 1.0
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Button,
  Paper,
  Grid,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Alert,
  CircularProgress,
  Tooltip,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  Badge,
  Avatar,
  CardHeader,
  CardActions,
  AlertTitle,
  Snackbar,
  Drawer,
  ListItemButton,
  ListItemAvatar,
  Fab,
  Zoom,
  Fade
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Stop,
  Refresh,
  Download,
  Visibility,
  Edit,
  Delete,
  Add,
  CheckCircle,
  Error,
  Warning,
  Info,
  Settings,
  Timeline,
  AccountTree,
  Hub,
  CallSplit,
  CallMerge,
  FilterAlt,
  Search,
  Sort,
  MoreVert,
  Notifications,
  Dashboard,
  Analytics,
  Backup,
  Restore,
  Assessment,
  TrendingUp,
  TrendingDown,
  WarningAmber,
  VerifiedUser,
  GppGood,
  GppBad,
  GppMaybe,
  ExpandMore,
  FilterList,
  Check,
  Close,
  Save,
  Cancel,
  DragIndicator,
  Link,
  Unlink,
  Code,
  DataObject,
  Api,
  Storage,
  Cloud,
  Lock,
  Public,
  Domain,
  Apartment,
  Group,
  Person,
  StorageOutlined,
  SpeedOutlined,
  SecurityOutlined,
  BusinessCenter,
  MonetizationOn,
  TimelineOutlined,
  AccountTreeOutlined,
  HubOutlined,
  CallSplitOutlined,
  CallMergeOutlined,
  FilterAltOutlined,
  SearchOutlined,
  SortOutlined,
  MoreVertOutlined,
  NotificationsOutlined,
  DashboardOutlined,
  AnalyticsOutlined,
  BackupOutlined,
  RestoreOutlined,
  AssessmentOutlined,
  TrendingUpOutlined,
  TrendingDownOutlined,
  WarningAmberOutlined,
  VerifiedUserOutlined,
  GppGoodOutlined,
  GppBadOutlined,
  GppMaybeOutlined,
  ExpandMoreOutlined,
  FilterListOutlined,
  CheckOutlined,
  CloseOutlined,
  SaveOutlined,
  CancelOutlined,
  DragIndicatorOutlined,
  LinkOutlined,
  UnlinkOutlined,
  CodeOutlined,
  DataObjectOutlined,
  ApiOutlined,
  StorageOutlined as StorageOutlinedIcon,
  CloudOutlined,
  LockOutlined,
  PublicOutlined,
  DomainOutlined,
  ApartmentOutlined,
  GroupOutlined,
  PersonOutlined,
  StorageOutlined as StorageOutlinedIcon2,
  SpeedOutlined as SpeedOutlinedIcon,
  SecurityOutlined as SecurityOutlinedIcon,
  BusinessCenterOutlined,
  MonetizationOnOutlined,
  TimelineOutlined as TimelineOutlinedIcon,
  AccountTreeOutlined as AccountTreeOutlinedIcon,
  HubOutlined as HubOutlinedIcon,
  CallSplitOutlined as CallSplitOutlinedIcon,
  CallMergeOutlined as CallMergeOutlinedIcon,
  FilterAltOutlined as FilterAltOutlinedIcon,
  SearchOutlined as SearchOutlinedIcon,
  SortOutlined as SortOutlinedIcon,
  MoreVertOutlined as MoreVertOutlinedIcon,
  NotificationsOutlined as NotificationsOutlinedIcon,
  DashboardOutlined as DashboardOutlinedIcon,
  AnalyticsOutlined as AnalyticsOutlinedIcon,
  BackupOutlined as BackupOutlinedIcon,
  RestoreOutlined as RestoreOutlinedIcon,
  AssessmentOutlined as AssessmentOutlinedIcon,
  TrendingUpOutlined as TrendingUpOutlinedIcon,
  TrendingDownOutlined as TrendingDownOutlinedIcon,
  WarningAmberOutlined as WarningAmberOutlinedIcon,
  VerifiedUserOutlined as VerifiedUserOutlinedIcon,
  GppGoodOutlined as GppGoodOutlinedIcon,
  GppBadOutlined as GppBadOutlinedIcon,
  GppMaybeOutlined as GppMaybeOutlinedIcon,
  ExpandMoreOutlined as ExpandMoreOutlinedIcon,
  FilterListOutlined as FilterListOutlinedIcon,
  CheckOutlined as CheckOutlinedIcon,
  CloseOutlined as CloseOutlinedIcon,
  SaveOutlined as SaveOutlinedIcon,
  CancelOutlined as CancelOutlinedIcon,
  DragIndicatorOutlined as DragIndicatorOutlinedIcon,
  LinkOutlined as LinkOutlinedIcon,
  UnlinkOutlined as UnlinkOutlinedIcon,
  CodeOutlined as CodeOutlinedIcon,
  DataObjectOutlined as DataObjectOutlinedIcon,
  ApiOutlined as ApiOutlinedIcon,
  StorageOutlined as StorageOutlinedIcon3,
  CloudOutlined as CloudOutlinedIcon,
  LockOutlined as LockOutlinedIcon,
  PublicOutlined as PublicOutlinedIcon,
  DomainOutlined as DomainOutlinedIcon,
  ApartmentOutlined as ApartmentOutlinedIcon,
  GroupOutlined as GroupOutlinedIcon,
  PersonOutlined as PersonOutlinedIcon
} from '@mui/icons-material';

// Types
interface WorkflowStep {
  id: string;
  name: string;
  type: 'trigger' | 'action' | 'condition' | 'api' | 'data' | 'notification' | 'wait' | 'loop' | 'error';
  position: { x: number; y: number };
  config: {
    [key: string]: any;
  };
  connections: string[];
  status: 'idle' | 'running' | 'completed' | 'error' | 'waiting';
  executionTime?: number;
  lastExecuted?: string;
  errorMessage?: string;
}

interface Workflow {
  id: string;
  name: string;
  description: string;
  version: string;
  status: 'draft' | 'active' | 'paused' | 'archived';
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  steps: WorkflowStep[];
  triggers: string[];
  variables: {
    [key: string]: {
      type: 'string' | 'number' | 'boolean' | 'object';
      value: any;
      description: string;
    };
  };
  settings: {
    timeout: number;
    retryAttempts: number;
    retryDelay: number;
    parallelExecution: boolean;
    errorHandling: 'stop' | 'continue' | 'retry';
  };
  statistics: {
    totalExecutions: number;
    successfulExecutions: number;
    failedExecutions: number;
    avgExecutionTime: number;
    lastExecuted: string;
  };
}

interface WorkflowExecution {
  id: string;
  workflowId: string;
  status: 'running' | 'completed' | 'failed' | 'cancelled';
  startedAt: string;
  completedAt?: string;
  duration?: number;
  steps: {
    stepId: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    startedAt: string;
    completedAt?: string;
    duration?: number;
    result?: any;
    error?: string;
  }[];
  variables: {
    [key: string]: any;
  };
  error?: string;
}

// Mock data
const mockWorkflows: Workflow[] = [
  {
    id: 'workflow_001',
    name: 'Processamento de Keywords',
    description: 'Workflow para processamento automático de keywords',
    version: '1.0.0',
    status: 'active',
    createdAt: '2024-01-15T00:00:00Z',
    updatedAt: '2024-12-20T10:30:00Z',
    createdBy: 'admin@omni.com',
    steps: [
      {
        id: 'step_001',
        name: 'Trigger - Nova Keyword',
        type: 'trigger',
        position: { x: 100, y: 100 },
        config: {
          event: 'keyword.created',
          conditions: {
            source: 'manual',
            priority: 'high'
          }
        },
        connections: ['step_002'],
        status: 'idle'
      },
      {
        id: 'step_002',
        name: 'Validar Keyword',
        type: 'action',
        position: { x: 300, y: 100 },
        config: {
          action: 'validate_keyword',
          parameters: {
            minLength: 3,
            maxLength: 100,
            allowedChars: 'alphanumeric'
          }
        },
        connections: ['step_003'],
        status: 'idle'
      },
      {
        id: 'step_003',
        name: 'Condição - Keyword Válida?',
        type: 'condition',
        position: { x: 500, y: 100 },
        config: {
          condition: 'keyword.isValid',
          trueBranch: 'step_004',
          falseBranch: 'step_005'
        },
        connections: ['step_004', 'step_005'],
        status: 'idle'
      },
      {
        id: 'step_004',
        name: 'Processar Keyword',
        type: 'action',
        position: { x: 700, y: 50 },
        config: {
          action: 'process_keyword',
          parameters: {
            algorithm: 'semantic_analysis',
            includeSynonyms: true
          }
        },
        connections: ['step_006'],
        status: 'idle'
      },
      {
        id: 'step_005',
        name: 'Registrar Erro',
        type: 'action',
        position: { x: 700, y: 150 },
        config: {
          action: 'log_error',
          parameters: {
            level: 'warning',
            message: 'Keyword inválida'
          }
        },
        connections: ['step_006'],
        status: 'idle'
      },
      {
        id: 'step_006',
        name: 'Notificar Conclusão',
        type: 'notification',
        position: { x: 900, y: 100 },
        config: {
          type: 'email',
          template: 'keyword_processed',
          recipients: ['admin@omni.com']
        },
        connections: [],
        status: 'idle'
      }
    ],
    triggers: ['keyword.created'],
    variables: {
      keyword: {
        type: 'string',
        value: '',
        description: 'Keyword a ser processada'
      },
      result: {
        type: 'object',
        value: {},
        description: 'Resultado do processamento'
      }
    },
    settings: {
      timeout: 300,
      retryAttempts: 3,
      retryDelay: 60,
      parallelExecution: false,
      errorHandling: 'stop'
    },
    statistics: {
      totalExecutions: 1250,
      successfulExecutions: 1180,
      failedExecutions: 70,
      avgExecutionTime: 45.2,
      lastExecuted: '2024-12-20T10:25:00Z'
    }
  },
  {
    id: 'workflow_002',
    name: 'Backup Automático',
    description: 'Workflow para backup automático de dados',
    version: '1.0.0',
    status: 'active',
    createdAt: '2024-02-01T00:00:00Z',
    updatedAt: '2024-12-20T09:15:00Z',
    createdBy: 'admin@omni.com',
    steps: [
      {
        id: 'step_007',
        name: 'Trigger - Agendamento',
        type: 'trigger',
        position: { x: 100, y: 100 },
        config: {
          event: 'schedule.daily',
          time: '02:00'
        },
        connections: ['step_008'],
        status: 'idle'
      },
      {
        id: 'step_008',
        name: 'Criar Backup',
        type: 'action',
        position: { x: 300, y: 100 },
        config: {
          action: 'create_backup',
          parameters: {
            type: 'full',
            compression: true
          }
        },
        connections: ['step_009'],
        status: 'idle'
      },
      {
        id: 'step_009',
        name: 'Upload para Cloud',
        type: 'action',
        position: { x: 500, y: 100 },
        config: {
          action: 'upload_to_cloud',
          parameters: {
            provider: 'aws_s3',
            bucket: 'omni-backups'
          }
        },
        connections: ['step_010'],
        status: 'idle'
      },
      {
        id: 'step_010',
        name: 'Notificar Sucesso',
        type: 'notification',
        position: { x: 700, y: 100 },
        config: {
          type: 'email',
          template: 'backup_success',
          recipients: ['admin@omni.com']
        },
        connections: [],
        status: 'idle'
      }
    ],
    triggers: ['schedule.daily'],
    variables: {
      backupPath: {
        type: 'string',
        value: '',
        description: 'Caminho do arquivo de backup'
      },
      cloudUrl: {
        type: 'string',
        value: '',
        description: 'URL do backup na cloud'
      }
    },
    settings: {
      timeout: 1800,
      retryAttempts: 2,
      retryDelay: 300,
      parallelExecution: false,
      errorHandling: 'retry'
    },
    statistics: {
      totalExecutions: 320,
      successfulExecutions: 315,
      failedExecutions: 5,
      avgExecutionTime: 1200.5,
      lastExecuted: '2024-12-20T02:00:00Z'
    }
  }
];

const mockExecutions: WorkflowExecution[] = [
  {
    id: 'exec_001',
    workflowId: 'workflow_001',
    status: 'completed',
    startedAt: '2024-12-20T10:20:00Z',
    completedAt: '2024-12-20T10:21:00Z',
    duration: 60,
    steps: [
      {
        stepId: 'step_001',
        status: 'completed',
        startedAt: '2024-12-20T10:20:00Z',
        completedAt: '2024-12-20T10:20:05Z',
        duration: 5,
        result: { keyword: 'test keyword' }
      },
      {
        stepId: 'step_002',
        status: 'completed',
        startedAt: '2024-12-20T10:20:05Z',
        completedAt: '2024-12-20T10:20:10Z',
        duration: 5,
        result: { isValid: true }
      },
      {
        stepId: 'step_003',
        status: 'completed',
        startedAt: '2024-12-20T10:20:10Z',
        completedAt: '2024-12-20T10:20:12Z',
        duration: 2,
        result: { condition: true }
      },
      {
        stepId: 'step_004',
        status: 'completed',
        startedAt: '2024-12-20T10:20:12Z',
        completedAt: '2024-12-20T10:20:45Z',
        duration: 33,
        result: { processed: true, synonyms: ['test', 'keyword'] }
      },
      {
        stepId: 'step_006',
        status: 'completed',
        startedAt: '2024-12-20T10:20:45Z',
        completedAt: '2024-12-20T10:21:00Z',
        duration: 15,
        result: { sent: true }
      }
    ],
    variables: {
      keyword: 'test keyword',
      result: { processed: true, synonyms: ['test', 'keyword'] }
    }
  }
];

// Step types configuration
const stepTypes = {
  trigger: {
    name: 'Trigger',
    icon: <Timeline />,
    color: '#1976d2',
    description: 'Inicia o workflow baseado em eventos'
  },
  action: {
    name: 'Ação',
    icon: <PlayArrow />,
    color: '#2e7d32',
    description: 'Executa uma ação específica'
  },
  condition: {
    name: 'Condição',
    icon: <CallSplit />,
    color: '#ed6c02',
    description: 'Avalia uma condição e direciona o fluxo'
  },
  api: {
    name: 'API',
    icon: <Api />,
    color: '#9c27b0',
    description: 'Chama uma API externa'
  },
  data: {
    name: 'Dados',
    icon: <DataObject />,
    color: '#0288d1',
    description: 'Manipula dados'
  },
  notification: {
    name: 'Notificação',
    icon: <Notifications />,
    color: '#d32f2f',
    description: 'Envia notificações'
  },
  wait: {
    name: 'Aguardar',
    icon: <Pause />,
    color: '#7b1fa2',
    description: 'Aguarda um tempo específico'
  },
  loop: {
    name: 'Loop',
    icon: <Loop />,
    color: '#388e3c',
    description: 'Repete ações'
  },
  error: {
    name: 'Erro',
    icon: <Error />,
    color: '#d32f2f',
    description: 'Trata erros'
  }
};

// Main Component
const WorkflowBuilder: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [workflows, setWorkflows] = useState<Workflow[]>(mockWorkflows);
  const [executions, setExecutions] = useState<WorkflowExecution[]>(mockExecutions);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [workflowDialog, setWorkflowDialog] = useState(false);
  const [stepDialog, setStepDialog] = useState(false);
  const [selectedStep, setSelectedStep] = useState<WorkflowStep | null>(null);
  const [canvasPosition, setCanvasPosition] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' | 'warning' | 'info' }>({
    open: false,
    message: '',
    severity: 'info'
  });

  // Calculated metrics
  const metrics = useMemo(() => {
    const totalWorkflows = workflows.length;
    const activeWorkflows = workflows.filter(w => w.status === 'active').length;
    const totalExecutions = workflows.reduce((sum, w) => sum + w.statistics.totalExecutions, 0);
    const successRate = workflows.reduce((sum, w) => {
      if (w.statistics.totalExecutions > 0) {
        return sum + (w.statistics.successfulExecutions / w.statistics.totalExecutions);
      }
      return sum;
    }, 0) / totalWorkflows * 100;

    return {
      totalWorkflows,
      activeWorkflows,
      totalExecutions,
      successRate
    };
  }, [workflows]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleWorkflowCreate = () => {
    setSelectedWorkflow(null);
    setWorkflowDialog(true);
  };

  const handleWorkflowEdit = (workflow: Workflow) => {
    setSelectedWorkflow(workflow);
    setWorkflowDialog(true);
  };

  const handleWorkflowSelect = (workflow: Workflow) => {
    setSelectedWorkflow(workflow);
  };

  const handleStepCreate = (type: string) => {
    const newStep: WorkflowStep = {
      id: `step_${Date.now()}`,
      name: `Novo ${stepTypes[type as keyof typeof stepTypes]?.name || 'Step'}`,
      type: type as any,
      position: { x: 100, y: 100 },
      config: {},
      connections: [],
      status: 'idle'
    };
    setSelectedStep(newStep);
    setStepDialog(true);
  };

  const handleStepEdit = (step: WorkflowStep) => {
    setSelectedStep(step);
    setStepDialog(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'draft': return 'default';
      case 'paused': return 'warning';
      case 'archived': return 'error';
      default: return 'default';
    }
  };

  const getExecutionStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'primary';
      case 'failed': return 'error';
      case 'cancelled': return 'warning';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            <AccountTree sx={{ mr: 1, verticalAlign: 'middle' }} />
            Construtor de Workflows
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Crie e gerencie workflows automatizados com interface visual
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<Refresh />}>
          Atualizar
        </Button>
      </Box>

      {/* Metrics Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <AccountTree color="primary" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="h6">{metrics.totalWorkflows}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total de Workflows
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <PlayArrow color="primary" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="h6">{metrics.activeWorkflows}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Workflows Ativos
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Timeline color="primary" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="h6">{metrics.totalExecutions.toLocaleString()}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Execuções Totais
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp color="primary" sx={{ mr: 1 }} />
                <Box>
                  <Typography variant="h6">{metrics.successRate.toFixed(1)}%</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Taxa de Sucesso
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Workflow List */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="Workflows"
              action={
                <Button
                  variant="contained"
                  size="small"
                  startIcon={<Add />}
                  onClick={handleWorkflowCreate}
                >
                  Novo
                </Button>
              }
            />
            <CardContent>
              <List>
                {workflows.map((workflow) => (
                  <ListItem
                    key={workflow.id}
                    button
                    selected={selectedWorkflow?.id === workflow.id}
                    onClick={() => handleWorkflowSelect(workflow)}
                  >
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: stepTypes.trigger.color }}>
                        <AccountTree />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={workflow.name}
                      secondary={
                        <Box>
                          <Typography variant="caption" display="block">
                            {workflow.description}
                          </Typography>
                          <Chip
                            label={workflow.status}
                            color={getStatusColor(workflow.status) as any}
                            size="small"
                            sx={{ mt: 0.5 }}
                          />
                        </Box>
                      }
                    />
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleWorkflowEdit(workflow);
                      }}
                    >
                      <Edit />
                    </IconButton>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Workflow Canvas */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
                <Tab label="Canvas" icon={<AccountTree />} />
                <Tab label="Execuções" icon={<Timeline />} />
                <Tab label="Configurações" icon={<Settings />} />
              </Tabs>

              {/* Canvas Tab */}
              {activeTab === 0 && (
                <Box>
                  {selectedWorkflow ? (
                    <Box>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                        <Typography variant="h6">{selectedWorkflow.name}</Typography>
                        <Box display="flex" gap={1}>
                          <Button variant="outlined" size="small" startIcon={<PlayArrow />}>
                            Executar
                          </Button>
                          <Button variant="outlined" size="small" startIcon={<Pause />}>
                            Pausar
                          </Button>
                          <Button variant="outlined" size="small" startIcon={<Stop />}>
                            Parar
                          </Button>
                        </Box>
                      </Box>

                      {/* Canvas Area */}
                      <Paper
                        sx={{
                          height: 600,
                          position: 'relative',
                          overflow: 'auto',
                          bgcolor: '#f5f5f5',
                          backgroundImage: 'radial-gradient(circle, #ddd 1px, transparent 1px)',
                          backgroundSize: '20px 20px'
                        }}
                      >
                        {/* Workflow Steps */}
                        {selectedWorkflow.steps.map((step) => (
                          <Box
                            key={step.id}
                            sx={{
                              position: 'absolute',
                              left: step.position.x,
                              top: step.position.y,
                              width: 200,
                              height: 80,
                              bgcolor: 'white',
                              border: 2,
                              borderColor: stepTypes[step.type]?.color || '#ccc',
                              borderRadius: 2,
                              p: 1,
                              cursor: 'pointer',
                              '&:hover': {
                                boxShadow: 3,
                                transform: 'scale(1.02)'
                              }
                            }}
                            onClick={() => handleStepEdit(step)}
                          >
                            <Box display="flex" alignItems="center" mb={1}>
                              {stepTypes[step.type]?.icon}
                              <Typography variant="body2" fontWeight="bold" ml={1}>
                                {step.name}
                              </Typography>
                            </Box>
                            <Typography variant="caption" color="text.secondary">
                              {stepTypes[step.type]?.description}
                            </Typography>
                            <Chip
                              label={step.status}
                              size="small"
                              color={getStatusColor(step.status) as any}
                              sx={{ position: 'absolute', top: 4, right: 4 }}
                            />
                          </Box>
                        ))}

                        {/* Connections */}
                        {selectedWorkflow.steps.map((step) =>
                          step.connections.map((connectionId, index) => {
                            const targetStep = selectedWorkflow.steps.find(s => s.id === connectionId);
                            if (!targetStep) return null;

                            return (
                              <svg
                                key={`${step.id}-${connectionId}`}
                                style={{
                                  position: 'absolute',
                                  top: 0,
                                  left: 0,
                                  width: '100%',
                                  height: '100%',
                                  pointerEvents: 'none',
                                  zIndex: 1
                                }}
                              >
                                <line
                                  x1={step.position.x + 200}
                                  y1={step.position.y + 40}
                                  x2={targetStep.position.x}
                                  y2={targetStep.position.y + 40}
                                  stroke="#666"
                                  strokeWidth="2"
                                  markerEnd="url(#arrowhead)"
                                />
                                <defs>
                                  <marker
                                    id="arrowhead"
                                    markerWidth="10"
                                    markerHeight="7"
                                    refX="9"
                                    refY="3.5"
                                    orient="auto"
                                  >
                                    <polygon points="0 0, 10 3.5, 0 7" fill="#666" />
                                  </marker>
                                </defs>
                              </svg>
                            );
                          })
                        )}
                      </Paper>

                      {/* Step Palette */}
                      <Box mt={2}>
                        <Typography variant="subtitle2" gutterBottom>
                          Adicionar Step:
                        </Typography>
                        <Box display="flex" gap={1} flexWrap="wrap">
                          {Object.entries(stepTypes).map(([type, config]) => (
                            <Button
                              key={type}
                              variant="outlined"
                              size="small"
                              startIcon={config.icon}
                              onClick={() => handleStepCreate(type)}
                              sx={{ borderColor: config.color, color: config.color }}
                            >
                              {config.name}
                            </Button>
                          ))}
                        </Box>
                      </Box>
                    </Box>
                  ) : (
                    <Box
                      display="flex"
                      flexDirection="column"
                      alignItems="center"
                      justifyContent="center"
                      height={600}
                      color="text.secondary"
                    >
                      <AccountTree sx={{ fontSize: 64, mb: 2 }} />
                      <Typography variant="h6" gutterBottom>
                        Selecione um Workflow
                      </Typography>
                      <Typography variant="body2">
                        Escolha um workflow da lista para visualizar e editar
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}

              {/* Executions Tab */}
              {activeTab === 1 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Execuções Recentes
                  </Typography>
                  
                  <TableContainer component={Paper}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>ID</TableCell>
                          <TableCell>Workflow</TableCell>
                          <TableCell>Status</TableCell>
                          <TableCell>Início</TableCell>
                          <TableCell>Duração</TableCell>
                          <TableCell>Ações</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {executions.map((execution) => {
                          const workflow = workflows.find(w => w.id === execution.workflowId);
                          return (
                            <TableRow key={execution.id}>
                              <TableCell>{execution.id}</TableCell>
                              <TableCell>{workflow?.name}</TableCell>
                              <TableCell>
                                <Chip
                                  label={execution.status}
                                  color={getExecutionStatusColor(execution.status) as any}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell>
                                {new Date(execution.startedAt).toLocaleString('pt-BR')}
                              </TableCell>
                              <TableCell>
                                {execution.duration ? `${execution.duration}s` : '-'}
                              </TableCell>
                              <TableCell>
                                <Box display="flex" gap={1}>
                                  <Tooltip title="Ver detalhes">
                                    <IconButton size="small">
                                      <Visibility />
                                    </IconButton>
                                  </Tooltip>
                                  <Tooltip title="Reexecutar">
                                    <IconButton size="small">
                                      <Refresh />
                                    </IconButton>
                                  </Tooltip>
                                </Box>
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}

              {/* Settings Tab */}
              {activeTab === 2 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Configurações do Workflow
                  </Typography>
                  
                  {selectedWorkflow ? (
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                        <Card>
                          <CardHeader title="Configurações Gerais" />
                          <CardContent>
                            <TextField
                              fullWidth
                              label="Nome"
                              defaultValue={selectedWorkflow.name}
                              sx={{ mb: 2 }}
                            />
                            <TextField
                              fullWidth
                              label="Descrição"
                              multiline
                              rows={3}
                              defaultValue={selectedWorkflow.description}
                              sx={{ mb: 2 }}
                            />
                            <FormControl fullWidth sx={{ mb: 2 }}>
                              <InputLabel>Status</InputLabel>
                              <Select defaultValue={selectedWorkflow.status}>
                                <MenuItem value="draft">Rascunho</MenuItem>
                                <MenuItem value="active">Ativo</MenuItem>
                                <MenuItem value="paused">Pausado</MenuItem>
                                <MenuItem value="archived">Arquivado</MenuItem>
                              </Select>
                            </FormControl>
                          </CardContent>
                        </Card>
                      </Grid>
                      
                      <Grid item xs={12} md={6}>
                        <Card>
                          <CardHeader title="Configurações de Execução" />
                          <CardContent>
                            <TextField
                              fullWidth
                              label="Timeout (segundos)"
                              type="number"
                              defaultValue={selectedWorkflow.settings.timeout}
                              sx={{ mb: 2 }}
                            />
                            <TextField
                              fullWidth
                              label="Tentativas de Retry"
                              type="number"
                              defaultValue={selectedWorkflow.settings.retryAttempts}
                              sx={{ mb: 2 }}
                            />
                            <TextField
                              fullWidth
                              label="Delay entre Retries (segundos)"
                              type="number"
                              defaultValue={selectedWorkflow.settings.retryDelay}
                              sx={{ mb: 2 }}
                            />
                            <FormControlLabel
                              control={<Switch defaultChecked={selectedWorkflow.settings.parallelExecution} />}
                              label="Execução Paralela"
                            />
                          </CardContent>
                        </Card>
                      </Grid>
                    </Grid>
                  ) : (
                    <Alert severity="info">
                      Selecione um workflow para ver suas configurações
                    </Alert>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Workflow Dialog */}
      <Dialog open={workflowDialog} onClose={() => setWorkflowDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedWorkflow ? 'Editar Workflow' : 'Novo Workflow'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Nome do Workflow"
                defaultValue={selectedWorkflow?.name}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Descrição"
                multiline
                rows={3}
                defaultValue={selectedWorkflow?.description}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select defaultValue={selectedWorkflow?.status || 'draft'}>
                  <MenuItem value="draft">Rascunho</MenuItem>
                  <MenuItem value="active">Ativo</MenuItem>
                  <MenuItem value="paused">Pausado</MenuItem>
                  <MenuItem value="archived">Arquivado</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Versão"
                defaultValue={selectedWorkflow?.version || '1.0.0'}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setWorkflowDialog(false)}>Cancelar</Button>
          <Button 
            variant="contained"
            onClick={() => {
              setSnackbar({
                open: true,
                message: selectedWorkflow ? 'Workflow atualizado com sucesso' : 'Workflow criado com sucesso',
                severity: 'success'
              });
              setWorkflowDialog(false);
              setSelectedWorkflow(null);
            }}
          >
            {selectedWorkflow ? 'Atualizar' : 'Criar'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Step Dialog */}
      <Dialog open={stepDialog} onClose={() => setStepDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedStep ? 'Editar Step' : 'Novo Step'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Nome do Step"
                defaultValue={selectedStep?.name}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Tipo</InputLabel>
                <Select defaultValue={selectedStep?.type}>
                  {Object.entries(stepTypes).map(([type, config]) => (
                    <MenuItem key={type} value={type}>
                      <Box display="flex" alignItems="center">
                        {config.icon}
                        <Typography ml={1}>{config.name}</Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Configuração (JSON)"
                multiline
                rows={4}
                defaultValue={JSON.stringify(selectedStep?.config || {}, null, 2)}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStepDialog(false)}>Cancelar</Button>
          <Button 
            variant="contained"
            onClick={() => {
              setSnackbar({
                open: true,
                message: selectedStep ? 'Step atualizado com sucesso' : 'Step criado com sucesso',
                severity: 'success'
              });
              setStepDialog(false);
              setSelectedStep(null);
            }}
          >
            {selectedStep ? 'Atualizar' : 'Criar'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Speed Dial */}
      <SpeedDial
        ariaLabel="Ações rápidas"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        icon={<SpeedDialIcon />}
      >
        <SpeedDialAction
          icon={<Add />}
          tooltipTitle="Novo workflow"
          onClick={handleWorkflowCreate}
        />
        <SpeedDialAction
          icon={<PlayArrow />}
          tooltipTitle="Executar todos"
          onClick={() => {
            setSnackbar({
              open: true,
              message: 'Execução em lote iniciada',
              severity: 'success'
            });
          }}
        />
        <SpeedDialAction
          icon={<Assessment />}
          tooltipTitle="Relatório"
          onClick={() => {
            setSnackbar({
              open: true,
              message: 'Relatório gerado com sucesso',
              severity: 'success'
            });
          }}
        />
      </SpeedDial>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default WorkflowBuilder; 