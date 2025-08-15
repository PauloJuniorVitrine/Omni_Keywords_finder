/**
 * colors.ts
 * 
 * Sistema de cores padronizado para o Omni Keywords Finder
 * Tokens de design centralizados seguindo padrões enterprise
 * 
 * Tracing ID: UI-004
 * Data/Hora: 2024-12-20 07:45:00 UTC
 * Versão: 1.0
 */

// Paleta de cores primária
export const primaryColors = {
  50: '#eff6ff',
  100: '#dbeafe',
  200: '#bfdbfe',
  300: '#93c5fd',
  400: '#60a5fa',
  500: '#3b82f6',
  600: '#2563eb',
  700: '#1d4ed8',
  800: '#1e40af',
  900: '#1e3a8a',
  950: '#172554'
} as const;

// Paleta de cores secundária
export const secondaryColors = {
  50: '#f8fafc',
  100: '#f1f5f9',
  200: '#e2e8f0',
  300: '#cbd5e1',
  400: '#94a3b8',
  500: '#64748b',
  600: '#475569',
  700: '#334155',
  800: '#1e293b',
  900: '#0f172a',
  950: '#020617'
} as const;

// Cores de estado
export const stateColors = {
  success: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0',
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
    950: '#052e16'
  },
  warning: {
    50: '#fffbeb',
    100: '#fef3c7',
    200: '#fde68a',
    300: '#fcd34d',
    400: '#fbbf24',
    500: '#f59e0b',
    600: '#d97706',
    700: '#b45309',
    800: '#92400e',
    900: '#78350f',
    950: '#451a03'
  },
  error: {
    50: '#fef2f2',
    100: '#fee2e2',
    200: '#fecaca',
    300: '#fca5a5',
    400: '#f87171',
    500: '#ef4444',
    600: '#dc2626',
    700: '#b91c1c',
    800: '#991b1b',
    900: '#7f1d1d',
    950: '#450a0a'
  },
  info: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
    950: '#172554'
  }
} as const;

// Cores neutras
export const neutralColors = {
  white: '#ffffff',
  black: '#000000',
  transparent: 'transparent',
  current: 'currentColor'
} as const;

// Cores de acessibilidade
export const accessibilityColors = {
  focus: {
    ring: primaryColors[500],
    offset: neutralColors.white
  },
  selection: {
    background: primaryColors[200],
    text: primaryColors[900]
  },
  highlight: {
    background: primaryColors[100],
    text: primaryColors[900]
  }
} as const;

// Variantes de cores
export const colorVariants = {
  primary: {
    light: primaryColors[400],
    main: primaryColors[600],
    dark: primaryColors[800],
    contrast: neutralColors.white
  },
  secondary: {
    light: secondaryColors[400],
    main: secondaryColors[600],
    dark: secondaryColors[800],
    contrast: neutralColors.white
  },
  success: {
    light: stateColors.success[400],
    main: stateColors.success[600],
    dark: stateColors.success[800],
    contrast: neutralColors.white
  },
  warning: {
    light: stateColors.warning[400],
    main: stateColors.warning[600],
    dark: stateColors.warning[800],
    contrast: neutralColors.black
  },
  error: {
    light: stateColors.error[400],
    main: stateColors.error[600],
    dark: stateColors.error[800],
    contrast: neutralColors.white
  },
  info: {
    light: stateColors.info[400],
    main: stateColors.info[600],
    dark: stateColors.info[800],
    contrast: neutralColors.white
  }
} as const;

// Cores de fundo
export const backgroundColors = {
  primary: neutralColors.white,
  secondary: secondaryColors[50],
  tertiary: secondaryColors[100],
  overlay: 'rgba(0, 0, 0, 0.5)',
  backdrop: 'rgba(0, 0, 0, 0.1)',
  modal: neutralColors.white,
  card: neutralColors.white,
  sidebar: secondaryColors[50],
  header: neutralColors.white,
  footer: secondaryColors[100]
} as const;

// Cores de texto
export const textColors = {
  primary: secondaryColors[900],
  secondary: secondaryColors[600],
  tertiary: secondaryColors[500],
  disabled: secondaryColors[400],
  inverse: neutralColors.white,
  link: primaryColors[600],
  linkHover: primaryColors[700],
  placeholder: secondaryColors[400],
  error: stateColors.error[600],
  success: stateColors.success[600],
  warning: stateColors.warning[600],
  info: stateColors.info[600]
} as const;

// Cores de borda
export const borderColors = {
  primary: secondaryColors[200],
  secondary: secondaryColors[300],
  focus: primaryColors[500],
  error: stateColors.error[300],
  success: stateColors.success[300],
  warning: stateColors.warning[300],
  info: stateColors.info[300],
  disabled: secondaryColors[200]
} as const;

// Cores de sombra
export const shadowColors = {
  light: 'rgba(0, 0, 0, 0.05)',
  medium: 'rgba(0, 0, 0, 0.1)',
  heavy: 'rgba(0, 0, 0, 0.2)',
  colored: `${primaryColors[500]}20`
} as const;

// Gradientes
export const gradients = {
  primary: `linear-gradient(135deg, ${primaryColors[500]} 0%, ${primaryColors[700]} 100%)`,
  secondary: `linear-gradient(135deg, ${secondaryColors[500]} 0%, ${secondaryColors[700]} 100%)`,
  success: `linear-gradient(135deg, ${stateColors.success[500]} 0%, ${stateColors.success[700]} 100%)`,
  warning: `linear-gradient(135deg, ${stateColors.warning[500]} 0%, ${stateColors.warning[700]} 100%)`,
  error: `linear-gradient(135deg, ${stateColors.error[500]} 0%, ${stateColors.error[700]} 100%)`,
  info: `linear-gradient(135deg, ${stateColors.info[500]} 0%, ${stateColors.info[700]} 100%)`
} as const;

// Tema escuro
export const darkThemeColors = {
  primary: {
    ...primaryColors,
    main: primaryColors[400],
    light: primaryColors[300],
    dark: primaryColors[600]
  },
  secondary: {
    ...secondaryColors,
    main: secondaryColors[400],
    light: secondaryColors[300],
    dark: secondaryColors[600]
  },
  background: {
    primary: secondaryColors[900],
    secondary: secondaryColors[800],
    tertiary: secondaryColors[700],
    card: secondaryColors[800],
    sidebar: secondaryColors[900],
    header: secondaryColors[900],
    footer: secondaryColors[800]
  },
  text: {
    primary: secondaryColors[100],
    secondary: secondaryColors[300],
    tertiary: secondaryColors[400],
    disabled: secondaryColors[500],
    inverse: secondaryColors[900],
    link: primaryColors[400],
    linkHover: primaryColors[300]
  },
  border: {
    primary: secondaryColors[700],
    secondary: secondaryColors[600],
    focus: primaryColors[400],
    error: stateColors.error[400],
    success: stateColors.success[400],
    warning: stateColors.warning[400],
    info: stateColors.info[400]
  }
} as const;

// Classes utilitárias
export const colorClasses = {
  // Background colors
  'bg-primary': `background-color: ${primaryColors[600]}`,
  'bg-secondary': `background-color: ${secondaryColors[600]}`,
  'bg-success': `background-color: ${stateColors.success[600]}`,
  'bg-warning': `background-color: ${stateColors.warning[600]}`,
  'bg-error': `background-color: ${stateColors.error[600]}`,
  'bg-info': `background-color: ${stateColors.info[600]}`,
  
  // Text colors
  'text-primary': `color: ${primaryColors[600]}`,
  'text-secondary': `color: ${secondaryColors[600]}`,
  'text-success': `color: ${stateColors.success[600]}`,
  'text-warning': `color: ${stateColors.warning[600]}`,
  'text-error': `color: ${stateColors.error[600]}`,
  'text-info': `color: ${stateColors.info[600]}`,
  
  // Border colors
  'border-primary': `border-color: ${primaryColors[600]}`,
  'border-secondary': `border-color: ${secondaryColors[600]}`,
  'border-success': `border-color: ${stateColors.success[600]}`,
  'border-warning': `border-color: ${stateColors.warning[600]}`,
  'border-error': `border-color: ${stateColors.error[600]}`,
  'border-info': `border-color: ${stateColors.info[600]}`
} as const;

// Funções utilitárias
export const colorUtils = {
  // Obter cor com opacidade
  withOpacity: (color: string, opacity: number): string => {
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
  },

  // Obter cor mais clara
  lighten: (color: string, amount: number): string => {
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    const newR = Math.min(255, r + amount);
    const newG = Math.min(255, g + amount);
    const newB = Math.min(255, b + amount);
    
    return `#${Math.round(newR).toString(16).padStart(2, '0')}${Math.round(newG).toString(16).padStart(2, '0')}${Math.round(newB).toString(16).padStart(2, '0')}`;
  },

  // Obter cor mais escura
  darken: (color: string, amount: number): string => {
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    const newR = Math.max(0, r - amount);
    const newG = Math.max(0, g - amount);
    const newB = Math.max(0, b - amount);
    
    return `#${Math.round(newR).toString(16).padStart(2, '0')}${Math.round(newG).toString(16).padStart(2, '0')}${Math.round(newB).toString(16).padStart(2, '0')}`;
  },

  // Verificar se cor é clara
  isLight: (color: string): boolean => {
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    const brightness = (r * 299 + g * 587 + b * 114) / 1000;
    return brightness > 128;
  },

  // Obter cor de contraste
  getContrast: (color: string): string => {
    return colorUtils.isLight(color) ? neutralColors.black : neutralColors.white;
  }
} as const;

// Exportação principal
export const colors = {
  primary: primaryColors,
  secondary: secondaryColors,
  state: stateColors,
  neutral: neutralColors,
  accessibility: accessibilityColors,
  variants: colorVariants,
  background: backgroundColors,
  text: textColors,
  border: borderColors,
  shadow: shadowColors,
  gradients,
  dark: darkThemeColors,
  classes: colorClasses,
  utils: colorUtils
} as const;

export default colors; 