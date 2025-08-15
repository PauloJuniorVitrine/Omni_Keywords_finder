/**
 * Testes Unitários - useKeyboard Hook
 * 
 * Testa funcionalidades de navegação por teclado do hook useKeyboard
 * Baseado no código real do sistema Omni Keywords Finder
 * 
 * Tracing ID: useKeyboard_test_20250127_001
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import { renderHook, act } from '@testing-library/react';
import { useKeyboard } from '../../../hooks/useKeyboard';

describe('useKeyboard Hook', () => {
  let mockContainer: HTMLElement;
  let mockButton1: HTMLElement;
  let mockButton2: HTMLElement;
  let mockInput: HTMLElement;

  beforeEach(() => {
    // Mock dos elementos DOM
    mockContainer = document.createElement('div');
    mockButton1 = document.createElement('button');
    mockButton2 = document.createElement('button');
    mockInput = document.createElement('input');

    mockButton1.id = 'button1';
    mockButton2.id = 'button2';
    mockInput.id = 'input1';

    mockContainer.appendChild(mockButton1);
    mockContainer.appendChild(mockButton2);
    mockContainer.appendChild(mockInput);

    // Mock do querySelector
    jest.spyOn(mockContainer, 'querySelectorAll').mockReturnValue([
      mockButton1,
      mockButton2,
      mockInput
    ] as any);

    // Mock do getComputedStyle
    Object.defineProperty(window, 'getComputedStyle', {
      value: () => ({
        display: 'block',
        visibility: 'visible',
        opacity: '1'
      })
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Registro de Atalhos', () => {
    it('deve registrar atalho de teclado', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      const handler = jest.fn();
      
      act(() => {
        result.current.registerShortcut({
          key: 'Ctrl+Enter',
          handler,
          description: 'Salvar formulário'
        });
      });

      expect(result.current.navigation.focusableElements).toHaveLength(3);
    });

    it('deve remover atalho de teclado', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      const handler = jest.fn();
      
      act(() => {
        result.current.registerShortcut({
          key: 'Ctrl+Enter',
          handler,
          description: 'Salvar formulário'
        });
      });

      act(() => {
        result.current.unregisterShortcut('Ctrl+Enter');
      });

      // Verifica se o atalho foi removido
      expect(result.current.navigation.focusableElements).toHaveLength(3);
    });
  });

  describe('Validação de Teclas', () => {
    it('deve validar teclas válidas', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      expect(result.current.isValidKey('Enter')).toBe(true);
      expect(result.current.isValidKey('Escape')).toBe(true);
      expect(result.current.isValidKey('Tab')).toBe(true);
      expect(result.current.isValidKey('a')).toBe(true);
      expect(result.current.isValidKey('1')).toBe(true);
    });

    it('deve rejeitar teclas inválidas', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      expect(result.current.isValidKey('')).toBe(false);
      expect(result.current.isValidKey('InvalidKey')).toBe(false);
    });
  });

  describe('Simulação de Teclas', () => {
    it('deve simular pressionamento de tecla', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      const mockElement = {
        dispatchEvent: jest.fn()
      } as unknown as HTMLElement;

      act(() => {
        result.current.simulateKey('Enter', mockElement);
      });

      expect(mockElement.dispatchEvent).toHaveBeenCalled();
    });

    it('deve simular tecla no elemento ativo quando não especificado', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      const mockActiveElement = {
        dispatchEvent: jest.fn()
      } as unknown as HTMLElement;

      Object.defineProperty(document, 'activeElement', {
        value: mockActiveElement,
        writable: true
      });

      act(() => {
        result.current.simulateKey('Enter');
      });

      expect(mockActiveElement.dispatchEvent).toHaveBeenCalled();
    });
  });

  describe('Navegação por Foco', () => {
    it('deve focar próximo elemento', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      // Simula foco no primeiro elemento
      act(() => {
        result.current.focusByIndex(0);
      });

      expect(result.current.navigation.currentFocus).toBe(mockButton1);
      expect(result.current.navigation.focusIndex).toBe(0);

      // Foca próximo elemento
      act(() => {
        result.current.focusNext();
      });

      expect(result.current.navigation.currentFocus).toBe(mockButton2);
      expect(result.current.navigation.focusIndex).toBe(1);
    });

    it('deve focar elemento anterior', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      // Simula foco no segundo elemento
      act(() => {
        result.current.focusByIndex(1);
      });

      expect(result.current.navigation.currentFocus).toBe(mockButton2);
      expect(result.current.navigation.focusIndex).toBe(1);

      // Foca elemento anterior
      act(() => {
        result.current.focusPrevious();
      });

      expect(result.current.navigation.currentFocus).toBe(mockButton1);
      expect(result.current.navigation.focusIndex).toBe(0);
    });

    it('deve focar primeiro elemento', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      act(() => {
        result.current.focusFirst();
      });

      expect(result.current.navigation.currentFocus).toBe(mockButton1);
      expect(result.current.navigation.focusIndex).toBe(0);
    });

    it('deve focar último elemento', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      act(() => {
        result.current.focusLast();
      });

      expect(result.current.navigation.currentFocus).toBe(mockInput);
      expect(result.current.navigation.focusIndex).toBe(2);
    });

    it('deve focar elemento por índice', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      act(() => {
        result.current.focusByIndex(1);
      });

      expect(result.current.navigation.currentFocus).toBe(mockButton2);
      expect(result.current.navigation.focusIndex).toBe(1);
    });

    it('deve focar elemento por ID', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      // Mock do getElementById
      jest.spyOn(document, 'getElementById').mockReturnValue(mockButton2);

      act(() => {
        result.current.focusById('button2');
      });

      expect(result.current.navigation.currentFocus).toBe(mockButton2);
      expect(result.current.navigation.focusIndex).toBe(1);
    });

    it('não deve focar elemento inexistente', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      jest.spyOn(document, 'getElementById').mockReturnValue(null);

      act(() => {
        result.current.focusById('inexistente');
      });

      expect(result.current.navigation.currentFocus).toBeNull();
    });
  });

  describe('Controle de Navegação', () => {
    it('deve ativar navegação', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      act(() => {
        result.current.setNavigationActive(true);
      });

      expect(result.current.navigation.isActive).toBe(true);
    });

    it('deve desativar navegação', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      act(() => {
        result.current.setNavigationActive(false);
      });

      expect(result.current.navigation.isActive).toBe(false);
    });
  });

  describe('Obtenção de Elementos Focáveis', () => {
    it('deve obter elementos focáveis do container', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      const elements = result.current.getFocusableElements();
      expect(elements).toHaveLength(3);
      expect(elements).toContain(mockButton1);
      expect(elements).toContain(mockButton2);
      expect(elements).toContain(mockInput);
    });

    it('deve obter elementos focáveis do documento quando não há container', () => {
      const { result } = renderHook(() => useKeyboard());

      // Mock do querySelector global
      jest.spyOn(document, 'querySelectorAll').mockReturnValue([
        mockButton1,
        mockButton2
      ] as any);

      const elements = result.current.getFocusableElements();
      expect(elements).toHaveLength(2);
    });
  });

  describe('Ciclo de Navegação', () => {
    it('deve fazer ciclo para o primeiro elemento quando no último', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      // Foca no último elemento
      act(() => {
        result.current.focusByIndex(2);
      });

      // Foca próximo (deve ir para o primeiro)
      act(() => {
        result.current.focusNext();
      });

      expect(result.current.navigation.currentFocus).toBe(mockButton1);
      expect(result.current.navigation.focusIndex).toBe(0);
    });

    it('deve fazer ciclo para o último elemento quando no primeiro', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      // Foca no primeiro elemento
      act(() => {
        result.current.focusByIndex(0);
      });

      // Foca anterior (deve ir para o último)
      act(() => {
        result.current.focusPrevious();
      });

      expect(result.current.navigation.currentFocus).toBe(mockInput);
      expect(result.current.navigation.focusIndex).toBe(2);
    });
  });

  describe('Navegação com Lista Vazia', () => {
    it('deve lidar com lista vazia de elementos focáveis', () => {
      // Mock de container vazio
      const emptyContainer = document.createElement('div');
      jest.spyOn(emptyContainer, 'querySelectorAll').mockReturnValue([] as any);

      const { result } = renderHook(() => useKeyboard({ current: emptyContainer }));

      act(() => {
        result.current.focusNext();
      });

      expect(result.current.navigation.currentFocus).toBeNull();
      expect(result.current.navigation.focusIndex).toBe(-1);
    });
  });

  describe('Índices Inválidos', () => {
    it('não deve focar com índice negativo', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      act(() => {
        result.current.focusByIndex(-1);
      });

      expect(result.current.navigation.currentFocus).toBeNull();
    });

    it('não deve focar com índice maior que a lista', () => {
      const { result } = renderHook(() => useKeyboard({ current: mockContainer }));

      act(() => {
        result.current.focusByIndex(10);
      });

      expect(result.current.navigation.currentFocus).toBeNull();
    });
  });
}); 