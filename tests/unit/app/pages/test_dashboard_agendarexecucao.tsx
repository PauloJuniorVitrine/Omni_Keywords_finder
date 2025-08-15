import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AgendarExecucao from '../../../../../../app/pages/dashboard/AgendarExecucao';

beforeEach(() => {
  global.fetch = jest.fn((url) => {
    if (typeof url === 'string' && url.includes('/api/categorias/1/')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([
          { id: 1, nome: 'Categoria 1' },
          { id: 2, nome: 'Categoria 2' },
        ]),
      });
    }
    if (typeof url === 'string' && url.includes('/api/execucoes/agendadas')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([
          {
            id: 1,
            categoria_id: 1,
            palavras_chave: ['teste'],
            data_agendada: new Date().toISOString(),
            status: 'pendente',
            usuario: 'user',
            criado_em: new Date().toISOString(),
          },
        ]),
      });
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({ sugestoes: [] }) });
  }) as jest.Mock;
});

afterEach(() => {
  jest.clearAllMocks();
});

describe('AgendarExecucao (Dashboard)', () => {
  it('renderiza skeletons durante carregamento', async () => {
    render(<AgendarExecucao />);
    expect(screen.getAllByLabelText('Carregando...').length).toBeGreaterThan(0);
    await waitFor(() => expect(screen.queryByLabelText('Carregando...')).not.toBeInTheDocument());
  });

  it('exibe execuções agendadas após carregamento', async () => {
    render(<AgendarExecucao />);
    await waitFor(() => expect(screen.getByText('Categoria 1')).toBeInTheDocument());
    expect(screen.getByText('pendente')).toBeInTheDocument();
  });

  it('exibe tooltip ao focar no botão "Agendar"', async () => {
    render(<AgendarExecucao />);
    const btn = screen.getByRole('button', { name: /agendar/i });
    fireEvent.mouseEnter(btn);
    expect(await screen.findByRole('tooltip')).toBeInTheDocument();
  });

  it('exibe tooltip ao focar no botão "Cancelar"', async () => {
    render(<AgendarExecucao />);
    await waitFor(() => expect(screen.getByText('Cancelar')).toBeInTheDocument());
    const btn = screen.getByText('Cancelar');
    fireEvent.mouseEnter(btn);
    expect(await screen.findByRole('tooltip')).toBeInTheDocument();
  });

  it('é acessível via teclado', async () => {
    render(<AgendarExecucao />);
    await waitFor(() => expect(screen.getByText('Categoria 1')).toBeInTheDocument());
    const btn = screen.getByText('Cancelar');
    btn.focus();
    expect(btn).toHaveFocus();
  });
}); 