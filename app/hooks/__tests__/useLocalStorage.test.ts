/**
 * Testes para useLocalStorage Hook
 * 
 * Prompt: Implementação de testes para hooks críticos
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_USE_LOCAL_STORAGE_001
 * 
 * Testes baseados APENAS no código real do useLocalStorage.ts
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { 
  useLocalStorage, 
  useLocalStorageString, 
  useLocalStorageNumber, 
  useLocalStorageBoolean, 
  useLocalStorageArray, 
  useLocalStorageObject,
  useEncryptedLocalStorage,
  useExpiringLocalStorage,
  useSyncedLocalStorage
} from '../useLocalStorage';

// Mock do localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  key: jest.fn(),
  length: 0
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Mock do btoa e atob para criptografia
Object.defineProperty(window, 'btoa', {
  value: (str: string) => Buffer.from(str, 'binary').toString('base64')
});

Object.defineProperty(window, 'atob', {
  value: (str: string) => Buffer.from(str, 'base64').toString('binary')
});

describe('useLocalStorage Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  describe('useLocalStorage - Funcionalidade Básica', () => {
    it('deve inicializar com valor padrão quando localStorage está vazio', () => {
      const defaultValue = { name: 'Test User', age: 30 };
      
      const { result } = renderHook(() => useLocalStorage('test-key', defaultValue));

      const [value, actions, state] = result.current;

      expect(value).toEqual(defaultValue);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.lastUpdated).toBeNull();
      expect(state.isExpired).toBe(false);
    });

    it('deve carregar valor existente do localStorage', () => {
      const storedValue = { name: 'Stored User', age: 25 };
      localStorageMock.getItem.mockReturnValue(JSON.stringify(storedValue));

      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [value] = result.current;

      expect(value).toEqual(storedValue);
      expect(localStorageMock.getItem).toHaveBeenCalledWith('test-key');
    });

    it('deve salvar valor no localStorage', () => {
      const newValue = { name: 'New User', age: 35 };
      
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      act(() => {
        const [, actions] = result.current;
        actions.setValue(newValue);
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'test-key',
        JSON.stringify(newValue)
      );
    });

    it('deve remover valor do localStorage', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      act(() => {
        const [, actions] = result.current;
        actions.removeValue();
      });

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('test-key');
    });

    it('deve limpar todos os valores do localStorage', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      act(() => {
        const [, actions] = result.current;
        actions.clearAll();
      });

      expect(localStorageMock.clear).toHaveBeenCalled();
    });

    it('deve atualizar valor usando função de callback', () => {
      const initialValue = { count: 0 };
      const { result } = renderHook(() => useLocalStorage('counter', initialValue));

      act(() => {
        const [, actions] = result.current;
        actions.setValue(prev => ({ count: prev.count + 1 }));
      });

      const [value] = result.current;
      expect(value.count).toBe(1);
    });
  });

  describe('useLocalStorage - Validação e Serialização', () => {
    it('deve usar serializador customizado', () => {
      const customSerializer = jest.fn((value) => `custom-${JSON.stringify(value)}`);
      const testValue = { data: 'test' };

      const { result } = renderHook(() => 
        useLocalStorage('test-key', testValue, { serializer: customSerializer })
      );

      act(() => {
        const [, actions] = result.current;
        actions.setValue(testValue);
      });

      expect(customSerializer).toHaveBeenCalledWith(testValue);
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'test-key',
        `custom-${JSON.stringify(testValue)}`
      );
    });

    it('deve usar deserializador customizado', () => {
      const customDeserializer = jest.fn((value) => ({ parsed: value }));
      const storedValue = 'stored-data';
      
      localStorageMock.getItem.mockReturnValue(storedValue);

      const { result } = renderHook(() => 
        useLocalStorage('test-key', {}, { deserializer: customDeserializer })
      );

      expect(customDeserializer).toHaveBeenCalledWith(storedValue);
    });

    it('deve usar validador customizado', () => {
      const customValidator = jest.fn((value) => value && value.valid === true);
      const invalidValue = { valid: false };
      const validValue = { valid: true };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(invalidValue));

      const { result } = renderHook(() => 
        useLocalStorage('test-key', { valid: true }, { validator: customValidator })
      );

      expect(customValidator).toHaveBeenCalledWith(invalidValue);
    });

    it('deve tratar erro de serialização', () => {
      const circularObject: any = { name: 'test' };
      circularObject.self = circularObject;

      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      act(() => {
        const [, actions] = result.current;
        actions.setValue(circularObject);
      });

      const [, , state] = result.current;
      expect(state.error).toBeTruthy();
    });
  });

  describe('useLocalStorage - Expiração', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('deve marcar valor como expirado', () => {
      const expiredValue = {
        data: 'test',
        timestamp: Date.now() - 10000 // 10 segundos atrás
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(expiredValue));

      const { result } = renderHook(() => 
        useLocalStorage('test-key', {}, { expiration: 5000 })
      );

      const [, , state] = result.current;
      expect(state.isExpired).toBe(true);
    });

    it('deve remover valor expirado automaticamente', () => {
      const expiredValue = {
        data: 'test',
        timestamp: Date.now() - 10000
      };

      localStorageMock.getItem.mockReturnValue(JSON.stringify(expiredValue));

      renderHook(() => useLocalStorage('test-key', {}, { expiration: 5000 }));

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('test-key');
    });
  });

  describe('useLocalStorage - Criptografia', () => {
    it('deve criptografar valor quando encryption está habilitado', () => {
      const testValue = { secret: 'sensitive-data' };

      const { result } = renderHook(() => 
        useLocalStorage('test-key', testValue, { encryption: true })
      );

      act(() => {
        const [, actions] = result.current;
        actions.setValue(testValue);
      });

      const setItemCall = localStorageMock.setItem.mock.calls[0];
      expect(setItemCall[0]).toBe('test-key');
      expect(setItemCall[1]).not.toBe(JSON.stringify(testValue)); // Deve estar criptografado
    });

    it('deve descriptografar valor criptografado', () => {
      const testValue = { secret: 'sensitive-data' };
      const encryptedValue = btoa(encodeURIComponent(JSON.stringify(testValue)));
      
      localStorageMock.getItem.mockReturnValue(encryptedValue);

      const { result } = renderHook(() => 
        useLocalStorage('test-key', {}, { encryption: true })
      );

      const [value] = result.current;
      expect(value).toEqual(testValue);
    });
  });

  describe('useLocalStorage - Sincronização entre Abas', () => {
    it('deve sincronizar mudanças entre abas', () => {
      const { result } = renderHook(() => 
        useLocalStorage('test-key', {}, { syncAcrossTabs: true })
      );

      // Simular mudança em outra aba
      act(() => {
        const storageEvent = new StorageEvent('storage', {
          key: 'test-key',
          newValue: JSON.stringify({ updated: true }),
          oldValue: null,
          storageArea: localStorage
        });
        window.dispatchEvent(storageEvent);
      });

      const [value] = result.current;
      expect(value).toEqual({ updated: true });
    });
  });

  describe('useLocalStorageString', () => {
    it('deve gerenciar strings no localStorage', () => {
      const { result } = renderHook(() => useLocalStorageString('string-key', 'default'));

      const [value, actions] = result.current;

      expect(value).toBe('default');

      act(() => {
        actions.setValue('new string value');
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'string-key',
        JSON.stringify('new string value')
      );
    });

    it('deve carregar string existente', () => {
      const storedString = 'stored string value';
      localStorageMock.getItem.mockReturnValue(JSON.stringify(storedString));

      const { result } = renderHook(() => useLocalStorageString('string-key', 'default'));

      const [value] = result.current;
      expect(value).toBe(storedString);
    });
  });

  describe('useLocalStorageNumber', () => {
    it('deve gerenciar números no localStorage', () => {
      const { result } = renderHook(() => useLocalStorageNumber('number-key', 0));

      const [value, actions] = result.current;

      expect(value).toBe(0);

      act(() => {
        actions.setValue(42);
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'number-key',
        JSON.stringify(42)
      );
    });

    it('deve carregar número existente', () => {
      const storedNumber = 100;
      localStorageMock.getItem.mockReturnValue(JSON.stringify(storedNumber));

      const { result } = renderHook(() => useLocalStorageNumber('number-key', 0));

      const [value] = result.current;
      expect(value).toBe(storedNumber);
    });
  });

  describe('useLocalStorageBoolean', () => {
    it('deve gerenciar booleanos no localStorage', () => {
      const { result } = renderHook(() => useLocalStorageBoolean('bool-key', false));

      const [value, actions] = result.current;

      expect(value).toBe(false);

      act(() => {
        actions.setValue(true);
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'bool-key',
        JSON.stringify(true)
      );
    });

    it('deve carregar booleano existente', () => {
      const storedBoolean = true;
      localStorageMock.getItem.mockReturnValue(JSON.stringify(storedBoolean));

      const { result } = renderHook(() => useLocalStorageBoolean('bool-key', false));

      const [value] = result.current;
      expect(value).toBe(storedBoolean);
    });
  });

  describe('useLocalStorageArray', () => {
    it('deve gerenciar arrays no localStorage', () => {
      const { result } = renderHook(() => useLocalStorageArray('array-key', []));

      const [value, actions] = result.current;

      expect(value).toEqual([]);

      act(() => {
        actions.setValue(['item1', 'item2']);
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'array-key',
        JSON.stringify(['item1', 'item2'])
      );
    });

    it('deve carregar array existente', () => {
      const storedArray = ['stored', 'items'];
      localStorageMock.getItem.mockReturnValue(JSON.stringify(storedArray));

      const { result } = renderHook(() => useLocalStorageArray('array-key', []));

      const [value] = result.current;
      expect(value).toEqual(storedArray);
    });
  });

  describe('useLocalStorageObject', () => {
    it('deve gerenciar objetos no localStorage', () => {
      const { result } = renderHook(() => useLocalStorageObject('object-key', {}));

      const [value, actions] = result.current;

      expect(value).toEqual({});

      act(() => {
        actions.setValue({ name: 'John', age: 30 });
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'object-key',
        JSON.stringify({ name: 'John', age: 30 })
      );
    });

    it('deve carregar objeto existente', () => {
      const storedObject = { name: 'Stored', age: 25 };
      localStorageMock.getItem.mockReturnValue(JSON.stringify(storedObject));

      const { result } = renderHook(() => useLocalStorageObject('object-key', {}));

      const [value] = result.current;
      expect(value).toEqual(storedObject);
    });
  });

  describe('useEncryptedLocalStorage', () => {
    it('deve criptografar valores automaticamente', () => {
      const testValue = { secret: 'confidential' };

      const { result } = renderHook(() => useEncryptedLocalStorage('secret-key', testValue));

      act(() => {
        const [, actions] = result.current;
        actions.setValue(testValue);
      });

      const setItemCall = localStorageMock.setItem.mock.calls[0];
      expect(setItemCall[0]).toBe('secret-key');
      expect(setItemCall[1]).not.toBe(JSON.stringify(testValue));
    });
  });

  describe('useExpiringLocalStorage', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('deve configurar expiração automaticamente', () => {
      const testValue = { data: 'temporary' };

      const { result } = renderHook(() => 
        useExpiringLocalStorage('temp-key', testValue, 60000) // 1 minuto
      );

      act(() => {
        const [, actions] = result.current;
        actions.setValue(testValue);
      });

      const [, , state] = result.current;
      expect(state.lastUpdated).toBeTruthy();
    });
  });

  describe('useSyncedLocalStorage', () => {
    it('deve habilitar sincronização entre abas', () => {
      const { result } = renderHook(() => useSyncedLocalStorage('sync-key', {}));

      // Simular mudança em outra aba
      act(() => {
        const storageEvent = new StorageEvent('storage', {
          key: 'sync-key',
          newValue: JSON.stringify({ synced: true }),
          oldValue: null,
          storageArea: localStorage
        });
        window.dispatchEvent(storageEvent);
      });

      const [value] = result.current;
      expect(value).toEqual({ synced: true });
    });
  });

  describe('Utilitários', () => {
    it('deve verificar disponibilidade do localStorage', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [, actions] = result.current;
      const isAvailable = actions.isAvailable();

      expect(isAvailable).toBe(true);
    });

    it('deve calcular tamanho do localStorage', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [, actions] = result.current;
      const size = actions.getSize();

      expect(typeof size).toBe('number');
    });

    it('deve atualizar lastUpdated ao modificar valor', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      act(() => {
        const [, actions] = result.current;
        actions.setValue({ updated: true });
      });

      const [, , state] = result.current;
      expect(state.lastUpdated).toBeTruthy();
      expect(typeof state.lastUpdated).toBe('number');
    });
  });

  describe('Tratamento de Erros', () => {
    it('deve tratar localStorage não disponível', () => {
      // Simular localStorage não disponível
      const originalLocalStorage = window.localStorage;
      delete (window as any).localStorage;

      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [, , state] = result.current;
      expect(state.error).toBeTruthy();

      // Restaurar localStorage
      (window as any).localStorage = originalLocalStorage;
    });

    it('deve tratar erro de serialização', () => {
      const circularObject: any = { name: 'test' };
      circularObject.self = circularObject;

      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      act(() => {
        const [, actions] = result.current;
        actions.setValue(circularObject);
      });

      const [, , state] = result.current;
      expect(state.error).toBeTruthy();
    });

    it('deve tratar erro de deserialização', () => {
      localStorageMock.getItem.mockReturnValue('invalid-json');

      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [, , state] = result.current;
      expect(state.error).toBeTruthy();
    });
  });

  describe('Integração useLocalStorage', () => {
    it('deve manter consistência entre operações', () => {
      const { result } = renderHook(() => useLocalStorage('integration-key', { count: 0 }));

      // Operação 1: Definir valor
      act(() => {
        const [, actions] = result.current;
        actions.setValue({ count: 1 });
      });

      // Operação 2: Atualizar usando callback
      act(() => {
        const [, actions] = result.current;
        actions.setValue(prev => ({ count: prev.count + 1 }));
      });

      // Operação 3: Remover
      act(() => {
        const [, actions] = result.current;
        actions.removeValue();
      });

      expect(localStorageMock.setItem).toHaveBeenCalledTimes(2);
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('integration-key');
    });
  });

  describe('Performance useLocalStorage', () => {
    it('deve evitar operações desnecessárias', () => {
      const { result } = renderHook(() => useLocalStorage('perf-key', { data: 'initial' }));

      // Definir mesmo valor
      act(() => {
        const [, actions] = result.current;
        actions.setValue({ data: 'initial' });
      });

      // Verificar se não houve operação desnecessária
      expect(localStorageMock.setItem).toHaveBeenCalledTimes(1);
    });
  });
}); 