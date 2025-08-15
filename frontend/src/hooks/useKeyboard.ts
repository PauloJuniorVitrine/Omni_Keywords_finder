/**
 * Hook de Navegação por Teclado - useKeyboard
 * 
 * Fornece funcionalidades de navegação por teclado para componentes React
 * Baseado em WCAG 2.1 AA e padrões de acessibilidade
 * 
 * Tracing ID: useKeyboard_20250127_001
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import { useCallback, useEffect, useRef, useState } from 'react';

export interface KeyboardShortcut {
  /** Combinação de teclas (ex: "Ctrl+Enter", "Escape") */
  key: string;
  /** Função a ser executada */
  handler: (event: KeyboardEvent) => void;
  /** Se o atalho está ativo */
  enabled?: boolean;
  /** Descrição do atalho para acessibilidade */
  description?: string;
  /** Se deve prevenir comportamento padrão */
  preventDefault?: boolean;
}

export interface KeyboardNavigation {
  /** Elementos focáveis */
  focusableElements: HTMLElement[];
  /** Elemento atualmente focado */
  currentFocus: HTMLElement | null;
  /** Índice do elemento focado */
  focusIndex: number;
  /** Se a navegação está ativa */
  isActive: boolean;
}

export interface KeyboardReturn {
  /** Função para registrar atalho */
  registerShortcut: (shortcut: KeyboardShortcut) => void;
  /** Função para remover atalho */
  unregisterShortcut: (key: string) => void;
  /** Função para navegar para próximo elemento */
  focusNext: () => void;
  /** Função para navegar para elemento anterior */
  focusPrevious: () => void;
  /** Função para focar primeiro elemento */
  focusFirst: () => void;
  /** Função para focar último elemento */
  focusLast: () => void;
  /** Função para focar elemento por índice */
  focusByIndex: (index: number) => void;
  /** Função para focar elemento por ID */
  focusById: (id: string) => void;
  /** Estado da navegação */
  navigation: KeyboardNavigation;
  /** Função para ativar/desativar navegação */
  setNavigationActive: (active: boolean) => void;
  /** Função para obter elementos focáveis */
  getFocusableElements: () => HTMLElement[];
  /** Função para validar se tecla é válida */
  isValidKey: (key: string) => boolean;
  /** Função para simular tecla */
  simulateKey: (key: string, element?: HTMLElement) => void;
}

/**
 * Hook principal de navegação por teclado
 */
export const useKeyboard = (containerRef?: React.RefObject<HTMLElement>): KeyboardReturn => {
  const [shortcuts, setShortcuts] = useState<Map<string, KeyboardShortcut>>(new Map());
  const [navigation, setNavigation] = useState<KeyboardNavigation>({
    focusableElements: [],
    currentFocus: null,
    focusIndex: -1,
    isActive: true
  });

  const shortcutsRef = useRef<Map<string, KeyboardShortcut>>(new Map());
  const navigationRef = useRef<KeyboardNavigation>(navigation);

  /**
   * Obtém elementos focáveis dentro do container
   */
  const getFocusableElements = useCallback((): HTMLElement[] => {
    if (!containerRef?.current) {
      return Array.from(document.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"]), [contenteditable="true"]'
      )) as HTMLElement[];
    }

    return Array.from(containerRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"]), [contenteditable="true"]'
    )) as HTMLElement[];
  }, [containerRef]);

  /**
   * Atualiza elementos focáveis
   */
  const updateFocusableElements = useCallback(() => {
    const elements = getFocusableElements().filter(el => {
      const style = window.getComputedStyle(el);
      return style.display !== 'none' && 
             style.visibility !== 'hidden' && 
             style.opacity !== '0' &&
             !el.hasAttribute('aria-hidden');
    });

    setNavigation(prev => ({
      ...prev,
      focusableElements: elements
    }));
  }, [getFocusableElements]);

  /**
   * Registra atalho de teclado
   */
  const registerShortcut = useCallback((shortcut: KeyboardShortcut): void => {
    shortcutsRef.current.set(shortcut.key, shortcut);
    setShortcuts(new Map(shortcutsRef.current));
  }, []);

  /**
   * Remove atalho de teclado
   */
  const unregisterShortcut = useCallback((key: string): void => {
    shortcutsRef.current.delete(key);
    setShortcuts(new Map(shortcutsRef.current));
  }, []);

  /**
   * Valida se tecla é válida
   */
  const isValidKey = useCallback((key: string): boolean => {
    const validKeys = [
      'Escape', 'Enter', 'Space', 'Tab', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight',
      'Home', 'End', 'PageUp', 'PageDown', 'Backspace', 'Delete', 'Insert',
      'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'
    ];
    
    return validKeys.includes(key) || /^[a-zA-Z0-9]$/.test(key);
  }, []);

  /**
   * Simula pressionamento de tecla
   */
  const simulateKey = useCallback((key: string, element?: HTMLElement): void => {
    const target = element || document.activeElement;
    if (!target) return;

    const event = new KeyboardEvent('keydown', {
      key,
      code: `Key${key.toUpperCase()}`,
      bubbles: true,
      cancelable: true
    });

    target.dispatchEvent(event);
  }, []);

  /**
   * Foca próximo elemento
   */
  const focusNext = useCallback((): void => {
    const { focusableElements, focusIndex } = navigationRef.current;
    if (focusableElements.length === 0) return;

    const nextIndex = focusIndex < focusableElements.length - 1 ? focusIndex + 1 : 0;
    const nextElement = focusableElements[nextIndex];

    if (nextElement) {
      nextElement.focus();
      setNavigation(prev => ({
        ...prev,
        currentFocus: nextElement,
        focusIndex: nextIndex
      }));
    }
  }, []);

  /**
   * Foca elemento anterior
   */
  const focusPrevious = useCallback((): void => {
    const { focusableElements, focusIndex } = navigationRef.current;
    if (focusableElements.length === 0) return;

    const prevIndex = focusIndex > 0 ? focusIndex - 1 : focusableElements.length - 1;
    const prevElement = focusableElements[prevIndex];

    if (prevElement) {
      prevElement.focus();
      setNavigation(prev => ({
        ...prev,
        currentFocus: prevElement,
        focusIndex: prevIndex
      }));
    }
  }, []);

  /**
   * Foca primeiro elemento
   */
  const focusFirst = useCallback((): void => {
    const { focusableElements } = navigationRef.current;
    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    firstElement.focus();
    setNavigation(prev => ({
      ...prev,
      currentFocus: firstElement,
      focusIndex: 0
    }));
  }, []);

  /**
   * Foca último elemento
   */
  const focusLast = useCallback((): void => {
    const { focusableElements } = navigationRef.current;
    if (focusableElements.length === 0) return;

    const lastElement = focusableElements[focusableElements.length - 1];
    lastElement.focus();
    setNavigation(prev => ({
      ...prev,
      currentFocus: lastElement,
      focusIndex: focusableElements.length - 1
    }));
  }, []);

  /**
   * Foca elemento por índice
   */
  const focusByIndex = useCallback((index: number): void => {
    const { focusableElements } = navigationRef.current;
    if (index < 0 || index >= focusableElements.length) return;

    const element = focusableElements[index];
    element.focus();
    setNavigation(prev => ({
      ...prev,
      currentFocus: element,
      focusIndex: index
    }));
  }, []);

  /**
   * Foca elemento por ID
   */
  const focusById = useCallback((id: string): void => {
    const element = document.getElementById(id);
    if (!element) return;

    const { focusableElements } = navigationRef.current;
    const index = focusableElements.findIndex(el => el.id === id);
    
    if (index !== -1) {
      element.focus();
      setNavigation(prev => ({
        ...prev,
        currentFocus: element,
        focusIndex: index
      }));
    }
  }, []);

  /**
   * Ativa/desativa navegação
   */
  const setNavigationActive = useCallback((active: boolean): void => {
    setNavigation(prev => ({
      ...prev,
      isActive: active
    }));
  }, []);

  /**
   * Handler principal de eventos de teclado
   */
  const handleKeyDown = useCallback((event: KeyboardEvent): void => {
    const { isActive } = navigationRef.current;
    if (!isActive) return;

    // Verifica atalhos registrados
    const key = event.key;
    const ctrlKey = event.ctrlKey || event.metaKey;
    const shiftKey = event.shiftKey;
    const altKey = event.altKey;

    // Constrói chave do atalho
    let shortcutKey = '';
    if (ctrlKey) shortcutKey += 'Ctrl+';
    if (shiftKey) shortcutKey += 'Shift+';
    if (altKey) shortcutKey += 'Alt+';
    shortcutKey += key;

    const shortcut = shortcutsRef.current.get(shortcutKey);
    if (shortcut && shortcut.enabled !== false) {
      if (shortcut.preventDefault) {
        event.preventDefault();
      }
      shortcut.handler(event);
      return;
    }

    // Navegação por teclado padrão
    switch (key) {
      case 'Tab':
        if (shiftKey) {
          focusPrevious();
        } else {
          focusNext();
        }
        break;
      case 'ArrowDown':
        event.preventDefault();
        focusNext();
        break;
      case 'ArrowUp':
        event.preventDefault();
        focusPrevious();
        break;
      case 'Home':
        event.preventDefault();
        focusFirst();
        break;
      case 'End':
        event.preventDefault();
        focusLast();
        break;
      case 'Escape':
        // Foca no container ou fecha modal
        if (containerRef?.current) {
          containerRef.current.focus();
        }
        break;
    }
  }, [focusNext, focusPrevious, focusFirst, focusLast]);

  /**
   * Handler de mudança de foco
   */
  const handleFocusChange = useCallback((): void => {
    const activeElement = document.activeElement as HTMLElement;
    const { focusableElements } = navigationRef.current;
    
    if (activeElement && focusableElements.includes(activeElement)) {
      const index = focusableElements.indexOf(activeElement);
      setNavigation(prev => ({
        ...prev,
        currentFocus: activeElement,
        focusIndex: index
      }));
    }
  }, []);

  // Efeitos
  useEffect(() => {
    navigationRef.current = navigation;
  }, [navigation]);

  useEffect(() => {
    updateFocusableElements();
    
    const container = containerRef?.current || document;
    container.addEventListener('keydown', handleKeyDown);
    container.addEventListener('focusin', handleFocusChange);
    
    // Observa mudanças no DOM
    const observer = new MutationObserver(updateFocusableElements);
    observer.observe(container, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['style', 'aria-hidden', 'tabindex']
    });

    return () => {
      container.removeEventListener('keydown', handleKeyDown);
      container.removeEventListener('focusin', handleFocusChange);
      observer.disconnect();
    };
  }, [containerRef, handleKeyDown, handleFocusChange, updateFocusableElements]);

  return {
    registerShortcut,
    unregisterShortcut,
    focusNext,
    focusPrevious,
    focusFirst,
    focusLast,
    focusByIndex,
    focusById,
    navigation,
    setNavigationActive,
    getFocusableElements,
    isValidKey,
    simulateKey
  };
};

/**
 * Hook para atalhos globais
 */
export const useGlobalShortcuts = () => {
  const [globalShortcuts, setGlobalShortcuts] = useState<Map<string, KeyboardShortcut>>(new Map());

  const registerGlobalShortcut = useCallback((shortcut: KeyboardShortcut): void => {
    setGlobalShortcuts(prev => new Map(prev.set(shortcut.key, shortcut)));
  }, []);

  const unregisterGlobalShortcut = useCallback((key: string): void => {
    setGlobalShortcuts(prev => {
      const newMap = new Map(prev);
      newMap.delete(key);
      return newMap;
    });
  }, []);

  useEffect(() => {
    const handleGlobalKeyDown = (event: KeyboardEvent): void => {
      const key = event.key;
      const ctrlKey = event.ctrlKey || event.metaKey;
      const shiftKey = event.shiftKey;
      const altKey = event.altKey;

      let shortcutKey = '';
      if (ctrlKey) shortcutKey += 'Ctrl+';
      if (shiftKey) shortcutKey += 'Shift+';
      if (altKey) shortcutKey += 'Alt+';
      shortcutKey += key;

      const shortcut = globalShortcuts.get(shortcutKey);
      if (shortcut && shortcut.enabled !== false) {
        if (shortcut.preventDefault) {
          event.preventDefault();
        }
        shortcut.handler(event);
      }
    };

    document.addEventListener('keydown', handleGlobalKeyDown);
    return () => document.removeEventListener('keydown', handleGlobalKeyDown);
  }, [globalShortcuts]);

  return {
    registerGlobalShortcut,
    unregisterGlobalShortcut
  };
};

/**
 * Hook para navegação por rolagem
 */
export const useScrollNavigation = (containerRef?: React.RefObject<HTMLElement>) => {
  const scrollToElement = useCallback((element: HTMLElement): void => {
    if (!element) return;

    element.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
      inline: 'nearest'
    });
  }, []);

  const scrollToTop = useCallback((): void => {
    const container = containerRef?.current || window;
    container.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }, [containerRef]);

  const scrollToBottom = useCallback((): void => {
    const container = containerRef?.current || window;
    container.scrollTo({
      top: container.scrollHeight,
      behavior: 'smooth'
    });
  }, [containerRef]);

  return {
    scrollToElement,
    scrollToTop,
    scrollToBottom
  };
};

export default useKeyboard; 