/**
 * MainLayout.test.tsx
 * 
 * Testes unitários para o componente MainLayout
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { createTheme } from '@mui/material/styles';
import MainLayout from '../MainLayout';

// Mock dos componentes dependentes
jest.mock('../Sidebar', () => {
  return function MockSidebar({ open, onClose, drawerWidth, drawerWidthCollapsed, isMobile }: any) {
    return (
      <div data-testid="sidebar" data-open={open} data-width={drawerWidth}>
        Mock Sidebar
        <button onClick={onClose}>Close</button>
      </div>
    );
  };
});

jest.mock('../Header', () => {
  return function MockHeader() {
    return <div data-testid="header">Mock Header</div>;
  };
});

// Mock do useColorMode
const mockToggleColorMode = jest.fn();
jest.mock('@mui/material', () => ({
  ...jest.requireActual('@mui/material'),
  useColorMode: () => ({
    colorMode: 'light',
    toggleColorMode: mockToggleColorMode,
  }),
}));

// Tema para testes
const theme = createTheme();

// Wrapper para testes
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    <ThemeProvider theme={theme}>
      {children}
    </ThemeProvider>
  </BrowserRouter>
);

describe('MainLayout', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização', () => {
    it('deve renderizar o layout principal com children', () => {
      render(
        <TestWrapper>
          <MainLayout>
            <div data-testid="content">Conteúdo de teste</div>
          </MainLayout>
        </TestWrapper>
      );

      expect(screen.getByTestId('content')).toBeInTheDocument();
      expect(screen.getByTestId('sidebar')).toBeInTheDocument();
    });

    it('deve renderizar breadcrumbs corretamente', () => {
      render(
        <TestWrapper>
          <MainLayout>
            <div>Conteúdo</div>
          </MainLayout>
        </TestWrapper>
      );

      // Deve ter breadcrumb Home por padrão
      expect(screen.getByText('Home')).toBeInTheDocument();
    });

    it('deve renderizar botão de toggle da sidebar', () => {
      render(
        <TestWrapper>
          <MainLayout>
            <div>Conteúdo</div>
          </MainLayout>
        </TestWrapper>
      );

      const toggleButton = screen.getByLabelText('toggle sidebar');
      expect(toggleButton).toBeInTheDocument();
    });

    it('deve renderizar botão de toggle de tema', () => {
      render(
        <TestWrapper>
          <MainLayout>
            <div>Conteúdo</div>
          </MainLayout>
        </TestWrapper>
      );

      const themeButton = screen.getByLabelText('toggle theme');
      expect(themeButton).toBeInTheDocument();
    });
  });

  describe('Interações', () => {
    it('deve alternar sidebar quando botão é clicado', async () => {
      render(
        <TestWrapper>
          <MainLayout>
            <div>Conteúdo</div>
          </MainLayout>
        </TestWrapper>
      );

      const sidebar = screen.getByTestId('sidebar');
      const toggleButton = screen.getByLabelText('toggle sidebar');

      // Sidebar deve estar aberta inicialmente
      expect(sidebar).toHaveAttribute('data-open', 'true');

      // Clicar no botão para fechar
      fireEvent.click(toggleButton);

      await waitFor(() => {
        expect(sidebar).toHaveAttribute('data-open', 'false');
      });
    });

    it('deve chamar toggleColorMode quando botão de tema é clicado', () => {
      render(
        <TestWrapper>
          <MainLayout>
            <div>Conteúdo</div>
          </MainLayout>
        </TestWrapper>
      );

      const themeButton = screen.getByLabelText('toggle theme');
      fireEvent.click(themeButton);

      expect(mockToggleColorMode).toHaveBeenCalledTimes(1);
    });

    it('deve fechar sidebar quando botão close é clicado', async () => {
      render(
        <TestWrapper>
          <MainLayout>
            <div>Conteúdo</div>
          </MainLayout>
        </TestWrapper>
      );

      const sidebar = screen.getByTestId('sidebar');
      const closeButton = screen.getByText('Close');

      // Sidebar deve estar aberta inicialmente
      expect(sidebar).toHaveAttribute('data-open', 'true');

      // Clicar no botão close
      fireEvent.click(closeButton);

      await waitFor(() => {
        expect(sidebar).toHaveAttribute('data-open', 'false');
      });
    });
  });

  describe('Responsividade', () => {
    it('deve ajustar layout para mobile', () => {
      // Mock de useMediaQuery para mobile
      jest.spyOn(require('@mui/material'), 'useMediaQuery').mockReturnValue(true);

      render(
        <TestWrapper>
          <MainLayout>
            <div>Conteúdo</div>
          </MainLayout>
        </TestWrapper>
      );

      const sidebar = screen.getByTestId('sidebar');
      expect(sidebar).toBeInTheDocument();
    });
  });

  describe('Navegação', () => {
    it('deve navegar quando breadcrumb é clicado', () => {
      const mockNavigate = jest.fn();
      jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(mockNavigate);

      render(
        <TestWrapper>
          <MainLayout>
            <div>Conteúdo</div>
          </MainLayout>
        </TestWrapper>
      );

      const homeBreadcrumb = screen.getByText('Home');
      fireEvent.click(homeBreadcrumb);

      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter labels apropriados para botões', () => {
      render(
        <TestWrapper>
          <MainLayout>
            <div>Conteúdo</div>
          </MainLayout>
        </TestWrapper>
      );

      expect(screen.getByLabelText('toggle sidebar')).toBeInTheDocument();
      expect(screen.getByLabelText('toggle theme')).toBeInTheDocument();
    });

    it('deve ter breadcrumbs com aria-label', () => {
      render(
        <TestWrapper>
          <MainLayout>
            <div>Conteúdo</div>
          </MainLayout>
        </TestWrapper>
      );

      const breadcrumbs = screen.getByLabelText('breadcrumb');
      expect(breadcrumbs).toBeInTheDocument();
    });
  });
}); 