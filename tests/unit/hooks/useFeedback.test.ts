/**
 * Testes Unitários - useFeedback Hook
 * 
 * Prompt: Implementação de testes para componentes importantes
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_USE_FEEDBACK_027
 * 
 * Baseado em código real do useFeedback.ts
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useFeedback } from '../../../app/hooks/useFeedback';

// Mock do fetch global
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('useFeedback - Hook de Feedback', () => {
  
  beforeEach(() => {
    jest.clearAllMocks();
    mockFetch.mockClear();
  });

  describe('Estados Iniciais', () => {
    
    test('deve retornar estados iniciais corretos', () => {
      const { result } = renderHook(() => useFeedback());
      
      expect(result.current.isModalOpen).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(null);
    });

    test('deve retornar funções necessárias', () => {
      const { result } = renderHook(() => useFeedback());
      
      expect(typeof result.current.openModal).toBe('function');
      expect(typeof result.current.closeModal).toBe('function');
      expect(typeof result.current.submitFeedback).toBe('function');
    });
  });

  describe('Controle do Modal', () => {
    
    test('deve abrir o modal corretamente', () => {
      const { result } = renderHook(() => useFeedback());
      
      act(() => {
        result.current.openModal();
      });
      
      expect(result.current.isModalOpen).toBe(true);
      expect(result.current.error).toBe(null);
    });

    test('deve fechar o modal corretamente', () => {
      const { result } = renderHook(() => useFeedback());
      
      // Abrir modal primeiro
      act(() => {
        result.current.openModal();
      });
      
      expect(result.current.isModalOpen).toBe(true);
      
      // Fechar modal
      act(() => {
        result.current.closeModal();
      });
      
      expect(result.current.isModalOpen).toBe(false);
      expect(result.current.error).toBe(null);
    });

    test('deve limpar erro ao abrir modal', () => {
      const { result } = renderHook(() => useFeedback());
      
      // Simular erro
      act(() => {
        result.current.submitFeedback({
          rating: 5,
          feedback: 'Teste',
          category: 'bug',
          timestamp: new Date().toISOString()
        });
      });
      
      // Abrir modal deve limpar erro
      act(() => {
        result.current.openModal();
      });
      
      expect(result.current.error).toBe(null);
    });

    test('deve limpar erro ao fechar modal', () => {
      const { result } = renderHook(() => useFeedback());
      
      // Simular erro
      act(() => {
        result.current.submitFeedback({
          rating: 5,
          feedback: 'Teste',
          category: 'bug',
          timestamp: new Date().toISOString()
        });
      });
      
      // Fechar modal deve limpar erro
      act(() => {
        result.current.closeModal();
      });
      
      expect(result.current.error).toBe(null);
    });
  });

  describe('Envio de Feedback', () => {
    
    const mockFeedbackData = {
      rating: 5,
      feedback: 'Excelente aplicação! Muito útil para encontrar keywords.',
      category: 'feature',
      email: 'usuario@exemplo.com',
      timestamp: new Date('2025-01-27T10:30:00Z').toISOString()
    };

    test('deve enviar feedback com sucesso', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      const { result } = renderHook(() => useFeedback());
      
      await act(async () => {
        await result.current.submitFeedback(mockFeedbackData);
      });
      
      expect(mockFetch).toHaveBeenCalledWith('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(mockFeedbackData),
      });
      
      expect(result.current.isModalOpen).toBe(false);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(null);
    });

    test('deve mostrar loading durante envio', async () => {
      mockFetch.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

      const { result } = renderHook(() => useFeedback());
      
      act(() => {
        result.current.submitFeedback(mockFeedbackData);
      });
      
      expect(result.current.isLoading).toBe(true);
      
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });
    });

    test('deve tratar erro de resposta não ok', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500
      });

      const { result } = renderHook(() => useFeedback());
      
      await act(async () => {
        await result.current.submitFeedback(mockFeedbackData);
      });
      
      expect(result.current.error).toBe('Erro ao enviar feedback');
      expect(result.current.isLoading).toBe(false);
      expect(result.current.isModalOpen).toBe(true); // Modal permanece aberto
    });

    test('deve tratar erro de rede', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Erro de rede'));

      const { result } = renderHook(() => useFeedback());
      
      await act(async () => {
        await result.current.submitFeedback(mockFeedbackData);
      });
      
      expect(result.current.error).toBe('Erro de rede');
      expect(result.current.isLoading).toBe(false);
      expect(result.current.isModalOpen).toBe(true); // Modal permanece aberto
    });

    test('deve tratar erro desconhecido', async () => {
      mockFetch.mockRejectedValueOnce('Erro desconhecido');

      const { result } = renderHook(() => useFeedback());
      
      await act(async () => {
        await result.current.submitFeedback(mockFeedbackData);
      });
      
      expect(result.current.error).toBe('Erro desconhecido');
      expect(result.current.isLoading).toBe(false);
    });

    test('deve fechar modal após envio bem-sucedido', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      const { result } = renderHook(() => useFeedback());
      
      // Abrir modal primeiro
      act(() => {
        result.current.openModal();
      });
      
      expect(result.current.isModalOpen).toBe(true);
      
      // Enviar feedback
      await act(async () => {
        await result.current.submitFeedback(mockFeedbackData);
      });
      
      expect(result.current.isModalOpen).toBe(false);
    });
  });

  describe('Validação de Dados', () => {
    
    test('deve aceitar dados de feedback válidos', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      const { result } = renderHook(() => useFeedback());
      
      const validData = {
        rating: 4,
        feedback: 'Muito bom aplicativo',
        category: 'bug',
        timestamp: new Date().toISOString()
      };
      
      await act(async () => {
        await result.current.submitFeedback(validData);
      });
      
      expect(mockFetch).toHaveBeenCalledWith('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(validData),
      });
    });

    test('deve aceitar feedback sem email', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      const { result } = renderHook(() => useFeedback());
      
      const dataWithoutEmail = {
        rating: 3,
        feedback: 'Aplicativo funcional',
        category: 'suggestion',
        timestamp: new Date().toISOString()
      };
      
      await act(async () => {
        await result.current.submitFeedback(dataWithoutEmail);
      });
      
      expect(mockFetch).toHaveBeenCalledWith('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dataWithoutEmail),
      });
    });

    test('deve aceitar diferentes categorias de feedback', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200
      });

      const { result } = renderHook(() => useFeedback());
      
      const categories = ['bug', 'feature', 'suggestion', 'other'];
      
      for (const category of categories) {
        const data = {
          rating: 5,
          feedback: `Feedback de ${category}`,
          category,
          timestamp: new Date().toISOString()
        };
        
        await act(async () => {
          await result.current.submitFeedback(data);
        });
        
        expect(mockFetch).toHaveBeenCalledWith('/api/feedback', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });
      }
    });

    test('deve aceitar diferentes ratings', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200
      });

      const { result } = renderHook(() => useFeedback());
      
      for (let rating = 1; rating <= 5; rating++) {
        const data = {
          rating,
          feedback: `Rating ${rating}`,
          category: 'test',
          timestamp: new Date().toISOString()
        };
        
        await act(async () => {
          await result.current.submitFeedback(data);
        });
        
        expect(mockFetch).toHaveBeenCalledWith('/api/feedback', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });
      }
    });
  });

  describe('Estados de Loading', () => {
    
    test('deve iniciar loading ao enviar feedback', async () => {
      mockFetch.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

      const { result } = renderHook(() => useFeedback());
      
      act(() => {
        result.current.submitFeedback({
          rating: 5,
          feedback: 'Teste',
          category: 'bug',
          timestamp: new Date().toISOString()
        });
      });
      
      expect(result.current.isLoading).toBe(true);
    });

    test('deve finalizar loading após sucesso', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      const { result } = renderHook(() => useFeedback());
      
      await act(async () => {
        await result.current.submitFeedback({
          rating: 5,
          feedback: 'Teste',
          category: 'bug',
          timestamp: new Date().toISOString()
        });
      });
      
      expect(result.current.isLoading).toBe(false);
    });

    test('deve finalizar loading após erro', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Erro de teste'));

      const { result } = renderHook(() => useFeedback());
      
      await act(async () => {
        await result.current.submitFeedback({
          rating: 5,
          feedback: 'Teste',
          category: 'bug',
          timestamp: new Date().toISOString()
        });
      });
      
      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('Tratamento de Erros', () => {
    
    test('deve capturar erro de rede', async () => {
      const networkError = new Error('Erro de conexão');
      mockFetch.mockRejectedValueOnce(networkError);

      const { result } = renderHook(() => useFeedback());
      
      await act(async () => {
        await result.current.submitFeedback({
          rating: 5,
          feedback: 'Teste',
          category: 'bug',
          timestamp: new Date().toISOString()
        });
      });
      
      expect(result.current.error).toBe('Erro de conexão');
    });

    test('deve capturar erro de resposta HTTP', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request'
      });

      const { result } = renderHook(() => useFeedback());
      
      await act(async () => {
        await result.current.submitFeedback({
          rating: 5,
          feedback: 'Teste',
          category: 'bug',
          timestamp: new Date().toISOString()
        });
      });
      
      expect(result.current.error).toBe('Erro ao enviar feedback');
    });

    test('deve capturar erro de servidor', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });

      const { result } = renderHook(() => useFeedback());
      
      await act(async () => {
        await result.current.submitFeedback({
          rating: 5,
          feedback: 'Teste',
          category: 'bug',
          timestamp: new Date().toISOString()
        });
      });
      
      expect(result.current.error).toBe('Erro ao enviar feedback');
    });

    test('deve tratar erro desconhecido', async () => {
      mockFetch.mockRejectedValueOnce('String de erro');

      const { result } = renderHook(() => useFeedback());
      
      await act(async () => {
        await result.current.submitFeedback({
          rating: 5,
          feedback: 'Teste',
          category: 'bug',
          timestamp: new Date().toISOString()
        });
      });
      
      expect(result.current.error).toBe('Erro desconhecido');
    });
  });

  describe('Integração com API', () => {
    
    test('deve usar endpoint correto', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      const { result } = renderHook(() => useFeedback());
      
      await act(async () => {
        await result.current.submitFeedback({
          rating: 5,
          feedback: 'Teste',
          category: 'bug',
          timestamp: new Date().toISOString()
        });
      });
      
      expect(mockFetch).toHaveBeenCalledWith('/api/feedback', expect.any(Object));
    });

    test('deve usar método POST', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      const { result } = renderHook(() => useFeedback());
      
      await act(async () => {
        await result.current.submitFeedback({
          rating: 5,
          feedback: 'Teste',
          category: 'bug',
          timestamp: new Date().toISOString()
        });
      });
      
      expect(mockFetch).toHaveBeenCalledWith('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: expect.any(String),
      });
    });

    test('deve enviar headers corretos', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      const { result } = renderHook(() => useFeedback());
      
      await act(async () => {
        await result.current.submitFeedback({
          rating: 5,
          feedback: 'Teste',
          category: 'bug',
          timestamp: new Date().toISOString()
        });
      });
      
      expect(mockFetch).toHaveBeenCalledWith('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: expect.any(String),
      });
    });

    test('deve serializar dados corretamente', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200
      });

      const { result } = renderHook(() => useFeedback());
      
      const feedbackData = {
        rating: 5,
        feedback: 'Teste com caracteres especiais: áéíóú çãõ',
        category: 'feature',
        email: 'teste@exemplo.com',
        timestamp: '2025-01-27T10:30:00.000Z'
      };
      
      await act(async () => {
        await result.current.submitFeedback(feedbackData);
      });
      
      expect(mockFetch).toHaveBeenCalledWith('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedbackData),
      });
    });
  });

  describe('Performance e Otimização', () => {
    
    test('deve usar useCallback para otimização', () => {
      const { result, rerender } = renderHook(() => useFeedback());
      
      const initialOpenModal = result.current.openModal;
      const initialCloseModal = result.current.closeModal;
      const initialSubmitFeedback = result.current.submitFeedback;
      
      rerender();
      
      expect(result.current.openModal).toBe(initialOpenModal);
      expect(result.current.closeModal).toBe(initialCloseModal);
      expect(result.current.submitFeedback).toBe(initialSubmitFeedback);
    });

    test('deve lidar com múltiplos envios simultâneos', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200
      });

      const { result } = renderHook(() => useFeedback());
      
      const promises = [
        result.current.submitFeedback({
          rating: 5,
          feedback: 'Feedback 1',
          category: 'bug',
          timestamp: new Date().toISOString()
        }),
        result.current.submitFeedback({
          rating: 4,
          feedback: 'Feedback 2',
          category: 'feature',
          timestamp: new Date().toISOString()
        })
      ];
      
      await act(async () => {
        await Promise.all(promises);
      });
      
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });
}); 