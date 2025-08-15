/**
 * shadows.ts
 * 
 * Sistema de sombras e espaçamentos padronizado para o Omni Keywords Finder
 * Tokens de design centralizados seguindo padrões enterprise
 * 
 * Tracing ID: UI-006
 * Data/Hora: 2024-12-20 08:15:00 UTC
 * Versão: 1.0
 */

// Sistema de sombras
export const shadows = {
  // Sombras básicas
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  
  // Sombras coloridas
  colored: {
    primary: '0 4px 6px -1px rgba(59, 130, 246, 0.1), 0 2px 4px -1px rgba(59, 130, 246, 0.06)',
    success: '0 4px 6px -1px rgba(34, 197, 94, 0.1), 0 2px 4px -1px rgba(34, 197, 94, 0.06)',
    warning: '0 4px 6px -1px rgba(245, 158, 11, 0.1), 0 2px 4px -1px rgba(245, 158, 11, 0.06)',
    error: '0 4px 6px -1px rgba(239, 68, 68, 0.1), 0 2px 4px -1px rgba(239, 68, 68, 0.06)',
    info: '0 4px 6px -1px rgba(59, 130, 246, 0.1), 0 2px 4px -1px rgba(59, 130, 246, 0.06)'
  },
  
  // Sombras internas
  inner: {
    sm: 'inset 0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: 'inset 0 1px 3px 0 rgba(0, 0, 0, 0.1), inset 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: 'inset 0 4px 6px -1px rgba(0, 0, 0, 0.1), inset 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: 'inset 0 10px 15px -3px rgba(0, 0, 0, 0.1), inset 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
  },
  
  // Sombras de elevação
  elevation: {
    0: 'none',
    1: '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)',
    2: '0 3px 6px rgba(0, 0, 0, 0.16), 0 3px 6px rgba(0, 0, 0, 0.23)',
    3: '0 10px 20px rgba(0, 0, 0, 0.19), 0 6px 6px rgba(0, 0, 0, 0.23)',
    4: '0 14px 28px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.22)',
    5: '0 19px 38px rgba(0, 0, 0, 0.30), 0 15px 12px rgba(0, 0, 0, 0.22)'
  }
} as const;

// Sistema de espaçamentos
export const spacing = {
  // Espaçamentos base (em rem)
  0: '0rem',
  px: '0.0625rem', // 1px
  0.5: '0.125rem',  // 2px
  1: '0.25rem',     // 4px
  1.5: '0.375rem',  // 6px
  2: '0.5rem',      // 8px
  2.5: '0.625rem',  // 10px
  3: '0.75rem',     // 12px
  3.5: '0.875rem',  // 14px
  4: '1rem',        // 16px
  5: '1.25rem',     // 20px
  6: '1.5rem',      // 24px
  7: '1.75rem',     // 28px
  8: '2rem',        // 32px
  9: '2.25rem',     // 36px
  10: '2.5rem',     // 40px
  11: '2.75rem',    // 44px
  12: '3rem',       // 48px
  14: '3.5rem',     // 56px
  16: '4rem',       // 64px
  20: '5rem',       // 80px
  24: '6rem',       // 96px
  28: '7rem',       // 112px
  32: '8rem',       // 128px
  36: '9rem',       // 144px
  40: '10rem',      // 160px
  44: '11rem',      // 176px
  48: '12rem',      // 192px
  52: '13rem',      // 208px
  56: '14rem',      // 224px
  60: '15rem',      // 240px
  64: '16rem',      // 256px
  72: '18rem',      // 288px
  80: '20rem',      // 320px
  96: '24rem'       // 384px
} as const;

// Sistema de bordas
export const borders = {
  // Raios de borda
  radius: {
    none: '0',
    sm: '0.125rem',   // 2px
    base: '0.25rem',  // 4px
    md: '0.375rem',   // 6px
    lg: '0.5rem',     // 8px
    xl: '0.75rem',    // 12px
    '2xl': '1rem',    // 16px
    '3xl': '1.5rem',  // 24px
    full: '9999px'
  },
  
  // Larguras de borda
  width: {
    0: '0px',
    DEFAULT: '1px',
    2: '2px',
    4: '4px',
    8: '8px'
  },
  
  // Estilos de borda
  style: {
    solid: 'solid',
    dashed: 'dashed',
    dotted: 'dotted',
    double: 'double',
    none: 'none'
  }
} as const;

// Sistema de elevação
export const elevation = {
  // Níveis de elevação
  levels: {
    0: {
      shadow: shadows.elevation[0],
      zIndex: 0
    },
    1: {
      shadow: shadows.elevation[1],
      zIndex: 1
    },
    2: {
      shadow: shadows.elevation[2],
      zIndex: 2
    },
    3: {
      shadow: shadows.elevation[3],
      zIndex: 3
    },
    4: {
      shadow: shadows.elevation[4],
      zIndex: 4
    },
    5: {
      shadow: shadows.elevation[5],
      zIndex: 5
    }
  },
  
  // Contextos de elevação
  contexts: {
    card: {
      shadow: shadows.md,
      zIndex: 1
    },
    modal: {
      shadow: shadows['2xl'],
      zIndex: 50
    },
    dropdown: {
      shadow: shadows.lg,
      zIndex: 40
    },
    tooltip: {
      shadow: shadows.base,
      zIndex: 30
    },
    overlay: {
      shadow: shadows.none,
      zIndex: 20
    }
  }
} as const;

// Variantes de sombra
export const shadowVariants = {
  // Variantes por contexto
  button: {
    default: shadows.base,
    hover: shadows.md,
    active: shadows.inner.base,
    disabled: shadows.none
  },
  
  card: {
    default: shadows.base,
    hover: shadows.md,
    elevated: shadows.lg,
    pressed: shadows.inner.base
  },
  
  input: {
    default: shadows.none,
    focus: shadows.sm,
    error: shadows.colored.error,
    success: shadows.colored.success
  },
  
  modal: {
    backdrop: '0 0 0 1000px rgba(0, 0, 0, 0.5)',
    content: shadows['2xl']
  },
  
  dropdown: {
    menu: shadows.lg,
    item: shadows.none,
    itemHover: shadows.sm
  }
} as const;

// Responsividade de espaçamentos
export const responsiveSpacing = {
  // Breakpoints para espaçamentos responsivos
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px'
  },
  
  // Escalas responsivas
  scales: {
    container: {
      sm: spacing[4],
      md: spacing[6],
      lg: spacing[8],
      xl: spacing[12]
    },
    
    section: {
      sm: spacing[8],
      md: spacing[12],
      lg: spacing[16],
      xl: spacing[20]
    },
    
    component: {
      sm: spacing[2],
      md: spacing[3],
      lg: spacing[4],
      xl: spacing[5]
    }
  }
} as const;

// Acessibilidade de contrastes
export const accessibilityContrasts = {
  // Contraste mínimo para sombras
  shadowContrast: {
    light: 0.05,
    medium: 0.1,
    heavy: 0.2
  },
  
  // Espaçamento mínimo para acessibilidade
  minimumSpacing: {
    touch: '44px', // Mínimo para elementos touch
    focus: '2px',  // Mínimo para indicador de foco
    text: '1.5em'  // Mínimo entre linhas de texto
  },
  
  // Bordas mínimas para acessibilidade
  minimumBorders: {
    focus: '2px',
    interactive: '1px'
  }
} as const;

// Tokens de design
export const designTokens = {
  // Tokens de espaçamento
  spacing: {
    xs: spacing[1],
    sm: spacing[2],
    md: spacing[4],
    lg: spacing[6],
    xl: spacing[8],
    '2xl': spacing[12],
    '3xl': spacing[16],
    '4xl': spacing[20]
  },
  
  // Tokens de borda
  border: {
    radius: {
      sm: borders.radius.sm,
      md: borders.radius.md,
      lg: borders.radius.lg,
      xl: borders.radius.xl
    },
    width: {
      thin: borders.width.DEFAULT,
      medium: borders.width[2],
      thick: borders.width[4]
    }
  },
  
  // Tokens de sombra
  shadow: {
    subtle: shadows.sm,
    medium: shadows.md,
    prominent: shadows.lg,
    dramatic: shadows.xl
  }
} as const;

// Classes utilitárias
export const utilityClasses = {
  // Classes de espaçamento
  'p-0': `padding: ${spacing[0]}`,
  'p-1': `padding: ${spacing[1]}`,
  'p-2': `padding: ${spacing[2]}`,
  'p-4': `padding: ${spacing[4]}`,
  'p-6': `padding: ${spacing[6]}`,
  'p-8': `padding: ${spacing[8]}`,
  
  'px-0': `padding-left: ${spacing[0]}; padding-right: ${spacing[0]}`,
  'px-1': `padding-left: ${spacing[1]}; padding-right: ${spacing[1]}`,
  'px-2': `padding-left: ${spacing[2]}; padding-right: ${spacing[2]}`,
  'px-4': `padding-left: ${spacing[4]}; padding-right: ${spacing[4]}`,
  
  'py-0': `padding-top: ${spacing[0]}; padding-bottom: ${spacing[0]}`,
  'py-1': `padding-top: ${spacing[1]}; padding-bottom: ${spacing[1]}`,
  'py-2': `padding-top: ${spacing[2]}; padding-bottom: ${spacing[2]}`,
  'py-4': `padding-top: ${spacing[4]}; padding-bottom: ${spacing[4]}`,
  
  'm-0': `margin: ${spacing[0]}`,
  'm-1': `margin: ${spacing[1]}`,
  'm-2': `margin: ${spacing[2]}`,
  'm-4': `margin: ${spacing[4]}`,
  'm-6': `margin: ${spacing[6]}`,
  'm-8': `margin: ${spacing[8]}`,
  
  'mx-0': `margin-left: ${spacing[0]}; margin-right: ${spacing[0]}`,
  'mx-1': `margin-left: ${spacing[1]}; margin-right: ${spacing[1]}`,
  'mx-2': `margin-left: ${spacing[2]}; margin-right: ${spacing[2]}`,
  'mx-4': `margin-left: ${spacing[4]}; margin-right: ${spacing[4]}`,
  
  'my-0': `margin-top: ${spacing[0]}; margin-bottom: ${spacing[0]}`,
  'my-1': `margin-top: ${spacing[1]}; margin-bottom: ${spacing[1]}`,
  'my-2': `margin-top: ${spacing[2]}; margin-bottom: ${spacing[2]}`,
  'my-4': `margin-top: ${spacing[4]}; margin-bottom: ${spacing[4]}`,
  
  // Classes de borda
  'border-0': `border-width: ${borders.width[0]}`,
  'border': `border-width: ${borders.width.DEFAULT}`,
  'border-2': `border-width: ${borders.width[2]}`,
  'border-4': `border-width: ${borders.width[4]}`,
  
  'rounded-none': `border-radius: ${borders.radius.none}`,
  'rounded-sm': `border-radius: ${borders.radius.sm}`,
  'rounded': `border-radius: ${borders.radius.base}`,
  'rounded-md': `border-radius: ${borders.radius.md}`,
  'rounded-lg': `border-radius: ${borders.radius.lg}`,
  'rounded-xl': `border-radius: ${borders.radius.xl}`,
  'rounded-2xl': `border-radius: ${borders.radius['2xl']}`,
  'rounded-full': `border-radius: ${borders.radius.full}`,
  
  // Classes de sombra
  'shadow-none': `box-shadow: ${shadows.none}`,
  'shadow-sm': `box-shadow: ${shadows.sm}`,
  'shadow': `box-shadow: ${shadows.base}`,
  'shadow-md': `box-shadow: ${shadows.md}`,
  'shadow-lg': `box-shadow: ${shadows.lg}`,
  'shadow-xl': `box-shadow: ${shadows.xl}`,
  'shadow-2xl': `box-shadow: ${shadows['2xl']}`,
  
  'shadow-inner': `box-shadow: ${shadows.inner.base}`,
  'shadow-inner-sm': `box-shadow: ${shadows.inner.sm}`,
  'shadow-inner-md': `box-shadow: ${shadows.inner.md}`,
  'shadow-inner-lg': `box-shadow: ${shadows.inner.lg}`
} as const;

// Funções utilitárias
export const shadowUtils = {
  // Aplicar sombra por contexto
  applyShadow: (context: keyof typeof shadowVariants, state: string = 'default') => {
    const contextShadows = shadowVariants[context];
    return contextShadows[state as keyof typeof contextShadows] || contextShadows.default;
  },

  // Aplicar elevação
  applyElevation: (level: keyof typeof elevation.levels) => {
    const elevationLevel = elevation.levels[level];
    return {
      boxShadow: elevationLevel.shadow,
      zIndex: elevationLevel.zIndex
    };
  },

  // Calcular espaçamento responsivo
  getResponsiveSpacing: (type: keyof typeof responsiveSpacing.scales, breakpoint: string) => {
    const scale = responsiveSpacing.scales[type];
    return scale[breakpoint as keyof typeof scale] || scale.md;
  },

  // Gerar sombra customizada
  generateShadow: (x: number, y: number, blur: number, spread: number, color: string, opacity: number = 0.1) => {
    return `${x}px ${y}px ${blur}px ${spread}px ${color}${Math.round(opacity * 255).toString(16).padStart(2, '0')}`;
  },

  // Converter rem para px
  remToPx: (rem: string) => {
    const value = parseFloat(rem.replace('rem', ''));
    return `${value * 16}px`;
  },

  // Converter px para rem
  pxToRem: (px: number) => {
    return `${px / 16}rem`;
  },

  // Verificar se espaçamento é acessível
  isAccessibleSpacing: (spacingValue: string) => {
    const value = parseFloat(spacingValue.replace('rem', ''));
    const valueInPx = value * 16;
    return valueInPx >= 4; // Mínimo 4px para acessibilidade
  },

  // Gerar escala de espaçamentos
  generateSpacingScale: (baseSize: number, ratio: number = 1.5) => {
    return {
      xs: `${baseSize * Math.pow(ratio, -2)}rem`,
      sm: `${baseSize * Math.pow(ratio, -1)}rem`,
      md: `${baseSize}rem`,
      lg: `${baseSize * ratio}rem`,
      xl: `${baseSize * Math.pow(ratio, 2)}rem`,
      '2xl': `${baseSize * Math.pow(ratio, 3)}rem`
    };
  }
} as const;

// Exportação principal
export const shadowsAndSpacing = {
  shadows,
  spacing,
  borders,
  elevation,
  variants: shadowVariants,
  responsive: responsiveSpacing,
  accessibility: accessibilityContrasts,
  tokens: designTokens,
  classes: utilityClasses,
  utils: shadowUtils
} as const;

export default shadowsAndSpacing; 