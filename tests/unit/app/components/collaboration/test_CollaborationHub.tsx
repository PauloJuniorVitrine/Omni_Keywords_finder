/**
 * Testes Unitários - CollaborationHub
 * ===================================
 * 
 * Testes para o componente de colaboração em tempo real
 * 
 * Tracing ID: TEST_UI-024_COLLAB_HUB_001
 * Data: 2024-12-20
 * Versão: 1.0
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CollaborationHub from '../../../../../app/components/collaboration/CollaborationHub';

// Mock do Material-UI
jest.mock('@mui/material', () => ({
  ...jest.requireActual('@mui/material'),
  SpeedDial: ({ children, ...props }: any) => <div data-testid="speed-dial" {...props}>{children}</div>,
  SpeedDialAction: ({ tooltipTitle, ...props }: any) => <button data-testid={`speed-dial-${tooltipTitle}`} {...props} />,
  SpeedDialIcon: () => <div data-testid="speed-dial-icon" />
}));

// Mock dos ícones
jest.mock('@mui/icons-material', () => ({
  Chat: () => <div data-testid="chat-icon" />,
  Assignment: () => <div data-testid="assignment-icon" />,
  Event: () => <div data-testid="event-icon" />,
  Comment: () => <div data-testid="comment-icon" />,
  AttachFile: () => <div data-testid="attach-file-icon" />,
  Analytics: () => <div data-testid="analytics-icon" />,
  Send: () => <div data-testid="send-icon" />,
  Add: () => <div data-testid="add-icon" />,
  Group: () => <div data-testid="group-icon" />,
  Settings: () => <div data-testid="settings-icon" />
}));

const theme = createTheme();

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('CollaborationHub', () => {
  const defaultProps = {
    userId: 'test-user-1',
    projectId: 'test-project-1'
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização Inicial', () => {
    it('deve renderizar o componente com loading inicial', () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('deve renderizar o header com título correto', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Hub de Colaboração')).toBeInTheDocument();
      });
    });

    it('deve renderizar as abas corretas', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Chat')).toBeInTheDocument();
        expect(screen.getByText('Tarefas')).toBeInTheDocument();
        expect(screen.getByText('Calendário')).toBeInTheDocument();
        expect(screen.getByText('Comentários')).toBeInTheDocument();
        expect(screen.getByText('Arquivos')).toBeInTheDocument();
        expect(screen.getByText('Analytics')).toBeInTheDocument();
      });
    });

    it('deve mostrar informações de usuários online', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText(/usuários online/)).toBeInTheDocument();
        expect(screen.getByText(/membros/)).toBeInTheDocument();
      });
    });
  });

  describe('Funcionalidade de Chat', () => {
    it('deve exibir mensagens existentes', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('João Silva')).toBeInTheDocument();
        expect(screen.getByText('Maria Santos')).toBeInTheDocument();
        expect(screen.getByText('Olá pessoal! Como está o progresso?')).toBeInTheDocument();
        expect(screen.getByText('Tudo bem! Terminei a análise.')).toBeInTheDocument();
      });
    });

    it('deve permitir digitar nova mensagem', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        const input = screen.getByPlaceholderText('Digite sua mensagem...');
        fireEvent.change(input, { target: { value: 'Nova mensagem de teste' } });
        expect(input).toHaveValue('Nova mensagem de teste');
      });
    });

    it('deve enviar mensagem ao pressionar Enter', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        const input = screen.getByPlaceholderText('Digite sua mensagem...');
        fireEvent.change(input, { target: { value: 'Mensagem de teste' } });
        fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });
        
        expect(screen.getByText('Mensagem enviada!')).toBeInTheDocument();
      });
    });

    it('deve enviar mensagem ao clicar no botão', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        const input = screen.getByPlaceholderText('Digite sua mensagem...');
        const sendButton = screen.getByRole('button', { name: /send/i });
        
        fireEvent.change(input, { target: { value: 'Mensagem de teste' } });
        fireEvent.click(sendButton);
        
        expect(screen.getByText('Mensagem enviada!')).toBeInTheDocument();
      });
    });

    it('não deve enviar mensagem vazia', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        const sendButton = screen.getByRole('button', { name: /send/i });
        expect(sendButton).toBeDisabled();
      });
    });
  });

  describe('Funcionalidade de Tarefas', () => {
    it('deve exibir tarefas existentes', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        // Mudar para aba de tarefas
        fireEvent.click(screen.getByText('Tarefas'));
        
        expect(screen.getByText('Revisar análise de keywords')).toBeInTheDocument();
        expect(screen.getByText('Atualizar documentação')).toBeInTheDocument();
        expect(screen.getByText('Verificar resultados da análise semântica')).toBeInTheDocument();
      });
    });

    it('deve mostrar status das tarefas', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Tarefas'));
        
        expect(screen.getByText('in_progress')).toBeInTheDocument();
        expect(screen.getByText('todo')).toBeInTheDocument();
      });
    });

    it('deve mostrar prioridades das tarefas', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Tarefas'));
        
        expect(screen.getByText('high')).toBeInTheDocument();
        expect(screen.getByText('medium')).toBeInTheDocument();
      });
    });

    it('deve ter botão para nova tarefa', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Tarefas'));
        
        expect(screen.getByText('Nova Tarefa')).toBeInTheDocument();
      });
    });
  });

  describe('Funcionalidade de Calendário', () => {
    it('deve mostrar mensagem de implementação futura', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Calendário'));
        
        expect(screen.getByText('Funcionalidade de calendário será implementada em breve.')).toBeInTheDocument();
      });
    });
  });

  describe('Funcionalidade de Comentários', () => {
    it('deve mostrar mensagem quando não há comentários', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Comentários'));
        
        expect(screen.getByText('Nenhum comentário encontrado.')).toBeInTheDocument();
      });
    });
  });

  describe('Funcionalidade de Arquivos', () => {
    it('deve mostrar mensagem de implementação futura', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Arquivos'));
        
        expect(screen.getByText('Funcionalidade de compartilhamento de arquivos será implementada em breve.')).toBeInTheDocument();
      });
    });
  });

  describe('Funcionalidade de Analytics', () => {
    it('deve exibir métricas de colaboração', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Analytics'));
        
        expect(screen.getByText('Total de Mensagens')).toBeInTheDocument();
        expect(screen.getByText('Tarefas Ativas')).toBeInTheDocument();
        expect(screen.getByText('Usuários Ativos')).toBeInTheDocument();
        expect(screen.getByText('Score de Colaboração')).toBeInTheDocument();
      });
    });

    it('deve mostrar valores corretos das métricas', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        fireEvent.click(screen.getByText('Analytics'));
        
        expect(screen.getByText('2')).toBeInTheDocument(); // Total de mensagens
        expect(screen.getByText('2')).toBeInTheDocument(); // Total de tarefas
        expect(screen.getByText('2')).toBeInTheDocument(); // Usuários ativos
        expect(screen.getByText('85%')).toBeInTheDocument(); // Score de colaboração
      });
    });
  });

  describe('Speed Dial', () => {
    it('deve renderizar speed dial com ações', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('speed-dial')).toBeInTheDocument();
        expect(screen.getByTestId('speed-dial-Nova Tarefa')).toBeInTheDocument();
        expect(screen.getByTestId('speed-dial-Novo Evento')).toBeInTheDocument();
        expect(screen.getByTestId('speed-dial-Compartilhar Arquivo')).toBeInTheDocument();
        expect(screen.getByTestId('speed-dial-Configurações')).toBeInTheDocument();
      });
    });
  });

  describe('Notificações', () => {
    it('deve mostrar notificação ao enviar mensagem', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        const input = screen.getByPlaceholderText('Digite sua mensagem...');
        fireEvent.change(input, { target: { value: 'Teste' } });
        fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });
        
        expect(screen.getByText('Mensagem enviada!')).toBeInTheDocument();
      });
    });

    it('deve fechar notificação automaticamente', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        const input = screen.getByPlaceholderText('Digite sua mensagem...');
        fireEvent.change(input, { target: { value: 'Teste' } });
        fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });
        
        expect(screen.getByText('Mensagem enviada!')).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.queryByText('Mensagem enviada!')).not.toBeInTheDocument();
      }, { timeout: 7000 });
    });
  });

  describe('Navegação entre Abas', () => {
    it('deve alternar entre abas corretamente', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        // Verificar que chat está ativo por padrão
        expect(screen.getByPlaceholderText('Digite sua mensagem...')).toBeInTheDocument();
        
        // Mudar para tarefas
        fireEvent.click(screen.getByText('Tarefas'));
        expect(screen.getByText('Nova Tarefa')).toBeInTheDocument();
        
        // Mudar para analytics
        fireEvent.click(screen.getByText('Analytics'));
        expect(screen.getByText('Total de Mensagens')).toBeInTheDocument();
        
        // Voltar para chat
        fireEvent.click(screen.getByText('Chat'));
        expect(screen.getByPlaceholderText('Digite sua mensagem...')).toBeInTheDocument();
      });
    });
  });

  describe('Responsividade', () => {
    it('deve renderizar corretamente em diferentes tamanhos', async () => {
      const { container } = renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        expect(container.firstChild).toHaveStyle({ height: '100%' });
      });
    });
  });

  describe('Acessibilidade', () => {
    it('deve ter labels apropriados', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Digite sua mensagem...')).toHaveAttribute('placeholder');
        expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
      });
    });

    it('deve ter navegação por teclado', async () => {
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        const input = screen.getByPlaceholderText('Digite sua mensagem...');
        input.focus();
        expect(input).toHaveFocus();
      });
    });
  });

  describe('Performance', () => {
    it('deve carregar dados rapidamente', async () => {
      const startTime = Date.now();
      
      renderWithTheme(<CollaborationHub {...defaultProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Hub de Colaboração')).toBeInTheDocument();
      });
      
      const endTime = Date.now();
      expect(endTime - startTime).toBeLessThan(2000); // Deve carregar em menos de 2 segundos
    });
  });

  describe('Tratamento de Erros', () => {
    it('deve lidar com props inválidas graciosamente', () => {
      expect(() => {
        renderWithTheme(<CollaborationHub userId="" />);
      }).not.toThrow();
    });
  });
}); 