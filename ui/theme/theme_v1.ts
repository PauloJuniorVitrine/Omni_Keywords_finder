// Tokens de cor e estrutura de temas para ThemeProvider
// v1 — Dark/Light mode e alto contraste

export interface Theme {
  name: 'light' | 'dark' | 'high-contrast';
  colors: {
    background: string;
    surface: string;
    primary: string;
    secondary: string;
    text: string;
    textSecondary: string;
    border: string;
    hover: string;
    focus: string;
    error: string;
    success: string;
    contrast: string;
  };
  font: {
    family: string;
    size: string;
    weight: string;
  };
}

export const lightTheme: Theme = {
  name: 'light',
  colors: {
    background: '#f7fafc',
    surface: '#fff',
    primary: '#4f8cff',
    secondary: '#eab308',
    text: '#222',
    textSecondary: '#555',
    border: '#d1d5db',
    hover: '#f3f4f6',
    focus: '#a5b4fc',
    error: '#ef4444',
    success: '#22c55e',
    contrast: '#000',
  },
  font: {
    family: 'Inter, Arial, sans-serif',
    size: '16px',
    weight: '400',
  },
};

export const darkTheme: Theme = {
  name: 'dark',
  colors: {
    background: '#18181b',
    surface: '#23232a',
    primary: '#4f8cff',
    secondary: '#eab308',
    text: '#f3f4f6',
    textSecondary: '#a1a1aa',
    border: '#333',
    hover: '#27272a',
    focus: '#2563eb',
    error: '#ef4444',
    success: '#22c55e',
    contrast: '#fff',
  },
  font: {
    family: 'Inter, Arial, sans-serif',
    size: '16px',
    weight: '400',
  },
};

export const highContrastTheme: Theme = {
  name: 'high-contrast',
  colors: {
    background: '#000',
    surface: '#fff',
    primary: '#ff0',
    secondary: '#0ff',
    text: '#fff',
    textSecondary: '#ff0',
    border: '#fff',
    hover: '#222',
    focus: '#fff',
    error: '#f00',
    success: '#0f0',
    contrast: '#fff',
  },
  font: {
    family: 'Inter, Arial, sans-serif',
    size: '18px',
    weight: '700',
  },
}; 