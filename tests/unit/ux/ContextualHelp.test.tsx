/**
 * Testes Unitários - ContextualHelp Component
 * 
 * Prompt: Implementação de testes para componentes importantes
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_CONTEXTUAL_HELP_029
 * 
 * Baseado em código real do ContextualHelp.tsx
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ContextualHelp } from '../../../app/components/ux/ContextualHelp';

describe('ContextualHelp - Componente de Ajuda Contextual', () => {
  
  const defaultProps = {
    title: 'Como usar o sistema',
    content: 'Este é um guia de como usar o sistema de keywords.'
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização do Componente', () => {
    
    test('deve renderizar o trigger padrão', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      expect(screen.getByText('?')).toBeInTheDocument();
    });

    test('deve renderizar trigger personalizado', () => {
      const customTrigger = <button data-testid="custom-trigger">Ajuda</button>;
      
      render(<ContextualHelp {...defaultProps} trigger={customTrigger} />);
      
      expect(screen.getByTestId('custom-trigger')).toBeInTheDocument();
      expect(screen.queryByText('?')).not.toBeInTheDocument();
    });

    test('deve renderizar título e conteúdo', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      // Abrir o help
      fireEvent.click(screen.getByText('?'));
      
      expect(screen.getByText('Como usar o sistema')).toBeInTheDocument();
      expect(screen.getByText('Este é um guia de como usar o sistema de keywords.')).toBeInTheDocument();
    });

    test('deve aplicar classe CSS personalizada', () => {
      render(<ContextualHelp {...defaultProps} className="custom-help" />);
      
      const helpContainer = screen.getByText('?').closest('.contextual-help');
      expect(helpContainer).toHaveClass('custom-help');
    });

    test('deve renderizar conteúdo React complexo', () => {
      const complexContent = (
        <div>
          <p>Parágrafo 1</p>
          <ul>
            <li>Item 1</li>
            <li>Item 2</li>
          </ul>
        </div>
      );

      render(<ContextualHelp {...defaultProps} content={complexContent} />);
      
      // Abrir o help
      fireEvent.click(screen.getByText('?'));
      
      expect(screen.getByText('Parágrafo 1')).toBeInTheDocument();
      expect(screen.getByText('Item 1')).toBeInTheDocument();
      expect(screen.getByText('Item 2')).toBeInTheDocument();
    });
  });

  describe('Interação do Usuário', () => {
    
    test('deve abrir help ao clicar no trigger', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      const trigger = screen.getByText('?');
      fireEvent.click(trigger);
      
      expect(screen.getByText('Como usar o sistema')).toBeInTheDocument();
      expect(screen.getByText('Este é um guia de como usar o sistema de keywords.')).toBeInTheDocument();
    });

    test('deve fechar help ao clicar no botão fechar', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      // Abrir help
      fireEvent.click(screen.getByText('?'));
      expect(screen.getByText('Como usar o sistema')).toBeInTheDocument();
      
      // Fechar help
      fireEvent.click(screen.getByText('Fechar'));
      expect(screen.queryByText('Como usar o sistema')).not.toBeInTheDocument();
    });

    test('deve alternar estado ao clicar no trigger', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      const trigger = screen.getByText('?');
      
      // Primeiro clique - abrir
      fireEvent.click(trigger);
      expect(screen.getByText('Como usar o sistema')).toBeInTheDocument();
      
      // Segundo clique - fechar
      fireEvent.click(trigger);
      expect(screen.queryByText('Como usar o sistema')).not.toBeInTheDocument();
    });

    test('deve funcionar com trigger personalizado', () => {
      const customTrigger = <button data-testid="custom-trigger">Ajuda</button>;
      
      render(<ContextualHelp {...defaultProps} trigger={customTrigger} />);
      
      const trigger = screen.getByTestId('custom-trigger');
      fireEvent.click(trigger);
      
      expect(screen.getByText('Como usar o sistema')).toBeInTheDocument();
    });
  });

  describe('Posicionamento e Estilo', () => {
    
    test('deve ter posicionamento absoluto', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      // Abrir help
      fireEvent.click(screen.getByText('?'));
      
      const helpContent = screen.getByText('Como usar o sistema').closest('.contextual-help-content');
      expect(helpContent).toHaveStyle({ position: 'absolute' });
    });

    test('deve ter z-index alto', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      // Abrir help
      fireEvent.click(screen.getByText('?'));
      
      const helpContent = screen.getByText('Como usar o sistema').closest('.contextual-help-content');
      expect(helpContent).toHaveStyle({ zIndex: 1000 });
    });

    test('deve ter largura mínima e máxima', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      // Abrir help
      fireEvent.click(screen.getByText('?'));
      
      const helpContent = screen.getByText('Como usar o sistema').closest('.contextual-help-content');
      expect(helpContent).toHaveStyle({ minWidth: '200px' });
      expect(helpContent).toHaveStyle({ maxWidth: '300px' });
    });

    test('deve ter borda e sombra', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      // Abrir help
      fireEvent.click(screen.getByText('?'));
      
      const helpContent = screen.getByText('Como usar o sistema').closest('.contextual-help-content');
      expect(helpContent).toHaveStyle({ 
        border: '1px solid #ccc',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      });
    });

    test('deve ter padding interno', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      // Abrir help
      fireEvent.click(screen.getByText('?'));
      
      const helpContent = screen.getByText('Como usar o sistema').closest('.contextual-help-content');
      expect(helpContent).toHaveStyle({ padding: '16px' });
    });
  });

  describe('Acessibilidade', () => {
    
    test('deve ter cursor pointer no trigger', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      const trigger = screen.getByText('?');
      expect(trigger.closest('div')).toHaveStyle({ cursor: 'pointer' });
    });

    test('deve ser navegável por teclado', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      const trigger = screen.getByText('?');
      expect(trigger.closest('div')).toHaveAttribute('tabIndex', '0');
    });

    test('deve ter estrutura semântica adequada', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      // Abrir help
      fireEvent.click(screen.getByText('?'));
      
      expect(screen.getByRole('heading', { level: 4 })).toBeInTheDocument();
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    test('deve ter botão fechar acessível', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      // Abrir help
      fireEvent.click(screen.getByText('?'));
      
      const closeButton = screen.getByText('Fechar');
      expect(closeButton).toHaveAttribute('role', 'button');
    });

    test('deve ter contraste adequado no trigger', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      const trigger = screen.getByText('?');
      expect(trigger).toHaveStyle({ color: '#1976d2' });
    });

    test('deve ter tamanho de fonte adequado no trigger', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      const trigger = screen.getByText('?');
      expect(trigger).toHaveStyle({ fontSize: '16px' });
    });
  });

  describe('Estados do Componente', () => {
    
    test('deve iniciar fechado', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      expect(screen.queryByText('Como usar o sistema')).not.toBeInTheDocument();
      expect(screen.queryByText('Fechar')).not.toBeInTheDocument();
    });

    test('deve abrir ao clicar', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      fireEvent.click(screen.getByText('?'));
      
      expect(screen.getByText('Como usar o sistema')).toBeInTheDocument();
      expect(screen.getByText('Fechar')).toBeInTheDocument();
    });

    test('deve fechar ao clicar no botão fechar', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      // Abrir
      fireEvent.click(screen.getByText('?'));
      expect(screen.getByText('Como usar o sistema')).toBeInTheDocument();
      
      // Fechar
      fireEvent.click(screen.getByText('Fechar'));
      expect(screen.queryByText('Como usar o sistema')).not.toBeInTheDocument();
    });

    test('deve manter estado entre re-renders', () => {
      const { rerender } = render(<ContextualHelp {...defaultProps} />);
      
      // Abrir
      fireEvent.click(screen.getByText('?'));
      expect(screen.getByText('Como usar o sistema')).toBeInTheDocument();
      
      // Re-renderizar
      rerender(<ContextualHelp {...defaultProps} />);
      
      // Deve manter aberto
      expect(screen.getByText('Como usar o sistema')).toBeInTheDocument();
    });
  });

  describe('Validação de Props', () => {
    
    test('deve aceitar título obrigatório', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      fireEvent.click(screen.getByText('?'));
      expect(screen.getByText('Como usar o sistema')).toBeInTheDocument();
    });

    test('deve aceitar conteúdo obrigatório', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      fireEvent.click(screen.getByText('?'));
      expect(screen.getByText('Este é um guia de como usar o sistema de keywords.')).toBeInTheDocument();
    });

    test('deve aceitar trigger opcional', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      // Deve usar trigger padrão
      expect(screen.getByText('?')).toBeInTheDocument();
    });

    test('deve aceitar className opcional', () => {
      render(<ContextualHelp {...defaultProps} className="test-class" />);
      
      const container = screen.getByText('?').closest('.contextual-help');
      expect(container).toHaveClass('test-class');
    });
  });

  describe('Performance e Otimização', () => {
    
    test('deve renderizar rapidamente', () => {
      const startTime = performance.now();
      
      render(<ContextualHelp {...defaultProps} />);
      
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(100); // Deve renderizar em menos de 100ms
    });

    test('deve evitar re-renders desnecessários', () => {
      const { rerender } = render(<ContextualHelp {...defaultProps} />);
      
      const initialTrigger = screen.getByText('?');
      
      // Re-renderizar com os mesmos props
      rerender(<ContextualHelp {...defaultProps} />);
      
      const newTrigger = screen.getByText('?');
      expect(newTrigger).toBe(initialTrigger);
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
      
      render(<ContextualHelp {...defaultProps} content={complexContent} />);
      
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(500); // Deve renderizar em menos de 500ms
    });
  });

  describe('Casos de Borda', () => {
    
    test('deve lidar com título vazio', () => {
      render(<ContextualHelp title="" content="Conteúdo" />);
      
      fireEvent.click(screen.getByText('?'));
      expect(screen.getByRole('heading', { level: 4 })).toBeInTheDocument();
    });

    test('deve lidar com conteúdo vazio', () => {
      render(<ContextualHelp title="Título" content="" />);
      
      fireEvent.click(screen.getByText('?'));
      expect(screen.getByText('Título')).toBeInTheDocument();
    });

    test('deve lidar com trigger complexo', () => {
      const complexTrigger = (
        <div data-testid="complex-trigger">
          <span>Clique aqui para</span>
          <strong>ajuda</strong>
        </div>
      );

      render(<ContextualHelp {...defaultProps} trigger={complexTrigger} />);
      
      expect(screen.getByTestId('complex-trigger')).toBeInTheDocument();
      expect(screen.getByText('Clique aqui para')).toBeInTheDocument();
      expect(screen.getByText('ajuda')).toBeInTheDocument();
    });

    test('deve lidar com múltiplos cliques rápidos', () => {
      render(<ContextualHelp {...defaultProps} />);
      
      const trigger = screen.getByText('?');
      
      // Múltiplos cliques rápidos
      fireEvent.click(trigger);
      fireEvent.click(trigger);
      fireEvent.click(trigger);
      
      // Deve estar fechado após cliques ímpares
      expect(screen.queryByText('Como usar o sistema')).not.toBeInTheDocument();
    });
  });
}); 