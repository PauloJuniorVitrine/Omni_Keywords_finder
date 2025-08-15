/**
 * NichosTable.tsx
 * 
 * Tabela de nichos com funcionalidades avançadas de gestão
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_005
 * Data: 2025-01-27
 * Versão: 1.0
 * 
 * Funcionalidades:
 * - Tabela com paginação
 * - Filtros avançados
 * - Ordenação
 * - Seleção múltipla
 * - Integração com APIs do backend
 */

import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Checkbox,
  Paper,
  Box,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Skeleton,
  Alert,
  useTheme,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  PlayArrow as PlayIcon,
  Download as DownloadIcon,
  MoreVert as MoreIcon,
} from '@mui/icons-material';

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

interface NichosTableProps {
  nichos: Nicho[];
  loading?: boolean;
  error?: string | null;
  selectedItems: string[];
  onSelectionChange: (selectedIds: string[]) => void;
  onEdit: (nichoId: string) => void;
  onDelete: (nichoId: string) => void;
  onView: (nichoId: string) => void;
  onExecute: (nichoId: string) => void;
  onExport: (nichoId: string) => void;
}

type OrderBy = 'nome' | 'categoria' | 'status' | 'totalKeywords' | 'execucoesRealizadas' | 'dataCriacao' | 'dataAtualizacao' | 'ultimaExecucao';
type OrderDirection = 'asc' | 'desc';

/**
 * Componente de tabela de nichos
 */
const NichosTable: React.FC<NichosTableProps> = ({
  nichos,
  loading = false,
  error = null,
  selectedItems,
  onSelectionChange,
  onEdit,
  onDelete,
  onView,
  onExecute,
  onExport,
}) => {
  // Estados
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [orderBy, setOrderBy] = useState<OrderBy>('nome');
  const [orderDirection, setOrderDirection] = useState<OrderDirection>('asc');

  // Hooks
  const theme = useTheme();

  // Efeitos
  useEffect(() => {
    setPage(0); // Reset para primeira página quando dados mudam
  }, [nichos]);

  /**
   * Manipula mudança de página
   */
  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  /**
   * Manipula mudança de linhas por página
   */
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  /**
   * Manipula ordenação
   */
  const handleSort = (property: OrderBy) => {
    const isAsc = orderBy === property && orderDirection === 'asc';
    setOrderDirection(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  /**
   * Manipula seleção de item
   */
  const handleSelectItem = (itemId: string) => {
    const newSelected = selectedItems.includes(itemId)
      ? selectedItems.filter(id => id !== itemId)
      : [...selectedItems, itemId];
    onSelectionChange(newSelected);
  };

  /**
   * Manipula seleção de todos os itens
   */
  const handleSelectAll = () => {
    if (selectedItems.length === nichos.length) {
      onSelectionChange([]);
    } else {
      onSelectionChange(nichos.map(nicho => nicho.id));
    }
  };

  /**
   * Ordena os dados
   */
  const sortData = (data: Nicho[]) => {
    return data.sort((a, b) => {
      let aValue: any = a[orderBy];
      let bValue: any = b[orderBy];

      // Tratamento especial para datas
      if (orderBy === 'dataCriacao' || orderBy === 'dataAtualizacao') {
        aValue = new Date(aValue).getTime();
        bValue = new Date(bValue).getTime();
      }

      // Tratamento especial para ultimaExecucao (pode ser null)
      if (orderBy === 'ultimaExecucao') {
        aValue = aValue ? new Date(aValue).getTime() : 0;
        bValue = bValue ? new Date(bValue).getTime() : 0;
      }

      if (orderDirection === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });
  };

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
   * Renderiza data formatada
   */
  const renderDate = (date: Date | null) => {
    if (!date) return '-';
    return new Date(date).toLocaleDateString('pt-BR');
  };

  /**
   * Renderiza ações da tabela
   */
  const renderActions = (nicho: Nicho) => (
    <Box sx={{ display: 'flex', gap: 0.5 }}>
      <Tooltip title="Visualizar">
        <IconButton
          size="small"
          onClick={() => onView(nicho.id)}
        >
          <ViewIcon />
        </IconButton>
      </Tooltip>
      <Tooltip title="Editar">
        <IconButton
          size="small"
          onClick={() => onEdit(nicho.id)}
        >
          <EditIcon />
        </IconButton>
      </Tooltip>
      <Tooltip title="Executar">
        <IconButton
          size="small"
          onClick={() => onExecute(nicho.id)}
        >
          <PlayIcon />
        </IconButton>
      </Tooltip>
      <Tooltip title="Exportar">
        <IconButton
          size="small"
          onClick={() => onExport(nicho.id)}
        >
          <DownloadIcon />
        </IconButton>
      </Tooltip>
      <Tooltip title="Excluir">
        <IconButton
          size="small"
          color="error"
          onClick={() => onDelete(nicho.id)}
        >
          <DeleteIcon />
        </IconButton>
      </Tooltip>
    </Box>
  );

  // Dados ordenados e paginados
  const sortedData = sortData([...nichos]);
  const paginatedData = sortedData.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  // Loading skeleton
  if (loading) {
    return (
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Skeleton variant="rectangular" width={20} height={20} />
                </TableCell>
                <TableCell><Skeleton variant="text" width={100} /></TableCell>
                <TableCell><Skeleton variant="text" width={80} /></TableCell>
                <TableCell><Skeleton variant="text" width={60} /></TableCell>
                <TableCell><Skeleton variant="text" width={80} /></TableCell>
                <TableCell><Skeleton variant="text" width={80} /></TableCell>
                <TableCell><Skeleton variant="text" width={80} /></TableCell>
                <TableCell><Skeleton variant="text" width={100} /></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {Array.from({ length: 5 }).map((_, index) => (
                <TableRow key={index}>
                  <TableCell padding="checkbox">
                    <Skeleton variant="rectangular" width={20} height={20} />
                  </TableCell>
                  <TableCell><Skeleton variant="text" width={120} /></TableCell>
                  <TableCell><Skeleton variant="text" width={100} /></TableCell>
                  <TableCell><Skeleton variant="text" width={60} /></TableCell>
                  <TableCell><Skeleton variant="text" width={40} /></TableCell>
                  <TableCell><Skeleton variant="text" width={40} /></TableCell>
                  <TableCell><Skeleton variant="text" width={80} /></TableCell>
                  <TableCell><Skeleton variant="text" width={120} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    );
  }

  // Error state
  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Paper>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  indeterminate={selectedItems.length > 0 && selectedItems.length < nichos.length}
                  checked={nichos.length > 0 && selectedItems.length === nichos.length}
                  onChange={handleSelectAll}
                />
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'nome'}
                  direction={orderBy === 'nome' ? orderDirection : 'asc'}
                  onClick={() => handleSort('nome')}
                >
                  Nome
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'categoria'}
                  direction={orderBy === 'categoria' ? orderDirection : 'asc'}
                  onClick={() => handleSort('categoria')}
                >
                  Categoria
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'status'}
                  direction={orderBy === 'status' ? orderDirection : 'asc'}
                  onClick={() => handleSort('status')}
                >
                  Status
                </TableSortLabel>
              </TableCell>
              <TableCell align="center">
                <TableSortLabel
                  active={orderBy === 'totalKeywords'}
                  direction={orderBy === 'totalKeywords' ? orderDirection : 'asc'}
                  onClick={() => handleSort('totalKeywords')}
                >
                  Keywords
                </TableSortLabel>
              </TableCell>
              <TableCell align="center">
                <TableSortLabel
                  active={orderBy === 'execucoesRealizadas'}
                  direction={orderBy === 'execucoesRealizadas' ? orderDirection : 'asc'}
                  onClick={() => handleSort('execucoesRealizadas')}
                >
                  Execuções
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'dataCriacao'}
                  direction={orderBy === 'dataCriacao' ? orderDirection : 'asc'}
                  onClick={() => handleSort('dataCriacao')}
                >
                  Criado em
                </TableSortLabel>
              </TableCell>
              <TableCell align="center">Ações</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedData.map((nicho) => (
              <TableRow
                key={nicho.id}
                hover
                selected={selectedItems.includes(nicho.id)}
              >
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedItems.includes(nicho.id)}
                    onChange={() => handleSelectItem(nicho.id)}
                  />
                </TableCell>
                <TableCell>
                  <Box>
                    <Typography variant="body2" fontWeight={500}>
                      {nicho.nome}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {nicho.descricao}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={nicho.categoria}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  {renderStatus(nicho.status)}
                </TableCell>
                <TableCell align="center">
                  <Typography variant="body2" fontWeight={500}>
                    {nicho.totalKeywords.toLocaleString()}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <Typography variant="body2">
                    {nicho.execucoesRealizadas}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {renderDate(nicho.dataCriacao)}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  {renderActions(nicho)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      
      <TablePagination
        rowsPerPageOptions={[5, 10, 25, 50]}
        component="div"
        count={nichos.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        labelRowsPerPage="Linhas por página:"
        labelDisplayedRows={({ from, to, count }: { from: number; to: number; count: number }) =>
          `${from}-${to} de ${count !== -1 ? count : `mais de ${to}`}`
        }
      />
    </Paper>
  );
};

export default NichosTable; 