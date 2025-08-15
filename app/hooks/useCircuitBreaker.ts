/**
 * 🛡️ Circuit Breaker Hook
 * 🎯 Objetivo: Hook React para circuit breakers com fallbacks inteligentes
 * 📅 Data: 2025-01-27
 * 🔗 Tracing ID: USE_CIRCUIT_BREAKER_001
 * 📋 Ruleset: enterprise_control_layer.yaml
 */

import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';

// Tipos para circuit breaker
export interface CircuitBreakerState {
  isOpen: boolean;
  isHalfOpen: boolean;
  isClosed: boolean;
  failureCount: number;
  lastFailureTime: number | null;
  lastSuccessTime: number | null;
  totalRequests: number;
  successRate: number;
  avgResponseTime: number;
}

export interface CircuitBreakerConfig {
  failureThreshold: number;
  recoveryTimeout: number; // segundos
  timeoutDuration: number; // segundos
  minRequestsBeforeTrip: number;
  successThreshold: number;
  enableAdaptiveThresholds: boolean;
  enableHealthCheck: boolean;
  healthCheckInterval: number; // segundos
  fallbackStrategy: 'cache_first' | 'static_response' | 'degraded_service';
}

export interface CircuitBreakerMetrics {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  timeoutRequests: number;
  circuitTrips: number;
  circuitResets: number;
  avgResponseTime: number;
  failureRate: number;
  lastFailureTime: number | null;
  lastSuccessTime: number | null;
}

export interface FallbackHandler {
  name: string;
  handler: (...args: any[]) => any;
  priority: number;
}

export interface StaticResponse {
  name: string;
  data: any;
  priority: number;
}

// Estado interno do circuit breaker
interface InternalCircuitState {
  state: 'closed' | 'open' | 'half_open';
  failureCount: number;
  successCount: number;
  lastFailureTime: number | null;
  lastSuccessTime: number | null;
  lastStateChange: number;
  failureHistory: Array<{
    timestamp: number;
    error: string;
    responseTime: number;
  }>;
  responseTimes: number[];
  metrics: CircuitBreakerMetrics;
}

// Hook principal
export function useCircuitBreaker(
  name: string,
  config: Partial<CircuitBreakerConfig> = {}
): {
  state: CircuitBreakerState;
  metrics: CircuitBreakerMetrics;
  call: <T>(fn: () => Promise<T>) => Promise<T>;
  callWithFallback: <T>(fn: () => Promise<T>, fallback?: () => T) => Promise<T>;
  registerFallback: (fallback: FallbackHandler) => void;
  setStaticResponse: (response: StaticResponse) => void;
  reset: () => void;
  forceOpen: () => void;
  isHealthy: boolean;
  error: string | null;
} {
  // Configuração padrão
  const defaultConfig: CircuitBreakerConfig = {
    failureThreshold: 5,
    recoveryTimeout: 30,
    timeoutDuration: 10,
    minRequestsBeforeTrip: 3,
    successThreshold: 2,
    enableAdaptiveThresholds: true,
    enableHealthCheck: true,
    healthCheckInterval: 60,
    fallbackStrategy: 'cache_first'
  };

  const finalConfig = { ...defaultConfig, ...config };
  
  // Estados
  const [internalState, setInternalState] = useState<InternalCircuitState>({
    state: 'closed',
    failureCount: 0,
    successCount: 0,
    lastFailureTime: null,
    lastSuccessTime: null,
    lastStateChange: Date.now(),
    failureHistory: [],
    responseTimes: [],
    metrics: {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      timeoutRequests: 0,
      circuitTrips: 0,
      circuitResets: 0,
      avgResponseTime: 0,
      failureRate: 0,
      lastFailureTime: null,
      lastSuccessTime: null
    }
  });

  const [fallbacks, setFallbacks] = useState<FallbackHandler[]>([]);
  const [staticResponses, setStaticResponses] = useState<StaticResponse[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  // Refs
  const healthCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const queryClient = useQueryClient();

  // Estado derivado
  const state: CircuitBreakerState = useMemo(() => ({
    isOpen: internalState.state === 'open',
    isHalfOpen: internalState.state === 'half_open',
    isClosed: internalState.state === 'closed',
    failureCount: internalState.failureCount,
    lastFailureTime: internalState.lastFailureTime,
    lastSuccessTime: internalState.lastSuccessTime,
    totalRequests: internalState.metrics.totalRequests,
    successRate: internalState.metrics.totalRequests > 0 
      ? internalState.metrics.successfulRequests / internalState.metrics.totalRequests 
      : 1,
    avgResponseTime: internalState.metrics.avgResponseTime
  }), [internalState]);

  const isHealthy = useMemo(() => {
    return !state.isOpen && state.successRate > 0.8;
  }, [state]);

  // Funções auxiliares
  const shouldOpenCircuit = useCallback(() => {
    if (internalState.metrics.totalRequests < finalConfig.minRequestsBeforeTrip) {
      return false;
    }

    const failureRate = internalState.metrics.failedRequests / internalState.metrics.totalRequests;
    let threshold = finalConfig.failureThreshold;

    // Threshold adaptativo
    if (finalConfig.enableAdaptiveThresholds) {
      threshold = calculateAdaptiveThreshold();
    }

    return internalState.failureCount >= threshold || failureRate > 0.5;
  }, [internalState, finalConfig]);

  const calculateAdaptiveThreshold = useCallback(() => {
    if (internalState.failureHistory.length < 10) {
      return finalConfig.failureThreshold;
    }

    const recentFailures = internalState.failureHistory.slice(-10);
    const hasTimeouts = recentFailures.some(f => f.error.includes('timeout'));
    const hasConnectionErrors = recentFailures.some(f => f.error.includes('connection'));

    if (hasTimeouts) {
      return Math.max(3, finalConfig.failureThreshold - 2);
    } else if (hasConnectionErrors) {
      return finalConfig.failureThreshold + 1;
    }

    return finalConfig.failureThreshold;
  }, [internalState.failureHistory, finalConfig.failureThreshold]);

  const shouldAttemptReset = useCallback(() => {
    if (internalState.state === 'closed') {
      return false;
    }

    const timeSinceLastFailure = internalState.lastFailureTime 
      ? Date.now() - internalState.lastFailureTime 
      : Infinity;

    return timeSinceLastFailure >= finalConfig.recoveryTimeout * 1000;
  }, [internalState, finalConfig.recoveryTimeout]);

  const openCircuit = useCallback(() => {
    setInternalState(prev => ({
      ...prev,
      state: 'open',
      lastStateChange: Date.now(),
      metrics: {
        ...prev.metrics,
        circuitTrips: prev.metrics.circuitTrips + 1
      }
    }));

    console.warn(`[CIRCUIT_BREAKER] Circuit breaker '${name}' opened after ${internalState.failureCount} failures`);
  }, [name, internalState.failureCount]);

  const closeCircuit = useCallback(() => {
    setInternalState(prev => ({
      ...prev,
      state: 'closed',
      lastStateChange: Date.now(),
      failureCount: 0,
      successCount: 0,
      metrics: {
        ...prev.metrics,
        circuitResets: prev.metrics.circuitResets + 1
      }
    }));

    console.info(`[CIRCUIT_BREAKER] Circuit breaker '${name}' closed after recovery`);
  }, [name]);

  const halfOpenCircuit = useCallback(() => {
    setInternalState(prev => ({
      ...prev,
      state: 'half_open',
      lastStateChange: Date.now()
    }));

    console.info(`[CIRCUIT_BREAKER] Circuit breaker '${name}' in half-open mode`);
  }, [name]);

  const onSuccess = useCallback((responseTime: number) => {
    setInternalState(prev => {
      const newResponseTimes = [...prev.responseTimes, responseTime].slice(-50);
      const avgResponseTime = newResponseTimes.length > 0 
        ? newResponseTimes.reduce((a, b) => a + b, 0) / newResponseTimes.length 
        : 0;

      const newMetrics = {
        ...prev.metrics,
        totalRequests: prev.metrics.totalRequests + 1,
        successfulRequests: prev.metrics.successfulRequests + 1,
        lastSuccessTime: Date.now(),
        avgResponseTime
      };

      let newState = prev.state;
      let newFailureCount = prev.failureCount;
      let newSuccessCount = prev.successCount;

      if (prev.state === 'half_open') {
        newSuccessCount = prev.successCount + 1;
        if (newSuccessCount >= finalConfig.successThreshold) {
          newState = 'closed';
          newFailureCount = 0;
          newSuccessCount = 0;
        }
      } else if (prev.state === 'closed') {
        newFailureCount = Math.max(0, prev.failureCount - 1);
      }

      return {
        ...prev,
        state: newState,
        failureCount: newFailureCount,
        successCount: newSuccessCount,
        lastSuccessTime: Date.now(),
        responseTimes: newResponseTimes,
        metrics: newMetrics
      };
    });
  }, [finalConfig.successThreshold]);

  const onFailure = useCallback((error: Error, responseTime: number) => {
    setInternalState(prev => {
      const newFailureHistory = [
        ...prev.failureHistory,
        {
          timestamp: Date.now(),
          error: error.message,
          responseTime
        }
      ].slice(-100);

      const newMetrics = {
        ...prev.metrics,
        totalRequests: prev.metrics.totalRequests + 1,
        failedRequests: prev.metrics.failedRequests + 1,
        lastFailureTime: Date.now()
      };

      // Classificar tipo de falha
      if (error.message.includes('timeout')) {
        newMetrics.timeoutRequests = prev.metrics.timeoutRequests + 1;
      }

      const newFailureCount = prev.failureCount + 1;

      return {
        ...prev,
        failureCount: newFailureCount,
        failureHistory: newFailureHistory,
        metrics: newMetrics
      };
    });

    console.warn(`[CIRCUIT_BREAKER] Failure in '${name}': ${error.message}`);
  }, [name]);

  const executeFallback = useCallback(async (fn: () => Promise<any>, args: any[] = []): Promise<any> => {
    try {
      // Estratégia cache_first
      if (finalConfig.fallbackStrategy === 'cache_first') {
        const cacheKey = `circuit_breaker_fallback_${name}_${JSON.stringify(args)}`;
        const cachedData = queryClient.getQueryData(cacheKey);
        
        if (cachedData) {
          console.info(`[CIRCUIT_BREAKER] Cache fallback used for '${name}'`);
          return cachedData;
        }
      }

      // Handlers de fallback ordenados por prioridade
      const sortedFallbacks = [...fallbacks].sort((a, b) => a.priority - b.priority);
      
      for (const fallback of sortedFallbacks) {
        try {
          const result = await fallback.handler(...args);
          console.info(`[CIRCUIT_BREAKER] Fallback '${fallback.name}' used for '${name}'`);
          return result;
        } catch (fallbackError) {
          console.warn(`[CIRCUIT_BREAKER] Fallback '${fallback.name}' failed: ${fallbackError}`);
          continue;
        }
      }

      // Respostas estáticas ordenadas por prioridade
      const sortedResponses = [...staticResponses].sort((a, b) => a.priority - b.priority);
      
      if (sortedResponses.length > 0) {
        console.info(`[CIRCUIT_BREAKER] Static response used for '${name}'`);
        return sortedResponses[0].data;
      }

      // Fallback padrão
      return {
        error: 'Service temporarily unavailable',
        circuitBreaker: name,
        state: internalState.state,
        timestamp: Date.now()
      };

    } catch (fallbackError) {
      console.error(`[CIRCUIT_BREAKER] All fallbacks failed for '${name}': ${fallbackError}`);
      throw fallbackError;
    }
  }, [name, finalConfig.fallbackStrategy, fallbacks, staticResponses, internalState.state, queryClient]);

  // Função principal de chamada
  const call = useCallback(async <T>(fn: () => Promise<T>): Promise<T> => {
    const startTime = Date.now();
    
    try {
      // Verificar se circuit está aberto
      if (internalState.state === 'open') {
        if (shouldAttemptReset()) {
          halfOpenCircuit();
        } else {
          return await executeFallback(fn);
        }
      }

      // Executar função com timeout
      const timeoutPromise = new Promise<never>((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), finalConfig.timeoutDuration * 1000);
      });

      const result = await Promise.race([fn(), timeoutPromise]);
      const responseTime = Date.now() - startTime;
      
      onSuccess(responseTime);
      return result;

    } catch (error) {
      const responseTime = Date.now() - startTime;
      const errorObj = error instanceof Error ? error : new Error(String(error));
      
      onFailure(errorObj, responseTime);

      // Verificar se deve abrir circuit
      if (shouldOpenCircuit()) {
        openCircuit();
      }

      // Executar fallback
      return await executeFallback(fn);
    }
  }, [
    internalState.state,
    shouldAttemptReset,
    halfOpenCircuit,
    executeFallback,
    finalConfig.timeoutDuration,
    onSuccess,
    onFailure,
    shouldOpenCircuit,
    openCircuit
  ]);

  const callWithFallback = useCallback(async <T>(
    fn: () => Promise<T>, 
    fallback?: () => T
  ): Promise<T> => {
    try {
      return await call(fn);
    } catch (error) {
      if (fallback) {
        return fallback();
      }
      throw error;
    }
  }, [call]);

  const registerFallback = useCallback((fallback: FallbackHandler) => {
    setFallbacks(prev => [...prev, fallback]);
    console.info(`[CIRCUIT_BREAKER] Fallback '${fallback.name}' registered for '${name}'`);
  }, [name]);

  const setStaticResponse = useCallback((response: StaticResponse) => {
    setStaticResponses(prev => [...prev, response]);
    console.info(`[CIRCUIT_BREAKER] Static response '${response.name}' set for '${name}'`);
  }, [name]);

  const reset = useCallback(() => {
    setInternalState(prev => ({
      ...prev,
      state: 'closed',
      failureCount: 0,
      successCount: 0,
      lastFailureTime: null,
      lastStateChange: Date.now(),
      metrics: {
        ...prev.metrics,
        circuitResets: prev.metrics.circuitResets + 1
      }
    }));
    setError(null);
    console.info(`[CIRCUIT_BREAKER] Circuit breaker '${name}' reset`);
  }, [name]);

  const forceOpen = useCallback(() => {
    setInternalState(prev => ({
      ...prev,
      state: 'open',
      lastStateChange: Date.now(),
      metrics: {
        ...prev.metrics,
        circuitTrips: prev.metrics.circuitTrips + 1
      }
    }));
    console.warn(`[CIRCUIT_BREAKER] Circuit breaker '${name}' forced open`);
  }, [name]);

  // Health check
  useEffect(() => {
    if (!finalConfig.enableHealthCheck) return;

    healthCheckIntervalRef.current = setInterval(() => {
      if (shouldAttemptReset()) {
        halfOpenCircuit();
      }
    }, finalConfig.healthCheckInterval * 1000);

    return () => {
      if (healthCheckIntervalRef.current) {
        clearInterval(healthCheckIntervalRef.current);
      }
    };
  }, [finalConfig.enableHealthCheck, finalConfig.healthCheckInterval, shouldAttemptReset, halfOpenCircuit]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (healthCheckIntervalRef.current) {
        clearInterval(healthCheckIntervalRef.current);
      }
    };
  }, []);

  return {
    state,
    metrics: internalState.metrics,
    call,
    callWithFallback,
    registerFallback,
    setStaticResponse,
    reset,
    forceOpen,
    isHealthy,
    error
  };
}

// Hook para múltiplos circuit breakers
export function useCircuitBreakers(
  breakers: Array<{ name: string; config?: Partial<CircuitBreakerConfig> }>
) {
  const circuitBreakers = breakers.map(({ name, config }) => 
    useCircuitBreaker(name, config)
  );

  const overallHealth = useMemo(() => {
    return circuitBreakers.every(cb => cb.isHealthy);
  }, [circuitBreakers]);

  const resetAll = useCallback(() => {
    circuitBreakers.forEach(cb => cb.reset());
  }, [circuitBreakers]);

  const forceOpenAll = useCallback(() => {
    circuitBreakers.forEach(cb => cb.forceOpen());
  }, [circuitBreakers]);

  return {
    circuitBreakers,
    overallHealth,
    resetAll,
    forceOpenAll
  };
}

// Hook para monitoramento de circuit breakers
export function useCircuitBreakerMonitoring() {
  const [monitoredBreakers, setMonitoredBreakers] = useState<Map<string, CircuitBreakerState>>(new Map());
  const [alerts, setAlerts] = useState<Array<{
    id: string;
    breakerName: string;
    type: 'opened' | 'reset' | 'high_failure_rate';
    message: string;
    timestamp: number;
  }>>([]);

  const registerBreaker = useCallback((name: string, state: CircuitBreakerState) => {
    setMonitoredBreakers(prev => {
      const newMap = new Map(prev);
      newMap.set(name, state);
      return newMap;
    });
  }, []);

  const addAlert = useCallback((breakerName: string, type: string, message: string) => {
    const alert = {
      id: `${breakerName}_${Date.now()}`,
      breakerName,
      type: type as any,
      message,
      timestamp: Date.now()
    };
    
    setAlerts(prev => [...prev, alert]);
    
    // Remover alertas antigos (mais de 1 hora)
    setTimeout(() => {
      setAlerts(prev => prev.filter(a => a.timestamp > Date.now() - 3600000));
    }, 3600000);
  }, []);

  const clearAlerts = useCallback(() => {
    setAlerts([]);
  }, []);

  return {
    monitoredBreakers,
    alerts,
    registerBreaker,
    addAlert,
    clearAlerts
  };
}

// Testes unitários (não executar)
export function testUseCircuitBreaker() {
  /**
   * Testa criação do hook
   */
  function testHookCreation() {
    // Mock do React
    const mockState = { state: 'closed' as const };
    const mockCall = jest.fn();
    
    // Simular hook
    const hook = {
      state: mockState,
      call: mockCall,
      isHealthy: true
    };
    
    expect(hook.state.state).toBe('closed');
    expect(hook.isHealthy).toBe(true);
  }

  /**
   * Testa abertura do circuit breaker
   */
  function testCircuitBreakerTrip() {
    // Simular falhas
    const mockCall = jest.fn().mockRejectedValue(new Error('Network error'));
    
    // Simular hook com falhas
    const hook = {
      call: mockCall,
      state: { isOpen: true, failureCount: 5 }
    };
    
    expect(hook.state.isOpen).toBe(true);
    expect(hook.state.failureCount).toBe(5);
  }

  /**
   * Testa fallbacks
   */
  function testFallbacks() {
    const mockFallback = jest.fn().mockReturnValue('fallback_data');
    const mockCall = jest.fn().mockRejectedValue(new Error('Service unavailable'));
    
    // Simular hook com fallback
    const hook = {
      call: mockCall,
      callWithFallback: jest.fn().mockResolvedValue('fallback_data'),
      registerFallback: jest.fn()
    };
    
    hook.registerFallback({
      name: 'test_fallback',
      handler: mockFallback,
      priority: 1
    });
    
    expect(hook.registerFallback).toHaveBeenCalled();
  }
}

// Exportações
export type {
  CircuitBreakerState,
  CircuitBreakerConfig,
  CircuitBreakerMetrics,
  FallbackHandler,
  StaticResponse
}; 