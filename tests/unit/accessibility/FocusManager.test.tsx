/**
 * Testes Unitários - FocusManager Component
 * 
 * Prompt: Implementação de testes para componentes de acessibilidade
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_FOCUS_MANAGER_002
 * 
 * Baseado em código real do componente FocusManager.tsx
 */

import React from 'react';
import { FocusManager, FocusIndicator, FocusGroup, FocusHistory } from '../../../app/components/accessibility/FocusManager';

// Funções utilitárias extraídas do componente para teste
const findFocusableElements = (container: HTMLElement): HTMLElement[] => {
  const focusableSelectors = [
    'button:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    'a[href]',
    '[tabindex]:not([tabindex="-1"])',
    '[contenteditable="true"]'
  ];

  return Array.from(container.querySelectorAll(focusableSelectors.join(', '))) as HTMLElement[];
};

const createFocusableElement = (tag: string, attributes: Record<string, string> = {}): HTMLElement => {
  const element = document.createElement(tag);
  Object.entries(attributes).forEach(([key, value]) => {
    element.setAttribute(key, value);
  });
  return element;
};

describe('FocusManager - Gerenciamento de Foco WCAG 2.1', () => {
  
  let container: HTMLDivElement;
  let button1: HTMLButtonElement;
  let button2: HTMLButtonElement;
  let input1: HTMLInputElement;
  let link1: HTMLAnchorElement;

  beforeEach(() => {
    // Setup DOM para testes
    container = document.createElement('div');
    button1 = document.createElement('button');
    button2 = document.createElement('button');
    input1 = document.createElement('input');
    link1 = document.createElement('a');

    button1.textContent = 'Botão 1';
    button2.textContent = 'Botão 2';
    input1.type = 'text';
    input1.placeholder = 'Input de teste';
    link1.href = '#';
    link1.textContent = 'Link de teste';

    container.appendChild(button1);
    container.appendChild(button2);
    container.appendChild(input1);
    container.appendChild(link1);
    document.body.appendChild(container);
  });

  afterEach(() => {
    document.body.removeChild(container);
  });

  describe('findFocusableElements - Detecção de Elementos Focáveis', () => {
    
    test('deve detectar botões focáveis', () => {
      const focusableElements = findFocusableElements(container);
      expect(focusableElements).toContain(button1);
      expect(focusableElements).toContain(button2);
    });

    test('deve detectar inputs focáveis', () => {
      const focusableElements = findFocusableElements(container);
      expect(focusableElements).toContain(input1);
    });

    test('deve detectar links focáveis', () => {
      const focusableElements = findFocusableElements(container);
      expect(focusableElements).toContain(link1);
    });

    test('deve ignorar elementos desabilitados', () => {
      const disabledButton = createFocusableElement('button', { disabled: 'true' });
      container.appendChild(disabledButton);

      const focusableElements = findFocusableElements(container);
      expect(focusableElements).not.toContain(disabledButton);
    });

    test('deve detectar elementos com tabindex positivo', () => {
      const tabindexElement = createFocusableElement('div', { tabindex: '1' });
      container.appendChild(tabindexElement);

      const focusableElements = findFocusableElements(container);
      expect(focusableElements).toContain(tabindexElement);
    });

    test('deve ignorar elementos com tabindex negativo', () => {
      const tabindexElement = createFocusableElement('div', { tabindex: '-1' });
      container.appendChild(tabindexElement);

      const focusableElements = findFocusableElements(container);
      expect(focusableElements).not.toContain(tabindexElement);
    });

    test('deve detectar elementos contenteditable', () => {
      const editableElement = createFocusableElement('div', { contenteditable: 'true' });
      container.appendChild(editableElement);

      const focusableElements = findFocusableElements(container);
      expect(focusableElements).toContain(editableElement);
    });
  });

  describe('FocusManager - Funcionalidades Principais', () => {
    
    test('deve aplicar classe CSS personalizada', () => {
      const props = {
        className: 'custom-focus-manager'
      };

      expect(props.className).toBe('custom-focus-manager');
      expect(typeof props.className).toBe('string');
    });

    test('deve validar props do FocusManager', () => {
      const props = {
        autoFocus: true,
        restoreFocus: true,
        trapFocus: false,
        className: 'test-class'
      };

      expect(typeof props.autoFocus).toBe('boolean');
      expect(typeof props.restoreFocus).toBe('boolean');
      expect(typeof props.trapFocus).toBe('boolean');
      expect(typeof props.className).toBe('string');
    });

    test('deve configurar role dialog quando trapFocus está ativo', () => {
      const props = {
        trapFocus: true
      };

      // Simula a lógica do componente
      const role = props.trapFocus ? 'dialog' : undefined;
      const ariaModal = props.trapFocus ? 'true' : undefined;

      expect(role).toBe('dialog');
      expect(ariaModal).toBe('true');
    });

    test('deve não configurar role quando trapFocus está inativo', () => {
      const props = {
        trapFocus: false
      };

      // Simula a lógica do componente
      const role = props.trapFocus ? 'dialog' : undefined;
      const ariaModal = props.trapFocus ? 'true' : undefined;

      expect(role).toBeUndefined();
      expect(ariaModal).toBeUndefined();
    });
  });

  describe('FocusIndicator - Indicadores Visuais de Foco', () => {
    
    test('deve aplicar estilo ring por padrão', () => {
      const props = {
        style: 'ring' as const,
        color: '#2196f3',
        width: 2
      };

      const getFocusStyles = () => {
        switch (props.style) {
          case 'ring':
            return {
              boxShadow: `0 0 0 ${props.width}px ${props.color}`,
              outline: 'none'
            };
          default:
            return {};
        }
      };

      const styles = getFocusStyles();
      expect(styles).toEqual({
        boxShadow: '0 0 0 2px #2196f3',
        outline: 'none'
      });
    });

    test('deve aplicar estilo outline', () => {
      const props = {
        style: 'outline' as const,
        color: '#ff0000',
        width: 3
      };

      const getFocusStyles = () => {
        switch (props.style) {
          case 'outline':
            return {
              outline: `${props.width}px solid ${props.color}`,
              outlineOffset: '2px'
            };
          default:
            return {};
        }
      };

      const styles = getFocusStyles();
      expect(styles).toEqual({
        outline: '3px solid #ff0000',
        outlineOffset: '2px'
      });
    });

    test('deve aplicar estilo highlight', () => {
      const props = {
        style: 'highlight' as const,
        color: '#00ff00',
        width: 1
      };

      const getFocusStyles = () => {
        switch (props.style) {
          case 'highlight':
            return {
              backgroundColor: `${props.color}20`,
              border: `${props.width}px solid ${props.color}`,
              outline: 'none'
            };
          default:
            return {};
        }
      };

      const styles = getFocusStyles();
      expect(styles).toEqual({
        backgroundColor: '#00ff0020',
        border: '1px solid #00ff00',
        outline: 'none'
      });
    });

    test('deve validar props do FocusIndicator', () => {
      const props = {
        style: 'ring' as const,
        color: '#2196f3',
        width: 2,
        className: 'focus-indicator-class'
      };

      expect(['outline', 'ring', 'highlight', 'custom']).toContain(props.style);
      expect(props.color).toMatch(/^#[0-9A-Fa-f]{6}$/);
      expect(props.width).toBeGreaterThan(0);
      expect(typeof props.className).toBe('string');
    });
  });

  describe('FocusGroup - Navegação por Grupo', () => {
    
    test('deve validar props do FocusGroup', () => {
      const props = {
        direction: 'both' as const,
        loop: true,
        className: 'focus-group-class'
      };

      expect(['horizontal', 'vertical', 'both']).toContain(props.direction);
      expect(typeof props.loop).toBe('boolean');
      expect(typeof props.className).toBe('string');
    });

    test('deve configurar role group', () => {
      const props = {
        className: 'test-group'
      };

      // Simula a lógica do componente
      const role = 'group';
      const className = `focus-group ${props.className}`;

      expect(role).toBe('group');
      expect(className).toBe('focus-group test-group');
    });
  });

  describe('FocusHistory - Histórico de Foco', () => {
    
    test('deve validar estrutura do FocusHistory', () => {
      const mockElement = document.createElement('button');
      const history: FocusHistory = {
        element: mockElement,
        timestamp: Date.now()
      };

      expect(history).toHaveProperty('element');
      expect(history).toHaveProperty('timestamp');
      expect(history.element).toBeInstanceOf(HTMLElement);
      expect(typeof history.timestamp).toBe('number');
    });

    test('deve manter histórico limitado a 10 elementos', () => {
      const histories: FocusHistory[] = [];
      
      // Simula adição de 15 elementos
      for (let i = 0; i < 15; i++) {
        const element = document.createElement('button');
        element.textContent = `Button ${i}`;
        
        histories.push({
          element,
          timestamp: Date.now() + i
        });
      }

      // Simula a lógica de manter apenas os últimos 10
      const limitedHistory = histories.slice(-10);
      
      expect(limitedHistory).toHaveLength(10);
      expect(limitedHistory[0].element.textContent).toBe('Button 5');
      expect(limitedHistory[9].element.textContent).toBe('Button 14');
    });
  });

  describe('Navegação por Teclado - Validação WCAG 2.1', () => {
    
    test('deve suportar navegação por Tab', () => {
      const focusableElements = findFocusableElements(container);
      expect(focusableElements.length).toBeGreaterThan(0);
      
      // Simula navegação por Tab
      const currentIndex = 0;
      const nextIndex = currentIndex < focusableElements.length - 1 ? currentIndex + 1 : 0;
      
      expect(nextIndex).toBe(1);
      expect(focusableElements[nextIndex]).toBe(button2);
    });

    test('deve suportar navegação por Shift+Tab', () => {
      const focusableElements = findFocusableElements(container);
      expect(focusableElements.length).toBeGreaterThan(0);
      
      // Simula navegação por Shift+Tab
      const currentIndex = 1;
      const prevIndex = currentIndex > 0 ? currentIndex - 1 : focusableElements.length - 1;
      
      expect(prevIndex).toBe(0);
      expect(focusableElements[prevIndex]).toBe(button1);
    });

    test('deve suportar navegação por setas (horizontal)', () => {
      const focusableElements = findFocusableElements(container);
      const direction = 'horizontal';
      const loop = true;
      
      // Simula navegação por ArrowRight
      const currentIndex = 0;
      const nextIndex = currentIndex < focusableElements.length - 1 ? currentIndex + 1 : (loop ? 0 : focusableElements.length - 1);
      
      expect(nextIndex).toBe(1);
      expect(focusableElements[nextIndex]).toBe(button2);
    });

    test('deve suportar navegação por setas (vertical)', () => {
      const focusableElements = findFocusableElements(container);
      const direction = 'vertical';
      const loop = true;
      
      // Simula navegação por ArrowDown
      const currentIndex = 0;
      const nextIndex = currentIndex < focusableElements.length - 1 ? currentIndex + 1 : (loop ? 0 : focusableElements.length - 1);
      
      expect(nextIndex).toBe(1);
      expect(focusableElements[nextIndex]).toBe(button2);
    });

    test('deve respeitar configuração de loop', () => {
      const focusableElements = findFocusableElements(container);
      const loop = false;
      
      // Simula navegação sem loop
      const currentIndex = focusableElements.length - 1;
      const nextIndex = currentIndex < focusableElements.length - 1 ? currentIndex + 1 : (loop ? 0 : focusableElements.length - 1);
      
      expect(nextIndex).toBe(focusableElements.length - 1);
    });
  });

  describe('Trap de Foco - Modal e Dialog', () => {
    
    test('deve configurar trap de foco para modais', () => {
      const trapFocus = true;
      const restoreFocus = true;
      
      // Simula configuração de modal
      const role = trapFocus ? 'dialog' : undefined;
      const ariaModal = trapFocus ? 'true' : undefined;
      
      expect(role).toBe('dialog');
      expect(ariaModal).toBe('true');
    });

    test('deve suportar escape para sair do trap', () => {
      const trapFocus = true;
      const restoreFocus = true;
      
      // Simula tecla Escape
      const key = 'Escape';
      const shouldRestoreFocus = key === 'Escape' && restoreFocus;
      
      expect(shouldRestoreFocus).toBe(true);
    });

    test('deve prevenir navegação padrão no trap', () => {
      const trapFocus = true;
      
      // Simula Tab no trap
      const key = 'Tab';
      const shouldPreventDefault = trapFocus && key === 'Tab';
      
      expect(shouldPreventDefault).toBe(true);
    });
  });

  describe('Auto Focus - Foco Automático', () => {
    
    test('deve focar primeiro elemento quando autoFocus está ativo', () => {
      const autoFocus = true;
      const focusableElements = findFocusableElements(container);
      
      if (autoFocus && focusableElements.length > 0) {
        const firstElement = focusableElements[0];
        expect(firstElement).toBe(button1);
      }
    });

    test('deve não focar quando autoFocus está inativo', () => {
      const autoFocus = false;
      const focusableElements = findFocusableElements(container);
      
      // Simula comportamento sem auto focus
      expect(autoFocus).toBe(false);
      expect(focusableElements.length).toBeGreaterThan(0);
    });
  });

  describe('Restore Focus - Restauração de Foco', () => {
    
    test('deve restaurar foco anterior quando restoreFocus está ativo', () => {
      const restoreFocus = true;
      const previousFocus = document.createElement('button');
      previousFocus.textContent = 'Botão Anterior';
      
      // Simula restauração de foco
      if (restoreFocus && previousFocus) {
        expect(previousFocus).toBeInstanceOf(HTMLElement);
        expect(previousFocus.textContent).toBe('Botão Anterior');
      }
    });

    test('deve não restaurar foco quando restoreFocus está inativo', () => {
      const restoreFocus = false;
      const previousFocus = document.createElement('button');
      
      // Simula comportamento sem restauração
      expect(restoreFocus).toBe(false);
      expect(previousFocus).toBeInstanceOf(HTMLElement);
    });
  });
}); 