/**
 * KeyboardNavigation - Componente para gerenciar navegação por teclado
 * 
 * Prompt: Implementação de ARIA labels para Criticalidade 3.2.1
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { createContext, useContext, useRef, useEffect, useState } from 'react';
import { Box } from '@mui/material';

interface FocusableElement {
  id: string;
  element: HTMLElement;
  tabIndex: number;
  priority: number;
}

interface KeyboardNavigationContextType {
  registerElement: (id: string, element: HTMLElement, tabIndex?: number, priority?: number) => void;
  unregisterElement: (id: string) => void;
  focusElement: (id: string) => void;
  focusNext: () => void;
  focusPrevious: () => void;
  focusFirst: () => void;
  focusLast: () => void;
  getFocusableElements: () => FocusableElement[];
  setFocusTrap: (enabled: boolean) => void;
}

const KeyboardNavigationContext = createContext<KeyboardNavigationContextType | undefined>(undefined);

interface KeyboardNavigationProviderProps {
  children: React.ReactNode;
  enableFocusTrap?: boolean;
  enableArrowKeys?: boolean;
  enableTabNavigation?: boolean;
  enableEscapeKey?: boolean;
  onEscape?: () => void;
}

export const KeyboardNavigationProvider: React.FC<KeyboardNavigationProviderProps> = ({
  children,
  enableFocusTrap = false,
  enableArrowKeys = true,
  enableTabNavigation = true,
  enableEscapeKey = true,
  onEscape
}) => {
  const [focusableElements, setFocusableElements] = useState<Map<string, FocusableElement>>(new Map());
  const [focusTrapEnabled, setFocusTrapEnabled] = useState(enableFocusTrap);
  const containerRef = useRef<HTMLDivElement>(null);

  const registerElement = (id: string, element: HTMLElement, tabIndex = 0, priority = 0) => {
    setFocusableElements(prev => {
      const newMap = new Map(prev);
      newMap.set(id, { id, element, tabIndex, priority });
      return newMap;
    });
  };

  const unregisterElement = (id: string) => {
    setFocusableElements(prev => {
      const newMap = new Map(prev);
      newMap.delete(id);
      return newMap;
    });
  };

  const getSortedElements = (): FocusableElement[] => {
    return Array.from(focusableElements.values())
      .filter(el => el.element.offsetParent !== null) // Apenas elementos visíveis
      .sort((a, b) => {
        // Ordenar por prioridade primeiro, depois por tabIndex
        if (a.priority !== b.priority) {
          return b.priority - a.priority;
        }
        return a.tabIndex - b.tabIndex;
      });
  };

  const focusElement = (id: string) => {
    const element = focusableElements.get(id);
    if (element && element.element) {
      element.element.focus();
    }
  };

  const focusNext = () => {
    const elements = getSortedElements();
    const currentIndex = elements.findIndex(el => el.element === document.activeElement);
    const nextIndex = currentIndex < elements.length - 1 ? currentIndex + 1 : 0;
    
    if (elements[nextIndex]) {
      elements[nextIndex].element.focus();
    }
  };

  const focusPrevious = () => {
    const elements = getSortedElements();
    const currentIndex = elements.findIndex(el => el.element === document.activeElement);
    const prevIndex = currentIndex > 0 ? currentIndex - 1 : elements.length - 1;
    
    if (elements[prevIndex]) {
      elements[prevIndex].element.focus();
    }
  };

  const focusFirst = () => {
    const elements = getSortedElements();
    if (elements[0]) {
      elements[0].element.focus();
    }
  };

  const focusLast = () => {
    const elements = getSortedElements();
    if (elements[elements.length - 1]) {
      elements[elements.length - 1].element.focus();
    }
  };

  const getFocusableElements = (): FocusableElement[] => {
    return getSortedElements();
  };

  const setFocusTrap = (enabled: boolean) => {
    setFocusTrapEnabled(enabled);
  };

  // Keyboard event handler
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const { key, ctrlKey, shiftKey, altKey } = event;

      // Ignorar se estiver em um input ou textarea
      const target = event.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.contentEditable === 'true') {
        return;
      }

      // Escape key
      if (enableEscapeKey && key === 'Escape') {
        event.preventDefault();
        onEscape?.();
        return;
      }

      // Arrow keys navigation
      if (enableArrowKeys && !ctrlKey && !shiftKey && !altKey) {
        switch (key) {
          case 'ArrowDown':
          case 'ArrowRight':
            event.preventDefault();
            focusNext();
            return;
          case 'ArrowUp':
          case 'ArrowLeft':
            event.preventDefault();
            focusPrevious();
            return;
          case 'Home':
            event.preventDefault();
            focusFirst();
            return;
          case 'End':
            event.preventDefault();
            focusLast();
            return;
        }
      }

      // Tab navigation with focus trap
      if (enableTabNavigation && key === 'Tab' && focusTrapEnabled) {
        const elements = getSortedElements();
        if (elements.length === 0) return;

        const firstElement = elements[0];
        const lastElement = elements[elements.length - 1];

        if (shiftKey) {
          // Shift + Tab: navegar para trás
          if (document.activeElement === firstElement.element) {
            event.preventDefault();
            lastElement.element.focus();
          }
        } else {
          // Tab: navegar para frente
          if (document.activeElement === lastElement.element) {
            event.preventDefault();
            firstElement.element.focus();
          }
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [focusTrapEnabled, enableArrowKeys, enableTabNavigation, enableEscapeKey, onEscape, focusableElements]);

  const contextValue: KeyboardNavigationContextType = {
    registerElement,
    unregisterElement,
    focusElement,
    focusNext,
    focusPrevious,
    focusFirst,
    focusLast,
    getFocusableElements,
    setFocusTrap
  };

  return (
    <KeyboardNavigationContext.Provider value={contextValue}>
      <Box ref={containerRef}>
        {children}
      </Box>
    </KeyboardNavigationContext.Provider>
  );
};

// Hook para usar navegação por teclado
export const useKeyboardNavigation = () => {
  const context = useContext(KeyboardNavigationContext);
  if (!context) {
    throw new Error('useKeyboardNavigation must be used within a KeyboardNavigationProvider');
  }
  return context;
};

// Hook para registrar elemento focável
export const useFocusableElement = (
  id: string,
  tabIndex: number = 0,
  priority: number = 0
) => {
  const { registerElement, unregisterElement } = useKeyboardNavigation();
  const elementRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (elementRef.current) {
      registerElement(id, elementRef.current, tabIndex, priority);
    }

    return () => {
      unregisterElement(id);
    };
  }, [id, tabIndex, priority, registerElement, unregisterElement]);

  return elementRef;
};

// Componente para área focável
interface FocusableAreaProps {
  children: React.ReactNode;
  id: string;
  tabIndex?: number;
  priority?: number;
  onFocus?: () => void;
  onBlur?: () => void;
  className?: string;
}

export const FocusableArea: React.FC<FocusableAreaProps> = ({
  children,
  id,
  tabIndex = 0,
  priority = 0,
  onFocus,
  onBlur,
  className
}) => {
  const elementRef = useFocusableElement(id, tabIndex, priority);

  return (
    <Box
      ref={elementRef}
      tabIndex={tabIndex}
      onFocus={onFocus}
      onBlur={onBlur}
      className={className}
      sx={{
        outline: 'none',
        '&:focus-visible': {
          outline: '2px solid',
          outlineColor: 'primary.main',
          outlineOffset: '2px',
          borderRadius: 1
        }
      }}
    >
      {children}
    </Box>
  );
};

// Componente para skip link
interface SkipLinkProps {
  targetId: string;
  children: React.ReactNode;
  className?: string;
}

export const SkipLink: React.FC<SkipLinkProps> = ({
  targetId,
  children,
  className
}) => {
  const handleClick = (event: React.MouseEvent) => {
    event.preventDefault();
    const target = document.getElementById(targetId);
    if (target) {
      target.focus();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <Box
      component="a"
      href={`#${targetId}`}
      onClick={handleClick}
      className={className}
      sx={{
        position: 'absolute',
        top: '-40px',
        left: '6px',
        zIndex: 1000,
        padding: '8px 16px',
        backgroundColor: 'primary.main',
        color: 'primary.contrastText',
        textDecoration: 'none',
        borderRadius: 1,
        fontSize: '14px',
        fontWeight: 500,
        transition: 'top 0.3s ease',
        '&:focus': {
          top: '6px',
          outline: '2px solid',
          outlineColor: 'primary.contrastText',
          outlineOffset: '2px'
        },
        '@media (prefers-reduced-motion: reduce)': {
          transition: 'none'
        }
      }}
    >
      {children}
    </Box>
  );
};

// Componente para focus trap
interface FocusTrapProps {
  children: React.ReactNode;
  enabled?: boolean;
  onEscape?: () => void;
}

export const FocusTrap: React.FC<FocusTrapProps> = ({
  children,
  enabled = true,
  onEscape
}) => {
  const { setFocusTrap } = useKeyboardNavigation();

  useEffect(() => {
    setFocusTrap(enabled);
  }, [enabled, setFocusTrap]);

  return <>{children}</>;
};

export default KeyboardNavigationProvider; 