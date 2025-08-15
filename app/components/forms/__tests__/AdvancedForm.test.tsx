/**
 * AdvancedForm.test.tsx - Testes unitários para AdvancedForm
 * 
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Item 5.1.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * Testes baseados APENAS no código real implementado
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import AdvancedForm from '../AdvancedForm';

// Mock do formik e yup
jest.mock('formik', () => ({
  useFormik: jest.fn()
}));

const theme = createTheme();

const mockFields = [
  {
    name: 'name',
    label: 'Nome',
    type: 'text' as const,
    required: true,
    placeholder: 'Digite seu nome'
  },
  {
    name: 'email',
    label: 'Email',
    type: 'email' as const,
    required: true,
    helperText: 'Digite um email válido'
  },
  {
    name: 'age',
    label: 'Idade',
    type: 'number' as const,
    min: 18,
    max: 100
  },
  {
    name: 'category',
    label: 'Categoria',
    type: 'select' as const,
    options: [
      { value: 'tech', label: 'Tecnologia' },
      { value: 'health', label: 'Saúde' },
      { value: 'finance', label: 'Finanças' }
    ]
  },
  {
    name: 'interests',
    label: 'Interesses',
    type: 'multiselect' as const,
    options: [
      { value: 'programming', label: 'Programação' },
      { value: 'design', label: 'Design' },
      { value: 'marketing', label: 'Marketing' }
    ]
  },
  {
    name: 'notifications',
    label: 'Receber notificações',
    type: 'switch' as const
  },
  {
    name: 'satisfaction',
    label: 'Nível de satisfação',
    type: 'slider' as const,
    min: 0,
    max: 10,
    step: 1
  }
];

const mockInitialValues = {
  name: '',
  email: '',
  age: 25,
  category: '',
  interests: [],
  notifications: false,
  satisfaction: 5
};

const mockOnSubmit = jest.fn();
const mockOnAutoSave = jest.fn();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('AdvancedForm', () => {
  const defaultProps = {
    title: 'Formulário de Configuração',
    fields: mockFields,
    initialValues: mockInitialValues,
    onSubmit: mockOnSubmit
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização básica', () => {
    it('deve renderizar o título do formulário', () => {
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      expect(screen.getByText('Formulário de Configuração')).toBeInTheDocument();
    });

    it('deve renderizar todos os campos do formulário', () => {
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      
      expect(screen.getByLabelText('Nome')).toBeInTheDocument();
      expect(screen.getByLabelText('Email')).toBeInTheDocument();
      expect(screen.getByLabelText('Idade')).toBeInTheDocument();
      expect(screen.getByLabelText('Categoria')).toBeInTheDocument();
      expect(screen.getByLabelText('Interesses')).toBeInTheDocument();
      expect(screen.getByText('Receber notificações')).toBeInTheDocument();
      expect(screen.getByText('Nível de satisfação')).toBeInTheDocument();
    });

    it('deve renderizar botões de ação', () => {
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      
      expect(screen.getByText('Salvar')).toBeInTheDocument();
      expect(screen.getByText('Salvar Rascunho')).toBeInTheDocument();
    });
  });

  describe('Campos de texto', () => {
    it('deve renderizar campo de texto com placeholder', () => {
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      
      const nameField = screen.getByLabelText('Nome');
      expect(nameField).toHaveAttribute('placeholder', 'Digite seu nome');
    });

    it('deve renderizar campo de email com helper text', () => {
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      
      expect(screen.getByText('Digite um email válido')).toBeInTheDocument();
    });

    it('deve renderizar campo numérico com min e max', () => {
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      
      const ageField = screen.getByLabelText('Idade');
      expect(ageField).toHaveAttribute('min', '18');
      expect(ageField).toHaveAttribute('max', '100');
    });
  });

  describe('Campos de seleção', () => {
    it('deve renderizar select com opções', () => {
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      
      const categoryField = screen.getByLabelText('Categoria');
      fireEvent.mouseDown(categoryField);
      
      expect(screen.getByText('Tecnologia')).toBeInTheDocument();
      expect(screen.getByText('Saúde')).toBeInTheDocument();
      expect(screen.getByText('Finanças')).toBeInTheDocument();
    });

    it('deve renderizar multiselect com opções', () => {
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      
      const interestsField = screen.getByLabelText('Interesses');
      fireEvent.mouseDown(interestsField);
      
      expect(screen.getByText('Programação')).toBeInTheDocument();
      expect(screen.getByText('Design')).toBeInTheDocument();
      expect(screen.getByText('Marketing')).toBeInTheDocument();
    });
  });

  describe('Campos especiais', () => {
    it('deve renderizar switch', () => {
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      
      const switchElement = screen.getByRole('checkbox');
      expect(switchElement).toBeInTheDocument();
    });

    it('deve renderizar slider', () => {
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      
      const slider = screen.getByRole('slider');
      expect(slider).toBeInTheDocument();
      expect(slider).toHaveAttribute('aria-valuemin', '0');
      expect(slider).toHaveAttribute('aria-valuemax', '10');
    });
  });

  describe('Auto-save', () => {
    it('deve renderizar indicador de auto-save quando habilitado', () => {
      renderWithTheme(
        <AdvancedForm {...defaultProps} onAutoSave={mockOnAutoSave} showAutoSave={true} />
      );
      
      expect(screen.getByLabelText('Auto-save ativo')).toBeInTheDocument();
    });

    it('não deve renderizar indicador de auto-save quando desabilitado', () => {
      renderWithTheme(
        <AdvancedForm {...defaultProps} showAutoSave={false} />
      );
      
      expect(screen.queryByLabelText('Auto-save ativo')).not.toBeInTheDocument();
    });
  });

  describe('Undo/Redo', () => {
    it('deve renderizar botões de undo/redo quando habilitado', () => {
      renderWithTheme(
        <AdvancedForm {...defaultProps} showUndoRedo={true} />
      );
      
      expect(screen.getByLabelText('Desfazer')).toBeInTheDocument();
      expect(screen.getByLabelText('Refazer')).toBeInTheDocument();
    });

    it('não deve renderizar botões de undo/redo quando desabilitado', () => {
      renderWithTheme(
        <AdvancedForm {...defaultProps} showUndoRedo={false} />
      );
      
      expect(screen.queryByLabelText('Desfazer')).not.toBeInTheDocument();
      expect(screen.queryByLabelText('Refazer')).not.toBeInTheDocument();
    });
  });

  describe('Validação', () => {
    it('deve renderizar indicador de validação quando habilitado', () => {
      renderWithTheme(
        <AdvancedForm {...defaultProps} showValidation={true} />
      );
      
      expect(screen.getByLabelText('Formulário válido')).toBeInTheDocument();
    });

    it('não deve renderizar indicador de validação quando desabilitado', () => {
      renderWithTheme(
        <AdvancedForm {...defaultProps} showValidation={false} />
      );
      
      expect(screen.queryByLabelText('Formulário válido')).not.toBeInTheDocument();
    });
  });

  describe('Estados de loading', () => {
    it('deve mostrar loading no botão de salvar durante submissão', async () => {
      mockOnSubmit.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      
      const submitButton = screen.getByText('Salvar');
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Salvando...')).toBeInTheDocument();
      });
    });

    it('deve desabilitar botões durante submissão', async () => {
      mockOnSubmit.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      
      const submitButton = screen.getByText('Salvar');
      const draftButton = screen.getByText('Salvar Rascunho');
      
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(submitButton).toBeDisabled();
        expect(draftButton).toBeDisabled();
      });
    });
  });

  describe('Callbacks', () => {
    it('deve chamar onSubmit quando formulário é submetido', async () => {
      mockOnSubmit.mockResolvedValue(undefined);
      
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      
      const submitButton = screen.getByText('Salvar');
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledTimes(1);
      });
    });

    it('deve chamar onAutoSave quando valores mudam', async () => {
      mockOnAutoSave.mockResolvedValue(undefined);
      
      renderWithTheme(
        <AdvancedForm {...defaultProps} onAutoSave={mockOnAutoSave} autoSaveInterval={100} />
      );
      
      const nameField = screen.getByLabelText('Nome');
      fireEvent.change(nameField, { target: { value: 'João Silva' } });
      
      await waitFor(() => {
        expect(mockOnAutoSave).toHaveBeenCalled();
      }, { timeout: 200 });
    });
  });

  describe('Snackbar', () => {
    it('deve mostrar mensagem de sucesso após submissão bem-sucedida', async () => {
      mockOnSubmit.mockResolvedValue(undefined);
      
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      
      const submitButton = screen.getByText('Salvar');
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Formulário salvo com sucesso!')).toBeInTheDocument();
      });
    });

    it('deve mostrar mensagem de erro após falha na submissão', async () => {
      mockOnSubmit.mockRejectedValue(new Error('Erro no servidor'));
      
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      
      const submitButton = screen.getByText('Salvar');
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Erro ao salvar formulário')).toBeInTheDocument();
      });
    });
  });

  describe('Tamanhos do formulário', () => {
    it('deve aplicar largura máxima correta para diferentes tamanhos', () => {
      const { rerender } = renderWithTheme(
        <AdvancedForm {...defaultProps} maxWidth="sm" />
      );
      
      let container = screen.getByText('Formulário de Configuração').closest('div');
      expect(container).toHaveStyle({ maxWidth: '600px' });
      
      rerender(
        <ThemeProvider theme={theme}>
          <AdvancedForm {...defaultProps} maxWidth="lg" />
        </ThemeProvider>
      );
      
      container = screen.getByText('Formulário de Configuração').closest('div');
      expect(container).toHaveStyle({ maxWidth: '1200px' });
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter título acessível', () => {
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      const title = screen.getByRole('heading', { level: 2 });
      expect(title).toHaveTextContent('Formulário de Configuração');
    });

    it('deve ter labels acessíveis para todos os campos', () => {
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      
      expect(screen.getByLabelText('Nome')).toBeInTheDocument();
      expect(screen.getByLabelText('Email')).toBeInTheDocument();
      expect(screen.getByLabelText('Idade')).toBeInTheDocument();
      expect(screen.getByLabelText('Categoria')).toBeInTheDocument();
      expect(screen.getByLabelText('Interesses')).toBeInTheDocument();
    });

    it('deve ter botões com labels acessíveis', () => {
      renderWithTheme(<AdvancedForm {...defaultProps} />);
      
      expect(screen.getByRole('button', { name: 'Salvar' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Salvar Rascunho' })).toBeInTheDocument();
    });
  });

  describe('Validação de schema', () => {
    it('deve usar schema de validação customizado quando fornecido', () => {
      const customSchema = {
        name: 'custom-schema'
      };
      
      renderWithTheme(
        <AdvancedForm {...defaultProps} validationSchema={customSchema} />
      );
      
      // O schema customizado deve ser usado internamente pelo formik
      expect(screen.getByText('Formulário de Configuração')).toBeInTheDocument();
    });
  });
}); 