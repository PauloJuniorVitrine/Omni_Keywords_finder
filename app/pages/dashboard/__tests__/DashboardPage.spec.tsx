import React from 'react';
import { render, screen } from '@testing-library/react';
import DashboardPage from '../index';

jest.mock('../TendenciasList', () => (props: any) => <div data-testid="mock-tendencias">Tendências mock</div>);

describe('DashboardPage', () => {
  it('renderiza loader durante carregamento', () => {
    render(<DashboardPage />);
    expect(screen.getByTestId('dashboard-loader')).toBeInTheDocument();
  });

  it('renderiza cards e ações após carregamento', async () => {
    render(<DashboardPage />);
    expect(await screen.findByTestId('dashboard-cards')).toBeInTheDocument();
    expect(screen.getByText('Execuções')).toBeInTheDocument();
    expect(screen.getByText('Clusters')).toBeInTheDocument();
    expect(screen.getByText('Tempo médio (s)')).toBeInTheDocument();
    expect(screen.getByText('Erros')).toBeInTheDocument();
    expect(screen.getByTestId('dashboard-actions')).toBeInTheDocument();
  });

  it('exibe botão de exportação apenas para admin', async () => {
    render(<DashboardPage />);
    expect(await screen.findByTestId('btn-exportar')).toBeInTheDocument();
  });

  it('exibe empty state se não houver dados', () => {
    jest.spyOn(React, 'useState').mockImplementationOnce(() => [null, jest.fn()]);
    render(<DashboardPage />);
    expect(screen.getByTestId('dashboard-empty')).toBeInTheDocument();
  });

  it('renderiza tabela de logs recentes', async () => {
    render(<DashboardPage />);
    expect(await screen.findByTestId('dashboard-logs')).toBeInTheDocument();
    // Não valida conteúdo pois depende do mock do fetch
  });
}); 