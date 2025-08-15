import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../ThemeProvider_v1';

const ThemeConsumer: React.FC = () => {
  const { themeName, setThemeName } = useTheme();
  return (
    <div>
      <span data-testid="theme-name">{themeName}</span>
      <button onClick={() => setThemeName('dark')}>Dark</button>
      <button onClick={() => setThemeName('light')}>Light</button>
      <button onClick={() => setThemeName('high-contrast')}>HighContrast</button>
    </div>
  );
};

describe('ThemeProvider_v1', () => {
  beforeEach(() => {
    localStorage.clear();
    document.body.removeAttribute('data-theme');
  });

  it('usa tema light por padrão', () => {
    render(<ThemeProvider><ThemeConsumer /></ThemeProvider>);
    expect(screen.getByTestId('theme-name')).toHaveTextContent('light');
    expect(document.body.getAttribute('data-theme')).toBe('light');
  });

  it('alterna para dark e high-contrast', () => {
    render(<ThemeProvider><ThemeConsumer /></ThemeProvider>);
    fireEvent.click(screen.getByText('Dark'));
    expect(screen.getByTestId('theme-name')).toHaveTextContent('dark');
    expect(document.body.getAttribute('data-theme')).toBe('dark');
    fireEvent.click(screen.getByText('HighContrast'));
    expect(screen.getByTestId('theme-name')).toHaveTextContent('high-contrast');
    expect(document.body.getAttribute('data-theme')).toBe('high-contrast');
  });

  it('persiste tema selecionado em localStorage', () => {
    render(<ThemeProvider><ThemeConsumer /></ThemeProvider>);
    fireEvent.click(screen.getByText('Dark'));
    expect(localStorage.getItem('omni_theme')).toBe('dark');
  });
}); 