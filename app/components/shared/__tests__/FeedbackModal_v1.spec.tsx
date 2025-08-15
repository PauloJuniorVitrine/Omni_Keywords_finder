import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import FeedbackModal, { FeedbackModalProps } from '../FeedbackModal_v1';

describe('FeedbackModal', () => {
  it('renderiza campos e envia feedback', () => {
    const onSubmit = jest.fn();
    render(<FeedbackModal open={true} onClose={jest.fn()} onSubmit={onSubmit} />);
    fireEvent.change(screen.getByLabelText(/mensagem de feedback/i), { target: { value: 'Mensagem teste' } });
    fireEvent.change(screen.getByLabelText(/categoria do feedback/i), { target: { value: 'bug' } });
    fireEvent.click(screen.getByText(/enviar/i));
    expect(onSubmit).toHaveBeenCalledWith({ message: 'Mensagem teste', category: 'bug' });
  });
  it('chama onClose ao cancelar', () => {
    const onClose = jest.fn();
    render(<FeedbackModal open={true} onClose={onClose} onSubmit={jest.fn()} />);
    fireEvent.click(screen.getByText(/cancelar/i));
    expect(onClose).toHaveBeenCalled();
  });
}); 