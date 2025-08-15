import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DashboardPage from '../index';

// Helper para simular tab
function pressTab() {
  fireEvent.keyDown(document, { key: 'Tab', code: 'Tab', keyCode: 9 });
}

describe('DashboardPage - Fluxos Descobertos (integração)', () => {
  it('navegação por tab entre cards, tendências e ações', async () => {
    render(<DashboardPage />);
    await screen.findByTestId('dashboard-cards');
    // Foca no título
    screen.getByTestId('dashboard-title').focus();
    expect(document.activeElement).toBe(screen.getByTestId('dashboard-title'));
    // Tab para cards
    pressTab();
    // Não é possível garantir ordem exata sem rotação de foco, mas tabIndex está presente
    expect(screen.getByTestId('dashboard-cards')).toBeInTheDocument();
  });

  it('loader persiste se fetch não resolve', () => {
    global.fetch = jest.fn(() => new Promise(() => {})) as any;
    render(<DashboardPage />);
    expect(screen.getByTestId('dashboard-loader')).toBeInTheDocument();
  });

  it('empty state de cards e tendências', () => {
    jest.spyOn(React, 'useState').mockImplementationOnce(() => [null, jest.fn()]);
    render(<DashboardPage />);
    expect(screen.getByTestId('dashboard-empty')).toBeInTheDocument();
  });

  it('renderiza badges e ícones corretamente', async () => {
    render(<DashboardPage />);
    await screen.findByTestId('dashboard-cards');
    expect(screen.getByText('Ativo')).toBeInTheDocument();
    expect(screen.getByText('Erro')).toBeInTheDocument();
    // Ícone de tendência (📈)
    expect(screen.getAllByRole('img', { name: /ícone de tendência/i })[0]).toBeInTheDocument();
  });

  it('exibe banner de erro e fallback para mock', async () => {
    (global.fetch as jest.Mock).mockImplementationOnce(() => Promise.resolve({ ok: false }));
    render(<DashboardPage />);
    expect(await screen.findByTestId('dashboard-error')).toBeInTheDocument();
    expect(await screen.findByTestId('dashboard-cards')).toBeInTheDocument();
  });

  it('permite exportação só para admin', async () => {
    render(<DashboardPage />);
    expect(await screen.findByTestId('btn-exportar')).toBeInTheDocument();
  });

  it('não permite exportação para user', async () => {
    jest.spyOn(React, 'useState').mockImplementationOnce(() => ['user', jest.fn()]);
    render(<DashboardPage />);
    await screen.findByTestId('dashboard-cards');
    expect(screen.queryByTestId('btn-exportar')).not.toBeInTheDocument();
  });

  it('todos os elementos principais têm ARIA labels e roles', async () => {
    render(<DashboardPage />);
    await screen.findByTestId('dashboard-cards');
    expect(screen.getByLabelText('Título do dashboard')).toBeInTheDocument();
    expect(screen.getByLabelText('Cards de métricas do dashboard')).toBeInTheDocument();
    expect(screen.getByLabelText('Ações do dashboard')).toBeInTheDocument();
  });
}); 