/**
 * Testes Unitários - Tooltip Component
 * 
 * Prompt: Implementação de testes para componentes importantes
 * Ruleset: geral_rules_melhorado.yaml
 * Data: 2025-01-27
 * Tracing ID: TEST_TOOLTIP_030
 * 
 * Baseado em código real do Tooltip.tsx
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Tooltip } from '../../../app/components/ux/Tooltip';

describe('Tooltip - Componente de Tooltip', () => {
  
  const defaultProps = {
    content: 'Informação adicional sobre este elemento',
    children: <button>Hover me</button>
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Renderização do Componente', () => {
    
    test('deve renderizar children corretamente', () => {
      render(<Tooltip {...defaultProps} />);
      
      expect(screen.getByText('Hover me')).toBeInTheDocument();
    });

    test('deve renderizar conteúdo do tooltip', () => {
      render(<Tooltip {...defaultProps} />);
      
      // Trigger hover
      fireEvent.mouseEnter(screen.getByText('Hover me'));
      
      expect(screen.getByText('Informação adicional sobre este elemento')).toBeInTheDocument();
    });

    test('deve aplicar classe CSS personalizada', () => {
      render(<Tooltip {...defaultProps} className="custom-tooltip" />);
      
      const tooltipContainer = screen.getByText('Hover me').closest('.tooltip-container');
      expect(tooltipContainer).toHaveClass('custom-tooltip');
    });

    test('deve renderizar children complexos', () => {
      const complexChildren = (
        <div>
          <span>Texto</span>
          <button>Botão</button>
          <input placeholder="Input" />
        </div>
      );

      render(<Tooltip content="Tooltip" children={complexChildren} />);
      
      expect(screen.getByText('Texto')).toBeInTheDocument();
      expect(screen.getByText('Botão')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Input')).toBeInTheDocument();
    });
  });

  describe('Interação do Usuário', () => {
    
    test('deve mostrar tooltip ao hover', () => {
      render(<Tooltip {...defaultProps} />);
      
      const trigger = screen.getByText('Hover me');
      fireEvent.mouseEnter(trigger);
      
      expect(screen.getByText('Informação adicional sobre este elemento')).toBeInTheDocument();
    });

    test('deve esconder tooltip ao sair do hover', () => {
      render(<Tooltip {...defaultProps} />);
      
      const trigger = screen.getByText('Hover me');
      
      // Mostrar tooltip
      fireEvent.mouseEnter(trigger);
      expect(screen.getByText('Informação adicional sobre este elemento')).toBeInTheDocument();
      
      // Esconder tooltip
      fireEvent.mouseLeave(trigger);
      expect(screen.queryByText('Informação adicional sobre este elemento')).not.toBeInTheDocument();
    });

    test('deve funcionar com diferentes tipos de children', () => {
      const testCases = [
        { children: <span>Span element</span>, text: 'Span element' },
        { children: <div>Div element</div>, text: 'Div element' },
        { children: <input value="Input element" readOnly />, text: 'Input element' },
        { children: <button>Button element</button>, text: 'Button element' }
      ];

      testCases.forEach(({ children, text }) => {
        const { unmount } = render(<Tooltip content="Tooltip" children={children} />);
        
        const trigger = screen.getByText(text);
        fireEvent.mouseEnter(trigger);
        
        expect(screen.getByText('Tooltip')).toBeInTheDocument();
        
        unmount();
      });
    });
  });

  describe('Posicionamento', () => {
    
    test('deve posicionar tooltip no top por padrão', () => {
      render(<Tooltip {...defaultProps} />);
      
      const trigger = screen.getByText('Hover me');
      fireEvent.mouseEnter(trigger);
      
      const tooltipContent = screen.getByText('Informação adicional sobre este elemento');
      expect(tooltipContent).toHaveStyle({
        bottom: '100%',
        left: '50%',
        transform: 'translateX(-50%)',
        marginBottom: '4px'
      });
    });

    test('deve posicionar tooltip no bottom', () => {
      render(<Tooltip {...defaultProps} position="bottom" />);
      
      const trigger = screen.getByText('Hover me');
      fireEvent.mouseEnter(trigger);
      
      const tooltipContent = screen.getByText('Informação adicional sobre este elemento');
      expect(tooltipContent).toHaveStyle({
        top: '100%',
        left: '50%',
        transform: 'translateX(-50%)',
        marginTop: '4px'
      });
    });

    test('deve posicionar tooltip na esquerda', () => {
      render(<Tooltip {...defaultProps} position="left" />);
      
      const trigger = screen.getByText('Hover me');
      fireEvent.mouseEnter(trigger);
      
      const tooltipContent = screen.getByText('Informação adicional sobre este elemento');
      expect(tooltipContent).toHaveStyle({
        right: '100%',
        top: '50%',
        transform: 'translateY(-50%)',
        marginRight: '4px'
      });
    });

    test('deve posicionar tooltip na direita', () => {
      render(<Tooltip {...defaultProps} position="right" />);
      
      const trigger = screen.getByText('Hover me');
      fireEvent.mouseEnter(trigger);
      
      const tooltipContent = screen.getByText('Informação adicional sobre este elemento');
      expect(tooltipContent).toHaveStyle({
        left: '100%',
        top: '50%',
        transform: 'translateY(-50%)',
        marginLeft: '4px'
      });
    });
  });

  describe('Estilos do Tooltip', () => {
    
    test('deve ter estilo base correto', () => {
      render(<Tooltip {...defaultProps} />);
      
      const trigger = screen.getByText('Hover me');
      fireEvent.mouseEnter(trigger);
      
      const tooltipContent = screen.getByText('Informação adicional sobre este elemento');
      expect(tooltipContent).toHaveStyle({
        position: 'absolute',
        background: '#333',
        color: '#fff',
        padding: '8px',
        borderRadius: '4px',
        fontSize: '12px',
        whiteSpace: 'nowrap',
        zIndex: 1000
      });
    });

    test('deve ter posicionamento relativo no container', () => {
      render(<Tooltip {...defaultProps} />);
      
      const tooltipContainer = screen.getByText('Hover me').closest('.tooltip-container');
      expect(tooltipContainer).toHaveStyle({
        position: 'relative',
        display: 'inline-block'
      });
    });

    test('deve ter z-index alto', () => {
      render(<Tooltip {...defaultProps} />);
      
      const trigger = screen.getByText('Hover me');
      fireEvent.mouseEnter(trigger);
      
      const tooltipContent = screen.getByText('Informação adicional sobre este elemento');
      expect(tooltipContent).toHaveStyle({ zIndex: 1000 });
    });
  });

  describe('Acessibilidade', () => {
    
    test('deve ter estrutura semântica adequada', () => {
      render(<Tooltip {...defaultProps} />);
      
      const tooltipContainer = screen.getByText('Hover me').closest('.tooltip-container');
      expect(tooltipContainer).toBeInTheDocument();
    });

    test('deve ter contraste adequado', () => {
      render(<Tooltip {...defaultProps} />);
      
      const trigger = screen.getByText('Hover me');
      fireEvent.mouseEnter(trigger);
      
      const tooltipContent = screen.getByText('Informação adicional sobre este elemento');
      expect(tooltipContent).toHaveStyle({
        background: '#333',
        color: '#fff'
      });
    });

    test('deve ter tamanho de fonte legível', () => {
      render(<Tooltip {...defaultProps} />);
      
      const trigger = screen.getByText('Hover me');
      fireEvent.mouseEnter(trigger);
      
      const tooltipContent = screen.getByText('Informação adicional sobre este elemento');
      expect(tooltipContent).toHaveStyle({ fontSize: '12px' });
    });

    test('deve ter padding adequado', () => {
      render(<Tooltip {...defaultProps} />);
      
      const trigger = screen.getByText('Hover me');
      fireEvent.mouseEnter(trigger);
      
      const tooltipContent = screen.getByText('Informação adicional sobre este elemento');
      expect(tooltipContent).toHaveStyle({ padding: '8px' });
    });

    test('deve ter bordas arredondadas', () => {
      render(<Tooltip {...defaultProps} />);
      
      const trigger = screen.getByText('Hover me');
      fireEvent.mouseEnter(trigger);
      
      const tooltipContent = screen.getByText('Informação adicional sobre este elemento');
      expect(tooltipContent).toHaveStyle({ borderRadius: '4px' });
    });
  });

  describe('Estados do Componente', () => {
    
    test('deve iniciar invisível', () => {
      render(<Tooltip {...defaultProps} />);
      
      expect(screen.queryByText('Informação adicional sobre este elemento')).not.toBeInTheDocument();
    });

    test('deve mostrar ao hover', () => {
      render(<Tooltip {...defaultProps} />);
      
      const trigger = screen.getByText('Hover me');
      fireEvent.mouseEnter(trigger);
      
      expect(screen.getByText('Informação adicional sobre este elemento')).toBeInTheDocument();
    });

    test('deve esconder ao sair do hover', () => {
      render(<Tooltip {...defaultProps} />);
      
      const trigger = screen.getByText('Hover me');
      
      // Mostrar
      fireEvent.mouseEnter(trigger);
      expect(screen.getByText('Informação adicional sobre este elemento')).toBeInTheDocument();
      
      // Esconder
      fireEvent.mouseLeave(trigger);
      expect(screen.queryByText('Informação adicional sobre este elemento')).not.toBeInTheDocument();
    });

    test('deve manter estado entre re-renders', () => {
      const { rerender } = render(<Tooltip {...defaultProps} />);
      
      const trigger = screen.getByText('Hover me');
      fireEvent.mouseEnter(trigger);
      expect(screen.getByText('Informação adicional sobre este elemento')).toBeInTheDocument();
      
      rerender(<Tooltip {...defaultProps} />);
      
      // Deve manter visível
      expect(screen.getByText('Informação adicional sobre este elemento')).toBeInTheDocument();
    });
  });

  describe('Validação de Props', () => {
    
    test('deve aceitar conteúdo obrigatório', () => {
      render(<Tooltip content="Teste" children={<button>Botão</button>} />);
      
      const trigger = screen.getByText('Botão');
      fireEvent.mouseEnter(trigger);
      
      expect(screen.getByText('Teste')).toBeInTheDocument();
    });

    test('deve aceitar children obrigatório', () => {
      render(<Tooltip content="Teste" children={<span>Span</span>} />);
      
      expect(screen.getByText('Span')).toBeInTheDocument();
    });

    test('deve aceitar posição opcional', () => {
      render(<Tooltip {...defaultProps} position="bottom" />);
      
      const trigger = screen.getByText('Hover me');
      fireEvent.mouseEnter(trigger);
      
      const tooltipContent = screen.getByText('Informação adicional sobre este elemento');
      expect(tooltipContent).toHaveStyle({ top: '100%' });
    });

    test('deve aceitar className opcional', () => {
      render(<Tooltip {...defaultProps} className="custom-class" />);
      
      const tooltipContainer = screen.getByText('Hover me').closest('.tooltip-container');
      expect(tooltipContainer).toHaveClass('custom-class');
    });
  });

  describe('Performance e Otimização', () => {
    
    test('deve renderizar rapidamente', () => {
      const startTime = performance.now();
      
      render(<Tooltip {...defaultProps} />);
      
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(100); // Deve renderizar em menos de 100ms
    });

    test('deve evitar re-renders desnecessários', () => {
      const { rerender } = render(<Tooltip {...defaultProps} />);
      
      const initialTrigger = screen.getByText('Hover me');
      
      rerender(<Tooltip {...defaultProps} />);
      
      const newTrigger = screen.getByText('Hover me');
      expect(newTrigger).toBe(initialTrigger);
    });

    test('deve lidar com conteúdo longo eficientemente', () => {
      const longContent = 'A'.repeat(1000);
      
      const startTime = performance.now();
      
      render(<Tooltip content={longContent} children={<button>Botão</button>} />);
      
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(200); // Deve renderizar em menos de 200ms
    });
  });

  describe('Casos de Borda', () => {
    
    test('deve lidar com conteúdo vazio', () => {
      render(<Tooltip content="" children={<button>Botão</button>} />);
      
      const trigger = screen.getByText('Botão');
      fireEvent.mouseEnter(trigger);
      
      const tooltipContent = screen.getByText('').closest('.tooltip-content');
      expect(tooltipContent).toBeInTheDocument();
    });

    test('deve lidar com children vazio', () => {
      render(<Tooltip content="Tooltip" children={<></>} />);
      
      // Deve renderizar sem erro
      expect(screen.getByText('Tooltip')).not.toBeInTheDocument();
    });

    test('deve lidar com posição inválida', () => {
      render(<Tooltip {...defaultProps} position="invalid" as any />);
      
      const trigger = screen.getByText('Hover me');
      fireEvent.mouseEnter(trigger);
      
      // Deve usar posição padrão (top)
      const tooltipContent = screen.getByText('Informação adicional sobre este elemento');
      expect(tooltipContent).toHaveStyle({ bottom: '100%' });
    });

    test('deve lidar com múltiplos hovers rápidos', () => {
      render(<Tooltip {...defaultProps} />);
      
      const trigger = screen.getByText('Hover me');
      
      // Múltiplos hovers rápidos
      fireEvent.mouseEnter(trigger);
      fireEvent.mouseLeave(trigger);
      fireEvent.mouseEnter(trigger);
      fireEvent.mouseLeave(trigger);
      fireEvent.mouseEnter(trigger);
      
      // Deve estar visível após último hover
      expect(screen.getByText('Informação adicional sobre este elemento')).toBeInTheDocument();
    });
  });
}); 