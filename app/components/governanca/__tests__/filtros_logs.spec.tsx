import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import FiltrosLogs from '../filtros_logs';

describe('FiltrosLogs', () => {
  it('renderiza corretamente com props mínimas', () => {
    render(<FiltrosLogs onFiltrar={jest.fn()} />);
    expect(screen.getByTestId('filtros-logs')).toBeInTheDocument();
  });

  it('chama callback onFiltrar ao filtrar', () => {
    const mockFiltrar = jest.fn();
    render(<FiltrosLogs onFiltrar={mockFiltrar} />);
    fireEvent.change(screen.getByTestId('input-filtro'), { target: { value: 'erro' } });
    fireEvent.click(screen.getByTestId('btn-filtrar'));
    expect(mockFiltrar).toHaveBeenCalledWith('erro');
  });

  it('não quebra se onFiltrar não for função', () => {
    // @ts-expect-error Teste de edge case
    render(<FiltrosLogs onFiltrar={null} />);
    fireEvent.click(screen.getByTestId('btn-filtrar'));
    expect(screen.getByTestId('filtros-logs')).toBeInTheDocument();
  });

  it('possui atributos de acessibilidade', () => {
    render(<FiltrosLogs onFiltrar={jest.fn()} />);
    const painel = screen.getByTestId('filtros-logs');
    expect(painel).toHaveAttribute('role', 'search');
    expect(painel).toHaveAttribute('aria-label');
  });
}); 