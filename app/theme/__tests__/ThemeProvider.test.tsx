/**
 * ThemeProvider.test.tsx
 * 
 * Prompt: CHECKLIST_REFINO_FINAL_INTERFACE.md - Criticalidade 4.2.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * Testes unitários para ThemeProvider
 * - Baseado APENAS no código real implementado
 * - Sem dados sintéticos ou genéricos
 * - Validação de funcionalidades reais
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../ThemeProvider';

// ===== MOCK DO LOCALSTORAGE =====
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// ===== MOCK DO MATCHMEDIA =====
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// ===== COMPONENTE DE TESTE =====
const TestComponent = () => {
  const { mode, toggleTheme, setMode } = useTheme();

  return (
    <div>
      <div data-testid="current-mode">{mode}</div>
      <button data-testid="toggle-button" onClick={toggleTheme}>
        Toggle Theme
      </button>
      <button data-testid="set-light" onClick={() => setMode('light')}>
        Set Light
      </button>
      <button data-testid="set-dark" onClick={() => setMode('dark')}>
        Set Dark
      </button>
    </div>
  );
};

// ===== TESTES =====
describe('ThemeProvider', () => {
  beforeEach(() => {
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    jest.clearAllMocks();
  });

  it('deve renderizar com tema light padrão', () => {
    localStorageMock.getItem.mockReturnValue(null);

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('current-mode')).toHaveTextContent('light');
  });

  it('deve carregar tema do localStorage', () => {
    localStorageMock.getItem.mockReturnValue('dark');

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('current-mode')).toHaveTextContent('dark');
    expect(localStorageMock.getItem).toHaveBeenCalledWith('omni-keywords-theme-mode');
  });

  it('deve alternar entre light e dark mode', () => {
    localStorageMock.getItem.mockReturnValue('light');

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    const toggleButton = screen.getByTestId('toggle-button');
    const modeDisplay = screen.getByTestId('current-mode');

    // Inicialmente light
    expect(modeDisplay).toHaveTextContent('light');

    // Toggle para dark
    fireEvent.click(toggleButton);
    expect(modeDisplay).toHaveTextContent('dark');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('omni-keywords-theme-mode', 'dark');

    // Toggle para light
    fireEvent.click(toggleButton);
    expect(modeDisplay).toHaveTextContent('light');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('omni-keywords-theme-mode', 'light');
  });

  it('deve definir tema específico via setMode', () => {
    localStorageMock.getItem.mockReturnValue('light');

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    const setDarkButton = screen.getByTestId('set-dark');
    const setLightButton = screen.getByTestId('set-light');
    const modeDisplay = screen.getByTestId('current-mode');

    // Definir dark mode
    fireEvent.click(setDarkButton);
    expect(modeDisplay).toHaveTextContent('dark');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('omni-keywords-theme-mode', 'dark');

    // Definir light mode
    fireEvent.click(setLightButton);
    expect(modeDisplay).toHaveTextContent('light');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('omni-keywords-theme-mode', 'light');
  });

  it('deve persistir tema no localStorage', () => {
    localStorageMock.getItem.mockReturnValue('light');

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    const toggleButton = screen.getByTestId('toggle-button');

    fireEvent.click(toggleButton);

    expect(localStorageMock.setItem).toHaveBeenCalledWith('omni-keywords-theme-mode', 'dark');
  });

  it('deve lidar com erro no localStorage', () => {
    localStorageMock.getItem.mockImplementation(() => {
      throw new Error('localStorage error');
    });

    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('current-mode')).toHaveTextContent('light');
    expect(consoleSpy).not.toHaveBeenCalled(); // Não deve chamar console.warn no getItem

    // Testar setItem com erro
    localStorageMock.setItem.mockImplementation(() => {
      throw new Error('setItem error');
    });

    const toggleButton = screen.getByTestId('toggle-button');
    fireEvent.click(toggleButton);

    expect(consoleSpy).toHaveBeenCalledWith('Erro ao salvar tema no localStorage:', expect.any(Error));

    consoleSpy.mockRestore();
  });

  it('deve detectar preferência do sistema', () => {
    const mockMatchMedia = jest.fn().mockImplementation(query => ({
      matches: query === '(prefers-color-scheme: dark)',
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }));

    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: mockMatchMedia,
    });

    localStorageMock.getItem.mockReturnValue(null);

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(mockMatchMedia).toHaveBeenCalledWith('(prefers-color-scheme: dark)');
  });

  it('deve responder a mudanças na preferência do sistema', () => {
    let changeCallback: ((e: MediaQueryListEvent) => void) | null = null;

    const mockMatchMedia = jest.fn().mockImplementation(query => ({
      matches: query === '(prefers-color-scheme: dark)',
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn((event, callback) => {
        if (event === 'change') {
          changeCallback = callback;
        }
      }),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }));

    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: mockMatchMedia,
    });

    localStorageMock.getItem.mockReturnValue('light');

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('current-mode')).toHaveTextContent('light');

    // Simular mudança para dark mode
    if (changeCallback) {
      changeCallback({
        matches: true,
        media: '(prefers-color-scheme: dark)',
      } as MediaQueryListEvent);
    }

    expect(screen.getByTestId('current-mode')).toHaveTextContent('dark');
  });
});

// ===== TESTES DO HOOK USE THEME =====
describe('useTheme Hook', () => {
  it('deve lançar erro quando usado fora do ThemeProvider', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useTheme deve ser usado dentro de ThemeProvider');

    consoleSpy.mockRestore();
  });

  it('deve fornecer todas as funções necessárias', () => {
    localStorageMock.getItem.mockReturnValue('light');

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('current-mode')).toBeInTheDocument();
    expect(screen.getByTestId('toggle-button')).toBeInTheDocument();
    expect(screen.getByTestId('set-light')).toBeInTheDocument();
    expect(screen.getByTestId('set-dark')).toBeInTheDocument();
  });
});

// ===== TESTES DE INTEGRAÇÃO =====
describe('Integração ThemeProvider', () => {
  it('deve aplicar tema correto aos componentes filhos', () => {
    localStorageMock.getItem.mockReturnValue('dark');

    const TestChild = () => {
      const { mode } = useTheme();
      return (
        <div data-testid="child-component" data-theme={mode}>
          Child Component
        </div>
      );
    };

    render(
      <ThemeProvider>
        <TestChild />
      </ThemeProvider>
    );

    const childComponent = screen.getByTestId('child-component');
    expect(childComponent).toHaveAttribute('data-theme', 'dark');
  });

  it('deve manter estado entre re-renders', () => {
    localStorageMock.getItem.mockReturnValue('light');

    const { rerender } = render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('current-mode')).toHaveTextContent('light');

    // Re-render
    rerender(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('current-mode')).toHaveTextContent('light');
  });
}); 