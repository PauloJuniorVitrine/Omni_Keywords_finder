import '@testing-library/jest-dom';
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import GovernancaPage from '../../../pages/governanca/index';

// Mock global fetch
const originalFetch = global.fetch;

describe('Integração: Upload de Regras', () => {
  afterEach(() => {
    global.fetch = originalFetch;
    jest.clearAllMocks();
  });

  it('envia regras válidas e exibe feedback de sucesso', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'ok' }),
    });
    render(<GovernancaPage />);
    const textarea = screen.getByLabelText(/editor de regras yaml/i);
    fireEvent.change(textarea, {
      target: {
        value: 'score_minimo: 0.7\nblacklist:\n  - test_kw_banido\nwhitelist:\n  - test_kw_livre',
      },
    });
    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
    expect(screen.getByText(/regras enviadas com sucesso/i)).toBeInTheDocument();
  });

  it('exibe erro ao enviar regras inválidas', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      json: async () => ({ erro: 'score_minimo obrigatório e numérico' }),
    });
    render(<GovernancaPage />);
    const textarea = screen.getByLabelText(/editor de regras yaml/i);
    fireEvent.change(textarea, {
      target: {
        value: 'blacklist: []\nwhitelist: []',
      },
    });
    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
    expect(screen.getByText(/score_minimo obrigatório/i)).toBeInTheDocument();
  });

  it('exibe erro de rede ou exceção desconhecida', async () => {
    global.fetch = jest.fn().mockRejectedValue(new Error('Falha de rede'));
    render(<GovernancaPage />);
    const textarea = screen.getByLabelText(/editor de regras yaml/i);
    fireEvent.change(textarea, {
      target: {
        value: 'score_minimo: 0.7\nblacklist:\n  - test_kw_banido\nwhitelist:\n  - test_kw_livre',
      },
    });
    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
    expect(screen.getByText(/falha de rede/i)).toBeInTheDocument();
  });
}); 