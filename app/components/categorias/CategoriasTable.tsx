/**
 * CategoriasTable.tsx
 * 
 * Tabela hierárquica de categorias com funcionalidades avançadas
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_009
 * Data: 2025-01-27
 * Versão: 1.0
 * 
 * Funcionalidades:
 * - Tabela hierárquica
 * - Filtros por nicho
 * - Drag & drop para reordenação
 * - Ações em lote
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
  Collapse,
  IconButton as MuiIconButton,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Add as AddIcon,
  ExpandMore as ExpandMoreIcon,
  ChevronRight as ChevronRightIcon,
  DragIndicator as DragIcon,
  SubdirectoryArrowRight as SubdirectoryIcon,
  Category as CategoryIcon,
} from '@mui/icons-material';

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

interface CategoriasTableProps {
  categorias: Categoria[];
  loading?: boolean;
  error?: string | null;
  selectedItems: string[];
  onSelectionChange: (selectedIds: string[]) => void;
  onEdit: (categoriaId: string) => void;
  onDelete: (categoriaId: string) => void;
  onView: (categoriaId: string) => void;
  onAdd: (parentId?: string) => void;
  onReorder?: (draggedId: string, targetId: string) => void;
}

type OrderBy = 'nome' | 'nivel' | 'status' | 'totalNichos' | 'totalKeywords' | 'dataCriacao';
type OrderDirection = 'asc' | 'desc';

/**
 * Componente de tabela hierárquica de categorias
 */
const CategoriasTable: React.FC<CategoriasTableProps> = ({
  categorias,
  loading = false,
  error = null,
  selectedItems,
  onSelectionChange,
  onEdit,
  onDelete,
  onView,
  onAdd,
  onReorder,
}) => {
  // Estados
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [orderBy, setOrderBy] = useState<OrderBy>('nome');
  const [orderDirection, setOrderDirection] = useState<OrderDirection>('asc');
  const [expandedRows, setExpandedRows] = useState<string[]>([]);
  const [draggedItem, setDraggedItem] = useState<string | null>(null);

  // Hooks
  const theme = useTheme();

  // Efeitos
  useEffect(() => {
    setPage(0); // Reset para primeira página quando dados mudam
  }, [categorias]);

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
    if (selectedItems.length === categorias.length) {
      onSelectionChange([]);
    } else {
      onSelectionChange(categorias.map(categoria => categoria.id));
    }
  };

  /**
   * Manipula expansão/colapso de linha
   */
  const handleToggleExpanded = (categoriaId: string) => {
    setExpandedRows(prev =>
      prev.includes(categoriaId)
        ? prev.filter(id => id !== categoriaId)
        : [...prev, categoriaId]
    );
  };

  /**
   * Manipula início do drag
   */
  const handleDragStart = (event: React.DragEvent, categoriaId: string) => {
    setDraggedItem(categoriaId);
    event.dataTransfer.effectAllowed = 'move';
  };

  /**
   * Manipula drop
   */
  const handleDrop = (event: React.DragEvent, targetId: string) => {
    event.preventDefault();
    if (draggedItem && draggedItem !== targetId && onReorder) {
      onReorder(draggedItem, targetId);
    }
    setDraggedItem(null);
  };

  /**
   * Manipula drag over
   */
  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  };

  /**
   * Ordena os dados
   */
  const sortData = (data: Categoria[]) => {
    return data.sort((a, b) => {
      let aValue: any = a[orderBy];
      let bValue: any = b[orderBy];

      // Tratamento especial para datas
      if (orderBy === 'dataCriacao' || orderBy === 'dataAtualizacao') {
        aValue = new Date(aValue).getTime();
        bValue = new Date(bValue).getTime();
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
  const renderActions = (categoria: Categoria) => (
    <Box sx={{ display: 'flex', gap: 0.5 }}>
      <Tooltip title="Visualizar">
        <IconButton
          size="small"
          onClick={() => onView(categoria.id)}
        >
          <ViewIcon />
        </IconButton>
      </Tooltip>
      <Tooltip title="Adicionar Subcategoria">
        <IconButton
          size="small"
          onClick={() => onAdd(categoria.id)}
        >
          <AddIcon />
        </IconButton>
      </Tooltip>
      <Tooltip title="Editar">
        <IconButton
          size="small"
          onClick={() => onEdit(categoria.id)}
        >
          <EditIcon />
        </IconButton>
      </Tooltip>
      <Tooltip title="Excluir">
        <IconButton
          size="small"
          color="error"
          onClick={() => onDelete(categoria.id)}
        >
          <DeleteIcon />
        </IconButton>
      </Tooltip>
    </Box>
  );

  /**
   * Renderiza linha da tabela
   */
  const renderTableRow = (categoria: Categoria, level: number = 0) => {
    const isExpanded = expandedRows.includes(categoria.id);
    const hasChildren = categoria.subcategorias.length > 0;
    const isSelected = selectedItems.includes(categoria.id);

    return (
      <React.Fragment key={categoria.id}>
        <TableRow
          hover
          selected={isSelected}
          draggable
          onDragStart={(e) => handleDragStart(e, categoria.id)}
          onDrop={(e) => handleDrop(e, categoria.id)}
          onDragOver={handleDragOver}
          sx={{
            opacity: draggedItem === categoria.id ? 0.5 : 1,
            backgroundColor: draggedItem === categoria.id ? 'action.hover' : 'inherit',
          }}
        >
          <TableCell padding="checkbox">
            <Checkbox
              checked={isSelected}
              onChange={() => handleSelectItem(categoria.id)}
            />
          </TableCell>
          
          <TableCell>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Tooltip title="Arrastar para reordenar">
                <MuiIconButton size="small" sx={{ cursor: 'grab' }}>
                  <DragIcon />
                </MuiIconButton>
              </Tooltip>
              
              {hasChildren && (
                <IconButton
                  size="small"
                  onClick={() => handleToggleExpanded(categoria.id)}
                >
                  {isExpanded ? <ExpandMoreIcon /> : <ChevronRightIcon />}
                </IconButton>
              )}
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: level * 2 }}>
                {level > 0 && <SubdirectoryIcon fontSize="small" color="action" />}
                <CategoryIcon fontSize="small" color="primary" />
                <Typography variant="body2" fontWeight={500}>
                  {categoria.nome}
                </Typography>
                {level > 0 && (
                  <Chip
                    label={`Nível ${categoria.nivel}`}
                    size="small"
                    variant="outlined"
                  />
                )}
              </Box>
            </Box>
          </TableCell>
          
          <TableCell>
            <Typography variant="body2" color="textSecondary" sx={{ maxWidth: 200 }}>
              {categoria.descricao}
            </Typography>
          </TableCell>
          
          <TableCell>
            {renderStatus(categoria.status)}
          </TableCell>
          
          <TableCell align="center">
            <Typography variant="body2" fontWeight={500}>
              {categoria.totalNichos.toLocaleString()}
            </Typography>
          </TableCell>
          
          <TableCell align="center">
            <Typography variant="body2">
              {categoria.totalKeywords.toLocaleString()}
            </Typography>
          </TableCell>
          
          <TableCell align="center">
            <Typography variant="body2">
              {categoria.execucoesRealizadas}
            </Typography>
          </TableCell>
          
          <TableCell>
            <Typography variant="body2">
              {renderDate(categoria.dataCriacao)}
            </Typography>
          </TableCell>
          
          <TableCell align="center">
            {renderActions(categoria)}
          </TableCell>
        </TableRow>

        {/* Subcategorias expandidas */}
        {hasChildren && isExpanded && (
          <TableRow>
            <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={9}>
              <Collapse in={isExpanded} timeout="auto" unmountOnExit>
                <Box sx={{ margin: 1 }}>
                  <Table size="small">
                    <TableBody>
                      {categoria.subcategorias.map(subcat => renderTableRow(subcat, level + 1))}
                    </TableBody>
                  </Table>
                </Box>
              </Collapse>
            </TableCell>
          </TableRow>
        )}
      </React.Fragment>
    );
  };

  // Dados ordenados e paginados
  const sortedData = sortData([...categorias]);
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
                <TableCell><Skeleton variant="text" width={150} /></TableCell>
                <TableCell><Skeleton variant="text" width={200} /></TableCell>
                <TableCell><Skeleton variant="text" width={60} /></TableCell>
                <TableCell><Skeleton variant="text" width={40} /></TableCell>
                <TableCell><Skeleton variant="text" width={60} /></TableCell>
                <TableCell><Skeleton variant="text" width={40} /></TableCell>
                <TableCell><Skeleton variant="text" width={80} /></TableCell>
                <TableCell><Skeleton variant="text" width={120} /></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {Array.from({ length: 5 }).map((_, index) => (
                <TableRow key={index}>
                  <TableCell padding="checkbox">
                    <Skeleton variant="rectangular" width={20} height={20} />
                  </TableCell>
                  <TableCell><Skeleton variant="text" width={120} /></TableCell>
                  <TableCell><Skeleton variant="text" width={180} /></TableCell>
                  <TableCell><Skeleton variant="text" width={50} /></TableCell>
                  <TableCell><Skeleton variant="text" width={30} /></TableCell>
                  <TableCell><Skeleton variant="text" width={50} /></TableCell>
                  <TableCell><Skeleton variant="text" width={30} /></TableCell>
                  <TableCell><Skeleton variant="text" width={70} /></TableCell>
                  <TableCell><Skeleton variant="text" width={100} /></TableCell>
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
                  indeterminate={selectedItems.length > 0 && selectedItems.length < categorias.length}
                  checked={categorias.length > 0 && selectedItems.length === categorias.length}
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
              <TableCell>Descrição</TableCell>
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
                  active={orderBy === 'totalNichos'}
                  direction={orderBy === 'totalNichos' ? orderDirection : 'asc'}
                  onClick={() => handleSort('totalNichos')}
                >
                  Nichos
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
              <TableCell align="center">Execuções</TableCell>
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
            {paginatedData.map((categoria) => renderTableRow(categoria))}
          </TableBody>
        </Table>
      </TableContainer>
      
      <TablePagination
        rowsPerPageOptions={[5, 10, 25, 50]}
        component="div"
        count={categorias.length}
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

export default CategoriasTable; 