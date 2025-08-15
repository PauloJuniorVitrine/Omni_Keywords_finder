// Design Utilities - Omni Keywords Finder

import { colors, spacing, typography, shadows, borderRadius, transitions } from '../components/ui/DesignSystem';

// Color utilities
export const getColorValue = (colorPath: string): string => {
  const path = colorPath.split('.');
  let current: any = colors;
  
  for (const key of path) {
    if (current[key] === undefined) {
      console.warn(`Color path "${colorPath}" not found`);
      return '#000000';
    }
    current = current[key];
  }
  
  return current;
};

export const getContrastColor = (backgroundColor: string): string => {
  // Simple contrast calculation
  const hex = backgroundColor.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;
  
  return brightness > 128 ? '#000000' : '#ffffff';
};

export const hexToRgba = (hex: string, alpha: number = 1): string => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

export const rgbaToHex = (rgba: string): string => {
  const match = rgba.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
  if (!match) return '#000000';
  
  const r = parseInt(match[1]);
  const g = parseInt(match[2]);
  const b = parseInt(match[3]);
  
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
};

// Spacing utilities
export const getSpacingValue = (size: keyof typeof spacing): string => {
  return spacing[size];
};

export const createSpacingScale = (base: number = 4, steps: number = 10): Record<string, string> => {
  const scale: Record<string, string> = {};
  
  for (let i = 0; i <= steps; i++) {
    const value = base * Math.pow(2, i / 4);
    scale[i] = `${value}px`;
  }
  
  return scale;
};

// Typography utilities
export const getFontSize = (size: keyof typeof typography.fontSize): string => {
  return typography.fontSize[size];
};

export const getFontWeight = (weight: keyof typeof typography.fontWeight): string => {
  return typography.fontWeight[weight];
};

export const getLineHeight = (height: keyof typeof typography.lineHeight): string => {
  return typography.lineHeight[height];
};

export const createTypographyScale = (base: number = 16, ratio: number = 1.25): Record<string, string> => {
  const scale: Record<string, string> = {};
  
  for (let i = -2; i <= 8; i++) {
    const size = base * Math.pow(ratio, i);
    scale[i] = `${size}px`;
  }
  
  return scale;
};

// Shadow utilities
export const getShadow = (shadow: keyof typeof shadows): string => {
  return shadows[shadow];
};

export const createCustomShadow = (
  x: number = 0,
  y: number = 0,
  blur: number = 0,
  spread: number = 0,
  color: string = 'rgba(0, 0, 0, 0.1)'
): string => {
  return `${x}px ${y}px ${blur}px ${spread}px ${color}`;
};

// Border radius utilities
export const getBorderRadius = (radius: keyof typeof borderRadius): string => {
  return borderRadius[radius];
};

export const createBorderRadiusScale = (base: number = 4): Record<string, string> => {
  const scale: Record<string, string> = {};
  
  for (let i = 0; i <= 8; i++) {
    const value = base * Math.pow(2, i / 2);
    scale[i] = `${value}px`;
  }
  
  return scale;
};

// Transition utilities
export const getTransition = (transition: keyof typeof transitions): string => {
  return transitions[transition];
};

export const createCustomTransition = (
  properties: string[] = ['all'],
  duration: string = '200ms',
  easing: string = 'ease-in-out',
  delay: string = '0ms'
): string => {
  return properties.map(prop => `${prop} ${duration} ${easing} ${delay}`).join(', ');
};

// Responsive utilities
export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};

export const getBreakpoint = (breakpoint: keyof typeof breakpoints): string => {
  return breakpoints[breakpoint];
};

export const createMediaQuery = (breakpoint: keyof typeof breakpoints, minMax: 'min' | 'max' = 'min'): string => {
  return `@media (${minMax}-width: ${getBreakpoint(breakpoint)})`;
};

// Layout utilities
export const createGridTemplate = (columns: number, gap: string = '1rem'): string => {
  return `grid-template-columns: repeat(${columns}, 1fr); gap: ${gap};`;
};

export const createFlexbox = (
  direction: 'row' | 'column' = 'row',
  justify: 'start' | 'end' | 'center' | 'between' | 'around' | 'evenly' = 'start',
  align: 'start' | 'end' | 'center' | 'baseline' | 'stretch' = 'start',
  wrap: boolean = false
): string => {
  const flexDirection = direction === 'column' ? 'column' : 'row';
  const justifyContent = justify === 'between' ? 'space-between' : 
                        justify === 'around' ? 'space-around' : 
                        justify === 'evenly' ? 'space-evenly' : justify;
  const alignItems = align === 'baseline' ? 'baseline' : align;
  const flexWrap = wrap ? 'wrap' : 'nowrap';
  
  return `display: flex; flex-direction: ${flexDirection}; justify-content: ${justifyContent}; align-items: ${alignItems}; flex-wrap: ${flexWrap};`;
};

// Component class generators
export const generateButtonClasses = (
  variant: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' = 'primary',
  size: 'sm' | 'md' | 'lg' = 'md',
  disabled: boolean = false
): string => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';
  const disabledClasses = disabled ? 'opacity-50 cursor-not-allowed' : '';
  
  const variantClasses = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
    secondary: 'bg-secondary-100 text-secondary-900 hover:bg-secondary-200 focus:ring-secondary-500',
    outline: 'border border-secondary-300 bg-white text-secondary-700 hover:bg-secondary-50 focus:ring-secondary-500',
    ghost: 'text-secondary-700 hover:bg-secondary-100 focus:ring-secondary-500',
    danger: 'bg-error-600 text-white hover:bg-error-700 focus:ring-error-500',
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  return `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${disabledClasses}`.trim();
};

export const generateInputClasses = (error: boolean = false, disabled: boolean = false): string => {
  const baseClasses = 'block w-full rounded-lg border px-3 py-2 text-secondary-900 placeholder-secondary-500 focus:outline-none focus:ring-1';
  const errorClasses = error ? 'border-error-300 focus:border-error-500 focus:ring-error-500' : 'border-secondary-300 focus:border-primary-500 focus:ring-primary-500';
  const disabledClasses = disabled ? 'bg-secondary-100 cursor-not-allowed' : '';
  
  return `${baseClasses} ${errorClasses} ${disabledClasses}`.trim();
};

export const generateCardClasses = (elevated: boolean = false): string => {
  const baseClasses = 'bg-white rounded-lg border border-secondary-200';
  const shadowClasses = elevated ? 'shadow-lg' : 'shadow-base';
  
  return `${baseClasses} ${shadowClasses}`;
};

// Animation utilities
export const createKeyframes = (name: string, keyframes: Record<string, any>): string => {
  const keyframeString = Object.entries(keyframes)
    .map(([key, value]) => `${key} { ${Object.entries(value).map(([prop, val]) => `${prop}: ${val}`).join('; ')} }`)
    .join('\n');
  
  return `@keyframes ${name} {\n${keyframeString}\n}`;
};

export const createAnimation = (
  name: string,
  duration: string = '1s',
  timing: string = 'ease',
  delay: string = '0s',
  iteration: string = '1',
  direction: string = 'normal',
  fill: string = 'none'
): string => {
  return `${name} ${duration} ${timing} ${delay} ${iteration} ${direction} ${fill}`;
};

// Utility class generators
export const generateUtilityClasses = (): Record<string, string> => {
  return {
    // Text colors
    'text-primary': `color: ${colors.primary[600]}`,
    'text-secondary': `color: ${colors.secondary[600]}`,
    'text-success': `color: ${colors.success[600]}`,
    'text-warning': `color: ${colors.warning[600]}`,
    'text-error': `color: ${colors.error[600]}`,
    
    // Background colors
    'bg-primary': `background-color: ${colors.primary[600]}`,
    'bg-secondary': `background-color: ${colors.secondary[100]}`,
    'bg-success': `background-color: ${colors.success[600]}`,
    'bg-warning': `background-color: ${colors.warning[600]}`,
    'bg-error': `background-color: ${colors.error[600]}`,
    
    // Spacing
    'p-xs': `padding: ${spacing.xs}`,
    'p-sm': `padding: ${spacing.sm}`,
    'p-md': `padding: ${spacing.md}`,
    'p-lg': `padding: ${spacing.lg}`,
    'p-xl': `padding: ${spacing.xl}`,
    
    'm-xs': `margin: ${spacing.xs}`,
    'm-sm': `margin: ${spacing.sm}`,
    'm-md': `margin: ${spacing.md}`,
    'm-lg': `margin: ${spacing.lg}`,
    'm-xl': `margin: ${spacing.xl}`,
    
    // Typography
    'text-xs': `font-size: ${typography.fontSize.xs}`,
    'text-sm': `font-size: ${typography.fontSize.sm}`,
    'text-base': `font-size: ${typography.fontSize.base}`,
    'text-lg': `font-size: ${typography.fontSize.lg}`,
    'text-xl': `font-size: ${typography.fontSize.xl}`,
    
    'font-light': `font-weight: ${typography.fontWeight.light}`,
    'font-normal': `font-weight: ${typography.fontWeight.normal}`,
    'font-medium': `font-weight: ${typography.fontWeight.medium}`,
    'font-semibold': `font-weight: ${typography.fontWeight.semibold}`,
    'font-bold': `font-weight: ${typography.fontWeight.bold}`,
  };
};

// Theme-aware utilities
export const createThemeAwareValue = (
  lightValue: string,
  darkValue: string,
  cssProperty: string
): string => {
  return `
    ${cssProperty}: ${lightValue};
    [data-theme="dark"] & {
      ${cssProperty}: ${darkValue};
    }
  `;
};

// Export all utilities
export const designUtils = {
  colors: {
    getValue: getColorValue,
    getContrast: getContrastColor,
    hexToRgba,
    rgbaToHex,
  },
  spacing: {
    getValue: getSpacingValue,
    createScale: createSpacingScale,
  },
  typography: {
    getFontSize,
    getFontWeight,
    getLineHeight,
    createScale: createTypographyScale,
  },
  shadows: {
    get: getShadow,
    createCustom: createCustomShadow,
  },
  borderRadius: {
    get: getBorderRadius,
    createScale: createBorderRadiusScale,
  },
  transitions: {
    get: getTransition,
    createCustom: createCustomTransition,
  },
  responsive: {
    breakpoints,
    getBreakpoint,
    createMediaQuery,
  },
  layout: {
    createGridTemplate,
    createFlexbox,
  },
  components: {
    generateButtonClasses,
    generateInputClasses,
    generateCardClasses,
  },
  animation: {
    createKeyframes,
    createAnimation,
  },
  utilities: {
    generateUtilityClasses,
    createThemeAwareValue,
  },
}; 