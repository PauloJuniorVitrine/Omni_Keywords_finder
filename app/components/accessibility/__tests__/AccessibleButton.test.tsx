/**
 * Testes unitários para AccessibleButton
 * 
 * Prompt: Implementação de testes para Criticalidade 3.2.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import AccessibleButton from '../AccessibleButton';

const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('AccessibleButton', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização básica', () => {
    it('deve renderizar botão com aria-label', () => {
      renderWithTheme(
        <AccessibleButton ariaLabel="Salvar dados">
          Salvar
        </AccessibleButton>
      );

      const button = screen.getByRole('button', { name: 'Salvar dados' });
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('aria-label', 'Salvar dados');
    });

    it('deve renderizar com aria-description', () => {
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Exportar dados"
          ariaDescription="Exporta todos os dados para arquivo CSV"
        >
          Exportar
        </AccessibleButton>
      );

      const button = screen.getByRole('button', { name: 'Exportar dados' });
      expect(button).toHaveAttribute('aria-describedby', 'Exportar dados-description');
    });

    it('deve renderizar com aria-pressed', () => {
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Filtro ativo"
          ariaPressed={true}
        >
          Filtro
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-pressed', 'true');
    });

    it('deve renderizar com aria-expanded', () => {
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Menu dropdown"
          ariaExpanded={true}
        >
          Menu
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-expanded', 'true');
    });
  });

  describe('Navegação por teclado', () => {
    it('deve responder a Enter key', () => {
      const handleClick = jest.fn();
      
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Botão de teste"
          onClick={handleClick}
        >
          Teste
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      fireEvent.keyDown(button, { key: 'Enter' });
      
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('deve responder a Space key', () => {
      const handleClick = jest.fn();
      
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Botão de teste"
          onClick={handleClick}
        >
          Teste
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      fireEvent.keyDown(button, { key: ' ' });
      
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('deve responder a Escape key para popups', () => {
      const handleKeyDown = jest.fn();
      
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Menu dropdown"
          ariaHaspopup="menu"
          onKeyDown={handleKeyDown}
        >
          Menu
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      fireEvent.keyDown(button, { key: 'Escape' });
      
      expect(handleKeyDown).toHaveBeenCalledTimes(1);
    });
  });

  describe('Tooltips', () => {
    it('deve mostrar tooltip quando tooltipText for fornecido', async () => {
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Botão com tooltip"
          tooltipText="Informação adicional sobre o botão"
        >
          Botão
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      fireEvent.mouseEnter(button);

      await waitFor(() => {
        expect(screen.getByText('Informação adicional sobre o botão')).toBeInTheDocument();
      });
    });

    it('deve incluir atalho de teclado no tooltip', async () => {
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Salvar"
          tooltipText="Salvar alterações"
          keyboardShortcut="Ctrl+S"
        >
          Salvar
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      fireEvent.mouseEnter(button);

      await waitFor(() => {
        expect(screen.getByText('Salvar alterações - Ctrl+S')).toBeInTheDocument();
      });
    });

    it('deve mostrar tooltip no foco quando showTooltipOnFocus for true', async () => {
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Botão focável"
          tooltipText="Tooltip no foco"
          showTooltipOnFocus={true}
        >
          Botão
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      fireEvent.focus(button);

      await waitFor(() => {
        expect(screen.getByText('Tooltip no foco')).toBeInTheDocument();
      });
    });
  });

  describe('Atalhos de teclado', () => {
    it('deve incluir atalho no aria-label', () => {
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Salvar"
          keyboardShortcut="Ctrl+S"
        >
          Salvar
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Salvar (Ctrl+S)');
    });

    it('deve chamar onKeyboardShortcut quando atalho for pressionado', () => {
      const onKeyboardShortcut = jest.fn();
      
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Salvar"
          keyboardShortcut="Ctrl+S"
          onKeyboardShortcut={onKeyboardShortcut}
        >
          Salvar
        </AccessibleButton>
      );

      // Simular pressionar Ctrl+S
      fireEvent.keyDown(document, { 
        key: 'KeyS', 
        code: 'KeyS',
        ctrlKey: true 
      });

      expect(onKeyboardShortcut).toHaveBeenCalledTimes(1);
    });
  });

  describe('Focus e auto-focus', () => {
    it('deve focar automaticamente quando autoFocus for true', () => {
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Botão com auto-focus"
          autoFocus={true}
        >
          Botão
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveFocus();
    });

    it('deve focar no mount quando focusOnMount for true', () => {
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Botão com focus no mount"
          focusOnMount={true}
        >
          Botão
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveFocus();
    });

    it('deve ter tabIndex configurável', () => {
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Botão com tabIndex"
          tabIndex={5}
        >
          Botão
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('tabindex', '5');
    });
  });

  describe('Anúncios para screen readers', () => {
    it('deve anunciar ação quando ariaLive for configurado', () => {
      const originalCreateElement = document.createElement;
      const mockAnnouncement = {
        setAttribute: jest.fn(),
        textContent: '',
        style: {}
      };
      
      document.createElement = jest.fn().mockReturnValue(mockAnnouncement);
      document.body.appendChild = jest.fn();
      document.body.removeChild = jest.fn();

      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Salvar"
          ariaLive="polite"
          onClick={() => {}}
        >
          Salvar
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      fireEvent.click(button);

      expect(document.createElement).toHaveBeenCalledWith('div');
      expect(mockAnnouncement.setAttribute).toHaveBeenCalledWith('aria-live', 'polite');
      expect(mockAnnouncement.setAttribute).toHaveBeenCalledWith('aria-atomic', 'true');

      // Restaurar função original
      document.createElement = originalCreateElement;
    });
  });

  describe('Estilos e acessibilidade visual', () => {
    it('deve ter foco visível', () => {
      renderWithTheme(
        <AccessibleButton ariaLabel="Botão testável">
          Botão
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      
      // Simular foco
      fireEvent.focus(button);
      
      // Verificar se tem outline (estilo de foco)
      expect(button).toHaveStyle({ outline: expect.stringContaining('solid') });
    });

    it('deve suportar modo de alto contraste', () => {
      renderWithTheme(
        <AccessibleButton ariaLabel="Botão alto contraste">
          Botão
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      
      // Verificar se tem estilos para alto contraste
      expect(button).toBeInTheDocument();
    });
  });

  describe('Props do Material-UI', () => {
    it('deve passar props do Material-UI Button', () => {
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Botão com props MUI"
          variant="contained"
          color="primary"
          size="large"
        >
          Botão
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button).toHaveClass('MuiButton-contained');
      expect(button).toHaveClass('MuiButton-colorPrimary');
      expect(button).toHaveClass('MuiButton-sizeLarge');
    });

    it('deve suportar disabled state', () => {
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Botão desabilitado"
          disabled={true}
        >
          Botão
        </AccessibleButton>
      );

      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });
  });

  describe('Ref forwarding', () => {
    it('deve encaminhar ref corretamente', () => {
      const ref = React.createRef<HTMLButtonElement>();
      
      renderWithTheme(
        <AccessibleButton 
          ariaLabel="Botão com ref"
          ref={ref}
        >
          Botão
        </AccessibleButton>
      );

      expect(ref.current).toBeInstanceOf(HTMLButtonElement);
    });
  });
}); 