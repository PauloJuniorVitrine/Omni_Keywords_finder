/**
 * Hook de Acessibilidade - useA11y
 * 
 * Fornece funcionalidades de acessibilidade para componentes React
 * Baseado em WCAG 2.1 AA e ARIA 1.2
 * 
 * Tracing ID: useA11y_20250127_001
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import { useCallback, useMemo, useRef, useState } from 'react';

export interface A11yProps {
  /** ID único do elemento */
  id?: string;
  /** Label acessível */
  label?: string;
  /** Descrição detalhada */
  description?: string;
  /** Estado atual do elemento */
  state?: 'expanded' | 'collapsed' | 'selected' | 'checked' | 'unchecked' | 'busy' | 'error';
  /** Se o elemento está desabilitado */
  disabled?: boolean;
  /** Se o elemento é obrigatório */
  required?: boolean;
  /** Se o elemento é inválido */
  invalid?: boolean;
  /** Mensagem de erro */
  errorMessage?: string;
  /** Tipo de role ARIA */
  role?: string;
  /** Nível de heading (1-6) */
  headingLevel?: 1 | 2 | 3 | 4 | 5 | 6;
  /** Se o elemento está oculto do screen reader */
  hidden?: boolean;
  /** Texto alternativo para imagens */
  altText?: string;
  /** Se o elemento é live region */
  live?: 'polite' | 'assertive' | 'off';
  /** Se o elemento é expandível */
  expandable?: boolean;
  /** Se o elemento é controlado */
  controlled?: boolean;
}

export interface A11yReturn {
  /** Props de acessibilidade para o elemento */
  a11yProps: Record<string, any>;
  /** Função para anunciar mudanças ao screen reader */
  announce: (message: string, priority?: 'polite' | 'assertive') => void;
  /** Função para gerar ID único */
  generateId: (prefix?: string) => string;
  /** Função para validar contraste */
  validateContrast: (foreground: string, background: string) => boolean;
  /** Função para verificar se elemento está visível */
  isVisible: (element: HTMLElement) => boolean;
  /** Função para focar elemento */
  focusElement: (element: HTMLElement) => void;
  /** Função para obter texto acessível */
  getAccessibleText: () => string;
}

/**
 * Hook principal de acessibilidade
 */
export const useA11y = (props: A11yProps = {}): A11yReturn => {
  const {
    id,
    label,
    description,
    state,
    disabled = false,
    required = false,
    invalid = false,
    errorMessage,
    role,
    headingLevel,
    hidden = false,
    altText,
    live = 'off',
    expandable = false,
    controlled = false
  } = props;

  const [announcements, setAnnouncements] = useState<string[]>([]);
  const idRef = useRef<string>(id || `a11y-${Math.random().toString(36).substr(2, 9)}`);

  /**
   * Gera ID único para elementos
   */
  const generateId = useCallback((prefix = 'a11y'): string => {
    return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  /**
   * Anuncia mudanças ao screen reader
   */
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite'): void => {
    const announcement = { message, priority, timestamp: Date.now() };
    setAnnouncements(prev => [...prev, announcement.message]);
    
    // Cria elemento live region para anunciar
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', priority);
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.style.position = 'absolute';
    liveRegion.style.left = '-10000px';
    liveRegion.style.width = '1px';
    liveRegion.style.height = '1px';
    liveRegion.style.overflow = 'hidden';
    
    document.body.appendChild(liveRegion);
    liveRegion.textContent = message;
    
    // Remove após anunciar
    setTimeout(() => {
      document.body.removeChild(liveRegion);
    }, 1000);
  }, []);

  /**
   * Valida contraste de cores (WCAG 2.1 AA)
   */
  const validateContrast = useCallback((foreground: string, background: string): boolean => {
    // Converte cores hex para RGB
    const hexToRgb = (hex: string): number[] => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result ? [
        parseInt(result[1], 16),
        parseInt(result[2], 16),
        parseInt(result[3], 16)
      ] : [0, 0, 0];
    };

    const fg = hexToRgb(foreground);
    const bg = hexToRgb(background);

    // Calcula luminância relativa
    const getLuminance = (r: number, g: number, b: number): number => {
      const [rs, gs, bs] = [r, g, b].map(c => {
        c = c / 255;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
    };

    const l1 = getLuminance(fg[0], fg[1], fg[2]);
    const l2 = getLuminance(bg[0], bg[1], bg[2]);

    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    
    // WCAG 2.1 AA requer 4.5:1 para texto normal, 3:1 para texto grande
    return ratio >= 4.5;
  }, []);

  /**
   * Verifica se elemento está visível
   */
  const isVisible = useCallback((element: HTMLElement): boolean => {
    const style = window.getComputedStyle(element);
    return style.display !== 'none' && 
           style.visibility !== 'hidden' && 
           style.opacity !== '0' &&
           element.offsetWidth > 0 &&
           element.offsetHeight > 0;
  }, []);

  /**
   * Foca elemento com suporte a acessibilidade
   */
  const focusElement = useCallback((element: HTMLElement): void => {
    if (element && isVisible(element)) {
      element.focus();
      announce(`Focado em ${element.getAttribute('aria-label') || element.textContent || 'elemento'}`);
    }
  }, [announce, isVisible]);

  /**
   * Obtém texto acessível do elemento
   */
  const getAccessibleText = useCallback((): string => {
    let text = '';
    
    if (label) text += label;
    if (description) text += ` ${description}`;
    if (state) text += ` ${state}`;
    if (required) text += ' obrigatório';
    if (invalid && errorMessage) text += ` ${errorMessage}`;
    
    return text.trim();
  }, [label, description, state, required, invalid, errorMessage]);

  /**
   * Gera props de acessibilidade
   */
  const a11yProps = useMemo((): Record<string, any> => {
    const props: Record<string, any> = {
      id: idRef.current,
      'aria-label': label,
      'aria-describedby': description ? `${idRef.current}-desc` : undefined,
      'aria-disabled': disabled,
      'aria-required': required,
      'aria-invalid': invalid,
      'aria-hidden': hidden,
      'aria-live': live !== 'off' ? live : undefined,
      'aria-expanded': expandable ? (state === 'expanded') : undefined,
      'aria-checked': controlled ? (state === 'checked' ? true : state === 'unchecked' ? false : undefined) : undefined,
      'aria-selected': state === 'selected',
      'aria-busy': state === 'busy',
      'aria-errormessage': invalid && errorMessage ? `${idRef.current}-error` : undefined,
    };

    // Adiciona role específico
    if (role) {
      props.role = role;
    } else if (headingLevel) {
      props.role = `heading`;
      props['aria-level'] = headingLevel;
    }

    // Remove props undefined
    Object.keys(props).forEach(key => {
      if (props[key] === undefined) {
        delete props[key];
      }
    });

    return props;
  }, [
    label, description, disabled, required, invalid, hidden, live, 
    expandable, state, controlled, role, headingLevel, errorMessage
  ]);

  return {
    a11yProps,
    announce,
    generateId,
    validateContrast,
    isVisible,
    focusElement,
    getAccessibleText
  };
};

/**
 * Hook para gerenciar live regions
 */
export const useLiveRegion = (priority: 'polite' | 'assertive' = 'polite') => {
  const announce = useCallback((message: string): void => {
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', priority);
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.style.position = 'absolute';
    liveRegion.style.left = '-10000px';
    liveRegion.style.width = '1px';
    liveRegion.style.height = '1px';
    liveRegion.style.overflow = 'hidden';
    
    document.body.appendChild(liveRegion);
    liveRegion.textContent = message;
    
    setTimeout(() => {
      if (document.body.contains(liveRegion)) {
        document.body.removeChild(liveRegion);
      }
    }, 1000);
  }, [priority]);

  return { announce };
};

/**
 * Hook para gerenciar landmarks
 */
export const useLandmark = (type: 'main' | 'navigation' | 'banner' | 'contentinfo' | 'complementary' | 'region') => {
  const landmarkProps = useMemo(() => ({
    role: type,
    'aria-label': `${type} section`
  }), [type]);

  return { landmarkProps };
};

export default useA11y; 