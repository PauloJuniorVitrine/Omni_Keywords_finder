import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import HistoryPanel, { HistoryItem } from '../HistoryPanel_v1';

describe('HistoryPanel_v1', () => {
  const items: HistoryItem[] = [
    { id: '1', data: '2024-06-27T10:00:00Z', status: 'Concluído', resumo: 'Execução 1' },
    { id: '2', data: '2024-06-28T10:00:00Z', status: 'Concluído', resumo: 'Execução 2' },
  ];

  it('renderiza histórico e seleciona item', () => {
    const onSelect = jest.fn();
    render(<HistoryPanel items={items} onSelect={onSelect} selectedId="1" />);
    expect(screen.getByText('Execução 1')).toBeInTheDocument();
    expect(screen.getByText('Execução 2')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Execução 2'));
    expect(onSelect).toHaveBeenCalledWith('2');
  });

  it('exibe fallback visual quando vazio', () => {
    render(<HistoryPanel items={[]} onSelect={() => {}} />);
    expect(screen.getByText(/nenhuma execução/i)).toBeInTheDocument();
  });

  it('é acessível via aria-label', () => {
    render(<HistoryPanel items={items} onSelect={() => {}} />);
    expect(screen.getByLabelText('Histórico de Execuções')).toBeInTheDocument();
  });
}); 