import React from 'react';
import { render, screen } from '@testing-library/react';
import Badge from '../Badge';

describe('Badge', () => {
  it('renderiza label e cor padrão', () => {
    render(<Badge label="Ativo" />);
    expect(screen.getByText('Ativo')).toBeInTheDocument();
    expect(screen.getByText('Ativo')).toHaveStyle('background: #22c55e');
  });

  it('aplica cor customizada', () => {
    render(<Badge label="Erro" color="#ef4444" />);
    expect(screen.getByText('Erro')).toHaveStyle('background: #ef4444');
  });

  it('é acessível via aria-label', () => {
    render(<Badge label="Acessível" />);
    expect(screen.getByLabelText('Status: Acessível')).toBeInTheDocument();
  });
}); 