import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { lightTheme, darkTheme, highContrastTheme, Theme } from '../../../ui/theme/theme_v1';

/**
 * Contexto e provider global para alternância de tema (light/dark/high-contrast).
 * Persiste escolha do usuário em localStorage.
 */
export type ThemeName = 'light' | 'dark' | 'high-contrast';

interface ThemeContextProps {
  theme: Theme;
  themeName: ThemeName;
  setThemeName: (name: ThemeName) => void;
}

const ThemeContext = createContext<ThemeContextProps>({
  theme: lightTheme,
  themeName: 'light',
  setThemeName: () => {},
});

const THEME_KEY = 'omni_theme';

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [themeName, setThemeName] = useState<ThemeName>('light');

  useEffect(() => {
    const saved = localStorage.getItem(THEME_KEY) as ThemeName | null;
    if (saved && ['light', 'dark', 'high-contrast'].includes(saved)) {
      setThemeName(saved);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(THEME_KEY, themeName);
    document.body.setAttribute('data-theme', themeName);
  }, [themeName]);

  const theme =
    themeName === 'dark' ? darkTheme :
    themeName === 'high-contrast' ? highContrastTheme :
    lightTheme;

  return (
    <ThemeContext.Provider value={{ theme, themeName, setThemeName }}>
      <div style={{ background: theme.colors.background, color: theme.colors.text, minHeight: '100vh', fontFamily: theme.font.family }}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
};

export const useTheme = () => useContext(ThemeContext); 