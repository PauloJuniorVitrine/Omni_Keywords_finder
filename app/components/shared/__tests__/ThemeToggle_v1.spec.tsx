import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from '../ThemeProvider_v1';
import ThemeToggle from '../ThemeToggle_v1';

describe('ThemeToggle_v1', () => {
  it('renderiza botão e tooltip', () => {
    render(<ThemeProvider><ThemeToggle /></ThemeProvider>);
    expect(screen.getByRole('button')).toBeInTheDocument();
    fireEvent.mouseEnter(screen.getByRole('button'));
    expect(screen.getByRole('tooltip')).toBeInTheDocument();
  });

  it('alterna tema ao clicar', () => {
    render(<ThemeProvider><ThemeToggle /></ThemeProvider>);
    const btn = screen.getByRole('button');
    expect(document.body.getAttribute('data-theme')).toBe('light');
    fireEvent.click(btn);
    expect(document.body.getAttribute('data-theme')).toBe('dark');
    fireEvent.click(btn);
    expect(document.body.getAttribute('data-theme')).toBe('high-contrast');
    fireEvent.click(btn);
    expect(document.body.getAttribute('data-theme')).toBe('light');
  });

  it('é acessível via aria-label', () => {
    render(<ThemeProvider><ThemeToggle /></ThemeProvider>);
    expect(screen.getByLabelText(/modo/i)).toBeInTheDocument();
  });
}); 