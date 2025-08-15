/**
 * KeywordsTable - Tabela de keywords com funcionalidades avançadas
 * 
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 2.1.2
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { useState, useMemo, useCallback } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Paper,
  TextField,
  Box,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Checkbox,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  LinearProgress
} from '@mui/material';
import {
  Search,
  FilterList,
  Sort,
  Download,
  Delete,
  Edit,
  Visibility,
  Add,
  Refresh
} from '@mui/icons-material';

interface Keyword {
  id: string;
  keyword: string;
  niche: string;
  searchVolume: number;
  difficulty: number;
  cpc: number;
  competition: 'low' | 'medium' | 'high';
  status: 'active' | 'paused' | 'archived';
  lastUpdated: string;
  performance: number;
}

interface KeywordsTableProps {
  keywords: Keyword[];
  isLoading?: boolean;
  onKeywordEdit?: (keyword: Keyword) => void;
  onKeywordDelete?: (keywordIds: string[]) => void;
  onKeywordExport?: (keywordIds: string[]) => void;
  onKeywordBulkAction?: (action: string, keywordIds: string[]) => void;
}

const KeywordsTable: React.FC<KeywordsTableProps> = ({
  keywords,
  isLoading = false,
  onKeywordEdit,
  onKeywordDelete,
  onKeywordExport,
  onKeywordBulkAction
}) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);
  const [sortField, setSortField] = useState<keyof Keyword>('keyword');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [filters, setFilters] = useState({
    niche: '',
    competition: '',
    status: '',
    difficulty: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [showBulkActions, setShowBulkActions] = useState(false);

  // Filtered and sorted data
  const filteredKeywords = useMemo(() => {
    let filtered = keywords.filter(keyword => {
      const matchesSearch = keyword.keyword.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           keyword.niche.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesNiche = !filters.niche || keyword.niche === filters.niche;
      const matchesCompetition = !filters.competition || keyword.competition === filters.competition;
      const matchesStatus = !filters.status || keyword.status === filters.status;
      const matchesDifficulty = !filters.difficulty || 
        (filters.difficulty === 'low' && keyword.difficulty <= 30) ||
        (filters.difficulty === 'medium' && keyword.difficulty > 30 && keyword.difficulty <= 70) ||
        (filters.difficulty === 'high' && keyword.difficulty > 70);

      return matchesSearch && matchesNiche && matchesCompetition && matchesStatus && matchesDifficulty;
    });

    // Sorting
    filtered.sort((a, b) => {
      const aValue = a[sortField];
      const bValue = b[sortField];
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
      }
      
      return 0;
    });

    return filtered;
  }, [keywords, searchTerm, filters, sortField, sortDirection]);

  // Pagination
  const paginatedKeywords = useMemo(() => {
    const startIndex = page * rowsPerPage;
    return filteredKeywords.slice(startIndex, startIndex + rowsPerPage);
  }, [filteredKeywords, page, rowsPerPage]);

  // Available niches for filter
  const availableNiches = useMemo(() => {
    return [...new Set(keywords.map(k => k.niche))];
  }, [keywords]);

  const handleSort = (field: keyof Keyword) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedKeywords(paginatedKeywords.map(k => k.id));
    } else {
      setSelectedKeywords([]);
    }
  };

  const handleSelectKeyword = (keywordId: string, checked: boolean) => {
    if (checked) {
      setSelectedKeywords(prev => [...prev, keywordId]);
    } else {
      setSelectedKeywords(prev => prev.filter(id => id !== keywordId));
    }
  };

  const handleBulkAction = (action: string) => {
    if (selectedKeywords.length === 0) return;
    
    switch (action) {
      case 'delete':
        onKeywordDelete?.(selectedKeywords);
        break;
      case 'export':
        onKeywordExport?.(selectedKeywords);
        break;
      case 'pause':
        onKeywordBulkAction?.('pause', selectedKeywords);
        break;
      case 'activate':
        onKeywordBulkAction?.('activate', selectedKeywords);
        break;
    }
    
    setSelectedKeywords([]);
    setShowBulkActions(false);
  };

  const getCompetitionColor = (competition: string) => {
    switch (competition) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'paused': return 'warning';
      case 'archived': return 'default';
      default: return 'default';
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      {/* Header with search and filters */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="h2">
            Keywords ({filteredKeywords.length})
          </Typography>
          
          <Box display="flex" gap={1}>
            <Button
              variant="outlined"
              startIcon={<FilterList />}
              onClick={() => setShowFilters(!showFilters)}
              size="small"
            >
              Filtros
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={() => onKeywordExport?.(selectedKeywords)}
              disabled={selectedKeywords.length === 0}
              size="small"
            >
              Exportar
            </Button>
            
            <Button
              variant="contained"
              startIcon={<Add />}
              size="small"
            >
              Nova Keyword
            </Button>
          </Box>
        </Box>

        {/* Search */}
        <TextField
          fullWidth
          placeholder="Buscar keywords ou nichos..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
          }}
          size="small"
        />

        {/* Filters */}
        {showFilters && (
          <Box display="flex" gap={2} mt={2} flexWrap="wrap">
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Nicho</InputLabel>
              <Select
                value={filters.niche}
                onChange={(e) => setFilters(prev => ({ ...prev, niche: e.target.value }))}
                label="Nicho"
              >
                <MenuItem value="">Todos</MenuItem>
                {availableNiches.map(niche => (
                  <MenuItem key={niche} value={niche}>{niche}</MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Competição</InputLabel>
              <Select
                value={filters.competition}
                onChange={(e) => setFilters(prev => ({ ...prev, competition: e.target.value }))}
                label="Competição"
              >
                <MenuItem value="">Todas</MenuItem>
                <MenuItem value="low">Baixa</MenuItem>
                <MenuItem value="medium">Média</MenuItem>
                <MenuItem value="high">Alta</MenuItem>
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={filters.status}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                label="Status"
              >
                <MenuItem value="">Todos</MenuItem>
                <MenuItem value="active">Ativo</MenuItem>
                <MenuItem value="paused">Pausado</MenuItem>
                <MenuItem value="archived">Arquivado</MenuItem>
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Dificuldade</InputLabel>
              <Select
                value={filters.difficulty}
                onChange={(e) => setFilters(prev => ({ ...prev, difficulty: e.target.value }))}
                label="Dificuldade"
              >
                <MenuItem value="">Todas</MenuItem>
                <MenuItem value="low">Baixa (≤30)</MenuItem>
                <MenuItem value="medium">Média (31-70)</MenuItem>
                <MenuItem value="high">Alta (>70)</MenuItem>
              </Select>
            </FormControl>
          </Box>
        )}

        {/* Bulk Actions */}
        {selectedKeywords.length > 0 && (
          <Alert 
            severity="info" 
            sx={{ mt: 2 }}
            action={
              <Box display="flex" gap={1}>
                <Button
                  size="small"
                  onClick={() => handleBulkAction('activate')}
                >
                  Ativar
                </Button>
                <Button
                  size="small"
                  onClick={() => handleBulkAction('pause')}
                >
                  Pausar
                </Button>
                <Button
                  size="small"
                  color="error"
                  onClick={() => handleBulkAction('delete')}
                >
                  Excluir
                </Button>
              </Box>
            }
          >
            {selectedKeywords.length} keyword(s) selecionada(s)
          </Alert>
        )}
      </Box>

      {/* Loading */}
      {isLoading && <LinearProgress />}

      {/* Table */}
      <TableContainer sx={{ maxHeight: 600 }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  indeterminate={selectedKeywords.length > 0 && selectedKeywords.length < paginatedKeywords.length}
                  checked={selectedKeywords.length === paginatedKeywords.length && paginatedKeywords.length > 0}
                  onChange={(e) => handleSelectAll(e.target.checked)}
                />
              </TableCell>
              <TableCell>
                <Box display="flex" alignItems="center" gap={1}>
                  Keyword
                  <IconButton size="small" onClick={() => handleSort('keyword')}>
                    <Sort />
                  </IconButton>
                </Box>
              </TableCell>
              <TableCell>Nicho</TableCell>
              <TableCell>
                <Box display="flex" alignItems="center" gap={1}>
                  Volume
                  <IconButton size="small" onClick={() => handleSort('searchVolume')}>
                    <Sort />
                  </IconButton>
                </Box>
              </TableCell>
              <TableCell>
                <Box display="flex" alignItems="center" gap={1}>
                  Dificuldade
                  <IconButton size="small" onClick={() => handleSort('difficulty')}>
                    <Sort />
                  </IconButton>
                </Box>
              </TableCell>
              <TableCell>CPC</TableCell>
              <TableCell>Competição</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Performance</TableCell>
              <TableCell>Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedKeywords.map((keyword) => (
              <TableRow key={keyword.id} hover>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedKeywords.includes(keyword.id)}
                    onChange={(e) => handleSelectKeyword(keyword.id, e.target.checked)}
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {keyword.keyword}
                  </Typography>
                </TableCell>
                <TableCell>{keyword.niche}</TableCell>
                <TableCell>{keyword.searchVolume.toLocaleString()}</TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Typography variant="body2">
                      {keyword.difficulty}%
                    </Typography>
                    <Box
                      sx={{
                        width: 40,
                        height: 4,
                        bgcolor: 'grey.200',
                        borderRadius: 2,
                        overflow: 'hidden'
                      }}
                    >
                      <Box
                        sx={{
                          width: `${keyword.difficulty}%`,
                          height: '100%',
                          bgcolor: keyword.difficulty <= 30 ? 'success.main' : 
                                  keyword.difficulty <= 70 ? 'warning.main' : 'error.main'
                        }}
                      />
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>{formatCurrency(keyword.cpc)}</TableCell>
                <TableCell>
                  <Chip
                    label={keyword.competition === 'low' ? 'Baixa' : 
                           keyword.competition === 'medium' ? 'Média' : 'Alta'}
                    color={getCompetitionColor(keyword.competition)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={keyword.status === 'active' ? 'Ativo' :
                           keyword.status === 'paused' ? 'Pausado' : 'Arquivado'}
                    color={getStatusColor(keyword.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {keyword.performance}%
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box display="flex" gap={1}>
                    <Tooltip title="Visualizar">
                      <IconButton size="small">
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Editar">
                      <IconButton size="small" onClick={() => onKeywordEdit?.(keyword)}>
                        <Edit />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Excluir">
                      <IconButton 
                        size="small" 
                        color="error"
                        onClick={() => onKeywordDelete?.([keyword.id])}
                      >
                        <Delete />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      <TablePagination
        rowsPerPageOptions={[10, 25, 50, 100]}
        component="div"
        count={filteredKeywords.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={(_, newPage) => setPage(newPage)}
        onRowsPerPageChange={(e) => {
          setRowsPerPage(parseInt(e.target.value, 10));
          setPage(0);
        }}
        labelRowsPerPage="Linhas por página:"
        labelDisplayedRows={({ from, to, count }) => `${from}-${to} de ${count}`}
      />
    </Paper>
  );
};

export default KeywordsTable; 