/**
 * Hook useLocalStorage - Gerenciamento de Estado Persistente
 * 
 * Prompt: Implementação de testes para hooks críticos
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: HOOK_USE_LOCAL_STORAGE_016
 * 
 * Hook para gerenciamento seguro e persistente de dados no localStorage
 */

import { useState, useEffect, useCallback, useRef } from 'react';

export interface LocalStorageConfig {
  key: string;
  defaultValue?: any;
  serializer?: (value: any) => string;
  deserializer?: (value: string) => any;
  validator?: (value: any) => boolean;
  expiration?: number; // Tempo em ms
  encryption?: boolean;
  compression?: boolean;
  syncAcrossTabs?: boolean;
}

export interface LocalStorageState<T> {
  value: T;
  loading: boolean;
  error: Error | null;
  lastUpdated: number | null;
  isExpired: boolean;
}

export interface LocalStorageActions<T> {
  setValue: (value: T | ((prev: T) => T)) => void;
  removeValue: () => void;
  clearAll: () => void;
  refresh: () => void;
  getSize: () => number;
  isAvailable: () => boolean;
}

export type UseLocalStorageReturn<T> = [T, LocalStorageActions<T>, LocalStorageState<T>];

// Serializadores padrão
const defaultSerializer = (value: any): string => {
  try {
    return JSON.stringify(value);
  } catch (error) {
    console.warn('Failed to serialize value:', error);
    return '';
  }
};

const defaultDeserializer = (value: string): any => {
  try {
    return JSON.parse(value);
  } catch (error) {
    console.warn('Failed to deserialize value:', error);
    return null;
  }
};

// Validador padrão
const defaultValidator = (value: any): boolean => {
  return value !== null && value !== undefined;
};

// Verificar disponibilidade do localStorage
const isLocalStorageAvailable = (): boolean => {
  try {
    const test = '__localStorage_test__';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch {
    return false;
  }
};

// Criptografia simples (base64 para demonstração)
const encrypt = (value: string): string => {
  if (typeof window === 'undefined') return value;
  return btoa(encodeURIComponent(value));
};

const decrypt = (value: string): string => {
  if (typeof window === 'undefined') return value;
  try {
    return decodeURIComponent(atob(value));
  } catch {
    return value;
  }
};

// Compressão simples (para demonstração)
const compress = (value: string): string => {
  // Implementação básica de compressão
  return value.length > 100 ? value.replace(/\s+/g, ' ') : value;
};

const decompress = (value: string): string => {
  return value;
};

export function useLocalStorage<T>(
  key: string,
  defaultValue?: T,
  config?: Partial<LocalStorageConfig>
): UseLocalStorageReturn<T> {
  const {
    serializer = defaultSerializer,
    deserializer = defaultDeserializer,
    validator = defaultValidator,
    expiration,
    encryption = false,
    compression = false,
    syncAcrossTabs = false,
  } = config || {};

  const [state, setState] = useState<LocalStorageState<T>>({
    value: defaultValue as T,
    loading: true,
    error: null,
    lastUpdated: null,
    isExpired: false,
  });

  const isInitialized = useRef(false);
  const storageKey = useRef(`omni_${key}`);

  // Carregar valor do localStorage
  const loadValue = useCallback((): T | null => {
    if (!isLocalStorageAvailable()) {
      return null;
    }

    try {
      const stored = localStorage.getItem(storageKey.current);
      if (!stored) return null;

      let processedValue = stored;

      // Descriptografar se necessário
      if (encryption) {
        processedValue = decrypt(processedValue);
      }

      // Descomprimir se necessário
      if (compression) {
        processedValue = decompress(processedValue);
      }

      const parsed = deserializer(processedValue);

      // Verificar expiração
      if (expiration && parsed?.timestamp) {
        const isExpired = Date.now() - parsed.timestamp > expiration;
        if (isExpired) {
          localStorage.removeItem(storageKey.current);
          return null;
        }
      }

      // Validar valor
      if (!validator(parsed?.data ?? parsed)) {
        console.warn(`Invalid value for key ${key}`);
        return null;
      }

      return parsed?.data ?? parsed;
    } catch (error) {
      console.error(`Error loading from localStorage for key ${key}:`, error);
      return null;
    }
  }, [key, deserializer, validator, expiration, encryption, compression]);

  // Salvar valor no localStorage
  const saveValue = useCallback((value: T): void => {
    if (!isLocalStorageAvailable()) {
      return;
    }

    try {
      const dataToStore = {
        data: value,
        timestamp: Date.now(),
        version: '1.0',
      };

      let serialized = serializer(dataToStore);

      // Comprimir se necessário
      if (compression) {
        serialized = compress(serialized);
      }

      // Criptografar se necessário
      if (encryption) {
        serialized = encrypt(serialized);
      }

      localStorage.setItem(storageKey.current, serialized);

      // Disparar evento para sincronização entre abas
      if (syncAcrossTabs) {
        window.dispatchEvent(
          new StorageEvent('storage', {
            key: storageKey.current,
            newValue: serialized,
            oldValue: null,
            storageArea: localStorage,
          })
        );
      }
    } catch (error) {
      console.error(`Error saving to localStorage for key ${key}:`, error);
      setState(prev => ({ ...prev, error: error as Error }));
    }
  }, [key, serializer, encryption, compression, syncAcrossTabs]);

  // Remover valor do localStorage
  const removeValue = useCallback((): void => {
    if (!isLocalStorageAvailable()) {
      return;
    }

    try {
      localStorage.removeItem(storageKey.current);
      setState(prev => ({
        ...prev,
        value: defaultValue as T,
        lastUpdated: null,
        isExpired: false,
      }));
    } catch (error) {
      console.error(`Error removing from localStorage for key ${key}:`, error);
      setState(prev => ({ ...prev, error: error as Error }));
    }
  }, [key, defaultValue]);

  // Limpar todos os valores do localStorage
  const clearAll = useCallback((): void => {
    if (!isLocalStorageAvailable()) {
      return;
    }

    try {
      localStorage.clear();
      setState(prev => ({
        ...prev,
        value: defaultValue as T,
        lastUpdated: null,
        isExpired: false,
      }));
    } catch (error) {
      console.error('Error clearing localStorage:', error);
      setState(prev => ({ ...prev, error: error as Error }));
    }
  }, [defaultValue]);

  // Atualizar valor
  const setValue = useCallback((newValue: T | ((prev: T) => T)): void => {
    const valueToSet = typeof newValue === 'function' 
      ? (newValue as (prev: T) => T)(state.value)
      : newValue;

    setState(prev => ({
      ...prev,
      value: valueToSet,
      loading: false,
      error: null,
      lastUpdated: Date.now(),
      isExpired: false,
    }));

    saveValue(valueToSet);
  }, [state.value, saveValue]);

  // Recarregar valor
  const refresh = useCallback((): void => {
    setState(prev => ({ ...prev, loading: true }));
    
    const loadedValue = loadValue();
    
    setState(prev => ({
      ...prev,
      value: loadedValue ?? (defaultValue as T),
      loading: false,
      lastUpdated: loadedValue ? Date.now() : null,
      isExpired: false,
    }));
  }, [loadValue, defaultValue]);

  // Obter tamanho do valor armazenado
  const getSize = useCallback((): number => {
    if (!isLocalStorageAvailable()) {
      return 0;
    }

    try {
      const stored = localStorage.getItem(storageKey.current);
      return stored ? new Blob([stored]).size : 0;
    } catch {
      return 0;
    }
  }, []);

  // Verificar disponibilidade
  const isAvailable = useCallback((): boolean => {
    return isLocalStorageAvailable();
  }, []);

  // Carregar valor inicial
  useEffect(() => {
    if (!isInitialized.current) {
      const loadedValue = loadValue();
      
      setState(prev => ({
        ...prev,
        value: loadedValue ?? (defaultValue as T),
        loading: false,
        lastUpdated: loadedValue ? Date.now() : null,
        isExpired: false,
      }));

      isInitialized.current = true;
    }
  }, [loadValue, defaultValue]);

  // Sincronização entre abas
  useEffect(() => {
    if (!syncAcrossTabs) return;

    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === storageKey.current && event.newValue !== event.oldValue) {
        refresh();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [syncAcrossTabs, refresh]);

  // Verificar expiração periodicamente
  useEffect(() => {
    if (!expiration) return;

    const checkExpiration = () => {
      const loadedValue = loadValue();
      if (!loadedValue) {
        setState(prev => ({
          ...prev,
          isExpired: true,
          value: defaultValue as T,
        }));
      }
    };

    const interval = setInterval(checkExpiration, 60000); // Verificar a cada minuto
    return () => clearInterval(interval);
  }, [expiration, loadValue, defaultValue]);

  const actions: LocalStorageActions<T> = {
    setValue,
    removeValue,
    clearAll,
    refresh,
    getSize,
    isAvailable,
  };

  return [state.value, actions, state];
}

// Hook especializado para strings
export function useLocalStorageString(
  key: string,
  defaultValue: string = ''
): UseLocalStorageReturn<string> {
  return useLocalStorage(key, defaultValue, {
    serializer: (value: string) => value,
    deserializer: (value: string) => value,
    validator: (value: string) => typeof value === 'string',
  });
}

// Hook especializado para números
export function useLocalStorageNumber(
  key: string,
  defaultValue: number = 0
): UseLocalStorageReturn<number> {
  return useLocalStorage(key, defaultValue, {
    serializer: (value: number) => value.toString(),
    deserializer: (value: string) => parseFloat(value),
    validator: (value: number) => !isNaN(value),
  });
}

// Hook especializado para booleanos
export function useLocalStorageBoolean(
  key: string,
  defaultValue: boolean = false
): UseLocalStorageReturn<boolean> {
  return useLocalStorage(key, defaultValue, {
    serializer: (value: boolean) => value.toString(),
    deserializer: (value: string) => value === 'true',
    validator: (value: boolean) => typeof value === 'boolean',
  });
}

// Hook especializado para arrays
export function useLocalStorageArray<T>(
  key: string,
  defaultValue: T[] = []
): UseLocalStorageReturn<T[]> {
  return useLocalStorage(key, defaultValue, {
    validator: (value: T[]) => Array.isArray(value),
  });
}

// Hook especializado para objetos
export function useLocalStorageObject<T extends Record<string, any>>(
  key: string,
  defaultValue: T = {} as T
): UseLocalStorageReturn<T> {
  return useLocalStorage(key, defaultValue, {
    validator: (value: T) => typeof value === 'object' && value !== null,
  });
}

// Hook para dados criptografados
export function useEncryptedLocalStorage<T>(
  key: string,
  defaultValue?: T
): UseLocalStorageReturn<T> {
  return useLocalStorage(key, defaultValue, {
    encryption: true,
  });
}

// Hook para dados com expiração
export function useExpiringLocalStorage<T>(
  key: string,
  defaultValue?: T,
  expirationMs: number = 24 * 60 * 60 * 1000 // 24 horas
): UseLocalStorageReturn<T> {
  return useLocalStorage(key, defaultValue, {
    expiration: expirationMs,
  });
}

// Hook para dados sincronizados entre abas
export function useSyncedLocalStorage<T>(
  key: string,
  defaultValue?: T
): UseLocalStorageReturn<T> {
  return useLocalStorage(key, defaultValue, {
    syncAcrossTabs: true,
  });
}

// Utilitários para gerenciamento global
export const localStorageUtils = {
  // Obter todas as chaves
  getAllKeys: (): string[] => {
    if (!isLocalStorageAvailable()) return [];
    
    try {
      return Object.keys(localStorage).filter(key => key.startsWith('omni_'));
    } catch {
      return [];
    }
  },

  // Obter tamanho total usado
  getTotalSize: (): number => {
    if (!isLocalStorageAvailable()) return 0;
    
    try {
      return localStorageUtils.getAllKeys().reduce((total, key) => {
        const value = localStorage.getItem(key);
        return total + (value ? new Blob([value]).size : 0);
      }, 0);
    } catch {
      return 0;
    }
  },

  // Limpar dados expirados
  clearExpired: (): void => {
    if (!isLocalStorageAvailable()) return;
    
    try {
      const keys = localStorageUtils.getAllKeys();
      keys.forEach(key => {
        const value = localStorage.getItem(key);
        if (value) {
          try {
            const parsed = JSON.parse(value);
            if (parsed.timestamp && parsed.expiration) {
              const isExpired = Date.now() - parsed.timestamp > parsed.expiration;
              if (isExpired) {
                localStorage.removeItem(key);
              }
            }
          } catch {
            // Ignorar valores que não são JSON válido
          }
        }
      });
    } catch (error) {
      console.error('Error clearing expired localStorage items:', error);
    }
  },

  // Backup de dados
  backup: (): Record<string, string> => {
    if (!isLocalStorageAvailable()) return {};
    
    try {
      const backup: Record<string, string> = {};
      const keys = localStorageUtils.getAllKeys();
      
      keys.forEach(key => {
        const value = localStorage.getItem(key);
        if (value) {
          backup[key] = value;
        }
      });
      
      return backup;
    } catch {
      return {};
    }
  },

  // Restaurar backup
  restore: (backup: Record<string, string>): void => {
    if (!isLocalStorageAvailable()) return;
    
    try {
      Object.entries(backup).forEach(([key, value]) => {
        localStorage.setItem(key, value);
      });
    } catch (error) {
      console.error('Error restoring localStorage backup:', error);
    }
  },
}; 