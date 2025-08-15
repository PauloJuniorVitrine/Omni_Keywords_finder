/**
 * FilterBar.test.tsx
 * 
 * Testes unitários para o componente FilterBar
 * 
 * Tracing ID: TEST_FILTERS_20250127_001
 * Prompt: CHECKLIST_TESTES_UNITARIOS_REACT.md - Fase 3.3
 * Data: 2025-01-27
 * Ruleset: enterprise_control_layer.yaml
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FilterBar, QuickFilter, SortOption, ViewOption } from '../../../app/components/filters/FilterBar';

// Mock data
const mockQuickFilters: QuickFilter[] = [
  { id: '1', label: 'Ativos', value: true, count: 15, active: true, color: 'green' },
  { id: '2', label: 'Pendentes', value: false, count: 8, active: false, color: 'yellow' },
  { id: '3', label: 'Erro', value: 'error', count: 3, active: false, color: 'red' },
];

const mockSortOptions: SortOption[] = [
  { id: 'name-asc', label: 'Nome A-Z', field: 'name', direction: 'asc' },
  { id: 'name-desc', label: 'Nome Z-A', field: 'name', direction: 'desc' },
  { id: 'date-asc', label: 'Data Antiga', field: 'date', direction: 'asc' },
  { id: 'date-desc', label: 'Data Recente', field: 'date', direction: 'desc' },
];

const mockViewOptions: ViewOption[] = [
  { id: 'grid', label: 'Grade', icon: <div>Grid</div>, type: 'grid' },
  { id: 'list', label: 'Lista', icon: <div>List</div>, type: 'list' },
  { id: 'table', label: 'Tabela', icon: <div>Table</div>, type: 'table' },
];

describe('FilterBar Component', () => {
  const defaultProps = {
    searchValue: '',
    onSearchChange: jest.fn(),
    quickFilters: mockQuickFilters,
    onQuickFilterChange: jest.fn(),
    sortOptions: mockSortOptions,
    currentSort: mockSortOptions[0],
    onSortChange: jest.fn(),
    viewOptions: mockViewOptions,
    currentView: mockViewOptions[0],
    onViewChange: jest.fn(),
    totalResults: 100,
    filteredResults: 26,
    onClearAll: jest.fn(),
    onExport: jest.fn(),
    onRefresh: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização Básica', () => {
    it('deve renderizar com todas as seções visíveis', () => {
      render(<FilterBar {...defaultProps} />);
      
      expect(screen.getByPlaceholderText('Buscar...')).toBeInTheDocument();
      expect(screen.getByText('Ativos')).toBeInTheDocument();
      expect(screen.getByText('Pendentes')).toBeInTheDocument();
      expect(screen.getByText('Erro')).toBeInTheDocument();
      expect(screen.getByText('Nome A-Z')).toBeInTheDocument();
      expect(screen.getByText('Grade')).toBeInTheDocument();
      expect(screen.getByText('100 resultados')).toBeInTheDocument();
    });

    it('deve renderizar em modo compacto', () => {
      render(<FilterBar {...defaultProps} compact={true} />);
      
      const filterBar = screen.getByRole('region', { name: /filtros/i });
      expect(filterBar).toHaveClass('p-2');
    });

    it('deve renderizar com loading state', () => {
      render(<FilterBar {...defaultProps} loading={true} />);
      
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    it('deve renderizar sem seções quando desabilitadas', () => {
      render(
        <FilterBar
          {...defaultProps}
          showSearch={false}
          showQuickFilters={false}
          showSort={false}
          showViewToggle={false}
          showResultsCount={false}
          showActions={false}
        />
      );
      
      expect(screen.queryByPlaceholderText('Buscar...')).not.toBeInTheDocument();
      expect(screen.queryByText('Ativos')).not.toBeInTheDocument();
      expect(screen.queryByText('Nome A-Z')).not.toBeInTheDocument();
      expect(screen.queryByText('Grade')).not.toBeInTheDocument();
      expect(screen.queryByText('100 resultados')).not.toBeInTheDocument();
    });
  });

  describe('Funcionalidade de Busca', () => {
    it('deve chamar onSearchChange ao digitar', async () => {
      const user = userEvent.setup();
      const onSearchChange = jest.fn();
      
      render(<FilterBar {...defaultProps} onSearchChange={onSearchChange} />);
      
      const searchInput = screen.getByPlaceholderText('Buscar...');
      await user.type(searchInput, 'teste');
      
      expect(onSearchChange).toHaveBeenCalledWith('teste');
    });

    it('deve usar placeholder customizado', () => {
      render(<FilterBar {...defaultProps} searchPlaceholder="Buscar keywords..." />);
      
      expect(screen.getByPlaceholderText('Buscar keywords...')).toBeInTheDocument();
    });

    it('deve mostrar valor inicial da busca', () => {
      render(<FilterBar {...defaultProps} searchValue="valor inicial" />);
      
      const searchInput = screen.getByPlaceholderText('Buscar...') as HTMLInputElement;
      expect(searchInput.value).toBe('valor inicial');
    });
  });

  describe('Filtros Rápidos', () => {
    it('deve renderizar filtros com cores corretas', () => {
      render(<FilterBar {...defaultProps} />);
      
      const ativoFilter = screen.getByText('Ativos').closest('div');
      const pendenteFilter = screen.getByText('Pendentes').closest('div');
      const erroFilter = screen.getByText('Erro').closest('div');
      
      expect(ativoFilter).toHaveClass('bg-green-100', 'text-green-800');
      expect(pendenteFilter).toHaveClass('bg-gray-100', 'text-gray-700');
      expect(erroFilter).toHaveClass('bg-gray-100', 'text-gray-700');
    });

    it('deve mostrar contadores nos filtros', () => {
      render(<FilterBar {...defaultProps} />);
      
      expect(screen.getByText('15')).toBeInTheDocument();
      expect(screen.getByText('8')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
    });

    it('deve chamar onQuickFilterChange ao clicar em filtro', async () => {
      const user = userEvent.setup();
      const onQuickFilterChange = jest.fn();
      
      render(<FilterBar {...defaultProps} onQuickFilterChange={onQuickFilterChange} />);
      
      const pendenteFilter = screen.getByText('Pendentes');
      await user.click(pendenteFilter);
      
      expect(onQuickFilterChange).toHaveBeenCalledWith(
        expect.arrayContaining([
          expect.objectContaining({ id: '2', active: true })
        ])
      );
    });

    it('deve permitir remoção de filtros quando onRemove fornecido', async () => {
      const user = userEvent.setup();
      const onQuickFilterChange = jest.fn();
      
      render(<FilterBar {...defaultProps} onQuickFilterChange={onQuickFilterChange} />);
      
      const removeButtons = screen.getAllByRole('button', { name: /remover/i });
      await user.click(removeButtons[0]);
      
      expect(onQuickFilterChange).toHaveBeenCalledWith(
        expect.arrayContaining([
          expect.objectContaining({ id: '2' }),
          expect.objectContaining({ id: '3' })
        ])
      );
    });
  });

  describe('Ordenação', () => {
    it('deve mostrar opções de ordenação', () => {
      render(<FilterBar {...defaultProps} />);
      
      expect(screen.getByText('Nome A-Z')).toBeInTheDocument();
      expect(screen.getByText('Nome Z-A')).toBeInTheDocument();
      expect(screen.getByText('Data Antiga')).toBeInTheDocument();
      expect(screen.getByText('Data Recente')).toBeInTheDocument();
    });

    it('deve destacar ordenação atual', () => {
      render(<FilterBar {...defaultProps} currentSort={mockSortOptions[1]} />);
      
      const currentSortButton = screen.getByText('Nome Z-A').closest('button');
      expect(currentSortButton).toHaveClass('bg-blue-100', 'text-blue-800');
    });

    it('deve chamar onSortChange ao selecionar ordenação', async () => {
      const user = userEvent.setup();
      const onSortChange = jest.fn();
      
      render(<FilterBar {...defaultProps} onSortChange={onSortChange} />);
      
      const sortButton = screen.getByText('Nome Z-A');
      await user.click(sortButton);
      
      expect(onSortChange).toHaveBeenCalledWith(mockSortOptions[1]);
    });
  });

  describe('Alternância de Visualização', () => {
    it('deve mostrar opções de visualização', () => {
      render(<FilterBar {...defaultProps} />);
      
      expect(screen.getByText('Grade')).toBeInTheDocument();
      expect(screen.getByText('Lista')).toBeInTheDocument();
      expect(screen.getByText('Tabela')).toBeInTheDocument();
    });

    it('deve destacar visualização atual', () => {
      render(<FilterBar {...defaultProps} currentView={mockViewOptions[1]} />);
      
      const currentViewButton = screen.getByText('Lista').closest('button');
      expect(currentViewButton).toHaveClass('bg-blue-100', 'text-blue-800');
    });

    it('deve chamar onViewChange ao selecionar visualização', async () => {
      const user = userEvent.setup();
      const onViewChange = jest.fn();
      
      render(<FilterBar {...defaultProps} onViewChange={onViewChange} />);
      
      const viewButton = screen.getByText('Lista');
      await user.click(viewButton);
      
      expect(onViewChange).toHaveBeenCalledWith(mockViewOptions[1]);
    });
  });

  describe('Contadores de Resultados', () => {
    it('deve mostrar total de resultados', () => {
      render(<FilterBar {...defaultProps} />);
      
      expect(screen.getByText('100 resultados')).toBeInTheDocument();
    });

    it('deve mostrar resultados filtrados quando diferente do total', () => {
      render(<FilterBar {...defaultProps} filteredResults={26} />);
      
      expect(screen.getByText('26 de 100 resultados')).toBeInTheDocument();
    });

    it('deve mostrar apenas total quando filteredResults igual ao total', () => {
      render(<FilterBar {...defaultProps} filteredResults={100} />);
      
      expect(screen.getByText('100 resultados')).toBeInTheDocument();
      expect(screen.queryByText('de 100 resultados')).not.toBeInTheDocument();
    });
  });

  describe('Ações', () => {
    it('deve chamar onClearAll ao clicar em limpar tudo', async () => {
      const user = userEvent.setup();
      const onClearAll = jest.fn();
      
      render(<FilterBar {...defaultProps} onClearAll={onClearAll} />);
      
      const clearButton = screen.getByRole('button', { name: /limpar tudo/i });
      await user.click(clearButton);
      
      expect(onClearAll).toHaveBeenCalled();
    });

    it('deve chamar onExport ao clicar em exportar', async () => {
      const user = userEvent.setup();
      const onExport = jest.fn();
      
      render(<FilterBar {...defaultProps} onExport={onExport} />);
      
      const exportButton = screen.getByRole('button', { name: /exportar/i });
      await user.click(exportButton);
      
      expect(onExport).toHaveBeenCalled();
    });

    it('deve chamar onRefresh ao clicar em atualizar', async () => {
      const user = userEvent.setup();
      const onRefresh = jest.fn();
      
      render(<FilterBar {...defaultProps} onRefresh={onRefresh} />);
      
      const refreshButton = screen.getByRole('button', { name: /atualizar/i });
      await user.click(refreshButton);
      
      expect(onRefresh).toHaveBeenCalled();
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter roles e labels apropriados', () => {
      render(<FilterBar {...defaultProps} />);
      
      expect(screen.getByRole('region', { name: /filtros/i })).toBeInTheDocument();
      expect(screen.getByRole('searchbox')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /limpar tudo/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /exportar/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /atualizar/i })).toBeInTheDocument();
    });

    it('deve ser navegável por teclado', async () => {
      const user = userEvent.setup();
      render(<FilterBar {...defaultProps} />);
      
      const searchInput = screen.getByPlaceholderText('Buscar...');
      searchInput.focus();
      
      await user.tab();
      expect(screen.getByText('Ativos')).toHaveFocus();
      
      await user.tab();
      expect(screen.getByText('Pendentes')).toHaveFocus();
    });

    it('deve ter aria-labels apropriados', () => {
      render(<FilterBar {...defaultProps} />);
      
      const searchInput = screen.getByPlaceholderText('Buscar...');
      expect(searchInput).toHaveAttribute('aria-label', 'Buscar');
      
      const clearButton = screen.getByRole('button', { name: /limpar tudo/i });
      expect(clearButton).toHaveAttribute('aria-label', 'Limpar todos os filtros');
    });
  });

  describe('Performance', () => {
    it('deve debounce mudanças de busca', async () => {
      jest.useFakeTimers();
      const onSearchChange = jest.fn();
      
      render(<FilterBar {...defaultProps} onSearchChange={onSearchChange} />);
      
      const searchInput = screen.getByPlaceholderText('Buscar...');
      fireEvent.change(searchInput, { target: { value: 'a' } });
      fireEvent.change(searchInput, { target: { value: 'ab' } });
      fireEvent.change(searchInput, { target: { value: 'abc' } });
      
      expect(onSearchChange).not.toHaveBeenCalled();
      
      jest.runAllTimers();
      
      await waitFor(() => {
        expect(onSearchChange).toHaveBeenCalledWith('abc');
      });
      
      jest.useRealTimers();
    });

    it('deve memoizar filtros para evitar re-renders desnecessários', () => {
      const { rerender } = render(<FilterBar {...defaultProps} />);
      
      const initialRender = screen.getByText('Ativos');
      
      rerender(<FilterBar {...defaultProps} />);
      
      const reRender = screen.getByText('Ativos');
      expect(reRender).toBe(initialRender);
    });
  });

  describe('Casos Extremos', () => {
    it('deve lidar com filtros vazios', () => {
      render(<FilterBar {...defaultProps} quickFilters={[]} />);
      
      expect(screen.queryByText('Ativos')).not.toBeInTheDocument();
      expect(screen.getByText('Nenhum filtro disponível')).toBeInTheDocument();
    });

    it('deve lidar com opções de ordenação vazias', () => {
      render(<FilterBar {...defaultProps} sortOptions={[]} />);
      
      expect(screen.queryByText('Nome A-Z')).not.toBeInTheDocument();
      expect(screen.getByText('Sem opções de ordenação')).toBeInTheDocument();
    });

    it('deve lidar com opções de visualização vazias', () => {
      render(<FilterBar {...defaultProps} viewOptions={[]} />);
      
      expect(screen.queryByText('Grade')).not.toBeInTheDocument();
      expect(screen.getByText('Sem opções de visualização')).toBeInTheDocument();
    });

    it('deve lidar com valores muito longos', () => {
      const longFilters: QuickFilter[] = [
        { 
          id: '1', 
          label: 'Este é um filtro com um nome muito longo que pode quebrar o layout da interface', 
          value: true, 
          count: 999999 
        }
      ];
      
      render(<FilterBar {...defaultProps} quickFilters={longFilters} />);
      
      const longFilter = screen.getByText(/Este é um filtro com um nome muito longo/);
      expect(longFilter).toBeInTheDocument();
      expect(longFilter.closest('div')).toHaveClass('truncate');
    });

    it('deve lidar com valores nulos/undefined', () => {
      render(
        <FilterBar
          {...defaultProps}
          searchValue={undefined}
          totalResults={undefined}
          filteredResults={undefined}
        />
      );
      
      expect(screen.getByPlaceholderText('Buscar...')).toBeInTheDocument();
      expect(screen.getByText('0 resultados')).toBeInTheDocument();
    });
  });

  describe('Variantes do Componente', () => {
    it('deve renderizar CompactFilterBar corretamente', () => {
      const { CompactFilterBar } = require('../../../app/components/filters/FilterBar');
      render(<CompactFilterBar {...defaultProps} />);
      
      const filterBar = screen.getByRole('region', { name: /filtros/i });
      expect(filterBar).toHaveClass('p-2', 'text-sm');
    });

    it('deve renderizar MinimalFilterBar corretamente', () => {
      const { MinimalFilterBar } = require('../../../app/components/filters/FilterBar');
      render(<MinimalFilterBar {...defaultProps} />);
      
      const filterBar = screen.getByRole('region', { name: /filtros/i });
      expect(filterBar).toHaveClass('p-1', 'text-xs');
    });
  });
}); 