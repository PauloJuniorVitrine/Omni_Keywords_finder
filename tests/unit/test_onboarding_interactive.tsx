/**
 * Testes Unitários para Onboarding Interativo - Omni Keywords Finder
 * Validação do componente de onboarding interativo
 * 
 * Tracing ID: ONBOARDING_TESTING_20250127_001
 * Data: 2025-01-27
 * Versão: 1.0
 * Status: 🟡 ALTO - Testes de Onboarding Interativo
 * 
 * Baseado no código real do sistema Omni Keywords Finder
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import InteractiveOnboarding from '../../app/components/onboarding/InteractiveOnboarding';

// Mock do react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock do framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
  AnimatePresence: ({ children }: any) => <div>{children}</div>,
}));

// Mock dos ícones do lucide-react
vi.mock('lucide-react', () => ({
  CheckCircle: () => <div data-testid="check-circle">✓</div>,
  AlertCircle: () => <div data-testid="alert-circle">⚠</div>,
  ArrowRight: () => <div data-testid="arrow-right">→</div>,
  ArrowLeft: () => <div data-testid="arrow-left">←</div>,
  Loader2: () => <div data-testid="loader">⏳</div>,
  User: () => <div data-testid="user-icon">👤</div>,
  Settings: () => <div data-testid="settings-icon">⚙️</div>,
  Target: () => <div data-testid="target-icon">🎯</div>,
  Database: () => <div data-testid="database-icon">🗄️</div>,
  Shield: () => <div data-testid="shield-icon">🛡️</div>,
  Zap: () => <div data-testid="zap-icon">⚡</div>,
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('InteractiveOnboarding', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Renderização Inicial', () => {
    it('deve renderizar o componente de onboarding corretamente', () => {
      renderWithRouter(<InteractiveOnboarding />);
      
      // Verificar elementos principais
      expect(screen.getByText('Omni Keywords Finder')).toBeInTheDocument();
      expect(screen.getByText('Passo 1 de 5')).toBeInTheDocument();
      expect(screen.getByText('Bem-vindo ao Omni Keywords Finder')).toBeInTheDocument();
    });

    it('deve mostrar a barra de progresso inicial', () => {
      renderWithRouter(<InteractiveOnboarding />);
      
      const progressBar = screen.getByRole('progressbar', { hidden: true });
      expect(progressBar).toBeInTheDocument();
    });

    it('deve mostrar os indicadores dos passos', () => {
      renderWithRouter(<InteractiveOnboarding />);
      
      // Verificar se os 5 passos estão visíveis
      expect(screen.getByText('Bem-vindo')).toBeInTheDocument();
      expect(screen.getByText('Projeto')).toBeInTheDocument();
      expect(screen.getByText('Técnico')).toBeInTheDocument();
      expect(screen.getByText('Preferências')).toBeInTheDocument();
      expect(screen.getByText('Conclusão')).toBeInTheDocument();
    });
  });

  describe('Passo 1 - Welcome', () => {
    it('deve mostrar os campos de nome e email', () => {
      renderWithRouter(<InteractiveOnboarding />);
      
      expect(screen.getByLabelText('Nome Completo')).toBeInTheDocument();
      expect(screen.getByLabelText('E-mail')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Digite seu nome completo')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('seu@email.com')).toBeInTheDocument();
    });

    it('deve desabilitar o botão continuar quando campos estão vazios', () => {
      renderWithRouter(<InteractiveOnboarding />);
      
      const continueButton = screen.getByText('Continuar');
      expect(continueButton).toBeDisabled();
    });

    it('deve habilitar o botão continuar quando campos são preenchidos', () => {
      renderWithRouter(<InteractiveOnboarding />);
      
      const nameInput = screen.getByLabelText('Nome Completo');
      const emailInput = screen.getByLabelText('E-mail');
      
      fireEvent.change(nameInput, { target: { value: 'João Silva' } });
      fireEvent.change(emailInput, { target: { value: 'joao@example.com' } });
      
      const continueButton = screen.getByText('Continuar');
      expect(continueButton).not.toBeDisabled();
    });

    it('deve avançar para o próximo passo quando continuar é clicado', async () => {
      renderWithRouter(<InteractiveOnboarding />);
      
      const nameInput = screen.getByLabelText('Nome Completo');
      const emailInput = screen.getByLabelText('E-mail');
      
      fireEvent.change(nameInput, { target: { value: 'João Silva' } });
      fireEvent.change(emailInput, { target: { value: 'joao@example.com' } });
      
      const continueButton = screen.getByText('Continuar');
      fireEvent.click(continueButton);
      
      // Verificar se avançou para o passo 2
      await waitFor(() => {
        expect(screen.getByText('Configure seu Projeto')).toBeInTheDocument();
      });
    });
  });

  describe('Passo 2 - Project Setup', () => {
    beforeEach(async () => {
      renderWithRouter(<InteractiveOnboarding />);
      
      // Preencher e avançar do passo 1
      const nameInput = screen.getByLabelText('Nome Completo');
      const emailInput = screen.getByLabelText('E-mail');
      
      fireEvent.change(nameInput, { target: { value: 'João Silva' } });
      fireEvent.change(emailInput, { target: { value: 'joao@example.com' } });
      
      const continueButton = screen.getByText('Continuar');
      fireEvent.click(continueButton);
      
      await waitFor(() => {
        expect(screen.getByText('Configure seu Projeto')).toBeInTheDocument();
      });
    });

    it('deve mostrar os campos do projeto', () => {
      expect(screen.getByLabelText('Nome do Projeto')).toBeInTheDocument();
      expect(screen.getByLabelText('Domínio do Site')).toBeInTheDocument();
      expect(screen.getByLabelText('Setor/Indústria')).toBeInTheDocument();
    });

    it('deve mostrar as opções de indústria', () => {
      const industrySelect = screen.getByLabelText('Setor/Indústria');
      fireEvent.click(industrySelect);
      
      expect(screen.getByText('E-commerce')).toBeInTheDocument();
      expect(screen.getByText('Saúde')).toBeInTheDocument();
      expect(screen.getByText('Educação')).toBeInTheDocument();
      expect(screen.getByText('Tecnologia')).toBeInTheDocument();
    });

    it('deve permitir voltar para o passo anterior', async () => {
      const backButton = screen.getByText('Voltar');
      fireEvent.click(backButton);
      
      await waitFor(() => {
        expect(screen.getByText('Bem-vindo ao Omni Keywords Finder')).toBeInTheDocument();
      });
    });

    it('deve avançar para o próximo passo quando campos obrigatórios são preenchidos', async () => {
      const projectNameInput = screen.getByLabelText('Nome do Projeto');
      const domainInput = screen.getByLabelText('Domínio do Site');
      const industrySelect = screen.getByLabelText('Setor/Indústria');
      
      fireEvent.change(projectNameInput, { target: { value: 'Meu Projeto' } });
      fireEvent.change(domainInput, { target: { value: 'https://meusite.com' } });
      fireEvent.change(industrySelect, { target: { value: 'E-commerce' } });
      
      const continueButton = screen.getByText('Continuar');
      fireEvent.click(continueButton);
      
      await waitFor(() => {
        expect(screen.getByText('Configurações Técnicas')).toBeInTheDocument();
      });
    });
  });

  describe('Passo 3 - Technical Setup', () => {
    beforeEach(async () => {
      renderWithRouter(<InteractiveOnboarding />);
      
      // Navegar até o passo 3
      const nameInput = screen.getByLabelText('Nome Completo');
      const emailInput = screen.getByLabelText('E-mail');
      
      fireEvent.change(nameInput, { target: { value: 'João Silva' } });
      fireEvent.change(emailInput, { target: { value: 'joao@example.com' } });
      
      fireEvent.click(screen.getByText('Continuar'));
      
      await waitFor(() => {
        expect(screen.getByText('Configure seu Projeto')).toBeInTheDocument();
      });
      
      const projectNameInput = screen.getByLabelText('Nome do Projeto');
      const domainInput = screen.getByLabelText('Domínio do Site');
      const industrySelect = screen.getByLabelText('Setor/Indústria');
      
      fireEvent.change(projectNameInput, { target: { value: 'Meu Projeto' } });
      fireEvent.change(domainInput, { target: { value: 'https://meusite.com' } });
      fireEvent.change(industrySelect, { target: { value: 'E-commerce' } });
      
      fireEvent.click(screen.getByText('Continuar'));
      
      await waitFor(() => {
        expect(screen.getByText('Configurações Técnicas')).toBeInTheDocument();
      });
    });

    it('deve mostrar os campos técnicos', () => {
      expect(screen.getByLabelText('Chave da API (Opcional)')).toBeInTheDocument();
      expect(screen.getByLabelText('Motor de Busca')).toBeInTheDocument();
      expect(screen.getByLabelText('Idioma')).toBeInTheDocument();
      expect(screen.getByLabelText('Região')).toBeInTheDocument();
    });

    it('deve mostrar as opções de motor de busca', () => {
      const searchEngineSelect = screen.getByLabelText('Motor de Busca');
      fireEvent.click(searchEngineSelect);
      
      expect(screen.getByText('Google')).toBeInTheDocument();
      expect(screen.getByText('Bing')).toBeInTheDocument();
      expect(screen.getByText('Google + Bing')).toBeInTheDocument();
    });

    it('deve permitir continuar sem preencher API key', async () => {
      const continueButton = screen.getByText('Continuar');
      fireEvent.click(continueButton);
      
      await waitFor(() => {
        expect(screen.getByText('Suas Preferências')).toBeInTheDocument();
      });
    });
  });

  describe('Passo 4 - Preferences', () => {
    beforeEach(async () => {
      renderWithRouter(<InteractiveOnboarding />);
      
      // Navegar até o passo 4
      const nameInput = screen.getByLabelText('Nome Completo');
      const emailInput = screen.getByLabelText('E-mail');
      
      fireEvent.change(nameInput, { target: { value: 'João Silva' } });
      fireEvent.change(emailInput, { target: { value: 'joao@example.com' } });
      
      fireEvent.click(screen.getByText('Continuar'));
      
      await waitFor(() => {
        expect(screen.getByText('Configure seu Projeto')).toBeInTheDocument();
      });
      
      const projectNameInput = screen.getByLabelText('Nome do Projeto');
      const domainInput = screen.getByLabelText('Domínio do Site');
      const industrySelect = screen.getByLabelText('Setor/Indústria');
      
      fireEvent.change(projectNameInput, { target: { value: 'Meu Projeto' } });
      fireEvent.change(domainInput, { target: { value: 'https://meusite.com' } });
      fireEvent.change(industrySelect, { target: { value: 'E-commerce' } });
      
      fireEvent.click(screen.getByText('Continuar'));
      
      await waitFor(() => {
        expect(screen.getByText('Configurações Técnicas')).toBeInTheDocument();
      });
      
      fireEvent.click(screen.getByText('Continuar'));
      
      await waitFor(() => {
        expect(screen.getByText('Suas Preferências')).toBeInTheDocument();
      });
    });

    it('deve mostrar as opções de preferências', () => {
      expect(screen.getByText('Notificações')).toBeInTheDocument();
      expect(screen.getByText('Receber alertas sobre mudanças de ranking')).toBeInTheDocument();
      expect(screen.getByLabelText('Frequência de Relatórios')).toBeInTheDocument();
      expect(screen.getByLabelText('Tipo de Dashboard')).toBeInTheDocument();
    });

    it('deve permitir alternar notificações', () => {
      const notificationToggle = screen.getByRole('checkbox');
      expect(notificationToggle).toBeChecked(); // Padrão é true
      
      fireEvent.click(notificationToggle);
      expect(notificationToggle).not.toBeChecked();
    });

    it('deve mostrar as opções de relatórios', () => {
      const reportsSelect = screen.getByLabelText('Frequência de Relatórios');
      fireEvent.click(reportsSelect);
      
      expect(screen.getByText('Diário')).toBeInTheDocument();
      expect(screen.getByText('Semanal')).toBeInTheDocument();
      expect(screen.getByText('Mensal')).toBeInTheDocument();
    });

    it('deve mostrar as opções de dashboard', () => {
      const dashboardSelect = screen.getByLabelText('Tipo de Dashboard');
      fireEvent.click(dashboardSelect);
      
      expect(screen.getByText('Simples')).toBeInTheDocument();
      expect(screen.getByText('Avançado')).toBeInTheDocument();
    });
  });

  describe('Passo 5 - Completion', () => {
    beforeEach(async () => {
      renderWithRouter(<InteractiveOnboarding />);
      
      // Navegar até o passo 5
      const nameInput = screen.getByLabelText('Nome Completo');
      const emailInput = screen.getByLabelText('E-mail');
      
      fireEvent.change(nameInput, { target: { value: 'João Silva' } });
      fireEvent.change(emailInput, { target: { value: 'joao@example.com' } });
      
      fireEvent.click(screen.getByText('Continuar'));
      
      await waitFor(() => {
        expect(screen.getByText('Configure seu Projeto')).toBeInTheDocument();
      });
      
      const projectNameInput = screen.getByLabelText('Nome do Projeto');
      const domainInput = screen.getByLabelText('Domínio do Site');
      const industrySelect = screen.getByLabelText('Setor/Indústria');
      
      fireEvent.change(projectNameInput, { target: { value: 'Meu Projeto' } });
      fireEvent.change(domainInput, { target: { value: 'https://meusite.com' } });
      fireEvent.change(industrySelect, { target: { value: 'E-commerce' } });
      
      fireEvent.click(screen.getByText('Continuar'));
      
      await waitFor(() => {
        expect(screen.getByText('Configurações Técnicas')).toBeInTheDocument();
      });
      
      fireEvent.click(screen.getByText('Continuar'));
      
      await waitFor(() => {
        expect(screen.getByText('Suas Preferências')).toBeInTheDocument();
      });
      
      fireEvent.click(screen.getByText('Finalizar'));
      
      await waitFor(() => {
        expect(screen.getByText('Configurando sua conta...')).toBeInTheDocument();
      });
    });

    it('deve mostrar a tela de carregamento inicialmente', () => {
      expect(screen.getByText('Configurando sua conta...')).toBeInTheDocument();
      expect(screen.getByText('Estamos salvando suas configurações e preparando seu dashboard.')).toBeInTheDocument();
    });

    it('deve mostrar a tela de conclusão após o carregamento', async () => {
      await waitFor(() => {
        expect(screen.getByText('Tudo pronto!')).toBeInTheDocument();
      }, { timeout: 3000 });
      
      expect(screen.getByText('Sua conta foi configurada com sucesso. Você será redirecionado para o dashboard.')).toBeInTheDocument();
    });

    it('deve mostrar o resumo da configuração', async () => {
      await waitFor(() => {
        expect(screen.getByText('Resumo da configuração:')).toBeInTheDocument();
      }, { timeout: 3000 });
      
      expect(screen.getByText('• Projeto: Meu Projeto')).toBeInTheDocument();
      expect(screen.getByText('• Domínio: https://meusite.com')).toBeInTheDocument();
      expect(screen.getByText('• Setor: E-commerce')).toBeInTheDocument();
      expect(screen.getByText('• Relatórios: weekly')).toBeInTheDocument();
    });

    it('deve redirecionar para o dashboard quando finalizar é clicado', async () => {
      await waitFor(() => {
        expect(screen.getByText('Ir para o Dashboard')).toBeInTheDocument();
      }, { timeout: 3000 });
      
      const dashboardButton = screen.getByText('Ir para o Dashboard');
      fireEvent.click(dashboardButton);
      
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  describe('Navegação e Funcionalidades', () => {
    it('deve permitir pular o onboarding', () => {
      renderWithRouter(<InteractiveOnboarding />);
      
      const skipButton = screen.getByText('Pular para depois');
      fireEvent.click(skipButton);
      
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });

    it('deve atualizar o progresso conforme avança pelos passos', async () => {
      renderWithRouter(<InteractiveOnboarding />);
      
      // Passo 1
      expect(screen.getByText('Passo 1 de 5')).toBeInTheDocument();
      
      // Avançar para passo 2
      const nameInput = screen.getByLabelText('Nome Completo');
      const emailInput = screen.getByLabelText('E-mail');
      
      fireEvent.change(nameInput, { target: { value: 'João Silva' } });
      fireEvent.change(emailInput, { target: { value: 'joao@example.com' } });
      
      fireEvent.click(screen.getByText('Continuar'));
      
      await waitFor(() => {
        expect(screen.getByText('Passo 2 de 5')).toBeInTheDocument();
      });
    });

    it('deve manter os dados entre os passos', async () => {
      renderWithRouter(<InteractiveOnboarding />);
      
      // Preencher dados no passo 1
      const nameInput = screen.getByLabelText('Nome Completo');
      const emailInput = screen.getByLabelText('E-mail');
      
      fireEvent.change(nameInput, { target: { value: 'João Silva' } });
      fireEvent.change(emailInput, { target: { value: 'joao@example.com' } });
      
      fireEvent.click(screen.getByText('Continuar'));
      
      await waitFor(() => {
        expect(screen.getByText('Configure seu Projeto')).toBeInTheDocument();
      });
      
      // Voltar para o passo 1
      fireEvent.click(screen.getByText('Voltar'));
      
      await waitFor(() => {
        expect(screen.getByText('Bem-vindo ao Omni Keywords Finder')).toBeInTheDocument();
      });
      
      // Verificar se os dados foram mantidos
      expect(screen.getByDisplayValue('João Silva')).toBeInTheDocument();
      expect(screen.getByDisplayValue('joao@example.com')).toBeInTheDocument();
    });
  });

  describe('Validações', () => {
    it('deve validar email no formato correto', () => {
      renderWithRouter(<InteractiveOnboarding />);
      
      const nameInput = screen.getByLabelText('Nome Completo');
      const emailInput = screen.getByLabelText('E-mail');
      
      fireEvent.change(nameInput, { target: { value: 'João Silva' } });
      fireEvent.change(emailInput, { target: { value: 'email-invalido' } });
      
      const continueButton = screen.getByText('Continuar');
      expect(continueButton).toBeDisabled();
      
      fireEvent.change(emailInput, { target: { value: 'email@valido.com' } });
      expect(continueButton).not.toBeDisabled();
    });

    it('deve validar campos obrigatórios no passo do projeto', async () => {
      renderWithRouter(<InteractiveOnboarding />);
      
      // Avançar para o passo 2
      const nameInput = screen.getByLabelText('Nome Completo');
      const emailInput = screen.getByLabelText('E-mail');
      
      fireEvent.change(nameInput, { target: { value: 'João Silva' } });
      fireEvent.change(emailInput, { target: { value: 'joao@example.com' } });
      
      fireEvent.click(screen.getByText('Continuar'));
      
      await waitFor(() => {
        expect(screen.getByText('Configure seu Projeto')).toBeInTheDocument();
      });
      
      const continueButton = screen.getByText('Continuar');
      expect(continueButton).toBeDisabled();
      
      // Preencher campos obrigatórios
      const projectNameInput = screen.getByLabelText('Nome do Projeto');
      const domainInput = screen.getByLabelText('Domínio do Site');
      const industrySelect = screen.getByLabelText('Setor/Indústria');
      
      fireEvent.change(projectNameInput, { target: { value: 'Meu Projeto' } });
      fireEvent.change(domainInput, { target: { value: 'https://meusite.com' } });
      fireEvent.change(industrySelect, { target: { value: 'E-commerce' } });
      
      expect(continueButton).not.toBeDisabled();
    });
  });
}); 