/**
 * typography.ts
 * 
 * Sistema de tipografia padronizado para o Omni Keywords Finder
 * Tokens de tipografia centralizados seguindo padrões enterprise
 * 
 * Tracing ID: UI-005
 * Data/Hora: 2024-12-20 08:00:00 UTC
 * Versão: 1.0
 */

// Famílias de fonte
export const fontFamilies = {
  // Fontes principais
  primary: {
    sans: [
      'Inter',
      '-apple-system',
      'BlinkMacSystemFont',
      'Segoe UI',
      'Roboto',
      'Helvetica Neue',
      'Arial',
      'sans-serif'
    ].join(', '),
    serif: [
      'Georgia',
      'Times',
      'Times New Roman',
      'serif'
    ].join(', '),
    mono: [
      'SF Mono',
      'Monaco',
      'Inconsolata',
      'Roboto Mono',
      'Source Code Pro',
      'Menlo',
      'Consolas',
      'DejaVu Sans Mono',
      'monospace'
    ].join(', ')
  },
  
  // Fontes alternativas
  secondary: {
    display: [
      'Poppins',
      'Inter',
      'sans-serif'
    ].join(', '),
    body: [
      'Inter',
      'system-ui',
      'sans-serif'
    ].join(', '),
    code: [
      'JetBrains Mono',
      'Fira Code',
      'monospace'
    ].join(', ')
  }
} as const;

// Tamanhos de fonte (em rem)
export const fontSizes = {
  // Tamanhos base
  xs: '0.75rem',    // 12px
  sm: '0.875rem',   // 14px
  base: '1rem',     // 16px
  lg: '1.125rem',   // 18px
  xl: '1.25rem',    // 20px
  '2xl': '1.5rem',  // 24px
  '3xl': '1.875rem', // 30px
  '4xl': '2.25rem',  // 36px
  '5xl': '3rem',     // 48px
  '6xl': '3.75rem',  // 60px
  '7xl': '4.5rem',   // 72px
  '8xl': '6rem',     // 96px
  '9xl': '8rem'      // 128px
} as const;

// Pesos de fonte
export const fontWeights = {
  thin: 100,
  extralight: 200,
  light: 300,
  normal: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
  extrabold: 800,
  black: 900
} as const;

// Alturas de linha
export const lineHeights = {
  none: 1,
  tight: 1.25,
  snug: 1.375,
  normal: 1.5,
  relaxed: 1.625,
  loose: 2,
  // Alturas específicas para diferentes tamanhos
  xs: 1.2,
  sm: 1.4,
  base: 1.6,
  lg: 1.7,
  xl: 1.8,
  '2xl': 1.9,
  '3xl': 2,
  '4xl': 2.1,
  '5xl': 2.2,
  '6xl': 2.3
} as const;

// Espaçamentos de letra
export const letterSpacings = {
  tighter: '-0.05em',
  tight: '-0.025em',
  normal: '0em',
  wide: '0.025em',
  wider: '0.05em',
  widest: '0.1em'
} as const;

// Hierarquia tipográfica
export const typographyHierarchy = {
  // Títulos
  h1: {
    fontSize: fontSizes['4xl'],
    fontWeight: fontWeights.bold,
    lineHeight: lineHeights['4xl'],
    letterSpacing: letterSpacings.tight,
    fontFamily: fontFamilies.primary.sans
  },
  h2: {
    fontSize: fontSizes['3xl'],
    fontWeight: fontWeights.bold,
    lineHeight: lineHeights['3xl'],
    letterSpacing: letterSpacings.tight,
    fontFamily: fontFamilies.primary.sans
  },
  h3: {
    fontSize: fontSizes['2xl'],
    fontWeight: fontWeights.semibold,
    lineHeight: lineHeights['2xl'],
    letterSpacing: letterSpacings.normal,
    fontFamily: fontFamilies.primary.sans
  },
  h4: {
    fontSize: fontSizes.xl,
    fontWeight: fontWeights.semibold,
    lineHeight: lineHeights.xl,
    letterSpacing: letterSpacings.normal,
    fontFamily: fontFamilies.primary.sans
  },
  h5: {
    fontSize: fontSizes.lg,
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.lg,
    letterSpacing: letterSpacings.normal,
    fontFamily: fontFamilies.primary.sans
  },
  h6: {
    fontSize: fontSizes.base,
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.base,
    letterSpacing: letterSpacings.normal,
    fontFamily: fontFamilies.primary.sans
  },
  
  // Texto do corpo
  body: {
    fontSize: fontSizes.base,
    fontWeight: fontWeights.normal,
    lineHeight: lineHeights.base,
    letterSpacing: letterSpacings.normal,
    fontFamily: fontFamilies.primary.sans
  },
  bodyLarge: {
    fontSize: fontSizes.lg,
    fontWeight: fontWeights.normal,
    lineHeight: lineHeights.lg,
    letterSpacing: letterSpacings.normal,
    fontFamily: fontFamilies.primary.sans
  },
  bodySmall: {
    fontSize: fontSizes.sm,
    fontWeight: fontWeights.normal,
    lineHeight: lineHeights.sm,
    letterSpacing: letterSpacings.normal,
    fontFamily: fontFamilies.primary.sans
  },
  
  // Texto de interface
  caption: {
    fontSize: fontSizes.xs,
    fontWeight: fontWeights.normal,
    lineHeight: lineHeights.xs,
    letterSpacing: letterSpacings.wide,
    fontFamily: fontFamilies.primary.sans
  },
  overline: {
    fontSize: fontSizes.xs,
    fontWeight: fontWeights.medium,
    lineHeight: lineHeights.xs,
    letterSpacing: letterSpacings.widest,
    fontFamily: fontFamilies.primary.sans,
    textTransform: 'uppercase' as const
  },
  
  // Código
  code: {
    fontSize: fontSizes.sm,
    fontWeight: fontWeights.normal,
    lineHeight: lineHeights.sm,
    letterSpacing: letterSpacings.normal,
    fontFamily: fontFamilies.primary.mono
  },
  codeLarge: {
    fontSize: fontSizes.base,
    fontWeight: fontWeights.normal,
    lineHeight: lineHeights.base,
    letterSpacing: letterSpacings.normal,
    fontFamily: fontFamilies.primary.mono
  }
} as const;

// Responsividade tipográfica
export const responsiveTypography = {
  // Breakpoints para tipografia responsiva
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px'
  },
  
  // Escalas responsivas
  scales: {
    h1: {
      sm: fontSizes['3xl'],
      md: fontSizes['4xl'],
      lg: fontSizes['5xl'],
      xl: fontSizes['6xl']
    },
    h2: {
      sm: fontSizes['2xl'],
      md: fontSizes['3xl'],
      lg: fontSizes['4xl'],
      xl: fontSizes['5xl']
    },
    h3: {
      sm: fontSizes.xl,
      md: fontSizes['2xl'],
      lg: fontSizes['3xl'],
      xl: fontSizes['4xl']
    },
    body: {
      sm: fontSizes.sm,
      md: fontSizes.base,
      lg: fontSizes.lg,
      xl: fontSizes.lg
    }
  }
} as const;

// Acessibilidade tipográfica
export const accessibilityTypography = {
  // Tamanhos mínimos para acessibilidade
  minimumSizes: {
    body: '16px',
    caption: '12px',
    button: '14px'
  },
  
  // Contraste mínimo
  contrastRatios: {
    normal: 4.5,
    large: 3.0
  },
  
  // Espaçamento mínimo entre linhas
  minimumLineHeight: 1.4,
  
  // Espaçamento mínimo entre parágrafos
  minimumParagraphSpacing: '1.5em'
} as const;

// Variantes de texto
export const textVariants = {
  // Variantes de título
  title: {
    display: typographyHierarchy.h1,
    h1: typographyHierarchy.h1,
    h2: typographyHierarchy.h2,
    h3: typographyHierarchy.h3,
    h4: typographyHierarchy.h4,
    h5: typographyHierarchy.h5,
    h6: typographyHierarchy.h6
  },
  
  // Variantes de corpo
  body: {
    large: typographyHierarchy.bodyLarge,
    normal: typographyHierarchy.body,
    small: typographyHierarchy.bodySmall
  },
  
  // Variantes de interface
  ui: {
    caption: typographyHierarchy.caption,
    overline: typographyHierarchy.overline,
    button: {
      fontSize: fontSizes.sm,
      fontWeight: fontWeights.medium,
      lineHeight: lineHeights.sm,
      letterSpacing: letterSpacings.wide,
      fontFamily: fontFamilies.primary.sans
    },
    label: {
      fontSize: fontSizes.sm,
      fontWeight: fontWeights.medium,
      lineHeight: lineHeights.sm,
      letterSpacing: letterSpacings.normal,
      fontFamily: fontFamilies.primary.sans
    }
  },
  
  // Variantes de código
  code: {
    inline: typographyHierarchy.code,
    block: typographyHierarchy.codeLarge
  }
} as const;

// Classes utilitárias
export const typographyClasses = {
  // Classes de tamanho
  'text-xs': `font-size: ${fontSizes.xs}`,
  'text-sm': `font-size: ${fontSizes.sm}`,
  'text-base': `font-size: ${fontSizes.base}`,
  'text-lg': `font-size: ${fontSizes.lg}`,
  'text-xl': `font-size: ${fontSizes.xl}`,
  'text-2xl': `font-size: ${fontSizes['2xl']}`,
  'text-3xl': `font-size: ${fontSizes['3xl']}`,
  'text-4xl': `font-size: ${fontSizes['4xl']}`,
  'text-5xl': `font-size: ${fontSizes['5xl']}`,
  'text-6xl': `font-size: ${fontSizes['6xl']}`,
  
  // Classes de peso
  'font-thin': `font-weight: ${fontWeights.thin}`,
  'font-light': `font-weight: ${fontWeights.light}`,
  'font-normal': `font-weight: ${fontWeights.normal}`,
  'font-medium': `font-weight: ${fontWeights.medium}`,
  'font-semibold': `font-weight: ${fontWeights.semibold}`,
  'font-bold': `font-weight: ${fontWeights.bold}`,
  'font-extrabold': `font-weight: ${fontWeights.extrabold}`,
  'font-black': `font-weight: ${fontWeights.black}`,
  
  // Classes de altura de linha
  'leading-none': `line-height: ${lineHeights.none}`,
  'leading-tight': `line-height: ${lineHeights.tight}`,
  'leading-snug': `line-height: ${lineHeights.snug}`,
  'leading-normal': `line-height: ${lineHeights.normal}`,
  'leading-relaxed': `line-height: ${lineHeights.relaxed}`,
  'leading-loose': `line-height: ${lineHeights.loose}`,
  
  // Classes de espaçamento de letra
  'tracking-tighter': `letter-spacing: ${letterSpacings.tighter}`,
  'tracking-tight': `letter-spacing: ${letterSpacings.tight}`,
  'tracking-normal': `letter-spacing: ${letterSpacings.normal}`,
  'tracking-wide': `letter-spacing: ${letterSpacings.wide}`,
  'tracking-wider': `letter-spacing: ${letterSpacings.wider}`,
  'tracking-widest': `letter-spacing: ${letterSpacings.widest}`,
  
  // Classes de família de fonte
  'font-sans': `font-family: ${fontFamilies.primary.sans}`,
  'font-serif': `font-family: ${fontFamilies.primary.serif}`,
  'font-mono': `font-family: ${fontFamilies.primary.mono}`
} as const;

// Funções utilitárias
export const typographyUtils = {
  // Aplicar estilo tipográfico
  applyStyle: (variant: keyof typeof typographyHierarchy) => {
    const style = typographyHierarchy[variant];
    return {
      fontSize: style.fontSize,
      fontWeight: style.fontWeight,
      lineHeight: style.lineHeight,
      letterSpacing: style.letterSpacing,
      fontFamily: style.fontFamily,
      ...(style.textTransform && { textTransform: style.textTransform })
    };
  },

  // Calcular altura de linha baseada no tamanho da fonte
  calculateLineHeight: (fontSize: string, ratio: number = 1.5) => {
    const size = parseFloat(fontSize.replace('rem', ''));
    return `${size * ratio}rem`;
  },

  // Verificar se o tamanho da fonte é acessível
  isAccessibleSize: (fontSize: string) => {
    const size = parseFloat(fontSize.replace('rem', ''));
    const sizeInPx = size * 16; // 1rem = 16px
    return sizeInPx >= 12; // Mínimo 12px para acessibilidade
  },

  // Gerar escala tipográfica
  generateScale: (baseSize: number, ratio: number = 1.25) => {
    return {
      xs: `${baseSize * Math.pow(ratio, -2)}rem`,
      sm: `${baseSize * Math.pow(ratio, -1)}rem`,
      base: `${baseSize}rem`,
      lg: `${baseSize * ratio}rem`,
      xl: `${baseSize * Math.pow(ratio, 2)}rem`,
      '2xl': `${baseSize * Math.pow(ratio, 3)}rem`,
      '3xl': `${baseSize * Math.pow(ratio, 4)}rem`,
      '4xl': `${baseSize * Math.pow(ratio, 5)}rem`
    };
  },

  // Converter rem para px
  remToPx: (rem: string) => {
    const value = parseFloat(rem.replace('rem', ''));
    return `${value * 16}px`;
  },

  // Converter px para rem
  pxToRem: (px: number) => {
    return `${px / 16}rem`;
  }
} as const;

// Exportação principal
export const typography = {
  families: fontFamilies,
  sizes: fontSizes,
  weights: fontWeights,
  lineHeights,
  letterSpacings,
  hierarchy: typographyHierarchy,
  responsive: responsiveTypography,
  accessibility: accessibilityTypography,
  variants: textVariants,
  classes: typographyClasses,
  utils: typographyUtils
} as const;

export default typography; 