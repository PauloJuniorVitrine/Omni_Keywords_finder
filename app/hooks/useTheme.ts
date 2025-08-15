import { useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark' | 'system';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  resolvedTheme: 'light' | 'dark';
}

// Mock context for standalone hook usage
const createMockContext = (): ThemeContextType => {
  const [theme, setThemeState] = useState<Theme>('system');
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light');

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    if (typeof window !== 'undefined') {
      localStorage.setItem('omni-theme', newTheme);
    }
  };

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('omni-theme') as Theme;
      if (stored) {
        setThemeState(stored);
      }
    }
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const updateResolvedTheme = () => {
        let newResolvedTheme: 'light' | 'dark';
        
        if (theme === 'system') {
          newResolvedTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        } else {
          newResolvedTheme = theme;
        }
        
        setResolvedTheme(newResolvedTheme);
        document.documentElement.setAttribute('data-theme', newResolvedTheme);
        document.documentElement.classList.toggle('dark', newResolvedTheme === 'dark');
      };

      updateResolvedTheme();

      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = () => {
        if (theme === 'system') {
          updateResolvedTheme();
        }
      };

      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [theme]);

  return { theme, setTheme, resolvedTheme };
};

// Context for theme management
let ThemeContext: React.Context<ThemeContextType>;

// Initialize context
if (typeof window !== 'undefined') {
  const React = require('react');
  ThemeContext = React.createContext<ThemeContextType | undefined>(undefined);
} else {
  // Server-side fallback
  ThemeContext = {
    Provider: ({ children }: any) => children,
    Consumer: ({ children }: any) => children(createMockContext()),
  } as any;
}

export const useTheme = (): ThemeContextType => {
  try {
    const context = useContext(ThemeContext);
    if (context === undefined) {
      // Fallback to standalone hook
      return createMockContext();
    }
    return context;
  } catch {
    // Fallback to standalone hook
    return createMockContext();
  }
};

// Extended theme utilities
export const useThemeUtils = () => {
  const { theme, setTheme, resolvedTheme } = useTheme();

  const isDark = resolvedTheme === 'dark';
  const isLight = resolvedTheme === 'light';
  const isSystem = theme === 'system';

  const toggleTheme = () => {
    if (theme === 'light') {
      setTheme('dark');
    } else if (theme === 'dark') {
      setTheme('system');
    } else {
      setTheme('light');
    }
  };

  const setLightTheme = () => setTheme('light');
  const setDarkTheme = () => setTheme('dark');
  const setSystemTheme = () => setTheme('system');

  return {
    theme,
    setTheme,
    resolvedTheme,
    isDark,
    isLight,
    isSystem,
    toggleTheme,
    setLightTheme,
    setDarkTheme,
    setSystemTheme,
  };
};

// Theme-aware color utilities
export const useThemeColors = () => {
  const { resolvedTheme } = useTheme();

  const colors = {
    primary: resolvedTheme === 'dark' ? '#60a5fa' : '#3b82f6',
    secondary: resolvedTheme === 'dark' ? '#94a3b8' : '#64748b',
    success: resolvedTheme === 'dark' ? '#4ade80' : '#22c55e',
    warning: resolvedTheme === 'dark' ? '#fbbf24' : '#f59e0b',
    error: resolvedTheme === 'dark' ? '#f87171' : '#ef4444',
    background: resolvedTheme === 'dark' ? '#0f172a' : '#ffffff',
    surface: resolvedTheme === 'dark' ? '#1e293b' : '#f8fafc',
    text: resolvedTheme === 'dark' ? '#f1f5f9' : '#0f172a',
    textSecondary: resolvedTheme === 'dark' ? '#94a3b8' : '#64748b',
    border: resolvedTheme === 'dark' ? '#334155' : '#e2e8f0',
  };

  return colors;
};

// Theme-aware spacing utilities
export const useThemeSpacing = () => {
  return {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
    '3xl': '4rem',
    '4xl': '6rem',
  };
};

// Theme-aware typography utilities
export const useThemeTypography = () => {
  const { resolvedTheme } = useTheme();

  return {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      serif: ['Georgia', 'serif'],
      mono: ['JetBrains Mono', 'monospace'],
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem',
      '5xl': '3rem',
      '6xl': '3.75rem',
    },
    fontWeight: {
      light: '300',
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
      extrabold: '800',
    },
    lineHeight: {
      none: '1',
      tight: '1.25',
      snug: '1.375',
      normal: '1.5',
      relaxed: '1.625',
      loose: '2',
    },
    color: resolvedTheme === 'dark' ? '#f1f5f9' : '#0f172a',
  };
};

// Theme-aware shadow utilities
export const useThemeShadows = () => {
  const { resolvedTheme } = useTheme();

  const shadows = {
    sm: resolvedTheme === 'dark' 
      ? '0 1px 2px 0 rgb(0 0 0 / 0.3)' 
      : '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    base: resolvedTheme === 'dark'
      ? '0 1px 3px 0 rgb(0 0 0 / 0.3), 0 1px 2px -1px rgb(0 0 0 / 0.3)'
      : '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    md: resolvedTheme === 'dark'
      ? '0 4px 6px -1px rgb(0 0 0 / 0.3), 0 2px 4px -2px rgb(0 0 0 / 0.3)'
      : '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: resolvedTheme === 'dark'
      ? '0 10px 15px -3px rgb(0 0 0 / 0.3), 0 4px 6px -4px rgb(0 0 0 / 0.3)'
      : '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: resolvedTheme === 'dark'
      ? '0 20px 25px -5px rgb(0 0 0 / 0.3), 0 8px 10px -6px rgb(0 0 0 / 0.3)'
      : '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    '2xl': resolvedTheme === 'dark'
      ? '0 25px 50px -12px rgb(0 0 0 / 0.5)'
      : '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  };

  return shadows;
};

// Theme-aware transition utilities
export const useThemeTransitions = () => {
  return {
    fast: '150ms ease-in-out',
    base: '200ms ease-in-out',
    slow: '300ms ease-in-out',
    slower: '500ms ease-in-out',
  };
}; 