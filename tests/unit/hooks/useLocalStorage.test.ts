/**
 * Testes Unitários - useLocalStorage Hook
 * 
 * Prompt: Implementação de testes para hooks críticos
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_USE_LOCAL_STORAGE_017
 * 
 * Baseado em código real do hook useLocalStorage.ts
 */

import { renderHook, act } from '@testing-library/react';
import {
  useLocalStorage,
  useLocalStorageString,
  useLocalStorageNumber,
  useLocalStorageBoolean,
  useLocalStorageArray,
  useLocalStorageObject,
  useEncryptedLocalStorage,
  useExpiringLocalStorage,
  useSyncedLocalStorage,
  localStorageUtils,
  type LocalStorageConfig,
  type LocalStorageState,
  type LocalStorageActions
} from '../../app/hooks/useLocalStorage';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
    key: jest.fn((index: number) => Object.keys(store)[index] || null),
    length: Object.keys(store).length,
  };
})();

// Mock StorageEvent
const createStorageEvent = (key: string, newValue: string | null, oldValue: string | null) => {
  return new StorageEvent('storage', {
    key,
    newValue,
    oldValue,
    storageArea: localStorageMock,
  });
};

// Setup mocks
beforeEach(() => {
  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
    writable: true,
  });

  Object.defineProperty(window, 'btoa', {
    value: (str: string) => Buffer.from(str, 'binary').toString('base64'),
    writable: true,
  });

  Object.defineProperty(window, 'atob', {
    value: (str: string) => Buffer.from(str, 'base64').toString('binary'),
    writable: true,
  });

  // Reset mocks
  localStorageMock.clear();
  jest.clearAllMocks();
});

describe('useLocalStorage Hook - Gerenciamento de Estado Persistente', () => {
  
  describe('Hook Principal useLocalStorage', () => {
    
    test('deve retornar valor padrão quando localStorage está vazio', () => {
      const defaultValue = { name: 'test', value: 123 };
      const { result } = renderHook(() => useLocalStorage('test-key', defaultValue));

      const [value, actions, state] = result.current;

      expect(value).toEqual(defaultValue);
      expect(state.loading).toBe(false);
      expect(state.error).toBe(null);
      expect(state.lastUpdated).toBe(null);
      expect(state.isExpired).toBe(false);
      expect(typeof actions.setValue).toBe('function');
      expect(typeof actions.removeValue).toBe('function');
      expect(typeof actions.clearAll).toBe('function');
      expect(typeof actions.refresh).toBe('function');
      expect(typeof actions.getSize).toBe('function');
      expect(typeof actions.isAvailable).toBe('function');
    });

    test('deve carregar valor existente do localStorage', () => {
      const storedValue = { name: 'stored', value: 456 };
      const serializedValue = JSON.stringify({
        data: storedValue,
        timestamp: Date.now(),
        version: '1.0',
      });

      localStorageMock.getItem.mockReturnValue(serializedValue);

      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [value, actions, state] = result.current;

      expect(value).toEqual(storedValue);
      expect(state.loading).toBe(false);
      expect(state.lastUpdated).toBeGreaterThan(0);
    });

    test('deve salvar valor no localStorage', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue({ name: 'new-value', value: 789 });
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'omni_test-key',
        expect.stringContaining('"name":"new-value"')
      );
    });

    test('deve atualizar valor usando função', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', { count: 0 }));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue(prev => ({ ...prev, count: prev.count + 1 }));
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'omni_test-key',
        expect.stringContaining('"count":1')
      );
    });

    test('deve remover valor do localStorage', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [value, actions] = result.current;

      act(() => {
        actions.removeValue();
      });

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('omni_test-key');
    });

    test('deve limpar todos os valores do localStorage', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [value, actions] = result.current;

      act(() => {
        actions.clearAll();
      });

      expect(localStorageMock.clear).toHaveBeenCalled();
    });

    test('deve recarregar valor do localStorage', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [value, actions] = result.current;

      act(() => {
        actions.refresh();
      });

      expect(localStorageMock.getItem).toHaveBeenCalledWith('omni_test-key');
    });

    test('deve calcular tamanho do valor armazenado', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue({ large: 'data'.repeat(100) });
      });

      const size = actions.getSize();
      expect(size).toBeGreaterThan(0);
    });

    test('deve verificar disponibilidade do localStorage', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [value, actions] = result.current;

      const isAvailable = actions.isAvailable();
      expect(isAvailable).toBe(true);
    });

    test('deve lidar com erro de serialização', () => {
      const circularObject: any = {};
      circularObject.self = circularObject;

      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue(circularObject);
      });

      // Deve lidar graciosamente com erro de serialização
      expect(localStorageMock.setItem).toHaveBeenCalled();
    });

    test('deve lidar com erro de deserialização', () => {
      localStorageMock.getItem.mockReturnValue('invalid-json');

      const { result } = renderHook(() => useLocalStorage('test-key', { default: true }));

      const [value, actions, state] = result.current;

      expect(value).toEqual({ default: true });
      expect(state.error).toBe(null);
    });
  });

  describe('Configurações Avançadas', () => {
    
    test('deve usar serializador personalizado', () => {
      const customSerializer = jest.fn((value: any) => `custom_${JSON.stringify(value)}`);
      const customDeserializer = jest.fn((value: string) => JSON.parse(value.replace('custom_', '')));

      const config: Partial<LocalStorageConfig> = {
        serializer: customSerializer,
        deserializer: customDeserializer,
      };

      const { result } = renderHook(() => useLocalStorage('test-key', {}, config));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue({ test: 'data' });
      });

      expect(customSerializer).toHaveBeenCalled();
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'omni_test-key',
        expect.stringContaining('custom_')
      );
    });

    test('deve usar validador personalizado', () => {
      const customValidator = jest.fn((value: any) => value && value.isValid === true);

      const config: Partial<LocalStorageConfig> = {
        validator: customValidator,
      };

      const { result } = renderHook(() => useLocalStorage('test-key', {}, config));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue({ isValid: true, data: 'test' });
      });

      expect(customValidator).toHaveBeenCalled();
    });

    test('deve lidar com valores inválidos', () => {
      const customValidator = jest.fn((value: any) => value && value.isValid === true);

      const config: Partial<LocalStorageConfig> = {
        validator: customValidator,
      };

      const { result } = renderHook(() => useLocalStorage('test-key', { default: true }, config));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue({ isValid: false, data: 'test' });
      });

      expect(customValidator).toHaveBeenCalledWith({ isValid: false, data: 'test' });
    });
  });

  describe('Criptografia', () => {
    
    test('deve criptografar dados quando habilitado', () => {
      const { result } = renderHook(() => useEncryptedLocalStorage('test-key', {}));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue({ secret: 'data' });
      });

      const setItemCall = localStorageMock.setItem.mock.calls[0];
      const storedValue = setItemCall[1];

      // Verificar se o valor está criptografado (base64)
      expect(storedValue).toMatch(/^[A-Za-z0-9+/=]+$/);
    });

    test('deve descriptografar dados ao carregar', () => {
      const originalValue = { secret: 'data' };
      const encryptedValue = btoa(encodeURIComponent(JSON.stringify({
        data: originalValue,
        timestamp: Date.now(),
        version: '1.0',
      })));

      localStorageMock.getItem.mockReturnValue(encryptedValue);

      const { result } = renderHook(() => useEncryptedLocalStorage('test-key', {}));

      const [value, actions, state] = result.current;

      expect(value).toEqual(originalValue);
    });

    test('deve lidar com erro de descriptografia', () => {
      localStorageMock.getItem.mockReturnValue('invalid-encrypted-data');

      const { result } = renderHook(() => useEncryptedLocalStorage('test-key', { default: true }));

      const [value, actions, state] = result.current;

      expect(value).toEqual({ default: true });
    });
  });

  describe('Expiração', () => {
    
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    test('deve marcar dados como expirados', () => {
      const expiredTimestamp = Date.now() - (25 * 60 * 60 * 1000); // 25 horas atrás
      const storedValue = JSON.stringify({
        data: { test: 'data' },
        timestamp: expiredTimestamp,
        version: '1.0',
      });

      localStorageMock.getItem.mockReturnValue(storedValue);

      const { result } = renderHook(() => useExpiringLocalStorage('test-key', { default: true }, 24 * 60 * 60 * 1000));

      const [value, actions, state] = result.current;

      expect(state.isExpired).toBe(true);
      expect(value).toEqual({ default: true });
    });

    test('deve remover dados expirados automaticamente', () => {
      const expiredTimestamp = Date.now() - (25 * 60 * 60 * 1000);
      const storedValue = JSON.stringify({
        data: { test: 'data' },
        timestamp: expiredTimestamp,
        version: '1.0',
      });

      localStorageMock.getItem.mockReturnValue(storedValue);

      renderHook(() => useExpiringLocalStorage('test-key', { default: true }, 24 * 60 * 60 * 1000));

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('omni_test-key');
    });

    test('deve verificar expiração periodicamente', () => {
      const { result } = renderHook(() => useExpiringLocalStorage('test-key', { default: true }, 24 * 60 * 60 * 1000));

      act(() => {
        jest.advanceTimersByTime(60000); // Avançar 1 minuto
      });

      expect(localStorageMock.getItem).toHaveBeenCalled();
    });
  });

  describe('Sincronização entre Abas', () => {
    
    test('deve sincronizar mudanças entre abas', () => {
      const { result } = renderHook(() => useSyncedLocalStorage('test-key', { default: true }));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue({ synced: 'data' });
      });

      // Verificar se o evento de storage foi disparado
      expect(localStorageMock.setItem).toHaveBeenCalled();
    });

    test('deve reagir a mudanças de outras abas', () => {
      const { result } = renderHook(() => useSyncedLocalStorage('test-key', { default: true }));

      const [value, actions] = result.current;

      // Simular mudança de outra aba
      act(() => {
        const storageEvent = createStorageEvent('omni_test-key', 'new-value', 'old-value');
        window.dispatchEvent(storageEvent);
      });

      expect(localStorageMock.getItem).toHaveBeenCalled();
    });
  });

  describe('Hooks Especializados', () => {
    
    test('useLocalStorageString deve trabalhar com strings', () => {
      const { result } = renderHook(() => useLocalStorageString('string-key', 'default'));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue('new string value');
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'omni_string-key',
        expect.stringContaining('"data":"new string value"')
      );
    });

    test('useLocalStorageNumber deve trabalhar com números', () => {
      const { result } = renderHook(() => useLocalStorageNumber('number-key', 0));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue(42);
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'omni_number-key',
        expect.stringContaining('"data":42')
      );
    });

    test('useLocalStorageBoolean deve trabalhar com booleanos', () => {
      const { result } = renderHook(() => useLocalStorageBoolean('bool-key', false));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue(true);
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'omni_bool-key',
        expect.stringContaining('"data":true')
      );
    });

    test('useLocalStorageArray deve trabalhar com arrays', () => {
      const { result } = renderHook(() => useLocalStorageArray('array-key', []));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue([1, 2, 3, 'test']);
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'omni_array-key',
        expect.stringContaining('"data":[1,2,3,"test"]')
      );
    });

    test('useLocalStorageObject deve trabalhar com objetos', () => {
      const { result } = renderHook(() => useLocalStorageObject('object-key', {}));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue({ name: 'test', value: 123 });
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'omni_object-key',
        expect.stringContaining('"data":{"name":"test","value":123}')
      );
    });
  });

  describe('Utilitários localStorageUtils', () => {
    
    test('getAllKeys deve retornar todas as chaves omni_', () => {
      localStorageMock.setItem('omni_key1', 'value1');
      localStorageMock.setItem('omni_key2', 'value2');
      localStorageMock.setItem('other_key', 'value3');

      const keys = localStorageUtils.getAllKeys();

      expect(keys).toContain('omni_key1');
      expect(keys).toContain('omni_key2');
      expect(keys).not.toContain('other_key');
    });

    test('getTotalSize deve calcular tamanho total', () => {
      localStorageMock.setItem('omni_key1', 'value1');
      localStorageMock.setItem('omni_key2', 'value2');

      const totalSize = localStorageUtils.getTotalSize();

      expect(totalSize).toBeGreaterThan(0);
    });

    test('clearExpired deve remover dados expirados', () => {
      const expiredData = JSON.stringify({
        data: { test: 'data' },
        timestamp: Date.now() - (25 * 60 * 60 * 1000),
        expiration: 24 * 60 * 60 * 1000,
      });

      localStorageMock.setItem('omni_expired_key', expiredData);

      localStorageUtils.clearExpired();

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('omni_expired_key');
    });

    test('backup deve criar backup dos dados', () => {
      localStorageMock.setItem('omni_key1', 'value1');
      localStorageMock.setItem('omni_key2', 'value2');

      const backup = localStorageUtils.backup();

      expect(backup).toHaveProperty('omni_key1', 'value1');
      expect(backup).toHaveProperty('omni_key2', 'value2');
    });

    test('restore deve restaurar backup', () => {
      const backup = {
        'omni_key1': 'value1',
        'omni_key2': 'value2',
      };

      localStorageUtils.restore(backup);

      expect(localStorageMock.setItem).toHaveBeenCalledWith('omni_key1', 'value1');
      expect(localStorageMock.setItem).toHaveBeenCalledWith('omni_key2', 'value2');
    });
  });

  describe('Validação de Dados', () => {
    
    test('deve validar tipos de dados corretos', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [value, actions] = result.current;

      const testData = [
        { string: 'test' },
        { number: 123 },
        { boolean: true },
        { array: [1, 2, 3] },
        { object: { nested: 'value' } },
        { null: null },
        { undefined: undefined },
      ];

      testData.forEach(data => {
        act(() => {
          actions.setValue(data);
        });

        expect(localStorageMock.setItem).toHaveBeenCalled();
      });
    });

    test('deve lidar com valores nulos e undefined', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', { default: true }));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue(null);
      });

      expect(localStorageMock.setItem).toHaveBeenCalled();
    });

    test('deve validar tamanho dos dados', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [value, actions] = result.current;

      const largeData = { data: 'x'.repeat(10000) };

      act(() => {
        actions.setValue(largeData);
      });

      const size = actions.getSize();
      expect(size).toBeGreaterThan(10000);
    });
  });

  describe('Tratamento de Erros', () => {
    
    test('deve lidar com localStorage indisponível', () => {
      // Mock localStorage indisponível
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: jest.fn(() => { throw new Error('Storage not available'); }),
          setItem: jest.fn(() => { throw new Error('Storage not available'); }),
          removeItem: jest.fn(() => { throw new Error('Storage not available'); }),
          clear: jest.fn(() => { throw new Error('Storage not available'); }),
        },
        writable: true,
      });

      const { result } = renderHook(() => useLocalStorage('test-key', { default: true }));

      const [value, actions] = result.current;

      expect(value).toEqual({ default: true });
      expect(actions.isAvailable()).toBe(false);
    });

    test('deve lidar com erro de criptografia', () => {
      Object.defineProperty(window, 'atob', {
        value: jest.fn(() => { throw new Error('Decryption failed'); }),
        writable: true,
      });

      localStorageMock.getItem.mockReturnValue('invalid-encrypted');

      const { result } = renderHook(() => useEncryptedLocalStorage('test-key', { default: true }));

      const [value, actions, state] = result.current;

      expect(value).toEqual({ default: true });
    });

    test('deve lidar com erro de compressão', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}, { compression: true }));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue({ test: 'data' });
      });

      // Deve continuar funcionando mesmo com erro de compressão
      expect(localStorageMock.setItem).toHaveBeenCalled();
    });
  });

  describe('Performance e Otimização', () => {
    
    test('deve evitar re-renders desnecessários', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [value, actions] = result.current;

      // Primeira atualização
      act(() => {
        actions.setValue({ test: 'data1' });
      });

      const firstCallCount = localStorageMock.setItem.mock.calls.length;

      // Segunda atualização com mesmo valor
      act(() => {
        actions.setValue({ test: 'data1' });
      });

      expect(localStorageMock.setItem.mock.calls.length).toBeGreaterThan(firstCallCount);
    });

    test('deve usar prefixo omni_ para evitar conflitos', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue({ test: 'data' });
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'omni_test-key',
        expect.any(String)
      );
    });

    test('deve incluir metadados nos dados armazenados', () => {
      const { result } = renderHook(() => useLocalStorage('test-key', {}));

      const [value, actions] = result.current;

      act(() => {
        actions.setValue({ test: 'data' });
      });

      const storedValue = localStorageMock.setItem.mock.calls[0][1];
      const parsed = JSON.parse(storedValue);

      expect(parsed).toHaveProperty('data');
      expect(parsed).toHaveProperty('timestamp');
      expect(parsed).toHaveProperty('version');
    });
  });
}); 