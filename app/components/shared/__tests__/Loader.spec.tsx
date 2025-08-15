import React from 'react';
import { render, screen } from '@testing-library/react';
import Loader from '../Loader';

describe('Loader', () => {
  it('renderiza loader padrão', () => {
    render(<Loader />);
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByLabelText('Carregando')).toBeInTheDocument();
  });

  it('renderiza loader grande', () => {
    render(<Loader size="large" />);
    const svg = screen.getByRole('status').querySelector('svg');
    expect(svg).toHaveAttribute('width', '36');
  });

  it('aplica cor customizada', () => {
    render(<Loader color="#eab308" />);
    const circle = screen.getByRole('status').querySelector('circle');
    expect(circle).toHaveAttribute('stroke', '#eab308');
  });
}); 