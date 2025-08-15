/**
 * ExecucoesTable.tsx
 * 
 * Tabela de execuções com status visual e ações em tempo real
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_012
 * Data: 2025-01-27
 * Versão: 1.0
 * 
 * Funcionalidades:
 * - Tabela com status visual
 * - Filtros avançados
 * - Ações por execução
 * - Logs em tempo real
 * - Integração com APIs do backend
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  IconButton,
  Chip,
  LinearProgress,
  Tooltip,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Checkbox,
  Button,
  Menu,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  Alert,
  Skeleton,
  useTheme,
  useMediaQuery,
  Collapse,
  Card,
  CardContent,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Pause as PauseIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  MoreVert as MoreIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Schedule as ScheduleIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Timer as TimerIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
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

interface FilterState {
  search: string;
  status: string;
  nicho: string;
  categoria: string;
  dataInicio: string;
  dataFim: string;
  selectedItems: string[];
}

type SortField = 'nome' | 'status' | 'dataInicio' | 'tempoExecucao' | 'progresso';
type SortOrder = 'asc' | 'desc';

/**
 * Componente de tabela de execuções
 */
const ExecucoesTable: React.FC = () => {
  // Estados
  const [execucoes, setExecucoes] = useState<Execucao[]>([]);
  const [filteredExecucoes, setFilteredExecucoes] = useState<Execucao[]>([]);
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    status: '',
    nicho: '',
    categoria: '',
    dataInicio: '',
    dataFim: '',
    selectedItems: [],
  });
  const [sortField, setSortField] = useState<SortField>('dataInicio');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedRows, setExpandedRows] = useState<string[]>([]);
  const [actionMenuAnchor, setActionMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedExecucao, setSelectedExecucao] = useState<Execucao | null>(null);

  // Hooks
  const theme = useTheme();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Efeitos
  useEffect(() => {
    loadExecucoes();
  }, []);

  useEffect(() => {
    filterAndSortExecucoes();
  }, [execucoes, filters, sortField, sortOrder]);

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
              timestamp: new Date('2025-01-27T10:46:00'),
              nivel: 'success',
              mensagem: '650 keywords processadas com sucesso',
            },
          ],
        },
        {
          id: '2',
          nome: 'Execução Saúde - Lote 2',
          nicho: 'Saúde e Bem-estar',
          categoria: 'Fitness',
          status: 'concluida',
          progresso: 100,
          keywordsProcessadas: 890,
          keywordsEncontradas: 720,
          tempoExecucao: 120,
          tempoEstimado: 120,
          dataInicio: new Date('2025-01-27T08:00:00'),
          dataFim: new Date('2025-01-27T10:00:00'),
          logs: [
            {
              id: '3',
              timestamp: new Date('2025-01-27T10:00:00'),
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
          progresso: 35,
          keywordsProcessadas: 350,
          keywordsEncontradas: 0,
          tempoExecucao: 25,
          tempoEstimado: 90,
          dataInicio: new Date('2025-01-27T09:00:00'),
          dataFim: new Date('2025-01-27T09:25:00'),
          erro: 'Erro de conexão com API externa',
          logs: [
            {
              id: '4',
              timestamp: new Date('2025-01-27T09:25:00'),
              nivel: 'error',
              mensagem: 'Falha na conexão com API externa',
            },
          ],
        },
        {
          id: '4',
          nome: 'Execução Educação - Lote 4',
          nicho: 'Educação',
          categoria: 'Cursos Online',
          status: 'pausada',
          progresso: 45,
          keywordsProcessadas: 450,
          keywordsEncontradas: 280,
          tempoExecucao: 30,
          tempoEstimado: 60,
          dataInicio: new Date('2025-01-27T11:00:00'),
          dataFim: null,
          logs: [
            {
              id: '5',
              timestamp: new Date('2025-01-27T11:30:00'),
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
   * Filtra e ordena execuções
   */
  const filterAndSortExecucoes = () => {
    let filtered = [...execucoes];

    // Aplicar filtros
    if (filters.search) {
      filtered = filtered.filter(exec =>
        exec.nome.toLowerCase().includes(filters.search.toLowerCase()) ||
        exec.nicho.toLowerCase().includes(filters.search.toLowerCase()) ||
        exec.categoria.toLowerCase().includes(filters.search.toLowerCase())
      );
    }

    if (filters.status) {
      filtered = filtered.filter(exec => exec.status === filters.status);
    }

    if (filters.nicho) {
      filtered = filtered.filter(exec => exec.nicho === filters.nicho);
    }

    if (filters.categoria) {
      filtered = filtered.filter(exec => exec.categoria === filters.categoria);
    }

    if (filters.dataInicio) {
      filtered = filtered.filter(exec => 
        exec.dataInicio >= new Date(filters.dataInicio)
      );
    }

    if (filters.dataFim) {
      filtered = filtered.filter(exec => 
        exec.dataFim ? exec.dataFim <= new Date(filters.dataFim) : true
      );
    }

    // Aplicar ordenação
    filtered.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortField) {
        case 'nome':
          aValue = a.nome;
          bValue = b.nome;
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        case 'dataInicio':
          aValue = a.dataInicio;
          bValue = b.dataInicio;
          break;
        case 'tempoExecucao':
          aValue = a.tempoExecucao;
          bValue = b.tempoExecucao;
          break;
        case 'progresso':
          aValue = a.progresso;
          bValue = b.progresso;
          break;
        default:
          aValue = a.dataInicio;
          bValue = b.dataInicio;
      }

      if (aValue < bValue) {
        return sortOrder === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortOrder === 'asc' ? 1 : -1;
      }
      return 0;
    });

    setFilteredExecucoes(filtered);
  };

  /**
   * Manipula mudança de filtros
   */
  const handleFilterChange = (field: keyof FilterState, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  /**
   * Manipula seleção de itens
   */
  const handleItemSelection = (itemId: string) => {
    setFilters(prev => ({
      ...prev,
      selectedItems: prev.selectedItems.includes(itemId)
        ? prev.selectedItems.filter(id => id !== itemId)
        : [...prev.selectedItems, itemId]
    }));
  };

  /**
   * Manipula seleção de todos os itens
   */
  const handleSelectAll = () => {
    const currentPageItems = filteredExecucoes.slice(
      page * rowsPerPage,
      page * rowsPerPage + rowsPerPage
    );
    
    if (filters.selectedItems.length === currentPageItems.length) {
      setFilters(prev => ({ ...prev, selectedItems: [] }));
    } else {
      setFilters(prev => ({
        ...prev,
        selectedItems: currentPageItems.map(item => item.id)
      }));
    }
  };

  /**
   * Manipula ordenação
   */
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  /**
   * Manipula expansão de linha
   */
  const handleRowExpand = (execucaoId: string) => {
    setExpandedRows(prev =>
      prev.includes(execucaoId)
        ? prev.filter(id => id !== execucaoId)
        : [...prev, execucaoId]
    );
  };

  /**
   * Manipula menu de ações
   */
  const handleActionMenuOpen = (event: React.MouseEvent<HTMLElement>, execucao: Execucao) => {
    setActionMenuAnchor(event.currentTarget);
    setSelectedExecucao(execucao);
  };

  const handleActionMenuClose = () => {
    setActionMenuAnchor(null);
    setSelectedExecucao(null);
  };

  /**
   * Manipula ações de controle
   */
  const handleControlAction = (action: 'pause' | 'stop' | 'resume' | 'view' | 'edit' | 'delete') => {
    if (!selectedExecucao) return;

    switch (action) {
      case 'pause':
        console.log('Pausar execução:', selectedExecucao.id);
        break;
      case 'stop':
        console.log('Parar execução:', selectedExecucao.id);
        break;
      case 'resume':
        console.log('Retomar execução:', selectedExecucao.id);
        break;
      case 'view':
        navigate(`/execucoes/${selectedExecucao.id}`);
        break;
      case 'edit':
        navigate(`/execucoes/${selectedExecucao.id}/editar`);
        break;
      case 'delete':
        console.log('Deletar execução:', selectedExecucao.id);
        break;
    }

    handleActionMenuClose();
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
        <Typography variant="caption" color="text.secondary">
          {execucao.progresso}%
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {execucao.keywordsProcessadas}/{execucao.keywordsEncontradas}
        </Typography>
      </Box>
      <LinearProgress
        variant="determinate"
        value={execucao.progresso}
        sx={{
          height: 6,
          borderRadius: 3,
          backgroundColor: 'grey.200',
          '& .MuiLinearProgress-bar': {
            borderRadius: 3,
          }
        }}
      />
    </Box>
  );

  /**
   * Renderiza logs da execução
   */
  const renderLogs = (execucao: Execucao) => (
    <Box sx={{ p: 2, backgroundColor: 'grey.50' }}>
      <Typography variant="subtitle2" gutterBottom>
        Logs da Execução
      </Typography>
      <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
        {execucao.logs.map((log) => (
          <Box key={log.id} sx={{ mb: 1, p: 1, backgroundColor: 'white', borderRadius: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
              {log.nivel === 'info' && <InfoIcon color="info" fontSize="small" />}
              {log.nivel === 'success' && <CheckCircleIcon color="success" fontSize="small" />}
              {log.nivel === 'warning' && <WarningIcon color="warning" fontSize="small" />}
              {log.nivel === 'error' && <ErrorIcon color="error" fontSize="small" />}
              <Typography variant="caption" color="text.secondary">
                {log.timestamp.toLocaleTimeString()}
              </Typography>
              <Chip
                label={log.nivel}
                size="small"
                color={log.nivel as any}
                variant="outlined"
              />
            </Box>
            <Typography variant="body2">
              {log.mensagem}
            </Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );

  if (loading) {
    return (
      <Box>
        <Skeleton variant="rectangular" height={400} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Filtros */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
          <TextField
            size="small"
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
            sx={{ minWidth: 200 }}
          />

          <FormControl size="small" sx={{ minWidth: 120 }}>
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
              <MenuItem value="cancelada">Cancelada</MenuItem>
              <MenuItem value="pausada">Pausada</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Nicho</InputLabel>
            <Select
              value={filters.nicho}
              onChange={(e) => handleFilterChange('nicho', e.target.value)}
              label="Nicho"
            >
              <MenuItem value="">Todos</MenuItem>
              <MenuItem value="Tecnologia">Tecnologia</MenuItem>
              <MenuItem value="Saúde e Bem-estar">Saúde e Bem-estar</MenuItem>
              <MenuItem value="Finanças">Finanças</MenuItem>
              <MenuItem value="Educação">Educação</MenuItem>
            </Select>
          </FormControl>

          <TextField
            size="small"
            type="date"
            label="Data Início"
            value={filters.dataInicio}
            onChange={(e) => handleFilterChange('dataInicio', e.target.value)}
            InputLabelProps={{ shrink: true }}
          />

          <TextField
            size="small"
            type="date"
            label="Data Fim"
            value={filters.dataFim}
            onChange={(e) => handleFilterChange('dataFim', e.target.value)}
            InputLabelProps={{ shrink: true }}
          />

          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadExecucoes}
          >
            Atualizar
          </Button>
        </Box>
      </Paper>

      {/* Tabela */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={filters.selectedItems.length === filteredExecucoes.slice(
                      page * rowsPerPage,
                      page * rowsPerPage + rowsPerPage
                    ).length}
                    indeterminate={filters.selectedItems.length > 0 && filters.selectedItems.length < filteredExecucoes.slice(
                      page * rowsPerPage,
                      page * rowsPerPage + rowsPerPage
                    ).length}
                    onChange={handleSelectAll}
                  />
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === 'nome'}
                    direction={sortField === 'nome' ? sortOrder : 'asc'}
                    onClick={() => handleSort('nome')}
                  >
                    Nome
                  </TableSortLabel>
                </TableCell>
                <TableCell>Nicho</TableCell>
                <TableCell>Categoria</TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === 'status'}
                    direction={sortField === 'status' ? sortOrder : 'asc'}
                    onClick={() => handleSort('status')}
                  >
                    Status
                  </TableSortLabel>
                </TableCell>
                <TableCell>Progresso</TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === 'tempoExecucao'}
                    direction={sortField === 'tempoExecucao' ? sortOrder : 'asc'}
                    onClick={() => handleSort('tempoExecucao')}
                  >
                    Tempo
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === 'dataInicio'}
                    direction={sortField === 'dataInicio' ? sortOrder : 'asc'}
                    onClick={() => handleSort('dataInicio')}
                  >
                    Data Início
                  </TableSortLabel>
                </TableCell>
                <TableCell align="center">Ações</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredExecucoes
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((execucao) => (
                  <React.Fragment key={execucao.id}>
                    <TableRow hover>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={filters.selectedItems.includes(execucao.id)}
                          onChange={() => handleItemSelection(execucao.id)}
                        />
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {execucao.nome}
                          </Typography>
                          {execucao.erro && (
                            <Typography variant="caption" color="error">
                              {execucao.erro}
                            </Typography>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>{execucao.nicho}</TableCell>
                      <TableCell>{execucao.categoria}</TableCell>
                      <TableCell>{renderStatus(execucao.status)}</TableCell>
                      <TableCell sx={{ width: 200 }}>
                        {renderProgress(execucao)}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <TimerIcon fontSize="small" color="action" />
                          <Typography variant="body2">
                            {execucao.tempoExecucao}min
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {execucao.dataInicio.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="Ver detalhes">
                            <IconButton
                              size="small"
                              onClick={() => navigate(`/execucoes/${execucao.id}`)}
                            >
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>
                          
                          {execucao.status === 'em_andamento' && (
                            <>
                              <Tooltip title="Pausar">
                                <IconButton
                                  size="small"
                                  onClick={() => console.log('Pausar:', execucao.id)}
                                >
                                  <PauseIcon />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Parar">
                                <IconButton
                                  size="small"
                                  onClick={() => console.log('Parar:', execucao.id)}
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
                                onClick={() => console.log('Retomar:', execucao.id)}
                              >
                                <PlayIcon />
                              </IconButton>
                            </Tooltip>
                          )}

                          <IconButton
                            size="small"
                            onClick={(e) => handleActionMenuOpen(e, execucao)}
                          >
                            <MoreIcon />
                          </IconButton>
                        </Box>
                      </TableCell>
                    </TableRow>
                    
                    {/* Linha expandida com logs */}
                    <TableRow>
                      <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={9}>
                        <Collapse in={expandedRows.includes(execucao.id)} timeout="auto" unmountOnExit>
                          {renderLogs(execucao)}
                        </Collapse>
                      </TableCell>
                    </TableRow>
                  </React.Fragment>
                ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Paginação */}
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={filteredExecucoes.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
          labelRowsPerPage="Linhas por página:"
          labelDisplayedRows={({ from, to, count }) =>
            `${from}-${to} de ${count !== -1 ? count : `mais de ${to}`}`
          }
        />
      </Paper>

      {/* Menu de ações */}
      <Menu
        anchorEl={actionMenuAnchor}
        open={Boolean(actionMenuAnchor)}
        onClose={handleActionMenuClose}
      >
        <MenuItem onClick={() => handleControlAction('view')}>
          <ListItemIcon>
            <ViewIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Ver Detalhes</ListItemText>
        </MenuItem>
        
        <MenuItem onClick={() => handleControlAction('edit')}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Editar</ListItemText>
        </MenuItem>

        <Divider />

        <MenuItem onClick={() => handleControlAction('delete')}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Excluir</ListItemText>
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default ExecucoesTable; 