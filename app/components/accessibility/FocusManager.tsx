import React, { useState, useEffect, useRef, useCallback } from 'react';

export interface FocusManagerProps {
  children: React.ReactNode;
  autoFocus?: boolean;
  restoreFocus?: boolean;
  trapFocus?: boolean;
  onFocusChange?: (element: HTMLElement | null) => void;
  className?: string;
}

export interface FocusHistory {
  element: HTMLElement;
  timestamp: number;
}

export const FocusManager: React.FC<FocusManagerProps> = ({
  children,
  autoFocus = false,
  restoreFocus = true,
  trapFocus = false,
  onFocusChange,
  className = ''
}) => {
  const [focusHistory, setFocusHistory] = useState<FocusHistory[]>([]);
  const [currentFocus, setCurrentFocus] = useState<HTMLElement | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  // Find focusable elements within the container
  const findFocusableElements = useCallback(() => {
    if (!containerRef.current) return [];

    const focusableSelectors = [
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])',
      '[contenteditable="true"]'
    ];

    return Array.from(containerRef.current.querySelectorAll(focusableSelectors.join(', '))) as HTMLElement[];
  }, []);

  // Focus management functions
  const focusElement = useCallback((element: HTMLElement) => {
    element.focus();
    setCurrentFocus(element);
    onFocusChange?.(element);
  }, [onFocusChange]);

  const focusFirstElement = useCallback(() => {
    const focusableElements = findFocusableElements();
    if (focusableElements.length > 0) {
      focusElement(focusableElements[0]);
    }
  }, [findFocusableElements, focusElement]);

  const focusLastElement = useCallback(() => {
    const focusableElements = findFocusableElements();
    if (focusableElements.length > 0) {
      focusElement(focusableElements[focusableElements.length - 1]);
    }
  }, [findFocusableElements, focusElement]);

  const focusNextElement = useCallback(() => {
    const focusableElements = findFocusableElements();
    if (focusableElements.length === 0) return;

    const currentIndex = focusableElements.indexOf(currentFocus!);
    const nextIndex = currentIndex < focusableElements.length - 1 ? currentIndex + 1 : 0;
    focusElement(focusableElements[nextIndex]);
  }, [findFocusableElements, currentFocus, focusElement]);

  const focusPreviousElement = useCallback(() => {
    const focusableElements = findFocusableElements();
    if (focusableElements.length === 0) return;

    const currentIndex = focusableElements.indexOf(currentFocus!);
    const prevIndex = currentIndex > 0 ? currentIndex - 1 : focusableElements.length - 1;
    focusElement(focusableElements[prevIndex]);
  }, [findFocusableElements, currentFocus, focusElement]);

  // Save focus history
  const saveFocus = useCallback((element: HTMLElement) => {
    setFocusHistory(prev => [
      ...prev.filter(item => item.element !== element),
      { element, timestamp: Date.now() }
    ].slice(-10)); // Keep last 10 focus events
  }, []);

  // Restore previous focus
  const restorePreviousFocus = useCallback(() => {
    if (previousFocusRef.current) {
      previousFocusRef.current.focus();
    }
  }, []);

  // Handle focus events
  const handleFocusIn = useCallback((event: FocusEvent) => {
    const target = event.target as HTMLElement;
    if (containerRef.current?.contains(target)) {
      setCurrentFocus(target);
      saveFocus(target);
      onFocusChange?.(target);
    }
  }, [saveFocus, onFocusChange]);

  const handleFocusOut = useCallback((event: FocusEvent) => {
    const target = event.target as HTMLElement;
    if (containerRef.current?.contains(target)) {
      setCurrentFocus(null);
      onFocusChange?.(null);
    }
  }, [onFocusChange]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!trapFocus) return;

    switch (event.key) {
      case 'Tab':
        if (event.shiftKey) {
          // Shift + Tab
          event.preventDefault();
          focusPreviousElement();
        } else {
          // Tab
          event.preventDefault();
          focusNextElement();
        }
        break;

      case 'Escape':
        if (restoreFocus) {
          restorePreviousFocus();
        }
        break;
    }
  }, [trapFocus, focusPreviousElement, focusNextElement, restoreFocus, restorePreviousFocus]);

  // Initialize focus management
  useEffect(() => {
    // Save the currently focused element before mounting
    previousFocusRef.current = document.activeElement as HTMLElement;

    // Auto-focus first element if enabled
    if (autoFocus) {
      setTimeout(focusFirstElement, 0);
    }

    // Add event listeners
    document.addEventListener('focusin', handleFocusIn);
    document.addEventListener('focusout', handleFocusOut);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('focusin', handleFocusIn);
      document.removeEventListener('focusout', handleFocusOut);
      document.removeEventListener('keydown', handleKeyDown);

      // Restore focus on unmount if enabled
      if (restoreFocus && previousFocusRef.current) {
        previousFocusRef.current.focus();
      }
    };
  }, [autoFocus, focusFirstElement, handleFocusIn, handleFocusOut, handleKeyDown, restoreFocus]);

  return (
    <div
      ref={containerRef}
      className={className}
      role={trapFocus ? 'dialog' : undefined}
      aria-modal={trapFocus ? 'true' : undefined}
    >
      {children}
    </div>
  );
};

// Focus Indicator Component
export interface FocusIndicatorProps {
  children: React.ReactNode;
  style?: 'outline' | 'ring' | 'highlight' | 'custom';
  color?: string;
  width?: number;
  className?: string;
}

export const FocusIndicator: React.FC<FocusIndicatorProps> = ({
  children,
  style = 'ring',
  color = '#2196f3',
  width = 2,
  className = ''
}) => {
  const getFocusStyles = () => {
    switch (style) {
      case 'outline':
        return {
          outline: `${width}px solid ${color}`,
          outlineOffset: '2px'
        };
      case 'ring':
        return {
          boxShadow: `0 0 0 ${width}px ${color}`,
          outline: 'none'
        };
      case 'highlight':
        return {
          backgroundColor: `${color}20`,
          border: `${width}px solid ${color}`,
          outline: 'none'
        };
      default:
        return {};
    }
  };

  return (
    <div
      className={`focus-indicator ${className}`}
      style={{
        ...getFocusStyles(),
        transition: 'all 0.2s ease-in-out'
      }}
    >
      {children}
    </div>
  );
};

// Focus Group Component
export interface FocusGroupProps {
  children: React.ReactNode;
  direction?: 'horizontal' | 'vertical' | 'both';
  loop?: boolean;
  onFocusChange?: (element: HTMLElement | null) => void;
  className?: string;
}

export const FocusGroup: React.FC<FocusGroupProps> = ({
  children,
  direction = 'both',
  loop = true,
  onFocusChange,
  className = ''
}) => {
  const [focusedElement, setFocusedElement] = useState<HTMLElement | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const findFocusableElements = useCallback(() => {
    if (!containerRef.current) return [];

    const focusableSelectors = [
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])',
      '[contenteditable="true"]'
    ];

    return Array.from(containerRef.current.querySelectorAll(focusableSelectors.join(', '))) as HTMLElement[];
  }, []);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    const focusableElements = findFocusableElements();
    if (focusableElements.length === 0) return;

    const currentIndex = focusedElement ? focusableElements.indexOf(focusedElement) : -1;
    let nextIndex = -1;

    switch (event.key) {
      case 'ArrowUp':
        if (direction === 'vertical' || direction === 'both') {
          event.preventDefault();
          nextIndex = currentIndex > 0 ? currentIndex - 1 : (loop ? focusableElements.length - 1 : 0);
        }
        break;

      case 'ArrowDown':
        if (direction === 'vertical' || direction === 'both') {
          event.preventDefault();
          nextIndex = currentIndex < focusableElements.length - 1 ? currentIndex + 1 : (loop ? 0 : focusableElements.length - 1);
        }
        break;

      case 'ArrowLeft':
        if (direction === 'horizontal' || direction === 'both') {
          event.preventDefault();
          nextIndex = currentIndex > 0 ? currentIndex - 1 : (loop ? focusableElements.length - 1 : 0);
        }
        break;

      case 'ArrowRight':
        if (direction === 'horizontal' || direction === 'both') {
          event.preventDefault();
          nextIndex = currentIndex < focusableElements.length - 1 ? currentIndex + 1 : (loop ? 0 : focusableElements.length - 1);
        }
        break;
    }

    if (nextIndex >= 0 && nextIndex < focusableElements.length) {
      focusableElements[nextIndex].focus();
      setFocusedElement(focusableElements[nextIndex]);
      onFocusChange?.(focusableElements[nextIndex]);
    }
  }, [direction, loop, focusedElement, findFocusableElements, onFocusChange]);

  const handleFocusIn = useCallback((event: FocusEvent) => {
    const target = event.target as HTMLElement;
    if (containerRef.current?.contains(target)) {
      setFocusedElement(target);
      onFocusChange?.(target);
    }
  }, [onFocusChange]);

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.addEventListener('keydown', handleKeyDown);
      container.addEventListener('focusin', handleFocusIn);
      return () => {
        container.removeEventListener('keydown', handleKeyDown);
        container.removeEventListener('focusin', handleFocusIn);
      };
    }
  }, [handleKeyDown, handleFocusIn]);

  return (
    <div
      ref={containerRef}
      className={`focus-group ${className}`}
      role="group"
    >
      {children}
    </div>
  );
}; 