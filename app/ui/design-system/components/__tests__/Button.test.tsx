/**
 * Button Component Tests - Omni Keywords Finder
 * 
 * Testes unitários básicos para o componente Button
 * 
 * Tracing ID: DS-TEST-001
 * Data/Hora: 2025-01-27 15:30:00 UTC
 * Versão: 1.0
 */

import React from 'react';
import { render } from '@testing-library/react';
import Button from '../Button';

// =============================================================================
// TESTES BÁSICOS
// =============================================================================

describe('Button Component', () => {
  test('renderiza com texto básico', () => {
    const { getByText } = render(<Button>Clique aqui</Button>);
    expect(getByText('Clique aqui')).toBeInTheDocument();
  });

  test('renderiza com variante primária por padrão', () => {
    const { getByRole } = render(<Button>Botão</Button>);
    const button = getByRole('button');
    expect(button).toHaveStyle({ backgroundColor: 'rgb(37, 99, 235)' });
  });

  test('renderiza com tamanho médio por padrão', () => {
    const { getByRole } = render(<Button>Botão</Button>);
    const button = getByRole('button');
    expect(button).toHaveStyle({ fontSize: '1rem' });
  });

  test('renderiza com ícones', () => {
    const { getByText } = render(
      <Button leftIcon="🔍" rightIcon="➡️">
        Buscar
      </Button>
    );
    expect(getByText('🔍')).toBeInTheDocument();
    expect(getByText('➡️')).toBeInTheDocument();
    expect(getByText('Buscar')).toBeInTheDocument();
  });

  test('renderiza em largura total', () => {
    const { getByRole } = render(<Button fullWidth>Botão Largo</Button>);
    const button = getByRole('button');
    expect(button).toHaveStyle({ width: '100%' });
  });

  test('renderiza variante danger', () => {
    const { getByRole } = render(<Button variant="danger">Danger</Button>);
    const button = getByRole('button');
    expect(button).toHaveStyle({ backgroundColor: 'rgb(220, 38, 38)' });
  });

  test('renderiza estado disabled', () => {
    const { getByRole } = render(<Button disabled>Disabled</Button>);
    const button = getByRole('button');
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute('aria-disabled', 'true');
  });

  test('renderiza estado loading', () => {
    const { getByRole } = render(<Button loading>Loading</Button>);
    const button = getByRole('button');
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute('aria-busy', 'true');
  });

  test('chama onClick quando clicado', () => {
    const handleClick = jest.fn();
    const { getByRole } = render(<Button onClick={handleClick}>Clique</Button>);
    
    const button = getByRole('button');
    button.click();
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('não chama onClick quando disabled', () => {
    const handleClick = jest.fn();
    const { getByRole } = render(<Button disabled onClick={handleClick}>Disabled</Button>);
    
    const button = getByRole('button');
    button.click();
    expect(handleClick).not.toHaveBeenCalled();
  });

  test('combina múltiplas props corretamente', () => {
    const { getByRole, getByText } = render(
      <Button
        variant="danger"
        size="lg"
        fullWidth
        leftIcon="⚠️"
        disabled
      >
        Botão Complexo
      </Button>
    );
    
    const button = getByRole('button');
    expect(button).toHaveStyle({ backgroundColor: 'rgb(220, 38, 38)' });
    expect(button).toHaveStyle({ fontSize: '1.125rem' });
    expect(button).toHaveStyle({ width: '100%' });
    expect(button).toBeDisabled();
    expect(getByText('⚠️')).toBeInTheDocument();
    expect(getByText('Botão Complexo')).toBeInTheDocument();
  });
}); 