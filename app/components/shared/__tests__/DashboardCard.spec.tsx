import React from 'react';
import { render, screen } from '@testing-library/react';
import DashboardCard from '../DashboardCard';

describe('DashboardCard', () => {
  it('renderiza título, valor e status', () => {
    render(<DashboardCard title="Test Card" value={42} status="Ativo" />);
    expect(screen.getByText('Test Card')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByLabelText(/Card: Test Card/)).toBeInTheDocument();
    expect(screen.getByText('Ativo')).toBeInTheDocument();
  });

  it('exibe badge com cor customizada', () => {
    render(<DashboardCard title="Card" value={1} status="Erro" badgeColor="#ef4444" />);
    const badge = screen.getByText('Erro');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveStyle('background: #ef4444');
  });

  it('é acessível via aria-label', () => {
    render(<DashboardCard title="Acessível" value={0} />);
    expect(screen.getByLabelText(/Card: Acessível/)).toBeInTheDocument();
  });
}); 