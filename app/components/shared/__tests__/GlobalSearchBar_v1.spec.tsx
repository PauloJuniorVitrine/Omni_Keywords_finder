import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import GlobalSearchBar from '../GlobalSearchBar_v1';

describe('GlobalSearchBar_v1', () => {
  it('renderiza input com placeholder', () => {
    render(<GlobalSearchBar onSearch={() => {}} placeholder="Buscar..." />);
    expect(screen.getByPlaceholderText('Buscar...')).toBeInTheDocument();
  });

  it('chama onSearch com debounce', () => {
    jest.useFakeTimers();
    const onSearch = jest.fn();
    render(<GlobalSearchBar onSearch={onSearch} />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'abc' } });
    act(() => { jest.advanceTimersByTime(300); });
    expect(onSearch).toHaveBeenCalledWith('abc');
    jest.useRealTimers();
  });

  it('exibe sugestões de autocomplete', () => {
    render(<GlobalSearchBar onSearch={() => {}} suggestions={['Alpha', 'Beta', 'Gamma']} />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'a' } });
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Al' } });
    expect(screen.getByRole('listbox')).toBeInTheDocument();
    expect(screen.getByText('Alpha')).toBeInTheDocument();
  });

  it('navega sugestões com teclado', () => {
    render(<GlobalSearchBar onSearch={() => {}} suggestions={['Alpha', 'Beta']} />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'a' } });
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Al' } });
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'ArrowDown' });
    fireEvent.keyDown(screen.getByRole('textbox'), { key: 'Enter' });
    expect(screen.getByRole('textbox')).toHaveValue('Alpha');
  });

  it('é acessível via aria-label', () => {
    render(<GlobalSearchBar onSearch={() => {}} ariaLabel="Busca global" />);
    expect(screen.getByLabelText('Busca global')).toBeInTheDocument();
  });
}); 