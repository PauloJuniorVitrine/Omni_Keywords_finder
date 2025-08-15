/**
 * ExecucoesDashboard.tsx
 * 
 * Dashboard de monitoramento de execuções em tempo real
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_011
 * Data: 2025-01-27
 * Versão: 1.0
 * 
 * Funcionalidades:
 * - Dashboard de execuções
 * - Status em tempo real
 * - Métricas de performance
 * - Filtros por status/tipo
 * - Integração com APIs do backend
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  IconButton,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Paper,
  Tooltip,
  Alert,
  Skeleton,
  LinearProgress,
  useTheme,
  useMediaQuery,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Pause as PauseIcon,
  Visibility as ViewIcon,
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Timer as TimerIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

// Tipos
interface Execucao {
  id: string;
  nome: string;
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
}

interface ExecucaoLog {
  id: string;
  timestamp: Date;
  nivel: 'info' | 'warning' | 'error' | 'success';
  mensagem: string;
  detalhes?: any;
}

interface ExecucaoMetrics {
  totalExecucoes: number;
  execucoesEmAndamento: number;
  execucoesConcluidas: number;
  execucoesFalharam: number;
  totalKeywordsProcessadas: number;
  totalKeywordsEncontradas: number;
  tempoMedioExecucao: number;
  taxaSucesso: number;
}

interface FilterState {
  search: string;
  status: string;
  nicho: string;
  categoria: string;
  selectedItems: string[];
}

/**
 * Componente de dashboard de execuções
 */
const ExecucoesDashboard: React.FC = () => {
  // Estados
  const [execucoes, setExecucoes] = useState<Execucao[]>([]);
  const [metrics, setMetrics] = useState<ExecucaoMetrics>({
    totalExecucoes: 0,
    execucoesEmAndamento: 0,
    execucoesConcluidas: 0,
    execucoesFalharam: 0,
    totalKeywordsProcessadas: 0,
    totalKeywordsEncontradas: 0,
    tempoMedioExecucao: 0,
    taxaSucesso: 0,
  });
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    status: '',
    nicho: '',
    categoria: '',
    selectedItems: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Hooks
  const theme = useTheme();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Efeitos
  useEffect(() => {
    loadExecucoes();
    loadMetrics();
  }, []);

  useEffect(() => {
    // Auto-refresh para execuções em andamento
    if (autoRefresh) {
      const interval = setInterval(() => {
        if (execucoes.some(exec => exec.status === 'em_andamento')) {
          loadExecucoes();
          loadMetrics();
        }
      }, 5000); // Atualiza a cada 5 segundos

      return () => clearInterval(interval);
    }
  }, [autoRefresh, execucoes]);

  useEffect(() => {
    // Filtrar execuções baseado nos filtros
    filterExecucoes();
  }, [filters]);

  /**
   * Carrega execuções da API
   */
  const loadExecucoes = async () => {
    try {
      setLoading(true);
      // TODO: Implementar chamada real da API
      // const response = await api.get('/execucoes');
      
      // Mock de dados
      const mockExecucoes: Execucao[] = [
        {
          id: '1',
          nome: 'Execução Tecnologia - Lote 1',
          nicho: 'Tecnologia',
          categoria: 'Desenvolvimento Web',
          status: 'em_andamento',
          progresso: 65,
          keywordsProcessadas: 650,
          keywordsEncontradas: 420,
          tempoExecucao: 45,
          tempoEstimado: 70,
          dataInicio: new Date('2025-01-27T10:00:00'),
          dataFim: null,
          logs: [
            {
              id: '1',
              timestamp: new Date('2025-01-27T10:45:00'),
              nivel: 'info',
              mensagem: 'Processando keywords do lote 1',
            },
            {
              id: '2',
              timestamp: new Date('2025-01-27T10:44:00'),
              nivel: 'success',
              mensagem: '650 keywords processadas com sucesso',
            },
          ],
        },
        {
          id: '2',
          nome: 'Execução Saúde - Lote 2',
          nicho: 'Saúde',
          categoria: 'Fitness',
          status: 'concluida',
          progresso: 100,
          keywordsProcessadas: 800,
          keywordsEncontradas: 520,
          tempoExecucao: 75,
          tempoEstimado: 75,
          dataInicio: new Date('2025-01-27T09:00:00'),
          dataFim: new Date('2025-01-27T10:15:00'),
          logs: [
            {
              id: '3',
              timestamp: new Date('2025-01-27T10:15:00'),
              nivel: 'success',
              mensagem: 'Execução concluída com sucesso',
            },
          ],
        },
        {
          id: '3',
          nome: 'Execução Finanças - Lote 3',
          nicho: 'Finanças',
          categoria: 'Investimentos',
          status: 'falhou',
          progresso: 30,
          keywordsProcessadas: 300,
          keywordsEncontradas: 0,
          tempoExecucao: 20,
          tempoEstimado: 60,
          dataInicio: new Date('2025-01-27T08:00:00'),
          dataFim: new Date('2025-01-27T08:20:00'),
          erro: 'Erro de conexão com API externa',
          logs: [
            {
              id: '4',
              timestamp: new Date('2025-01-27T08:20:00'),
              nivel: 'error',
              mensagem: 'Falha na execução: Erro de conexão',
            },
          ],
        },
        {
          id: '4',
          nome: 'Execução Educação - Lote 4',
          nicho: 'Educação',
          categoria: 'Cursos Online',
          status: 'pausada',
          progresso: 40,
          keywordsProcessadas: 400,
          keywordsEncontradas: 250,
          tempoExecucao: 30,
          tempoEstimado: 80,
          dataInicio: new Date('2025-01-27T07:00:00'),
          dataFim: null,
          logs: [
            {
              id: '5',
              timestamp: new Date('2025-01-27T07:30:00'),
              nivel: 'warning',
              mensagem: 'Execução pausada pelo usuário',
            },
          ],
        },
      ];

      setExecucoes(mockExecucoes);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar execuções');
      console.error('Erro ao carregar execuções:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Carrega métricas da API
   */
  const loadMetrics = async () => {
    try {
      // TODO: Implementar chamada real da API
      // const response = await api.get('/execucoes/metrics');
      
      // Mock de métricas
      const mockMetrics: ExecucaoMetrics = {
        totalExecucoes: 45,
        execucoesEmAndamento: 1,
        execucoesConcluidas: 38,
        execucoesFalharam: 6,
        totalKeywordsProcessadas: 12500,
        totalKeywordsEncontradas: 8200,
        tempoMedioExecucao: 72.5,
        taxaSucesso: 84.4,
      };

      setMetrics(mockMetrics);
    } catch (err) {
      console.error('Erro ao carregar métricas:', err);
    }
  };

  /**
   * Filtra execuções baseado nos filtros
   */
  const filterExecucoes = () => {
    let filtered = [...execucoes];

    // Filtro por busca
    if (filters.search) {
      filtered = filtered.filter(exec =>
        exec.nome.toLowerCase().includes(filters.search.toLowerCase()) ||
        exec.nicho.toLowerCase().includes(filters.search.toLowerCase()) ||
        exec.categoria.toLowerCase().includes(filters.search.toLowerCase())
      );
    }

    // Filtro por status
    if (filters.status) {
      filtered = filtered.filter(exec => exec.status === filters.status);
    }

    // Filtro por nicho
    if (filters.nicho) {
      filtered = filtered.filter(exec => exec.nicho === filters.nicho);
    }

    // Filtro por categoria
    if (filters.categoria) {
      filtered = filtered.filter(exec => exec.categoria === filters.categoria);
    }

    setExecucoes(filtered);
  };

  /**
   * Manipula mudança de filtro
   */
  const handleFilterChange = (field: keyof FilterState, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  /**
   * Manipula seleção de item
   */
  const handleItemSelection = (itemId: string) => {
    setFilters(prev => ({
      ...prev,
      selectedItems: prev.selectedItems.includes(itemId)
        ? prev.selectedItems.filter(id => id !== itemId)
        : [...prev.selectedItems, itemId],
    }));
  };

  /**
   * Manipula seleção de todos os itens
   */
  const handleSelectAll = () => {
    if (filters.selectedItems.length === execucoes.length) {
      setFilters(prev => ({ ...prev, selectedItems: [] }));
    } else {
      setFilters(prev => ({ ...prev, selectedItems: execucoes.map(exec => exec.id) }));
    }
  };

  /**
   * Manipula criação de execução
   */
  const handleCreateExecucao = () => {
    navigate('/execucoes/nova');
  };

  /**
   * Manipula visualização de execução
   */
  const handleViewExecucao = (execucaoId: string) => {
    navigate(`/execucoes/${execucaoId}`);
  };

  /**
   * Manipula controle de execução
   */
  const handleControlExecucao = (execucaoId: string, action: 'pause' | 'stop' | 'resume') => {
    console.log(`Controle de execução: ${action}`, execucaoId);
    // TODO: Implementar controles de execução
  };

  /**
   * Renderiza card de métrica
   */
  const renderMetricCard = (title: string, value: number | string, icon: React.ReactNode, color: string, subtitle?: string) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h4" component="div" fontWeight={600} color={color}>
              {typeof value === 'number' ? value.toLocaleString() : value}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {title}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="textSecondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box sx={{ color: color }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  /**
   * Renderiza status com chip colorido
   */
  const renderStatus = (status: string) => {
    const statusConfig = {
      em_andamento: { color: 'info', label: 'Em Andamento', icon: <PlayIcon /> },
      concluida: { color: 'success', label: 'Concluída', icon: <CheckCircleIcon /> },
      falhou: { color: 'error', label: 'Falhou', icon: <ErrorIcon /> },
      cancelada: { color: 'default', label: 'Cancelada', icon: <StopIcon /> },
      pausada: { color: 'warning', label: 'Pausada', icon: <PauseIcon /> },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.em_andamento;

    return (
      <Chip
        icon={config.icon}
        label={config.label}
        color={config.color as any}
        size="small"
        variant="outlined"
      />
    );
  };

  /**
   * Renderiza progresso da execução
   */
  const renderProgress = (execucao: Execucao) => (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="body2" color="textSecondary">
          {execucao.keywordsProcessadas} / {execucao.keywordsEncontradas} keywords
        </Typography>
        <Typography variant="body2" color="textSecondary">
          {execucao.progresso}%
        </Typography>
      </Box>
      <LinearProgress
        variant="determinate"
        value={execucao.progresso}
        sx={{
          height: 8,
          borderRadius: 4,
          backgroundColor: 'grey.200',
          '& .MuiLinearProgress-bar': {
            borderRadius: 4,
          },
        }}
      />
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
        <Typography variant="caption" color="textSecondary">
          {execucao.tempoExecucao} min
        </Typography>
        <Typography variant="caption" color="textSecondary">
          Estimado: {execucao.tempoEstimado} min
        </Typography>
      </Box>
    </Box>
  );

  /**
   * Renderiza execução em card
   */
  const renderExecucaoCard = (execucao: Execucao) => (
    <Card key={execucao.id} sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" gutterBottom>
              {execucao.nome}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
              <Chip label={execucao.nicho} size="small" variant="outlined" />
              <Chip label={execucao.categoria} size="small" variant="outlined" />
              {renderStatus(execucao.status)}
            </Box>
            <Typography variant="body2" color="textSecondary">
              Iniciada em: {execucao.dataInicio.toLocaleString('pt-BR')}
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Visualizar">
              <IconButton
                size="small"
                onClick={() => handleViewExecucao(execucao.id)}
              >
                <ViewIcon />
              </IconButton>
            </Tooltip>
            
            {execucao.status === 'em_andamento' && (
              <>
                <Tooltip title="Pausar">
                  <IconButton
                    size="small"
                    onClick={() => handleControlExecucao(execucao.id, 'pause')}
                  >
                    <PauseIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Parar">
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => handleControlExecucao(execucao.id, 'stop')}
                  >
                    <StopIcon />
                  </IconButton>
                </Tooltip>
              </>
            )}
            
            {execucao.status === 'pausada' && (
              <Tooltip title="Retomar">
                <IconButton
                  size="small"
                  color="primary"
                  onClick={() => handleControlExecucao(execucao.id, 'resume')}
                >
                  <PlayIcon />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        </Box>

        {execucao.status === 'em_andamento' && renderProgress(execucao)}
        
        {execucao.erro && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {execucao.erro}
          </Alert>
        )}

        {/* Logs recentes */}
        {execucao.logs.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Logs Recentes
            </Typography>
            <List dense>
              {execucao.logs.slice(-3).map((log) => (
                <ListItem key={log.id} sx={{ py: 0 }}>
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <Avatar sx={{ width: 16, height: 16, fontSize: '0.75rem' }}>
                      {log.nivel === 'error' ? <ErrorIcon /> : 
                       log.nivel === 'warning' ? <WarningIcon /> :
                       log.nivel === 'success' ? <CheckCircleIcon /> : <ScheduleIcon />}
                    </Avatar>
                  </ListItemIcon>
                  <ListItemText
                    primary={log.mensagem}
                    secondary={log.timestamp.toLocaleTimeString('pt-BR')}
                    primaryTypographyProps={{ variant: 'body2' }}
                    secondaryTypographyProps={{ variant: 'caption' }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" fontWeight={600}>
          Monitoramento de Execuções
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadExecucoes}
          >
            Atualizar
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateExecucao}
          >
            Nova Execução
          </Button>
        </Box>
      </Box>

      {/* Métricas */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          {renderMetricCard(
            'Total Execuções',
            metrics.totalExecucoes,
            <TrendingUpIcon />,
            'primary.main'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          {renderMetricCard(
            'Em Andamento',
            metrics.execucoesEmAndamento,
            <PlayIcon />,
            'info.main'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          {renderMetricCard(
            'Taxa de Sucesso',
            `${metrics.taxaSucesso}%`,
            <CheckCircleIcon />,
            'success.main'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          {renderMetricCard(
            'Tempo Médio',
            `${metrics.tempoMedioExecucao} min`,
            <TimerIcon />,
            'warning.main'
          )}
        </Grid>
      </Grid>

      {/* Filtros */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                placeholder="Buscar execuções..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  label="Status"
                >
                  <MenuItem value="">Todos</MenuItem>
                  <MenuItem value="em_andamento">Em Andamento</MenuItem>
                  <MenuItem value="concluida">Concluída</MenuItem>
                  <MenuItem value="falhou">Falhou</MenuItem>
                  <MenuItem value="pausada">Pausada</MenuItem>
                  <MenuItem value="cancelada">Cancelada</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Nicho</InputLabel>
                <Select
                  value={filters.nicho}
                  onChange={(e) => handleFilterChange('nicho', e.target.value)}
                  label="Nicho"
                >
                  <MenuItem value="">Todos</MenuItem>
                  <MenuItem value="Tecnologia">Tecnologia</MenuItem>
                  <MenuItem value="Saúde">Saúde</MenuItem>
                  <MenuItem value="Finanças">Finanças</MenuItem>
                  <MenuItem value="Educação">Educação</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Categoria</InputLabel>
                <Select
                  value={filters.categoria}
                  onChange={(e) => handleFilterChange('categoria', e.target.value)}
                  label="Categoria"
                >
                  <MenuItem value="">Todas</MenuItem>
                  <MenuItem value="Desenvolvimento Web">Desenvolvimento Web</MenuItem>
                  <MenuItem value="Fitness">Fitness</MenuItem>
                  <MenuItem value="Investimentos">Investimentos</MenuItem>
                  <MenuItem value="Cursos Online">Cursos Online</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={loadExecucoes}
                >
                  Atualizar
                </Button>
                <Button
                  variant={autoRefresh ? 'contained' : 'outlined'}
                  onClick={() => setAutoRefresh(!autoRefresh)}
                >
                  Auto
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Lista de execuções */}
      {error ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      ) : loading ? (
        <Grid container spacing={2}>
          {Array.from({ length: 4 }).map((_, index) => (
            <Grid item xs={12} key={index}>
              <Skeleton variant="rectangular" height={200} />
            </Grid>
          ))}
        </Grid>
      ) : (
        <Box>
          {execucoes.length === 0 ? (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="textSecondary" gutterBottom>
                Nenhuma execução encontrada
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Crie uma nova execução para começar
              </Typography>
            </Paper>
          ) : (
            execucoes.map(execucao => renderExecucaoCard(execucao))
          )}
        </Box>
      )}
    </Box>
  );
};

export default ExecucoesDashboard; 