/**
 * ExecucaoDetails.tsx
 * 
 * Página de detalhes de uma execução específica
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_014
 * Data: 2025-01-27
 * Versão: 1.0
 * 
 * Funcionalidades:
 * - Detalhes da execução
 * - Logs completos
 * - Resultados
 * - Ações de controle
 * - Métricas em tempo real
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Button,
  Chip,
  IconButton,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  Skeleton,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  useTheme,
  useMediaQuery,
  Tooltip,
  Badge,
  Avatar,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Pause as PauseIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Settings as SettingsIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Schedule as ScheduleIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Timer as TimerIcon,
  TrendingUp as TrendingUpIcon,
  Visibility as ViewIcon,
  FileDownload as FileDownloadIcon,
  CloudDownload as CloudDownloadIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  BugReport as BugReportIcon,
} from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';

// Tipos
interface Execucao {
  id: string;
  nome: string;
  descricao: string;
  nicho: string;
  categoria: string;
  status: 'em_andamento' | 'concluida' | 'falhou' | 'cancelada' | 'pausada';
  progresso: number;
  keywordsProcessadas: number;
  keywordsEncontradas: number;
  tempoExecucao: number;
  tempoEstimado: number;
  dataInicio: Date;
  dataFim: Date | null;
  erro?: string;
  logs: ExecucaoLog[];
  resultados: ExecucaoResultado[];
  metricas: ExecucaoMetricas;
}

interface ExecucaoLog {
  id: string;
  timestamp: Date;
  nivel: 'info' | 'warning' | 'error' | 'success';
  mensagem: string;
  detalhes?: any;
}

interface ExecucaoResultado {
  id: string;
  keyword: string;
  volume: number;
  dificuldade: number;
  cpc: number;
  posicao: number;
  url: string;
  titulo: string;
  descricao: string;
  dataEncontrada: Date;
}

interface ExecucaoMetricas {
  totalKeywords: number;
  keywordsProcessadas: number;
  keywordsEncontradas: number;
  taxaSucesso: number;
  tempoMedioPorKeyword: number;
  erros: number;
  warnings: number;
  usoMemoria: number;
  usoCPU: number;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

/**
 * Componente de painel de abas
 */
function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`execucao-tabpanel-${index}`}
      aria-labelledby={`execucao-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

/**
 * Componente de detalhes da execução
 */
const ExecucaoDetails: React.FC = () => {
  // Estados
  const [execucao, setExecucao] = useState<Execucao | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [filteredLogs, setFilteredLogs] = useState<ExecucaoLog[]>([]);
  const [logFilter, setLogFilter] = useState<string>('all');

  // Hooks
  const theme = useTheme();
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Efeitos
  useEffect(() => {
    if (id) {
      loadExecucao(id);
    }
  }, [id]);

  useEffect(() => {
    // Auto-refresh para execuções em andamento
    if (autoRefresh && execucao?.status === 'em_andamento') {
      const interval = setInterval(() => {
        if (id) {
          loadExecucao(id);
        }
      }, 5000); // Atualiza a cada 5 segundos

      return () => clearInterval(interval);
    }
  }, [autoRefresh, execucao?.status, id]);

  useEffect(() => {
    // Filtrar logs
    if (execucao) {
      let filtered = [...execucao.logs];
      
      if (logFilter !== 'all') {
        filtered = filtered.filter(log => log.nivel === logFilter);
      }
      
      setFilteredLogs(filtered);
    }
  }, [execucao, logFilter]);

  /**
   * Carrega execução da API
   */
  const loadExecucao = async (execucaoId: string) => {
    try {
      setLoading(true);
      // TODO: Implementar chamada real da API
      // const response = await api.get(`/execucoes/${execucaoId}`);
      
      // Mock de dados
      const mockExecucao: Execucao = {
        id: execucaoId,
        nome: 'Execução Tecnologia - Lote 1',
        descricao: 'Execução completa para nicho de tecnologia',
        nicho: 'Tecnologia',
        categoria: 'Desenvolvimento Web',
        status: 'em_andamento',
        progresso: 75,
        keywordsProcessadas: 750,
        keywordsEncontradas: 520,
        tempoExecucao: 65,
        tempoEstimado: 90,
        dataInicio: new Date('2025-01-27T10:00:00'),
        dataFim: null,
        logs: [
          {
            id: '1',
            timestamp: new Date('2025-01-27T10:00:00'),
            nivel: 'info',
            mensagem: 'Iniciando execução',
          },
          {
            id: '2',
            timestamp: new Date('2025-01-27T10:05:00'),
            nivel: 'success',
            mensagem: 'Configuração carregada com sucesso',
          },
          {
            id: '3',
            timestamp: new Date('2025-01-27T10:10:00'),
            nivel: 'info',
            mensagem: 'Processando keywords do lote 1',
          },
          {
            id: '4',
            timestamp: new Date('2025-01-27T10:15:00'),
            nivel: 'warning',
            mensagem: 'Taxa de requisições alta, aguardando...',
          },
          {
            id: '5',
            timestamp: new Date('2025-01-27T10:20:00'),
            nivel: 'success',
            mensagem: '750 keywords processadas com sucesso',
          },
        ],
        resultados: [
          {
            id: '1',
            keyword: 'react development',
            volume: 12000,
            dificuldade: 45,
            cpc: 2.50,
            posicao: 1,
            url: 'https://example.com/react',
            titulo: 'React Development Guide',
            descricao: 'Complete guide to React development',
            dataEncontrada: new Date('2025-01-27T10:05:00'),
          },
          {
            id: '2',
            keyword: 'typescript tutorial',
            volume: 8500,
            dificuldade: 38,
            cpc: 1.80,
            posicao: 2,
            url: 'https://example.com/typescript',
            titulo: 'TypeScript Tutorial',
            descricao: 'Learn TypeScript from scratch',
            dataEncontrada: new Date('2025-01-27T10:08:00'),
          },
        ],
        metricas: {
          totalKeywords: 1000,
          keywordsProcessadas: 750,
          keywordsEncontradas: 520,
          taxaSucesso: 69.3,
          tempoMedioPorKeyword: 5.2,
          erros: 2,
          warnings: 5,
          usoMemoria: 45.2,
          usoCPU: 67.8,
        },
      };

      setExecucao(mockExecucao);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar execução');
      console.error('Erro ao carregar execução:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Manipula controle da execução
   */
  const handleControlAction = async (action: 'pause' | 'stop' | 'resume') => {
    if (!execucao) return;

    try {
      // TODO: Implementar chamada real da API
      // await api.post(`/execucoes/${execucao.id}/${action}`);
      
      console.log(`${action} execução:`, execucao.id);
      
      // Recarregar dados
      if (id) {
        loadExecucao(id);
      }
    } catch (err) {
      console.error(`Erro ao ${action} execução:`, err);
    }
  };

  /**
   * Manipula exclusão da execução
   */
  const handleDelete = async () => {
    if (!execucao) return;

    try {
      // TODO: Implementar chamada real da API
      // await api.delete(`/execucoes/${execucao.id}`);
      
      console.log('Excluir execução:', execucao.id);
      navigate('/execucoes');
    } catch (err) {
      console.error('Erro ao excluir execução:', err);
    }
  };

  /**
   * Exporta resultados
   */
  const handleExport = (format: 'csv' | 'json' | 'excel') => {
    if (!execucao) return;

    console.log(`Exportar ${format}:`, execucao.id);
    // TODO: Implementar exportação
  };

  /**
   * Renderiza status da execução
   */
  const renderStatus = (status: string) => {
    const statusConfig = {
      em_andamento: {
        color: 'primary',
        icon: <PlayIcon />,
        label: 'Em Andamento'
      },
      concluida: {
        color: 'success',
        icon: <CheckCircleIcon />,
        label: 'Concluída'
      },
      falhou: {
        color: 'error',
        icon: <ErrorIcon />,
        label: 'Falhou'
      },
      cancelada: {
        color: 'default',
        icon: <StopIcon />,
        label: 'Cancelada'
      },
      pausada: {
        color: 'warning',
        icon: <PauseIcon />,
        label: 'Pausada'
      }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.em_andamento;

    return (
      <Chip
        icon={config.icon}
        label={config.label}
        color={config.color as any}
        size="medium"
        variant="outlined"
      />
    );
  };

  /**
   * Renderiza métricas
   */
  const renderMetricCard = (title: string, value: string | number, icon: React.ReactNode, color: string, subtitle?: string) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar sx={{ bgcolor: color, width: 48, height: 48 }}>
            {icon}
          </Avatar>
          <Box>
            <Typography variant="h6" component="div">
              {value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {title}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  /**
   * Renderiza timeline de logs
   */
  const renderLogsTimeline = () => (
    <Timeline>
      {filteredLogs.map((log) => (
        <TimelineItem key={log.id}>
          <TimelineOppositeContent sx={{ m: 'auto 0' }} variant="body2" color="text.secondary">
            {log.timestamp.toLocaleTimeString()}
          </TimelineOppositeContent>
          <TimelineSeparator>
            <TimelineDot color={log.nivel as any}>
              {log.nivel === 'info' && <InfoIcon />}
              {log.nivel === 'success' && <CheckCircleIcon />}
              {log.nivel === 'warning' && <WarningIcon />}
              {log.nivel === 'error' && <ErrorIcon />}
            </TimelineDot>
            <TimelineConnector />
          </TimelineSeparator>
          <TimelineContent sx={{ py: '12px', px: 2 }}>
            <Typography variant="body2" component="span">
              {log.mensagem}
            </Typography>
            {log.detalhes && (
              <Typography variant="caption" display="block" color="text.secondary">
                {JSON.stringify(log.detalhes)}
              </Typography>
            )}
          </TimelineContent>
        </TimelineItem>
      ))}
    </Timeline>
  );

  /**
   * Renderiza resultados
   */
  const renderResultados = () => (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Keyword</TableCell>
            <TableCell align="right">Volume</TableCell>
            <TableCell align="right">Dificuldade</TableCell>
            <TableCell align="right">CPC</TableCell>
            <TableCell align="right">Posição</TableCell>
            <TableCell>URL</TableCell>
            <TableCell>Data</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {execucao?.resultados.map((resultado) => (
            <TableRow key={resultado.id} hover>
              <TableCell>
                <Typography variant="body2" fontWeight="medium">
                  {resultado.keyword}
                </Typography>
              </TableCell>
              <TableCell align="right">
                <Chip
                  label={resultado.volume.toLocaleString()}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              </TableCell>
              <TableCell align="right">
                <Chip
                  label={`${resultado.dificuldade}%`}
                  size="small"
                  color={resultado.dificuldade > 70 ? 'error' : resultado.dificuldade > 40 ? 'warning' : 'success'}
                  variant="outlined"
                />
              </TableCell>
              <TableCell align="right">
                <Typography variant="body2">
                  ${resultado.cpc.toFixed(2)}
                </Typography>
              </TableCell>
              <TableCell align="right">
                <Chip
                  label={resultado.posicao}
                  size="small"
                  color={resultado.posicao <= 3 ? 'success' : resultado.posicao <= 10 ? 'warning' : 'default'}
                  variant="outlined"
                />
              </TableCell>
              <TableCell>
                <Tooltip title={resultado.url}>
                  <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                    {resultado.url}
                  </Typography>
                </Tooltip>
              </TableCell>
              <TableCell>
                <Typography variant="body2">
                  {resultado.dataEncontrada.toLocaleString()}
                </Typography>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );

  if (loading) {
    return (
      <Box>
        <Skeleton variant="rectangular" height={400} />
      </Box>
    );
  }

  if (error || !execucao) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error || 'Execução não encontrada'}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <IconButton onClick={() => navigate('/execucoes')}>
          <ArrowBackIcon />
        </IconButton>
        
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h4" gutterBottom>
            {execucao.nome}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {execucao.descricao}
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', gap: 1 }}>
          {execucao.status === 'em_andamento' && (
            <>
              <Tooltip title="Pausar">
                <IconButton
                  onClick={() => handleControlAction('pause')}
                  color="warning"
                >
                  <PauseIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Parar">
                <IconButton
                  onClick={() => handleControlAction('stop')}
                  color="error"
                >
                  <StopIcon />
                </IconButton>
              </Tooltip>
            </>
          )}

          {execucao.status === 'pausada' && (
            <Tooltip title="Retomar">
              <IconButton
                onClick={() => handleControlAction('resume')}
                color="primary"
              >
                <PlayIcon />
              </IconButton>
            </Tooltip>
          )}

          <Tooltip title="Atualizar">
            <IconButton onClick={() => id && loadExecucao(id)}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Editar">
            <IconButton onClick={() => navigate(`/execucoes/${execucao.id}/editar`)}>
              <EditIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Excluir">
            <IconButton
              onClick={() => setShowDeleteDialog(true)}
              color="error"
            >
              <DeleteIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Status e Progresso */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              {renderStatus(execucao.status)}
              <Typography variant="h6">
                {execucao.progresso}% Concluído
              </Typography>
            </Box>
            
            <LinearProgress
              variant="determinate"
              value={execucao.progresso}
              sx={{ height: 8, borderRadius: 4 }}
            />
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
              <Typography variant="body2" color="text.secondary">
                {execucao.keywordsProcessadas} processadas
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {execucao.keywordsEncontradas} encontradas
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Tempo de Execução
                </Typography>
                <Typography variant="h6">
                  {execucao.tempoExecucao}min
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Tempo Estimado
                </Typography>
                <Typography variant="h6">
                  {execucao.tempoEstimado}min
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Nicho
                </Typography>
                <Typography variant="h6">
                  {execucao.nicho}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Categoria
                </Typography>
                <Typography variant="h6">
                  {execucao.categoria}
                </Typography>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </Paper>

      {/* Métricas */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          {renderMetricCard(
            'Taxa de Sucesso',
            `${execucao.metricas.taxaSucesso}%`,
            <TrendingUpIcon />,
            'success'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          {renderMetricCard(
            'Tempo Médio',
            `${execucao.metricas.tempoMedioPorKeyword}s`,
            <TimerIcon />,
            'info'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          {renderMetricCard(
            'Uso de Memória',
            `${execucao.metricas.usoMemoria}%`,
            <MemoryIcon />,
            'warning'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          {renderMetricCard(
            'Uso de CPU',
            `${execucao.metricas.usoCPU}%`,
            <SpeedIcon />,
            'error'
          )}
        </Grid>
      </Grid>

      {/* Abas */}
      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          variant={isMobile ? 'scrollable' : 'fullWidth'}
          scrollButtons={isMobile ? 'auto' : false}
        >
          <Tab label="Visão Geral" icon={<ViewIcon />} />
          <Tab label="Logs" icon={<BugReportIcon />} />
          <Tab label="Resultados" icon={<AssessmentIcon />} />
          <Tab label="Timeline" icon={<TimelineIcon />} />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader title="Informações da Execução" />
                <CardContent>
                  <List>
                    <ListItem>
                      <ListItemText
                        primary="Data de Início"
                        secondary={execucao.dataInicio.toLocaleString()}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Data de Fim"
                        secondary={execucao.dataFim ? execucao.dataFim.toLocaleString() : 'Em andamento'}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Total de Keywords"
                        secondary={execucao.metricas.totalKeywords}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Keywords Processadas"
                        secondary={execucao.metricas.keywordsProcessadas}
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardHeader title="Ações Rápidas" />
                <CardContent>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Button
                      variant="outlined"
                      startIcon={<DownloadIcon />}
                      onClick={() => handleExport('csv')}
                    >
                      Exportar CSV
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<DownloadIcon />}
                      onClick={() => handleExport('json')}
                    >
                      Exportar JSON
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<ShareIcon />}
                    >
                      Compartilhar
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ mb: 2 }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Filtrar Logs</InputLabel>
              <Select
                value={logFilter}
                onChange={(e) => setLogFilter(e.target.value)}
                label="Filtrar Logs"
              >
                <MenuItem value="all">Todos</MenuItem>
                <MenuItem value="info">Info</MenuItem>
                <MenuItem value="success">Sucesso</MenuItem>
                <MenuItem value="warning">Aviso</MenuItem>
                <MenuItem value="error">Erro</MenuItem>
              </Select>
            </FormControl>
          </Box>

          <List>
            {filteredLogs.map((log) => (
              <ListItem key={log.id}>
                <ListItemIcon>
                  {log.nivel === 'info' && <InfoIcon color="info" />}
                  {log.nivel === 'success' && <CheckCircleIcon color="success" />}
                  {log.nivel === 'warning' && <WarningIcon color="warning" />}
                  {log.nivel === 'error' && <ErrorIcon color="error" />}
                </ListItemIcon>
                <ListItemText
                  primary={log.mensagem}
                  secondary={log.timestamp.toLocaleString()}
                />
              </ListItem>
            ))}
          </List>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          {renderResultados()}
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          {renderLogsTimeline()}
        </TabPanel>
      </Paper>

      {/* Dialog de confirmação de exclusão */}
      <Dialog open={showDeleteDialog} onClose={() => setShowDeleteDialog(false)}>
        <DialogTitle>Confirmar Exclusão</DialogTitle>
        <DialogContent>
          <Typography>
            Tem certeza que deseja excluir esta execução? Esta ação não pode ser desfeita.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDeleteDialog(false)}>
            Cancelar
          </Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Excluir
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ExecucaoDetails; 