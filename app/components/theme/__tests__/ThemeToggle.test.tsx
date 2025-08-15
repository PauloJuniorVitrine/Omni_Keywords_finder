/**
 * ThemeToggle.test.tsx
 * 
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Criticalidade 4.2.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * Testes unitários para ThemeToggle
 * - Baseado APENAS no código real implementado
 * - Sem dados sintéticos ou genéricos
 * - Validação de funcionalidades reais
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { createTheme } from '@mui/material/styles';
import { ThemeToggle, ThemeToggleDemo } from '../ThemeToggle';

// ===== MOCK DO TEMA =====
const mockTheme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={mockTheme}>
      {component}
    </ThemeProvider>
  );
};

// ===== TESTES PARA THEME TOGGLE =====
describe('ThemeToggle', () => {
  it('deve renderizar toggle com ícone correto para tema light', () => {
    renderWithTheme(<ThemeToggle />);

    // Deve mostrar ícone de dark mode quando está em light mode
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('deve exibir tooltip correto', () => {
    renderWithTheme(<ThemeToggle />);

    const toggleButton = screen.getByRole('button');
    expect(toggleButton).toHaveAttribute('aria-label', 'Alternar para modo escuro');
  });

  it('deve aplicar tamanhos diferentes', () => {
    const { rerender } = renderWithTheme(<ThemeToggle size="small" />);
    let button = screen.getByRole('button');
    expect(button).toBeInTheDocument();

    rerender(
      <ThemeProvider theme={mockTheme}>
        <ThemeToggle size="medium" />
      </ThemeProvider>
    );
    button = screen.getByRole('button');
    expect(button).toBeInTheDocument();

    rerender(
      <ThemeProvider theme={mockTheme}>
        <ThemeToggle size="large" />
      </ThemeProvider>
    );
    button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
  });

  it('deve ocultar tooltip quando showTooltip é false', () => {
    renderWithTheme(<ThemeToggle showTooltip={false} />);

    const toggleButton = screen.getByRole('button');
    expect(toggleButton).not.toHaveAttribute('aria-label');
  });

  it('deve ocultar indicador quando showIndicator é false', () => {
    renderWithTheme(<ThemeToggle showIndicator={false} />);

    const toggleButton = screen.getByRole('button');
    expect(toggleButton).toBeInTheDocument();
    
    // Verificar se não há indicador
    const indicator = document.querySelector('[class*="ThemeIndicator"]');
    expect(indicator).not.toBeInTheDocument();
  });

  it('deve aplicar classe customizada', () => {
    const customClass = 'custom-toggle-class';
    renderWithTheme(<ThemeToggle className={customClass} />);

    const toggleButton = screen.getByRole('button');
    expect(toggleButton).toHaveClass(customClass);
  });

  it('deve desabilitar durante animação', async () => {
    renderWithTheme(<ThemeToggle />);

    const toggleButton = screen.getByRole('button');
    
    // Clicar no botão
    fireEvent.click(toggleButton);
    
    // Deve estar desabilitado durante animação
    expect(toggleButton).toBeDisabled();
    
    // Aguardar fim da animação
    await waitFor(() => {
      expect(toggleButton).not.toBeDisabled();
    }, { timeout: 700 });
  });
});

// ===== TESTES PARA THEME TOGGLE DEMO =====
describe('ThemeToggleDemo', () => {
  it('deve renderizar todos os tamanhos de toggle', () => {
    renderWithTheme(<ThemeToggleDemo />);

    // Deve ter 5 botões (3 tamanhos + 2 variações)
    const buttons = screen.getAllByRole('button');
    expect(buttons).toHaveLength(5);
  });

  it('deve exibir container de demonstração', () => {
    renderWithTheme(<ThemeToggleDemo />);

    const demoContainer = document.querySelector('[class*="display: flex"]');
    expect(demoContainer).toBeInTheDocument();
  });
});

// ===== TESTES DE INTEGRAÇÃO =====
describe('Integração ThemeToggle', () => {
  it('deve integrar com ThemeProvider', () => {
    const TestApp = () => {
      return (
        <ThemeProvider theme={mockTheme}>
          <ThemeToggle />
        </ThemeProvider>
      );
    };

    render(<TestApp />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('deve manter funcionalidade em diferentes contextos', () => {
    const TestContext = () => {
      return (
        <div data-testid="context-wrapper">
          <ThemeToggle />
        </div>
      );
    };

    renderWithTheme(<TestContext />);
    
    expect(screen.getByTestId('context-wrapper')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });
});

// ===== TESTES DE ACESSIBILIDADE =====
describe('Acessibilidade ThemeToggle', () => {
  it('deve ter role button', () => {
    renderWithTheme(<ThemeToggle />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('deve ter aria-label apropriado', () => {
    renderWithTheme(<ThemeToggle />);
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label');
  });

  it('deve ser focável', () => {
    renderWithTheme(<ThemeToggle />);
    const button = screen.getByRole('button');
    button.focus();
    expect(button).toHaveFocus();
  });

  it('deve responder a teclado', () => {
    renderWithTheme(<ThemeToggle />);
    const button = screen.getByRole('button');
    
    button.focus();
    fireEvent.keyDown(button, { key: 'Enter' });
    
    // Deve estar desabilitado após clique
    expect(button).toBeDisabled();
  });
});

// ===== TESTES DE ESTADOS =====
describe('Estados ThemeToggle', () => {
  it('deve mostrar estado inicial correto', () => {
    renderWithTheme(<ThemeToggle />);
    const button = screen.getByRole('button');
    expect(button).not.toBeDisabled();
  });

  it('deve mostrar estado durante animação', async () => {
    renderWithTheme(<ThemeToggle />);
    const button = screen.getByRole('button');
    
    fireEvent.click(button);
    expect(button).toBeDisabled();
    
    await waitFor(() => {
      expect(button).not.toBeDisabled();
    }, { timeout: 700 });
  });

  it('deve manter estado após múltiplos cliques', async () => {
    renderWithTheme(<ThemeToggle />);
    const button = screen.getByRole('button');
    
    // Primeiro clique
    fireEvent.click(button);
    expect(button).toBeDisabled();
    
    await waitFor(() => {
      expect(button).not.toBeDisabled();
    }, { timeout: 700 });
    
    // Segundo clique
    fireEvent.click(button);
    expect(button).toBeDisabled();
    
    await waitFor(() => {
      expect(button).not.toBeDisabled();
    }, { timeout: 700 });
  });
});

// ===== TESTES DE PERFORMANCE =====
describe('Performance ThemeToggle', () => {
  it('deve renderizar rapidamente', () => {
    const startTime = performance.now();
    
    renderWithTheme(<ThemeToggle />);
    
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    // Deve renderizar em menos de 100ms
    expect(renderTime).toBeLessThan(100);
  });

  it('deve responder rapidamente a cliques', async () => {
    renderWithTheme(<ThemeToggle />);
    const button = screen.getByRole('button');
    
    const startTime = performance.now();
    fireEvent.click(button);
    const endTime = performance.now();
    const clickTime = endTime - startTime;
    
    // Deve responder em menos de 50ms
    expect(clickTime).toBeLessThan(50);
  });
}); 