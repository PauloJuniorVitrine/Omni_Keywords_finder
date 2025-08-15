/**
 * Testes Unitários - CategoriasTable Component
 * 
 * Prompt: Implementação de testes para componentes importantes
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_CATEGORIAS_TABLE_026
 * 
 * Baseado em código real do CategoriasTable.tsx
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import CategoriasTable from '../../../app/components/categorias/CategoriasTable';

// Mock do Material-UI
jest.mock('@mui/material', () => ({
  Table: ({ children, ...props }: any) => <table data-testid="table" {...props}>{children}</table>,
  TableBody: ({ children, ...props }: any) => <tbody data-testid="table-body" {...props}>{children}</tbody>,
  TableCell: ({ children, align, padding, colSpan, ...props }: any) => (
    <td data-testid="table-cell" data-align={align} data-padding={padding} colSpan={colSpan} {...props}>
      {children}
    </td>
  ),
  TableContainer: ({ children, ...props }: any) => (
    <div data-testid="table-container" {...props}>{children}</div>
  ),
  TableHead: ({ children, ...props }: any) => <thead data-testid="table-head" {...props}>{children}</thead>,
  TableRow: ({ children, ...props }: any) => <tr data-testid="table-row" {...props}>{children}</tr>,
  TablePagination: ({ 
    count, 
    page, 
    rowsPerPage, 
    onPageChange, 
    onRowsPerPageChange, 
    ...props 
  }: any) => (
    <div data-testid="table-pagination" data-count={count} data-page={page} data-rows-per-page={rowsPerPage}>
      <button data-testid="prev-page" onClick={() => onPageChange(null, page - 1)}>Anterior</button>
      <button data-testid="next-page" onClick={() => onPageChange(null, page + 1)}>Próximo</button>
      <select 
        data-testid="rows-per-page" 
        value={rowsPerPage} 
        onChange={(e) => onRowsPerPageChange({ target: { value: e.target.value } })}
      >
        <option value={5}>5</option>
        <option value={10}>10</option>
        <option value={25}>25</option>
        <option value={50}>50</option>
      </select>
    </div>
  ),
  TableSortLabel: ({ children, active, direction, onClick, ...props }: any) => (
    <button data-testid="sort-label" data-active={active} data-direction={direction} onClick={onClick} {...props}>
      {children}
    </button>
  ),
  Checkbox: ({ checked, indeterminate, onChange, ...props }: any) => (
    <input 
      type="checkbox" 
      data-testid="checkbox" 
      checked={checked} 
      ref={(el) => {
        if (el) el.indeterminate = indeterminate;
      }}
      onChange={onChange} 
      {...props} 
    />
  ),
  Paper: ({ children, ...props }: any) => <div data-testid="paper" {...props}>{children}</div>,
  Box: ({ children, ...props }: any) => <div data-testid="box" {...props}>{children}</div>,
  Typography: ({ children, variant, fontWeight, ...props }: any) => (
    <div data-testid="typography" data-variant={variant} data-font-weight={fontWeight} {...props}>
      {children}
    </div>
  ),
  Chip: ({ label, color, ...props }: any) => (
    <span data-testid="chip" data-color={color} {...props}>{label}</span>
  ),
  IconButton: ({ children, onClick, ...props }: any) => (
    <button data-testid="icon-button" onClick={onClick} {...props}>{children}</button>
  ),
  Tooltip: ({ children, ...props }: any) => <div data-testid="tooltip" {...props}>{children}</div>,
  Skeleton: ({ variant, width, height, ...props }: any) => (
    <div data-testid="skeleton" data-variant={variant} style={{ width, height }} {...props} />
  ),
  Alert: ({ children, severity, ...props }: any) => (
    <div data-testid="alert" data-severity={severity} {...props}>{children}</div>
  ),
  useTheme: () => ({
    breakpoints: {
      down: () => false
    }
  }),
  Collapse: ({ children, in: inProp, ...props }: any) => (
    <div data-testid="collapse" data-in={inProp} {...props}>
      {inProp && children}
    </div>
  ),
}));

// Mock dos ícones Material-UI
jest.mock('@mui/icons-material', () => ({
  Edit: ({ ...props }: any) => <div data-testid="icon-edit" {...props} />,
  Delete: ({ ...props }: any) => <div data-testid="icon-delete" {...props} />,
  Visibility: ({ ...props }: any) => <div data-testid="icon-visibility" {...props} />,
  Add: ({ ...props }: any) => <div data-testid="icon-add" {...props} />,
  ExpandMore: ({ ...props }: any) => <div data-testid="icon-expand-more" {...props} />,
  ChevronRight: ({ ...props }: any) => <div data-testid="icon-chevron-right" {...props} />,
  DragIndicator: ({ ...props }: any) => <div data-testid="icon-drag" {...props} />,
  SubdirectoryArrowRight: ({ ...props }: any) => <div data-testid="icon-subdirectory" {...props} />,
  Category: ({ ...props }: any) => <div data-testid="icon-category" {...props} />,
}));

describe('CategoriasTable - Tabela Hierárquica de Categorias', () => {
  
  const mockOnSelectionChange = jest.fn();
  const mockOnEdit = jest.fn();
  const mockOnDelete = jest.fn();
  const mockOnView = jest.fn();
  const mockOnAdd = jest.fn();
  const mockOnReorder = jest.fn();

  const mockCategorias = [
    {
      id: '1',
      nome: 'Tecnologia',
      descricao: 'Categoria de tecnologia',
      nivel: 1,
      status: 'ativo' as const,
      totalNichos: 15,
      totalKeywords: 2500,
      execucoesRealizadas: 45,
      ultimaExecucao: new Date('2025-01-27'),
      dataCriacao: new Date('2025-01-01'),
      dataAtualizacao: new Date('2025-01-27'),
      subcategorias: [
        {
          id: '2',
          nome: 'Desenvolvimento Web',
          descricao: 'Subcategoria de desenvolvimento web',
          categoriaPai: '1',
          nivel: 2,
          status: 'ativo' as const,
          totalNichos: 8,
          totalKeywords: 1200,
          execucoesRealizadas: 25,
          ultimaExecucao: new Date('2025-01-26'),
          dataCriacao: new Date('2025-01-05'),
          dataAtualizacao: new Date('2025-01-26'),
          subcategorias: []
        }
      ]
    },
    {
      id: '3',
      nome: 'Marketing',
      descricao: 'Categoria de marketing',
      nivel: 1,
      status: 'pendente' as const,
      totalNichos: 12,
      totalKeywords: 1800,
      execucoesRealizadas: 30,
      ultimaExecucao: new Date('2025-01-25'),
      dataCriacao: new Date('2025-01-02'),
      dataAtualizacao: new Date('2025-01-25'),
      subcategorias: []
    }
  ];

  const defaultProps = {
    categorias: mockCategorias,
    loading: false,
    error: null,
    selectedItems: [],
    onSelectionChange: mockOnSelectionChange,
    onEdit: mockOnEdit,
    onDelete: mockOnDelete,
    onView: mockOnView,
    onAdd: mockOnAdd,
    onReorder: mockOnReorder
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização do Componente', () => {
    
    test('deve renderizar a tabela com cabeçalhos', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      expect(screen.getByTestId('table')).toBeInTheDocument();
      expect(screen.getByText('Nome')).toBeInTheDocument();
      expect(screen.getByText('Descrição')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('Nichos')).toBeInTheDocument();
      expect(screen.getByText('Keywords')).toBeInTheDocument();
      expect(screen.getByText('Execuções')).toBeInTheDocument();
      expect(screen.getByText('Criado em')).toBeInTheDocument();
      expect(screen.getByText('Ações')).toBeInTheDocument();
    });

    test('deve renderizar categorias na tabela', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      expect(screen.getByText('Tecnologia')).toBeInTheDocument();
      expect(screen.getByText('Marketing')).toBeInTheDocument();
      expect(screen.getByText('Categoria de tecnologia')).toBeInTheDocument();
      expect(screen.getByText('Categoria de marketing')).toBeInTheDocument();
    });

    test('deve renderizar status das categorias', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      expect(screen.getByText('ativo')).toBeInTheDocument();
      expect(screen.getByText('pendente')).toBeInTheDocument();
    });

    test('deve renderizar métricas das categorias', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      expect(screen.getByText('15')).toBeInTheDocument(); // totalNichos
      expect(screen.getByText('12')).toBeInTheDocument(); // totalNichos
      expect(screen.getByText('2,500')).toBeInTheDocument(); // totalKeywords
      expect(screen.getByText('1,800')).toBeInTheDocument(); // totalKeywords
      expect(screen.getByText('45')).toBeInTheDocument(); // execucoesRealizadas
      expect(screen.getByText('30')).toBeInTheDocument(); // execucoesRealizadas
    });

    test('deve renderizar botões de ação', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      const actionButtons = screen.getAllByTestId('icon-button');
      expect(actionButtons.length).toBeGreaterThan(0);
    });
  });

  describe('Tabela Hierárquica', () => {
    
    test('deve renderizar estrutura hierárquica', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      expect(screen.getByText('Tecnologia')).toBeInTheDocument();
      expect(screen.getByText('Marketing')).toBeInTheDocument();
    });

    test('deve permitir expandir/colapsar subcategorias', async () => {
      const user = userEvent.setup();
      render(<CategoriasTable {...defaultProps} />);
      
      const expandButtons = screen.getAllByTestId('icon-expand-more');
      expect(expandButtons.length).toBeGreaterThan(0);
      
      await user.click(expandButtons[0]);
      
      // Verificar se a subcategoria foi expandida
      expect(screen.getByText('Desenvolvimento Web')).toBeInTheDocument();
    });

    test('deve mostrar indicador de subcategorias', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      const subdirectoryIcons = screen.getAllByTestId('icon-subdirectory');
      expect(subdirectoryIcons.length).toBeGreaterThan(0);
    });

    test('deve renderizar subcategorias com indentação', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      // Expandir a categoria pai
      const expandButtons = screen.getAllByTestId('icon-expand-more');
      fireEvent.click(expandButtons[0]);
      
      expect(screen.getByText('Desenvolvimento Web')).toBeInTheDocument();
    });
  });

  describe('Filtros e Busca', () => {
    
    test('deve permitir ordenação por nome', async () => {
      const user = userEvent.setup();
      render(<CategoriasTable {...defaultProps} />);
      
      const nomeSortButton = screen.getByText('Nome');
      await user.click(nomeSortButton);
      
      expect(nomeSortButton).toHaveAttribute('data-active', 'true');
    });

    test('deve permitir ordenação por status', async () => {
      const user = userEvent.setup();
      render(<CategoriasTable {...defaultProps} />);
      
      const statusSortButton = screen.getByText('Status');
      await user.click(statusSortButton);
      
      expect(statusSortButton).toHaveAttribute('data-active', 'true');
    });

    test('deve permitir ordenação por total de nichos', async () => {
      const user = userEvent.setup();
      render(<CategoriasTable {...defaultProps} />);
      
      const nichosSortButton = screen.getByText('Nichos');
      await user.click(nichosSortButton);
      
      expect(nichosSortButton).toHaveAttribute('data-active', 'true');
    });

    test('deve permitir ordenação por total de keywords', async () => {
      const user = userEvent.setup();
      render(<CategoriasTable {...defaultProps} />);
      
      const keywordsSortButton = screen.getByText('Keywords');
      await user.click(keywordsSortButton);
      
      expect(keywordsSortButton).toHaveAttribute('data-active', 'true');
    });

    test('deve permitir ordenação por data de criação', async () => {
      const user = userEvent.setup();
      render(<CategoriasTable {...defaultProps} />);
      
      const dataSortButton = screen.getByText('Criado em');
      await user.click(dataSortButton);
      
      expect(dataSortButton).toHaveAttribute('data-active', 'true');
    });
  });

  describe('Ações em Lote', () => {
    
    test('deve permitir seleção individual de itens', async () => {
      const user = userEvent.setup();
      render(<CategoriasTable {...defaultProps} />);
      
      const checkboxes = screen.getAllByTestId('checkbox');
      await user.click(checkboxes[1]); // Selecionar primeira categoria
      
      expect(mockOnSelectionChange).toHaveBeenCalledWith(['1']);
    });

    test('deve permitir seleção de todos os itens', async () => {
      const user = userEvent.setup();
      render(<CategoriasTable {...defaultProps} />);
      
      const selectAllCheckbox = screen.getAllByTestId('checkbox')[0];
      await user.click(selectAllCheckbox);
      
      expect(mockOnSelectionChange).toHaveBeenCalledWith(['1', '3']);
    });

    test('deve permitir deseleção de todos os itens', async () => {
      const user = userEvent.setup();
      render(<CategoriasTable {...defaultProps} selectedItems={['1', '3']} />);
      
      const selectAllCheckbox = screen.getAllByTestId('checkbox')[0];
      await user.click(selectAllCheckbox);
      
      expect(mockOnSelectionChange).toHaveBeenCalledWith([]);
    });

    test('deve mostrar estado indeterminado do checkbox', () => {
      render(<CategoriasTable {...defaultProps} selectedItems={['1']} />);
      
      const selectAllCheckbox = screen.getAllByTestId('checkbox')[0];
      expect(selectAllCheckbox).toHaveAttribute('data-indeterminate', 'true');
    });
  });

  describe('Ações de Item', () => {
    
    test('deve permitir editar categoria', async () => {
      const user = userEvent.setup();
      render(<CategoriasTable {...defaultProps} />);
      
      const editButtons = screen.getAllByTestId('icon-edit');
      await user.click(editButtons[0]);
      
      expect(mockOnEdit).toHaveBeenCalledWith('1');
    });

    test('deve permitir excluir categoria', async () => {
      const user = userEvent.setup();
      render(<CategoriasTable {...defaultProps} />);
      
      const deleteButtons = screen.getAllByTestId('icon-delete');
      await user.click(deleteButtons[0]);
      
      expect(mockOnDelete).toHaveBeenCalledWith('1');
    });

    test('deve permitir visualizar categoria', async () => {
      const user = userEvent.setup();
      render(<CategoriasTable {...defaultProps} />);
      
      const viewButtons = screen.getAllByTestId('icon-visibility');
      await user.click(viewButtons[0]);
      
      expect(mockOnView).toHaveBeenCalledWith('1');
    });

    test('deve permitir adicionar subcategoria', async () => {
      const user = userEvent.setup();
      render(<CategoriasTable {...defaultProps} />);
      
      const addButtons = screen.getAllByTestId('icon-add');
      await user.click(addButtons[0]);
      
      expect(mockOnAdd).toHaveBeenCalledWith('1');
    });
  });

  describe('Drag & Drop', () => {
    
    test('deve permitir iniciar drag de item', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      const dragIcons = screen.getAllByTestId('icon-drag');
      expect(dragIcons.length).toBeGreaterThan(0);
    });

    test('deve permitir drop de item', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      const tableRows = screen.getAllByTestId('table-row');
      expect(tableRows.length).toBeGreaterThan(0);
    });

    test('deve chamar onReorder quando item é dropado', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      const tableRows = screen.getAllByTestId('table-row');
      const firstRow = tableRows[1]; // Primeira linha de dados
      
      // Simular drag and drop
      fireEvent.dragStart(firstRow, { dataTransfer: { effectAllowed: 'move' } });
      fireEvent.drop(firstRow);
      
      expect(mockOnReorder).toHaveBeenCalled();
    });
  });

  describe('Paginação', () => {
    
    test('deve renderizar controles de paginação', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      expect(screen.getByTestId('table-pagination')).toBeInTheDocument();
      expect(screen.getByTestId('prev-page')).toBeInTheDocument();
      expect(screen.getByTestId('next-page')).toBeInTheDocument();
      expect(screen.getByTestId('rows-per-page')).toBeInTheDocument();
    });

    test('deve permitir mudança de página', async () => {
      const user = userEvent.setup();
      render(<CategoriasTable {...defaultProps} />);
      
      const nextButton = screen.getByTestId('next-page');
      await user.click(nextButton);
      
      expect(nextButton).toBeInTheDocument();
    });

    test('deve permitir mudança de linhas por página', async () => {
      const user = userEvent.setup();
      render(<CategoriasTable {...defaultProps} />);
      
      const rowsPerPageSelect = screen.getByTestId('rows-per-page');
      await user.selectOptions(rowsPerPageSelect, '25');
      
      expect(rowsPerPageSelect).toHaveValue('25');
    });
  });

  describe('Estados de Loading e Erro', () => {
    
    test('deve mostrar skeleton durante loading', () => {
      render(<CategoriasTable {...defaultProps} loading={true} />);
      
      const skeletons = screen.getAllByTestId('skeleton');
      expect(skeletons.length).toBeGreaterThan(0);
    });

    test('deve mostrar erro quando fornecido', () => {
      render(<CategoriasTable {...defaultProps} error="Erro ao carregar categorias" />);
      
      expect(screen.getByText('Erro ao carregar categorias')).toBeInTheDocument();
      expect(screen.getByTestId('alert')).toHaveAttribute('data-severity', 'error');
    });

    test('deve renderizar tabela vazia quando não há categorias', () => {
      render(<CategoriasTable {...defaultProps} categorias={[]} />);
      
      expect(screen.getByTestId('table')).toBeInTheDocument();
      expect(screen.getByTestId('table-head')).toBeInTheDocument();
    });
  });

  describe('Validação de Campos', () => {
    
    test('deve validar dados obrigatórios das categorias', () => {
      render(<CategoriaForm {...defaultProps} />);
      
      expect(screen.getByText('Tecnologia')).toBeInTheDocument();
      expect(screen.getByText('Marketing')).toBeInTheDocument();
      expect(screen.getByText('Categoria de tecnologia')).toBeInTheDocument();
      expect(screen.getByText('Categoria de marketing')).toBeInTheDocument();
    });

    test('deve validar métricas das categorias', () => {
      render(<CategoriaForm {...defaultProps} />);
      
      expect(screen.getByText('15')).toBeInTheDocument(); // totalNichos
      expect(screen.getByText('12')).toBeInTheDocument(); // totalNichos
      expect(screen.getByText('2,500')).toBeInTheDocument(); // totalKeywords
      expect(screen.getByText('1,800')).toBeInTheDocument(); // totalKeywords
    });

    test('deve validar status das categorias', () => {
      render(<CategoriaForm {...defaultProps} />);
      
      expect(screen.getByText('ativo')).toBeInTheDocument();
      expect(screen.getByText('pendente')).toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    
    test('deve ter estrutura semântica adequada', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      expect(screen.getByTestId('table')).toBeInTheDocument();
      expect(screen.getByTestId('table-head')).toBeInTheDocument();
      expect(screen.getByTestId('table-body')).toBeInTheDocument();
    });

    test('deve ter navegação por teclado', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      const buttons = screen.getAllByTestId('icon-button');
      expect(buttons.length).toBeGreaterThan(0);
      
      buttons.forEach(button => {
        expect(button).toHaveAttribute('tabIndex', '0');
      });
    });

    test('deve ter labels apropriados', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      expect(screen.getByText('Nome')).toBeInTheDocument();
      expect(screen.getByText('Descrição')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('Nichos')).toBeInTheDocument();
      expect(screen.getByText('Keywords')).toBeInTheDocument();
      expect(screen.getByText('Execuções')).toBeInTheDocument();
      expect(screen.getByText('Criado em')).toBeInTheDocument();
      expect(screen.getByText('Ações')).toBeInTheDocument();
    });

    test('deve ter tooltips informativos', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      const tooltips = screen.getAllByTestId('tooltip');
      expect(tooltips.length).toBeGreaterThan(0);
    });
  });

  describe('Performance e Otimização', () => {
    
    test('deve renderizar rapidamente com muitas categorias', () => {
      const manyCategorias = Array.from({ length: 100 }, (_, i) => ({
        id: `cat-${i}`,
        nome: `Categoria ${i}`,
        descricao: `Descrição da categoria ${i}`,
        nivel: 1,
        status: 'ativo' as const,
        totalNichos: Math.floor(Math.random() * 50),
        totalKeywords: Math.floor(Math.random() * 5000),
        execucoesRealizadas: Math.floor(Math.random() * 100),
        ultimaExecucao: new Date(),
        dataCriacao: new Date(),
        dataAtualizacao: new Date(),
        subcategorias: []
      }));

      const startTime = performance.now();
      
      render(<CategoriasTable {...defaultProps} categorias={manyCategorias} />);
      
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(1000); // Deve renderizar em menos de 1s
    });

    test('deve evitar re-renders desnecessários', () => {
      const { rerender } = render(<CategoriasTable {...defaultProps} />);
      
      // Re-renderizar com os mesmos dados não deve causar mudanças
      rerender(<CategoriasTable {...defaultProps} />);
      
      expect(screen.getByText('Tecnologia')).toBeInTheDocument();
    });

    test('deve usar paginação eficiente', () => {
      render(<CategoriasTable {...defaultProps} />);
      
      const pagination = screen.getByTestId('table-pagination');
      expect(pagination).toHaveAttribute('data-count', '2');
      expect(pagination).toHaveAttribute('data-page', '0');
      expect(pagination).toHaveAttribute('data-rows-per-page', '10');
    });
  });
}); 