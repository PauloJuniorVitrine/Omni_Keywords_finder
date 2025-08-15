import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ModalConfirm from '../ModalConfirm';

describe('ModalConfirm', () => {
  it('renderiza mensagem e botões', () => {
    render(<ModalConfirm open message="Confirmar ação?" />);
    expect(screen.getByText('Confirmar ação?')).toBeInTheDocument();
    expect(screen.getByText('Confirmar')).toBeInTheDocument();
    expect(screen.getByText('Cancelar')).toBeInTheDocument();
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('chama onConfirm e onCancel', () => {
    const onConfirm = jest.fn();
    const onCancel = jest.fn();
    render(<ModalConfirm open message="Confirma?" onConfirm={onConfirm} onCancel={onCancel} />);
    fireEvent.click(screen.getByText('Confirmar'));
    expect(onConfirm).toHaveBeenCalled();
    fireEvent.click(screen.getByText('Cancelar'));
    expect(onCancel).toHaveBeenCalled();
  });

  it('não renderiza se open for false', () => {
    render(<ModalConfirm open={false} message="Não deve aparecer" />);
    expect(screen.queryByText('Não deve aparecer')).not.toBeInTheDocument();
  });
}); 