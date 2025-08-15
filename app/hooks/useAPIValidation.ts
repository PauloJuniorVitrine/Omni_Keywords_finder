/**
 * Hook para validação em tempo real de chaves de API
 * 
 * Prompt: Implementação do hook useAPIValidation
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 * 
 * @author Paulo Júnior
 * @description Hook para validação de chaves de API com debouncing e feedback em tempo real
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// Tipos de provedores de IA
export type AIProvider = 'deepseek' | 'openai' | 'claude' | 'gemini';

// Tipos de provedores de redes sociais
export type SocialProvider = 'instagram' | 'tiktok' | 'youtube' | 'pinterest' | 'reddit';

// Tipos de provedores de analytics
export type AnalyticsProvider = 'google_analytics' | 'semrush' | 'ahrefs' | 'google_search_console';

// Tipo unificado de provedor
export type Provider = AIProvider | SocialProvider | AnalyticsProvider;

// Status da validação
export type ValidationStatus = 'idle' | 'validating' | 'valid' | 'invalid' | 'error';

// Resultado da validação
export interface ValidationResult {
  isValid: boolean;
  message: string;
  details?: {
    rateLimit?: number;
    quota?: number;
    expiresAt?: string;
    permissions?: string[];
  };
}

// Configuração do hook
export interface UseAPIValidationConfig {
  debounceMs?: number;
  enableRealTime?: boolean;
  maxRetries?: number;
  retryDelay?: number;
  timeout?: number;
}

// Estado interno do hook
interface ValidationState {
  status: ValidationStatus;
  result: ValidationResult | null;
  error: string | null;
  lastValidated: Date | null;
  retryCount: number;
}

// Hook principal
export const useAPIValidation = (
  apiKey: string,
  provider: Provider,
  config: UseAPIValidationConfig = {}
) => {
  const {
    debounceMs = 500,
    enableRealTime = true,
    maxRetries = 3,
    retryDelay = 1000,
    timeout = 10000
  } = config;

  // Estado interno
  const [state, setState] = useState<ValidationState>({
    status: 'idle',
    result: null,
    error: null,
    lastValidated: null,
    retryCount: 0
  });

  // Refs para controle
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Função para validar chave de API
  const validateAPIKey = useCallback(async (
    key: string,
    provider: Provider,
    signal?: AbortSignal
  ): Promise<ValidationResult> => {
    try {
      const response = await fetch('/api/credentials/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}`
        },
        body: JSON.stringify({
          apiKey: key,
          provider: provider,
          validateType: 'api_key'
        }),
        signal
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      return {
        isValid: data.isValid,
        message: data.message,
        details: data.details
      };
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Validação cancelada');
      }
      
      throw new Error(`Erro na validação: ${error instanceof Error ? error.message : 'Erro desconhecido'}`);
    }
  }, []);

  // Função para validar com retry
  const validateWithRetry = useCallback(async (
    key: string,
    provider: Provider,
    retryCount = 0
  ) => {
    // Cancelar validação anterior se existir
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Criar novo controller
    abortControllerRef.current = new AbortController();

    setState(prev => ({
      ...prev,
      status: 'validating',
      error: null
    }));

    try {
      const result = await validateAPIKey(key, provider, abortControllerRef.current.signal);
      
      setState(prev => ({
        ...prev,
        status: result.isValid ? 'valid' : 'invalid',
        result,
        lastValidated: new Date(),
        retryCount: 0
      }));

      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      
      // Se ainda há tentativas e não foi cancelado
      if (retryCount < maxRetries && errorMessage !== 'Validação cancelada') {
        setState(prev => ({
          ...prev,
          retryCount: retryCount + 1
        }));

        // Aguardar antes de tentar novamente
        await new Promise(resolve => setTimeout(resolve, retryDelay));

        // Tentar novamente
        return validateWithRetry(key, provider, retryCount + 1);
      }

      // Falha definitiva
      setState(prev => ({
        ...prev,
        status: 'error',
        error: errorMessage,
        retryCount: 0
      }));

      throw error;
    }
  }, [validateAPIKey, maxRetries, retryDelay]);

  // Função para validar manualmente
  const validate = useCallback(async () => {
    if (!apiKey.trim()) {
      setState(prev => ({
        ...prev,
        status: 'idle',
        result: null,
        error: null
      }));
      return;
    }

    try {
      await validateWithRetry(apiKey, provider);
    } catch (error) {
      // Erro já tratado no validateWithRetry
    }
  }, [apiKey, provider, validateWithRetry]);

  // Função para resetar estado
  const reset = useCallback(() => {
    setState({
      status: 'idle',
      result: null,
      error: null,
      lastValidated: null,
      retryCount: 0
    });
  }, []);

  // Função para cancelar validação em andamento
  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
      debounceRef.current = null;
    }

    setState(prev => ({
      ...prev,
      status: 'idle'
    }));
  }, []);

  // Efeito para validação automática em tempo real
  useEffect(() => {
    if (!enableRealTime || !apiKey.trim()) {
      return;
    }

    // Cancelar validação anterior
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    // Agendar nova validação com debounce
    debounceRef.current = setTimeout(() => {
      validate();
    }, debounceMs);

    // Cleanup
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [apiKey, provider, enableRealTime, debounceMs, validate]);

  // Cleanup no unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  // Função para validar múltiplas chaves
  const validateMultiple = useCallback(async (
    keys: Array<{ key: string; provider: Provider }>
  ) => {
    const results = await Promise.allSettled(
      keys.map(({ key, provider }) => validateAPIKey(key, provider))
    );

    return results.map((result, index) => ({
      key: keys[index].key,
      provider: keys[index].provider,
      success: result.status === 'fulfilled',
      result: result.status === 'fulfilled' ? result.value : null,
      error: result.status === 'rejected' ? result.reason : null
    }));
  }, [validateAPIKey]);

  return {
    // Estado
    status: state.status,
    result: state.result,
    error: state.error,
    lastValidated: state.lastValidated,
    retryCount: state.retryCount,
    
    // Ações
    validate,
    validateMultiple,
    reset,
    cancel,
    
    // Utilitários
    isValid: state.status === 'valid',
    isInvalid: state.status === 'invalid',
    isValidating: state.status === 'validating',
    hasError: state.status === 'error',
    isIdle: state.status === 'idle'
  };
};

// Hook para validação de múltiplas chaves
export const useMultiAPIValidation = (
  keys: Array<{ key: string; provider: Provider }>,
  config: UseAPIValidationConfig = {}
) => {
  const [results, setResults] = useState<Array<{
    key: string;
    provider: Provider;
    success: boolean;
    result: ValidationResult | null;
    error: string | null;
  }>>([]);

  const [isValidating, setIsValidating] = useState(false);

  const validateAll = useCallback(async () => {
    setIsValidating(true);
    
    try {
      const validationResults = await Promise.allSettled(
        keys.map(async ({ key, provider }) => {
          const response = await fetch('/api/credentials/validate', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('authToken') || ''}`
            },
            body: JSON.stringify({
              apiKey: key,
              provider: provider,
              validateType: 'api_key'
            })
          });

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }

          return await response.json();
        })
      );

      const processedResults = validationResults.map((result, index) => ({
        key: keys[index].key,
        provider: keys[index].provider,
        success: result.status === 'fulfilled',
        result: result.status === 'fulfilled' ? result.value : null,
        error: result.status === 'rejected' ? result.reason : null
      }));

      setResults(processedResults);
    } catch (error) {
      console.error('Erro na validação múltipla:', error);
    } finally {
      setIsValidating(false);
    }
  }, [keys]);

  const reset = useCallback(() => {
    setResults([]);
  }, []);

  return {
    results,
    isValidating,
    validateAll,
    reset,
    
    // Utilitários
    validCount: results.filter(r => r.success && r.result?.isValid).length,
    invalidCount: results.filter(r => r.success && !r.result?.isValid).length,
    errorCount: results.filter(r => !r.success).length,
    totalCount: results.length
  };
};

export default useAPIValidation; 