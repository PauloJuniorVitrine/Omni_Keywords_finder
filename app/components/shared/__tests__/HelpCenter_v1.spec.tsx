import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import HelpCenter, { HelpCenterProps } from '../HelpCenter_v1';

describe('HelpCenter', () => {
  const topics = [
    { title: 'Tópico 1', content: 'Conteúdo 1' },
    { title: 'Tópico 2', content: 'Conteúdo 2' },
  ];
  it('renderiza tópicos e link de suporte', () => {
    render(<HelpCenter open={true} onClose={jest.fn()} topics={topics} supportLink="mailto:suporte@omni.com" />);
    expect(screen.getByText('Tópico 1')).toBeInTheDocument();
    expect(screen.getByText('Conteúdo 2')).toBeInTheDocument();
    expect(screen.getByText(/fale com o suporte/i)).toBeInTheDocument();
  });
  it('chama onClose ao clicar em fechar', () => {
    const onClose = jest.fn();
    render(<HelpCenter open={true} onClose={onClose} topics={topics} />);
    fireEvent.click(screen.getByLabelText(/fechar ajuda/i));
    expect(onClose).toHaveBeenCalled();
  });
}); 