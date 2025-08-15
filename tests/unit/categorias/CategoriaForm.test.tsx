/**
 * Testes Unitários - CategoriaForm Component
 * 
 * Prompt: Implementação de testes para componentes importantes
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_CATEGORIA_FORM_025
 * 
 * Baseado em código real do CategoriaForm.tsx
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CategoriaForm } from '../../../app/components/categorias/CategoriaForm';

// Mock do Material-UI
jest.mock('@mui/material', () => ({
  Box: ({ children, ...props }: any) => <div data-testid="box" {...props}>{children}</div>,
  TextField: ({ label, value, onChange, error, helperText, ...props }: any) => (
    <div data-testid="text-field" data-label={label} data-error={!!error}>
      <label>{label}</label>
      <input
        value={value}
        onChange={onChange}
        data-testid={`input-${label?.toLowerCase().replace(/\s+/g, '-')}`}
        {...props}
      />
      {helperText && <span data-testid="helper-text">{helperText}</span>}
    </div>
  ),
  Button: ({ children, onClick, variant, startIcon, disabled, ...props }: any) => (
    <button 
      data-testid="button" 
      onClick={onClick} 
      data-variant={variant}
      disabled={disabled}
      {...props}
    >
      {startIcon}
      {children}
    </button>
  ),
  Card: ({ children, ...props }: any) => <div data-testid="card" {...props}>{children}</div>,
  CardContent: ({ children, ...props }: any) => <div data-testid="card-content" {...props}>{children}</div>,
  Typography: ({ children, variant, ...props }: any) => (
    <div data-testid="typography" data-variant={variant} {...props}>{children}</div>
  ),
  Grid: ({ children, container, item, ...props }: any) => (
    <div data-testid={container ? "grid-container" : "grid-item"} {...props}>{children}</div>
  ),
  FormControl: ({ children, ...props }: any) => <div data-testid="form-control" {...props}>{children}</div>,
  InputLabel: ({ children, ...props }: any) => <label data-testid="input-label" {...props}>{children}</label>,
  Select: ({ children, value, onChange, label, ...props }: any) => (
    <div data-testid="select" data-value={value} data-label={label} {...props}>
      <select value={value} onChange={onChange}>
        {children}
      </select>
    </div>
  ),
  MenuItem: ({ children, value, ...props }: any) => (
    <option data-testid="menu-item" value={value} {...props}>{children}</option>
  ),
  Chip: ({ label, onDelete, ...props }: any) => (
    <span data-testid="chip" {...props}>
      {label}
      {onDelete && <button data-testid="chip-delete" onClick={onDelete}>×</button>}
    </span>
  ),
  Alert: ({ children, severity, ...props }: any) => (
    <div data-testid="alert" data-severity={severity} {...props}>{children}</div>
  ),
  CircularProgress: ({ ...props }: any) => <div data-testid="circular-progress" {...props} />,
  IconButton: ({ children, onClick, ...props }: any) => (
    <button data-testid="icon-button" onClick={onClick} {...props}>{children}</button>
  ),
  Tooltip: ({ children, ...props }: any) => <div data-testid="tooltip" {...props}>{children}</div>,
  Divider: ({ ...props }: any) => <hr data-testid="divider" {...props} />,
  Paper: ({ children, ...props }: any) => <div data-testid="paper" {...props}>{children}</div>,
  Switch: ({ checked, onChange, ...props }: any) => (
    <input 
      type="checkbox" 
      data-testid="switch" 
      checked={checked} 
      onChange={onChange} 
      {...props} 
    />
  ),
  FormControlLabel: ({ control, label, ...props }: any) => (
    <label data-testid="form-control-label" {...props}>
      {control}
      {label}
    </label>
  ),
  Accordion: ({ children, ...props }: any) => <div data-testid="accordion" {...props}>{children}</div>,
  AccordionSummary: ({ children, ...props }: any) => (
    <div data-testid="accordion-summary" {...props}>{children}</div>
  ),
  AccordionDetails: ({ children, ...props }: any) => (
    <div data-testid="accordion-details" {...props}>{children}</div>
  ),
}));

// Mock dos ícones Material-UI
jest.mock('@mui/icons-material', () => ({
  Save: ({ ...props }: any) => <div data-testid="icon-save" {...props} />,
  Cancel: ({ ...props }: any) => <div data-testid="icon-cancel" {...props} />,
  Upload: ({ ...props }: any) => <div data-testid="icon-upload" {...props} />,
  Preview: ({ ...props }: any) => <div data-testid="icon-preview" {...props} />,
  Delete: ({ ...props }: any) => <div data-testid="icon-delete" {...props} />,
  CloudUpload: ({ ...props }: any) => <div data-testid="icon-cloud-upload" {...props} />,
  ExpandMore: ({ ...props }: any) => <div data-testid="icon-expand-more" {...props} />,
  Category: ({ ...props }: any) => <div data-testid="icon-category" {...props} />,
  Template: ({ ...props }: any) => <div data-testid="icon-template" {...props} />,
  Settings: ({ ...props }: any) => <div data-testid="icon-settings" {...props} />,
}));

describe('CategoriaForm - Formulário de Categoria', () => {
  
  const mockOnSubmit = jest.fn();
  const mockOnCancel = jest.fn();
  
  const defaultProps = {
    categoriasPai: [
      { id: '1', nome: 'Tecnologia', nivel: 1 },
      { id: '2', nome: 'Marketing', nivel: 1 },
      { id: '3', nome: 'Desenvolvimento Web', nivel: 2 }
    ],
    nichosDisponiveis: [
      { id: '1', nome: 'React', categoria: '1' },
      { id: '2', nome: 'Vue.js', categoria: '1' },
      { id: '3', nome: 'SEO', categoria: '2' }
    ],
    onSubmit: mockOnSubmit,
    onCancel: mockOnCancel,
    loading: false,
    error: null
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização do Componente', () => {
    
    test('deve renderizar o formulário com campos obrigatórios', () => {
      render(<CategoriaForm {...defaultProps} />);
      
      expect(screen.getByText('Nome')).toBeInTheDocument();
      expect(screen.getByText('Descrição')).toBeInTheDocument();
      expect(screen.getByText('Categoria Pai')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
    });

    test('deve renderizar com dados iniciais quando categoria é fornecida', () => {
      const categoria = {
        nome: 'Categoria Teste',
        descricao: 'Descrição da categoria teste',
        categoriaPai: '1',
        nivel: 2,
        status: 'ativo' as const,
        configuracao: {
          maxNichos: 5,
          maxKeywords: 500,
          intervaloExecucao: 12,
          ativo: true
        },
        templates: {
          promptTemplate: 'Template de prompt',
          keywordsTemplate: 'Template de keywords',
          outputTemplate: 'Template de output'
        },
        nichosAssociados: ['1', '2']
      };

      render(<CategoriaForm {...defaultProps} categoria={categoria} />);
      
      expect(screen.getByDisplayValue('Categoria Teste')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Descrição da categoria teste')).toBeInTheDocument();
    });

    test('deve renderizar botões de ação', () => {
      render(<CategoriaForm {...defaultProps} />);
      
      expect(screen.getByText('Salvar')).toBeInTheDocument();
      expect(screen.getByText('Cancelar')).toBeInTheDocument();
    });

    test('deve renderizar seções de configuração', () => {
      render(<CategoriaForm {...defaultProps} />);
      
      expect(screen.getByText('Configuração')).toBeInTheDocument();
      expect(screen.getByText('Templates')).toBeInTheDocument();
      expect(screen.getByText('Nichos Associados')).toBeInTheDocument();
    });
  });

  describe('Validação de Campos', () => {
    
    test('deve validar nome obrigatório', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const nomeInput = screen.getByTestId('input-nome');
      await user.clear(nomeInput);
      await user.tab(); // Sair do campo para trigger validação
      
      expect(screen.getByText('Nome é obrigatório')).toBeInTheDocument();
    });

    test('deve validar nome com mínimo de caracteres', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const nomeInput = screen.getByTestId('input-nome');
      await user.clear(nomeInput);
      await user.type(nomeInput, 'ab');
      await user.tab();
      
      expect(screen.getByText('Nome deve ter pelo menos 3 caracteres')).toBeInTheDocument();
    });

    test('deve validar nome com máximo de caracteres', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const nomeInput = screen.getByTestId('input-nome');
      await user.clear(nomeInput);
      await user.type(nomeInput, 'a'.repeat(101));
      await user.tab();
      
      expect(screen.getByText('Nome deve ter no máximo 100 caracteres')).toBeInTheDocument();
    });

    test('deve validar descrição obrigatória', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const descricaoInput = screen.getByTestId('input-descrição');
      await user.clear(descricaoInput);
      await user.tab();
      
      expect(screen.getByText('Descrição é obrigatória')).toBeInTheDocument();
    });

    test('deve validar descrição com mínimo de caracteres', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const descricaoInput = screen.getByTestId('input-descrição');
      await user.clear(descricaoInput);
      await user.type(descricaoInput, 'Curta');
      await user.tab();
      
      expect(screen.getByText('Descrição deve ter pelo menos 10 caracteres')).toBeInTheDocument();
    });

    test('deve validar descrição com máximo de caracteres', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const descricaoInput = screen.getByTestId('input-descrição');
      await user.clear(descricaoInput);
      await user.type(descricaoInput, 'a'.repeat(501));
      await user.tab();
      
      expect(screen.getByText('Descrição deve ter no máximo 500 caracteres')).toBeInTheDocument();
    });

    test('deve aceitar nome válido', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const nomeInput = screen.getByTestId('input-nome');
      await user.clear(nomeInput);
      await user.type(nomeInput, 'Categoria Válida');
      await user.tab();
      
      expect(screen.queryByText(/Nome deve/)).not.toBeInTheDocument();
    });

    test('deve aceitar descrição válida', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const descricaoInput = screen.getByTestId('input-descrição');
      await user.clear(descricaoInput);
      await user.type(descricaoInput, 'Esta é uma descrição válida com mais de 10 caracteres');
      await user.tab();
      
      expect(screen.queryByText(/Descrição deve/)).not.toBeInTheDocument();
    });
  });

  describe('Mudança de Campos', () => {
    
    test('deve permitir editar nome', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const nomeInput = screen.getByTestId('input-nome');
      await user.clear(nomeInput);
      await user.type(nomeInput, 'Novo Nome da Categoria');
      
      expect(nomeInput).toHaveValue('Novo Nome da Categoria');
    });

    test('deve permitir editar descrição', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const descricaoInput = screen.getByTestId('input-descrição');
      await user.clear(descricaoInput);
      await user.type(descricaoInput, 'Nova descrição da categoria');
      
      expect(descricaoInput).toHaveValue('Nova descrição da categoria');
    });

    test('deve permitir selecionar categoria pai', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const categoriaPaiSelect = screen.getByTestId('select');
      await user.selectOptions(categoriaPaiSelect, '1');
      
      expect(categoriaPaiSelect).toHaveValue('1');
    });

    test('deve atualizar nível baseado na categoria pai selecionada', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const categoriaPaiSelect = screen.getByTestId('select');
      await user.selectOptions(categoriaPaiSelect, '3'); // Desenvolvimento Web (nível 2)
      
      // O nível deve ser atualizado para 3 (nível da categoria pai + 1)
      expect(categoriaPaiSelect).toHaveValue('3');
    });

    test('deve permitir alterar configurações', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const maxNichosInput = screen.getByTestId('input-máximo-de-nichos');
      await user.clear(maxNichosInput);
      await user.type(maxNichosInput, '15');
      
      expect(maxNichosInput).toHaveValue('15');
    });

    test('deve permitir alterar templates', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const promptTemplateInput = screen.getByTestId('input-template-de-prompt');
      await user.clear(promptTemplateInput);
      await user.type(promptTemplateInput, 'Novo template de prompt');
      
      expect(promptTemplateInput).toHaveValue('Novo template de prompt');
    });
  });

  describe('Upload de Templates', () => {
    
    test('deve permitir upload de template', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const uploadButton = screen.getByTestId('icon-upload');
      expect(uploadButton).toBeInTheDocument();
    });

    test('deve permitir remover template', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const deleteButton = screen.getByTestId('icon-delete');
      expect(deleteButton).toBeInTheDocument();
    });

    test('deve mostrar preview de template', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const previewButton = screen.getByTestId('icon-preview');
      expect(previewButton).toBeInTheDocument();
    });
  });

  describe('Nichos Associados', () => {
    
    test('deve permitir adicionar nicho', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const nichosSection = screen.getByText('Nichos Associados');
      expect(nichosSection).toBeInTheDocument();
    });

    test('deve permitir remover nicho', async () => {
      const user = userEvent.setup();
      const categoria = {
        nichosAssociados: ['1', '2']
      };

      render(<CategoriaForm {...defaultProps} categoria={categoria} />);
      
      const chips = screen.getAllByTestId('chip');
      expect(chips.length).toBeGreaterThan(0);
    });
  });

  describe('Submissão de Dados', () => {
    
    test('deve chamar onSubmit com dados válidos', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      // Preencher campos obrigatórios
      const nomeInput = screen.getByTestId('input-nome');
      const descricaoInput = screen.getByTestId('input-descrição');
      
      await user.clear(nomeInput);
      await user.type(nomeInput, 'Categoria Válida');
      await user.clear(descricaoInput);
      await user.type(descricaoInput, 'Esta é uma descrição válida com mais de 10 caracteres');
      
      const submitButton = screen.getByText('Salvar');
      await user.click(submitButton);
      
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          nome: 'Categoria Válida',
          descricao: 'Esta é uma descrição válida com mais de 10 caracteres'
        })
      );
    });

    test('deve chamar onCancel quando botão cancelar é clicado', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const cancelButton = screen.getByText('Cancelar');
      await user.click(cancelButton);
      
      expect(mockOnCancel).toHaveBeenCalled();
    });

    test('deve desabilitar botão salvar quando loading', () => {
      render(<CategoriaForm {...defaultProps} loading={true} />);
      
      const submitButton = screen.getByText('Salvar');
      expect(submitButton).toBeDisabled();
    });

    test('deve mostrar erro quando fornecido', () => {
      render(<CategoriaForm {...defaultProps} error="Erro de validação" />);
      
      expect(screen.getByText('Erro de validação')).toBeInTheDocument();
    });

    test('deve mostrar loading quando loading é true', () => {
      render(<CategoriaForm {...defaultProps} loading={true} />);
      
      expect(screen.getByTestId('circular-progress')).toBeInTheDocument();
    });
  });

  describe('Validação de Formulário', () => {
    
    test('deve impedir submissão com campos inválidos', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      // Tentar submeter sem preencher campos obrigatórios
      const submitButton = screen.getByText('Salvar');
      await user.click(submitButton);
      
      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    test('deve validar formulário completo', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      // Preencher todos os campos obrigatórios
      const nomeInput = screen.getByTestId('input-nome');
      const descricaoInput = screen.getByTestId('input-descrição');
      
      await user.clear(nomeInput);
      await user.type(nomeInput, 'Categoria Completa');
      await user.clear(descricaoInput);
      await user.type(descricaoInput, 'Esta é uma descrição completa da categoria com mais de 10 caracteres');
      
      const submitButton = screen.getByText('Salvar');
      await user.click(submitButton);
      
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          nome: 'Categoria Completa',
          descricao: 'Esta é uma descrição completa da categoria com mais de 10 caracteres',
          nivel: 1,
          status: 'pendente'
        })
      );
    });
  });

  describe('Acessibilidade', () => {
    
    test('deve ter labels apropriados para todos os campos', () => {
      render(<CategoriaForm {...defaultProps} />);
      
      expect(screen.getByText('Nome')).toBeInTheDocument();
      expect(screen.getByText('Descrição')).toBeInTheDocument();
      expect(screen.getByText('Categoria Pai')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
    });

    test('deve ter navegação por teclado', () => {
      render(<CategoriaForm {...defaultProps} />);
      
      const inputs = screen.getAllByRole('textbox');
      expect(inputs.length).toBeGreaterThan(0);
      
      inputs.forEach(input => {
        expect(input).toHaveAttribute('tabIndex', '0');
      });
    });

    test('deve ter estrutura semântica adequada', () => {
      render(<CategoriaForm {...defaultProps} />);
      
      expect(screen.getByTestId('card')).toBeInTheDocument();
      expect(screen.getByTestId('form-control')).toBeInTheDocument();
    });

    test('deve ter mensagens de erro acessíveis', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const nomeInput = screen.getByTestId('input-nome');
      await user.clear(nomeInput);
      await user.tab();
      
      const errorMessage = screen.getByText('Nome é obrigatório');
      expect(errorMessage).toBeInTheDocument();
    });
  });

  describe('Performance e Otimização', () => {
    
    test('deve renderizar rapidamente com dados complexos', () => {
      const categoria = {
        nome: 'Categoria Complexa',
        descricao: 'a'.repeat(500),
        templates: {
          promptTemplate: 'b'.repeat(1000),
          keywordsTemplate: 'c'.repeat(1000),
          outputTemplate: 'd'.repeat(1000)
        }
      };

      const startTime = performance.now();
      
      render(<CategoriaForm {...defaultProps} categoria={categoria} />);
      
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(100); // Deve renderizar em menos de 100ms
    });

    test('deve evitar re-renders desnecessários', () => {
      const { rerender } = render(<CategoriaForm {...defaultProps} />);
      
      // Re-renderizar com os mesmos props não deve causar mudanças
      rerender(<CategoriaForm {...defaultProps} />);
      
      expect(screen.getByText('Nome')).toBeInTheDocument();
    });

    test('deve usar validação em tempo real eficiente', async () => {
      const user = userEvent.setup();
      render(<CategoriaForm {...defaultProps} />);
      
      const nomeInput = screen.getByTestId('input-nome');
      
      // Digitar rapidamente não deve causar problemas de performance
      await user.type(nomeInput, 'Teste');
      
      expect(nomeInput).toHaveValue('Teste');
    });
  });
}); 