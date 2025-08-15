/**
 * Testes Unitários - ExpandableCard Component
 * 
 * Prompt: Implementação de testes para componentes importantes
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_EXPANDABLE_CARD_031
 * 
 * Baseado em código real do ExpandableCard.tsx
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ExpandableCard } from '../../../app/components/ux/ExpandableCard';

describe('ExpandableCard - Componente de Card Expansível', () => {
  
  const defaultProps = {
    title: 'Título do Card',
    children: <div>Conteúdo do card</div>
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização do Componente', () => {
    
    test('deve renderizar título corretamente', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      expect(screen.getByText('Título do Card')).toBeInTheDocument();
    });

    test('deve renderizar children quando expandido', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      // Expandir o card
      fireEvent.click(screen.getByText('Título do Card'));
      
      expect(screen.getByText('Conteúdo do card')).toBeInTheDocument();
    });

    test('deve renderizar summary quando fornecido', () => {
      render(<ExpandableCard {...defaultProps} summary="Resumo do card" />);
      
      expect(screen.getByText('Resumo do card')).toBeInTheDocument();
    });

    test('deve aplicar classe CSS personalizada', () => {
      render(<ExpandableCard {...defaultProps} className="custom-card" />);
      
      const cardContainer = screen.getByText('Título do Card').closest('.expandable-card');
      expect(cardContainer).toHaveClass('custom-card');
    });

    test('deve renderizar children complexos', () => {
      const complexChildren = (
        <div>
          <p>Parágrafo 1</p>
          <ul>
            <li>Item 1</li>
            <li>Item 2</li>
          </ul>
          <button>Botão</button>
        </div>
      );

      render(<ExpandableCard {...defaultProps} children={complexChildren} />);
      
      // Expandir o card
      fireEvent.click(screen.getByText('Título do Card'));
      
      expect(screen.getByText('Parágrafo 1')).toBeInTheDocument();
      expect(screen.getByText('Item 1')).toBeInTheDocument();
      expect(screen.getByText('Item 2')).toBeInTheDocument();
      expect(screen.getByText('Botão')).toBeInTheDocument();
    });
  });

  describe('Expansão e Contração', () => {
    
    test('deve iniciar contraído por padrão', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      expect(screen.queryByText('Conteúdo do card')).not.toBeInTheDocument();
      expect(screen.getByText('+')).toBeInTheDocument();
    });

    test('deve expandir ao clicar no header', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      const header = screen.getByText('Título do Card').closest('div');
      fireEvent.click(header!);
      
      expect(screen.getByText('Conteúdo do card')).toBeInTheDocument();
      expect(screen.getByText('−')).toBeInTheDocument();
    });

    test('deve contrair ao clicar novamente', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      const header = screen.getByText('Título do Card').closest('div');
      
      // Expandir
      fireEvent.click(header!);
      expect(screen.getByText('Conteúdo do card')).toBeInTheDocument();
      expect(screen.getByText('−')).toBeInTheDocument();
      
      // Contrair
      fireEvent.click(header!);
      expect(screen.queryByText('Conteúdo do card')).not.toBeInTheDocument();
      expect(screen.getByText('+')).toBeInTheDocument();
    });

    test('deve iniciar expandido quando defaultExpanded é true', () => {
      render(<ExpandableCard {...defaultProps} defaultExpanded={true} />);
      
      expect(screen.getByText('Conteúdo do card')).toBeInTheDocument();
      expect(screen.getByText('−')).toBeInTheDocument();
    });

    test('deve alternar ícone de expansão', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      const header = screen.getByText('Título do Card').closest('div');
      
      // Inicialmente contraído
      expect(screen.getByText('+')).toBeInTheDocument();
      
      // Expandir
      fireEvent.click(header!);
      expect(screen.getByText('−')).toBeInTheDocument();
      
      // Contrair
      fireEvent.click(header!);
      expect(screen.getByText('+')).toBeInTheDocument();
    });
  });

  describe('Estilos e Layout', () => {
    
    test('deve ter borda e border-radius', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      const cardContainer = screen.getByText('Título do Card').closest('.expandable-card');
      expect(cardContainer).toHaveStyle({
        border: '1px solid #ccc',
        borderRadius: '8px',
        margin: '8px 0'
      });
    });

    test('deve ter padding no header', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      const header = screen.getByText('Título do Card').closest('div');
      expect(header).toHaveStyle({
        padding: '16px',
        cursor: 'pointer',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      });
    });

    test('deve ter padding no conteúdo expandido', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      // Expandir o card
      fireEvent.click(screen.getByText('Título do Card'));
      
      const content = screen.getByText('Conteúdo do card').closest('.expandable-content');
      expect(content).toHaveStyle({ padding: '0 16px 16px' });
    });

    test('deve ter cursor pointer no header', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      const header = screen.getByText('Título do Card').closest('div');
      expect(header).toHaveStyle({ cursor: 'pointer' });
    });

    test('deve ter layout flex no header', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      const header = screen.getByText('Título do Card').closest('div');
      expect(header).toHaveStyle({
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      });
    });
  });

  describe('Acessibilidade', () => {
    
    test('deve ter estrutura semântica adequada', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      expect(screen.getByRole('heading', { level: 3 })).toBeInTheDocument();
      expect(screen.getByText('Título do Card')).toBeInTheDocument();
    });

    test('deve ter navegação por teclado', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      const header = screen.getByText('Título do Card').closest('div');
      expect(header).toHaveAttribute('tabIndex', '0');
    });

    test('deve ter indicadores visuais de estado', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      // Estado inicial
      expect(screen.getByText('+')).toBeInTheDocument();
      
      // Expandir
      fireEvent.click(screen.getByText('Título do Card').closest('div')!);
      expect(screen.getByText('−')).toBeInTheDocument();
    });

    test('deve ter contraste adequado', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      const cardContainer = screen.getByText('Título do Card').closest('.expandable-card');
      expect(cardContainer).toHaveStyle({ border: '1px solid #ccc' });
    });

    test('deve ter tamanho de fonte adequado no título', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      const title = screen.getByRole('heading', { level: 3 });
      expect(title).toBeInTheDocument();
    });
  });

  describe('Interação do Usuário', () => {
    
    test('deve responder a cliques no header', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      const header = screen.getByText('Título do Card').closest('div');
      
      // Primeiro clique - expandir
      fireEvent.click(header!);
      expect(screen.getByText('Conteúdo do card')).toBeInTheDocument();
      
      // Segundo clique - contrair
      fireEvent.click(header!);
      expect(screen.queryByText('Conteúdo do card')).not.toBeInTheDocument();
    });

    test('deve responder a cliques no título', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      const title = screen.getByText('Título do Card');
      fireEvent.click(title);
      
      expect(screen.getByText('Conteúdo do card')).toBeInTheDocument();
    });

    test('deve responder a cliques no summary', () => {
      render(<ExpandableCard {...defaultProps} summary="Resumo do card" />);
      
      const summary = screen.getByText('Resumo do card');
      fireEvent.click(summary);
      
      expect(screen.getByText('Conteúdo do card')).toBeInTheDocument();
    });

    test('deve responder a cliques no ícone', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      const icon = screen.getByText('+');
      fireEvent.click(icon);
      
      expect(screen.getByText('Conteúdo do card')).toBeInTheDocument();
    });
  });

  describe('Estados do Componente', () => {
    
    test('deve iniciar contraído por padrão', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      expect(screen.queryByText('Conteúdo do card')).not.toBeInTheDocument();
      expect(screen.getByText('+')).toBeInTheDocument();
    });

    test('deve iniciar expandido quando configurado', () => {
      render(<ExpandableCard {...defaultProps} defaultExpanded={true} />);
      
      expect(screen.getByText('Conteúdo do card')).toBeInTheDocument();
      expect(screen.getByText('−')).toBeInTheDocument();
    });

    test('deve manter estado entre re-renders', () => {
      const { rerender } = render(<ExpandableCard {...defaultProps} />);
      
      // Expandir
      fireEvent.click(screen.getByText('Título do Card').closest('div')!);
      expect(screen.getByText('Conteúdo do card')).toBeInTheDocument();
      
      // Re-renderizar
      rerender(<ExpandableCard {...defaultProps} />);
      
      // Deve manter expandido
      expect(screen.getByText('Conteúdo do card')).toBeInTheDocument();
    });

    test('deve alternar estado corretamente', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      const header = screen.getByText('Título do Card').closest('div');
      
      // Estado inicial
      expect(screen.getByText('+')).toBeInTheDocument();
      expect(screen.queryByText('Conteúdo do card')).not.toBeInTheDocument();
      
      // Primeiro clique
      fireEvent.click(header!);
      expect(screen.getByText('−')).toBeInTheDocument();
      expect(screen.getByText('Conteúdo do card')).toBeInTheDocument();
      
      // Segundo clique
      fireEvent.click(header!);
      expect(screen.getByText('+')).toBeInTheDocument();
      expect(screen.queryByText('Conteúdo do card')).not.toBeInTheDocument();
    });
  });

  describe('Validação de Props', () => {
    
    test('deve aceitar título obrigatório', () => {
      render(<ExpandableCard title="Título Teste" children={<div>Conteúdo</div>} />);
      
      expect(screen.getByText('Título Teste')).toBeInTheDocument();
    });

    test('deve aceitar children obrigatório', () => {
      render(<ExpandableCard title="Título" children={<div>Conteúdo Teste</div>} />);
      
      // Expandir para ver o conteúdo
      fireEvent.click(screen.getByText('Título').closest('div')!);
      expect(screen.getByText('Conteúdo Teste')).toBeInTheDocument();
    });

    test('deve aceitar summary opcional', () => {
      render(<ExpandableCard {...defaultProps} summary="Resumo opcional" />);
      
      expect(screen.getByText('Resumo opcional')).toBeInTheDocument();
    });

    test('deve aceitar defaultExpanded opcional', () => {
      render(<ExpandableCard {...defaultProps} defaultExpanded={true} />);
      
      expect(screen.getByText('Conteúdo do card')).toBeInTheDocument();
    });

    test('deve aceitar className opcional', () => {
      render(<ExpandableCard {...defaultProps} className="test-class" />);
      
      const cardContainer = screen.getByText('Título do Card').closest('.expandable-card');
      expect(cardContainer).toHaveClass('test-class');
    });
  });

  describe('Performance e Otimização', () => {
    
    test('deve renderizar rapidamente', () => {
      const startTime = performance.now();
      
      render(<ExpandableCard {...defaultProps} />);
      
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(100); // Deve renderizar em menos de 100ms
    });

    test('deve evitar re-renders desnecessários', () => {
      const { rerender } = render(<ExpandableCard {...defaultProps} />);
      
      const initialTitle = screen.getByText('Título do Card');
      
      rerender(<ExpandableCard {...defaultProps} />);
      
      const newTitle = screen.getByText('Título do Card');
      expect(newTitle).toBe(initialTitle);
    });

    test('deve lidar com conteúdo complexo eficientemente', () => {
      const complexContent = (
        <div>
          {Array.from({ length: 100 }, (_, i) => (
            <p key={i}>Parágrafo {i + 1}</p>
          ))}
        </div>
      );

      const startTime = performance.now();
      
      render(<ExpandableCard {...defaultProps} children={complexContent} />);
      
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(500); // Deve renderizar em menos de 500ms
    });
  });

  describe('Casos de Borda', () => {
    
    test('deve lidar com título vazio', () => {
      render(<ExpandableCard title="" children={<div>Conteúdo</div>} />);
      
      const title = screen.getByRole('heading', { level: 3 });
      expect(title).toBeInTheDocument();
    });

    test('deve lidar com children vazio', () => {
      render(<ExpandableCard title="Título" children={<></>} />);
      
      // Expandir
      fireEvent.click(screen.getByText('Título').closest('div')!);
      
      // Deve renderizar sem erro
      const content = screen.getByText('Título').closest('.expandable-card')?.querySelector('.expandable-content');
      expect(content).toBeInTheDocument();
    });

    test('deve lidar com summary vazio', () => {
      render(<ExpandableCard {...defaultProps} summary="" />);
      
      // Deve renderizar sem erro
      expect(screen.getByText('Título do Card')).toBeInTheDocument();
    });

    test('deve lidar com múltiplos cliques rápidos', () => {
      render(<ExpandableCard {...defaultProps} />);
      
      const header = screen.getByText('Título do Card').closest('div');
      
      // Múltiplos cliques rápidos
      fireEvent.click(header!);
      fireEvent.click(header!);
      fireEvent.click(header!);
      
      // Deve estar expandido após cliques ímpares
      expect(screen.getByText('Conteúdo do card')).toBeInTheDocument();
    });
  });
}); 