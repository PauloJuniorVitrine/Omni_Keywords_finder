import React from 'react';
import { render, screen } from '@testing-library/react';
import Skeleton from '../Skeleton_v1';
import PromptList from '../../nichos/PromptList';

describe('Skeleton_v1', () => {
  it('renderiza skeleton padrão (linha)', () => {
    render(<Skeleton />);
    expect(screen.getByLabelText('Carregando...')).toBeInTheDocument();
  });

  it('renderiza skeleton bloco', () => {
    render(<Skeleton variant="block" height={40} />);
    const skeleton = screen.getByLabelText('Carregando...');
    expect(skeleton).toHaveStyle('border-radius: 8px');
    expect(skeleton).toHaveStyle('height: 40px');
  });

  it('renderiza skeleton círculo', () => {
    render(<Skeleton variant="circle" width={32} height={32} />);
    const skeleton = screen.getByLabelText('Carregando...');
    expect(skeleton).toHaveStyle('border-radius: 50%');
    expect(skeleton).toHaveStyle('width: 32px');
    expect(skeleton).toHaveStyle('height: 32px');
  });

  it('aplica estilos customizados', () => {
    render(<Skeleton style={{ background: '#eab308' }} />);
    expect(screen.getByLabelText('Carregando...')).toHaveStyle('background: #eab308');
  });

  it('é acessível via aria-busy', () => {
    render(<Skeleton />);
    expect(screen.getByLabelText('Carregando...')).toHaveAttribute('aria-busy', 'true');
  });

  it('renderiza skeletons em PromptList durante carregamento', () => {
    render(<PromptList prompts={[]} onRemove={() => {}} renderSkeleton />);
    expect(screen.getAllByLabelText('Carregando...').length).toBeGreaterThan(1);
  });
}); 