import { useState, useEffect, useRef, useCallback } from 'react';

export interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  metaKey?: boolean;
  action: () => void;
  description: string;
  preventDefault?: boolean;
}

export interface NavigationItem {
  id: string;
  element: HTMLElement;
  index: number;
}

export interface UseKeyboardNavigationReturn {
  focusedIndex: number;
  navigationItems: NavigationItem[];
  focusItem: (index: number) => void;
  focusNext: () => void;
  focusPrevious: () => void;
  focusFirst: () => void;
  focusLast: () => void;
  addShortcut: (shortcut: KeyboardShortcut) => void;
  removeShortcut: (key: string) => void;
  clearShortcuts: () => void;
  isNavigating: boolean;
}

export const useKeyboardNavigation = (
  direction: 'horizontal' | 'vertical' | 'both' = 'both',
  loop: boolean = true,
  containerRef?: React.RefObject<HTMLElement>
): UseKeyboardNavigationReturn => {
  const [focusedIndex, setFocusedIndex] = useState(0);
  const [navigationItems, setNavigationItems] = useState<NavigationItem[]>([]);
  const [shortcuts, setShortcuts] = useState<KeyboardShortcut[]>([]);
  const [isNavigating, setIsNavigating] = useState(false);

  // Find navigation items
  const findNavigationItems = useCallback(() => {
    const targetContainer = containerRef?.current || document.body;
    if (!targetContainer) return [];

    const selectors = [
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])',
      '[data-navigable="true"]'
    ];

    const elements = targetContainer.querySelectorAll(selectors.join(', '));
    return Array.from(elements).map((element, index) => ({
      id: element.id || `nav-item-${index}`,
      element: element as HTMLElement,
      index
    }));
  }, [containerRef]);

  // Update navigation items
  useEffect(() => {
    const updateItems = () => {
      const items = findNavigationItems();
      setNavigationItems(items);
    };

    updateItems();

    // Update on DOM changes
    const observer = new MutationObserver(updateItems);
    if (containerRef?.current) {
      observer.observe(containerRef.current, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['disabled', 'tabindex', 'data-navigable']
      });
    }

    return () => observer.disconnect();
  }, [findNavigationItems, containerRef]);

  // Focus management
  const focusItem = useCallback((index: number) => {
    if (index >= 0 && index < navigationItems.length) {
      navigationItems[index].element.focus();
      setFocusedIndex(index);
      setIsNavigating(true);
      
      // Reset navigation state after a short delay
      setTimeout(() => setIsNavigating(false), 100);
    }
  }, [navigationItems]);

  const focusNext = useCallback(() => {
    if (navigationItems.length === 0) return;

    const nextIndex = focusedIndex < navigationItems.length - 1 
      ? focusedIndex + 1 
      : (loop ? 0 : focusedIndex);
    
    focusItem(nextIndex);
  }, [navigationItems.length, focusedIndex, loop, focusItem]);

  const focusPrevious = useCallback(() => {
    if (navigationItems.length === 0) return;

    const prevIndex = focusedIndex > 0 
      ? focusedIndex - 1 
      : (loop ? navigationItems.length - 1 : focusedIndex);
    
    focusItem(prevIndex);
  }, [navigationItems.length, focusedIndex, loop, focusItem]);

  const focusFirst = useCallback(() => {
    if (navigationItems.length > 0) {
      focusItem(0);
    }
  }, [navigationItems.length, focusItem]);

  const focusLast = useCallback(() => {
    if (navigationItems.length > 0) {
      focusItem(navigationItems.length - 1);
    }
  }, [navigationItems.length, focusItem]);

  // Shortcut management
  const addShortcut = useCallback((shortcut: KeyboardShortcut) => {
    setShortcuts(prev => [...prev, shortcut]);
  }, []);

  const removeShortcut = useCallback((key: string) => {
    setShortcuts(prev => prev.filter(shortcut => shortcut.key !== key));
  }, []);

  const clearShortcuts = useCallback(() => {
    setShortcuts([]);
  }, []);

  // Handle keyboard events
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    const { key, ctrlKey, shiftKey, altKey, metaKey } = event;

    // Check shortcuts first
    const pressedShortcut = shortcuts.find(shortcut => {
      return (
        event.key.toLowerCase() === shortcut.key.toLowerCase() &&
        !!ctrlKey === !!shortcut.ctrlKey &&
        !!shiftKey === !!shortcut.shiftKey &&
        !!altKey === !!shortcut.altKey &&
        !!metaKey === !!shortcut.metaKey
      );
    });

    if (pressedShortcut) {
      if (pressedShortcut.preventDefault !== false) {
        event.preventDefault();
      }
      pressedShortcut.action();
      return;
    }

    // Handle navigation keys
    switch (key) {
      case 'ArrowUp':
        if (direction === 'vertical' || direction === 'both') {
          event.preventDefault();
          focusPrevious();
        }
        break;

      case 'ArrowDown':
        if (direction === 'vertical' || direction === 'both') {
          event.preventDefault();
          focusNext();
        }
        break;

      case 'ArrowLeft':
        if (direction === 'horizontal' || direction === 'both') {
          event.preventDefault();
          focusPrevious();
        }
        break;

      case 'ArrowRight':
        if (direction === 'horizontal' || direction === 'both') {
          event.preventDefault();
          focusNext();
        }
        break;

      case 'Home':
        event.preventDefault();
        focusFirst();
        break;

      case 'End':
        event.preventDefault();
        focusLast();
        break;

      case 'PageUp':
        event.preventDefault();
        // Jump 10 items up
        const pageUpIndex = Math.max(0, focusedIndex - 10);
        focusItem(pageUpIndex);
        break;

      case 'PageDown':
        event.preventDefault();
        // Jump 10 items down
        const pageDownIndex = Math.min(navigationItems.length - 1, focusedIndex + 10);
        focusItem(pageDownIndex);
        break;
    }
  }, [direction, focusPrevious, focusNext, focusFirst, focusLast, focusItem, focusedIndex, navigationItems.length, shortcuts]);

  // Set up event listeners
  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return {
    focusedIndex,
    navigationItems,
    focusItem,
    focusNext,
    focusPrevious,
    focusFirst,
    focusLast,
    addShortcut,
    removeShortcut,
    clearShortcuts,
    isNavigating
  };
};

// Specialized navigation hooks
export const useArrowKeyNavigation = (direction: 'horizontal' | 'vertical' | 'both' = 'both') => {
  const [focusedIndex, setFocusedIndex] = useState(0);
  const [items, setItems] = useState<NavigationItem[]>([]);

  const findItems = useCallback(() => {
    const selectors = [
      'button:not([disabled])',
      'input:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])'
    ];

    const elements = document.querySelectorAll(selectors.join(', '));
    return Array.from(elements).map((element, index) => ({
      id: element.id || `nav-${index}`,
      element: element as HTMLElement,
      index
    }));
  }, []);

  useEffect(() => {
    setItems(findItems());
  }, [findItems]);

  const focusItem = useCallback((index: number) => {
    if (index >= 0 && index < items.length) {
      items[index].element.focus();
      setFocusedIndex(index);
    }
  }, [items]);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    switch (event.key) {
      case 'ArrowUp':
        if (direction === 'vertical' || direction === 'both') {
          event.preventDefault();
          const prevIndex = focusedIndex > 0 ? focusedIndex - 1 : items.length - 1;
          focusItem(prevIndex);
        }
        break;

      case 'ArrowDown':
        if (direction === 'vertical' || direction === 'both') {
          event.preventDefault();
          const nextIndex = focusedIndex < items.length - 1 ? focusedIndex + 1 : 0;
          focusItem(nextIndex);
        }
        break;

      case 'ArrowLeft':
        if (direction === 'horizontal' || direction === 'both') {
          event.preventDefault();
          const prevIndex = focusedIndex > 0 ? focusedIndex - 1 : items.length - 1;
          focusItem(prevIndex);
        }
        break;

      case 'ArrowRight':
        if (direction === 'horizontal' || direction === 'both') {
          event.preventDefault();
          const nextIndex = focusedIndex < items.length - 1 ? focusedIndex + 1 : 0;
          focusItem(nextIndex);
        }
        break;
    }
  }, [direction, focusedIndex, items.length, focusItem]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return {
    focusedIndex,
    items,
    focusItem
  };
};

export const useKeyboardShortcuts = (shortcuts: KeyboardShortcut[]) => {
  const [activeShortcuts, setActiveShortcuts] = useState<KeyboardShortcut[]>(shortcuts);

  const addShortcut = useCallback((shortcut: KeyboardShortcut) => {
    setActiveShortcuts(prev => [...prev, shortcut]);
  }, []);

  const removeShortcut = useCallback((key: string) => {
    setActiveShortcuts(prev => prev.filter(s => s.key !== key));
  }, []);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    const { key, ctrlKey, shiftKey, altKey, metaKey } = event;

    const pressedShortcut = activeShortcuts.find(shortcut => {
      return (
        event.key.toLowerCase() === shortcut.key.toLowerCase() &&
        !!ctrlKey === !!shortcut.ctrlKey &&
        !!shiftKey === !!shortcut.shiftKey &&
        !!altKey === !!shortcut.altKey &&
        !!metaKey === !!shortcut.metaKey
      );
    });

    if (pressedShortcut) {
      if (pressedShortcut.preventDefault !== false) {
        event.preventDefault();
      }
      pressedShortcut.action();
    }
  }, [activeShortcuts]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return {
    addShortcut,
    removeShortcut,
    shortcuts: activeShortcuts
  };
}; 