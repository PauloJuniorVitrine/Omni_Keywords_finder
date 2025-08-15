import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Tooltip from '../Tooltip_v1';

const DummyButton: React.FC = () => (
  <Tooltip content="Dica de ação">
    <button>Ação</button>
  </Tooltip>
);

describe('Tooltip_v1', () => {
  it('renderiza o conteúdo do filho normalmente', () => {
    render(<Tooltip content="Dica"> <button>Alvo</button> </Tooltip>);
    expect(screen.getByText('Alvo')).toBeInTheDocument();
  });

  it('exibe o tooltip ao hover/focus', () => {
    render(<Tooltip content="Dica"> <button>Alvo</button> </Tooltip>);
    fireEvent.mouseEnter(screen.getByText('Alvo'));
    expect(screen.getByRole('tooltip')).toHaveTextContent('Dica');
  });

  it('esconde o tooltip ao mouse leave/blur', () => {
    render(<Tooltip content="Dica"> <button>Alvo</button> </Tooltip>);
    const alvo = screen.getByText('Alvo');
    fireEvent.mouseEnter(alvo);
    expect(screen.getByRole('tooltip')).toBeInTheDocument();
    fireEvent.mouseLeave(alvo);
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
  });

  it('respeita o delay', () => {
    jest.useFakeTimers();
    render(<Tooltip content="Dica" delay={500}> <button>Alvo</button> </Tooltip>);
    fireEvent.mouseEnter(screen.getByText('Alvo'));
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
    jest.advanceTimersByTime(500);
    expect(screen.getByRole('tooltip')).toBeInTheDocument();
    jest.useRealTimers();
  });

  it('é acessível via teclado', () => {
    render(<Tooltip content="Acessível"> <button>Alvo</button> </Tooltip>);
    fireEvent.focus(screen.getByText('Alvo'));
    expect(screen.getByRole('tooltip')).toBeInTheDocument();
  });

  it('funciona em um botão de ação real', () => {
    render(<DummyButton />);
    fireEvent.mouseEnter(screen.getByText('Ação'));
    expect(screen.getByRole('tooltip')).toHaveTextContent('Dica de ação');
  });
}); 