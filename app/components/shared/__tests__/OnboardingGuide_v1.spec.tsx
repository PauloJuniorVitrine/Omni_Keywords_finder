import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import OnboardingGuide, { OnboardingGuideProps } from '../OnboardingGuide_v1';

const steps = [
  { target: 'body', content: 'Bem-vindo!' },
  { target: 'body', content: 'Segundo passo.' },
];

describe('OnboardingGuide', () => {
  it('renderiza e navega entre etapas', () => {
    const onClose = jest.fn();
    render(<OnboardingGuide steps={steps} run={true} onClose={onClose} />);
    expect(screen.getByText('Bem-vindo!')).toBeInTheDocument();
    fireEvent.click(screen.getByText(/próximo/i));
    expect(screen.getByText('Segundo passo.')).toBeInTheDocument();
  });

  it('chama onClose ao finalizar', () => {
    const onClose = jest.fn();
    render(<OnboardingGuide steps={steps} run={true} onClose={onClose} />);
    fireEvent.click(screen.getByText(/próximo/i));
    fireEvent.click(screen.getByText(/finalizar/i));
    expect(onClose).toHaveBeenCalled();
  });
}); 