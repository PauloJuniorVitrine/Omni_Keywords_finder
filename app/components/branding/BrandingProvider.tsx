/**
 * BrandingProvider.tsx
 * 
 * Provider centralizado para configuração de branding e temas
 * 
 * Tracing ID: UI_BRANDING_PROVIDER_20250127_001
 * Prompt: CHECKLIST_INTERFACE_ENTERPRISE_DEFINITIVA.md - Item 14.2
 * Ruleset: enterprise_control_layer.yaml
 * Data: 2025-01-27
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Tipos de configuração de branding
interface BrandingConfig {
  // Cores principais
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    success: string;
    warning: string;
    error: string;
    info: string;
    background: string;
    surface: string;
    text: {
      primary: string;
      secondary: string;
      disabled: string;
    };
  };

  // Tipografia
  typography: {
    fontFamily: {
      primary: string;
      secondary: string;
      mono: string;
    };
    fontSize: {
      xs: string;
      sm: string;
      base: string;
      lg: string;
      xl: string;
      '2xl': string;
      '3xl': string;
      '4xl': string;
    };
    fontWeight: {
      light: number;
      normal: number;
      medium: number;
      semibold: number;
      bold: number;
    };
  };

  // Espaçamento
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
    '2xl': string;
    '3xl': string;
  };

  // Bordas e sombras
  borders: {
    radius: {
      sm: string;
      md: string;
      lg: string;
      xl: string;
      full: string;
    };
    width: {
      thin: string;
      normal: string;
      thick: string;
    };
  };

  shadows: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
    '2xl': string;
  };

  // Animações
  animations: {
    duration: {
      fast: string;
      normal: string;
      slow: string;
    };
    easing: {
      linear: string;
      ease: string;
      easeIn: string;
      easeOut: string;
      easeInOut: string;
    };
  };

  // Logo e marca
  logo: {
    url: string;
    alt: string;
    width: string;
    height: string;
  };

  // Configurações específicas
  features: {
    enableAnimations: boolean;
    enableShadows: boolean;
    enableGradients: boolean;
    enableRoundedCorners: boolean;
  };
}

// Configuração padrão
const defaultBrandingConfig: BrandingConfig = {
  colors: {
    primary: '#3B82F6',
    secondary: '#1E40AF',
    accent: '#60A5FA',
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#06B6D4',
    background: '#FFFFFF',
    surface: '#F9FAFB',
    text: {
      primary: '#1F2937',
      secondary: '#6B7280',
      disabled: '#9CA3AF'
    }
  },
  typography: {
    fontFamily: {
      primary: 'Inter, system-ui, sans-serif',
      secondary: 'Poppins, system-ui, sans-serif',
      mono: 'JetBrains Mono, monospace'
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem'
    },
    fontWeight: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700
    }
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
    '3xl': '4rem'
  },
  borders: {
    radius: {
      sm: '0.125rem',
      md: '0.375rem',
      lg: '0.5rem',
      xl: '0.75rem',
      full: '9999px'
    },
    width: {
      thin: '1px',
      normal: '2px',
      thick: '4px'
    }
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
  },
  animations: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '500ms'
    },
    easing: {
      linear: 'linear',
      ease: 'ease',
      easeIn: 'ease-in',
      easeOut: 'ease-out',
      easeInOut: 'ease-in-out'
    }
  },
  logo: {
    url: '/logo.svg',
    alt: 'Omni Keywords Finder',
    width: '32px',
    height: '32px'
  },
  features: {
    enableAnimations: true,
    enableShadows: true,
    enableGradients: true,
    enableRoundedCorners: true
  }
};

// Configuração para tema escuro
const darkBrandingConfig: BrandingConfig = {
  ...defaultBrandingConfig,
  colors: {
    ...defaultBrandingConfig.colors,
    background: '#111827',
    surface: '#1F2937',
    text: {
      primary: '#F9FAFB',
      secondary: '#D1D5DB',
      disabled: '#6B7280'
    }
  }
};

// Contexto do branding
interface BrandingContextType {
  config: BrandingConfig;
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
  updateConfig: (updates: Partial<BrandingConfig>) => void;
  resetConfig: () => void;
  getCSSVariables: () => Record<string, string>;
}

const BrandingContext = createContext<BrandingContextType | undefined>(undefined);

// Hook para usar o branding
export const useBranding = () => {
  const context = useContext(BrandingContext);
  if (!context) {
    throw new Error('useBranding must be used within a BrandingProvider');
  }
  return context;
};

// Props do provider
interface BrandingProviderProps {
  children: ReactNode;
  initialConfig?: Partial<BrandingConfig>;
  initialTheme?: 'light' | 'dark';
  enableThemeToggle?: boolean;
  enableConfigPersistence?: boolean;
}

export const BrandingProvider: React.FC<BrandingProviderProps> = ({
  children,
  initialConfig = {},
  initialTheme = 'light',
  enableThemeToggle = true,
  enableConfigPersistence = true
}) => {
  const [config, setConfig] = useState<BrandingConfig>({
    ...defaultBrandingConfig,
    ...initialConfig
  });
  const [theme, setThemeState] = useState<'light' | 'dark'>(initialTheme);

  // Carregar configuração salva
  useEffect(() => {
    if (enableConfigPersistence) {
      const savedConfig = localStorage.getItem('branding-config');
      const savedTheme = localStorage.getItem('branding-theme');
      
      if (savedConfig) {
        try {
          const parsedConfig = JSON.parse(savedConfig);
          setConfig(prev => ({ ...prev, ...parsedConfig }));
        } catch (error) {
          console.warn('Erro ao carregar configuração de branding:', error);
        }
      }
      
      if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
        setThemeState(savedTheme);
      }
    }
  }, [enableConfigPersistence]);

  // Salvar configuração
  useEffect(() => {
    if (enableConfigPersistence) {
      localStorage.setItem('branding-config', JSON.stringify(config));
    }
  }, [config, enableConfigPersistence]);

  // Salvar tema
  useEffect(() => {
    if (enableConfigPersistence) {
      localStorage.setItem('branding-theme', theme);
    }
    
    // Aplicar tema ao documento
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme, enableConfigPersistence]);

  // Atualizar configuração
  const updateConfig = (updates: Partial<BrandingConfig>) => {
    setConfig(prev => ({ ...prev, ...updates }));
  };

  // Resetar configuração
  const resetConfig = () => {
    setConfig(defaultBrandingConfig);
    setThemeState('light');
  };

  // Definir tema
  const setTheme = (newTheme: 'light' | 'dark') => {
    if (enableThemeToggle) {
      setThemeState(newTheme);
    }
  };

  // Gerar variáveis CSS
  const getCSSVariables = (): Record<string, string> => {
    const currentConfig = theme === 'dark' ? darkBrandingConfig : config;
    
    return {
      // Cores
      '--color-primary': currentConfig.colors.primary,
      '--color-secondary': currentConfig.colors.secondary,
      '--color-accent': currentConfig.colors.accent,
      '--color-success': currentConfig.colors.success,
      '--color-warning': currentConfig.colors.warning,
      '--color-error': currentConfig.colors.error,
      '--color-info': currentConfig.colors.info,
      '--color-background': currentConfig.colors.background,
      '--color-surface': currentConfig.colors.surface,
      '--color-text-primary': currentConfig.colors.text.primary,
      '--color-text-secondary': currentConfig.colors.text.secondary,
      '--color-text-disabled': currentConfig.colors.text.disabled,
      
      // Tipografia
      '--font-family-primary': currentConfig.typography.fontFamily.primary,
      '--font-family-secondary': currentConfig.typography.fontFamily.secondary,
      '--font-family-mono': currentConfig.typography.fontFamily.mono,
      '--font-size-xs': currentConfig.typography.fontSize.xs,
      '--font-size-sm': currentConfig.typography.fontSize.sm,
      '--font-size-base': currentConfig.typography.fontSize.base,
      '--font-size-lg': currentConfig.typography.fontSize.lg,
      '--font-size-xl': currentConfig.typography.fontSize.xl,
      '--font-size-2xl': currentConfig.typography.fontSize['2xl'],
      '--font-size-3xl': currentConfig.typography.fontSize['3xl'],
      '--font-size-4xl': currentConfig.typography.fontSize['4xl'],
      '--font-weight-light': currentConfig.typography.fontWeight.light.toString(),
      '--font-weight-normal': currentConfig.typography.fontWeight.normal.toString(),
      '--font-weight-medium': currentConfig.typography.fontWeight.medium.toString(),
      '--font-weight-semibold': currentConfig.typography.fontWeight.semibold.toString(),
      '--font-weight-bold': currentConfig.typography.fontWeight.bold.toString(),
      
      // Espaçamento
      '--spacing-xs': currentConfig.spacing.xs,
      '--spacing-sm': currentConfig.spacing.sm,
      '--spacing-md': currentConfig.spacing.md,
      '--spacing-lg': currentConfig.spacing.lg,
      '--spacing-xl': currentConfig.spacing.xl,
      '--spacing-2xl': currentConfig.spacing['2xl'],
      '--spacing-3xl': currentConfig.spacing['3xl'],
      
      // Bordas
      '--border-radius-sm': currentConfig.borders.radius.sm,
      '--border-radius-md': currentConfig.borders.radius.md,
      '--border-radius-lg': currentConfig.borders.radius.lg,
      '--border-radius-xl': currentConfig.borders.radius.xl,
      '--border-radius-full': currentConfig.borders.radius.full,
      '--border-width-thin': currentConfig.borders.width.thin,
      '--border-width-normal': currentConfig.borders.width.normal,
      '--border-width-thick': currentConfig.borders.width.thick,
      
      // Sombras
      '--shadow-sm': currentConfig.shadows.sm,
      '--shadow-md': currentConfig.shadows.md,
      '--shadow-lg': currentConfig.shadows.lg,
      '--shadow-xl': currentConfig.shadows.xl,
      '--shadow-2xl': currentConfig.shadows['2xl'],
      
      // Animações
      '--animation-duration-fast': currentConfig.animations.duration.fast,
      '--animation-duration-normal': currentConfig.animations.duration.normal,
      '--animation-duration-slow': currentConfig.animations.duration.slow,
      '--animation-easing-linear': currentConfig.animations.easing.linear,
      '--animation-easing-ease': currentConfig.animations.easing.ease,
      '--animation-easing-ease-in': currentConfig.animations.easing.easeIn,
      '--animation-easing-ease-out': currentConfig.animations.easing.easeOut,
      '--animation-easing-ease-in-out': currentConfig.animations.easing.easeInOut
    };
  };

  // Aplicar variáveis CSS ao documento
  useEffect(() => {
    const cssVariables = getCSSVariables();
    const root = document.documentElement;
    
    Object.entries(cssVariables).forEach(([property, value]) => {
      root.style.setProperty(property, value);
    });
  }, [config, theme]);

  const contextValue: BrandingContextType = {
    config,
    theme,
    setTheme,
    updateConfig,
    resetConfig,
    getCSSVariables
  };

  return (
    <BrandingContext.Provider value={contextValue}>
      {children}
    </BrandingContext.Provider>
  );
};

// Componente para aplicar estilos globais
export const BrandingStyles: React.FC = () => {
  const { config, theme } = useBranding();
  
  const currentConfig = theme === 'dark' ? darkBrandingConfig : config;

  return (
    <style jsx global>{`
      :root {
        /* Aplicar variáveis CSS */
        --color-primary: ${currentConfig.colors.primary};
        --color-secondary: ${currentConfig.colors.secondary};
        --color-accent: ${currentConfig.colors.accent};
        --color-success: ${currentConfig.colors.success};
        --color-warning: ${currentConfig.colors.warning};
        --color-error: ${currentConfig.colors.error};
        --color-info: ${currentConfig.colors.info};
        --color-background: ${currentConfig.colors.background};
        --color-surface: ${currentConfig.colors.surface};
        --color-text-primary: ${currentConfig.colors.text.primary};
        --color-text-secondary: ${currentConfig.colors.text.secondary};
        --color-text-disabled: ${currentConfig.colors.text.disabled};
        
        /* Tipografia */
        --font-family-primary: ${currentConfig.typography.fontFamily.primary};
        --font-family-secondary: ${currentConfig.typography.fontFamily.secondary};
        --font-family-mono: ${currentConfig.typography.fontFamily.mono};
        
        /* Animações */
        --animation-duration-fast: ${currentConfig.animations.duration.fast};
        --animation-duration-normal: ${currentConfig.animations.duration.normal};
        --animation-duration-slow: ${currentConfig.animations.duration.slow};
        --animation-easing-linear: ${currentConfig.animations.easing.linear};
        --animation-easing-ease: ${currentConfig.animations.easing.ease};
        --animation-easing-ease-in: ${currentConfig.animations.easing.easeIn};
        --animation-easing-ease-out: ${currentConfig.animations.easing.easeOut};
        --animation-easing-ease-in-out: ${currentConfig.animations.easing.easeInOut};
      }

      /* Estilos globais baseados na configuração */
      body {
        font-family: var(--font-family-primary);
        background-color: var(--color-background);
        color: var(--color-text-primary);
        transition: background-color var(--animation-duration-normal) var(--animation-easing-ease-in-out);
      }

      /* Animações condicionais */
      ${currentConfig.features.enableAnimations ? `
        * {
          transition: all var(--animation-duration-normal) var(--animation-easing-ease-in-out);
        }
      ` : ''}

      /* Sombras condicionais */
      ${currentConfig.features.enableShadows ? `
        .shadow-sm { box-shadow: var(--shadow-sm); }
        .shadow-md { box-shadow: var(--shadow-md); }
        .shadow-lg { box-shadow: var(--shadow-lg); }
        .shadow-xl { box-shadow: var(--shadow-xl); }
        .shadow-2xl { box-shadow: var(--shadow-2xl); }
      ` : ''}

      /* Bordas arredondadas condicionais */
      ${currentConfig.features.enableRoundedCorners ? `
        .rounded-sm { border-radius: var(--border-radius-sm); }
        .rounded-md { border-radius: var(--border-radius-md); }
        .rounded-lg { border-radius: var(--border-radius-lg); }
        .rounded-xl { border-radius: var(--border-radius-xl); }
        .rounded-full { border-radius: var(--border-radius-full); }
      ` : ''}

      /* Gradientes condicionais */
      ${currentConfig.features.enableGradients ? `
        .gradient-primary {
          background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
        }
        .gradient-accent {
          background: linear-gradient(135deg, var(--color-accent), var(--color-primary));
        }
      ` : ''}
    `}</style>
  );
};

export default BrandingProvider; 