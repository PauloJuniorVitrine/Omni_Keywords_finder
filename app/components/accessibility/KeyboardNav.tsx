import React, { useState, useEffect, useRef, useCallback } from 'react';

export interface KeyboardNavProps {
  children: React.ReactNode;
  direction?: 'horizontal' | 'vertical' | 'both';
  loop?: boolean;
  onNavigate?: (direction: string, index: number) => void;
  onSelect?: (index: number) => void;
  onEscape?: () => void;
  className?: string;
}

export interface KeyboardNavItem {
  id: string;
  element: HTMLElement;
  index: number;
}

export const KeyboardNav: React.FC<KeyboardNavProps> = ({
  children,
  direction = 'both',
  loop = true,
  onNavigate,
  onSelect,
  onEscape,
  className = ''
}) => {
  const [focusedIndex, setFocusedIndex] = useState(0);
  const [items, setItems] = useState<KeyboardNavItem[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);

  // Find all focusable elements
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

    const elements = containerRef.current.querySelectorAll(focusableSelectors.join(', '));
    return Array.from(elements).map((element, index) => ({
      id: element.id || `nav-item-${index}`,
      element: element as HTMLElement,
      index
    }));
  }, []);

  useEffect(() => {
    setItems(findFocusableElements());
  }, [findFocusableElements]);

  // Focus management
  const focusElement = useCallback((index: number) => {
    if (items[index]) {
      items[index].element.focus();
      setFocusedIndex(index);
    }
  }, [items]);

  // Navigation handlers
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    const { key, ctrlKey, shiftKey, metaKey } = event;

    // Prevent default for navigation keys
    if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Home', 'End', 'Escape'].includes(key)) {
      event.preventDefault();
    }

    switch (key) {
      case 'ArrowUp':
        if (direction === 'vertical' || direction === 'both') {
          const newIndex = focusedIndex > 0 ? focusedIndex - 1 : (loop ? items.length - 1 : 0);
          focusElement(newIndex);
          onNavigate?.('up', newIndex);
        }
        break;

      case 'ArrowDown':
        if (direction === 'vertical' || direction === 'both') {
          const newIndex = focusedIndex < items.length - 1 ? focusedIndex + 1 : (loop ? 0 : items.length - 1);
          focusElement(newIndex);
          onNavigate?.('down', newIndex);
        }
        break;

      case 'ArrowLeft':
        if (direction === 'horizontal' || direction === 'both') {
          const newIndex = focusedIndex > 0 ? focusedIndex - 1 : (loop ? items.length - 1 : 0);
          focusElement(newIndex);
          onNavigate?.('left', newIndex);
        }
        break;

      case 'ArrowRight':
        if (direction === 'horizontal' || direction === 'both') {
          const newIndex = focusedIndex < items.length - 1 ? focusedIndex + 1 : (loop ? 0 : items.length - 1);
          focusElement(newIndex);
          onNavigate?.('right', newIndex);
        }
        break;

      case 'Home':
        focusElement(0);
        onNavigate?.('home', 0);
        break;

      case 'End':
        focusElement(items.length - 1);
        onNavigate?.('end', items.length - 1);
        break;

      case 'Enter':
      case ' ':
        onSelect?.(focusedIndex);
        break;

      case 'Escape':
        onEscape?.();
        break;
    }
  }, [direction, loop, focusedIndex, items.length, focusElement, onNavigate, onSelect, onEscape]);

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.addEventListener('keydown', handleKeyDown);
      return () => container.removeEventListener('keydown', handleKeyDown);
    }
  }, [handleKeyDown]);

  return (
    <div
      ref={containerRef}
      className={className}
      role="navigation"
      tabIndex={-1}
    >
      {children}
    </div>
  );
};

// Keyboard Navigation List Component
export interface KeyboardNavListProps {
  items: Array<{
    id: string;
    label: string;
    disabled?: boolean;
  }>;
  onSelect?: (item: any, index: number) => void;
  onNavigate?: (direction: string, index: number) => void;
  className?: string;
}

export const KeyboardNavList: React.FC<KeyboardNavListProps> = ({
  items,
  onSelect,
  onNavigate,
  className = ''
}) => {
  const [focusedIndex, setFocusedIndex] = useState(0);

  const handleKeyDown = (event: React.KeyboardEvent, index: number) => {
    switch (event.key) {
      case 'ArrowUp':
        event.preventDefault();
        const prevIndex = index > 0 ? index - 1 : items.length - 1;
        setFocusedIndex(prevIndex);
        onNavigate?.('up', prevIndex);
        break;

      case 'ArrowDown':
        event.preventDefault();
        const nextIndex = index < items.length - 1 ? index + 1 : 0;
        setFocusedIndex(nextIndex);
        onNavigate?.('down', nextIndex);
        break;

      case 'Enter':
      case ' ':
        event.preventDefault();
        onSelect?.(items[index], index);
        break;
    }
  };

  return (
    <ul
      role="listbox"
      className={className}
      aria-label="Navigation list"
    >
      {items.map((item, index) => (
        <li
          key={item.id}
          role="option"
          aria-selected={focusedIndex === index}
          tabIndex={focusedIndex === index ? 0 : -1}
          onKeyDown={(e) => handleKeyDown(e, index)}
          onClick={() => onSelect?.(item, index)}
          className={`keyboard-nav-item ${focusedIndex === index ? 'focused' : ''} ${item.disabled ? 'disabled' : ''}`}
          style={{
            padding: '8px 12px',
            cursor: item.disabled ? 'not-allowed' : 'pointer',
            backgroundColor: focusedIndex === index ? '#e3f2fd' : 'transparent',
            outline: focusedIndex === index ? '2px solid #2196f3' : 'none'
          }}
        >
          {item.label}
        </li>
      ))}
    </ul>
  );
};

// Keyboard Shortcuts Component
export interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  metaKey?: boolean;
  action: () => void;
  description: string;
}

export interface KeyboardShortcutsProps {
  shortcuts: KeyboardShortcut[];
  enabled?: boolean;
  onShortcut?: (shortcut: KeyboardShortcut) => void;
}

export const KeyboardShortcuts: React.FC<KeyboardShortcutsProps> = ({
  shortcuts,
  enabled = true,
  onShortcut
}) => {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!enabled) return;

    const pressedShortcut = shortcuts.find(shortcut => {
      return (
        event.key.toLowerCase() === shortcut.key.toLowerCase() &&
        !!event.ctrlKey === !!shortcut.ctrlKey &&
        !!event.shiftKey === !!shortcut.shiftKey &&
        !!event.altKey === !!shortcut.altKey &&
        !!event.metaKey === !!shortcut.metaKey
      );
    });

    if (pressedShortcut) {
      event.preventDefault();
      pressedShortcut.action();
      onShortcut?.(pressedShortcut);
    }
  }, [shortcuts, enabled, onShortcut]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return null; // This component doesn't render anything visible
};

// Keyboard Focus Trap Component
export interface KeyboardFocusTrapProps {
  children: React.ReactNode;
  enabled?: boolean;
  onEscape?: () => void;
  className?: string;
}

export const KeyboardFocusTrap: React.FC<KeyboardFocusTrapProps> = ({
  children,
  enabled = true,
  onEscape,
  className = ''
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const firstFocusableRef = useRef<HTMLElement | null>(null);
  const lastFocusableRef = useRef<HTMLElement | null>(null);

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

  useEffect(() => {
    if (!enabled) return;

    const focusableElements = findFocusableElements();
    if (focusableElements.length > 0) {
      firstFocusableRef.current = focusableElements[0];
      lastFocusableRef.current = focusableElements[focusableElements.length - 1];
    }
  }, [enabled, findFocusableElements]);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!enabled) return;

    if (event.key === 'Escape') {
      onEscape?.();
      return;
    }

    if (event.key === 'Tab') {
      const focusableElements = findFocusableElements();
      if (focusableElements.length === 0) return;

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (event.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement.focus();
        }
      }
    }
  }, [enabled, onEscape, findFocusableElements]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return (
    <div
      ref={containerRef}
      className={className}
      role="dialog"
      aria-modal="true"
    >
      {children}
    </div>
  );
}; 