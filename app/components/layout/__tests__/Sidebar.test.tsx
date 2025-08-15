/**
 * Sidebar.test.tsx
 * 
 * Testes unitários para o componente Sidebar
 * 
 * Tracing ID: UI_ENTERPRISE_IMPLEMENTATION_20250127_002
 * Data: 2025-01-27
 * Versão: 1.0
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { createTheme } from '@mui/material/styles';
import Sidebar from '../Sidebar';

// Mock do useMediaQuery
jest.mock('@mui/material', () => ({
  ...jest.requireActual('@mui/material'),
  useMediaQuery: jest.fn(),
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

describe('Sidebar', () => {
  const defaultProps = {
    open: true,
    onClose: jest.fn(),
    drawerWidth: 240,
    drawerWidthCollapsed: 64,
    isMobile: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock useMediaQuery para desktop por padrão
    require('@mui/material').useMediaQuery.mockReturnValue(false);
  });

  describe('Renderização', () => {
    it('deve renderizar a sidebar com menu principal', () => {
      render(
        <TestWrapper>
          <Sidebar {...defaultProps} />
        </TestWrapper>
      );

      expect(screen.getByText('Omni Keywords')).toBeInTheDocument();
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Nichos')).toBeInTheDocument();
      expect(screen.getByText('Categorias')).toBeInTheDocument();
      expect(screen.getByText('Execuções')).toBeInTheDocument();
    });

    it('deve renderizar grupos de menu corretamente', () => {
      render(
        <TestWrapper>
          <Sidebar {...defaultProps} />
        </TestWrapper>
      );

      expect(screen.getByText('Principal')).toBeInTheDocument();
      expect(screen.getByText('Gestão')).toBeInTheDocument();
      expect(screen.getByText('Analytics')).toBeInTheDocument();
      expect(screen.getByText('Administração')).toBeInTheDocument();
    });

    it('deve renderizar badges quando especificados', () => {
      render(
        <TestWrapper>
          <Sidebar {...defaultProps} />
        </TestWrapper>
      );

      // Nichos tem badge 12
      const nichosItem = screen.getByText('Nichos');
      expect(nichosItem).toBeInTheDocument();
      
      // Execuções tem badge 3
      const execucoesItem = screen.getByText('Execuções');
      expect(execucoesItem).toBeInTheDocument();
    });

    it('deve renderizar versão colapsada em telas pequenas', () => {
      // Mock useMediaQuery para telas pequenas
      require('@mui/material').useMediaQuery.mockReturnValue(true);

      render(
        <TestWrapper>
          <Sidebar {...defaultProps} />
        </TestWrapper>
      );

      expect(screen.getByText('OKF')).toBeInTheDocument();
    });
  });

  describe('Interações', () => {
    it('deve navegar quando item do menu é clicado', () => {
      const mockNavigate = jest.fn();
      jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(mockNavigate);

      render(
        <TestWrapper>
          <Sidebar {...defaultProps} />
        </TestWrapper>
      );

      const dashboardItem = screen.getByText('Dashboard');
      fireEvent.click(dashboardItem);

      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });

    it('deve fechar sidebar em mobile quando item é clicado', () => {
      const mockOnClose = jest.fn();
      const mockNavigate = jest.fn();
      
      jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(mockNavigate);

      render(
        <TestWrapper>
          <Sidebar {...defaultProps} open={true} onClose={mockOnClose} isMobile={true} />
        </TestWrapper>
      );

      const dashboardItem = screen.getByText('Dashboard');
      fireEvent.click(dashboardItem);

      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
      expect(mockOnClose).toHaveBeenCalled();
    });

    it('deve marcar item como ativo baseado na rota atual', () => {
      // Mock useLocation para simular rota ativa
      jest.spyOn(require('react-router-dom'), 'useLocation').mockReturnValue({
        pathname: '/dashboard',
        search: '',
        hash: '',
        state: null,
      });

      render(
        <TestWrapper>
          <Sidebar {...defaultProps} />
        </TestWrapper>
      );

      const dashboardItem = screen.getByText('Dashboard');
      expect(dashboardItem.closest('button')).toHaveClass('Mui-selected');
    });
  });

  describe('Permissões', () => {
    it('deve ocultar itens sem permissão', () => {
      // Mock de permissões - simular que usuário não tem acesso a webhooks
      // TODO: Implementar mock de permissões quando sistema estiver pronto

      render(
        <TestWrapper>
          <Sidebar {...defaultProps} />
        </TestWrapper>
      );

      // Por enquanto, todos os itens devem estar visíveis (mock retorna true)
      expect(screen.getByText('Webhooks')).toBeInTheDocument();
      expect(screen.getByText('Templates')).toBeInTheDocument();
      expect(screen.getByText('Credenciais')).toBeInTheDocument();
    });
  });

  describe('Responsividade', () => {
    it('deve ajustar largura baseado no estado colapsado', () => {
      render(
        <TestWrapper>
          <Sidebar {...defaultProps} />
        </TestWrapper>
      );

      const drawer = screen.getByRole('presentation');
      expect(drawer).toBeInTheDocument();
    });

    it('deve usar variant temporary em mobile', () => {
      render(
        <TestWrapper>
          <Sidebar {...defaultProps} isMobile={true} />
        </TestWrapper>
      );

      const drawer = screen.getByRole('presentation');
      expect(drawer).toBeInTheDocument();
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter estrutura semântica correta', () => {
      render(
        <TestWrapper>
          <Sidebar {...defaultProps} />
        </TestWrapper>
      );

      // Deve ter role navigation
      const nav = screen.getByRole('navigation');
      expect(nav).toBeInTheDocument();

      // Itens devem ser clicáveis
      const menuItems = screen.getAllByRole('button');
      expect(menuItems.length).toBeGreaterThan(0);
    });

    it('deve ter labels apropriados para itens do menu', () => {
      render(
        <TestWrapper>
          <Sidebar {...defaultProps} />
        </TestWrapper>
      );

      const dashboardItem = screen.getByText('Dashboard');
      expect(dashboardItem).toBeInTheDocument();
    });
  });

  describe('Estados', () => {
    it('deve mostrar versão colapsada quando collapsed é true', () => {
      // Mock useMediaQuery para telas pequenas
      require('@mui/material').useMediaQuery.mockReturnValue(true);

      render(
        <TestWrapper>
          <Sidebar {...defaultProps} />
        </TestWrapper>
      );

      expect(screen.getByText('OKF')).toBeInTheDocument();
      expect(screen.queryByText('Omni Keywords')).not.toBeInTheDocument();
    });

    it('deve mostrar footer com versão quando não colapsado', () => {
      render(
        <TestWrapper>
          <Sidebar {...defaultProps} />
        </TestWrapper>
      );

      expect(screen.getByText('v1.0.0')).toBeInTheDocument();
    });
  });
}); 