import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ActionButton from '../ActionButton';

describe('ActionButton', () => {
  it('renderiza label e variante primária', () => {
    render(<ActionButton label="Criar" variant="primary" />);
    expect(screen.getByText('Criar')).toBeInTheDocument();
    expect(screen.getByRole('button')).toHaveStyle('background: #4f8cff');
  });

  it('renderiza variante secundária', () => {
    render(<ActionButton label="Exportar" variant="secondary" />);
    expect(screen.getByText('Exportar')).toBeInTheDocument();
    expect(screen.getByRole('button')).toHaveStyle('background: #eab308');
  });

  it('fica desabilitado', () => {
    render(<ActionButton label="Desabilitado" disabled />);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('chama onClick quando clicado', () => {
    const onClick = jest.fn();
    render(<ActionButton label="Clique" onClick={onClick} />);
    fireEvent.click(screen.getByText('Clique'));
    expect(onClick).toHaveBeenCalled();
  });

  it('é acessível via aria-label', () => {
    render(<ActionButton label="Acessível" />);
    expect(screen.getByLabelText('Acessível')).toBeInTheDocument();
  });
}); 