/**
 * Utilitários de Acessibilidade - a11y.ts
 * 
 * Fornece funções utilitárias para acessibilidade
 * Baseado em WCAG 2.1 AA e ARIA 1.2
 * 
 * Tracing ID: a11y_utils_20250127_001
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

/**
 * Tipos de roles ARIA
 */
export type AriaRole = 
  | 'button' | 'checkbox' | 'dialog' | 'gridcell' | 'link' | 'menuitem' 
  | 'menuitemcheckbox' | 'menuitemradio' | 'option' | 'progressbar' 
  | 'radio' | 'scrollbar' | 'searchbox' | 'slider' | 'spinbutton' 
  | 'switch' | 'tab' | 'tabpanel' | 'textbox' | 'treeitem' | 'combobox'
  | 'grid' | 'listbox' | 'menu' | 'menubar' | 'radiogroup' | 'tablist'
  | 'tree' | 'treegrid' | 'article' | 'banner' | 'complementary' 
  | 'contentinfo' | 'form' | 'main' | 'navigation' | 'region' | 'search'
  | 'section' | 'sectionhead' | 'separator' | 'toolbar' | 'tooltip'
  | 'application' | 'document' | 'feed' | 'log' | 'marquee' | 'presentation'
  | 'status' | 'timer' | 'alert' | 'alertdialog' | 'definition' | 'directory'
  | 'group' | 'heading' | 'img' | 'list' | 'listitem' | 'math' | 'note'
  | 'row' | 'rowgroup' | 'rowheader' | 'table' | 'term' | 'text' | 'columnheader';

/**
 * Estados ARIA
 */
export type AriaState = 
  | 'aria-expanded' | 'aria-selected' | 'aria-checked' | 'aria-pressed'
  | 'aria-current' | 'aria-invalid' | 'aria-required' | 'aria-disabled'
  | 'aria-hidden' | 'aria-busy' | 'aria-live' | 'aria-atomic'
  | 'aria-relevant' | 'aria-autocomplete' | 'aria-haspopup'
  | 'aria-level' | 'aria-multiselectable' | 'aria-orientation'
  | 'aria-readonly' | 'aria-sort' | 'aria-valuemax' | 'aria-valuemin'
  | 'aria-valuenow' | 'aria-valuetext';

/**
 * Propriedades ARIA
 */
export interface AriaProps {
  role?: AriaRole;
  'aria-label'?: string;
  'aria-labelledby'?: string;
  'aria-describedby'?: string;
  'aria-controls'?: string;
  'aria-expanded'?: boolean;
  'aria-selected'?: boolean;
  'aria-checked'?: boolean | 'mixed';
  'aria-pressed'?: boolean | 'mixed';
  'aria-current'?: boolean | 'page' | 'step' | 'location' | 'date' | 'time';
  'aria-invalid'?: boolean;
  'aria-required'?: boolean;
  'aria-disabled'?: boolean;
  'aria-hidden'?: boolean;
  'aria-busy'?: boolean;
  'aria-live'?: 'off' | 'polite' | 'assertive';
  'aria-atomic'?: boolean;
  'aria-relevant'?: 'additions' | 'additions removals' | 'additions text' | 'all' | 'removals' | 'removals additions' | 'removals text' | 'text' | 'text additions' | 'text removals';
  'aria-autocomplete'?: 'none' | 'inline' | 'list' | 'both';
  'aria-haspopup'?: boolean | 'menu' | 'listbox' | 'tree' | 'grid' | 'dialog';
  'aria-level'?: number;
  'aria-multiselectable'?: boolean;
  'aria-orientation'?: 'horizontal' | 'vertical';
  'aria-readonly'?: boolean;
  'aria-sort'?: 'none' | 'ascending' | 'descending' | 'other';
  'aria-valuemax'?: number;
  'aria-valuemin'?: number;
  'aria-valuenow'?: number;
  'aria-valuetext'?: string;
  'aria-errormessage'?: string;
  'aria-activedescendant'?: string;
  'aria-colcount'?: number;
  'aria-colindex'?: number;
  'aria-colspan'?: number;
  'aria-rowcount'?: number;
  'aria-rowindex'?: number;
  'aria-rowspan'?: number;
  'aria-setsize'?: number;
  'aria-posinset'?: number;
  'aria-flowto'?: string;
  'aria-details'?: string;
  'aria-keyshortcuts'?: string;
  'aria-roledescription'?: string;
  'aria-owns'?: string;
  'aria-placeholder'?: string;
  'aria-describedby'?: string;
  'aria-labelledby'?: string;
}

/**
 * Gera ID único para elementos ARIA
 */
export const generateAriaId = (prefix = 'aria'): string => {
  return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Gera props ARIA para elemento
 */
export const generateAriaProps = (props: Partial<AriaProps>): Record<string, any> => {
  const ariaProps: Record<string, any> = {};

  Object.entries(props).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      ariaProps[key] = value;
    }
  });

  return ariaProps;
};

/**
 * Valida se role ARIA é válido
 */
export const isValidAriaRole = (role: string): role is AriaRole => {
  const validRoles: AriaRole[] = [
    'button', 'checkbox', 'dialog', 'gridcell', 'link', 'menuitem',
    'menuitemcheckbox', 'menuitemradio', 'option', 'progressbar',
    'radio', 'scrollbar', 'searchbox', 'slider', 'spinbutton',
    'switch', 'tab', 'tabpanel', 'textbox', 'treeitem', 'combobox',
    'grid', 'listbox', 'menu', 'menubar', 'radiogroup', 'tablist',
    'tree', 'treegrid', 'article', 'banner', 'complementary',
    'contentinfo', 'form', 'main', 'navigation', 'region', 'search',
    'section', 'sectionhead', 'separator', 'toolbar', 'tooltip',
    'application', 'document', 'feed', 'log', 'marquee', 'presentation',
    'status', 'timer', 'alert', 'alertdialog', 'definition', 'directory',
    'group', 'heading', 'img', 'list', 'listitem', 'math', 'note',
    'row', 'rowgroup', 'rowheader', 'table', 'term', 'text', 'columnheader'
  ];

  return validRoles.includes(role as AriaRole);
};

/**
 * Obtém roles ARIA obrigatórios para elemento
 */
export const getRequiredAriaRoles = (element: HTMLElement): AriaRole[] => {
  const tagName = element.tagName.toLowerCase();
  const roles: AriaRole[] = [];

  switch (tagName) {
    case 'button':
      roles.push('button');
      break;
    case 'input':
      const type = element.getAttribute('type');
      switch (type) {
        case 'checkbox':
          roles.push('checkbox');
          break;
        case 'radio':
          roles.push('radio');
          break;
        case 'search':
          roles.push('searchbox');
          break;
        default:
          roles.push('textbox');
      }
      break;
    case 'a':
      roles.push('link');
      break;
    case 'dialog':
      roles.push('dialog');
      break;
    case 'nav':
      roles.push('navigation');
      break;
    case 'main':
      roles.push('main');
      break;
    case 'header':
      roles.push('banner');
      break;
    case 'footer':
      roles.push('contentinfo');
      break;
    case 'aside':
      roles.push('complementary');
      break;
    case 'article':
      roles.push('article');
      break;
    case 'section':
      roles.push('region');
      break;
    case 'form':
      roles.push('form');
      break;
    case 'table':
      roles.push('table');
      break;
    case 'ul':
    case 'ol':
      roles.push('list');
      break;
    case 'li':
      roles.push('listitem');
      break;
  }

  return roles;
};

/**
 * Valida se elemento tem atributos ARIA obrigatórios
 */
export const validateAriaAttributes = (element: HTMLElement): {
  isValid: boolean;
  errors: string[];
  warnings: string[];
} => {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Verifica se tem role
  const role = element.getAttribute('role');
  if (!role) {
    const requiredRoles = getRequiredAriaRoles(element);
    if (requiredRoles.length > 0) {
      warnings.push(`Elemento ${element.tagName} deveria ter role ARIA: ${requiredRoles.join(', ')}`);
    }
  } else if (!isValidAriaRole(role)) {
    errors.push(`Role ARIA inválido: ${role}`);
  }

  // Verifica se tem label
  const hasLabel = element.hasAttribute('aria-label') || 
                   element.hasAttribute('aria-labelledby') ||
                   element.hasAttribute('title');
  
  if (!hasLabel) {
    const interactiveElements = ['button', 'input', 'select', 'textarea', 'a'];
    if (interactiveElements.includes(element.tagName.toLowerCase())) {
      errors.push(`Elemento interativo ${element.tagName} deve ter label acessível`);
    }
  }

  // Verifica se tem descrição quando necessário
  const hasDescription = element.hasAttribute('aria-describedby') ||
                        element.hasAttribute('aria-description');
  
  if (!hasDescription) {
    const complexElements = ['dialog', 'combobox', 'grid', 'tree'];
    if (complexElements.includes(role || '')) {
      warnings.push(`Elemento complexo com role ${role} deveria ter descrição`);
    }
  }

  // Verifica estados ARIA
  const ariaStates = ['aria-expanded', 'aria-selected', 'aria-checked', 'aria-pressed'];
  ariaStates.forEach(state => {
    const value = element.getAttribute(state);
    if (value && !['true', 'false', 'mixed'].includes(value)) {
      errors.push(`Valor inválido para ${state}: ${value}`);
    }
  });

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
};

/**
 * Anuncia mensagem para screen reader
 */
export const announceToScreenReader = (
  message: string, 
  priority: 'polite' | 'assertive' = 'polite'
): void => {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.style.position = 'absolute';
  announcement.style.left = '-10000px';
  announcement.style.width = '1px';
  announcement.style.height = '1px';
  announcement.style.overflow = 'hidden';
  
  document.body.appendChild(announcement);
  announcement.textContent = message;
  
  setTimeout(() => {
    if (document.body.contains(announcement)) {
      document.body.removeChild(announcement);
    }
  }, 1000);
};

/**
 * Obtém texto acessível de elemento
 */
export const getAccessibleText = (element: HTMLElement): string => {
  let text = '';

  // Prioridade 1: aria-label
  const ariaLabel = element.getAttribute('aria-label');
  if (ariaLabel) {
    text = ariaLabel;
  }
  // Prioridade 2: aria-labelledby
  else {
    const labelledBy = element.getAttribute('aria-labelledby');
    if (labelledBy) {
      const labelElement = document.getElementById(labelledBy);
      if (labelElement) {
        text = labelElement.textContent || '';
      }
    }
  }
  // Prioridade 3: title
  if (!text) {
    const title = element.getAttribute('title');
    if (title) {
      text = title;
    }
  }
  // Prioridade 4: alt (para imagens)
  if (!text && element.tagName === 'IMG') {
    const alt = element.getAttribute('alt');
    if (alt) {
      text = alt;
    }
  }
  // Prioridade 5: textContent
  if (!text) {
    text = element.textContent?.trim() || '';
  }

  return text;
};

/**
 * Verifica se elemento está oculto do screen reader
 */
export const isHiddenFromScreenReader = (element: HTMLElement): boolean => {
  const ariaHidden = element.getAttribute('aria-hidden');
  if (ariaHidden === 'true') return true;

  const style = window.getComputedStyle(element);
  return style.display === 'none' || 
         style.visibility === 'hidden' || 
         style.opacity === '0';
};

/**
 * Obtém elementos focáveis dentro de container
 */
export const getFocusableElements = (container: HTMLElement): HTMLElement[] => {
  const focusableSelectors = [
    'button:not([disabled])',
    '[href]',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
    '[contenteditable="true"]'
  ];

  const elements = Array.from(container.querySelectorAll(focusableSelectors.join(','))) as HTMLElement[];
  
  return elements.filter(element => {
    const style = window.getComputedStyle(element);
    return style.display !== 'none' && 
           style.visibility !== 'hidden' && 
           style.opacity !== '0' &&
           !isHiddenFromScreenReader(element);
  });
};

/**
 * Verifica se elemento é focável
 */
export const isFocusable = (element: HTMLElement): boolean => {
  if (!element) return false;

  // Verifica se tem tabindex
  const tabIndex = element.getAttribute('tabindex');
  if (tabIndex === '-1') return false;

  // Verifica se está desabilitado
  if (element.hasAttribute('disabled') || element.getAttribute('aria-disabled') === 'true') {
    return false;
  }

  // Verifica se está oculto
  if (isHiddenFromScreenReader(element)) return false;

  // Verifica se é elemento focável por natureza
  const focusableTags = ['button', 'input', 'select', 'textarea', 'a'];
  const tagName = element.tagName.toLowerCase();
  
  if (focusableTags.includes(tagName)) return true;
  if (tabIndex !== null) return true;
  if (element.getAttribute('contenteditable') === 'true') return true;

  return false;
};

/**
 * Foca elemento com suporte a acessibilidade
 */
export const focusElement = (element: HTMLElement): void => {
  if (!element || !isFocusable(element)) return;

  element.focus();
  
  // Anuncia foco para screen reader
  const accessibleText = getAccessibleText(element);
  if (accessibleText) {
    announceToScreenReader(`Focado em ${accessibleText}`);
  }
};

/**
 * Cria live region para anúncios
 */
export const createLiveRegion = (
  priority: 'polite' | 'assertive' = 'polite',
  atomic: boolean = true
): HTMLElement => {
  const liveRegion = document.createElement('div');
  liveRegion.setAttribute('aria-live', priority);
  liveRegion.setAttribute('aria-atomic', atomic.toString());
  liveRegion.style.position = 'absolute';
  liveRegion.style.left = '-10000px';
  liveRegion.style.width = '1px';
  liveRegion.style.height = '1px';
  liveRegion.style.overflow = 'hidden';
  
  return liveRegion;
};

/**
 * Remove live region
 */
export const removeLiveRegion = (liveRegion: HTMLElement): void => {
  if (document.body.contains(liveRegion)) {
    document.body.removeChild(liveRegion);
  }
};

/**
 * Anuncia mudança usando live region
 */
export const announceChange = (
  message: string,
  priority: 'polite' | 'assertive' = 'polite'
): void => {
  const liveRegion = createLiveRegion(priority);
  document.body.appendChild(liveRegion);
  
  liveRegion.textContent = message;
  
  setTimeout(() => {
    removeLiveRegion(liveRegion);
  }, 1000);
};

/**
 * Valida estrutura de landmarks
 */
export const validateLandmarks = (): {
  isValid: boolean;
  errors: string[];
  warnings: string[];
} => {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Verifica se tem main
  const mainElements = document.querySelectorAll('[role="main"], main');
  if (mainElements.length === 0) {
    errors.push('Página deve ter um elemento main');
  } else if (mainElements.length > 1) {
    errors.push('Página deve ter apenas um elemento main');
  }

  // Verifica se tem navigation
  const navElements = document.querySelectorAll('[role="navigation"], nav');
  if (navElements.length === 0) {
    warnings.push('Página deveria ter elementos de navegação');
  }

  // Verifica se tem banner
  const bannerElements = document.querySelectorAll('[role="banner"], header');
  if (bannerElements.length === 0) {
    warnings.push('Página deveria ter um banner/header');
  }

  // Verifica se tem contentinfo
  const contentInfoElements = document.querySelectorAll('[role="contentinfo"], footer');
  if (contentInfoElements.length === 0) {
    warnings.push('Página deveria ter um footer/contentinfo');
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
};

/**
 * Obtém estatísticas de acessibilidade da página
 */
export const getAccessibilityStats = (): {
  totalElements: number;
  elementsWithRole: number;
  elementsWithLabel: number;
  elementsWithDescription: number;
  focusableElements: number;
  hiddenElements: number;
  landmarks: number;
} => {
  const allElements = document.querySelectorAll('*');
  const elementsWithRole = document.querySelectorAll('[role]');
  const elementsWithLabel = document.querySelectorAll('[aria-label], [aria-labelledby]');
  const elementsWithDescription = document.querySelectorAll('[aria-describedby]');
  const focusableElements = getFocusableElements(document.body);
  const hiddenElements = document.querySelectorAll('[aria-hidden="true"]');
  const landmarks = document.querySelectorAll('[role="main"], [role="navigation"], [role="banner"], [role="contentinfo"], [role="complementary"], [role="region"]');

  return {
    totalElements: allElements.length,
    elementsWithRole: elementsWithRole.length,
    elementsWithLabel: elementsWithLabel.length,
    elementsWithDescription: elementsWithDescription.length,
    focusableElements: focusableElements.length,
    hiddenElements: hiddenElements.length,
    landmarks: landmarks.length
  };
};

export default {
  generateAriaId,
  generateAriaProps,
  isValidAriaRole,
  getRequiredAriaRoles,
  validateAriaAttributes,
  announceToScreenReader,
  getAccessibleText,
  isHiddenFromScreenReader,
  getFocusableElements,
  isFocusable,
  focusElement,
  createLiveRegion,
  removeLiveRegion,
  announceChange,
  validateLandmarks,
  getAccessibilityStats
}; 