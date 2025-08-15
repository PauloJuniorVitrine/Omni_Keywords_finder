import React from 'react';
import { render, screen } from '@testing-library/react';
import ResultsChart from '../ResultsChart_v1';

describe('ResultsChart_v1', () => {
  const data = [
    { categoria: 'A', score: 10 },
    { categoria: 'B', score: 20 },
    { categoria: 'C', score: 5 },
  ];

  it('renderiza gráfico de barras', () => {
    render(<ResultsChart data={data} type="bar" xKey="categoria" yKey="score" title="Bar Test" />);
    expect(screen.getByLabelText('Bar Test')).toBeInTheDocument();
    expect(screen.getByLabelText('Gráfico de barras')).toBeInTheDocument();
  });

  it('renderiza gráfico de linha', () => {
    render(<ResultsChart data={data} type="line" xKey="categoria" yKey="score" title="Line Test" />);
    expect(screen.getByLabelText('Line Test')).toBeInTheDocument();
    expect(screen.getByLabelText('Gráfico de linha')).toBeInTheDocument();
  });

  it('renderiza gráfico de pizza', () => {
    render(<ResultsChart data={data} type="pie" xKey="categoria" yKey="score" title="Pie Test" />);
    expect(screen.getByLabelText('Pie Test')).toBeInTheDocument();
    expect(screen.getByLabelText('Gráfico de pizza')).toBeInTheDocument();
  });
}); 