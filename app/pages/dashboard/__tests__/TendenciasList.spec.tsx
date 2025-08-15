import React from 'react';
import { render, screen } from '@testing-library/react';
import TendenciasList from '../TendenciasList';

describe('TendenciasList', () => {
  it('renderiza lista de tendências', () => {
    const tendencias = [
      { nome: 'Cluster A', volume: 10 },
      { nome: 'Cluster B', volume: 5 },
    ];
    render(<TendenciasList tendencias={tendencias} />);
    expect(screen.getByText('Cluster A: 10')).toBeInTheDocument();
    expect(screen.getByText('Cluster B: 5')).toBeInTheDocument();
    expect(screen.getAllByRole('img', { name: /ícone de tendência/i })).toHaveLength(2);
  });

  it('exibe mensagem de empty state', () => {
    render(<TendenciasList tendencias={[]} />);
    expect(screen.getByText(/Nenhuma tendência disponível/)).toBeInTheDocument();
  });
}); 