import React from 'react';
import { useTheme, ThemeName } from './ThemeProvider_v1';
import Tooltip from './Tooltip_v1';

/**
 * Botão de alternância de tema (light/dark/high-contrast) com acessibilidade e tooltip.
 */
const ThemeToggle: React.FC = () => {
  const { themeName, setThemeName } = useTheme();
  const nextTheme: ThemeName = themeName === 'light' ? 'dark' : themeName === 'dark' ? 'high-contrast' : 'light';
  const icon = themeName === 'light' ? '🌙' : themeName === 'dark' ? '🦾' : '☀️';
  const label = themeName === 'light' ? 'Ativar modo escuro' : themeName === 'dark' ? 'Ativar alto contraste' : 'Ativar modo claro';

  return (
    <Tooltip content={label}>
      <button
        onClick={() => setThemeName(nextTheme)}
        aria-label={label}
        style={{
          background: 'none',
          border: 'none',
          borderRadius: 8,
          padding: '8px 12px',
          fontSize: 22,
          cursor: 'pointer',
          transition: 'background 0.18s',
          outline: 'none',
        }}
        onFocus={e => e.currentTarget.style.background = '#e0e7ef'}
        onBlur={e => e.currentTarget.style.background = 'none'}
      >
        <span role="img" aria-label={label}>{icon}</span>
      </button>
    </Tooltip>
  );
};

export default ThemeToggle; 