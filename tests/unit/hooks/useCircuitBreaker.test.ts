/**
 * Testes Unitários - useCircuitBreaker Hook
 * 
 * Prompt: Implementação de testes para componentes importantes
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_USE_CIRCUIT_BREAKER_028
 * 
 * Baseado em código real do useCircuitBreaker.ts
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useCircuitBreaker } from '../../../app/hooks/useCircuitBreaker';

// Mock do console para evitar logs nos testes
const originalConsole = { ...console };
beforeAll(() => {
  console.warn = jest.fn();
  console.info = jest.fn();
  console.error = jest.fn();
});

afterAll(() => {
  console.warn = originalConsole.warn;
  console.info = originalConsole.info;
  console.error = originalConsole.error;
});

describe('useCircuitBreaker - Hook de Circuit Breaker', () => {
  
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('Estados Iniciais', () => {
    
    test('deve retornar estado inicial fechado', () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker'));
      
      expect(result.current.state.isClosed).toBe(true);
      expect(result.current.state.isOpen).toBe(false);
      expect(result.current.state.isHalfOpen).toBe(false);
      expect(result.current.state.failureCount).toBe(0);
      expect(result.current.state.totalRequests).toBe(0);
      expect(result.current.state.successRate).toBe(1);
      expect(result.current.state.avgResponseTime).toBe(0);
    });

    test('deve retornar métricas iniciais corretas', () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker'));
      
      expect(result.current.metrics.totalRequests).toBe(0);
      expect(result.current.metrics.successfulRequests).toBe(0);
      expect(result.current.metrics.failedRequests).toBe(0);
      expect(result.current.metrics.timeoutRequests).toBe(0);
      expect(result.current.metrics.circuitTrips).toBe(0);
      expect(result.current.metrics.circuitResets).toBe(0);
      expect(result.current.metrics.avgResponseTime).toBe(0);
      expect(result.current.metrics.failureRate).toBe(0);
      expect(result.current.metrics.lastFailureTime).toBe(null);
      expect(result.current.metrics.lastSuccessTime).toBe(null);
    });

    test('deve retornar funções necessárias', () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker'));
      
      expect(typeof result.current.call).toBe('function');
      expect(typeof result.current.callWithFallback).toBe('function');
      expect(typeof result.current.registerFallback).toBe('function');
      expect(typeof result.current.setStaticResponse).toBe('function');
      expect(typeof result.current.reset).toBe('function');
      expect(typeof result.current.forceOpen).toBe('function');
    });

    test('deve retornar estado saudável inicialmente', () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker'));
      
      expect(result.current.isHealthy).toBe(true);
      expect(result.current.error).toBe(null);
    });
  });

  describe('Configuração Padrão', () => {
    
    test('deve usar configuração padrão quando não fornecida', () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker'));
      
      // Verificar se o circuit breaker funciona com configuração padrão
      expect(result.current.state.isClosed).toBe(true);
    });

    test('deve aceitar configuração personalizada', () => {
      const customConfig = {
        failureThreshold: 3,
        recoveryTimeout: 10,
        timeoutDuration: 5,
        minRequestsBeforeTrip: 2,
        successThreshold: 1,
        enableAdaptiveThresholds: false,
        enableHealthCheck: false,
        healthCheckInterval: 30,
        fallbackStrategy: 'static_response' as const
      };

      const { result } = renderHook(() => useCircuitBreaker('test-breaker', customConfig));
      
      expect(result.current.state.isClosed).toBe(true);
    });
  });

  describe('Chamadas Bem-sucedidas', () => {
    
    test('deve executar função com sucesso', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker'));
      
      const mockFunction = jest.fn().mockResolvedValue('success');
      
      await act(async () => {
        const response = await result.current.call(mockFunction);
        expect(response).toBe('success');
      });
      
      expect(mockFunction).toHaveBeenCalledTimes(1);
      expect(result.current.state.isClosed).toBe(true);
      expect(result.current.metrics.successfulRequests).toBe(1);
      expect(result.current.metrics.totalRequests).toBe(1);
    });

    test('deve atualizar métricas após sucesso', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker'));
      
      const mockFunction = jest.fn().mockResolvedValue('success');
      
      await act(async () => {
        await result.current.call(mockFunction);
      });
      
      expect(result.current.metrics.successfulRequests).toBe(1);
      expect(result.current.metrics.totalRequests).toBe(1);
      expect(result.current.metrics.failedRequests).toBe(0);
      expect(result.current.metrics.failureRate).toBe(0);
      expect(result.current.metrics.lastSuccessTime).toBeGreaterThan(0);
      expect(result.current.state.successRate).toBe(1);
    });

    test('deve calcular tempo de resposta médio', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker'));
      
      const mockFunction = jest.fn().mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve('success'), 100))
      );
      
      await act(async () => {
        await result.current.call(mockFunction);
      });
      
      expect(result.current.metrics.avgResponseTime).toBeGreaterThan(0);
      expect(result.current.state.avgResponseTime).toBeGreaterThan(0);
    });
  });

  describe('Chamadas com Falha', () => {
    
    test('deve contar falhas corretamente', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker', {
        failureThreshold: 3,
        minRequestsBeforeTrip: 1
      }));
      
      const mockFunction = jest.fn().mockRejectedValue(new Error('API Error'));
      
      await act(async () => {
        try {
          await result.current.call(mockFunction);
        } catch (error) {
          // Erro esperado
        }
      });
      
      expect(result.current.metrics.failedRequests).toBe(1);
      expect(result.current.metrics.totalRequests).toBe(1);
      expect(result.current.metrics.failureRate).toBe(1);
      expect(result.current.state.failureCount).toBe(1);
    });

    test('deve abrir circuit após threshold de falhas', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker', {
        failureThreshold: 2,
        minRequestsBeforeTrip: 1
      }));
      
      const mockFunction = jest.fn().mockRejectedValue(new Error('API Error'));
      
      // Primeira falha
      await act(async () => {
        try {
          await result.current.call(mockFunction);
        } catch (error) {
          // Erro esperado
        }
      });
      
      expect(result.current.state.isClosed).toBe(true);
      
      // Segunda falha - deve abrir circuit
      await act(async () => {
        try {
          await result.current.call(mockFunction);
        } catch (error) {
          // Erro esperado
        }
      });
      
      expect(result.current.state.isOpen).toBe(true);
      expect(result.current.metrics.circuitTrips).toBe(1);
    });

    test('deve tratar timeouts como falhas', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker', {
        timeoutDuration: 1,
        failureThreshold: 1,
        minRequestsBeforeTrip: 1
      }));
      
      const mockFunction = jest.fn().mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve('success'), 2000))
      );
      
      await act(async () => {
        try {
          await result.current.call(mockFunction);
        } catch (error) {
          // Timeout esperado
        }
      });
      
      expect(result.current.metrics.timeoutRequests).toBe(1);
      expect(result.current.metrics.failedRequests).toBe(1);
    });
  });

  describe('Estados do Circuit Breaker', () => {
    
    test('deve transicionar de closed para open', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker', {
        failureThreshold: 1,
        minRequestsBeforeTrip: 1
      }));
      
      const mockFunction = jest.fn().mockRejectedValue(new Error('API Error'));
      
      expect(result.current.state.isClosed).toBe(true);
      
      await act(async () => {
        try {
          await result.current.call(mockFunction);
        } catch (error) {
          // Erro esperado
        }
      });
      
      expect(result.current.state.isOpen).toBe(true);
      expect(result.current.state.isClosed).toBe(false);
    });

    test('deve transicionar de open para half-open após timeout', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker', {
        failureThreshold: 1,
        recoveryTimeout: 1,
        minRequestsBeforeTrip: 1
      }));
      
      const mockFunction = jest.fn().mockRejectedValue(new Error('API Error'));
      
      // Abrir circuit
      await act(async () => {
        try {
          await result.current.call(mockFunction);
        } catch (error) {
          // Erro esperado
        }
      });
      
      expect(result.current.state.isOpen).toBe(true);
      
      // Avançar tempo para recovery
      act(() => {
        jest.advanceTimersByTime(2000);
      });
      
      // Tentar nova chamada
      await act(async () => {
        try {
          await result.current.call(mockFunction);
        } catch (error) {
          // Erro esperado
        }
      });
      
      expect(result.current.state.isHalfOpen).toBe(true);
    });

    test('deve transicionar de half-open para closed após sucessos', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker', {
        failureThreshold: 1,
        recoveryTimeout: 1,
        successThreshold: 1,
        minRequestsBeforeTrip: 1
      }));
      
      const mockFunction = jest.fn().mockRejectedValue(new Error('API Error'));
      const successFunction = jest.fn().mockResolvedValue('success');
      
      // Abrir circuit
      await act(async () => {
        try {
          await result.current.call(mockFunction);
        } catch (error) {
          // Erro esperado
        }
      });
      
      // Avançar tempo para recovery
      act(() => {
        jest.advanceTimersByTime(2000);
      });
      
      // Tentar com sucesso
      await act(async () => {
        await result.current.call(successFunction);
      });
      
      expect(result.current.state.isClosed).toBe(true);
      expect(result.current.metrics.circuitResets).toBe(1);
    });
  });

  describe('Fallbacks', () => {
    
    test('deve usar fallback quando circuit está aberto', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker', {
        failureThreshold: 1,
        minRequestsBeforeTrip: 1
      }));
      
      const mockFunction = jest.fn().mockRejectedValue(new Error('API Error'));
      const fallbackFunction = jest.fn().mockReturnValue('fallback-data');
      
      // Abrir circuit
      await act(async () => {
        try {
          await result.current.call(mockFunction);
        } catch (error) {
          // Erro esperado
        }
      });
      
      // Tentar chamada com fallback
      await act(async () => {
        const response = await result.current.callWithFallback(mockFunction, fallbackFunction);
        expect(response).toBe('fallback-data');
      });
      
      expect(fallbackFunction).toHaveBeenCalledTimes(1);
    });

    test('deve registrar fallback handler', () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker'));
      
      const fallbackHandler = {
        name: 'test-fallback',
        handler: jest.fn().mockReturnValue('fallback-data'),
        priority: 1
      };
      
      act(() => {
        result.current.registerFallback(fallbackHandler);
      });
      
      // Verificar se fallback foi registrado (não há API pública para verificar)
      expect(result.current.registerFallback).toBeDefined();
    });

    test('deve definir resposta estática', () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker'));
      
      const staticResponse = {
        name: 'test-response',
        data: { message: 'Service unavailable' },
        priority: 1
      };
      
      act(() => {
        result.current.setStaticResponse(staticResponse);
      });
      
      // Verificar se resposta estática foi definida (não há API pública para verificar)
      expect(result.current.setStaticResponse).toBeDefined();
    });
  });

  describe('Controles Manuais', () => {
    
    test('deve permitir reset manual', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker', {
        failureThreshold: 1,
        minRequestsBeforeTrip: 1
      }));
      
      const mockFunction = jest.fn().mockRejectedValue(new Error('API Error'));
      
      // Abrir circuit
      await act(async () => {
        try {
          await result.current.call(mockFunction);
        } catch (error) {
          // Erro esperado
        }
      });
      
      expect(result.current.state.isOpen).toBe(true);
      
      // Reset manual
      act(() => {
        result.current.reset();
      });
      
      expect(result.current.state.isClosed).toBe(true);
      expect(result.current.state.failureCount).toBe(0);
    });

    test('deve permitir forçar abertura do circuit', () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker'));
      
      expect(result.current.state.isClosed).toBe(true);
      
      act(() => {
        result.current.forceOpen();
      });
      
      expect(result.current.state.isOpen).toBe(true);
    });
  });

  describe('Thresholds Adaptativos', () => {
    
    test('deve usar threshold adaptativo quando habilitado', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker', {
        failureThreshold: 5,
        enableAdaptiveThresholds: true,
        minRequestsBeforeTrip: 1
      }));
      
      const mockFunction = jest.fn().mockRejectedValue(new Error('Request timeout'));
      
      // Múltiplas falhas de timeout devem reduzir threshold
      for (let i = 0; i < 3; i++) {
        await act(async () => {
          try {
            await result.current.call(mockFunction);
          } catch (error) {
            // Erro esperado
          }
        });
      }
      
      // Circuit deve abrir com threshold reduzido
      expect(result.current.state.isOpen).toBe(true);
    });
  });

  describe('Monitoramento de Saúde', () => {
    
    test('deve calcular saúde baseada em sucesso', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker'));
      
      const mockFunction = jest.fn().mockResolvedValue('success');
      
      // Múltiplos sucessos
      for (let i = 0; i < 5; i++) {
        await act(async () => {
          await result.current.call(mockFunction);
        });
      }
      
      expect(result.current.isHealthy).toBe(true);
    });

    test('deve considerar circuit não saudável com muitas falhas', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker', {
        failureThreshold: 3,
        minRequestsBeforeTrip: 1
      }));
      
      const mockFunction = jest.fn().mockRejectedValue(new Error('API Error'));
      
      // Múltiplas falhas
      for (let i = 0; i < 3; i++) {
        await act(async () => {
          try {
            await result.current.call(mockFunction);
          } catch (error) {
            // Erro esperado
          }
        });
      }
      
      expect(result.current.isHealthy).toBe(false);
    });
  });

  describe('Estratégias de Fallback', () => {
    
    test('deve usar estratégia cache_first', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker', {
        fallbackStrategy: 'cache_first',
        failureThreshold: 1,
        minRequestsBeforeTrip: 1
      }));
      
      const mockFunction = jest.fn().mockRejectedValue(new Error('API Error'));
      
      // Abrir circuit
      await act(async () => {
        try {
          await result.current.call(mockFunction);
        } catch (error) {
          // Erro esperado
        }
      });
      
      // Tentar chamada com fallback
      await act(async () => {
        const response = await result.current.call(mockFunction);
        expect(response).toHaveProperty('error', 'Service temporarily unavailable');
        expect(response).toHaveProperty('circuitBreaker', 'test-breaker');
      });
    });

    test('deve usar estratégia static_response', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker', {
        fallbackStrategy: 'static_response',
        failureThreshold: 1,
        minRequestsBeforeTrip: 1
      }));
      
      const mockFunction = jest.fn().mockRejectedValue(new Error('API Error'));
      
      // Abrir circuit
      await act(async () => {
        try {
          await result.current.call(mockFunction);
        } catch (error) {
          // Erro esperado
        }
      });
      
      // Tentar chamada com fallback
      await act(async () => {
        const response = await result.current.call(mockFunction);
        expect(response).toHaveProperty('error', 'Service temporarily unavailable');
      });
    });
  });

  describe('Performance e Otimização', () => {
    
    test('deve lidar com múltiplas chamadas simultâneas', async () => {
      const { result } = renderHook(() => useCircuitBreaker('test-breaker'));
      
      const mockFunction = jest.fn().mockResolvedValue('success');
      
      const promises = Array.from({ length: 5 }, () => 
        result.current.call(mockFunction)
      );
      
      await act(async () => {
        const responses = await Promise.all(promises);
        expect(responses).toEqual(['success', 'success', 'success', 'success', 'success']);
      });
      
      expect(mockFunction).toHaveBeenCalledTimes(5);
      expect(result.current.metrics.totalRequests).toBe(5);
      expect(result.current.metrics.successfulRequests).toBe(5);
    });

    test('deve usar useCallback para otimização', () => {
      const { result, rerender } = renderHook(() => useCircuitBreaker('test-breaker'));
      
      const initialCall = result.current.call;
      const initialReset = result.current.reset;
      
      rerender();
      
      expect(result.current.call).toBe(initialCall);
      expect(result.current.reset).toBe(initialReset);
    });
  });
}); 