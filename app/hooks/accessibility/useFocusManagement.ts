import { useState, useEffect, useRef, useCallback } from 'react';

export interface FocusElement {
  id: string;
  element: HTMLElement;
  index: number;
}

export interface FocusHistory {
  element: HTMLElement;
  timestamp: number;
}

export interface UseFocusManagementReturn {
  focusedElement: HTMLElement | null;
  focusHistory: FocusHistory[];
  focusableElements: FocusElement[];
  focusElement: (element: HTMLElement) => void;
  focusFirst: () => void;
  focusLast: () => void;
  focusNext: () => void;
  focusPrevious: () => void;
  focusById: (id: string) => void;
  focusByIndex: (index: number) => void;
  saveFocus: () => void;
  restoreFocus: () => void;
  clearHistory: () => void;
  trapFocus: (container: HTMLElement) => void;
  releaseFocus: () => void;
}

export const useFocusManagement = (
  containerRef?: React.RefObject<HTMLElement>
): UseFocusManagementReturn => {
  const [focusedElement, setFocusedElement] = useState<HTMLElement | null>(null);
  const [focusHistory, setFocusHistory] = useState<FocusHistory[]>([]);
  const [focusableElements, setFocusableElements] = useState<FocusElement[]>([]);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const trappedContainerRef = useRef<HTMLElement | null>(null);

  // Find focusable elements
  const findFocusableElements = useCallback((container?: HTMLElement) => {
    const targetContainer = container || containerRef?.current || document.body;
    if (!targetContainer) return [];

    const focusableSelectors = [
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])',
      '[contenteditable="true"]'
    ];

    const elements = targetContainer.querySelectorAll(focusableSelectors.join(', '));
    return Array.from(elements).map((element, index) => ({
      id: element.id || `focusable-${index}`,
      element: element as HTMLElement,
      index
    }));
  }, [containerRef]);

  // Update focusable elements
  useEffect(() => {
    const updateFocusableElements = () => {
      const elements = findFocusableElements();
      setFocusableElements(elements);
    };

    updateFocusableElements();

    // Update on DOM changes
    const observer = new MutationObserver(updateFocusableElements);
    if (containerRef?.current) {
      observer.observe(containerRef.current, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['disabled', 'tabindex']
      });
    }

    return () => observer.disconnect();
  }, [findFocusableElements, containerRef]);

  // Focus management functions
  const focusElement = useCallback((element: HTMLElement) => {
    element.focus();
    setFocusedElement(element);
  }, []);

  const focusFirst = useCallback(() => {
    if (focusableElements.length > 0) {
      focusElement(focusableElements[0].element);
    }
  }, [focusableElements, focusElement]);

  const focusLast = useCallback(() => {
    if (focusableElements.length > 0) {
      focusElement(focusableElements[focusableElements.length - 1].element);
    }
  }, [focusableElements, focusElement]);

  const focusNext = useCallback(() => {
    if (focusableElements.length === 0) return;

    const currentIndex = focusedElement 
      ? focusableElements.findIndex(item => item.element === focusedElement)
      : -1;
    
    const nextIndex = currentIndex < focusableElements.length - 1 ? currentIndex + 1 : 0;
    focusElement(focusableElements[nextIndex].element);
  }, [focusableElements, focusedElement, focusElement]);

  const focusPrevious = useCallback(() => {
    if (focusableElements.length === 0) return;

    const currentIndex = focusedElement 
      ? focusableElements.findIndex(item => item.element === focusedElement)
      : -1;
    
    const prevIndex = currentIndex > 0 ? currentIndex - 1 : focusableElements.length - 1;
    focusElement(focusableElements[prevIndex].element);
  }, [focusableElements, focusedElement, focusElement]);

  const focusById = useCallback((id: string) => {
    const element = focusableElements.find(item => item.id === id);
    if (element) {
      focusElement(element.element);
    }
  }, [focusableElements, focusElement]);

  const focusByIndex = useCallback((index: number) => {
    if (index >= 0 && index < focusableElements.length) {
      focusElement(focusableElements[index].element);
    }
  }, [focusableElements, focusElement]);

  // Focus history management
  const saveFocus = useCallback(() => {
    const currentFocus = document.activeElement as HTMLElement;
    if (currentFocus) {
      previousFocusRef.current = currentFocus;
      setFocusHistory(prev => [
        ...prev.filter(item => item.element !== currentFocus),
        { element: currentFocus, timestamp: Date.now() }
      ].slice(-10)); // Keep last 10 focus events
    }
  }, []);

  const restoreFocus = useCallback(() => {
    if (previousFocusRef.current) {
      previousFocusRef.current.focus();
      setFocusedElement(previousFocusRef.current);
    }
  }, []);

  const clearHistory = useCallback(() => {
    setFocusHistory([]);
    previousFocusRef.current = null;
  }, []);

  // Focus trap management
  const trapFocus = useCallback((container: HTMLElement) => {
    trappedContainerRef.current = container;
    saveFocus();
    focusFirst();
  }, [saveFocus, focusFirst]);

  const releaseFocus = useCallback(() => {
    trappedContainerRef.current = null;
    restoreFocus();
  }, [restoreFocus]);

  // Handle focus events
  const handleFocusIn = useCallback((event: FocusEvent) => {
    const target = event.target as HTMLElement;
    
    // Check if focus is within trapped container
    if (trappedContainerRef.current && !trappedContainerRef.current.contains(target)) {
      event.preventDefault();
      focusFirst();
      return;
    }

    setFocusedElement(target);
  }, [focusFirst]);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!trappedContainerRef.current) return;

    switch (event.key) {
      case 'Tab':
        event.preventDefault();
        if (event.shiftKey) {
          focusPrevious();
        } else {
          focusNext();
        }
        break;

      case 'Escape':
        releaseFocus();
        break;
    }
  }, [focusPrevious, focusNext, releaseFocus]);

  // Set up event listeners
  useEffect(() => {
    document.addEventListener('focusin', handleFocusIn);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('focusin', handleFocusIn);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleFocusIn, handleKeyDown]);

  return {
    focusedElement,
    focusHistory,
    focusableElements,
    focusElement,
    focusFirst,
    focusLast,
    focusNext,
    focusPrevious,
    focusById,
    focusByIndex,
    saveFocus,
    restoreFocus,
    clearHistory,
    trapFocus,
    releaseFocus
  };
};

// Specialized focus hooks
export const useFocusTrap = (enabled: boolean = true) => {
  const [isTrapped, setIsTrapped] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const focusManager = useFocusManagement(containerRef);

  const trapFocus = useCallback(() => {
    if (enabled && containerRef.current) {
      focusManager.trapFocus(containerRef.current);
      setIsTrapped(true);
    }
  }, [enabled, focusManager]);

  const releaseFocus = useCallback(() => {
    focusManager.releaseFocus();
    setIsTrapped(false);
  }, [focusManager]);

  useEffect(() => {
    return () => {
      if (isTrapped) {
        releaseFocus();
      }
    };
  }, [isTrapped, releaseFocus]);

  return {
    containerRef,
    isTrapped,
    trapFocus,
    releaseFocus,
    ...focusManager
  };
};

export const useFocusRestoration = () => {
  const [savedFocus, setSavedFocus] = useState<HTMLElement | null>(null);
  const focusManager = useFocusManagement();

  const saveCurrentFocus = useCallback(() => {
    const currentFocus = document.activeElement as HTMLElement;
    if (currentFocus) {
      setSavedFocus(currentFocus);
    }
  }, []);

  const restoreSavedFocus = useCallback(() => {
    if (savedFocus) {
      savedFocus.focus();
    }
  }, [savedFocus]);

  return {
    savedFocus,
    saveCurrentFocus,
    restoreSavedFocus,
    ...focusManager
  };
};

export const useFocusNavigation = (direction: 'horizontal' | 'vertical' | 'both' = 'both') => {
  const focusManager = useFocusManagement();

  const handleKeyNavigation = useCallback((event: KeyboardEvent) => {
    switch (event.key) {
      case 'ArrowUp':
        if (direction === 'vertical' || direction === 'both') {
          event.preventDefault();
          focusManager.focusPrevious();
        }
        break;

      case 'ArrowDown':
        if (direction === 'vertical' || direction === 'both') {
          event.preventDefault();
          focusManager.focusNext();
        }
        break;

      case 'ArrowLeft':
        if (direction === 'horizontal' || direction === 'both') {
          event.preventDefault();
          focusManager.focusPrevious();
        }
        break;

      case 'ArrowRight':
        if (direction === 'horizontal' || direction === 'both') {
          event.preventDefault();
          focusManager.focusNext();
        }
        break;
    }
  }, [direction, focusManager]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyNavigation);
    return () => document.removeEventListener('keydown', handleKeyNavigation);
  }, [handleKeyNavigation]);

  return focusManager;
}; 