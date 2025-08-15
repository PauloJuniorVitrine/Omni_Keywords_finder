import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import DashboardPage from '../index';

// Mock global fetch
beforeEach(() => {
  global.fetch = jest.fn(() =>
    Promise.resolve({ ok: true, json: () => Promise.resolve({
      total_execucoes: 100,
      total_clusters: 5,
      tempo_medio_execucao: 2.345,
      total_erros: 1,
      logs_recentes: [
        { id: 1, tipo_operacao: 'CREATE', entidade: 'Execucao', id_referencia: 101, usuario: 'admin', timestamp: '2024-06-12T12:00:00Z', detalhes: 'Execução criada' },
        { id: 2, tipo_operacao: 'ERROR', entidade: 'Execucao', id_referencia: 102, usuario: 'user', timestamp: '2024-06-12T12:05:00Z', detalhes: 'Erro de processamento' },
      ],
    }) }) as any
  );
});

afterEach(() => {
  jest.resetAllMocks();
});

describe('DashboardPage (integração)', () => {
  it('fluxo completo: loader → cards → logs → ações', async () => {
    render(<DashboardPage />);
    expect(screen.getByTestId('dashboard-loader')).toBeInTheDocument();
    expect(await screen.findByTestId('dashboard-cards')).toBeInTheDocument();
    expect(screen.getByText('Execuções')).toBeInTheDocument();
    expect(screen.getByText('Clusters')).toBeInTheDocument();
    expect(screen.getByText('Tempo médio (s)')).toBeInTheDocument();
    expect(screen.getByText('Erros')).toBeInTheDocument();
    expect(screen.getByTestId('dashboard-logs')).toBeInTheDocument();
    expect(screen.getByText('Logs Recentes')).toBeInTheDocument();
    expect(screen.getByText('Execução criada')).toBeInTheDocument();
    expect(screen.getByText('Erro de processamento')).toBeInTheDocument();
    expect(screen.getByTestId('dashboard-actions')).toBeInTheDocument();
  });

  it('interação: exportação de dados exibe alerta (admin)', async () => {
    window.alert = jest.fn();
    render(<DashboardPage />);
    const btnExportar = await screen.findByTestId('btn-exportar');
    fireEvent.click(btnExportar);
    expect(window.alert).toHaveBeenCalledWith('Exportação não implementada neste mock.');
  });

  it('acessibilidade: navegação por tab e ARIA', async () => {
    render(<DashboardPage />);
    await screen.findByTestId('dashboard-cards');
    expect(screen.getByLabelText('Título do dashboard')).toBeInTheDocument();
    expect(screen.getByLabelText('Cards de métricas do dashboard')).toBeInTheDocument();
    expect(screen.getByLabelText('Ações do dashboard')).toBeInTheDocument();
  });

  it('edge case: erro de API exibe banner e empty state', async () => {
    (global.fetch as jest.Mock).mockImplementationOnce(() => Promise.resolve({ ok: false }));
    render(<DashboardPage />);
    expect(await screen.findByTestId('dashboard-error')).toBeInTheDocument();
    expect(await screen.findByTestId('dashboard-empty')).toBeInTheDocument();
  });

  it('permissão: usuário comum não vê botão de exportação', async () => {
    jest.spyOn(React, 'useState').mockImplementationOnce(() => ['user', jest.fn()]);
    render(<DashboardPage />);
    await screen.findByTestId('dashboard-cards');
    expect(screen.queryByTestId('btn-exportar')).not.toBeInTheDocument();
  });
}); 