import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Notifications from '../../../../../../app/pages/dashboard/Notifications';

// Mock fetch global
beforeEach(() => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve([
        { id: 1, titulo: 'Info', mensagem: 'Mensagem info', tipo: 'info', lida: false, timestamp: new Date().toISOString() },
        { id: 2, titulo: 'Erro', mensagem: 'Mensagem erro', tipo: 'error', lida: false, timestamp: new Date().toISOString() },
      ]),
    })
  ) as jest.Mock;
});

afterEach(() => {
  jest.clearAllMocks();
});

describe('Notifications (Dashboard)', () => {
  it('renderiza skeletons durante carregamento', async () => {
    render(<Notifications />);
    expect(screen.getAllByLabelText('Carregando...').length).toBeGreaterThan(0);
    await waitFor(() => expect(screen.queryByLabelText('Carregando...')).not.toBeInTheDocument());
  });

  it('exibe notificações após carregamento', async () => {
    render(<Notifications />);
    await waitFor(() => expect(screen.getByText('Info')).toBeInTheDocument());
    expect(screen.getByText('Mensagem info')).toBeInTheDocument();
    expect(screen.getByText('Mensagem erro')).toBeInTheDocument();
  });

  it('exibe tooltip ao focar no botão de atualização', async () => {
    render(<Notifications />);
    const btn = screen.getByRole('button', { name: /atualiza/i });
    fireEvent.mouseEnter(btn);
    expect(await screen.findByRole('tooltip')).toBeInTheDocument();
  });

  it('exibe tooltip ao focar no botão "Marcar como lida"', async () => {
    render(<Notifications />);
    await waitFor(() => expect(screen.getByText('Marcar como lida')).toBeInTheDocument());
    const btn = screen.getByText('Marcar como lida');
    fireEvent.mouseEnter(btn);
    expect(await screen.findByRole('tooltip')).toBeInTheDocument();
  });

  it('é acessível via teclado', async () => {
    render(<Notifications />);
    await waitFor(() => expect(screen.getByText('Info')).toBeInTheDocument());
    const btn = screen.getByText('Marcar como lida');
    btn.focus();
    expect(btn).toHaveFocus();
  });
}); 