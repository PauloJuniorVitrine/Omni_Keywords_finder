import React from 'react';
import { render, screen } from '@testing-library/react';
import PainelLogs from '../painel_logs';

describe('PainelLogs', () => {
  it('renderiza corretamente com props mínimas', () => {
    render(<PainelLogs logs={[]} />);
    expect(screen.getByTestId('painel-logs')).toBeInTheDocument();
  });

  it('renderiza lista de logs reais', () => {
    const logs = [
      { id: 1, mensagem: 'Log 1', tipo: 'info', data: '2024-06-11T10:00:00Z' },
      { id: 2, mensagem: 'Log 2', tipo: 'erro', data: '2024-06-11T11:00:00Z' }
    ];
    render(<PainelLogs logs={logs} />);
    expect(screen.getByText('Log 1')).toBeInTheDocument();
    expect(screen.getByText('Log 2')).toBeInTheDocument();
  });

  it('exibe fallback para lista vazia', () => {
    render(<PainelLogs logs={[]} />);
    expect(screen.getByTestId('painel-logs')).toBeInTheDocument();
    expect(screen.getByText(/nenhum log/i)).toBeInTheDocument();
  });

  it('possui atributos de acessibilidade', () => {
    render(<PainelLogs logs={[]} />);
    const painel = screen.getByTestId('painel-logs');
    expect(painel).toHaveAttribute('role', 'region');
    expect(painel).toHaveAttribute('aria-label');
  });
}); 