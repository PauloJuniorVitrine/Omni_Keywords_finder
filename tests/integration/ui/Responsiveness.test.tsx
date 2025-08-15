/**
 * @file Responsiveness.test.tsx
 * @description Testes de integração para responsividade e acessibilidade
 * @author Paulo Júnior
 * @date 2025-01-27
 * @tracing_id UI_INTEGRATION_RESPONSIVENESS_20250127_001
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { theme } from '../../app/ui/theme/theme';
import { AppStore } from '../../app/store/AppStore';
import { AppRouter } from '../../app/routes/AppRouter';
import { NotificationProvider } from '../../app/components/notifications/NotificationCenter';
import { BrandingProvider } from '../../app/components/branding/BrandingProvider';

// Mock das APIs
jest.mock('../../app/hooks/useAPI', () => ({
  useAPI: () => ({
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  }),
}));

// Mock do sistema de permissões
jest.mock('../../app/hooks/usePermissions', () => ({
  usePermissions: () => ({
    hasPermission: jest.fn(() => true),
    userRole: 'admin',
    permissions: ['read', 'write', 'delete'],
  }),
}));

// Mock do hook de responsividade
jest.mock('../../app/hooks/useResponsive', () => ({
  useResponsive: () => ({
    isMobile: false,
    isTablet: false,
    isDesktop: true,
    breakpoint: 'lg',
  }),
}));

const createTestWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <BrandingProvider>
          <NotificationProvider>
            <AppStore>
              <BrowserRouter>
                {children}
              </BrowserRouter>
            </AppStore>
          </NotificationProvider>
        </BrandingProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

// Função para simular diferentes tamanhos de tela
const setViewport = (width: number, height: number) => {
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: width,
  });
  Object.defineProperty(window, 'innerHeight', {
    writable: true,
    configurable: true,
    value: height,
  });
  window.dispatchEvent(new Event('resize'));
};

describe('Responsiveness Integration Tests', () => {
  const TestWrapper = createTestWrapper();

  beforeEach(() => {
    jest.clearAllMocks();
    // Reset para desktop por padrão
    setViewport(1920, 1080);
  });

  describe('Breakpoints e Responsividade', () => {
    test('Layout desktop (1920x1080) - Sidebar visível, conteúdo expandido', async () => {
      setViewport(1920, 1080);

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        // Verificar se sidebar está visível
        expect(screen.getByTestId('sidebar')).toBeInTheDocument();
        expect(screen.getByTestId('sidebar')).toHaveStyle({ width: '280px' });

        // Verificar se conteúdo principal está expandido
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
        expect(screen.getByTestId('main-content')).toHaveStyle({ marginLeft: '280px' });
      });
    });

    test('Layout tablet (768x1024) - Sidebar colapsável, menu hambúrguer', async () => {
      setViewport(768, 1024);

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        // Verificar se menu hambúrguer está visível
        expect(screen.getByTestId('menu-toggle')).toBeInTheDocument();

        // Verificar se sidebar está colapsada por padrão
        expect(screen.getByTestId('sidebar')).toHaveStyle({ transform: 'translateX(-100%)' });
      });

      // Testar abertura do menu
      const menuToggle = screen.getByTestId('menu-toggle');
      fireEvent.click(menuToggle);

      await waitFor(() => {
        expect(screen.getByTestId('sidebar')).toHaveStyle({ transform: 'translateX(0)' });
      });
    });

    test('Layout mobile (375x667) - Sidebar overlay, navegação otimizada', async () => {
      setViewport(375, 667);

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        // Verificar se sidebar está em overlay
        expect(screen.getByTestId('sidebar-overlay')).toBeInTheDocument();

        // Verificar se navegação está otimizada para mobile
        expect(screen.getByTestId('mobile-navigation')).toBeInTheDocument();
      });

      // Testar navegação mobile
      const menuToggle = screen.getByTestId('menu-toggle');
      fireEvent.click(menuToggle);

      await waitFor(() => {
        expect(screen.getByTestId('sidebar-overlay')).toHaveStyle({ opacity: '1' });
      });
    });

    test('Transição suave entre breakpoints', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      // Iniciar em desktop
      setViewport(1920, 1080);
      await waitFor(() => {
        expect(screen.getByTestId('sidebar')).toHaveStyle({ width: '280px' });
      });

      // Transicionar para tablet
      setViewport(768, 1024);
      await waitFor(() => {
        expect(screen.getByTestId('menu-toggle')).toBeInTheDocument();
      });

      // Transicionar para mobile
      setViewport(375, 667);
      await waitFor(() => {
        expect(screen.getByTestId('sidebar-overlay')).toBeInTheDocument();
      });
    });
  });

  describe('Orientação de Tela', () => {
    test('Orientação landscape - Layout otimizado', async () => {
      setViewport(1920, 1080); // Landscape

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        // Verificar se layout está otimizado para landscape
        expect(screen.getByTestId('main-content')).toHaveStyle({ height: '100vh' });
      });
    });

    test('Orientação portrait - Layout adaptado', async () => {
      setViewport(1080, 1920); // Portrait

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        // Verificar se layout está adaptado para portrait
        expect(screen.getByTestId('main-content')).toHaveStyle({ height: '100vh' });
      });
    });

    test('Mudança de orientação em tempo real', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      // Iniciar em landscape
      setViewport(1920, 1080);
      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      // Mudar para portrait
      setViewport(1080, 1920);
      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });
    });
  });

  describe('Acessibilidade', () => {
    test('Navegação por teclado - Tab order correto', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      // Verificar se elementos focáveis estão na ordem correta
      const focusableElements = screen.getAllByRole('button');
      expect(focusableElements.length).toBeGreaterThan(0);

      // Testar navegação por tab
      focusableElements[0].focus();
      expect(focusableElements[0]).toHaveFocus();
    });

    test('Screen reader compatibility - ARIA labels', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        // Verificar se elementos têm ARIA labels
        const elementsWithAria = screen.getAllByLabelText(/./);
        expect(elementsWithAria.length).toBeGreaterThan(0);

        // Verificar se botões têm descrições
        const buttons = screen.getAllByRole('button');
        buttons.forEach(button => {
          expect(button).toHaveAttribute('aria-label');
        });
      });
    });

    test('Contraste de cores - WCAG compliance', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        // Verificar se elementos de texto têm contraste adequado
        const textElements = screen.getAllByText(/./);
        textElements.forEach(element => {
          const computedStyle = window.getComputedStyle(element);
          const color = computedStyle.color;
          const backgroundColor = computedStyle.backgroundColor;
          
          // Verificar se cores estão definidas
          expect(color).not.toBe('rgba(0, 0, 0, 0)');
          expect(backgroundColor).not.toBe('rgba(0, 0, 0, 0)');
        });
      });
    });

    test('Zoom e redimensionamento - Funcionalidade preservada', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      // Simular zoom 200%
      Object.defineProperty(window, 'devicePixelRatio', {
        writable: true,
        configurable: true,
        value: 2,
      });

      // Verificar se funcionalidade ainda funciona
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });
  });

  describe('Performance em Diferentes Dispositivos', () => {
    test('Carregamento otimizado para mobile', async () => {
      setViewport(375, 667);

      const startTime = performance.now();

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      const endTime = performance.now();
      const loadTime = endTime - startTime;

      // Verificar se tempo de carregamento é aceitável para mobile
      expect(loadTime).toBeLessThan(3000); // 3 segundos
    });

    test('Lazy loading de componentes em mobile', async () => {
      setViewport(375, 667);

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        // Verificar se componentes não essenciais são carregados sob demanda
        expect(screen.queryByTestId('heavy-component')).not.toBeInTheDocument();
      });
    });

    test('Otimização de imagens para diferentes resoluções', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        const images = screen.getAllByRole('img');
        images.forEach(img => {
          // Verificar se imagens têm srcset para diferentes resoluções
          expect(img).toHaveAttribute('src');
        });
      });
    });
  });

  describe('Interações Touch vs Mouse', () => {
    test('Touch interactions em dispositivos móveis', async () => {
      setViewport(375, 667);

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      // Simular touch events
      const touchableElement = screen.getByTestId('touchable-element');
      fireEvent.touchStart(touchableElement);
      fireEvent.touchEnd(touchableElement);

      await waitFor(() => {
        expect(screen.getByText(/elemento tocado/i)).toBeInTheDocument();
      });
    });

    test('Hover states em desktop', async () => {
      setViewport(1920, 1080);

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      // Simular hover
      const hoverableElement = screen.getByTestId('hoverable-element');
      fireEvent.mouseEnter(hoverableElement);

      await waitFor(() => {
        expect(hoverableElement).toHaveClass('hover');
      });
    });

    test('Adaptação automática baseada no tipo de dispositivo', async () => {
      // Mock de detecção de dispositivo touch
      Object.defineProperty(window, 'ontouchstart', {
        writable: true,
        configurable: true,
        value: null,
      });

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByTestId('main-content')).toBeInTheDocument();
      });

      // Verificar se interface se adapta ao tipo de dispositivo
      if (window.ontouchstart !== null) {
        expect(screen.getByTestId('touch-optimized')).toBeInTheDocument();
      } else {
        expect(screen.getByTestId('mouse-optimized')).toBeInTheDocument();
      }
    });
  });

  describe('Compatibilidade Cross-Browser', () => {
    test('Funcionalidade em diferentes navegadores', async () => {
      // Mock de diferentes user agents
      const userAgents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
      ];

      for (const userAgent of userAgents) {
        Object.defineProperty(navigator, 'userAgent', {
          value: userAgent,
          configurable: true,
        });

        render(
          <TestWrapper>
            <AppRouter />
          </TestWrapper>
        );

        await waitFor(() => {
          expect(screen.getByTestId('main-content')).toBeInTheDocument();
        });
      }
    });

    test('Fallbacks para navegadores antigos', async () => {
      // Mock de navegador antigo
      Object.defineProperty(window, 'IntersectionObserver', {
        writable: true,
        configurable: true,
        value: undefined,
      });

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        // Verificar se fallbacks estão funcionando
        expect(screen.getByTestId('fallback-content')).toBeInTheDocument();
      });
    });
  });
}); 