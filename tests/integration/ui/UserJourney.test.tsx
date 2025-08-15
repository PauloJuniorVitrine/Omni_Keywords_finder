/**
 * @file UserJourney.test.tsx
 * @description Testes de integração para jornada completa do usuário
 * @author Paulo Júnior
 * @date 2025-01-27
 * @tracing_id UI_INTEGRATION_USERJOURNEY_20250127_001
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

describe('UserJourney Integration Tests', () => {
  const TestWrapper = createTestWrapper();

  beforeEach(() => {
    // Limpar mocks antes de cada teste
    jest.clearAllMocks();
  });

  describe('Cenários de Sucesso', () => {
    test('Jornada completa: Login → Dashboard → Nichos → Categorias → Execuções', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      // 1. Verificar se o dashboard carrega
      await waitFor(() => {
        expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
      });

      // 2. Navegar para nichos
      const nichosLink = screen.getByText(/nichos/i);
      fireEvent.click(nichosLink);

      await waitFor(() => {
        expect(screen.getByText(/gestão de nichos/i)).toBeInTheDocument();
      });

      // 3. Criar novo nicho
      const criarNichoBtn = screen.getByText(/criar nicho/i);
      fireEvent.click(criarNichoBtn);

      await waitFor(() => {
        expect(screen.getByText(/novo nicho/i)).toBeInTheDocument();
      });

      // 4. Preencher formulário
      const nomeInput = screen.getByLabelText(/nome do nicho/i);
      const descricaoInput = screen.getByLabelText(/descrição/i);

      fireEvent.change(nomeInput, { target: { value: 'Teste Nicho' } });
      fireEvent.change(descricaoInput, { target: { value: 'Descrição do nicho teste' } });

      // 5. Salvar nicho
      const salvarBtn = screen.getByText(/salvar/i);
      fireEvent.click(salvarBtn);

      await waitFor(() => {
        expect(screen.getByText(/nicho criado com sucesso/i)).toBeInTheDocument();
      });

      // 6. Navegar para categorias
      const categoriasLink = screen.getByText(/categorias/i);
      fireEvent.click(categoriasLink);

      await waitFor(() => {
        expect(screen.getByText(/gestão de categorias/i)).toBeInTheDocument();
      });

      // 7. Navegar para execuções
      const execucoesLink = screen.getByText(/execuções/i);
      fireEvent.click(execucoesLink);

      await waitFor(() => {
        expect(screen.getByText(/monitoramento de execuções/i)).toBeInTheDocument();
      });
    });

    test('Fluxo de criação de categoria com nicho associado', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      // Navegar para categorias
      const categoriasLink = screen.getByText(/categorias/i);
      fireEvent.click(categoriasLink);

      await waitFor(() => {
        expect(screen.getByText(/gestão de categorias/i)).toBeInTheDocument();
      });

      // Criar nova categoria
      const criarCategoriaBtn = screen.getByText(/criar categoria/i);
      fireEvent.click(criarCategoriaBtn);

      await waitFor(() => {
        expect(screen.getByText(/nova categoria/i)).toBeInTheDocument();
      });

      // Preencher formulário
      const nomeInput = screen.getByLabelText(/nome da categoria/i);
      const nichoSelect = screen.getByLabelText(/nichos/i);

      fireEvent.change(nomeInput, { target: { value: 'Categoria Teste' } });
      fireEvent.change(nichoSelect, { target: { value: '1' } });

      // Salvar categoria
      const salvarBtn = screen.getByText(/salvar/i);
      fireEvent.click(salvarBtn);

      await waitFor(() => {
        expect(screen.getByText(/categoria criada com sucesso/i)).toBeInTheDocument();
      });
    });

    test('Fluxo de execução de análise de keywords', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      // Navegar para execuções
      const execucoesLink = screen.getByText(/execuções/i);
      fireEvent.click(execucoesLink);

      await waitFor(() => {
        expect(screen.getByText(/monitoramento de execuções/i)).toBeInTheDocument();
      });

      // Criar nova execução
      const novaExecucaoBtn = screen.getByText(/nova execução/i);
      fireEvent.click(novaExecucaoBtn);

      await waitFor(() => {
        expect(screen.getByText(/configurar execução/i)).toBeInTheDocument();
      });

      // Selecionar categoria
      const categoriaSelect = screen.getByLabelText(/categoria/i);
      fireEvent.change(categoriaSelect, { target: { value: '1' } });

      // Upload de arquivo
      const fileInput = screen.getByLabelText(/arquivo de keywords/i);
      const file = new File(['keyword1\nkeyword2\nkeyword3'], 'keywords.txt', { type: 'text/plain' });
      fireEvent.change(fileInput, { target: { files: [file] } });

      // Iniciar execução
      const iniciarBtn = screen.getByText(/iniciar execução/i);
      fireEvent.click(iniciarBtn);

      await waitFor(() => {
        expect(screen.getByText(/execução iniciada com sucesso/i)).toBeInTheDocument();
      });
    });
  });

  describe('Cenários de Erro', () => {
    test('Tratamento de erro na criação de nicho', async () => {
      // Mock de erro na API
      const mockAPI = require('../../app/hooks/useAPI');
      mockAPI.useAPI = () => ({
        post: jest.fn().mockRejectedValue(new Error('Erro na criação')),
      });

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      // Navegar para nichos
      const nichosLink = screen.getByText(/nichos/i);
      fireEvent.click(nichosLink);

      await waitFor(() => {
        expect(screen.getByText(/gestão de nichos/i)).toBeInTheDocument();
      });

      // Tentar criar nicho
      const criarNichoBtn = screen.getByText(/criar nicho/i);
      fireEvent.click(criarNichoBtn);

      const nomeInput = screen.getByLabelText(/nome do nicho/i);
      fireEvent.change(nomeInput, { target: { value: 'Nicho com Erro' } });

      const salvarBtn = screen.getByText(/salvar/i);
      fireEvent.click(salvarBtn);

      await waitFor(() => {
        expect(screen.getByText(/erro na criação/i)).toBeInTheDocument();
      });
    });

    test('Validação de formulário com campos obrigatórios', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      // Navegar para nichos
      const nichosLink = screen.getByText(/nichos/i);
      fireEvent.click(nichosLink);

      await waitFor(() => {
        expect(screen.getByText(/gestão de nichos/i)).toBeInTheDocument();
      });

      // Tentar salvar sem preencher campos
      const criarNichoBtn = screen.getByText(/criar nicho/i);
      fireEvent.click(criarNichoBtn);

      const salvarBtn = screen.getByText(/salvar/i);
      fireEvent.click(salvarBtn);

      await waitFor(() => {
        expect(screen.getByText(/nome é obrigatório/i)).toBeInTheDocument();
      });
    });

    test('Tratamento de erro de rede', async () => {
      // Mock de erro de rede
      const mockAPI = require('../../app/hooks/useAPI');
      mockAPI.useAPI = () => ({
        get: jest.fn().mockRejectedValue(new Error('Network Error')),
      });

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/erro de conexão/i)).toBeInTheDocument();
      });
    });
  });

  describe('Validação de Permissões', () => {
    test('Acesso negado para usuário sem permissões', async () => {
      // Mock de usuário sem permissões
      const mockPermissions = require('../../app/hooks/usePermissions');
      mockPermissions.usePermissions = () => ({
        hasPermission: jest.fn(() => false),
        userRole: 'user',
        permissions: ['read'],
      });

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      // Tentar acessar área administrativa
      const adminLink = screen.queryByText(/administração/i);
      if (adminLink) {
        fireEvent.click(adminLink);

        await waitFor(() => {
          expect(screen.getByText(/acesso negado/i)).toBeInTheDocument();
        });
      }
    });

    test('Funcionalidades limitadas para usuário básico', async () => {
      // Mock de usuário básico
      const mockPermissions = require('../../app/hooks/usePermissions');
      mockPermissions.usePermissions = () => ({
        hasPermission: jest.fn((permission) => permission === 'read'),
        userRole: 'user',
        permissions: ['read'],
      });

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      // Verificar se botões de criação estão ocultos
      await waitFor(() => {
        const criarNichoBtn = screen.queryByText(/criar nicho/i);
        expect(criarNichoBtn).not.toBeInTheDocument();
      });
    });

    test('Acesso completo para administrador', async () => {
      // Mock de administrador
      const mockPermissions = require('../../app/hooks/usePermissions');
      mockPermissions.usePermissions = () => ({
        hasPermission: jest.fn(() => true),
        userRole: 'admin',
        permissions: ['read', 'write', 'delete', 'admin'],
      });

      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      // Verificar se todas as funcionalidades estão disponíveis
      await waitFor(() => {
        expect(screen.getByText(/criar nicho/i)).toBeInTheDocument();
        expect(screen.getByText(/criar categoria/i)).toBeInTheDocument();
        expect(screen.getByText(/nova execução/i)).toBeInTheDocument();
      });
    });
  });

  describe('Navegação e UX', () => {
    test('Breadcrumbs funcionam corretamente', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      // Navegar para nichos
      const nichosLink = screen.getByText(/nichos/i);
      fireEvent.click(nichosLink);

      await waitFor(() => {
        expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
        expect(screen.getByText(/nichos/i)).toBeInTheDocument();
      });

      // Navegar para criação de nicho
      const criarNichoBtn = screen.getByText(/criar nicho/i);
      fireEvent.click(criarNichoBtn);

      await waitFor(() => {
        expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
        expect(screen.getByText(/nichos/i)).toBeInTheDocument();
        expect(screen.getByText(/novo nicho/i)).toBeInTheDocument();
      });
    });

    test('Notificações aparecem corretamente', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      // Simular ação que gera notificação
      const nichosLink = screen.getByText(/nichos/i);
      fireEvent.click(nichosLink);

      await waitFor(() => {
        expect(screen.getByText(/nichos carregados/i)).toBeInTheDocument();
      });
    });

    test('Loading states funcionam corretamente', async () => {
      render(
        <TestWrapper>
          <AppRouter />
        </TestWrapper>
      );

      // Verificar se loading aparece durante carregamento
      expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.queryByTestId('loading-skeleton')).not.toBeInTheDocument();
      });
    });
  });
}); 