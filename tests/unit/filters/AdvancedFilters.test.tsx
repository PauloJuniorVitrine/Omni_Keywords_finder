/**
 * AdvancedFilters.test.tsx
 * 
 * Testes unitários para o componente AdvancedFilters
 * 
 * Tracing ID: TEST_FILTERS_20250127_002
 * Prompt: CHECKLIST_TESTES_UNITARIOS_REACT.md - Fase 3.3
 * Data: 2025-01-27
 * Ruleset: enterprise_control_layer.yaml
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { 
  AdvancedFilters, 
  FilterProvider, 
  useFilters,
  FilterConfig, 
  FilterValue,
  FilterType 
} from '../../../app/components/filters/AdvancedFilters';

// Mock data
const mockFilters: FilterConfig[] = [
  {
    id: 'keyword',
    label: 'Palavra-chave',
    type: 'text',
    placeholder: 'Digite uma palavra-chave...',
    validation: { min: 2, max: 50 }
  },
  {
    id: 'status',
    label: 'Status',
    type: 'select',
    options: [
      { label: 'Ativo', value: 'active' },
      { label: 'Pendente', value: 'pending' },
      { label: 'Erro', value: 'error' }
    ]
  },
  {
    id: 'date',
    label: 'Data de Criação',
    type: 'date'
  },
  {
    id: 'priority',
    label: 'Prioridade',
    type: 'number',
    validation: { min: 1, max: 10 }
  },
  {
    id: 'enabled',
    label: 'Habilitado',
    type: 'boolean'
  }
];

const mockValues: FilterValue[] = [
  { id: 'keyword', value: 'teste', operator: 'contains' },
  { id: 'status', value: 'active' }
];

// Componente de teste para usar o contexto
const TestComponent: React.FC = () => {
  const { filters, values, updateValue, getValue, clearFilter } = useFilters();
  
  return (
    <div>
      <div data-testid="filters-count">{filters.length}</div>
      <div data-testid="values-count">{values.length}</div>
      <button 
        onClick={() => updateValue('keyword', 'novo valor')}
        data-testid="update-button"
      >
        Atualizar
      </button>
      <button 
        onClick={() => clearFilter('keyword')}
        data-testid="clear-button"
      >
        Limpar
      </button>
      <div data-testid="keyword-value">{getValue('keyword')}</div>
    </div>
  );
};

describe('AdvancedFilters Component', () => {
  const defaultProps = {
    filters: mockFilters,
    values: mockValues,
    onChange: jest.fn(),
    onApply: jest.fn(),
    onReset: jest.fn(),
    onSave: jest.fn(),
    onLoad: jest.fn(),
    savedFilters: [
      { name: 'Filtro Salvo', values: mockValues }
    ],
    className: '',
    maxVisibleFilters: 6,
    enableSaveLoad: true,
    enableExport: true,
    enableAutoApply: false,
    debounceMs: 300,
    loading: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização Básica', () => {
    it('deve renderizar todos os filtros configurados', () => {
      render(<AdvancedFilters {...defaultProps} />);
      
      expect(screen.getByText('Palavra-chave')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('Data de Criação')).toBeInTheDocument();
      expect(screen.getByText('Prioridade')).toBeInTheDocument();
      expect(screen.getByText('Habilitado')).toBeInTheDocument();
    });

    it('deve renderizar com valores iniciais', () => {
      render(<AdvancedFilters {...defaultProps} />);
      
      const keywordInput = screen.getByPlaceholderText('Digite uma palavra-chave...') as HTMLInputElement;
      expect(keywordInput.value).toBe('teste');
      
      expect(screen.getByDisplayValue('Ativo')).toBeInTheDocument();
    });

    it('deve renderizar em modo compacto', () => {
      render(<AdvancedFilters {...defaultProps} maxVisibleFilters={3} />);
      
      const filterContainer = screen.getByTestId('filters-container');
      expect(filterContainer).toHaveClass('grid-cols-3');
    });

    it('deve renderizar com loading state', () => {
      render(<AdvancedFilters {...defaultProps} loading={true} />);
      
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    });

    it('deve mostrar botão "Mostrar Mais" quando há mais filtros que o limite', () => {
      render(<AdvancedFilters {...defaultProps} maxVisibleFilters={2} />);
      
      expect(screen.getByText('Mostrar Mais (3)')).toBeInTheDocument();
    });
  });

  describe('Tipos de Filtros', () => {
    describe('Filtro de Texto', () => {
      it('deve renderizar input de texto com placeholder', () => {
        render(<AdvancedFilters {...defaultProps} />);
        
        const input = screen.getByPlaceholderText('Digite uma palavra-chave...');
        expect(input).toHaveAttribute('type', 'text');
      });

      it('deve chamar onChange ao digitar', async () => {
        const user = userEvent.setup();
        const onChange = jest.fn();
        
        render(<AdvancedFilters {...defaultProps} onChange={onChange} />);
        
        const input = screen.getByPlaceholderText('Digite uma palavra-chave...');
        await user.type(input, ' novo');
        
        expect(onChange).toHaveBeenCalledWith(
          expect.arrayContaining([
            expect.objectContaining({ id: 'keyword', value: 'teste novo' })
          ])
        );
      });

      it('deve validar entrada conforme regras', async () => {
        const user = userEvent.setup();
        render(<AdvancedFilters {...defaultProps} />);
        
        const input = screen.getByPlaceholderText('Digite uma palavra-chave...');
        await user.clear(input);
        await user.type(input, 'a');
        
        expect(screen.getByText('Mínimo 2 caracteres')).toBeInTheDocument();
      });
    });

    describe('Filtro Select', () => {
      it('deve renderizar dropdown com opções', () => {
        render(<AdvancedFilters {...defaultProps} />);
        
        expect(screen.getByText('Status')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Ativo')).toBeInTheDocument();
      });

      it('deve abrir dropdown ao clicar', async () => {
        const user = userEvent.setup();
        render(<AdvancedFilters {...defaultProps} />);
        
        const select = screen.getByDisplayValue('Ativo');
        await user.click(select);
        
        expect(screen.getByText('Pendente')).toBeInTheDocument();
        expect(screen.getByText('Erro')).toBeInTheDocument();
      });

      it('deve selecionar opção do dropdown', async () => {
        const user = userEvent.setup();
        const onChange = jest.fn();
        
        render(<AdvancedFilters {...defaultProps} onChange={onChange} />);
        
        const select = screen.getByDisplayValue('Ativo');
        await user.click(select);
        await user.click(screen.getByText('Pendente'));
        
        expect(onChange).toHaveBeenCalledWith(
          expect.arrayContaining([
            expect.objectContaining({ id: 'status', value: 'pending' })
          ])
        );
      });
    });

    describe('Filtro de Data', () => {
      it('deve renderizar input de data', () => {
        render(<AdvancedFilters {...defaultProps} />);
        
        const dateInput = screen.getByLabelText('Data de Criação');
        expect(dateInput).toHaveAttribute('type', 'date');
      });

      it('deve atualizar valor da data', async () => {
        const user = userEvent.setup();
        const onChange = jest.fn();
        
        render(<AdvancedFilters {...defaultProps} onChange={onChange} />);
        
        const dateInput = screen.getByLabelText('Data de Criação');
        await user.type(dateInput, '2025-01-27');
        
        expect(onChange).toHaveBeenCalledWith(
          expect.arrayContaining([
            expect.objectContaining({ id: 'date', value: '2025-01-27' })
          ])
        );
      });
    });

    describe('Filtro Numérico', () => {
      it('deve renderizar input numérico', () => {
        render(<AdvancedFilters {...defaultProps} />);
        
        const numberInput = screen.getByLabelText('Prioridade');
        expect(numberInput).toHaveAttribute('type', 'number');
      });

      it('deve validar valores numéricos', async () => {
        const user = userEvent.setup();
        render(<AdvancedFilters {...defaultProps} />);
        
        const numberInput = screen.getByLabelText('Prioridade');
        await user.type(numberInput, '15');
        
        expect(screen.getByText('Valor máximo é 10')).toBeInTheDocument();
      });
    });

    describe('Filtro Boolean', () => {
      it('deve renderizar checkbox', () => {
        render(<AdvancedFilters {...defaultProps} />);
        
        const checkbox = screen.getByLabelText('Habilitado');
        expect(checkbox).toHaveAttribute('type', 'checkbox');
      });

      it('deve alternar valor do checkbox', async () => {
        const user = userEvent.setup();
        const onChange = jest.fn();
        
        render(<AdvancedFilters {...defaultProps} onChange={onChange} />);
        
        const checkbox = screen.getByLabelText('Habilitado');
        await user.click(checkbox);
        
        expect(onChange).toHaveBeenCalledWith(
          expect.arrayContaining([
            expect.objectContaining({ id: 'enabled', value: true })
          ])
        );
      });
    });
  });

  describe('Funcionalidades Avançadas', () => {
    it('deve aplicar filtros ao clicar em aplicar', async () => {
      const user = userEvent.setup();
      const onApply = jest.fn();
      
      render(<AdvancedFilters {...defaultProps} onApply={onApply} />);
      
      const applyButton = screen.getByRole('button', { name: /aplicar/i });
      await user.click(applyButton);
      
      expect(onApply).toHaveBeenCalledWith(mockValues);
    });

    it('deve resetar filtros ao clicar em resetar', async () => {
      const user = userEvent.setup();
      const onReset = jest.fn();
      
      render(<AdvancedFilters {...defaultProps} onReset={onReset} />);
      
      const resetButton = screen.getByRole('button', { name: /resetar/i });
      await user.click(resetButton);
      
      expect(onReset).toHaveBeenCalled();
    });

    it('deve salvar filtros', async () => {
      const user = userEvent.setup();
      const onSave = jest.fn();
      
      render(<AdvancedFilters {...defaultProps} onSave={onSave} />);
      
      const saveButton = screen.getByRole('button', { name: /salvar/i });
      await user.click(saveButton);
      
      const nameInput = screen.getByPlaceholderText('Nome do filtro...');
      await user.type(nameInput, 'Meu Filtro');
      
      const confirmButton = screen.getByRole('button', { name: /confirmar/i });
      await user.click(confirmButton);
      
      expect(onSave).toHaveBeenCalledWith('Meu Filtro', mockValues);
    });

    it('deve carregar filtros salvos', async () => {
      const user = userEvent.setup();
      const onLoad = jest.fn().mockReturnValue(mockValues);
      
      render(<AdvancedFilters {...defaultProps} onLoad={onLoad} />);
      
      const loadButton = screen.getByRole('button', { name: /carregar/i });
      await user.click(loadButton);
      
      const savedFilter = screen.getByText('Filtro Salvo');
      await user.click(savedFilter);
      
      expect(onLoad).toHaveBeenCalledWith('Filtro Salvo');
    });

    it('deve exportar filtros', async () => {
      const user = userEvent.setup();
      render(<AdvancedFilters {...defaultProps} />);
      
      const exportButton = screen.getByRole('button', { name: /exportar/i });
      await user.click(exportButton);
      
      // Verificar se o download foi iniciado
      expect(screen.getByText('Filtros exportados')).toBeInTheDocument();
    });

    it('deve importar filtros', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      render(<AdvancedFilters {...defaultProps} onChange={onChange} />);
      
      const importButton = screen.getByRole('button', { name: /importar/i });
      await user.click(importButton);
      
      const fileInput = screen.getByTestId('file-input');
      const file = new File(['{"filters": []}'], 'filters.json', { type: 'application/json' });
      await user.upload(fileInput, file);
      
      expect(onChange).toHaveBeenCalledWith([]);
    });
  });

  describe('Context e Hook useFilters', () => {
    it('deve fornecer contexto de filtros', () => {
      render(
        <FilterProvider filters={mockFilters} values={mockValues} onChange={jest.fn()}>
          <TestComponent />
        </FilterProvider>
      );
      
      expect(screen.getByTestId('filters-count')).toHaveTextContent('5');
      expect(screen.getByTestId('values-count')).toHaveTextContent('2');
    });

    it('deve atualizar valores via contexto', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      render(
        <FilterProvider filters={mockFilters} values={mockValues} onChange={onChange}>
          <TestComponent />
        </FilterProvider>
      );
      
      const updateButton = screen.getByTestId('update-button');
      await user.click(updateButton);
      
      expect(onChange).toHaveBeenCalledWith(
        expect.arrayContaining([
          expect.objectContaining({ id: 'keyword', value: 'novo valor' })
        ])
      );
    });

    it('deve limpar filtros via contexto', async () => {
      const user = userEvent.setup();
      const onChange = jest.fn();
      
      render(
        <FilterProvider filters={mockFilters} values={mockValues} onChange={onChange}>
          <TestComponent />
        </FilterProvider>
      );
      
      const clearButton = screen.getByTestId('clear-button');
      await user.click(clearButton);
      
      expect(onChange).toHaveBeenCalledWith(
        expect.arrayContaining([
          expect.objectContaining({ id: 'status', value: 'active' })
        ])
      );
    });

    it('deve obter valores via contexto', () => {
      render(
        <FilterProvider filters={mockFilters} values={mockValues} onChange={jest.fn()}>
          <TestComponent />
        </FilterProvider>
      );
      
      expect(screen.getByTestId('keyword-value')).toHaveTextContent('teste');
    });

    it('deve lançar erro se useFilters usado fora do provider', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      expect(() => render(<TestComponent />)).toThrow('useFilters must be used within FilterProvider');
      
      consoleSpy.mockRestore();
    });
  });

  describe('Auto-Apply', () => {
    it('deve aplicar automaticamente quando enableAutoApply é true', async () => {
      const user = userEvent.setup();
      const onApply = jest.fn();
      
      render(<AdvancedFilters {...defaultProps} enableAutoApply={true} onApply={onApply} />);
      
      const input = screen.getByPlaceholderText('Digite uma palavra-chave...');
      await user.type(input, ' novo');
      
      await waitFor(() => {
        expect(onApply).toHaveBeenCalled();
      });
    });

    it('deve debounce mudanças quando auto-apply está ativo', async () => {
      jest.useFakeTimers();
      const onApply = jest.fn();
      
      render(<AdvancedFilters {...defaultProps} enableAutoApply={true} onApply={onApply} />);
      
      const input = screen.getByPlaceholderText('Digite uma palavra-chave...');
      fireEvent.change(input, { target: { value: 'a' } });
      fireEvent.change(input, { target: { value: 'ab' } });
      fireEvent.change(input, { target: { value: 'abc' } });
      
      expect(onApply).not.toHaveBeenCalled();
      
      jest.runAllTimers();
      
      await waitFor(() => {
        expect(onApply).toHaveBeenCalledWith(
          expect.arrayContaining([
            expect.objectContaining({ id: 'keyword', value: 'abc' })
          ])
        );
      });
      
      jest.useRealTimers();
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter labels apropriados', () => {
      render(<AdvancedFilters {...defaultProps} />);
      
      expect(screen.getByLabelText('Palavra-chave')).toBeInTheDocument();
      expect(screen.getByLabelText('Status')).toBeInTheDocument();
      expect(screen.getByLabelText('Data de Criação')).toBeInTheDocument();
      expect(screen.getByLabelText('Prioridade')).toBeInTheDocument();
      expect(screen.getByLabelText('Habilitado')).toBeInTheDocument();
    });

    it('deve ser navegável por teclado', async () => {
      const user = userEvent.setup();
      render(<AdvancedFilters {...defaultProps} />);
      
      const keywordInput = screen.getByPlaceholderText('Digite uma palavra-chave...');
      keywordInput.focus();
      
      await user.tab();
      expect(screen.getByDisplayValue('Ativo')).toHaveFocus();
      
      await user.tab();
      expect(screen.getByLabelText('Data de Criação')).toHaveFocus();
    });

    it('deve ter aria-describedby para validações', () => {
      render(<AdvancedFilters {...defaultProps} />);
      
      const keywordInput = screen.getByPlaceholderText('Digite uma palavra-chave...');
      expect(keywordInput).toHaveAttribute('aria-describedby');
    });

    it('deve ter roles apropriados', () => {
      render(<AdvancedFilters {...defaultProps} />);
      
      expect(screen.getByRole('region', { name: /filtros avançados/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /aplicar/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /resetar/i })).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('deve memoizar filtros para evitar re-renders', () => {
      const { rerender } = render(<AdvancedFilters {...defaultProps} />);
      
      const initialRender = screen.getByText('Palavra-chave');
      
      rerender(<AdvancedFilters {...defaultProps} />);
      
      const reRender = screen.getByText('Palavra-chave');
      expect(reRender).toBe(initialRender);
    });

    it('deve limitar número de filtros visíveis', () => {
      const manyFilters: FilterConfig[] = Array.from({ length: 10 }, (_, i) => ({
        id: `filter-${i}`,
        label: `Filtro ${i}`,
        type: 'text' as FilterType
      }));
      
      render(<AdvancedFilters {...defaultProps} filters={manyFilters} maxVisibleFilters={5} />);
      
      expect(screen.getByText('Filtro 0')).toBeInTheDocument();
      expect(screen.getByText('Filtro 4')).toBeInTheDocument();
      expect(screen.queryByText('Filtro 5')).not.toBeInTheDocument();
      expect(screen.getByText('Mostrar Mais (5)')).toBeInTheDocument();
    });
  });

  describe('Casos Extremos', () => {
    it('deve lidar com filtros vazios', () => {
      render(<AdvancedFilters {...defaultProps} filters={[]} />);
      
      expect(screen.getByText('Nenhum filtro configurado')).toBeInTheDocument();
    });

    it('deve lidar com valores vazios', () => {
      render(<AdvancedFilters {...defaultProps} values={[]} />);
      
      const keywordInput = screen.getByPlaceholderText('Digite uma palavra-chave...') as HTMLInputElement;
      expect(keywordInput.value).toBe('');
    });

    it('deve lidar com filtros com dependências', () => {
      const dependentFilters: FilterConfig[] = [
        {
          id: 'category',
          label: 'Categoria',
          type: 'select',
          options: [
            { label: 'Tecnologia', value: 'tech' },
            { label: 'Marketing', value: 'marketing' }
          ]
        },
        {
          id: 'subcategory',
          label: 'Subcategoria',
          type: 'select',
          dependencies: ['category']
        }
      ];
      
      render(<AdvancedFilters {...defaultProps} filters={dependentFilters} />);
      
      expect(screen.getByText('Categoria')).toBeInTheDocument();
      expect(screen.getByText('Subcategoria')).toBeInTheDocument();
    });

    it('deve lidar com filtros com validações complexas', () => {
      const complexFilters: FilterConfig[] = [
        {
          id: 'email',
          label: 'Email',
          type: 'text',
          validation: {
            pattern: '^[^@]+@[^@]+\\.[^@]+$',
            message: 'Email inválido'
          }
        }
      ];
      
      render(<AdvancedFilters {...defaultProps} filters={complexFilters} />);
      
      const emailInput = screen.getByLabelText('Email');
      fireEvent.change(emailInput, { target: { value: 'email-invalido' } });
      
      expect(screen.getByText('Email inválido')).toBeInTheDocument();
    });

    it('deve lidar com operadores customizados', () => {
      const customFilters: FilterConfig[] = [
        {
          id: 'price',
          label: 'Preço',
          type: 'number',
          validation: { min: 0, max: 1000 }
        }
      ];
      
      render(<AdvancedFilters {...defaultProps} filters={customFilters} />);
      
      const priceInput = screen.getByLabelText('Preço');
      fireEvent.change(priceInput, { target: { value: '500' } });
      
      // Verificar se o operador padrão é aplicado
      expect(screen.getByDisplayValue('500')).toBeInTheDocument();
    });
  });

  describe('Integração com Sistema', () => {
    it('deve integrar com sistema de temas', () => {
      render(<AdvancedFilters {...defaultProps} />);
      
      const container = screen.getByTestId('filters-container');
      expect(container).toHaveClass('dark:bg-gray-800');
    });

    it('deve integrar com sistema de notificações', async () => {
      const user = userEvent.setup();
      render(<AdvancedFilters {...defaultProps} />);
      
      const saveButton = screen.getByRole('button', { name: /salvar/i });
      await user.click(saveButton);
      
      // Verificar se notificação é exibida
      expect(screen.getByText('Filtro salvo com sucesso')).toBeInTheDocument();
    });

    it('deve integrar com sistema de analytics', () => {
      const analyticsSpy = jest.spyOn(console, 'log');
      
      render(<AdvancedFilters {...defaultProps} />);
      
      // Simular evento de analytics
      fireEvent.click(screen.getByRole('button', { name: /aplicar/i }));
      
      expect(analyticsSpy).toHaveBeenCalledWith('filter_applied', expect.any(Object));
      
      analyticsSpy.mockRestore();
    });
  });
}); 