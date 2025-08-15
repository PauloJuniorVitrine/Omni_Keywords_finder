import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import UploadRegras from '../upload_regras';

describe('UploadRegras', () => {
  it('renderiza corretamente com props mínimas', () => {
    render(<UploadRegras onUpload={jest.fn()} />);
    expect(screen.getByTestId('upload-regras')).toBeInTheDocument();
  });

  it('chama callback onUpload ao submeter', () => {
    const mockUpload = jest.fn();
    render(<UploadRegras onUpload={mockUpload} />);
    fireEvent.click(screen.getByTestId('btn-upload'));
    expect(mockUpload).toHaveBeenCalled();
  });

  it('não quebra se onUpload não for função', () => {
    // @ts-expect-error Teste de edge case
    render(<UploadRegras onUpload={null} />);
    fireEvent.click(screen.getByTestId('btn-upload'));
    expect(screen.getByTestId('upload-regras')).toBeInTheDocument();
  });

  it('possui atributos de acessibilidade', () => {
    render(<UploadRegras onUpload={jest.fn()} />);
    const painel = screen.getByTestId('upload-regras');
    expect(painel).toHaveAttribute('role', 'form');
    expect(painel).toHaveAttribute('aria-label');
  });
}); 