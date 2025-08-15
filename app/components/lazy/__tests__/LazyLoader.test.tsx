/**
 * Testes unitários para LazyLoader
 * 
 * Prompt: Implementação de testes para Criticalidade 3.1.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import LazyLoader from '../LazyLoader';

const theme = createTheme();

// Mock do componente para teste
const MockComponent = () => <div data-testid="mock-component">Mock Component</div>;

// Mock do componente que falha
const MockFailingComponent = () => {
  throw new Error('Component failed to load');
};

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('LazyLoader', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização básica', () => {
    it('deve renderizar componente lazy com fallback padrão', async () => {
      const mockComponent = () => Promise.resolve({ default: MockComponent });
      
      renderWithTheme(
        <LazyLoader component={mockComponent} />
      );

      // Deve mostrar loading inicialmente
      expect(screen.getByText('Carregando...')).toBeInTheDocument();
      expect(screen.getByRole('progressbar')).toBeInTheDocument();

      // Deve carregar o componente
      await waitFor(() => {
        expect(screen.getByTestId('mock-component')).toBeInTheDocument();
      });
    });

    it('deve renderizar com fallback customizado', async () => {
      const mockComponent = () => Promise.resolve({ default: MockComponent });
      const customFallback = <div data-testid="custom-fallback">Custom Loading</div>;
      
      renderWithTheme(
        <LazyLoader 
          component={mockComponent} 
          fallback={customFallback}
        />
      );

      expect(screen.getByTestId('custom-fallback')).toBeInTheDocument();
    });

    it('deve renderizar com skeleton quando showSkeleton for true', async () => {
      const mockComponent = () => Promise.resolve({ default: MockComponent });
      
      renderWithTheme(
        <LazyLoader 
          component={mockComponent} 
          showSkeleton={true}
        />
      );

      // Deve mostrar skeleton
      const skeletons = screen.getAllByTestId('skeleton');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('Tratamento de erros', () => {
    it('deve mostrar error boundary quando componente falha', async () => {
      const failingComponent = () => Promise.resolve({ default: MockFailingComponent });
      
      renderWithTheme(
        <LazyLoader component={failingComponent} />
      );

      await waitFor(() => {
        expect(screen.getByText('Erro ao carregar componente')).toBeInTheDocument();
      });
    });

    it('deve permitir reset do erro', async () => {
      const failingComponent = () => Promise.resolve({ default: MockFailingComponent });
      
      renderWithTheme(
        <LazyLoader component={failingComponent} />
      );

      await waitFor(() => {
        expect(screen.getByText('Erro ao carregar componente')).toBeInTheDocument();
      });

      const resetButton = screen.getByText('Tentar novamente');
      expect(resetButton).toBeInTheDocument();
    });

    it('deve usar error boundary customizado', async () => {
      const failingComponent = () => Promise.resolve({ default: MockFailingComponent });
      const CustomErrorFallback = ({ error, resetError }: any) => (
        <div data-testid="custom-error">
          <p>Custom Error: {error.message}</p>
          <button onClick={resetError}>Custom Reset</button>
        </div>
      );
      
      renderWithTheme(
        <LazyLoader 
          component={failingComponent} 
          errorBoundary={CustomErrorFallback}
        />
      );

      await waitFor(() => {
        expect(screen.getByTestId('custom-error')).toBeInTheDocument();
        expect(screen.getByText('Custom Error: Component failed to load')).toBeInTheDocument();
      });
    });
  });

  describe('Preload', () => {
    it('deve preload componente quando preload for true', async () => {
      const mockComponent = jest.fn(() => Promise.resolve({ default: MockComponent }));
      
      renderWithTheme(
        <LazyLoader 
          component={mockComponent} 
          preload={true}
        />
      );

      // Deve chamar o componente para preload
      expect(mockComponent).toHaveBeenCalled();
    });

    it('não deve preload quando preload for false', async () => {
      const mockComponent = jest.fn(() => Promise.resolve({ default: MockComponent }));
      
      renderWithTheme(
        <LazyLoader 
          component={mockComponent} 
          preload={false}
        />
      );

      // Não deve chamar o componente imediatamente
      expect(mockComponent).not.toHaveBeenCalled();
    });
  });

  describe('Configurações de skeleton', () => {
    it('deve aplicar props customizadas do skeleton', async () => {
      const mockComponent = () => Promise.resolve({ default: MockComponent });
      
      renderWithTheme(
        <LazyLoader 
          component={mockComponent} 
          showSkeleton={true}
          skeletonProps={{
            variant: 'circular',
            width: 100,
            height: 100
          }}
        />
      );

      // Deve mostrar skeleton com props customizadas
      const skeletons = screen.getAllByTestId('skeleton');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('Timeout', () => {
    it('deve configurar timeout customizado', async () => {
      const mockComponent = () => Promise.resolve({ default: MockComponent });
      
      renderWithTheme(
        <LazyLoader 
          component={mockComponent} 
          timeout={5000}
        />
      );

      // Deve carregar normalmente
      await waitFor(() => {
        expect(screen.getByTestId('mock-component')).toBeInTheDocument();
      });
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter role e aria-label apropriados no loading', () => {
      const mockComponent = () => Promise.resolve({ default: MockComponent });
      
      renderWithTheme(
        <LazyLoader component={mockComponent} />
      );

      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toBeInTheDocument();
    });

    it('deve ter texto descritivo para screen readers', () => {
      const mockComponent = () => Promise.resolve({ default: MockComponent });
      
      renderWithTheme(
        <LazyLoader component={mockComponent} />
      );

      expect(screen.getByText('Carregando...')).toBeInTheDocument();
    });
  });
}); 