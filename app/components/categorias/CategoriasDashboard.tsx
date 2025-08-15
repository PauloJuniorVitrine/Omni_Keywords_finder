/**
 * CategoriasDashboard.tsx
 * 
 * Dashboard de gestão de categorias com visualização hierárquica
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_008
 * Data: 2025-01-27
 * Versão: 1.0
 * 
 * Funcionalidades:
 * - Dashboard de categorias
 * - Visualização hierárquica
 * - Associação com nichos
 * - Métricas por categoria
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
  TreeView,
  TreeItem,
  Paper,
  Tooltip,
  Alert,
  Skeleton,
  useTheme,
  useMediaQuery,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Collapse,
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  ExpandMore as ExpandMoreIcon,
  ChevronRight as ChevronRightIcon,
  Category as CategoryIcon,
  Folder as FolderIcon,
  SubdirectoryArrowRight as SubdirectoryIcon,
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

// Tipos
interface Categoria {
  id: string;
  nome: string;
  descricao: string;
  categoriaPai?: string;
  nivel: number;
  status: 'ativo' | 'inativo' | 'pendente';
  totalNichos: number;
  totalKeywords: number;
  execucoesRealizadas: number;
  ultimaExecucao: Date | null;
  dataCriacao: Date;
  dataAtualizacao: Date;
  subcategorias: Categoria[];
}

interface CategoriaMetrics {
  totalCategorias: number;
  categoriasAtivas: number;
  categoriasInativas: number;
  totalNichos: number;
  totalKeywords: number;
  execucoesHoje: number;
  execucoesSemana: number;
}

interface FilterState {
  search: string;
  status: string;
  nivel: string;
  selectedItems: string[];
}

/**
 * Componente de dashboard de categorias
 */
const CategoriasDashboard: React.FC = () => {
  // Estados
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [categoriasHierarquicas, setCategoriasHierarquicas] = useState<Categoria[]>([]);
  const [metrics, setMetrics] = useState<CategoriaMetrics>({
    totalCategorias: 0,
    categoriasAtivas: 0,
    categoriasInativas: 0,
    totalNichos: 0,
    totalKeywords: 0,
    execucoesHoje: 0,
    execucoesSemana: 0,
  });
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    status: '',
    nivel: '',
    selectedItems: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  // Hooks
  const theme = useTheme();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Efeitos
  useEffect(() => {
    loadCategorias();
    loadMetrics();
  }, []);

  useEffect(() => {
    // Filtrar categorias baseado nos filtros
    filterCategorias();
  }, [filters, categorias]);

  /**
   * Carrega categorias da API
   */
  const loadCategorias = async () => {
    try {
      setLoading(true);
      // TODO: Implementar chamada real da API
      // const response = await api.get('/categorias');
      
      // Mock de dados
      const mockCategorias: Categoria[] = [
        {
          id: '1',
          nome: 'Tecnologia',
          descricao: 'Categoria principal para nichos de tecnologia',
          nivel: 1,
          status: 'ativo',
          totalNichos: 5,
          totalKeywords: 2500,
          execucoesRealizadas: 120,
          ultimaExecucao: new Date('2025-01-26'),
          dataCriacao: new Date('2024-12-01'),
          dataAtualizacao: new Date('2025-01-26'),
          subcategorias: [
            {
              id: '1.1',
              nome: 'Desenvolvimento Web',
              descricao: 'Subcategoria para desenvolvimento web',
              categoriaPai: '1',
              nivel: 2,
              status: 'ativo',
              totalNichos: 2,
              totalKeywords: 800,
              execucoesRealizadas: 45,
              ultimaExecucao: new Date('2025-01-25'),
              dataCriacao: new Date('2024-12-05'),
              dataAtualizacao: new Date('2025-01-25'),
              subcategorias: [],
            },
            {
              id: '1.2',
              nome: 'Mobile',
              descricao: 'Subcategoria para desenvolvimento mobile',
              categoriaPai: '1',
              nivel: 2,
              status: 'ativo',
              totalNichos: 3,
              totalKeywords: 1200,
              execucoesRealizadas: 75,
              ultimaExecucao: new Date('2025-01-26'),
              dataCriacao: new Date('2024-12-10'),
              dataAtualizacao: new Date('2025-01-26'),
              subcategorias: [],
            },
          ],
        },
        {
          id: '2',
          nome: 'Saúde',
          descricao: 'Categoria principal para nichos de saúde',
          nivel: 1,
          status: 'ativo',
          totalNichos: 3,
          totalKeywords: 1800,
          execucoesRealizadas: 85,
          ultimaExecucao: new Date('2025-01-25'),
          dataCriacao: new Date('2024-11-15'),
          dataAtualizacao: new Date('2025-01-25'),
          subcategorias: [
            {
              id: '2.1',
              nome: 'Fitness',
              descricao: 'Subcategoria para fitness e bem-estar',
              categoriaPai: '2',
              nivel: 2,
              status: 'ativo',
              totalNichos: 2,
              totalKeywords: 900,
              execucoesRealizadas: 40,
              ultimaExecucao: new Date('2025-01-24'),
              dataCriacao: new Date('2024-11-20'),
              dataAtualizacao: new Date('2025-01-24'),
              subcategorias: [],
            },
          ],
        },
        {
          id: '3',
          nome: 'Finanças',
          descricao: 'Categoria principal para nichos financeiros',
          nivel: 1,
          status: 'pendente',
          totalNichos: 2,
          totalKeywords: 1200,
          execucoesRealizadas: 30,
          ultimaExecucao: null,
          dataCriacao: new Date('2025-01-20'),
          dataAtualizacao: new Date('2025-01-20'),
          subcategorias: [],
        },
      ];

      setCategorias(mockCategorias);
      setCategoriasHierarquicas(mockCategorias);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar categorias');
      console.error('Erro ao carregar categorias:', err);
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
      // const response = await api.get('/categorias/metrics');
      
      // Mock de métricas
      const mockMetrics: CategoriaMetrics = {
        totalCategorias: 8,
        categoriasAtivas: 6,
        categoriasInativas: 2,
        totalNichos: 12,
        totalKeywords: 5500,
        execucoesHoje: 15,
        execucoesSemana: 235,
      };

      setMetrics(mockMetrics);
    } catch (err) {
      console.error('Erro ao carregar métricas:', err);
    }
  };

  /**
   * Filtra categorias baseado nos filtros
   */
  const filterCategorias = () => {
    let filtered = [...categorias];

    // Filtro por busca
    if (filters.search) {
      filtered = filtered.filter(cat =>
        cat.nome.toLowerCase().includes(filters.search.toLowerCase()) ||
        cat.descricao.toLowerCase().includes(filters.search.toLowerCase())
      );
    }

    // Filtro por status
    if (filters.status) {
      filtered = filtered.filter(cat => cat.status === filters.status);
    }

    // Filtro por nível
    if (filters.nivel) {
      filtered = filtered.filter(cat => cat.nivel === parseInt(filters.nivel));
    }

    setCategoriasHierarquicas(filtered);
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
    if (filters.selectedItems.length === categorias.length) {
      setFilters(prev => ({ ...prev, selectedItems: [] }));
    } else {
      setFilters(prev => ({ ...prev, selectedItems: categorias.map(cat => cat.id) }));
    }
  };

  /**
   * Manipula expansão/colapso de item
   */
  const handleToggleExpanded = (itemId: string) => {
    setExpandedItems(prev =>
      prev.includes(itemId)
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  /**
   * Manipula criação de categoria
   */
  const handleCreateCategoria = () => {
    navigate('/categorias/nova');
  };

  /**
   * Manipula edição de categoria
   */
  const handleEditCategoria = (categoriaId: string) => {
    navigate(`/categorias/${categoriaId}/editar`);
  };

  /**
   * Manipula visualização de categoria
   */
  const handleViewCategoria = (categoriaId: string) => {
    navigate(`/categorias/${categoriaId}`);
  };

  /**
   * Manipula ação em lote
   */
  const handleBulkAction = (action: string) => {
    console.log(`Ação em lote: ${action}`, filters.selectedItems);
    // TODO: Implementar ações em lote
  };

  /**
   * Renderiza card de métrica
   */
  const renderMetricCard = (title: string, value: number, icon: React.ReactNode, color: string) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h4" component="div" fontWeight={600} color={color}>
              {value.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {title}
            </Typography>
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
      ativo: { color: 'success', label: 'Ativo' },
      inativo: { color: 'error', label: 'Inativo' },
      pendente: { color: 'warning', label: 'Pendente' },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pendente;

    return (
      <Chip
        label={config.label}
        color={config.color as any}
        size="small"
        variant="outlined"
      />
    );
  };

  /**
   * Renderiza item da árvore de categorias
   */
  const renderTreeItem = (categoria: Categoria, level: number = 0) => {
    const isExpanded = expandedItems.includes(categoria.id);
    const hasChildren = categoria.subcategorias.length > 0;

    return (
      <Box key={categoria.id}>
        <Paper
          sx={{
            p: 2,
            mb: 1,
            ml: level * 3,
            border: '1px solid',
            borderColor: 'divider',
            '&:hover': {
              borderColor: 'primary.main',
              backgroundColor: 'action.hover',
            },
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
              {hasChildren && (
                <IconButton
                  size="small"
                  onClick={() => handleToggleExpanded(categoria.id)}
                >
                  {isExpanded ? <ExpandMoreIcon /> : <ChevronRightIcon />}
                </IconButton>
              )}
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CategoryIcon color="primary" />
                <Box>
                  <Typography variant="subtitle1" fontWeight={500}>
                    {categoria.nome}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Nível {categoria.nivel} • {categoria.totalNichos} nichos • {categoria.totalKeywords} keywords
                  </Typography>
                </Box>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {renderStatus(categoria.status)}
              
              <Tooltip title="Visualizar">
                <IconButton
                  size="small"
                  onClick={() => handleViewCategoria(categoria.id)}
                >
                  <ViewIcon />
                </IconButton>
              </Tooltip>
              
              <Tooltip title="Editar">
                <IconButton
                  size="small"
                  onClick={() => handleEditCategoria(categoria.id)}
                >
                  <EditIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          {categoria.descricao && (
            <Typography variant="body2" color="textSecondary" sx={{ mt: 1, ml: hasChildren ? 4 : 0 }}>
              {categoria.descricao}
            </Typography>
          )}
        </Paper>

        {hasChildren && isExpanded && (
          <Box>
            {categoria.subcategorias.map(subcat => renderTreeItem(subcat, level + 1))}
          </Box>
        )}
      </Box>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" fontWeight={600}>
          Gestão de Categorias
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateCategoria}
        >
          Nova Categoria
        </Button>
      </Box>

      {/* Métricas */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2}>
          {renderMetricCard(
            'Total Categorias',
            metrics.totalCategorias,
            <CategoryIcon />,
            'primary.main'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          {renderMetricCard(
            'Categorias Ativas',
            metrics.categoriasAtivas,
            <CheckCircleIcon />,
            'success.main'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          {renderMetricCard(
            'Total Nichos',
            metrics.totalNichos,
            <FolderIcon />,
            'info.main'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          {renderMetricCard(
            'Total Keywords',
            metrics.totalKeywords,
            <TrendingUpIcon />,
            'warning.main'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          {renderMetricCard(
            'Execuções Hoje',
            metrics.execucoesHoje,
            <CheckCircleIcon />,
            'secondary.main'
          )}
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          {renderMetricCard(
            'Execuções Semana',
            metrics.execucoesSemana,
            <TrendingUpIcon />,
            'success.main'
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
                placeholder="Buscar categorias..."
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
                <InputLabel>Nível</InputLabel>
                <Select
                  value={filters.nivel}
                  onChange={(e) => handleFilterChange('nivel', e.target.value)}
                  label="Nível"
                >
                  <MenuItem value="">Todos</MenuItem>
                  <MenuItem value="1">Nível 1</MenuItem>
                  <MenuItem value="2">Nível 2</MenuItem>
                  <MenuItem value="3">Nível 3</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={loadCategorias}
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
        </Box>
      )}

      {/* Árvore de categorias */}
      {error ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      ) : loading ? (
        <Box>
          {Array.from({ length: 5 }).map((_, index) => (
            <Skeleton key={index} variant="rectangular" height={80} sx={{ mb: 1 }} />
          ))}
        </Box>
      ) : (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Estrutura Hierárquica de Categorias
            </Typography>
            <Box>
              {categoriasHierarquicas.map(categoria => renderTreeItem(categoria))}
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default CategoriasDashboard; 