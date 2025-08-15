import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ExecucaoAutomaticaButton from '../ExecucaoAutomaticaButton';

describe('ExecucaoAutomaticaButton', () => {
  it('renderiza texto padrão quando não está carregando', () => {
    render(<ExecucaoAutomaticaButton onClick={() => {}} />);
    expect(screen.getByText('Iniciar Busca Automática')).toBeInTheDocument();
  });

  it('exibe Loader e texto durante loading', () => {
    render(<ExecucaoAutomaticaButton onClick={() => {}} loading />);
    expect(screen.getByText('Executando...')).toBeInTheDocument();
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('dispara onClick quando clicado', () => {
    const onClick = jest.fn();
    render(<ExecucaoAutomaticaButton onClick={onClick} />);
    fireEvent.click(screen.getByText('Iniciar Busca Automática'));
    expect(onClick).toHaveBeenCalled();
  });

  it('fica desabilitado durante loading', () => {
    render(<ExecucaoAutomaticaButton onClick={() => {}} loading />);
    expect(screen.getByRole('button')).toBeDisabled();
  });
}); 