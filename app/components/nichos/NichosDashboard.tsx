/**
 * NichosDashboard.tsx
 * 
 * Dashboard principal de gestão de nichos da aplicação Omni Keywords Finder
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_004
 * Data: 2025-01-27
 * Versão: 1.0
 * 
 * Funcionalidades:
 * - Dashboard principal de nichos
 * - Listagem com filtros
 * - Métricas por nicho
 * - Ações em lote
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
  Checkbox,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
  Alert,
  Skeleton,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Download as DownloadIcon,
  TrendingUp as TrendingUpIcon,
  Category as CategoryIcon,
  PlayArrow as PlayIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

// Tipos
interface Nicho {
  id: string;
  nome: string;
  descricao: string;
  categoria: string;
  status: 'ativo' | 'inativo' | 'pendente';
  totalKeywords: number;
  execucoesRealizadas: number;
  ultimaExecucao: Date | null;
  dataCriacao: Date;
  dataAtualizacao: Date;
}

interface NichoMetrics {
  totalNichos: number;
  nichosAtivos: number;
  nichosInativos: number;
  totalKeywords: number;
  execucoesHoje: number;
  execucoesSemana: number;
}

interface FilterState {
  search: string;
  status: string;
  categoria: string;
  selectedItems: string[];
}

/**
 * Componente de dashboard de nichos
 */
const NichosDashboard: React.FC = () => {
  // Estados
  const [nichos, setNichos] = useState<Nicho[]>([]);
  const [metrics, setMetrics] = useState<NichoMetrics>({
    totalNichos: 0,
    nichosAtivos: 0,
    nichosInativos: 0,
    totalKeywords: 0,
    execucoesHoje: 0,
    execucoesSemana: 0,
  });
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    status: '',
    categoria: '',
    selectedItems: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Hooks
  const theme = useTheme();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Efeitos
  useEffect(() => {
    loadNichos();
    loadMetrics();
  }, []);

  useEffect(() => {
    // Filtrar nichos baseado nos filtros
    filterNichos();
  }, [filters]);

  /**
   * Carrega nichos da API
   */
  const loadNichos = async () => {
    try {
      setLoading(true);
      // TODO: Implementar chamada real da API
      // const response = await api.get('/nichos');
      
      // Mock de dados
      const mockNichos: Nicho[] = [
        {
          id: '1',
          nome: 'Tecnologia',
          descricao: 'Nichos relacionados a tecnologia e inovação',
          categoria: 'Tecnologia',
          status: 'ativo',
          totalKeywords: 1250,
          execucoesRealizadas: 45,
          ultimaExecucao: new Date('2025-01-26'),
          dataCriacao: new Date('2024-12-01'),
          dataAtualizacao: new Date('2025-01-26'),
        },
        {
          id: '2',
          nome: 'Saúde e Bem-estar',
          descricao: 'Nichos de saúde, fitness e bem-estar',
          categoria: 'Saúde',
          status: 'ativo',
          totalKeywords: 890,
          execucoesRealizadas: 32,
          ultimaExecucao: new Date('2025-01-25'),
          dataCriacao: new Date('2024-11-15'),
          dataAtualizacao: new Date('2025-01-25'),
        },
        {
          id: '3',
          nome: 'Finanças',
          descricao: 'Nichos financeiros e de investimentos',
          categoria: 'Finanças',
          status: 'pendente',
          totalKeywords: 650,
          execucoesRealizadas: 18,
          ultimaExecucao: null,
          dataCriacao: new Date('2025-01-20'),
          dataAtualizacao: new Date('2025-01-20'),
        },
        {
          id: '4',
          nome: 'Educação',
          descricao: 'Nichos educacionais e de cursos online',
          categoria: 'Educação',
          status: 'inativo',
          totalKeywords: 420,
          execucoesRealizadas: 12,
          ultimaExecucao: new Date('2025-01-15'),
          dataCriacao: new Date('2024-10-10'),
          dataAtualizacao: new Date('2025-01-15'),
        },
      ];

      setNichos(mockNichos);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar nichos');
      console.error('Erro ao carregar nichos:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Carrega métricas dos nichos
   */
  const loadMetrics = async () => {
    try {
      // TODO: Implementar chamada real da API
      // const response = await api.get('/nichos/metrics');
      
      // Mock de métricas
      const mockMetrics: NichoMetrics = {
        totalNichos: 4,
        nichosAtivos: 2,
        nichosInativos: 1,
        totalKeywords: 3210,
        execucoesHoje: 8,
        execucoesSemana: 45,
      };

      setMetrics(mockMetrics);
    } catch (err) {
      console.error('Erro ao carregar métricas:', err);
    }
  };

  /**
   * Filtra nichos baseado nos filtros aplicados
   */
  const filterNichos = () => {
    // TODO: Implementar filtros reais
    // Por enquanto, apenas simula filtros
    console.log('Aplicando filtros:', filters);
  };

  /**
   * Atualiza filtros
   */
  const handleFilterChange = (field: keyof FilterState, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  /**
   * Seleciona/desseleciona item
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
   * Seleciona/desseleciona todos os itens
   */
  const handleSelectAll = () => {
    setFilters(prev => ({
      ...prev,
      selectedItems: prev.selectedItems.length === nichos.length ? [] : nichos.map(n => n.id),
    }));
  };

  /**
   * Navega para criação de novo nicho
   */
  const handleCreateNicho = () => {
    navigate('/nichos/novo');
  };

  /**
   * Navega para edição de nicho
   */
  const handleEditNicho = (nichoId: string) => {
    navigate(`/nichos/${nichoId}/editar`);
  };

  /**
   * Navega para visualização de nicho
   */
  const handleViewNicho = (nichoId: string) => {
    navigate(`/nichos/${nichoId}`);
  };

  /**
   * Executa ação em lote
   */
  const handleBulkAction = (action: string) => {
    console.log(`Executando ação ${action} em:`, filters.selectedItems);
    // TODO: Implementar ações em lote
  };

  /**
   * Renderiza card de métrica
   */
  const renderMetricCard = (title: string, value: number, icon: React.ReactNode, color: string) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
              {value.toLocaleString()}
            </Typography>
          </Box>
          <Box sx={{ color }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  /**
   * Renderiza status do nicho
   */
  const renderStatus = (status: string) => {
    const statusConfig = {
      ativo: { color: 'success', icon: <CheckCircleIcon />, label: 'Ativo' },
      inativo: { color: 'error', icon: <ErrorIcon />, label: 'Inativo' },
      pendente: { color: 'warning', icon: <WarningIcon />, label: 'Pendente' },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pendente;

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
   * Renderiza tabela de nichos
   */
  const renderNichosTable = () => (
    <TableContainer component={Paper} sx={{ mt: 2 }}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox">
              <Checkbox
                checked={filters.selectedItems.length === nichos.length && nichos.length > 0}
                indeterminate={filters.selectedItems.length > 0 && filters.selectedItems.length < nichos.length}
                onChange={handleSelectAll}
              />
            </TableCell>
            <TableCell>Nome</TableCell>
            <TableCell>Categoria</TableCell>
            <TableCell>Status</TableCell>
            <TableCell align="right">Keywords</TableCell>
            <TableCell align="right">Execuções</TableCell>
            <TableCell>Última Execução</TableCell>
            <TableCell align="center">Ações</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {loading ? (
            // Skeletons para loading
            Array.from({ length: 5 }).map((_, index) => (
              <TableRow key={index}>
                <TableCell><Skeleton /></TableCell>
                <TableCell><Skeleton /></TableCell>
                <TableCell><Skeleton /></TableCell>
                <TableCell><Skeleton /></TableCell>
                <TableCell><Skeleton /></TableCell>
                <TableCell><Skeleton /></TableCell>
                <TableCell><Skeleton /></TableCell>
                <TableCell><Skeleton /></TableCell>
              </TableRow>
            ))
          ) : (
            nichos.map((nicho) => (
              <TableRow key={nicho.id} hover>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={filters.selectedItems.includes(nicho.id)}
                    onChange={() => handleItemSelection(nicho.id)}
                  />
                </TableCell>
                <TableCell>
                  <Box>
                    <Typography variant="subtitle2" fontWeight={600}>
                      {nicho.nome}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {nicho.descricao}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip label={nicho.categoria} size="small" />
                </TableCell>
                <TableCell>
                  {renderStatus(nicho.status)}
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2" fontWeight={600}>
                    {nicho.totalKeywords.toLocaleString()}
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2">
                    {nicho.execucoesRealizadas}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {nicho.ultimaExecucao 
                      ? nicho.ultimaExecucao.toLocaleDateString('pt-BR')
                      : 'Nunca'
                    }
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                    <Tooltip title="Visualizar">
                      <IconButton
                        size="small"
                        onClick={() => handleViewNicho(nicho.id)}
                      >
                        <ViewIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Editar">
                      <IconButton
                        size="small"
                        onClick={() => handleEditNicho(nicho.id)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Executar">
                      <IconButton
                        size="small"
                        onClick={() => navigate(`/execucoes/nova?nicho=${nicho.id}`)}
                      >
                        <PlayIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" fontWeight={600}>
          Gestão de Nichos
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateNicho}
        >
          Novo Nicho
        </Button>
      </Box>

      {/* Métricas */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2}>
          {renderMetricCard(
            'Total de Nichos',
            metrics.totalNichos,
            <CategoryIcon />,
            'primary.main'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          {renderMetricCard(
            'Nichos Ativos',
            metrics.nichosAtivos,
            <CheckCircleIcon />,
            'success.main'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          {renderMetricCard(
            'Total Keywords',
            metrics.totalKeywords,
            <TrendingUpIcon />,
            'info.main'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          {renderMetricCard(
            'Execuções Hoje',
            metrics.execucoesHoje,
            <PlayIcon />,
            'warning.main'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          {renderMetricCard(
            'Execuções Semana',
            metrics.execucoesSemana,
            <PlayIcon />,
            'secondary.main'
          )}
        </Grid>
      </Grid>

      {/* Filtros */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Buscar nichos..."
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
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  label="Status"
                >
                  <MenuItem value="">Todos</MenuItem>
                  <MenuItem value="ativo">Ativo</MenuItem>
                  <MenuItem value="inativo">Inativo</MenuItem>
                  <MenuItem value="pendente">Pendente</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Categoria</InputLabel>
                <Select
                  value={filters.categoria}
                  onChange={(e) => handleFilterChange('categoria', e.target.value)}
                  label="Categoria"
                >
                  <MenuItem value="">Todas</MenuItem>
                  <MenuItem value="Tecnologia">Tecnologia</MenuItem>
                  <MenuItem value="Saúde">Saúde</MenuItem>
                  <MenuItem value="Finanças">Finanças</MenuItem>
                  <MenuItem value="Educação">Educação</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={loadNichos}
              >
                Atualizar
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Ações em lote */}
      {filters.selectedItems.length > 0 && (
        <Box sx={{ mb: 2, display: 'flex', gap: 1, alignItems: 'center' }}>
          <Typography variant="body2" color="textSecondary">
            {filters.selectedItems.length} item(s) selecionado(s)
          </Typography>
          <Button
            size="small"
            variant="outlined"
            startIcon={<DeleteIcon />}
            onClick={() => handleBulkAction('delete')}
          >
            Excluir
          </Button>
          <Button
            size="small"
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={() => handleBulkAction('export')}
          >
            Exportar
          </Button>
        </Box>
      )}

      {/* Tabela de nichos */}
      {error ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      ) : (
        renderNichosTable()
      )}
    </Box>
  );
};

export default NichosDashboard; 