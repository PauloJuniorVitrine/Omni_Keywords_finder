/**
 * Hook de Gerenciamento de Foco - useFocus
 * 
 * Fornece funcionalidades de gerenciamento de foco para componentes React
 * Baseado em WCAG 2.1 AA e padrões de acessibilidade
 * 
 * Tracing ID: useFocus_20250127_001
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import { useCallback, useEffect, useRef, useState } from 'react';

export interface FocusTrapOptions {
  /** Se o focus trap está ativo */
  enabled?: boolean;
  /** Elemento que receberá o foco quando o trap for ativado */
  initialFocus?: HTMLElement | null;
  /** Elemento que receberá o foco quando o trap for desativado */
  returnFocus?: HTMLElement | null;
  /** Se deve restaurar foco ao desativar */
  restoreFocus?: boolean;
  /** Se deve focar automaticamente no primeiro elemento */
  autoFocus?: boolean;
  /** Se deve permitir foco fora do trap */
  allowOutsideFocus?: boolean;
}

export interface FocusHistory {
  /** Elementos que receberam foco */
  elements: HTMLElement[];
  /** Timestamps dos focos */
  timestamps: number[];
  /** Máximo de elementos no histórico */
  maxSize: number;
}

export interface FocusReturn {
  /** Função para ativar focus trap */
  activateFocusTrap: (options?: FocusTrapOptions) => void;
  /** Função para desativar focus trap */
  deactivateFocusTrap: () => void;
  /** Função para focar elemento específico */
  focusElement: (element: HTMLElement) => void;
  /** Função para focar primeiro elemento */
  focusFirst: () => void;
  /** Função para focar último elemento */
  focusLast: () => void;
  /** Função para focar próximo elemento */
  focusNext: () => void;
  /** Função para focar elemento anterior */
  focusPrevious: () => void;
  /** Função para restaurar foco anterior */
  restoreFocus: () => void;
  /** Função para limpar histórico de foco */
  clearFocusHistory: () => void;
  /** Estado do focus trap */
  isTrapActive: boolean;
  /** Elemento atualmente focado */
  currentFocus: HTMLElement | null;
  /** Histórico de foco */
  focusHistory: FocusHistory;
  /** Função para obter elementos focáveis */
  getFocusableElements: () => HTMLElement[];
  /** Função para verificar se elemento é focável */
  isFocusable: (element: HTMLElement) => boolean;
  /** Função para adicionar elemento ao histórico */
  addToHistory: (element: HTMLElement) => void;
}

/**
 * Hook principal de gerenciamento de foco
 */
export const useFocus = (containerRef?: React.RefObject<HTMLElement>): FocusReturn => {
  const [isTrapActive, setIsTrapActive] = useState(false);
  const [currentFocus, setCurrentFocus] = useState<HTMLElement | null>(null);
  const [focusHistory, setFocusHistory] = useState<FocusHistory>({
    elements: [],
    timestamps: [],
    maxSize: 10
  });

  const trapRef = useRef<{
    enabled: boolean;
    initialFocus: HTMLElement | null;
    returnFocus: HTMLElement | null;
    restoreFocus: boolean;
    autoFocus: boolean;
    allowOutsideFocus: boolean;
  }>({
    enabled: false,
    initialFocus: null,
    returnFocus: null,
    restoreFocus: true,
    autoFocus: true,
    allowOutsideFocus: false
  });

  const focusableElementsRef = useRef<HTMLElement[]>([]);
  const previousFocusRef = useRef<HTMLElement | null>(null);

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
   * Verifica se elemento é focável
   */
  const isFocusable = useCallback((element: HTMLElement): boolean => {
    if (!element) return false;

    const style = window.getComputedStyle(element);
    const isVisible = style.display !== 'none' && 
                     style.visibility !== 'hidden' && 
                     style.opacity !== '0';
    
    const isEnabled = !element.hasAttribute('disabled') && 
                     !element.hasAttribute('aria-disabled');
    
    const isAccessible = !element.hasAttribute('aria-hidden');

    return isVisible && isEnabled && isAccessible;
  }, []);

  /**
   * Atualiza lista de elementos focáveis
   */
  const updateFocusableElements = useCallback(() => {
    const elements = getFocusableElements().filter(isFocusable);
    focusableElementsRef.current = elements;
  }, [getFocusableElements, isFocusable]);

  /**
   * Adiciona elemento ao histórico de foco
   */
  const addToHistory = useCallback((element: HTMLElement): void => {
    if (!element) return;

    setFocusHistory(prev => {
      const newElements = [...prev.elements, element];
      const newTimestamps = [...prev.timestamps, Date.now()];

      // Remove elementos antigos se exceder o tamanho máximo
      if (newElements.length > prev.maxSize) {
        newElements.shift();
        newTimestamps.shift();
      }

      return {
        ...prev,
        elements: newElements,
        timestamps: newTimestamps
      };
    });
  }, []);

  /**
   * Foca elemento específico
   */
  const focusElement = useCallback((element: HTMLElement): void => {
    if (!element || !isFocusable(element)) return;

    // Salva foco anterior
    if (document.activeElement instanceof HTMLElement) {
      previousFocusRef.current = document.activeElement;
    }

    // Foca no elemento
    element.focus();
    setCurrentFocus(element);
    addToHistory(element);

    // Anuncia mudança de foco para screen readers
    const label = element.getAttribute('aria-label') || 
                  element.getAttribute('title') || 
                  element.textContent?.trim();
    
    if (label) {
      const announcement = document.createElement('div');
      announcement.setAttribute('aria-live', 'polite');
      announcement.setAttribute('aria-atomic', 'true');
      announcement.style.position = 'absolute';
      announcement.style.left = '-10000px';
      announcement.style.width = '1px';
      announcement.style.height = '1px';
      announcement.style.overflow = 'hidden';
      
      document.body.appendChild(announcement);
      announcement.textContent = `Focado em ${label}`;
      
      setTimeout(() => {
        if (document.body.contains(announcement)) {
          document.body.removeChild(announcement);
        }
      }, 1000);
    }
  }, [isFocusable, addToHistory]);

  /**
   * Foca primeiro elemento
   */
  const focusFirst = useCallback((): void => {
    const elements = focusableElementsRef.current;
    if (elements.length > 0) {
      focusElement(elements[0]);
    }
  }, [focusElement]);

  /**
   * Foca último elemento
   */
  const focusLast = useCallback((): void => {
    const elements = focusableElementsRef.current;
    if (elements.length > 0) {
      focusElement(elements[elements.length - 1]);
    }
  }, [focusElement]);

  /**
   * Foca próximo elemento
   */
  const focusNext = useCallback((): void => {
    const elements = focusableElementsRef.current;
    if (elements.length === 0) return;

    const currentIndex = currentFocus ? elements.indexOf(currentFocus) : -1;
    const nextIndex = currentIndex < elements.length - 1 ? currentIndex + 1 : 0;
    
    focusElement(elements[nextIndex]);
  }, [currentFocus, focusElement]);

  /**
   * Foca elemento anterior
   */
  const focusPrevious = useCallback((): void => {
    const elements = focusableElementsRef.current;
    if (elements.length === 0) return;

    const currentIndex = currentFocus ? elements.indexOf(currentFocus) : -1;
    const prevIndex = currentIndex > 0 ? currentIndex - 1 : elements.length - 1;
    
    focusElement(elements[prevIndex]);
  }, [currentFocus, focusElement]);

  /**
   * Restaura foco anterior
   */
  const restoreFocus = useCallback((): void => {
    if (previousFocusRef.current && isFocusable(previousFocusRef.current)) {
      focusElement(previousFocusRef.current);
    }
  }, [focusElement, isFocusable]);

  /**
   * Limpa histórico de foco
   */
  const clearFocusHistory = useCallback((): void => {
    setFocusHistory(prev => ({
      ...prev,
      elements: [],
      timestamps: []
    }));
  }, []);

  /**
   * Ativa focus trap
   */
  const activateFocusTrap = useCallback((options: FocusTrapOptions = {}): void => {
    const {
      enabled = true,
      initialFocus = null,
      returnFocus = document.activeElement as HTMLElement,
      restoreFocus = true,
      autoFocus = true,
      allowOutsideFocus = false
    } = options;

    // Salva foco atual
    if (document.activeElement instanceof HTMLElement) {
      previousFocusRef.current = document.activeElement;
    }

    // Atualiza configurações do trap
    trapRef.current = {
      enabled,
      initialFocus,
      returnFocus,
      restoreFocus,
      autoFocus,
      allowOutsideFocus
    };

    // Atualiza elementos focáveis
    updateFocusableElements();

    // Ativa o trap
    setIsTrapActive(true);

    // Foca elemento inicial ou primeiro elemento
    if (enabled) {
      if (initialFocus && isFocusable(initialFocus)) {
        focusElement(initialFocus);
      } else if (autoFocus) {
        focusFirst();
      }
    }
  }, [updateFocusableElements, isFocusable, focusElement, focusFirst]);

  /**
   * Desativa focus trap
   */
  const deactivateFocusTrap = useCallback((): void => {
    setIsTrapActive(false);
    setCurrentFocus(null);

    // Restaura foco se configurado
    if (trapRef.current.restoreFocus && previousFocusRef.current) {
      if (isFocusable(previousFocusRef.current)) {
        focusElement(previousFocusRef.current);
      } else if (trapRef.current.returnFocus && isFocusable(trapRef.current.returnFocus)) {
        focusElement(trapRef.current.returnFocus);
      }
    }

    // Limpa configurações
    trapRef.current = {
      enabled: false,
      initialFocus: null,
      returnFocus: null,
      restoreFocus: true,
      autoFocus: true,
      allowOutsideFocus: false
    };
  }, [isFocusable, focusElement]);

  /**
   * Handler para eventos de foco
   */
  const handleFocusIn = useCallback((event: FocusEvent): void => {
    const target = event.target as HTMLElement;
    
    if (!target) return;

    // Atualiza foco atual
    setCurrentFocus(target);
    addToHistory(target);

    // Se trap está ativo, verifica se foco está dentro do container
    if (isTrapActive && trapRef.current.enabled && !trapRef.current.allowOutsideFocus) {
      const container = containerRef?.current;
      if (container && !container.contains(target)) {
        // Foca primeiro elemento do container
        focusFirst();
      }
    }
  }, [isTrapActive, addToHistory, containerRef, focusFirst]);

  /**
   * Handler para eventos de teclado
   */
  const handleKeyDown = useCallback((event: KeyboardEvent): void => {
    if (!isTrapActive || !trapRef.current.enabled) return;

    const { key, shiftKey } = event;

    switch (key) {
      case 'Tab':
        event.preventDefault();
        if (shiftKey) {
          focusPrevious();
        } else {
          focusNext();
        }
        break;
      case 'Escape':
        if (trapRef.current.allowOutsideFocus) {
          deactivateFocusTrap();
        }
        break;
    }
  }, [isTrapActive, focusPrevious, focusNext, deactivateFocusTrap]);

  // Efeitos
  useEffect(() => {
    updateFocusableElements();
    
    const container = containerRef?.current || document;
    container.addEventListener('focusin', handleFocusIn);
    container.addEventListener('keydown', handleKeyDown);
    
    // Observa mudanças no DOM
    const observer = new MutationObserver(updateFocusableElements);
    observer.observe(container, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['style', 'aria-hidden', 'tabindex', 'disabled']
    });

    return () => {
      container.removeEventListener('focusin', handleFocusIn);
      container.removeEventListener('keydown', handleKeyDown);
      observer.disconnect();
    };
  }, [containerRef, handleFocusIn, handleKeyDown, updateFocusableElements]);

  return {
    activateFocusTrap,
    deactivateFocusTrap,
    focusElement,
    focusFirst,
    focusLast,
    focusNext,
    focusPrevious,
    restoreFocus,
    clearFocusHistory,
    isTrapActive,
    currentFocus,
    focusHistory,
    getFocusableElements,
    isFocusable,
    addToHistory
  };
};

/**
 * Hook para focus trap simples
 */
export const useFocusTrap = (containerRef: React.RefObject<HTMLElement>) => {
  const { activateFocusTrap, deactivateFocusTrap, isTrapActive } = useFocus(containerRef);

  return {
    activate: activateFocusTrap,
    deactivate: deactivateFocusTrap,
    isActive: isTrapActive
  };
};

/**
 * Hook para gerenciar foco em modais
 */
export const useModalFocus = (modalRef: React.RefObject<HTMLElement>) => {
  const { activateFocusTrap, deactivateFocusTrap, focusFirst, focusLast } = useFocus(modalRef);

  const openModal = useCallback((initialFocus?: HTMLElement) => {
    activateFocusTrap({
      enabled: true,
      initialFocus,
      autoFocus: !initialFocus,
      allowOutsideFocus: false
    });
  }, [activateFocusTrap]);

  const closeModal = useCallback(() => {
    deactivateFocusTrap();
  }, [deactivateFocusTrap]);

  return {
    openModal,
    closeModal,
    focusFirst,
    focusLast
  };
};

/**
 * Hook para gerenciar foco em dropdowns
 */
export const useDropdownFocus = (dropdownRef: React.RefObject<HTMLElement>) => {
  const { activateFocusTrap, deactivateFocusTrap, focusNext, focusPrevious } = useFocus(dropdownRef);

  const openDropdown = useCallback(() => {
    activateFocusTrap({
      enabled: true,
      autoFocus: true,
      allowOutsideFocus: true
    });
  }, [activateFocusTrap]);

  const closeDropdown = useCallback(() => {
    deactivateFocusTrap();
  }, [deactivateFocusTrap]);

  return {
    openDropdown,
    closeDropdown,
    focusNext,
    focusPrevious
  };
};

export default useFocus; 